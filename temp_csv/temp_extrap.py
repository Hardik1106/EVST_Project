import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import cKDTree

# --- CONFIG ---
years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
lpyears = [2016, 2020, 2024]
n_lat, n_lon = 31, 31

lats = np.linspace(6.5, 38.5, n_lat)
lons = np.linspace(66.5, 100.0, n_lon)

# Load districts GeoJSON
geojson_path = "GeoJsons/Delhi_NCR_Districts.geojson"
districts = gpd.read_file(geojson_path)
districts = districts.to_crs(epsg=4326)
if "NAME_2" in districts.columns:
    districts = districts.rename(columns={"NAME_2": "DISTRICT_NAME"})

for year in years:
    # --- Read binary min and max temperature files ---
    n_days = 366 if year in lpyears else 365

    min_file_path = f"minT_GRD/MinTemp_MinT_{year}.GRD"
    max_file_path = f"maxT_GRD/MaxTemp_MaxT_{year}.GRD"

    min_data = np.fromfile(min_file_path, dtype=np.float32).reshape(n_days, n_lat, n_lon)
    max_data = np.fromfile(max_file_path, dtype=np.float32).reshape(n_days, n_lat, n_lon)

    # Create grid points GeoDataFrame
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    coords = pd.DataFrame({
        "LATITUDE": lat_grid.ravel(),
        "LONGITUDE": lon_grid.ravel()
    })
    data_gdf = gpd.GeoDataFrame(coords, geometry=gpd.points_from_xy(coords["LONGITUDE"], coords["LATITUDE"]), crs="EPSG:4326")

    # --- Project to UTM for accurate centroid/distance calculations ---
    utm_crs = 32643  # UTM zone for Delhi/NCR
    data_gdf_proj = data_gdf.to_crs(epsg=utm_crs)
    districts_proj = districts.to_crs(epsg=utm_crs)

    # Compute district centroids in projected CRS
    districts_proj["centroid"] = districts_proj.geometry.centroid
    district_centroids = np.array(list(zip(districts_proj.centroid.x, districts_proj.centroid.y)))

    # Compute all grid points coordinates in projected CRS
    grid_points = np.array(list(zip(data_gdf_proj.geometry.x, data_gdf_proj.geometry.y)))

    # Build a KDTree for nearest-neighbor search
    tree = cKDTree(grid_points)

    # Find nearest grid point for each district centroid
    _, nearest_idx = tree.query(district_centroids)

    # --- Extract min and max temperatures per district ---
    results = []
    for day in range(n_days):
        min_flat = min_data[day, :, :].ravel()
        max_flat = max_data[day, :, :].ravel()
        
        day_df = pd.DataFrame({
            "DISTRICT_NAME": districts_proj["DISTRICT_NAME"],
            "date": pd.Timestamp(f"{year}-01-01") + pd.Timedelta(days=day),
            "minT": min_flat[nearest_idx],
            "maxT": max_flat[nearest_idx]
        })
        results.append(day_df)

    # Combine all days
    full_df = pd.concat(results, ignore_index=True)

    # Save CSV
    output_csv = f"temp_csv/Temperature_{year}.csv"
    full_df.to_csv(output_csv, index=False)
    print(f"✅ Saved combined min/max temperature CSV → {output_csv}")
