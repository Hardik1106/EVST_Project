import xarray as xr 
import geopandas as gpd 
import pandas as pd 
from shapely.geometry import Point 
 
# Paths 
file_path = "rainfall_NetCDF/RF25_ind2024_rfp25.nc" 
geojson_path = "GeoJsons/Delhi_NCR_Districts.geojson" 
output_dir = "rainfall_csv/" 
 
# Load GeoJSON 
districts = gpd.read_file(geojson_path) 
districts = districts.to_crs(epsg=4326) 
 
# Normalize common district name fields to `DISTRICT_NAME`
possible_name_cols = [c for c in districts.columns]
name_col = None
for cand in ["DISTRICT_NAME", "NAME_2", "dtname", "dt_name", "district", "District"]:
    if cand in possible_name_cols:
        name_col = cand
        break
if name_col and name_col != "DISTRICT_NAME":
    districts = districts.rename(columns={name_col: "DISTRICT_NAME"})
elif not name_col:
    districts["DISTRICT_NAME"] = districts.index.astype(str)
 
# Define Delhi NCR bounding box 
lat_bounds = slice(27.5, 29.5) 
lon_bounds = slice(76.5, 78.5) 

print("Processing 2024...")
 
# Open dataset - 2024 uses lowercase variable names
ds = xr.open_dataset(file_path)

# 2024 uses: 'rf' (not RAINFALL), 'lat' (not LATITUDE), 'lon' (not LONGITUDE), 'time' (not TIME)
rain = ds["rf"]
delhi_rain = rain.sel(lat=lat_bounds, lon=lon_bounds)
 
# Convert to DataFrame
df = delhi_rain.to_dataframe().reset_index()

# Rename to standard names for consistency
df = df.rename(columns={
    'lat': 'LATITUDE',
    'lon': 'LONGITUDE', 
    'rf': 'RAINFALL',
    'time': 'TIME'
})

# Drop NaN values
df = df.dropna(subset=["RAINFALL"])

# Create GeoDataFrame
gdf = gpd.GeoDataFrame( 
    df, 
    geometry=gpd.points_from_xy(df["LONGITUDE"], df["LATITUDE"]), 
    crs="EPSG:4326" 
) 
 
# Spatial join: prefer 'intersects' to include boundary points; fallback to 'within'
try:
    joined = gpd.sjoin(gdf, districts, how="inner", predicate="intersects")
except Exception:
    joined = gpd.sjoin(gdf, districts, how="inner", predicate="within")

# Ensure DISTRICT_NAME exists
if "DISTRICT_NAME" not in joined.columns:
    print("Warning: 'DISTRICT_NAME' not found in joined GeoDataFrame. Columns:", joined.columns.tolist())

# Detect TIME column case-insensitively
time_col = None
for c in joined.columns:
    if str(c).lower() == "time":
        time_col = c
        break

if time_col is not None:
    agg = joined.groupby(["DISTRICT_NAME", time_col])["RAINFALL"].mean().reset_index()
    if time_col != "TIME":
        agg = agg.rename(columns={time_col: "TIME"})
else:
    agg = joined.groupby(["DISTRICT_NAME"])["RAINFALL"].mean().reset_index()

# Ensure output directory exists
import os
os.makedirs(output_dir, exist_ok=True)
 
# Save to CSV
agg.to_csv(f"{output_dir}delhi_rainfall_districts_2024.csv", index=False) 
 
print(f"✅ Saved: {output_dir}delhi_rainfall_districts_2024.csv")
print(f"✅ Total rows: {len(agg)}")
print(f"✅ Districts: {agg['DISTRICT_NAME'].nunique()}")
print(f"✅ Time steps: {agg['TIME'].nunique()}")