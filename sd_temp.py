import pandas as pd
from sklearn.preprocessing import StandardScaler

# 1. Load the raw CSV
df = pd.read_csv("delhi_ncr_temp_monthly_avg_2013_2024.csv")

# 2. Ensure correct types
df['YEAR'] = df['YEAR'].astype(int)
df['MONTH'] = df['MONTH'].astype(int)

# 3. Create a combined DATE column
df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')

# 4. Global standardization (across all districts and months)
scaler = StandardScaler()
for col in ['minT', 'maxT', 'avgT']:
    df[f'{col}_STANDARDIZED'] = scaler.fit_transform(df[[col]])

# 5. District-wise standardization (for local trend comparisons)
for col in ['minT', 'maxT', 'avgT']:
    df[f'{col}_STANDARDIZED_DISTRICT'] = df.groupby('DISTRICT_NAME')[col].transform(
        lambda x: (x - x.mean()) / x.std()
    )

# 6. Save standardized dataset
df.to_csv("delhi_ncr_temp_monthly_avg_standardized.csv", index=False)

print("✅ Standardized dataset saved as 'delhi_ncr_temp_monthly_avg_standardized.csv'")
