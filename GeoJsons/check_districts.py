import geopandas as gpd
import pandas as pd

geo_path = 'GeoJsons/Delhi_NCR_Districts_final.geojson'
filled_csv = 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv'
base_csv = 'delhi_ncr_rainfall_monthly_avg_2013_2024.csv'

print('Reading geojson...')
b = gpd.read_file(geo_path).to_crs(epsg=4326)
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
print(f'Geo districts ({len(geo_names)}):')
print(geo_names)

# load filled CSV if present, else base
import os
if os.path.exists(filled_csv):
    df = pd.read_csv(filled_csv)
    print('Loaded filled CSV')
else:
    df = pd.read_csv(base_csv)
    print('Loaded base CSV')

# normalize df
if 'DISTRICT_NAME_clean' not in df.columns and 'DISTRICT_NAME' in df.columns:
    df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].astype(str).str.strip().str.lower()

csv_names = sorted(df['DISTRICT_NAME_clean'].unique())
print(f'CSV districts ({len(csv_names)}):')
print(csv_names)

geo_set = set(geo_names)
csv_set = set(csv_names)
missing_in_csv = sorted(list(geo_set - csv_set))
missing_in_geo = sorted(list(csv_set - geo_set))

print('\nDistricts present in geojson but NOT in CSV (missing_in_csv):')
print(missing_in_csv)
print('\nDistricts present in CSV but NOT in geojson (missing_in_geo):')
print(missing_in_geo)

# attempt fuzzy matches for missing_in_csv
from difflib import get_close_matches
print('\nFuzzy matches for missing geo districts:')
for name in missing_in_csv:
    matches = get_close_matches(name, csv_names, n=3, cutoff=0.6)
    print(name, '->', matches)

print('\nDone')
