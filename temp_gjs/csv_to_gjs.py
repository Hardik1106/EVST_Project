import geopandas as gpd
import pandas as pd
import os

# Paths
geojson_path = "GeoJsons/Delhi_NCR_Districts.geojson"
temp_csv_dir = "temp_csv"          # folder containing mergedT_2013.csv etc.
output_dir = "temp_gjs"            # folder to save output geojsons
os.makedirs(output_dir, exist_ok=True)

# Load district GeoJSON
districts = gpd.read_file(geojson_path)

# Standardize district name column
districts = districts.rename(columns={"NAME_2": "DISTRICT_NAME"})

# Optional normalization (if some names differ, e.g., "West" → "Delhi")
districts["DISTRICT_NAME"] = districts["DISTRICT_NAME"].replace({"West": "Delhi"})

# Loop through each year
for year in range(2013, 2025):
    csv_path = os.path.join(temp_csv_dir, f"Temperature_{year}.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️ CSV for {year} not found, skipping...")
        continue

    # Load temperature data
    temp_df = pd.read_csv(csv_path)

    # Merge GeoDataFrame with temperature CSV on district name
    merged = districts.merge(temp_df, on="DISTRICT_NAME", how="left")

    # Save to GeoJSON
    output_path = os.path.join(output_dir, f"delhi_ncr_temp_{year}.geojson")
    merged.to_file(output_path, driver="GeoJSON")

    print(f"✅ Saved GeoJSON for {year}: {output_path}")
