import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# --- CONFIG ---
year = 2013
lpyears = [2016, 2020, 2024]
n_lat, n_lon = 31, 31

lats = np.linspace(6.5, 38.5, n_lat)
lons = np.linspace(66.5, 100.0, n_lon)

# Load GeoJSON for all districts in India
geojson_path = "GeoJsons/INDIA.json"  # replace with your full India districts file
districts = gpd.read_file(geojson_path)
districts = districts.to_crs(epsg=4326)
if "NAME_2" in districts.columns:
    districts = districts.rename(columns={"NAME_2": "DISTRICT_NAME"})

# --- Read the binary data for the year ---
n_days = 366 if year in lpyears else 365
file_path = f"minT_GRD/MinTemp_MinT_{year}.GRD"
data = np.fromfile(file_path, dtype=np.float32).reshape(n_days, n_lat, n_lon)

# Create coordinate mesh for all grid points
lon_grid, lat_grid = np.meshgrid(lons, lats)
coords = pd.DataFrame({
    "LATITUDE": lat_grid.ravel(),
    "LONGITUDE": lon_grid.ravel()
})

# Convert all grid points to GeoDataFrame
points = gpd.GeoDataFrame(coords, geometry=gpd.points_from_xy(coords["LONGITUDE"], coords["LATITUDE"]), crs="EPSG:4326")

# --- Spatial join with all districts ---
joined = gpd.sjoin(points, districts, how="inner", predicate="intersects")

# Count grid points per district
district_counts = joined['DISTRICT_NAME'].value_counts()

print(f"\nYear {year} - districts present in binary:")
for district, count in district_counts.items():
    print(f" - {district}: {count} grid points")

print(f"\nTotal districts with data in binary: {len(district_counts)}")
