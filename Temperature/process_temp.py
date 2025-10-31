import pandas as pd
import os
import geopandas as gpd

# --- CONFIG ---
years = range(2013, 2025)
boundary_path = "GeoJsons/Delhi_NCR_Districts_final.geojson"
temp_csv_dir = "temp_csv"   # folder containing Temperature_{year}.csv
output_csv = "delhi_ncr_temp_monthly_avg_2013_2024.csv"

# Load complete district list from boundary
boundary = gpd.read_file(boundary_path)
# Detect district name column in the GeoJSON (new format uses 'dtname')
name_col = None
for cand in ['dtname', 'NAME_2', 'DISTRICT_NAME', 'dt_name', 'district', 'District']:
    if cand in boundary.columns:
        name_col = cand
        break
if name_col is None:
    # fallback: create a DISTRICT_NAME from the feature index
    boundary['DISTRICT_NAME'] = boundary.index.astype(str)
else:
    if name_col != 'DISTRICT_NAME':
        boundary = boundary.rename(columns={name_col: 'DISTRICT_NAME'})

# normalize spacing (keep case as-is to match temp CSV 'DISTRICT_NAME' produced earlier)
boundary['DISTRICT_NAME'] = boundary['DISTRICT_NAME'].astype(str).str.strip()
all_districts_df = pd.DataFrame({"DISTRICT_NAME": boundary["DISTRICT_NAME"]})

all_data = []

for year in years:
    csv_path = os.path.join(temp_csv_dir, f"Temperature_{year}.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️ {csv_path} not found, skipping...")
        continue

    # --- LOAD CSV ---
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df["DISTRICT_NAME"] = df["DISTRICT_NAME"].str.strip()  # remove extra spaces

    # --- EXTRACT MONTH ---
    df["MONTH"] = df["date"].dt.month

    # --- GROUP BY DISTRICT + MONTH ---
    monthly_avg = (
        df.groupby(["DISTRICT_NAME", "MONTH"])
          .agg({"minT": "mean", "maxT": "mean"})
          .reset_index()
    )

    # --- MERGE with full district list ---
    monthly_avg = all_districts_df.merge(monthly_avg, on="DISTRICT_NAME", how="left")

    # Add avgT column
    monthly_avg["avgT"] = (monthly_avg["minT"] + monthly_avg["maxT"]) / 2

    # Add YEAR column
    monthly_avg["YEAR"] = year

    # Reorder columns
    monthly_avg = monthly_avg[["YEAR", "MONTH", "DISTRICT_NAME", "minT", "maxT", "avgT"]]

    all_data.append(monthly_avg)

# --- COMBINE ALL YEARS ---
combined_df = pd.concat(all_data, ignore_index=True)

# --- SAVE COMBINED CSV ---
combined_df.to_csv(output_csv, index=False)
print(f"✅ Combined monthly temperature average CSV saved: {output_csv}")
