#!/usr/bin/env python3
"""
Add Missing New Districts to AQI_Final_Merged

This script adds the missing Charkhi Dadri and Karnal districts data 
to the existing AQI_Final_Merged folder, following the extraction 
pattern from reorganize_aqi_data.py
"""

import pandas as pd
import os
import re
from pathlib import Path
import numpy as np

def calculate_monthly_averages_fixed(df):
    """Calculate monthly averages from daily data (first 32 rows only)."""
    monthly_data = {}
    
    # Month names in the Excel files
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    # Only consider the first 32 rows (header + 31 days of data)
    df_daily = df.head(32)
    
    for i, month in enumerate(months, 1):
        if month in df_daily.columns:
            # Calculate mean, ignoring NaN values
            monthly_avg = df_daily[month].mean()
            if not pd.isna(monthly_avg):
                monthly_data[f"{i:02d}"] = monthly_avg
    
    return monthly_data

def extract_new_district_info(filename):
    """Extract year and district name from new districts filename."""
    # Following reorganize_aqi_data.py pattern for extraction
    
    if 'charkhi_dadri' in filename:
        # Pattern: AQI_daily_city_level_charkhi_dadri_YYYY_charkhi_dadri_YYYY.xlsx
        parts = filename.replace('.xlsx', '').split('_')
        if len(parts) >= 7:
            year = int(parts[6])  # Last year in filename
            return year, 'Charkhi Dadri'
    elif 'karnal' in filename:
        # Pattern: AQI_daily_city_level_karnal_YYYY_karnal_YYYY.xlsx
        parts = filename.replace('.xlsx', '').split('_')
        if len(parts) >= 6:
            year = int(parts[5])  # Last year in filename
            return year, 'Karnal'
    
    return None, None

def process_new_districts_and_merge():
    """Process new districts and add them to existing AQI_Final_Merged files."""
    
    new_data_dir = Path("/home/jatin/Code/Year3/EST/New aqi data")
    target_dir = Path("/home/jatin/Code/Year3/EST/AQI_Final_Merged")
    
    print("Adding missing new districts to AQI_Final_Merged...")
    print(f"Source: {new_data_dir}")
    print(f"Target: {target_dir}")
    print("=" * 60)
    
    # Dictionary to store new district data: {year: {month: {district: data}}}
    new_districts_data = {}
    
    # Process new districts files
    for file_path in new_data_dir.glob("*.xlsx"):
        filename = file_path.name
        
        # Skip Zone.Identifier files
        if filename.endswith(':Zone.Identifier'):
            continue
            
        year, district_name = extract_new_district_info(filename)
        
        # Skip 2017 and earlier, only process 2018 onwards
        if year is None or year < 2018:
            print(f"Skipping {filename} (year: {year})")
            continue
            
        print(f"Processing {filename} - Year: {year}, District: {district_name}")
        
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Calculate monthly averages (first 32 rows only)
            monthly_averages = calculate_monthly_averages_fixed(df)
            
            # Store in organized structure
            if year not in new_districts_data:
                new_districts_data[year] = {}
                
            for month, avg_aqi in monthly_averages.items():
                if month not in new_districts_data[year]:
                    new_districts_data[year][month] = {}
                new_districts_data[year][month][district_name] = {
                    'state': 'Haryana',
                    'aqi': avg_aqi
                }
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    # Now add the new district data to existing monthly files
    files_updated = 0
    districts_added = 0
    
    for year, year_data in new_districts_data.items():
        year_dir = target_dir / str(year)
        
        if not year_dir.exists():
            year_dir.mkdir(exist_ok=True)
            print(f"Created year directory: {year}")
        
        for month, month_districts in year_data.items():
            monthly_file = year_dir / f"{year}_{month}.xlsx"
            
            # Read existing monthly file or create new DataFrame
            if monthly_file.exists():
                df_existing = pd.read_excel(monthly_file)
                print(f"  Updating existing file: {year}/{year}_{month}.xlsx")
            else:
                df_existing = pd.DataFrame(columns=['District', 'State', 'Average_AQI'])
                print(f"  Creating new file: {year}/{year}_{month}.xlsx")
            
            # Add new districts data
            new_rows = []
            for district, data in month_districts.items():
                # Check if district already exists
                if district not in df_existing['District'].values:
                    new_rows.append({
                        'District': district,
                        'State': data['state'],
                        'Average_AQI': round(data['aqi'], 2)
                    })
                    districts_added += 1
                    print(f"    Added: {district} with AQI {data['aqi']:.2f}")
                else:
                    print(f"    Skipped: {district} (already exists)")
            
            # Add new rows to existing data
            if new_rows:
                df_new_rows = pd.DataFrame(new_rows)
                df_updated = pd.concat([df_existing, df_new_rows], ignore_index=True)
                
                # Sort by District
                df_updated = df_updated.sort_values('District')
                
                # Save updated file
                df_updated.to_excel(monthly_file, index=False)
                files_updated += 1
                
                print(f"    Updated: {monthly_file.name} now has {len(df_updated)} districts")
    
    return files_updated, districts_added

def main():
    """Main function to add missing new districts."""
    
    files_updated, districts_added = process_new_districts_and_merge()
    
    print("=" * 60)
    print("Adding new districts complete!")
    print(f"\\nSummary:")
    print(f"  Files updated: {files_updated}")
    print(f"  District entries added: {districts_added}")
    
    # Show sample of updated files
    target_dir = Path("/home/jatin/Code/Year3/EST/AQI_Final_Merged")
    if target_dir.exists():
        print("\\nUpdated structure:")
        total_files = 0
        for year_dir in sorted(target_dir.iterdir()):
            if year_dir.is_dir():
                files = list(year_dir.glob("*.xlsx"))
                total_files += len(files)
                print(f"  {year_dir.name}/: {len(files)} monthly files")
        
        print(f"\\nTotal files: {total_files}")
    
    print("\\nNew districts added:")
    print("  - Charkhi Dadri (Haryana)")
    print("  - Karnal (Haryana)")

if __name__ == "__main__":
    main()