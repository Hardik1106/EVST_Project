#!/usr/bin/env python3
"""
Process AQI Excel files and consolidate into a single CSV for visualization
"""

import pandas as pd
import os
import glob
import numpy as np
from datetime import datetime

def process_aqi_data():
    """
    Process all AQI Excel files from AQI_Data_Final folder and create a consolidated CSV
    """
    print("🔄 Processing AQI data from Excel files...")
    
    base_path = "AQI_Data_Final"
    all_data = []
    
    # Process files from each year
    years = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.isdigit()]
    years.sort()
    
    for year in years:
        year_path = os.path.join(base_path, year)
        xlsx_files = [f for f in os.listdir(year_path) if f.endswith('.xlsx') and not f.startswith('~')]
        xlsx_files.sort()
        
        for file in xlsx_files:
            # Extract month from filename (e.g., 2018_01.xlsx -> 01)
            try:
                month = file.split('_')[1].split('.')[0]
                month_num = int(month)
            except:
                print(f"⚠️ Could not parse month from {file}, skipping...")
                continue
            
            file_path = os.path.join(year_path, file)
            
            try:
                # Read Excel file
                df = pd.read_excel(file_path)
                
                # Add year and month columns
                df['YEAR'] = int(year)
                df['MONTH'] = month_num
                
                # Standardize column names
                if 'District' in df.columns:
                    df['DISTRICT_NAME'] = df['District']
                if 'Average_AQI' in df.columns:
                    df['AQI'] = df['Average_AQI']
                
                # Keep only required columns
                required_cols = ['DISTRICT_NAME', 'State', 'AQI', 'YEAR', 'MONTH']
                df_clean = df[required_cols].copy()
                
                all_data.append(df_clean)
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
    
    if not all_data:
        print("❌ No data found!")
        return None
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Create datetime column
    combined_df["TIME"] = pd.to_datetime(combined_df["YEAR"].astype(str) + "-" + combined_df["MONTH"].astype(str) + "-01")
    combined_df["TIME_ISO"] = combined_df["TIME"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Clean district names for matching
    combined_df['DISTRICT_NAME_clean'] = combined_df['DISTRICT_NAME'].astype(str).str.strip().str.lower()
    
    # Handle special cases for district name mapping
    name_mapping = {
        'west': 'west delhi',
        'new delhi': 'new delhi',
        'north west delhi': 'north west delhi',
        'north delhi': 'north delhi',
        'north east delhi': 'north east delhi',
        'central delhi': 'central delhi',
        'east delhi': 'east delhi',
        'south delhi': 'south delhi',
        'south west delhi': 'south west delhi',
        'west delhi': 'west delhi',
        'south east delhi': 'south east delhi',
        'shahdara': 'shahdara'
    }
    
    combined_df['DISTRICT_NAME_clean'] = combined_df['DISTRICT_NAME_clean'].replace(name_mapping)
    
    # Sort by time and district
    combined_df = combined_df.sort_values(['YEAR', 'MONTH', 'DISTRICT_NAME'])
    
    # Save consolidated CSV
    output_file = "delhi_ncr_aqi_monthly_2018_2024.csv"
    combined_df.to_csv(output_file, index=False)
    
    print(f"✅ AQI data consolidated and saved to: {output_file}")
    print(f"📊 Total records: {len(combined_df)}")
    print(f"📅 Date range: {combined_df['YEAR'].min()}-{combined_df['MONTH'].min():02d} to {combined_df['YEAR'].max()}-{combined_df['MONTH'].max():02d}")
    print(f"🏛️ Districts: {combined_df['DISTRICT_NAME'].nunique()}")
    
    # Show sample data
    print("\n📋 Sample data:")
    print(combined_df[['DISTRICT_NAME', 'AQI', 'YEAR', 'MONTH']].head(10))
    
    return combined_df

if __name__ == "__main__":
    process_aqi_data()