import geopandas as gpd
import pandas as pd
import os
from difflib import get_close_matches

boundary_path = 'GeoJsons/Delhi_NCR_Districts_final.geojson'
filled_csv = 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv'
base_csv = 'delhi_ncr_rainfall_monthly_avg_2013_2024.csv'

if not os.path.exists(boundary_path):
    raise FileNotFoundError(boundary_path)

b = gpd.read_file(boundary_path).to_crs(epsg=4326)
# detect name column
name_col = None
for cand in ['NAME_2','DISTRICT_NAME','dtname','dt_name','district','District']:
    if cand in b.columns:
        name_col = cand
        break
if name_col is None:
    b['DISTRICT_NAME'] = b.index.astype(str)
else:
    if name_col != 'DISTRICT_NAME':
        b = b.rename(columns={name_col: 'DISTRICT_NAME'})

b['DISTRICT_NAME_clean'] = b['DISTRICT_NAME'].astype(str).str.strip().str.lower()
geo_names = sorted(b['DISTRICT_NAME_clean'].unique())
print(f'Canonical geo names ({len(geo_names)}): {geo_names}')

# load CSV
if os.path.exists(filled_csv):
    df = pd.read_csv(filled_csv)
    print('Loaded filled CSV')
elif os.path.exists(base_csv):
    df = pd.read_csv(base_csv)
    print('Loaded base CSV')
else:
    raise FileNotFoundError('No CSV found')

# ensure district clean column
if 'DISTRICT_NAME_clean' not in df.columns and 'DISTRICT_NAME' in df.columns:
    df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].astype(str).str.strip().str.lower()

csv_names = sorted(df['DISTRICT_NAME_clean'].unique())
print(f'CSV unique district names before: {csv_names}')

# Manual mapping for known variants
manual_map = {
    'gautambuddhanagar': 'gautam buddha nagar',
    'gurgaon': 'gurugram',
    'mewat': 'nuh',
    # add other known synonyms here if needed
}

# build mapping using manual_map then fuzzy match for others
mapping = {}
for name in csv_names:
    if name in geo_names:
        mapping[name] = name
    elif name in manual_map:
        mapping[name] = manual_map[name]
    else:
        matches = get_close_matches(name, geo_names, n=1, cutoff=0.7)
        mapping[name] = matches[0] if matches else name

# apply mapping
df['DISTRICT_NAME_clean_mapped'] = df['DISTRICT_NAME_clean'].map(mapping)

# For display, set canonical display name from boundary
canon_name_map = {r['DISTRICT_NAME_clean']: r['DISTRICT_NAME'] for _, r in b[['DISTRICT_NAME_clean','DISTRICT_NAME']].iterrows()}

def canonical_display(mapped_clean):
    return canon_name_map.get(mapped_clean, mapped_clean)

# replace display name column
df['DISTRICT_NAME_mapped'] = df['DISTRICT_NAME_clean_mapped'].apply(canonical_display)

# collapse duplicates by YEAR,MONTH,DISTRICT_NAME_mapped -> prefer original (FILLED==False) values when present
group_cols = ['DISTRICT_NAME_mapped']
if 'YEAR' in df.columns and 'MONTH' in df.columns:
    group_cols = ['YEAR', 'MONTH'] + group_cols

def collapse_group(g):
    # g is a DataFrame for a group; prefer original (FILLED==False) rows when available
    has_original = 'FILLED' in g.columns and any(g['FILLED'] == False)
    if has_original:
        originals = g[g['FILLED'] == False]
        rainfall = originals['RAINFALL'].mean()
        filled_flag = False
        filled_methods = ''
    else:
        rainfall = g['RAINFALL'].mean()
        filled_flag = bool(('FILLED' in g.columns) and any(g['FILLED'] == True))
        if 'FILLED_METHOD' in g.columns:
            filled_methods = ','.join(sorted(set([str(x) for x in g['FILLED_METHOD'].dropna()])))
        else:
            filled_methods = ''
    row = {}
    row['RAINFALL'] = rainfall
    row['FILLED'] = filled_flag
    row['FILLED_METHOD'] = filled_methods
    return pd.Series(row)

collapsed = df.groupby(group_cols).apply(collapse_group).reset_index()
# Restore column names to expected
collapsed = collapsed.rename(columns={'DISTRICT_NAME_mapped': 'DISTRICT_NAME'})
collapsed['DISTRICT_NAME_clean'] = collapsed['DISTRICT_NAME'].astype(str).str.strip().str.lower()

# ensure TIME fields
if 'YEAR' in collapsed.columns and 'MONTH' in collapsed.columns:
    collapsed['TIME'] = pd.to_datetime(collapsed['YEAR'].astype(str) + '-' + collapsed['MONTH'].astype(str) + '-01')
    collapsed['TIME_ISO'] = collapsed['TIME'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# save back
out = filled_csv
collapsed.to_csv(out, index=False)
print(f'Wrote harmonized filled CSV: {out}')

# quick re-check
geo_set = set(geo_names)
csv_set = set(collapsed['DISTRICT_NAME_clean'].unique())
missing_in_csv = sorted(list(geo_set - csv_set))
missing_in_geo = sorted(list(csv_set - geo_set))
print('Missing in CSV (after mapping):', missing_in_csv)
print('CSV-only (after mapping):', missing_in_geo)
