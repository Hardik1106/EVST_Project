import pandas as pd
from sklearn.preprocessing import StandardScaler

# 1. Load the raw CSV
df = pd.read_csv("delhi_ncr_rainfall_monthly_avg_2013_2024.csv")

# 2. Optional: create a combined DATE column for convenience
df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')

# 3. Global standardization (across all districts and months)
scaler = StandardScaler()
df['RAINFALL_STANDARDIZED'] = scaler.fit_transform(df[['RAINFALL']])

# 4. Optional: district-wise standardization (for comparing relative local trends)
df['RAINFALL_STANDARDIZED_DISTRICT'] = df.groupby('DISTRICT_NAME')['RAINFALL'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# 5. Save standardized dataset
df.to_csv("delhi_ncr_rainfall_monthly_avg_standardized.csv", index=False)

print("✅ Standardized dataset saved as 'delhi_ncr_rainfall_monthly_avg_standardized.csv'")
