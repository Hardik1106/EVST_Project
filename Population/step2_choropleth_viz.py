#!/usr/bin/env python3
"""
Delhi NCR Choropleth Visualization Script
Step 2: Create an interactive choropleth map showing population density for Delhi NCR districts
"""

import pandas as pd
import numpy as np
import json
import folium
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

def load_delhi_ncr_data(csv_path):
    """Load the Delhi NCR census data"""
    print("Loading Delhi NCR census data...")
    
    df = pd.read_csv(csv_path)
    
    # Filter for 'Total' type and DISTRICT level only for the map
    map_data = df[(df['Type'] == 'Total') & (df['Level'] == 'DISTRICT')].copy()
    
    print(f"Loaded {len(df)} total records, {len(map_data)} district-level records for mapping")
    return df, map_data

def load_geojson_data(geojson_path):
    """Load the GeoJSON data"""
    print("Loading GeoJSON data...")
    
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    # Extract district names
    district_names = []
    for feature in geojson_data['features']:
        district_names.append(feature['properties']['dtname'])
    
    print(f"Loaded GeoJSON with {len(district_names)} districts")
    print(f"Districts: {sorted(district_names)}")
    
    return geojson_data, district_names

def create_district_mapping(census_data, geojson_districts):
    """Create mapping between census data and GeoJSON district names"""
    print("\nCreating district name mapping...")
    
    # Get unique area names from census data (district level)
    census_districts = census_data['Area_Name'].unique()
    
    # Manual mapping for districts that don't match exactly
    name_mapping = {
        # Delhi districts in census appear without 'Delhi' suffix
        'Central': 'Central Delhi',
        'East': 'East Delhi', 
        'North': 'North Delhi',
        'North East': 'North East Delhi',
        'North West': 'North West Delhi',
        'South': 'South Delhi',
        'South East': 'South East Delhi',  # Note: not found in census
        'South West': 'South West Delhi',
        'West Delhi': 'West Delhi',  # This might conflict with 'West'
        
        # Other potential mappings
        'Gurgaon': 'Gurugram',  # Census uses Gurgaon, GeoJSON uses Gurugram
        'Charkhi Dadri': 'Charki Dadri',  # Different spelling
        
        # Keep exact matches as-is
        'Alwar': 'Alwar',
        'Baghpat': 'Baghpat', 
        'Bharatpur': 'Bharatpur',
        'Bulandshahr': 'Bulandshahr',
        'Gautam Buddha Nagar': 'Gautam Buddha Nagar',
        'Ghaziabad': 'Ghaziabad',
        'Hapur': 'Hapur',
        'Meerut': 'Meerut',
        'Muzaffarnagar': 'Muzaffarnagar', 
        'New Delhi': 'New Delhi',
        'Shahdara': 'Shahdara',
        'Shamli': 'Shamli',
        'West': 'West',  # This is ambiguous - could be West Delhi or just West
        'Bhiwani': 'Bhiwani',
        'Faridabad': 'Faridabad',
        'Jhajjar': 'Jhajjar',
        'Jind': 'Jind', 
        'Karnal': 'Karnal',
        'Mahendragarh': 'Mahendragarh',
        'Nuh': 'Nuh',
        'Palwal': 'Palwal',
        'Panipat': 'Panipat',
        'Rewari': 'Rewari',
        'Rohtak': 'Rohtak',
        'Sonipat': 'Sonipat'
    }
    
    # Create the mapping dataframe
    mapping_df = pd.DataFrame(list(name_mapping.items()), 
                             columns=['Census_Name', 'GeoJSON_Name'])
    
    print("District mapping:")
    for _, row in mapping_df.iterrows():
        print(f"  {row['Census_Name']} -> {row['GeoJSON_Name']}")
    
    return mapping_df

