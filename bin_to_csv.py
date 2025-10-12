import os
import warnings
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
geojson_path = os.path.join("GeoJsons", "Delhi_NCR_Districts_final.geojson")
if not os.path.exists(geojson_path):
    raise FileNotFoundError(f"GeoJSON not found: {geojson_path}")
districts = gpd.read_file(geojson_path)
districts = districts.to_crs(epsg=4326)

# normalize district name column (handle dtname and other variants)
name_col = None
for cand in ["dtname", "NAME_2", "DISTRICT_NAME", "dt_name", "district", "District"]:
    if cand in districts.columns:
        name_col = cand
        break
if name_col is None:
    # fallback: use index as district name
    districts['DISTRICT_NAME'] = districts.index.astype(str)
else:
    if name_col != 'DISTRICT_NAME':
        districts = districts.rename(columns={name_col: 'DISTRICT_NAME'})

# ensure there are no empty geometries
empty_geom = districts['geometry'].is_empty.sum()
if empty_geom:
    warnings.warn(f"GeoJSON contains {empty_geom} empty geometries; these will be skipped.")
    districts = districts[~districts['geometry'].is_empty]

# --- MAIN LOOP ---
for year in years:
    if year in lpyears:
        n_days = 366
    else:
        n_days = 365
    print(f"Processing {year}...")

    # Read binary file
    file_path = f"maxT_GRD\MaxTemp_MaxT_{year}.GRD"
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

    # Spatial join with districts (use intersects to be robust; fallback to within)
    try:
        joined = gpd.sjoin(points, districts[['DISTRICT_NAME', 'geometry']], how="inner", predicate="intersects")
    except Exception:
        joined = gpd.sjoin(points, districts[['DISTRICT_NAME', 'geometry']], how="inner", predicate="within")

    # For each day, extract the temperature at grid indices that fall inside each district
    # Map the flattened grid index to array indices
    lat_indices = [int(np.argmin(np.abs(lats - lat))) for lat in joined["LATITUDE"]]
    lon_indices = [int(np.argmin(np.abs(lons - lon))) for lon in joined["LONGITUDE"]]

    # Prepare storage
    results = []

    for day in range(n_days):
        temp_grid = data[day, :, :]  # shape (n_lat, n_lon)

        # Safely extract temperature values; if indices are out-of-range use NaN
        temps = []
        for lat_i, lon_i in zip(lat_indices, lon_indices):
            try:
                val = temp_grid[lat_i, lon_i]
                if np.isfinite(val):
                    temps.append(float(val))
                else:
                    temps.append(np.nan)
            except Exception:
                temps.append(np.nan)

        joined = joined.copy()
        joined["TEMP"] = temps

        # Average per district
        day_avg = joined.groupby("DISTRICT_NAME")["TEMP"].mean().reset_index()
        day_avg["date"] = pd.Timestamp(f"{year}-01-01") + pd.Timedelta(days=day)
        results.append(day_avg)

    # Combine all days
    full_df = pd.concat(results, ignore_index=True)

    # Save CSV
    output_dir = os.path.join('maxT_csv')
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, f"Delhi_MaxTemp_Districts_{year}.csv")
    full_df.to_csv(output_csv, index=False)
    print(f"✅ Saved per-district max temperature for {year} → {output_csv}")

print("🎯 All years processed successfully!")
