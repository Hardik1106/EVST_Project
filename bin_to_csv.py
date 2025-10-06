import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# --- CONFIG ---
years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
lpyears = [2016, 2020, 2024]  # leap years
n_lat, n_lon = 31, 31

# Define coordinate ranges (from IMD grid info)
lats = np.linspace(6.5, 38.5, n_lat)
lons = np.linspace(66.5, 100.0, n_lon)

# Delhi NCR bounding box
lat_min, lat_max = 27.5, 29.5
lon_min, lon_max = 76.5, 78.5

# Load GeoJSON (Delhi NCR districts)
geojson_path = "GeoJsons/Delhi_NCR_Districts.geojson"
districts = gpd.read_file(geojson_path)
districts = districts.to_crs(epsg=4326)
if "NAME_2" in districts.columns:
    districts = districts.rename(columns={"NAME_2": "DISTRICT_NAME"})

# --- MAIN LOOP ---
for year in years:
    if year in lpyears:
        n_days = 366
    else:
        n_days = 365
    print(f"Processing {year}...")

    # Read binary file
    file_path = f"minT_GRD\MinTemp_MinT_{year}.GRD"
    data = np.fromfile(file_path, dtype=np.float32).reshape(n_days, n_lat, n_lon)

    # Create coordinate mesh for all grid points
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Flatten spatial grid
    coords = pd.DataFrame({
        "LATITUDE": lat_grid.ravel(),
        "LONGITUDE": lon_grid.ravel()
    })

    # Subset Delhi NCR region
    coords = coords[(coords["LATITUDE"] >= lat_min) & (coords["LATITUDE"] <= lat_max) &
                    (coords["LONGITUDE"] >= lon_min) & (coords["LONGITUDE"] <= lon_max)]

    # Convert grid to GeoDataFrame
    points = gpd.GeoDataFrame(coords, geometry=gpd.points_from_xy(coords["LONGITUDE"], coords["LATITUDE"]), crs="EPSG:4326")

    # Spatial join with districts
    joined = gpd.sjoin(points, districts, how="inner", predicate="within")

    # For each day, extract the temperature at grid indices that fall inside each district
    # Map the flattened grid index to array indices
    lat_indices = [np.argmin(np.abs(lats - lat)) for lat in joined["LATITUDE"]]
    lon_indices = [np.argmin(np.abs(lons - lon)) for lon in joined["LONGITUDE"]]

    # Prepare storage
    results = []

    for day in range(n_days):
        temp_grid = data[day, :, :]  # shape (n_lat, n_lon)
        joined["TEMP"] = [temp_grid[lat_i, lon_i] for lat_i, lon_i in zip(lat_indices, lon_indices)]

        # Average per district
        day_avg = joined.groupby("DISTRICT_NAME")["TEMP"].mean().reset_index()
        day_avg["date"] = pd.Timestamp(f"{year}-01-01") + pd.Timedelta(days=day)
        results.append(day_avg)

    # Combine all days
    full_df = pd.concat(results, ignore_index=True)

    # Save CSV
    output_csv = f"minT_csv/Delhi_MinTemp_Districts_{year}.csv"
    full_df.to_csv(output_csv, index=False)
    print(f"✅ Saved per-district min temperature for {year} → {output_csv}")

print("🎯 All years processed successfully!")
