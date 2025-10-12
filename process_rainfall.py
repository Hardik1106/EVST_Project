import os
import pandas as pd

years = range(2013, 2025)
daily_dir = "rainfall_csv"

# List to collect monthly averages for all years
all_data = []

for year in years:
    csv_path = os.path.join(daily_dir, f"delhi_rainfall_districts_{year}.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️  {csv_path} not found — skipping {year}.")
        continue

    df = pd.read_csv(csv_path)

    # Detect time-like column (case-insensitive)
    time_col = None
    for c in df.columns:
        if str(c).lower() in ("time", "date", "datetime"):
            time_col = c
            break

    if time_col is not None:
        df[time_col] = pd.to_datetime(df[time_col])
        df["MONTH"] = df[time_col].dt.month
    else:
        # If no time column, try to infer month if MONTH column exists
        if "MONTH" not in df.columns:
            raise ValueError(f"No time-like column found in {csv_path} and no 'MONTH' column to aggregate by.")

    # Group by district and month to get average rainfall
    monthly_avg = (
        df.groupby(["DISTRICT_NAME", "MONTH"]) ["RAINFALL"].mean().reset_index()
    )

    # Add year column
    monthly_avg["YEAR"] = year

    # Reorder columns
    monthly_avg = monthly_avg[["YEAR", "MONTH", "DISTRICT_NAME", "RAINFALL"]]

    all_data.append(monthly_avg)

# Combine all years
if len(all_data) > 0:
    combined_df = pd.concat(all_data, ignore_index=True)
else:
    combined_df = pd.DataFrame(columns=["YEAR", "MONTH", "DISTRICT_NAME", "RAINFALL"])

# Save to CSV
combined_csv_path = "delhi_ncr_rainfall_monthly_avg_2013_2024.csv"
combined_df.to_csv(combined_csv_path, index=False)
print(f"✅ Combined monthly average CSV saved: {combined_csv_path}")