def merge_data_with_geojson(census_data, geojson_data, mapping_df):
    """Merge census data with GeoJSON using the mapping"""
    print("\nMerging census data with GeoJSON...")
    
    # Create a merged dataset
    merged_data = []
    
    for feature in geojson_data['features']:
        geojson_name = feature['properties']['dtname']
        
        # Find corresponding census name
        mapping_row = mapping_df[mapping_df['GeoJSON_Name'] == geojson_name]
        
        if len(mapping_row) > 0:
            census_name = mapping_row.iloc[0]['Census_Name']
            
            # Find census data for this district
            census_row = census_data[census_data['Area_Name'] == census_name]
            
            if len(census_row) > 0:
                row_data = census_row.iloc[0]
                merged_data.append({
                    'District': geojson_name,
                    'Census_Name': census_name,
                    'Population': row_data['Population'],
                    'Area_sq_km': row_data['Area_sq_km'],
                    'Pop_Density': row_data['Pop_Density'],
                    'State': row_data.get('State', 'Unknown')
                })
                print(f"  ✓ Matched: {census_name} -> {geojson_name} (Density: {row_data['Pop_Density']:.0f})")
            else:
                print(f"  ✗ No census data found for: {census_name} -> {geojson_name}")
                # Add with NaN values
                merged_data.append({
                    'District': geojson_name,
                    'Census_Name': census_name,
                    'Population': np.nan,
                    'Area_sq_km': np.nan,
                    'Pop_Density': np.nan,
                    'State': 'Unknown'
                })
        else:
            print(f"  ✗ No mapping found for GeoJSON district: {geojson_name}")
            # Add with NaN values
            merged_data.append({
                'District': geojson_name,
                'Census_Name': geojson_name,
                'Population': np.nan,
                'Area_sq_km': np.nan,
                'Pop_Density': np.nan,
                'State': 'Unknown'
            })
    
    merged_df = pd.DataFrame(merged_data)
    print(f"\nMerged data created with {len(merged_df)} districts")
    print(f"Districts with population density data: {merged_df['Pop_Density'].notna().sum()}")
    
    return merged_df

