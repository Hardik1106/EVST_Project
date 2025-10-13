#!/usr/bin/env python3
"""
AQI 2.0 Data Reorganization Script

This script reorganizes district-level AQI Excel files from their current format to:
- Top level folders: Years (2018 onwards, skipping 2016 and 2017)
- Excel files: year_months 
- Excel files: District | State | average value over the month

Original format: AQI_daily_city_level_DISTRICT_YEAR_district_year.xlsx
Target structure:
- 2018/
  - 2018_01.xlsx (districts as rows with state and average AQI as columns)
  - 2018_02.xlsx
  - ...
"""

import pandas as pd
import os
from pathlib import Path
import numpy as np

def get_ncr_districts_mapping():
    """Get the complete NCR districts mapping with state information"""
    
    # Based on the NCR districts list and naming corrections
    ncr_districts = {
        # Haryana districts
        'Bhiwani': {'state': 'Haryana', 'file_name': 'bhiwani'},
        'Faridabad': {'state': 'Haryana', 'file_name': 'faridabad'},
        'Gurugram': {'state': 'Haryana', 'file_name': 'gurugram'},  # Note: files use 'gurugram'
        'Jhajjar': {'state': 'Haryana', 'file_name': None},  # Not available in files
        'Jind': {'state': 'Haryana', 'file_name': 'jind'},
        'Mahendragarh': {'state': 'Haryana', 'file_name': None},  # Not available
        'Mewat': {'state': 'Haryana', 'file_name': None},  # Not available
        'Palwal': {'state': 'Haryana', 'file_name': 'palwal'},
        'Panipat': {'state': 'Haryana', 'file_name': 'panipat'},
        'Rewari': {'state': 'Haryana', 'file_name': None},  # Not available
        'Rohtak': {'state': 'Haryana', 'file_name': 'rohtak'},
        'Sonipat': {'state': 'Haryana', 'file_name': 'sonipat'},
        
        # NCT of Delhi
        'West': {'state': 'NCTofDelhi', 'file_name': 'delhi'},  # Files use 'delhi' for all Delhi
        
        # Rajasthan districts
        'Alwar': {'state': 'Rajasthan', 'file_name': 'alwar'},
        'Bharatpur': {'state': 'Rajasthan', 'file_name': 'bharatpur'},
        
        # Uttar Pradesh districts
        'Baghpat': {'state': 'UttarPradesh', 'file_name': 'baghpat'},
        'Bulandshahr': {'state': 'UttarPradesh', 'file_name': 'bulandshahr'},
        'Greater Noida': {'state': 'UttarPradesh', 'file_name': 'greater'},  # Corrected name
        'Ghaziabad': {'state': 'UttarPradesh', 'file_name': 'ghaziabad'},
        'Hapur': {'state': 'UttarPradesh', 'file_name': 'hapur'},
        'Meerut': {'state': 'UttarPradesh', 'file_name': 'meerut'},
        'Muzaffarnagar': {'state': 'UttarPradesh', 'file_name': 'muzaffarnagar'},
        'Shamli': {'state': 'UttarPradesh', 'file_name': None},  # Not available
    }
    
    return ncr_districts

def extract_file_info(file_path):
    """Extract district, year information from filename."""
    filename = file_path.name
    
    if ':Zone.Identifier' in filename:
        return None, None, None
        
    # Pattern: AQI_daily_city_level_DISTRICT_YEAR_district_year.xlsx
    # Special case for "greater_noida" which has an underscore
    if 'greater_noida' in filename:
        # Handle greater_noida specially: AQI_daily_city_level_greater_noida_YEAR_greater_noida_YEAR.xlsx
        parts = filename.split('_')
        district_file_name = 'greater'  # We'll map this to "Greater Noida"
        # Find year - it should be after "noida"
        for i, part in enumerate(parts):
            if part == 'noida' and i+1 < len(parts):
                try:
                    year = int(parts[i+1])
                    break
                except ValueError:
                    continue
        else:
            return None, None, None
    else:
        parts = filename.split('_')
        if len(parts) >= 6:
            district_file_name = parts[4]  # 5th part is the district name in file
            try:
                year = int(parts[5])
            except ValueError:
                return None, None, None
        else:
            return None, None, None
        
    # Map state folder to state name
    state_folder = file_path.parent.name
    state_mapping = {
        'Delhi': 'NCTofDelhi',
        'Haryana': 'Haryana', 
        'Rajasthan': 'Rajasthan',
        'Uttar Pradesh': 'UttarPradesh'
    }
    state_name = state_mapping.get(state_folder, state_folder)
    
    return district_file_name, year, state_name

