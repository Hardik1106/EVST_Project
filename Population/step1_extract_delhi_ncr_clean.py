#!/usr/bin/env python3
"""
Delhi NCR Data Extraction Script (Refined)
Step 1: Extract only actual Delhi NCR regions from the census data
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_census_data(csv_path):
    """Load and clean the census data"""
    print("Loading census data...")
    
    # Read CSV file, skipping the first row which contains the title
    df = pd.read_csv(csv_path, skiprows=1)
    
    # Clean column names (remove extra spaces and newlines)
    df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ')
    
    # Direct index-based mapping for critical columns
    if len(df.columns) >= 15:
        df.rename(columns={
            df.columns[3]: 'Level',
            df.columns[4]: 'Area_Name', 
            df.columns[5]: 'Type',
            df.columns[10]: 'Population',
            df.columns[13]: 'Area_sq_km',
            df.columns[14]: 'Pop_Density'
        }, inplace=True)
    
    print(f"Loaded {len(df)} records")
    return df

def clean_numeric_data(df):
    """Clean numeric columns"""
    print("Cleaning numeric data...")
    
    def clean_numeric(x):
        if pd.isna(x) or x is None:
            return np.nan
        if isinstance(x, (int, float)):
            return float(x) if not np.isnan(x) else np.nan
        if isinstance(x, str):
            # Remove quotes, commas, and extra spaces
            cleaned = x.strip().replace('"', '').replace(',', '').replace(' ', '')
            if cleaned == '' or cleaned == '0':
                return np.nan
            try:
                return float(cleaned)
            except ValueError:
                return np.nan
        return np.nan
    
    # Clean numeric columns
    numeric_cols = ['Population', 'Area_sq_km', 'Pop_Density']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)
    
    return df

def extract_delhi_ncr_regions(df):
    """Extract Delhi NCR regions with precise matching"""
    
    # Delhi NCR regions - exact names as they appear in the GeoJSON
    delhi_ncr_exact = {
        # Delhi Districts (from GeoJSON)
        "New Delhi", "Shahdara", "West",
        "North West Delhi", "North Delhi", "North East Delhi", 
        "Central Delhi", "East Delhi", "South Delhi", 
        "South East Delhi", "South West Delhi", "West Delhi",
        
        # Haryana Districts
        "Bhiwani", "Faridabad", "Gurugram", "Gurgaon", 
        "Jhajjar", "Jind", "Karnal", "Mahendragarh", "Nuh", 
        "Palwal", "Panipat", "Rewari", "Rohtak", "Sonipat", "Charki Dadri",
        
        # Uttar Pradesh Districts  
        "Baghpat", "Bulandshahr", "Gautam Buddha Nagar", "Ghaziabad", 
        "Hapur", "Meerut", "Muzaffarnagar", "Shamli",
        
        # Rajasthan Districts
        "Alwar", "Bharatpur"
    }
    
    print(f"Looking for {len(delhi_ncr_exact)} specific Delhi NCR regions...")
    
    # Create filters for exact matches
    delhi_ncr_data = []
    
    for region in delhi_ncr_exact:
        # Exact match (case insensitive)
        exact_matches = df[df['Area_Name'].str.lower().str.strip() == region.lower().strip()]
        if len(exact_matches) > 0:
            delhi_ncr_data.append(exact_matches)
            print(f"  ✓ Found: {region} ({len(exact_matches)} records)")
        else:
            # Try some variations
            variations = [
                region.replace(" ", ""),  # No spaces
                region.replace("Delhi", "").strip(),  # Without Delhi suffix
            ]
            
            found = False
            for variation in variations:
                var_matches = df[df['Area_Name'].str.lower().str.strip() == variation.lower().strip()]
                if len(var_matches) > 0:
                    delhi_ncr_data.append(var_matches)
                    print(f"  ✓ Found: {region} as '{variation}' ({len(var_matches)} records)")
                    found = True
                    break
            
            if not found:
                print(f"  ✗ Not found: {region}")
    
    if delhi_ncr_data:
        combined_data = pd.concat(delhi_ncr_data, ignore_index=True)
        # Remove any duplicates
        combined_data = combined_data.drop_duplicates()
        print(f"\nTotal Delhi NCR records found: {len(combined_data)}")
    else:
        combined_data = pd.DataFrame()
        print("No Delhi NCR regions found!")
    
    return combined_data

def add_state_info(df):
    """Add state information for better organization"""
    
    def get_state(area_name):
        delhi_areas = [
            "New Delhi", "Shahdara", "West", "North West Delhi", "North Delhi", 
            "North East Delhi", "Central Delhi", "East Delhi", "South Delhi", 
            "South East Delhi", "South West Delhi", "West Delhi"
        ]
        
        haryana_areas = [
            "Bhiwani", "Faridabad", "Gurugram", "Gurgaon", "Jhajjar", "Jind", 
            "Karnal", "Mahendragarh", "Nuh", "Palwal", "Panipat", "Rewari", 
            "Rohtak", "Sonipat", "Charki Dadri"
        ]
        
        up_areas = [
            "Baghpat", "Bulandshahr", "Gautam Buddha Nagar", "Ghaziabad", 
            "Hapur", "Meerut", "Muzaffarnagar", "Shamli"
        ]
        
        rajasthan_areas = ["Alwar", "Bharatpur"]
        
        area_lower = area_name.lower().strip()
        
        for area in delhi_areas:
            if area.lower().strip() == area_lower:
                return "Delhi"
        
        for area in haryana_areas:
            if area.lower().strip() == area_lower:
                return "Haryana"
                
        for area in up_areas:
            if area.lower().strip() == area_lower:
                return "Uttar Pradesh"
                
        for area in rajasthan_areas:
            if area.lower().strip() == area_lower:
                return "Rajasthan"
                
        return "Unknown"
    
    df['State'] = df['Area_Name'].apply(get_state)
    return df

def save_clipped_data(df, output_path):
    """Save the clipped data to a new CSV file"""
    
    # Add state information
    df = add_state_info(df)
    
    # Sort by State, Level, Area_Name, and Type for better organization
    df_sorted = df.sort_values(['State', 'Level', 'Area_Name', 'Type'])
    
    # Reorder columns to put State first
    cols = ['State'] + [col for col in df.columns if col != 'State']
    df_sorted = df_sorted[cols]
    
    # Save to CSV
    df_sorted.to_csv(output_path, index=False)
    print(f"\nDelhi NCR data saved to: {output_path}")
    
    return df_sorted

def print_summary_stats(df):
    """Print summary statistics of the extracted data"""
    print("\n" + "="*60)
    print("DELHI NCR DATA SUMMARY")
    print("="*60)
    
    print(f"Total records: {len(df)}")
    
    # Count by state
    print(f"\nBy State:")
    state_counts = df['State'].value_counts()
    for state, count in state_counts.items():
        print(f"  {state}: {count} records")
    
    # Count by administrative level
    print(f"\nBy Administrative Level:")
    level_counts = df['Level'].value_counts()
    for level, count in level_counts.items():
        print(f"  {level}: {count} records")
    
    # Count by type
    print(f"\nBy Area Type:")
    type_counts = df['Type'].value_counts()
    for area_type, count in type_counts.items():
        print(f"  {area_type}: {count} records")
    
    # Show unique regions by state
    print(f"\nDelhi NCR Regions by State:")
    for state in sorted(df['State'].unique()):
        regions = df[df['State'] == state]['Area_Name'].unique()
        print(f"  {state} ({len(regions)} regions):")
        for region in sorted(regions):
            print(f"    - {region}")
    
    # Population density statistics for 'Total' areas only
    total_areas = df[(df['Type'] == 'Total') & (df['Pop_Density'].notna())]
    if len(total_areas) > 0:
        print(f"\nPopulation Density Statistics (Total areas only):")
        print(f"  Records with density data: {len(total_areas)}")
        print(f"  Mean: {total_areas['Pop_Density'].mean():.1f} per sq km")
        print(f"  Median: {total_areas['Pop_Density'].median():.1f} per sq km")
        print(f"  Max: {total_areas['Pop_Density'].max():.1f} per sq km")
        print(f"  Min: {total_areas['Pop_Density'].min():.1f} per sq km")
        
        # Top 10 densest areas
        top_10 = total_areas.nlargest(10, 'Pop_Density')
        print(f"\nTop 10 Densest Areas:")
        for idx, (_, row) in enumerate(top_10.iterrows(), 1):
            print(f"  {idx:2d}. {row['Area_Name']} ({row['State']}): {row['Pop_Density']:.1f} per sq km")

def main():
    """Main function"""
    # File paths
    input_csv = "A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.csv"
    output_csv = "Delhi_NCR_Population_Data_Clean.csv"
    
    # Check if input file exists
    if not Path(input_csv).exists():
        print(f"Error: Input file '{input_csv}' not found!")
        return
    
    try:
        # Step 1: Load the data
        df = load_census_data(input_csv)
        
        # Step 2: Clean numeric data
        df = clean_numeric_data(df)
        
        # Step 3: Extract Delhi NCR regions
        delhi_ncr_df = extract_delhi_ncr_regions(df)
        
        if len(delhi_ncr_df) == 0:
            print("Warning: No Delhi NCR regions found in the data!")
            return
        
        # Step 4: Save the clipped data
        delhi_ncr_df = save_clipped_data(delhi_ncr_df, output_csv)
        
        # Step 5: Print summary statistics
        print_summary_stats(delhi_ncr_df)
        
        print(f"\n✅ Successfully created clean Delhi NCR dataset: {output_csv}")
        print(f"📊 Ready for Step 2: Choropleth visualization with GeoJSON mapping")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()