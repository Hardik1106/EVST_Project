import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import os

# --- CONFIG ---
csv_file = "delhi_ncr_rainfall_monthly_avg_standardized.csv"
plot_dir = "/"
os.makedirs(plot_dir, exist_ok=True)

# --- LOAD DATA ---
df = pd.read_csv(csv_file)
df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')

# Replace 'West' with 'Delhi'
df['DISTRICT_NAME'] = df['DISTRICT_NAME'].replace({'West': 'Delhi'})

# --- 1. 12-Month Rolling Trend per District ---
df['RAINFALL_ROLL'] = df.groupby('DISTRICT_NAME')['RAINFALL_STANDARDIZED'] \
                        .transform(lambda x: x.rolling(12, min_periods=1).mean())

plt.figure(figsize=(15,6))
for district in df['DISTRICT_NAME'].unique():
    d = df[df['DISTRICT_NAME'] == district]
    plt.plot(d['DATE'], d['RAINFALL_ROLL'], label=district)
plt.title("12-Month Rolling Standardized Rainfall Trends by District")
plt.xlabel("Date")
plt.ylabel("Standardized Rainfall (Z-score)")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, "rolling_trends_by_district.png"))
plt.close()

# --- 2. Average Monthly Pattern ---
monthly_avg = df.groupby(['MONTH', 'DISTRICT_NAME'])['RAINFALL_STANDARDIZED'].mean().reset_index()
plt.figure(figsize=(12,6))
for district in monthly_avg['DISTRICT_NAME'].unique():
    d = monthly_avg[monthly_avg['DISTRICT_NAME']==district]
    plt.plot(d['MONTH'], d['RAINFALL_STANDARDIZED'], marker='o', label=district)
plt.title("Average Standardized Monthly Rainfall Pattern (2013-2024)")
plt.xlabel("Month")
plt.ylabel("Average Standardized Rainfall (Z-score)")
plt.xticks(range(1,13))
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, "avg_monthly_pattern.png"))
plt.close()

# --- 3. Yearly Trend Slopes ---
trend_results = []
districts = df['DISTRICT_NAME'].unique()
for district in districts:
    d = df[df['DISTRICT_NAME']==district].groupby('YEAR')['RAINFALL_STANDARDIZED'].mean().reset_index()
    slope, intercept, r_value, p_value, std_err = linregress(d['YEAR'], d['RAINFALL_STANDARDIZED'])
    trend_results.append({'DISTRICT': district, 'slope': slope, 'p_value': p_value, 'R2': r_value**2})

trend_df = pd.DataFrame(trend_results)
trend_df.to_csv(os.path.join(plot_dir, "yearly_trend_slopes.csv"), index=False)
print("✅ Yearly trend slopes saved to 'yearly_trend_slopes.csv'")

# --- 4. Heatmap over Time ---
pivot = df.pivot_table(index='DISTRICT_NAME', columns='DATE', values='RAINFALL_STANDARDIZED')
plt.figure(figsize=(18,6))
sns.heatmap(pivot, cmap='coolwarm', center=0)
plt.title("Standardized Rainfall Heatmap (Red=High, Blue=Low)")
plt.xlabel("Date")
plt.ylabel("District")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, "rainfall_heatmap.png"))
plt.close()

# --- 5. Highlight Extreme Anomalies ---
df['ANOMALY'] = df['RAINFALL_STANDARDIZED'].abs() > 2
anomaly_df = df[df['ANOMALY']]
anomaly_df.to_csv(os.path.join(plot_dir, "rainfall_anomalies.csv"), index=False)
print(f"✅ Extreme rainfall anomalies saved to 'rainfall_anomalies.csv', {len(anomaly_df)} events detected")
