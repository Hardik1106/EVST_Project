import os
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist

# --- CONFIG ---
YEARS = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
LPYEARS = [2016, 2020, 2024]

# Input CSV templates (these should already exist from previous steps)
MIN_CSV_TPL = os.path.join('minT_csv', 'Delhi_MinTemp_Districts_{year}.csv')
MAX_CSV_TPL = os.path.join('maxT_csv', 'Delhi_MaxTemp_Districts_{year}.csv')

OUT_DIR = 'temp_csv'
os.makedirs(OUT_DIR, exist_ok=True)

# Load districts GeoJSON and normalize name column
GEOJSON_PATH = os.path.join('GeoJsons', 'Delhi_NCR_Districts_final.geojson')
if not os.path.exists(GEOJSON_PATH):
    raise FileNotFoundError(GEOJSON_PATH)
districts = gpd.read_file(GEOJSON_PATH).to_crs(epsg=4326)
name_col = None
for cand in ['dtname', 'NAME_2', 'DISTRICT_NAME', 'dt_name', 'district', 'District']:
    if cand in districts.columns:
        name_col = cand
        break
if name_col is None:
    districts['DISTRICT_NAME'] = districts.index.astype(str)
else:
    if name_col != 'DISTRICT_NAME':
        districts = districts.rename(columns={name_col: 'DISTRICT_NAME'})

districts['DISTRICT_NAME_clean'] = districts['DISTRICT_NAME'].astype(str).str.strip().str.lower()

# Precompute projected centroids for IDW
proj_crs = 32643
districts_proj = districts.to_crs(epsg=proj_crs)
districts_proj['centroid'] = districts_proj.geometry.centroid
centroids = districts_proj['centroid'].apply(lambda p: (p.x, p.y)).tolist()
centroid_names = districts_proj['DISTRICT_NAME_clean'].tolist()
centroid_coords = np.array(centroids)

def idw_fill(target_point, donor_points, donor_values, k=3, eps=1e-6):
    # inverse distance weighting: donor_points is Nx2, donor_values is N
    if len(donor_points) == 0:
        return np.nan
    dists = np.linalg.norm(donor_points - target_point, axis=1)
    # avoid zero distances
    dists = np.maximum(dists, eps)
    idx = np.argsort(dists)[:k]
    weights = 1.0 / dists[idx]
    vals = donor_values[idx]
    return float(np.sum(weights * vals) / np.sum(weights))

