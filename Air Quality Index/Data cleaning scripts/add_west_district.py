#!/usr/bin/env python3
"""
Add Missing "West" District to AQI_Final_Merged

This script adds the missing "West" district data from AQI_2.0_Reorganized 
to the existing AQI_Final_Merged folder.
"""

import pandas as pd
import os
from pathlib import Path

def add_west_district():
    """Add West district data to AQI_Final_Merged from AQI_2.0_Reorganized."""
    
    source_dir = Path("/home/jatin/Code/Year3/EST/AQI_2.0_Reorganized")
    target_dir = Path("/home/jatin/Code/Year3/EST/AQI_Final_Merged")
    
    print("Adding missing 'West' district to AQI_Final_Merged...")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print("=" * 60)
    
    files_updated = 0
    entries_added = 0
    
    # Process each year
    for year_dir in sorted(source_dir.iterdir()):
        if not year_dir.is_dir():
            continue
            
        year = year_dir.name
        print(f"\\nProcessing {year}...")
        
        target_year_dir = target_dir / year
        if not target_year_dir.exists():
            print(f"  Skipping {year} - target year directory doesn't exist")
            continue
        
        # Process each monthly file
        for monthly_file in sorted(year_dir.glob("*.xlsx")):
            if monthly_file.name.endswith(':Zone.Identifier'):
                continue
                
            month_filename = monthly_file.name
            target_monthly_file = target_year_dir / month_filename
            
            if not target_monthly_file.exists():
                print(f"  Skipping {month_filename} - target file doesn't exist")
                continue
                
            try:
                # Read source file and look for "West" district
                df_source = pd.read_excel(monthly_file)
                west_data = df_source[df_source['District'] == 'West']
                
                if west_data.empty:
                    continue  # No West district in this file
                
                # Read target file
                df_target = pd.read_excel(target_monthly_file)
                
                # Check if West district already exists in target
                if 'West' in df_target['District'].values:
                    print(f"  {month_filename}: West already exists")
                    continue
                
                # Add West district data
                west_row = west_data.iloc[0].copy()
                new_row = pd.DataFrame([{
                    'District': 'West',
                    'State': west_row['State'],
                    'Average_AQI': round(west_row['Average_AQI'], 2)
                }])
                
                # Append to target data
                df_updated = pd.concat([df_target, new_row], ignore_index=True)
                
                # Sort by District
                df_updated = df_updated.sort_values('District')
                
                # Save updated file
                df_updated.to_excel(target_monthly_file, index=False)
                
                files_updated += 1
                entries_added += 1
                print(f"  {month_filename}: Added West district (AQI: {west_row['Average_AQI']:.2f})")
                
            except Exception as e:
                print(f"  Error processing {month_filename}: {e}")
                continue
    
    return files_updated, entries_added

def main():
    """Main function to add missing West district."""
    
    files_updated, entries_added = add_west_district()
    
    print("=" * 60)
    print("Adding West district complete!")
    print(f"\\nSummary:")
    print(f"  Files updated: {files_updated}")
    print(f"  West district entries added: {entries_added}")
    
    # Verify final count
    target_dir = Path("/home/jatin/Code/Year3/EST/AQI_Final_Merged")
    if target_dir.exists():
        print("\\nFinal structure:")
        total_files = 0
        for year_dir in sorted(target_dir.iterdir()):
            if year_dir.is_dir():
                files = list(year_dir.glob("*.xlsx"))
                total_files += len(files)
                print(f"  {year_dir.name}/: {len(files)} monthly files")
        
        print(f"\\nTotal files: {total_files}")
    
    print("\\nDistrict added:")
    print("  - West (from AQI_2.0_Reorganized)")

if __name__ == "__main__":
    main()