def create_choropleth_map(geojson_data, merged_df, output_path):
    """Create an interactive choropleth map"""
    print("\nCreating choropleth map...")
    
    # Calculate map center (rough center of Delhi NCR)
    center_lat, center_lon = 28.6, 77.2
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='OpenStreetMap'
    )
    
    # Prepare data for choropleth with log transformation
    # Create log-transformed population density for better visualization
    merged_df_log = merged_df.copy()
    
    # Apply log transformation to population density (add 1 to handle zeros)
    merged_df_log['Pop_Density_Log'] = np.where(
        merged_df_log['Pop_Density'].notna() & (merged_df_log['Pop_Density'] > 0),
        np.log(merged_df_log['Pop_Density']),
        np.nan
    )
    
    print(f"Log transformation applied:")
    print(f"  Original density range: {merged_df['Pop_Density'].min():.0f} - {merged_df['Pop_Density'].max():.0f}")
    print(f"  Log density range: {merged_df_log['Pop_Density_Log'].min():.2f} - {merged_df_log['Pop_Density_Log'].max():.2f}")
    
    # Create a dictionary mapping district names to log population density
    density_dict = {}
    for _, row in merged_df_log.iterrows():
        if pd.notna(row['Pop_Density_Log']):
            density_dict[row['District']] = row['Pop_Density_Log']
        else:
            density_dict[row['District']] = 0  # Use 0 for missing data
    
    # Add choropleth layer using log-transformed data
    choropleth = folium.Choropleth(
        geo_data=geojson_data,
        name='Population Density (Log Scale)',
        data=merged_df_log,
        columns=['District', 'Pop_Density_Log'],
        key_on='feature.properties.dtname',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Log(Population Density)',
        nan_fill_color='lightgray',
        nan_fill_opacity=0.4
    ).add_to(m)
    
    # Add tooltips with district information
    for feature in geojson_data['features']:
        district_name = feature['properties']['dtname']
        
        # Get data for this district
        district_data = merged_df[merged_df['District'] == district_name]
        
        if len(district_data) > 0:
            row = district_data.iloc[0]
            
            if pd.notna(row['Pop_Density']):
                popup_text = f"""
                <b>{district_name}</b><br>
                State: {row['State']}<br>
                Population: {row['Population']:,.0f}<br>
                Area: {row['Area_sq_km']:.1f} sq km<br>
                <b>Population Density: {row['Pop_Density']:.0f} per sq km</b><br>
                <i>Log(Density): {np.log(row['Pop_Density']):.2f}</i>
                """
            else:
                popup_text = f"""
                <b>{district_name}</b><br>
                <i>No census data available</i>
                """
        else:
            popup_text = f"<b>{district_name}</b><br><i>No data</i>"
        
        # Add popup to the feature
        folium.GeoJson(
            feature,
            popup=folium.Popup(popup_text, max_width=300),
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': 'transparent',
                'weight': 0
            }
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add title
    title_html = '''
    <h3 align="center" style="font-size:20px"><b>Delhi NCR Population Density (Log Scale)</b></h3>
    <p align="center" style="font-size:14px">Population per square kilometer by district - Log transformed for better visualization</p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    m.save(output_path)
    print(f"Interactive map saved to: {output_path}")
    
    return m

def create_static_visualizations(merged_df):
    """Create static visualizations"""
    print("\nCreating static visualizations...")
    
    # Filter out districts with no data
    plot_data = merged_df[merged_df['Pop_Density'].notna()].copy()
    
    if len(plot_data) == 0:
        print("No data available for static visualizations")
        return
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Add log transformation for static visualizations too
    plot_data['Pop_Density_Log'] = np.log(plot_data['Pop_Density'])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(24, 16))  # Increased size to accommodate more plots
    
    # 1. Horizontal bar chart of all districts (original scale)
    ax1 = plt.subplot(3, 3, (1, 2))
    plot_data_sorted = plot_data.sort_values('Pop_Density')
    bars = ax1.barh(range(len(plot_data_sorted)), plot_data_sorted['Pop_Density'], 
                    color='lightblue', edgecolor='navy', alpha=0.7)
    ax1.set_yticks(range(len(plot_data_sorted)))
    ax1.set_yticklabels(plot_data_sorted['District'], fontsize=10)
    ax1.set_xlabel('Population Density (per sq km)', fontsize=12)
    ax1.set_title('Population Density by District (Delhi NCR)', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, plot_data_sorted['Pop_Density'])):
        ax1.text(value + max(plot_data_sorted['Pop_Density']) * 0.01, i, f'{int(value)}', 
                va='center', fontsize=9)
    
    # 2. Horizontal bar chart (log scale)
    ax2 = plt.subplot(3, 3, 3)
    plot_data_log_sorted = plot_data.sort_values('Pop_Density_Log')
    bars_log = ax2.barh(range(len(plot_data_log_sorted)), plot_data_log_sorted['Pop_Density_Log'], 
                       color='lightcyan', edgecolor='darkblue', alpha=0.7)
    ax2.set_yticks(range(len(plot_data_log_sorted)))
    ax2.set_yticklabels(plot_data_log_sorted['District'], fontsize=10)
    ax2.set_xlabel('Log(Population Density)', fontsize=12)
    ax2.set_title('Log Population Density by District', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars_log, plot_data_log_sorted['Pop_Density_Log'])):
        ax2.text(value + max(plot_data_log_sorted['Pop_Density_Log']) * 0.01, i, f'{value:.2f}', 
                va='center', fontsize=9)
    
    # 3. Density by state
    ax3 = plt.subplot(3, 3, 4)
    state_avg = plot_data.groupby('State')['Pop_Density'].mean().sort_values(ascending=False)
    bars3 = ax3.bar(range(len(state_avg)), state_avg.values, 
                    color='lightcoral', edgecolor='darkred', alpha=0.7)
    ax3.set_xticks(range(len(state_avg)))
    ax3.set_xticklabels(state_avg.index, rotation=45, ha='right')
    ax3.set_ylabel('Avg Population Density (per sq km)')
    ax3.set_title('Average Density by State', fontsize=12, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars3, state_avg.values):
        ax3.text(bar.get_x() + bar.get_width()/2, value + max(state_avg.values) * 0.01,
                f'{int(value)}', ha='center', va='bottom', fontsize=9)
    
    # 4. Distribution histogram (original scale)
    ax4 = plt.subplot(3, 3, 5)
    ax4.hist(plot_data['Pop_Density'], bins=15, color='lightgreen', 
             edgecolor='darkgreen', alpha=0.7)
    ax4.set_xlabel('Population Density (per sq km)')
    ax4.set_ylabel('Number of Districts')
    ax4.set_title('Distribution of Population Density', fontsize=12, fontweight='bold')
    ax4.grid(alpha=0.3)
    
    # 5. Distribution histogram (log scale)
    ax5 = plt.subplot(3, 3, 6)
    ax5.hist(plot_data['Pop_Density_Log'], bins=15, color='lightsteelblue', 
             edgecolor='darkblue', alpha=0.7)
    ax5.set_xlabel('Log(Population Density)')
    ax5.set_ylabel('Number of Districts')
    ax5.set_title('Distribution of Log Population Density', fontsize=12, fontweight='bold')
    ax5.grid(alpha=0.3)
    
    # 6. Population vs Area scatter plot
    ax6 = plt.subplot(3, 3, 7)
    scatter = ax6.scatter(plot_data['Area_sq_km'], plot_data['Population'], 
                         c=plot_data['Pop_Density_Log'], cmap='viridis', s=100, alpha=0.7)
    ax6.set_xlabel('Area (sq km)')
    ax6.set_ylabel('Population')
    ax6.set_title('Population vs Area\n(Color = Log Density)', fontsize=12, fontweight='bold')
    ax6.set_xscale('log')
    ax6.set_yscale('log')
    plt.colorbar(scatter, ax=ax6, label='Log(Population Density)')
    
    # 7. Top 10 densest districts (original scale)
    ax7 = plt.subplot(3, 3, 8)
    top_10 = plot_data.nlargest(10, 'Pop_Density')
    bars7 = ax7.bar(range(len(top_10)), top_10['Pop_Density'], 
                    color='orange', edgecolor='darkorange', alpha=0.7)
    ax7.set_xticks(range(len(top_10)))
    ax7.set_xticklabels(top_10['District'], rotation=45, ha='right', fontsize=10)
    ax7.set_ylabel('Population Density (per sq km)')
    ax7.set_title('Top 10 Densest Districts', fontsize=12, fontweight='bold')
    ax7.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars7, top_10['Pop_Density']):
        ax7.text(bar.get_x() + bar.get_width()/2, value + max(top_10['Pop_Density']) * 0.01,
                f'{int(value)}', ha='center', va='bottom', fontsize=9, rotation=90)
    
    # 8. Top 10 densest districts (log scale)
    ax8 = plt.subplot(3, 3, 9)
    top_10_log = plot_data.nlargest(10, 'Pop_Density_Log')
    bars8 = ax8.bar(range(len(top_10_log)), top_10_log['Pop_Density_Log'], 
                    color='salmon', edgecolor='darkred', alpha=0.7)
    ax8.set_xticks(range(len(top_10_log)))
    ax8.set_xticklabels(top_10_log['District'], rotation=45, ha='right', fontsize=10)
    ax8.set_ylabel('Log(Population Density)')
    ax8.set_title('Top 10 Densest Districts (Log Scale)', fontsize=12, fontweight='bold')
    ax8.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars8, top_10_log['Pop_Density_Log']):
        ax8.text(bar.get_x() + bar.get_width()/2, value + max(top_10_log['Pop_Density_Log']) * 0.01,
                f'{value:.2f}', ha='center', va='bottom', fontsize=9, rotation=90)
    
    plt.tight_layout()
    plt.savefig('Delhi_NCR_Population_Density_Analysis_with_Log.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Static visualizations with log scale saved to: Delhi_NCR_Population_Density_Analysis_with_Log.png")

def print_final_summary(merged_df):
    """Print final summary of the analysis"""
    print("\n" + "="*70)
    print("DELHI NCR CHOROPLETH ANALYSIS SUMMARY")
    print("="*70)
    
    total_districts = len(merged_df)
    districts_with_data = merged_df['Pop_Density'].notna().sum()
    
    print(f"Total districts in map: {total_districts}")
    print(f"Districts with population data: {districts_with_data}")
    print(f"Data coverage: {districts_with_data/total_districts*100:.1f}%")
    
    if districts_with_data > 0:
        data_districts = merged_df[merged_df['Pop_Density'].notna()]
        
        print(f"\nPopulation Density Statistics:")
        print(f"  Mean: {data_districts['Pop_Density'].mean():.1f} per sq km")
        print(f"  Median: {data_districts['Pop_Density'].median():.1f} per sq km")
        print(f"  Range: {data_districts['Pop_Density'].min():.1f} - {data_districts['Pop_Density'].max():.1f} per sq km")
        
        print(f"\nTop 5 Densest Districts:")
        top_5 = data_districts.nlargest(5, 'Pop_Density')
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            print(f"  {i}. {row['District']} ({row['State']}): {row['Pop_Density']:.1f} per sq km")
        
        print(f"\nDistricts by State:")
        state_counts = merged_df['State'].value_counts()
        for state, count in state_counts.items():
            with_data = merged_df[(merged_df['State'] == state) & (merged_df['Pop_Density'].notna())]
            print(f"  {state}: {len(with_data)}/{count} districts with data")
    
    print(f"\n🗺️  Interactive map (Log Scale): Delhi_NCR_Choropleth_Map.html")
    print(f"📊 Static analysis with Log Scale: Delhi_NCR_Population_Density_Analysis_with_Log.png")

def main():
    """Main function"""
    # File paths
    csv_path = "Delhi_NCR_Population_Data_Clean.csv"
    geojson_path = "Delhi_NCR_Districts_final.geojson"
    map_output = "Delhi_NCR_Choropleth_Map.html"
    
    # Check if files exist
    if not Path(csv_path).exists():
        print(f"Error: Census data file '{csv_path}' not found!")
        print("Please run Step 1 first to create the Delhi NCR dataset.")
        return
    
    if not Path(geojson_path).exists():
        print(f"Error: GeoJSON file '{geojson_path}' not found!")
        return
    
    try:
        # Step 1: Load data
        full_data, district_data = load_delhi_ncr_data(csv_path)
        geojson_data, geojson_districts = load_geojson_data(geojson_path)
        
        # Step 2: Create mapping
        mapping_df = create_district_mapping(district_data, geojson_districts)
        
        # Step 3: Merge data
        merged_df = merge_data_with_geojson(district_data, geojson_data, mapping_df)
        
        # Step 4: Create choropleth map
        choropleth_map = create_choropleth_map(geojson_data, merged_df, map_output)
        
        # Step 5: Create static visualizations
        create_static_visualizations(merged_df)
        
        # Step 6: Print summary
        print_final_summary(merged_df)
        
        print(f"\n✅ Delhi NCR Choropleth visualization completed successfully!")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()