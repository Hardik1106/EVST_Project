import geopandas as gpd
import pandas as pd

years = range(2013, 2025)
boundary_path = "GeoJsons/Delhi_NCR_Districts.geojson"

# List to collect monthly averages for all years
all_data = []

for year in years:
    data_path = f"rainfall_gjs/delhi_ncr_rainfall_{year}.geojson"
    
    # Load data
    gdf = gpd.read_file(data_path)
    
    # Make sure TIME column is datetime
    if "TIME" in gdf.columns:
        gdf["TIME"] = pd.to_datetime(gdf["TIME"])
    else:
        raise ValueError(f"No 'TIME' column found in {data_path}")
    
    # Extract month
    gdf["MONTH"] = gdf["TIME"].dt.month
    
    # Group by district and month to get average rainfall
    monthly_avg = (
        gdf.groupby(["DISTRICT_NAME", "MONTH"])
           .agg({"RAINFALL": "mean"})
           .reset_index()
    )
    
    # Add year column
    monthly_avg["YEAR"] = year
    
    # Reorder columns
    monthly_avg = monthly_avg[["YEAR", "MONTH", "DISTRICT_NAME", "RAINFALL"]]
    
    all_data.append(monthly_avg)

# Combine all years
combined_df = pd.concat(all_data, ignore_index=True)

# Save to CSV
combined_csv_path = "delhi_ncr_rainfall_monthly_avg_2013_2024.csv"
combined_df.to_csv(combined_csv_path, index=False)
print(f"✅ Combined monthly average CSV saved: {combined_csv_path}")
