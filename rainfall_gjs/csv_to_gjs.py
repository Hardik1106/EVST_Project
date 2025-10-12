import os
import geopandas as gpd
import pandas as pd

# Load your GeoJSON
geojson_path = "GeoJsons/Delhi_NCR_Districts_final.geojson"
districts = gpd.read_file(geojson_path)
districts = districts.to_crs(epsg=4326)

# Normalize district name field
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

os.makedirs("rainfall_gjs", exist_ok=True)
os.makedirs("rainfall_csv", exist_ok=True)

years = range(2013, 2025)
for year in years:
    csv_path = f"rainfall_csv/delhi_rainfall_districts_{year}.csv"
    if not os.path.exists(csv_path):
        print(f"⚠️  {csv_path} not found — skipping {year}.")
        continue

    rain = pd.read_csv(csv_path)

    # Ensure the rainfall DF has a district column; try common names
    if "DISTRICT_NAME" not in rain.columns:
        for cand in ["DISTRICT_NAME", "dtname", "district", "District"]:
            if cand in rain.columns:
                rain = rain.rename(columns={cand: "DISTRICT_NAME"})
                break

    # Attempt a direct merge on DISTRICT_NAME
    if set(rain["DISTRICT_NAME"]).issubset(set(districts["DISTRICT_NAME"])):
        merged = districts.merge(rain, on="DISTRICT_NAME", how="left")
    else:
        # Fallback: spatial join — convert rain to points if it has LATITUDE/LONGITUDE, else perform merge with fuzzy matching
        if {"LATITUDE", "LONGITUDE"}.issubset(rain.columns):
            gdf_points = gpd.GeoDataFrame(rain, geometry=gpd.points_from_xy(rain["LONGITUDE"], rain["LATITUDE"]), crs="EPSG:4326")
            try:
                merged = gpd.sjoin(districts, gdf_points, how="left", predicate="intersects")
            except Exception:
                merged = gpd.sjoin(districts, gdf_points, how="left", predicate="within")
        else:
            # As a last resort do a left merge and log a warning
            print(f"⚠️  District name mismatch for {year}; performing left merge (may have missing attributes).")
            merged = districts.merge(rain, on="DISTRICT_NAME", how="left")

    out_path = f"rainfall_gjs/delhi_ncr_rainfall_{year}.geojson"
    merged.to_file(out_path, driver="GeoJSON")
    print(f"✅ Saved GIS-ready GeoJSON → {out_path}")