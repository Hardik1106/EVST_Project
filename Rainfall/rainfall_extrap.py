import os
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from branca.colormap import LinearColormap

# --- Load GeoJSON boundary ---
boundary_path = "GeoJsons/Delhi_NCR_Districts_final.geojson"
if not os.path.exists(boundary_path):
    raise FileNotFoundError(f"Boundary GeoJSON not found: {boundary_path}")
boundary = gpd.read_file(boundary_path)
boundary = boundary.to_crs(epsg=4326)

# --- Load monthly rainfall CSV ---
df = pd.read_csv("delhi_ncr_rainfall_monthly_avg_2013_2024.csv")
df['TIME'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')
df['TIME_ISO'] = df['TIME'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# Ensure YEAR and MONTH are ints
df['YEAR'] = df['YEAR'].astype(int)
df['MONTH'] = df['MONTH'].astype(int)

# --- Create color scale ---
max_rain = df['RAINFALL'].max()
colormap = LinearColormap(['white', 'blue', 'purple'], vmin=0, vmax=max_rain,
                          caption='Average Monthly Rainfall (mm)')

# --- Normalize names for matching ---
# Detect district name column in boundary
name_col = None
for cand in ["NAME_2", "DISTRICT_NAME", "dtname", "dt_name", "district", "District"]:
    if cand in boundary.columns:
        name_col = cand
        break
if name_col is None:
    # fallback: create a district name from index
    boundary['DISTRICT_NAME'] = boundary.index.astype(str)
    name_col = 'DISTRICT_NAME'
else:
    if name_col != 'DISTRICT_NAME':
        boundary = boundary.rename(columns={name_col: 'DISTRICT_NAME'})

boundary['DISTRICT_NAME_clean'] = boundary['DISTRICT_NAME'].astype(str).str.strip().str.lower()
df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].astype(str).str.strip().str.lower()

# --- Fill missing districts by averaging neighbors (algorithm requested)
# Determine which districts in the boundary are missing from the CSV data
available = set(df['DISTRICT_NAME_clean'].unique())
all_districts = set(boundary['DISTRICT_NAME_clean'].unique())
missing = sorted(list(all_districts - available))

filled_rows = []
if missing:
    # precompute unique year-month pairs present in data
    ym_pairs = df[['YEAR', 'MONTH']].drop_duplicates().to_records(index=False)
    for md in missing:
        poly = boundary[boundary['DISTRICT_NAME_clean'] == md]
        if poly.empty:
            continue
        poly_geom = poly.geometry.values[0]
        # neighbors: intersecting districts excluding itself
        neighbors = boundary[boundary.geometry.intersects(poly_geom) & (boundary['DISTRICT_NAME_clean'] != md)]
        neighbor_list = neighbors['DISTRICT_NAME_clean'].tolist()
        if not neighbor_list:
            # no neighbors found
            continue
        # for each year-month, compute mean of neighbors if available
        for y, m in ym_pairs:
            neigh_vals = df[(df['YEAR'] == int(y)) & (df['MONTH'] == int(m)) & (df['DISTRICT_NAME_clean'].isin(neighbor_list))]['RAINFALL']
            if not neigh_vals.empty:
                mean_val = float(neigh_vals.mean())
                # original display name from boundary
                orig_name = boundary.loc[boundary['DISTRICT_NAME_clean'] == md, 'DISTRICT_NAME'].values[0]
                filled_rows.append({
                    'YEAR': int(y),
                    'MONTH': int(m),
                    'DISTRICT_NAME': orig_name,
                    'RAINFALL': mean_val,
                    'DISTRICT_NAME_clean': md,
                    'FILLED': True
                })

# Create combined dataframe: original rows marked FILLED=False
df['FILLED'] = False
if filled_rows:
    df_filled = pd.concat([df, pd.DataFrame(filled_rows)], ignore_index=True, sort=False)
else:
    df_filled = df.copy()

# Recompute TIME and TIME_ISO for filled rows
if 'TIME' not in df_filled.columns:
    df_filled['TIME'] = pd.to_datetime(df_filled['YEAR'].astype(str) + '-' + df_filled['MONTH'].astype(str) + '-01')
df_filled['TIME_ISO'] = df_filled['TIME'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# --- Second-pass fill: nearest-neighbor by centroid for any remaining missing district-months
df_filled_final = df_filled.copy()
fill_actions = []

# prepare centroid lookup for districts using a projected CRS for accurate distances
try:
    proj_crs = 32643  # UTM zone 43N, appropriate for Delhi region
    boundary_proj = boundary.to_crs(epsg=proj_crs)
    cent_series = boundary_proj.geometry.centroid
    centroids = pd.DataFrame({
        'DISTRICT_NAME_clean': boundary['DISTRICT_NAME_clean'].values,
        'centroid_x': [c.x for c in cent_series],
        'centroid_y': [c.y for c in cent_series]
    }).set_index('DISTRICT_NAME_clean')
except Exception:
    # fallback to geographic centroids (less accurate for distances)
    boundary['centroid'] = boundary.geometry.centroid
    centroids = pd.DataFrame({
        'DISTRICT_NAME_clean': boundary['DISTRICT_NAME_clean'],
        'centroid_x': [c.x for c in boundary['centroid']],
        'centroid_y': [c.y for c in boundary['centroid']]
    }).set_index('DISTRICT_NAME_clean')

ym_pairs = df_filled_final[['YEAR', 'MONTH']].drop_duplicates().to_records(index=False)
all_districts = list(boundary['DISTRICT_NAME_clean'].unique())

for y, m in ym_pairs:
    present = df_filled_final[(df_filled_final['YEAR'] == int(y)) & (df_filled_final['MONTH'] == int(m))]['DISTRICT_NAME_clean'].unique().tolist()
    missing_now = [d for d in all_districts if d not in present]
    if not present:
        # nothing to fill from for this ym
        continue

    # build KDTree of centroids of present districts (only those that exist in centroids)
    present_in_centroids = [p for p in present if p in centroids.index]
    present_centroids = centroids.loc[present_in_centroids].dropna() if present_in_centroids else pd.DataFrame()
    if present_centroids.empty:
        # no centroids available to build tree for this year-month
        continue
    pts = np.vstack([present_centroids['centroid_x'].values, present_centroids['centroid_y'].values]).T
    tree = cKDTree(pts)

    for md in missing_now:
        if md not in centroids.index:
            # cannot find centroid for this district - skip
            continue
        target = centroids.loc[md]
        target_pt = np.array([target['centroid_x'], target['centroid_y']])
        dist, idx = tree.query(target_pt)
        nearest_d = present_centroids.index.values[idx]
        # get nearest district's value for this year-month
        val_ser = df_filled_final[(df_filled_final['YEAR'] == int(y)) & (df_filled_final['MONTH'] == int(m)) & (df_filled_final['DISTRICT_NAME_clean'] == nearest_d)]['RAINFALL']
        if not val_ser.empty:
            val = float(val_ser.iloc[0])
            orig_name = boundary.loc[boundary['DISTRICT_NAME_clean'] == md, 'DISTRICT_NAME'].values[0]
            df_filled_final = pd.concat([df_filled_final, pd.DataFrame([{
                'YEAR': int(y), 'MONTH': int(m), 'DISTRICT_NAME': orig_name, 'RAINFALL': val,
                'DISTRICT_NAME_clean': md, 'FILLED': True, 'FILLED_METHOD': 'nearest'
            }])], ignore_index=True, sort=False)
            fill_actions.append({'YEAR': int(y), 'MONTH': int(m), 'district': md, 'method': 'nearest', 'source': str(nearest_d)})

# mark filled method for neighbor averages if not present
if 'FILLED' in df_filled_final.columns and 'FILLED_METHOD' not in df_filled_final.columns:
    df_filled_final['FILLED_METHOD'] = df_filled_final.apply(lambda r: 'neighbor' if r.get('FILLED') else None, axis=1)

# Save filled CSV for reuse
out_filled = 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv'
df_filled_final.to_csv(out_filled, index=False)
print(f"✅ Filled CSV saved: {out_filled}")

# small report
report_df = pd.DataFrame(fill_actions)
if not report_df.empty:
    report_df.to_csv('coverage_fill_report.csv', index=False)
    print(f"✅ Fill actions reported: coverage_fill_report.csv ({len(report_df)} rows)")
else:
    print("No nearest-neighbor fills were required.")