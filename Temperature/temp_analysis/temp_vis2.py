import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import os

# --- CONFIG ---
csv_file = "delhi_ncr_temp_monthly_avg_standardized.csv"
plot_dir = "temp_analysis"
os.makedirs(plot_dir, exist_ok=True)

# --- LOAD DATA ---
df = pd.read_csv(csv_file)
df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')

# --- Clean names ---
df['DISTRICT_NAME'] = df['DISTRICT_NAME'].replace({'West': 'Delhi'})

# --- Choose which standardized column to analyze ---
metric = "avgT_STANDARDIZED"   # or minT_STANDARDIZED / maxT_STANDARDIZED
metric_label = metric.replace("_STANDARDIZED", "").upper()

# --- 1. 12-Month Rolling Trend per District ---
df['TEMP_ROLL'] = df.groupby('DISTRICT_NAME')[metric].transform(lambda x: x.rolling(12, min_periods=1).mean())

plt.figure(figsize=(15, 6))
for district in df['DISTRICT_NAME'].unique():
    d = df[df['DISTRICT_NAME'] == district]
    plt.plot(d['DATE'], d['TEMP_ROLL'], label=district)
plt.title(f"12-Month Rolling Standardized {metric_label} Trends by District")
plt.xlabel("Date")
plt.ylabel(f"Standardized {metric_label} (Z-score)")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"rolling_trends_{metric_label}.png"))
plt.close()

# --- 2. Average Monthly Pattern ---
monthly_avg = df.groupby(['MONTH', 'DISTRICT_NAME'])[metric].mean().reset_index()

plt.figure(figsize=(12, 6))
for district in monthly_avg['DISTRICT_NAME'].unique():
    d = monthly_avg[monthly_avg['DISTRICT_NAME'] == district]
    plt.plot(d['MONTH'], d[metric], marker='o', label=district)
plt.title(f"Average Standardized Monthly {metric_label} Pattern (2013–2024)")
plt.xlabel("Month")
plt.ylabel(f"Average Standardized {metric_label} (Z-score)")
plt.xticks(range(1, 13))
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"avg_monthly_pattern_{metric_label}.png"))
plt.close()

# --- 3. Yearly Trend Slopes ---
trend_results = []
for district in df['DISTRICT_NAME'].unique():
    d = df[df['DISTRICT_NAME'] == district].groupby('YEAR')[metric].mean().reset_index()
    slope, intercept, r_value, p_value, std_err = linregress(d['YEAR'], d[metric])
    trend_results.append({
        'DISTRICT': district,
        'slope': slope,
        'p_value': p_value,
        'R2': r_value**2
    })

trend_df = pd.DataFrame(trend_results)
trend_df.to_csv(os.path.join(plot_dir, f"yearly_trend_slopes_{metric_label}.csv"), index=False)
print(f"✅ Yearly trend slopes saved to '{plot_dir}/yearly_trend_slopes_{metric_label}.csv'")

# --- 4. Heatmap over Time ---
pivot = df.pivot_table(index='DISTRICT_NAME', columns='DATE', values=metric)
plt.figure(figsize=(18, 6))
sns.heatmap(pivot, cmap='coolwarm', center=0)
plt.title(f"Standardized {metric_label} Heatmap (Red=High, Blue=Low)")
plt.xlabel("Date")
plt.ylabel("District")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"heatmap_{metric_label}.png"))
plt.close()

# --- 5. Highlight Extreme Anomalies ---
df['ANOMALY'] = df[metric].abs() > 2
anomaly_df = df[df['ANOMALY']]
anomaly_df.to_csv(os.path.join(plot_dir, f"anomalies_{metric_label}.csv"), index=False)
print(f"✅ Extreme {metric_label} anomalies saved to '{plot_dir}/anomalies_{metric_label}.csv' — {len(anomaly_df)} events detected")
