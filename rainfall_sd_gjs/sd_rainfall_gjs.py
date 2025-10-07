import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping

years = range(2013, 2025)
# --- FILE PATHS ---
boundary_path = "GeoJsons/Delhi_NCR_Districts.geojson"

for year in years:
    raw_data_path = "rainfall_gjs/delhi_ncr_rainfall_" + str(year) + ".geojson"
    output_path = "rainfall_sd_gjs/delhi_ncr_rainfall_" + str(year) + "_standardized.geojson"

    # --- LOAD DATA ---
    gdf = gpd.read_file(raw_data_path)
    boundary = gpd.read_file(boundary_path)

    # --- ENSURE CRS IS WGS84 ---
    gdf = gdf.to_crs(epsg=4326)
    boundary = boundary.to_crs(epsg=4326)

    # --- CLIP TO NCR DISTRICTS ---
    gdf = gpd.clip(gdf, boundary)

    # --- STANDARDIZE TIME COLUMN ---
    gdf["TIME"] = pd.to_datetime(gdf["TIME"], errors="coerce").dt.strftime("%Y-%m-%d")

    # --- STANDARDIZE RAINFALL ---
    # Min-max normalization for visualization
    gdf["RAINFALL_STD"] = (gdf["RAINFALL"] - gdf["RAINFALL"].min()) / (gdf["RAINFALL"].max() - gdf["RAINFALL"].min())

    # Optional: Z-score standardization (for analytics)
    #gdf["RAINFALL_Z"] = (gdf["RAINFALL"] - gdf["RAINFALL"].mean()) / gdf["RAINFALL"].std()

    # --- SIMPLIFY GEOMETRIES ---
    gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.002, preserve_topology=True)

    # --- SAVE STANDARDIZED GEOJSON ---
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"✅ Standardized GeoJSON saved: {output_path}")
