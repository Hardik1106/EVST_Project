#!/usr/bin/env python3
"""
AQI Data Reorganization by Districts

This script reorganizes the station-level AQI data into district-level data by:
1. Reading the existing AQI_Reorganized station data
2. Mapping stations to their respective Delhi districts
3. Averaging AQI values for districts with multiple stations
4. Creating a new AQI_Reorganized_districts folder structure

Structure:
- Input: AQI_Reorganized (station-level data)
- Output: AQI_Reorganized_districts (district-level data)
- Years: 2018-2024
- Monthly files: YYYY_MM.xlsx with District | Average_AQI columns
"""

import pandas as pd
import os
from pathlib import Path
import numpy as np

def get_station_district_mapping():
    """Get the mapping of stations to districts from the stations file."""
    
    station_district_map = {
        # Central Delhi (7 stations)
        'Chandni Chowk': 'Central Delhi',
        'ITO': 'Central Delhi', 
        'Jawaharlal Nehru Stadium': 'Central Delhi',
        'Lodhi Road': 'Central Delhi',
        'Major Dhyan Chand National Stadium': 'Central Delhi',
        'Mandir Marg': 'Central Delhi',
        'Pusa': 'Central Delhi',
        
        # East Delhi (3 stations)
        'Anand Vihar': 'East Delhi',
        'Nehru Nagar': 'East Delhi',
        'Patparganj': 'East Delhi',
        
        # North Delhi (4 stations)
        'Alipur': 'North Delhi',
        'Burari Crossing': 'North Delhi',
        'Narela': 'North Delhi',
        'North Campus DU': 'North Delhi',
        
        # North East Delhi (3 stations)
        'IHBAS Dilshad Garden': 'North East Delhi',
        'Sonia Vihar': 'North East Delhi',
        'Vivek Vihar': 'North East Delhi',
        
        # North West Delhi (6 stations)
        'Ashok Vihar': 'North West Delhi',
        'Bawana': 'North West Delhi',
        'DTU': 'North West Delhi',
        'Jahangirpuri': 'North West Delhi',
        'Rohini': 'North West Delhi',
        'Wazirpur': 'North West Delhi',
        
        # South Delhi (4 stations)
        'Aya Nagar': 'South Delhi',
        'Dr. Karni Singh Shooting Range': 'South Delhi',
        'Sirifort': 'South Delhi',
        'Sri Aurobindo Marg': 'South Delhi',
        
        # South East Delhi (2 stations)
        'CRRI Mathura Road': 'South East Delhi',
        'Okhla Phase-2': 'South East Delhi',
        
        # South West Delhi (5 stations)
        'Dwarka-Sector 8': 'South West Delhi',
        'IGI Airport (T3)': 'South West Delhi',
        'NSIT Dwarka': 'South West Delhi',
        'Najafgarh': 'South West Delhi',
        'R K Puram': 'South West Delhi',
        
        # West Delhi (3 stations)
        'Mundka': 'West Delhi',
        'Punjabi Bagh': 'West Delhi',
        'Shadipur': 'West Delhi'
    }
    
    return station_district_map

def process_monthly_file(file_path, station_district_map):
    """Process a monthly file and return district-level averages."""
    
    try:
        df = pd.read_excel(file_path)
        
        # Check if file has the expected structure
        if 'Station' not in df.columns or 'Average_AQI' not in df.columns:
            print(f"Warning: Unexpected file structure in {file_path}")
            return pd.DataFrame()
        
        # Add district information
        df['District'] = df['Station'].map(station_district_map)
        
        # Remove stations not in our mapping (should not happen with clean data)
        df = df.dropna(subset=['District'])
        
        # Group by district and calculate average AQI
        district_averages = df.groupby('District')['Average_AQI'].mean().reset_index()
        
        # Round to 2 decimal places
        district_averages['Average_AQI'] = district_averages['Average_AQI'].round(2)
        
        return district_averages
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return pd.DataFrame()

def main():
    # Define paths
    source_dir = Path("/home/jatin/Code/Year3/EST/AQI_Reorganized")
    target_dir = Path("/home/jatin/Code/Year3/EST/AQI_Reorganized_districts")
    
    print("Starting AQI station-to-district reorganization...")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print("=" * 60)
    
    # Create target directory
    target_dir.mkdir(exist_ok=True)
    
    # Get station-district mapping
    station_district_map = get_station_district_mapping()
    print(f"Station-District mapping loaded: {len(station_district_map)} stations across 9 districts")
    
    # Process each year
    years_processed = 0
    files_processed = 0
    
    for year_dir in sorted(source_dir.glob("*")):
        if not year_dir.is_dir():
            continue
            
        year = year_dir.name
        print(f"\nProcessing {year}...")
        
        # Create year directory in target
        target_year_dir = target_dir / year
        target_year_dir.mkdir(exist_ok=True)
        
        # Process each monthly file
        year_files = 0
        for monthly_file in sorted(year_dir.glob("*.xlsx")):
            month_filename = monthly_file.name
            
            print(f"  Processing {month_filename}")
            
            # Process the file
            district_data = process_monthly_file(monthly_file, station_district_map)
            
            if not district_data.empty:
                # Save district-level data
                output_file = target_year_dir / month_filename
                district_data.to_excel(output_file, index=False)
                
                print(f"    Created: {output_file.relative_to(target_dir)} with {len(district_data)} districts")
                year_files += 1
                files_processed += 1
            else:
                print(f"    Skipped: {month_filename} (no valid data)")
        
        if year_files > 0:
            years_processed += 1
            print(f"  Completed {year}: {year_files} monthly files created")
    
    print("=" * 60)
    print("District-level reorganization complete!")
    print(f"\nSummary:")
    print(f"  Years processed: {years_processed}")
    print(f"  Monthly files created: {files_processed}")
    print(f"  Districts: 9 Delhi districts")
    
    # Show example of district coverage
    if files_processed > 0:
        print(f"\nDistrict coverage summary:")
        districts = list(station_district_map.values())
        district_counts = {district: districts.count(district) for district in set(districts)}
        
        for district, count in sorted(district_counts.items()):
            print(f"  {district}: {count} stations averaged")
    
    print(f"\nOutput structure:")
    for year_dir in sorted(target_dir.glob("*")):
        if year_dir.is_dir():
            file_count = len(list(year_dir.glob("*.xlsx")))
            print(f"  {year_dir.name}/: {file_count} monthly files")

if __name__ == "__main__":
    main()