for year in YEARS:
    print(f"Processing temperatures for {year}...")
    n_days = 366 if year in LPYEARS else 365

    min_csv = MIN_CSV_TPL.format(year=year)
    max_csv = MAX_CSV_TPL.format(year=year)
    if not os.path.exists(min_csv) or not os.path.exists(max_csv):
        warnings.warn(f"Missing CSV for year {year}: {min_csv} or {max_csv} not found — skipping")
        continue

    min_df = pd.read_csv(min_csv)
    max_df = pd.read_csv(max_csv)

    # Normalize district names in input CSVs
    for df in (min_df, max_df):
        if 'DISTRICT_NAME' in df.columns:
            df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].astype(str).str.strip().str.lower()
        else:
            raise ValueError(f"Input CSV {min_csv} missing DISTRICT_NAME column")

    # Detect value columns in min/max data and rename to minT/maxT
    def detect_value_col(df, prefer_contains=None):
        # prefer_contains: list of substrings indicating the desired column
        prefer_contains = prefer_contains or []
        cols = [c for c in df.columns if c not in ('DISTRICT_NAME','DISTRICT_NAME_clean','date')]
        if not cols:
            return None
        # If only one candidate, return it
        if len(cols) == 1:
            return cols[0]
        lowmap = {c.lower(): c for c in cols}
        for substr in prefer_contains:
            for lc, orig in lowmap.items():
                if substr in lc:
                    return orig
        # fallback: choose first numeric column
        for c in cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                return c
        return cols[0]

    min_val_col = detect_value_col(min_df, prefer_contains=['min','tmin','mintemp','value'])
    max_val_col = detect_value_col(max_df, prefer_contains=['max','tmax','maxtemp','value'])
    if min_val_col is None or max_val_col is None:
        raise ValueError(f"Could not detect value column in {min_csv} or {max_csv}")
    # rename to canonical names
    if min_val_col != 'minT':
        min_df = min_df.rename(columns={min_val_col: 'minT'})
    if max_val_col != 'maxT':
        max_df = max_df.rename(columns={max_val_col: 'maxT'})

    # Merge min and max on district and date (assumes both CSVs have same daily rows per district)
    merged = pd.merge(min_df[['DISTRICT_NAME_clean','date','minT']], max_df[['DISTRICT_NAME_clean','date','maxT']], on=['DISTRICT_NAME_clean', 'date'], how='outer')

    # Some CSVs may have different date formats; normalize
    merged['date'] = pd.to_datetime(merged['date'])
    # Keep TIME_ISO where available; otherwise will be recomputed from full['date'] later
    merged['TIME_ISO'] = merged['date'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Pivot to have rows per (district, date)
    # Ensure we have an entry for every district in the GeoJSON for every date
    all_districts = districts['DISTRICT_NAME_clean'].unique().tolist()
    all_dates = pd.date_range(start=f'{year}-01-01', periods=n_days, freq='D')
    full_index = pd.MultiIndex.from_product([all_districts, all_dates], names=['DISTRICT_NAME_clean', 'date'])
    full = pd.DataFrame(index=full_index).reset_index()

    # merged should already have minT and maxT columns
    if 'minT' not in merged.columns or 'maxT' not in merged.columns:
        raise ValueError(f"After detection merged is missing minT or maxT columns for year {year}")
    full = full.merge(merged[['DISTRICT_NAME_clean','date','minT','maxT','TIME_ISO']], on=['DISTRICT_NAME_clean','date'], how='left')

    # Mark which rows have original data
    full['FILLED'] = full['minT'].isna() | full['maxT'].isna()

    # First-pass fill: neighbor averaging using polygon intersections
    # Build spatial index for neighbors
    districts_sindex = districts.sindex

    for idx, row in full[full['FILLED']].iterrows():
        dname = row['DISTRICT_NAME_clean']
        d_geom = districts.loc[districts['DISTRICT_NAME_clean'] == dname, 'geometry']
        if d_geom.empty:
            continue
        d_geom = d_geom.iloc[0]
        possible_idx = list(districts_sindex.intersection(d_geom.bounds))
        neighbors = districts.iloc[possible_idx]
        neighbors = neighbors[neighbors.geometry.intersects(d_geom) & (neighbors['DISTRICT_NAME_clean'] != dname)]
        neighbor_names = neighbors['DISTRICT_NAME_clean'].tolist()
        if not neighbor_names:
            continue
        # collect neighbor values for the same date
        same_date = full[(full['date'] == row['date']) & (full['DISTRICT_NAME_clean'].isin(neighbor_names))]
        if same_date['minT'].notna().any():
            full.at[idx,'minT'] = same_date['minT'].mean()
        if same_date['maxT'].notna().any():
            full.at[idx,'maxT'] = same_date['maxT'].mean()

    # Second-pass fill: IDW using k nearest centroids with available data
    for idx, row in full[full['FILLED'] & (full['minT'].isna() | full['maxT'].isna())].iterrows():
        dname = row['DISTRICT_NAME_clean']
        # find centroid coords
        try:
            target_idx = centroid_names.index(dname)
            target_pt = centroid_coords[target_idx]
        except ValueError:
            continue
        # donors with data for that date (either minT or maxT available)
        donors = full[(full['date'] == row['date']) & (full['DISTRICT_NAME_clean'] != dname) & (full['minT'].notna() | full['maxT'].notna())]
        if donors.empty:
            continue
        donor_names = donors['DISTRICT_NAME_clean'].tolist()
        donor_coords = np.array([centroid_coords[centroid_names.index(n)] for n in donor_names])
        if full.at[idx,'minT'] is np.nan or pd.isna(full.at[idx,'minT']):
            donor_vals = donors['minT'].ffill().bfill().values
            try:
                filled_val = idw_fill(np.array(target_pt), donor_coords, donor_vals, k=5)
                full.at[idx,'minT'] = filled_val
            except Exception:
                pass
        if full.at[idx,'maxT'] is np.nan or pd.isna(full.at[idx,'maxT']):
            donor_vals = donors['maxT'].ffill().bfill().values
            try:
                filled_val = idw_fill(np.array(target_pt), donor_coords, donor_vals, k=5)
                full.at[idx,'maxT'] = filled_val
            except Exception:
                pass

    # After filling, mark FILLED rows properly
    full['FILLED'] = full['minT'].isna() | full['maxT'].isna()
    full['FILLED_METHOD'] = full['FILLED'].apply(lambda x: 'original' if not x else 'filled')

    # Restore display district name from GeoJSON
    canon_map = dict(zip(districts['DISTRICT_NAME_clean'], districts['DISTRICT_NAME']))
    full['DISTRICT_NAME'] = full['DISTRICT_NAME_clean'].map(canon_map)

    # Ensure TIME_ISO exists for all rows (recompute from date if necessary)
    if 'TIME_ISO' not in full.columns or full['TIME_ISO'].isna().any():
        full['TIME_ISO'] = full['date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    out_path = os.path.join(OUT_DIR, f'Temperature_{year}.csv')
    full[['DISTRICT_NAME','DISTRICT_NAME_clean','date','TIME_ISO','minT','maxT','FILLED','FILLED_METHOD']].to_csv(out_path, index=False)
    print(f"✅ Saved extrapolated temperatures for {year} → {out_path}")
