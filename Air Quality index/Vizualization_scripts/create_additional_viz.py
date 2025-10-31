#!/usr/bin/env python3
"""
Additional Specialized AQI Visualizations
Creates focused analysis charts for specific aspects of air quality data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from scipy.stats import pearsonr, spearmanr
import matplotlib.patches as patches

def create_pollution_severity_map(df):
    """Create a severity classification visualization"""
    print("🚨 Creating pollution severity analysis...")
    
    # Calculate pollution severity metrics
    severity_stats = df.groupby('DISTRICT_NAME').agg({
        'AQI': ['mean', 'max', 'std', 'count'],
    }).round(2)
    
    # Flatten column names
    severity_stats.columns = ['Avg_AQI', 'Max_AQI', 'AQI_Variability', 'Data_Points']
    severity_stats = severity_stats.reset_index()
    
    # Filter districts with sufficient data
    severity_stats = severity_stats[severity_stats['Data_Points'] >= 10]
    
    # Calculate severity score
    severity_stats['Severity_Score'] = (
        0.4 * severity_stats['Avg_AQI'] + 
        0.3 * severity_stats['Max_AQI'] + 
        0.3 * severity_stats['AQI_Variability']
    )
    
    # Sort by severity
    severity_stats = severity_stats.sort_values('Severity_Score', ascending=False)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Severity ranking
    top_15 = severity_stats.head(15)
    bars = axes[0,0].barh(range(len(top_15)), top_15['Severity_Score'], 
                         color=plt.cm.Reds(np.linspace(0.3, 0.9, len(top_15))))
    axes[0,0].set_yticks(range(len(top_15)))
    axes[0,0].set_yticklabels([name[:15] + '...' if len(name) > 15 else name 
                              for name in top_15['DISTRICT_NAME']])
    axes[0,0].set_title('Pollution Severity Ranking (Composite Score)', fontweight='bold')
    axes[0,0].set_xlabel('Severity Score')
    
    # Add score labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        axes[0,0].text(width + 1, bar.get_y() + bar.get_height()/2, 
                      f'{width:.1f}', ha='left', va='center', fontsize=9)
    
    # Scatter plot: Average vs Max AQI
    scatter = axes[0,1].scatter(severity_stats['Avg_AQI'], severity_stats['Max_AQI'],
                               s=severity_stats['Data_Points']*3,
                               c=severity_stats['AQI_Variability'],
                               cmap='viridis', alpha=0.7)
    axes[0,1].set_xlabel('Average AQI')
    axes[0,1].set_ylabel('Maximum AQI')
    axes[0,1].set_title('Average vs Maximum AQI\n(Size=Data Points, Color=Variability)', fontweight='bold')
    axes[0,1].grid(True, alpha=0.3)
    
    # Add colorbar
    plt.colorbar(scatter, ax=axes[0,1], label='AQI Variability (Std Dev)')
    
    # AQI range analysis
    df_clean = df.dropna(subset=['AQI'])
    aqi_ranges = pd.cut(df_clean['AQI'], 
                       bins=[0, 50, 100, 200, 300, 400, 500],
                       labels=['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe'])
    
    range_counts = aqi_ranges.value_counts()
    colors = ['green', 'yellow', 'orange', 'red', 'purple', 'maroon']
    
    wedges, texts, autotexts = axes[1,0].pie(range_counts.values, 
                                            labels=range_counts.index,
                                            autopct='%1.1f%%',
                                            colors=colors,
                                            startangle=90)
    axes[1,0].set_title('AQI Range Distribution\nAcross All Data Points', fontweight='bold')
    
    # Monthly severity trends
    monthly_severity = df.groupby(['YEAR', 'MONTH'])['AQI'].agg(['mean', 'max']).reset_index()
    monthly_severity['Date'] = pd.to_datetime(monthly_severity[['YEAR', 'MONTH']].assign(day=1))
    
    axes[1,1].plot(monthly_severity['Date'], monthly_severity['mean'], 
                  color='blue', linewidth=2, label='Monthly Average', alpha=0.7)
    axes[1,1].plot(monthly_severity['Date'], monthly_severity['max'], 
                  color='red', linewidth=1, alpha=0.6, label='Monthly Maximum')
    
    # Add severity zones
    axes[1,1].axhspan(0, 50, alpha=0.1, color='green', label='Good')
    axes[1,1].axhspan(50, 100, alpha=0.1, color='yellow')
    axes[1,1].axhspan(100, 200, alpha=0.1, color='orange')
    axes[1,1].axhspan(200, 300, alpha=0.1, color='red')
    axes[1,1].axhspan(300, 500, alpha=0.1, color='purple')
    
    axes[1,1].set_title('Monthly AQI Trends with Severity Zones', fontweight='bold')
    axes[1,1].set_ylabel('AQI')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('aqi_visualizations/09_pollution_severity_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_health_impact_visualization(df):
    """Create health impact assessment visualization"""
    print("🏥 Creating health impact assessment...")
    
    # Define health risk categories
    def get_health_risk(aqi):
        if pd.isna(aqi):
            return 'No Data'
        elif aqi <= 50:
            return 'Minimal Risk'
        elif aqi <= 100:
            return 'Sensitive Groups'
        elif aqi <= 200:
            return 'Unhealthy for Sensitive'
        elif aqi <= 300:
            return 'Unhealthy for All'
        elif aqi <= 400:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    df['Health_Risk'] = df['AQI'].apply(get_health_risk)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Population exposure estimation (hypothetical)
    # Using 2011 census data estimates for NCR districts
    population_estimates = {
        'New Delhi': 142004, 'Central Delhi': 582320, 'North Delhi': 887978,
        'North East Delhi': 2241624, 'East Delhi': 1709346, 'South East Delhi': 1326918,
        'South Delhi': 2731929, 'South West Delhi': 2292363, 'West Delhi': 2543243,
        'North West Delhi': 3656539, 'Shahdara': 1109652, 'Ghaziabad': 1729000,
        'Faridabad': 1414050, 'Gurugram': 876969, 'Gautam Buddha Nagar': 1648115
    }
    
    # Calculate exposure statistics
    risk_exposure = []
    for district, population in population_estimates.items():
        district_data = df[df['DISTRICT_NAME'] == district]
        if len(district_data) > 0:
            avg_aqi = district_data['AQI'].mean()
            risk_level = get_health_risk(avg_aqi)
            risk_exposure.append({
                'District': district,
                'Population': population,
                'Average_AQI': avg_aqi,
                'Health_Risk': risk_level
            })
    
    risk_df = pd.DataFrame(risk_exposure)
    
    # Population at risk
    if len(risk_df) > 0:
        risk_summary = risk_df.groupby('Health_Risk')['Population'].sum().sort_values(ascending=False)
        
        colors = ['green', 'yellow', 'orange', 'red', 'purple', 'maroon', 'gray']
        axes[0,0].pie(risk_summary.values, labels=risk_summary.index, autopct='%1.1f%%',
                     colors=colors[:len(risk_summary)], startangle=90)
        axes[0,0].set_title('Population Exposure to Health Risk Categories\n(Based on Average AQI)', fontweight='bold')
    
    # Temporal health risk patterns
    monthly_risk = df.groupby(['MONTH', 'Health_Risk']).size().unstack(fill_value=0)
    monthly_risk_pct = monthly_risk.div(monthly_risk.sum(axis=1), axis=0) * 100
    
    months = range(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    bottom = np.zeros(12)
    colors = ['green', 'yellow', 'orange', 'red', 'purple', 'maroon', 'gray']
    
    for i, risk_cat in enumerate(monthly_risk_pct.columns):
        if risk_cat != 'No Data':
            axes[0,1].bar(months, monthly_risk_pct[risk_cat], 
                         bottom=bottom, label=risk_cat, 
                         color=colors[i % len(colors)], alpha=0.8)
            bottom += monthly_risk_pct[risk_cat]
    
    axes[0,1].set_title('Monthly Health Risk Distribution (%)', fontweight='bold')
    axes[0,1].set_xlabel('Month')
    axes[0,1].set_ylabel('Percentage of Readings')
    axes[0,1].set_xticks(months)
    axes[0,1].set_xticklabels(month_names)
    axes[0,1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # AQI threshold exceedances
    thresholds = [100, 200, 300, 400]
    threshold_names = ['Satisfactory Limit', 'Moderate Limit', 'Poor Limit', 'Very Poor Limit']
    
    exceedances = []
    for threshold in thresholds:
        exceeded = (df['AQI'] > threshold).sum()
        total = df['AQI'].notna().sum()
        percentage = (exceeded / total) * 100
        exceedances.append(percentage)
    
    bars = axes[1,0].bar(threshold_names, exceedances, 
                        color=['orange', 'red', 'purple', 'maroon'], alpha=0.7)
    axes[1,0].set_title('AQI Threshold Exceedances', fontweight='bold')
    axes[1,0].set_ylabel('Percentage of Readings Above Threshold')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Add percentage labels on bars
    for bar, pct in zip(bars, exceedances):
        height = bar.get_height()
        axes[1,0].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                      f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Health advisory timeline
    df_timeline = df.copy()
    df_timeline['Health_Advisory'] = df_timeline['AQI'].apply(
        lambda x: 'Stay Indoors' if pd.notna(x) and x > 300 else 
                 'Limit Outdoor Activities' if pd.notna(x) and x > 200 else 
                 'Sensitive Groups Caution' if pd.notna(x) and x > 100 else 'Normal Activities')
    
    advisory_counts = df_timeline.groupby(['YEAR', 'Health_Advisory']).size().unstack(fill_value=0)
    
    years = sorted(df_timeline['YEAR'].unique())
    advisory_pct = advisory_counts.div(advisory_counts.sum(axis=1), axis=0) * 100
    
    bottom = np.zeros(len(years))
    advisory_colors = ['green', 'yellow', 'orange', 'red']
    
    for i, advisory in enumerate(['Normal Activities', 'Sensitive Groups Caution', 
                                 'Limit Outdoor Activities', 'Stay Indoors']):
        if advisory in advisory_pct.columns:
            axes[1,1].bar(years, advisory_pct[advisory], bottom=bottom, 
                         label=advisory, color=advisory_colors[i], alpha=0.8)
            bottom += advisory_pct[advisory]
    
    axes[1,1].set_title('Annual Health Advisory Distribution', fontweight='bold')
    axes[1,1].set_xlabel('Year')
    axes[1,1].set_ylabel('Percentage of Readings')
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig('aqi_visualizations/10_health_impact_assessment.png', dpi=300, bbox_inches='tight')
    plt.close()

def main_additional():
    """Generate additional specialized visualizations"""
    print("🎨 Creating additional specialized visualizations...")
    
    df = pd.read_csv("delhi_ncr_aqi_monthly_2018_2024.csv")
    df['TIME'] = pd.to_datetime(df['TIME'])
    
    create_pollution_severity_map(df)
    create_health_impact_visualization(df)
    
    print("✅ Additional visualizations completed!")
    print("   09_pollution_severity_analysis.png - Severity ranking and composite analysis")
    print("   10_health_impact_assessment.png - Health risk and population exposure analysis")

if __name__ == "__main__":
    main_additional()