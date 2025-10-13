#!/usr/bin/env python3
"""
Fix Spelling: Charkhi Dadri → Charki Dadri

This script corrects the spelling of "Charkhi Dadri" to "Charki Dadri" 
in all files in the AQI_Final_Merged folder.
"""

import pandas as pd
import os
from pathlib import Path

def fix_charkhi_dadri_spelling():
    """Fix the spelling of Charkhi Dadri to Charki Dadri in all files."""
    
    target_dir = Path("/home/jatin/Code/Year3/EST/AQI_Final_Merged")
    
    print("Fixing spelling: Charkhi Dadri → Charki Dadri...")
    print(f"Target: {target_dir}")
    print("=" * 60)
    
    files_updated = 0
    entries_fixed = 0
    
    # Process each year
    for year_dir in sorted(target_dir.iterdir()):
        if not year_dir.is_dir():
            continue
            
        year = year_dir.name
        print(f"\\nProcessing {year}...")
        
        # Process each monthly file
        for monthly_file in sorted(year_dir.glob("*.xlsx")):
            month_filename = monthly_file.name
            
            try:
                # Read the file
                df = pd.read_excel(monthly_file)
                
                # Check if Charkhi Dadri exists
                if 'Charkhi Dadri' in df['District'].values:
                    # Fix the spelling
                    df.loc[df['District'] == 'Charkhi Dadri', 'District'] = 'Charki Dadri'
                    
                    # Save the updated file
                    df.to_excel(monthly_file, index=False)
                    
                    files_updated += 1
                    entries_fixed += 1
                    print(f"  {month_filename}: Fixed Charkhi Dadri → Charki Dadri")
                
            except Exception as e:
                print(f"  Error processing {month_filename}: {e}")
                continue
    
    return files_updated, entries_fixed

def main():
    """Main function to fix the spelling."""
    
    files_updated, entries_fixed = fix_charkhi_dadri_spelling()
    
    print("=" * 60)
    print("Spelling correction complete!")
    print(f"\\nSummary:")
    print(f"  Files updated: {files_updated}")
    print(f"  Entries corrected: {entries_fixed}")
    
    print("\\nSpelling correction applied:")
    print("  - Charkhi Dadri → Charki Dadri")
    
    # Verify the change
    target_dir = Path("/home/jatin/Code/Year3/EST/AQI_Final_Merged")
    sample_file = target_dir / "2024" / "2024_01.xlsx"
    
    if sample_file.exists():
        try:
            df = pd.read_excel(sample_file)
            haryana_districts = df[df['State'] == 'Haryana']['District'].tolist()
            print(f"\\nVerification - Haryana districts in 2024_01:")
            for district in sorted(haryana_districts):
                print(f"  - {district}")
        except Exception as e:
            print(f"  Error verifying: {e}")

if __name__ == "__main__":
    main()