def calculate_monthly_averages(df):
    """Calculate monthly averages from daily data."""
    monthly_data = {}
    
    # Month names in the Excel files
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    # Only consider the first 32 rows (header + 31 days of data) to avoid including metadata/summary rows
    df_daily = df.head(32)
    
    for i, month in enumerate(months, 1):
        if month in df_daily.columns:
            # Calculate mean, ignoring NaN values
            monthly_avg = df_daily[month].mean()
            if not pd.isna(monthly_avg):
                monthly_data[f"{i:02d}"] = monthly_avg
    
    return monthly_data

def find_district_name_from_file(file_district_name, state_name):
    """Find the proper district name from file district name."""
    ncr_districts = get_ncr_districts_mapping()
    
    for district_name, info in ncr_districts.items():
        if info['file_name'] == file_district_name:
            return district_name
    
    # If not found, return capitalized version
    return file_district_name.capitalize()

def reorganize_aqi_district_data(source_dir, target_dir):
    """Reorganize AQI district data files according to the new structure."""
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create target directory if it doesn't exist
    target_path.mkdir(exist_ok=True)
    
    # Dictionary to store data: {year: {month: {district: {'state': state, 'avg_aqi': avg}}}}
    organized_data = {}
    
    # Get NCR districts mapping
    ncr_districts = get_ncr_districts_mapping()
    
    # Process all state folders
    for state_folder in source_path.iterdir():
        if not state_folder.is_dir():
            continue
            
        print(f"Processing {state_folder.name}...")
        
        # Process all Excel files in the state folder
        for file_path in state_folder.glob("*.xlsx"):
            if ':Zone.Identifier' in file_path.name:
                continue
                
            file_district_name, year, state_name = extract_file_info(file_path)
            
            # Skip 2016, 2017 and process only 2018 onwards
            if year is None or year < 2018:
                print(f"  Skipping {file_path.name} (year: {year})")
                continue
                
            # Find proper district name
            district_name = find_district_name_from_file(file_district_name, state_name)
            
            print(f"  Processing {file_path.name} - Year: {year}, District: {district_name}, State: {state_name}")
            
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
                    
                    organized_data[year][month][district_name] = {
                        'state': state_name,
                        'avg_aqi': avg_aqi
                    }
                    
            except Exception as e:
                print(f"  Error processing {file_path.name}: {e}")
                continue
    
    # Create year folders and monthly Excel files
    for year, year_data in organized_data.items():
        year_dir = target_path / str(year)
        year_dir.mkdir(exist_ok=True)
        
        for month, month_data in year_data.items():
            # Create DataFrame with all NCR districts
            rows = []
            
            for district_name, district_info in ncr_districts.items():
                if district_name in month_data:
                    # Data available
                    rows.append({
                        'District': district_name,
                        'State': month_data[district_name]['state'],
                        'Average_AQI': month_data[district_name]['avg_aqi']
                    })
                else:
                    # Data not available - use NA
                    rows.append({
                        'District': district_name,
                        'State': district_info['state'],
                        'Average_AQI': 'NA'
                    })
            
            # Create DataFrame and sort by district name
            df_month = pd.DataFrame(rows)
            df_month = df_month.sort_values('District')
            
            # Replace NaN values in Average_AQI with "NA" string
            df_month['Average_AQI'] = df_month['Average_AQI'].fillna('NA')
            
            # Save to Excel file
            output_file = year_dir / f"{year}_{month}.xlsx"
            df_month.to_excel(output_file, index=False)
            
            # Count available data
            available_count = len([r for r in rows if r['Average_AQI'] != 'NA'])
            print(f"Created: {output_file} with {available_count}/{len(rows)} districts with data")

def main():
    """Main function to run the reorganization."""
    source_directory = "/home/jatin/Code/Year3/EST/AQI  2.0"
    target_directory = "/home/jatin/Code/Year3/EST/AQI_2.0_Reorganized"
    
    print("Starting AQI 2.0 district data reorganization...")
    print(f"Source: {source_directory}")
    print(f"Target: {target_directory}")
    print("=" * 60)
    
    reorganize_aqi_district_data(source_directory, target_directory)
    
    print("=" * 60)
    print("Reorganization complete!")
    
    # Display summary
    target_path = Path(target_directory)
    if target_path.exists():
        print("\\nSummary of created structure:")
        for year_dir in sorted(target_path.iterdir()):
            if year_dir.is_dir():
                files = list(year_dir.glob("*.xlsx"))
                print(f"  {year_dir.name}/: {len(files)} monthly files")

if __name__ == "__main__":
    main()