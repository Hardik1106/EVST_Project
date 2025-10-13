#!/usr/bin/env python3
"""
AQI Data Analysis and Summary Statistics
Generates summary statistics and additional visualizations for AQI data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_aqi_data():
    """
    Perform comprehensive analysis of AQI data
    """
    print("📊 Analyzing AQI data...")
    
    # Load data
    aqi_file = "delhi_ncr_aqi_monthly_2018_2024.csv"
    if not os.path.exists(aqi_file):
        print(f"❌ AQI data file not found: {aqi_file}")
        return
    
    df = pd.read_csv(aqi_file)
    df['TIME'] = pd.to_datetime(df['TIME'])
    
    print(f"\n📈 AQI Data Summary:")
    print(f"   Total records: {len(df)}")
    print(f"   Districts: {df['DISTRICT_NAME'].nunique()}")
    print(f"   Date range: {df['TIME'].min().strftime('%Y-%m')} to {df['TIME'].max().strftime('%Y-%m')}")
    print(f"   Records with AQI data: {df['AQI'].notna().sum()}")
    print(f"   Missing data: {df['AQI'].isna().sum()}")
    
    # AQI Statistics
    valid_aqi = df['AQI'].dropna()
    if len(valid_aqi) > 0:
        print(f"\n🎯 AQI Statistics:")
        print(f"   Mean AQI: {valid_aqi.mean():.1f}")
        print(f"   Median AQI: {valid_aqi.median():.1f}")
        print(f"   Min AQI: {valid_aqi.min():.1f}")
        print(f"   Max AQI: {valid_aqi.max():.1f}")
        print(f"   Std Dev: {valid_aqi.std():.1f}")
    
    # AQI Categories
    def categorize_aqi(aqi):
        if pd.isna(aqi):
            return 'No Data'
        elif aqi <= 50:
            return 'Good'
        elif aqi <= 100:
            return 'Satisfactory'
        elif aqi <= 200:
            return 'Moderate'
        elif aqi <= 300:
            return 'Poor'
        elif aqi <= 400:
            return 'Very Poor'
        else:
            return 'Severe'
    
    df['AQI_Category'] = df['AQI'].apply(categorize_aqi)
    category_counts = df['AQI_Category'].value_counts()
    
    print(f"\n🏷️ AQI Category Distribution:")
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {category}: {count} ({percentage:.1f}%)")
    
    # District-wise analysis
    district_stats = df.groupby('DISTRICT_NAME')['AQI'].agg(['count', 'mean', 'std', 'min', 'max']).round(1)
    district_stats = district_stats.sort_values('mean', ascending=False)
    
    print(f"\n🏛️ Top 10 Districts by Average AQI:")
    print(district_stats.head(10))
    
    # Temporal analysis
    monthly_avg = df.groupby(['YEAR', 'MONTH'])['AQI'].mean().reset_index()
    monthly_avg['DATE'] = pd.to_datetime(monthly_avg[['YEAR', 'MONTH']].assign(day=1))
    
    print(f"\n📅 Monthly AQI Trends (Recent 12 months):")
    recent_data = monthly_avg.tail(12)
    for _, row in recent_data.iterrows():
        print(f"   {row['DATE'].strftime('%Y-%m')}: {row['AQI']:.1f}")
    
    # Save detailed statistics
    os.makedirs("aqi_analysis", exist_ok=True)
    
    # Save district statistics
    district_stats.to_csv("aqi_analysis/district_aqi_statistics.csv")
    
    # Save monthly trends
    monthly_avg.to_csv("aqi_analysis/monthly_aqi_trends.csv", index=False)
    
    # Save category analysis
    category_df = pd.DataFrame({
        'Category': category_counts.index,
        'Count': category_counts.values,
        'Percentage': (category_counts.values / len(df)) * 100
    })
    category_df.to_csv("aqi_analysis/aqi_category_distribution.csv", index=False)
    
    print(f"\n✅ Analysis complete! Files saved in aqi_analysis/ folder:")
    print(f"   - district_aqi_statistics.csv")
    print(f"   - monthly_aqi_trends.csv")  
    print(f"   - aqi_category_distribution.csv")

if __name__ == "__main__":
    analyze_aqi_data()