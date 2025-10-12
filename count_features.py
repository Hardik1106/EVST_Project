import geopandas as gpd
import pandas as pd
import os

boundary_path = 'GeoJsons/Delhi_NCR_Districts_final.geojson'
filled_csv = 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv'

b = gpd.read_file(boundary_path).to_crs(epsg=4326)
# normalize name col
name_col = None
for cand in ['dtname','NAME_2','DISTRICT_NAME','dt_name','district','District']:
    if cand in b.columns:
        name_col = cand
        break
if name_col is None:
    b['DISTRICT_NAME'] = b.index.astype(str)
else:
    if name_col != 'DISTRICT_NAME':
        b = b.rename(columns={name_col: 'DISTRICT_NAME'})

b['DISTRICT_NAME_clean'] = b['DISTRICT_NAME'].astype(str).str.strip().str.lower()

if not os.path.exists(filled_csv):
    raise FileNotFoundError('filled csv missing')

df = pd.read_csv(filled_csv)
if 'DISTRICT_NAME_clean' not in df.columns and 'DISTRICT_NAME' in df.columns:
    df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].astype(str).str.strip().str.lower()

# ensure TIME_ISO
if 'TIME_ISO' not in df.columns and 'YEAR' in df.columns and 'MONTH' in df.columns:
    df['TIME'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')
    df['TIME_ISO'] = df['TIME'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# build features count
counts = {}
for district_name_clean, polygons in b.groupby('DISTRICT_NAME_clean'):
    district_data = df[df['DISTRICT_NAME_clean'] == district_name_clean]
    num_features = 0
    for _, polygon in polygons.iterrows():
        for _, row in district_data.iterrows():
            num_features += 1
    counts[district_name_clean] = num_features

# Print few districts
for k in sorted(counts.keys()):
    if k in ['faridabad','gautam buddha nagar','gurugram']:
        print(k, counts[k])

# show districts with zero features
zeros = [k for k,v in counts.items() if v==0]
print('\nDistricts with zero features:', zeros)
