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
 
# Standardize the district name column 
if "NAME_2" in districts.columns: 
    districts = districts.rename(columns={"NAME_2": "DISTRICT_NAME"})
 
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
 
# Spatial join 
joined = gpd.sjoin(gdf, districts, how="inner", predicate="within") 
 
# Aggregate by district and time
agg = joined.groupby(["DISTRICT_NAME", "TIME"])["RAINFALL"].mean().reset_index()
 
# Save to CSV
agg.to_csv(f"{output_dir}delhi_rainfall_districts_2024.csv", index=False) 
 
print(f"✅ Saved: {output_dir}delhi_rainfall_districts_2024.csv")
print(f"✅ Total rows: {len(agg)}")
print(f"✅ Districts: {agg['DISTRICT_NAME'].nunique()}")
print(f"✅ Time steps: {agg['TIME'].nunique()}")