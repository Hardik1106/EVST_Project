import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import os
import matplotlib.dates as mdates
import numpy as np

# --- CONFIG ---
csv_file = "delhi_ncr_temp_monthly_avg_standardized.csv"
plot_dir = "temp_analysis"
os.makedirs(plot_dir, exist_ok=True)

# Set publication-quality style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# --- LOAD DATA ---
df = pd.read_csv(csv_file)
df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')

# --- Clean names ---
df['DISTRICT_NAME'] = df['DISTRICT_NAME'].replace({'West': 'Delhi'})

# Get list of districts sorted alphabetically
all_districts = sorted(df['DISTRICT_NAME'].unique())

# --- Choose which standardized column to analyze ---
metric = "avgT_STANDARDIZED"   # or minT_STANDARDIZED / maxT_STANDARDIZED
metric_label = metric.replace("_STANDARDIZED", "").upper()

# --- 1. 12-Month Rolling Trend - AGGREGATED VIEW ---
df['TEMP_ROLL'] = df.groupby('DISTRICT_NAME')[metric].transform(lambda x: x.rolling(12, min_periods=1).mean())

# Calculate NCR-wide average and quartiles
ncr_stats = df.groupby('DATE').agg({
    'TEMP_ROLL': ['mean', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]
}).reset_index()
ncr_stats.columns = ['DATE', 'mean', 'q25', 'q75']

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(ncr_stats['DATE'], ncr_stats['mean'], color='darkred', linewidth=2.5, label='NCR Average')
ax.fill_between(ncr_stats['DATE'], ncr_stats['q25'], ncr_stats['q75'], 
                alpha=0.3, color='coral', label='Interquartile Range (25th-75th percentile)')
ax.axhline(y=0, color='blue', linestyle='--', alpha=0.5, linewidth=1, label='Normal (Z=0)')

# Format x-axis to show only years
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_minor_locator(mdates.MonthLocator((1, 7)))

ax.set_title(f"12-Month Rolling Standardized {metric_label} Trend - Delhi NCR Region", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Year", fontsize=12, fontweight='bold')
ax.set_ylabel(f"Standardized {metric_label} (Z-score)", fontsize=12, fontweight='bold')
ax.legend(loc='best', frameon=True, shadow=True)
ax.grid(True, alpha=0.3, linestyle='--')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"rolling_trends_ncr_aggregate_{metric_label}.png"), dpi=300, bbox_inches='tight')
plt.close()

# --- 1b. Individual District Trends - SMALL MULTIPLES ---
n_districts = len(all_districts)
ncols = 4
nrows = (n_districts + ncols - 1) // ncols

fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows*2.5), sharex=True, sharey=True)
axes = axes.flatten()

for idx, district in enumerate(all_districts):
    d = df[df['DISTRICT_NAME'] == district].sort_values('DATE')
    axes[idx].plot(d['DATE'], d['TEMP_ROLL'], linewidth=1.5, color='darkred')
    axes[idx].axhline(y=0, color='blue', linestyle='--', alpha=0.5, linewidth=0.8)
    axes[idx].set_title(district, fontsize=10, fontweight='bold')
    axes[idx].grid(True, alpha=0.3, linestyle='--')
    axes[idx].xaxis.set_major_locator(mdates.YearLocator(2))
    axes[idx].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axes[idx].tick_params(axis='x', rotation=45, labelsize=8)
    axes[idx].tick_params(axis='y', labelsize=8)

# Hide unused subplots
for idx in range(n_districts, len(axes)):
    axes[idx].axis('off')

fig.suptitle(f"12-Month Rolling Standardized {metric_label} by District (2013-2024)", 
             fontsize=14, fontweight='bold', y=0.995)
fig.text(0.5, 0.02, 'Year', ha='center', fontsize=11, fontweight='bold')
fig.text(0.02, 0.5, f'Standardized {metric_label} (Z-score)', va='center', rotation='vertical', 
         fontsize=11, fontweight='bold')
plt.tight_layout(rect=[0.03, 0.03, 1, 0.99])
plt.savefig(os.path.join(plot_dir, f"rolling_trends_small_multiples_{metric_label}.png"), dpi=300, bbox_inches='tight')
plt.close()

# --- 2. Average Monthly Pattern - BOX PLOT ---
monthly_avg = df.groupby(['MONTH', 'DISTRICT_NAME'])[metric].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
bp = ax.boxplot([monthly_avg[monthly_avg['MONTH']==m][metric].values 
                  for m in range(1, 13)],
                 tick_labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                 patch_artist=True, showfliers=True)

