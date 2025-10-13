#!/usr/bin/env python3
"""
AQI Data Reorganization Script

This script reorganizes AQI Excel files from their current format to:
- Top level folders: Years (2018 onwards, skipping 2016 and 2017)
- Excel files: year_months 
- Excel files: station | average value over the month

Original format: AQI_daily_YYYY_Station_Name_Organization_YYYY.xlsx
Target structure:
- 2018/
  - 2018_01.xlsx (stations as rows, average AQI as values)
  - 2018_02.xlsx
  - ...
- 2019/
  - 2019_01.xlsx
  - ...
"""

import pandas as pd
import os
import re
from pathlib import Path
import numpy as np
from datetime import datetime

def extract_file_info(filename):
    """Extract year and station name from filename."""
    # Pattern: AQI_daily_YYYY_Station_Name_Organization_YYYY.xlsx
    pattern = r'AQI_daily_(\d{4})_(.+?)_(\d{4})\.xlsx'
    match = re.match(pattern, filename)
    
    if match:
        year = int(match.group(1))
        station_part = match.group(2)
        # Remove organization suffixes and clean station name
        station_name = station_part.replace('_Delhi_DPCC', '').replace('_Delhi_CPCB', '').replace('_Delhi_IMD', '').replace('_Delhi_IITM', '')
        station_name = station_name.replace('_', ' ').strip()
        return year, station_name
    return None, None

def calculate_monthly_averages(df):
    """Calculate monthly averages from daily data."""
    monthly_data = {}
    
    # Month names in the Excel files
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    for i, month in enumerate(months, 1):
        if month in df.columns:
            # Calculate mean, ignoring NaN values
            monthly_avg = df[month].mean()
            if not pd.isna(monthly_avg):
                monthly_data[f"{i:02d}"] = monthly_avg
    
    return monthly_data

def reorganize_aqi_data(source_dir, target_dir):
    """Reorganize AQI data files according to the new structure."""
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create target directory if it doesn't exist
    target_path.mkdir(exist_ok=True)
    
    # Dictionary to store data: {year: {month: {station: avg_aqi}}}
    organized_data = {}
    
    # Process all Excel files
    for file_path in source_path.glob("*.xlsx"):
        filename = file_path.name
        
        # Skip Zone.Identifier files
        if filename.endswith(':Zone.Identifier'):
            continue
            
        year, station_name = extract_file_info(filename)
        
        # Skip 2016 and 2017, only process 2018 onwards
        if year is None or year < 2018:
            print(f"Skipping {filename} (year: {year})")
            continue
            
        print(f"Processing {filename} - Year: {year}, Station: {station_name}")
        
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Calculate monthly averages
            monthly_averages = calculate_monthly_averages(df)
            
            # Store in organized structure
            if year not in organized_data:
                organized_data[year] = {}
                
            for month, avg_aqi in monthly_averages.items():
                if month not in organized_data[year]:
                    organized_data[year][month] = {}
                organized_data[year][month][station_name] = avg_aqi
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    # Create year folders and monthly Excel files
    for year, year_data in organized_data.items():
        year_dir = target_path / str(year)
        year_dir.mkdir(exist_ok=True)
        
        for month, month_data in year_data.items():
            # Create DataFrame with stations and their average AQI
            df_month = pd.DataFrame(list(month_data.items()), 
                                  columns=['Station', 'Average_AQI'])
            df_month = df_month.sort_values('Station')
            
            # Save to Excel file
            output_file = year_dir / f"{year}_{month}.xlsx"
            df_month.to_excel(output_file, index=False)
            print(f"Created: {output_file} with {len(df_month)} stations")

def main():
    """Main function to run the reorganization."""
    source_directory = "/home/jatin/Code/Year3/EST/AQI"
    target_directory = "/home/jatin/Code/Year3/EST/AQI_Reorganized"
    
    print("Starting AQI data reorganization...")
    print(f"Source: {source_directory}")
    print(f"Target: {target_directory}")
    print("=" * 50)
    
    reorganize_aqi_data(source_directory, target_directory)
    
    print("=" * 50)
    print("Reorganization complete!")
    
    # Display summary
    target_path = Path(target_directory)
    if target_path.exists():
        print("\nSummary of created structure:")
        for year_dir in sorted(target_path.iterdir()):
            if year_dir.is_dir():
                files = list(year_dir.glob("*.xlsx"))
                print(f"  {year_dir.name}/: {len(files)} monthly files")

if __name__ == "__main__":
    main()