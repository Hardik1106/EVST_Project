import geopandas as gpd
import pandas as pd

# Load your GeoJSON
districts = gpd.read_file("GeoJsons/Delhi_NCR_Districts.geojson")

# Standardize name columns
districts = districts.rename(columns={"NAME_2": "DISTRICT_NAME"})

years = range(2013, 2025)
for year in years:
# Load rainfall data (aggregated CSV)
    rain = pd.read_csv("rainfall_csv/delhi_rainfall_districts_" + str(year) + ".csv")

    # Merge
    merged = districts.merge(rain, on="DISTRICT_NAME")

    # Save GIS-ready GeoJSON
    merged.to_file("rainfall_gjs/delhi_ncr_rainfall_" + str(year) + ".geojson", driver="GeoJSON")

    print("✅ Saved GIS-ready GeoJSON with rainfall attributes")