# Color summer months differently
summer_months = [4, 5, 6]  # Apr-Jun
winter_months = [12, 1, 2]  # Dec-Feb
for i, box in enumerate(bp['boxes']):
    month = i + 1
    if month in summer_months or (month == 12):
        box.set_facecolor('coral')
        box.set_alpha(0.7)
    elif month in [1, 2] or month in winter_months:
        box.set_facecolor('lightblue')
        box.set_alpha(0.7)
    else:
        box.set_facecolor('lightgray')
        box.set_alpha(0.5)

ax.axhline(y=0, color='blue', linestyle='--', alpha=0.5, linewidth=1.5, label='Normal (Z=0)')
ax.set_title(f"Distribution of Standardized Monthly {metric_label} Across All Districts (2013-2024)", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Month", fontsize=12, fontweight='bold')
ax.set_ylabel(f"Standardized {metric_label} (Z-score)", fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--', axis='y')

# Add legend for seasons
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='coral', alpha=0.7, label='Summer (Apr-Jun)'),
    Patch(facecolor='lightblue', alpha=0.7, label='Winter (Dec-Feb)'),
    Patch(facecolor='lightgray', alpha=0.5, label='Transition'),
    plt.Line2D([0], [0], color='blue', linestyle='--', label='Normal (Z=0)')
]
ax.legend(handles=legend_elements, loc='upper left', frameon=True, shadow=True)

plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"avg_monthly_pattern_boxplot_{metric_label}.png"), dpi=300, bbox_inches='tight')
plt.close()

# --- 3. Yearly Trend Slopes ---
import warnings
trend_results = []
for district in df['DISTRICT_NAME'].unique():
    d = df[df['DISTRICT_NAME'] == district].groupby('YEAR')[metric].mean().reset_index()
    # Skip if no variance (constant values)
    if d[metric].std() < 1e-10:
        trend_results.append({
            'DISTRICT': district,
            'slope': 0.0,
            'p_value': 1.0,
            'R2': 0.0,
            'note': 'No variance'
        })
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            slope, intercept, r_value, p_value, std_err = linregress(d['YEAR'], d[metric])
            trend_results.append({
                'DISTRICT': district,
                'slope': slope,
                'p_value': p_value,
                'R2': r_value**2,
                'note': ''
            })

trend_df = pd.DataFrame(trend_results)
trend_df.to_csv(os.path.join(plot_dir, f"yearly_trend_slopes_{metric_label}.csv"), index=False)
print(f"✅ Yearly trend slopes saved to '{plot_dir}/yearly_trend_slopes_{metric_label}.csv'")

# --- 4. Heatmap over Time - ANNUAL AGGREGATION ---
# Aggregate by year for clearer visualization
df_yearly = df.groupby(['DISTRICT_NAME', 'YEAR'])[metric].mean().reset_index()
pivot = df_yearly.pivot_table(index='DISTRICT_NAME', columns='YEAR', values=metric)

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(pivot, cmap='RdBu_r', center=0, annot=False, fmt='.1f', 
            cbar_kws={'label': f'Standardized {metric_label} (Z-score)'},
            linewidths=0.5, linecolor='gray', ax=ax)
ax.set_title(f"Annual Standardized {metric_label} by District (2013-2024)\nRed = Above Normal | Blue = Below Normal", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Year", fontsize=12, fontweight='bold')
ax.set_ylabel("District", fontsize=12, fontweight='bold')
plt.xticks(rotation=0)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"heatmap_annual_{metric_label}.png"), dpi=300, bbox_inches='tight')
plt.close()

# --- 4b. Heatmap - Monthly View (cleaner x-axis) ---
pivot_monthly = df.pivot_table(index='DISTRICT_NAME', columns='DATE', values=metric)
fig, ax = plt.subplots(figsize=(20, 10))
sns.heatmap(pivot_monthly, cmap='RdBu_r', center=0, 
            cbar_kws={'label': f'Standardized {metric_label} (Z-score)'},
            linewidths=0, ax=ax)

# Show only year labels at reasonable intervals
n_cols = len(pivot_monthly.columns)
tick_positions = range(0, n_cols, 12)  # Every year
tick_labels = [pivot_monthly.columns[i].strftime('%Y') if i < n_cols else '' 
               for i in tick_positions]
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, rotation=0)

ax.set_title(f"Monthly Standardized {metric_label} Heatmap by District (2013-2024)", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Year", fontsize=12, fontweight='bold')
ax.set_ylabel("District", fontsize=12, fontweight='bold')
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"heatmap_monthly_{metric_label}.png"), dpi=300, bbox_inches='tight')
plt.close()

# --- 5. Highlight Extreme Anomalies ---
df['ANOMALY'] = df[metric].abs() > 2
anomaly_df = df[df['ANOMALY']]
anomaly_df.to_csv(os.path.join(plot_dir, f"anomalies_{metric_label}.csv"), index=False)
print(f"✅ Extreme {metric_label} anomalies saved to '{plot_dir}/anomalies_{metric_label}.csv' — {len(anomaly_df)} events detected")
