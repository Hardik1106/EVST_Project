import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping
import os

years = range(2013, 2025)

# --- FILE PATHS ---
boundary_path = "GeoJsons/Delhi_NCR_Districts.geojson"
raw_dir = "temp_gjs"             # folder where delhi_ncr_temp_2013.geojson etc. are stored
output_dir = "temp_sd_gjs"       # standardized outputs
os.makedirs(output_dir, exist_ok=True)

for year in years:
    raw_data_path = os.path.join(raw_dir, f"delhi_ncr_temp_{year}.geojson")
    output_path = os.path.join(output_dir, f"delhi_ncr_temp_{year}_standardized.geojson")

    if not os.path.exists(raw_data_path):
        print(f"⚠️ GeoJSON for {year} not found, skipping...")
        continue

    # --- LOAD DATA ---
    gdf = gpd.read_file(raw_data_path)
    boundary = gpd.read_file(boundary_path)

    # --- ENSURE CRS IS WGS84 ---
    gdf = gdf.to_crs(epsg=4326)
    boundary = boundary.to_crs(epsg=4326)

    # --- CLIP TO NCR DISTRICTS ---
    gdf = gpd.clip(gdf, boundary)

    # --- STANDARDIZE DATE COLUMN ---
    # rename if needed (some CSVs might use 'date' lowercase)
    if "date" in gdf.columns:
        gdf["date"] = pd.to_datetime(gdf["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    elif "TIME" in gdf.columns:
        gdf["date"] = pd.to_datetime(gdf["TIME"], errors="coerce").dt.strftime("%Y-%m-%d")

    # --- STANDARDIZE TEMPERATURE ---
    # Min-max normalization for visualization
    gdf["minT_STD"] = (gdf["minT"] - gdf["minT"].min()) / (gdf["minT"].max() - gdf["minT"].min())
    gdf["maxT_STD"] = (gdf["maxT"] - gdf["maxT"].min()) / (gdf["maxT"].max() - gdf["maxT"].min())

    # Optional: Z-score normalization (useful for analytics)
    # gdf["minT_Z"] = (gdf["minT"] - gdf["minT"].mean()) / gdf["minT"].std()
    # gdf["maxT_Z"] = (gdf["maxT"] - gdf["maxT"].mean()) / gdf["maxT"].std()

    # --- SIMPLIFY GEOMETRIES ---
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.002, preserve_topology=True)

    # --- SAVE STANDARDIZED GEOJSON ---
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"✅ Standardized temperature GeoJSON saved: {output_path}")
