"""
Climate Vulnerability Index (CVI) Calculator for ALL Delhi NCR Districts

This script:
1. Calculates CVI for all districts in Delhi NCR
2. Generates visualizations and comparison charts
3. Creates an interactive HTML map with CVI scores overlaid on GeoJSON
4. Exports results to CSV and JSON formats

Based on the operational formulas:
1. Potential Impact (PI) = αE + βS
2. OUV Vulnerability = PI × (1 - AC)
3. ESC Potential Impact = δ × OUV + (1 - δ) × ESC_Dependency
4. Community Vulnerability (CV) = ESC × (1 - ESC_AC)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
import folium
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

# Get absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# ============================================================================
# CONFIGURATION
# ============================================================================

# List of all Delhi NCR districts
ALL_DISTRICTS = [
    'Alwar', 'Baghpat', 'Bharatpur', 'Bhiwani', 'Bulandshahr',
    'Central Delhi', 'Charki Dadri', 'East Delhi', 'Faridabad',
    'Gautam Buddha Nagar', 'Ghaziabad', 'Gurugram', 'Hapur',
    'Jhajjar', 'Jind', 'Karnal', 'Mahendragarh', 'Meerut',
    'Muzaffarnagar', 'New Delhi', 'North Delhi', 'North East Delhi',
    'North West Delhi', 'Nuh', 'Palwal', 'Panipat', 'Rewari',
    'Rohtak', 'Shahdara', 'Shamli', 'Sonipat', 'South Delhi',
    'South East Delhi', 'South West Delhi', 'West Delhi'
]

# District name mapping for data matching
# (Different datasets may use different names for the same district)
DISTRICT_NAME_MAPPING = {
    'Gurugram': 'Gurgaon',  # Population data uses old name
    'Gautam Buddha Nagar': 'Gautam Budh Nagar',  # Alternative spelling
}

# Default AQI values for districts (based on typical air quality patterns)
# Higher values for urban Delhi districts, lower for rural/peripheral districts
DEFAULT_AQI = {
    'Central Delhi': 178, 'New Delhi': 175, 'East Delhi': 168,
    'North Delhi': 170, 'North East Delhi': 165, 'North West Delhi': 162,
    'South Delhi': 160, 'South East Delhi': 158, 'South West Delhi': 156,
    'West Delhi': 164, 'Shahdara': 166,
    'Ghaziabad': 145, 'Faridabad': 140, 'Gurugram': 138,
    'Gautam Buddha Nagar': 135, 'Baghpat': 110, 'Bulandshahr': 105,
    'Hapur': 108, 'Meerut': 125, 'Muzaffarnagar': 100,
    'Shamli': 95, 'Alwar': 92, 'Bharatpur': 88,
    'Rewari': 90, 'Jhajjar': 115, 'Rohtak': 118,
    'Sonipat': 120, 'Panipat': 122, 'Karnal': 105,
    'Jind': 100, 'Bhiwani': 98, 'Mahendragarh': 85,
    'Charki Dadri': 102, 'Nuh': 110, 'Palwal': 112
}

# ============================================================================
# STEP 1: Load all available data
# ============================================================================

def load_data():
    """Load all necessary data files"""
    
    print("="*80)
    print("LOADING DATA FILES")
    print("="*80)
    
    # Rainfall data
    rainfall_path = os.path.join(project_root, 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv')
    df_rainfall = pd.read_csv(rainfall_path)
    print(f"✓ Loaded rainfall data: {len(df_rainfall)} records")
    
    # Temperature data
    temp_path = os.path.join(project_root, 'delhi_ncr_temp_monthly_avg_2013_2024.csv')
    df_temp = pd.read_csv(temp_path)
    print(f"✓ Loaded temperature data: {len(df_temp)} records")
    
    # Population data
    pop_path = os.path.join(project_root, 'population_data_and_vis', 'Delhi_NCR_Population_Data_Clean.csv')
    df_pop = pd.read_csv(pop_path)
    print(f"✓ Loaded population data: {len(df_pop)} records")
    
    # Income data
    income_path = os.path.join(project_root, 'Income', 'district_wise.csv')
    df_income = pd.read_csv(income_path)
    print(f"✓ Loaded income data: {len(df_income)} records")
    
    # Groundwater data
    gw_path = os.path.join(project_root, 'ground_water_vis', 'ncr_groundwater_yearly.csv')
    df_groundwater = pd.read_csv(gw_path)
    print(f"✓ Loaded groundwater data: {len(df_groundwater)} records")
    
    # GeoJSON data
    geojson_path = os.path.join(project_root, 'GeoJsons', 'Delhi_NCR_Districts_final.geojson')
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    print(f"✓ Loaded GeoJSON data: {len(geojson_data['features'])} districts")
    
    print()
    
    return {
        'rainfall': df_rainfall,
        'temperature': df_temp,
        'population': df_pop,
        'income': df_income,
        'groundwater': df_groundwater,
        'geojson': geojson_data
    }

# ============================================================================
# STEP 2: Calculate Exposure Index (E)
# ============================================================================

def calculate_exposure_index(data, district_name, verbose=False):
    """
    Calculate Exposure Index based on:
    - Temperature extremes (max temp variability, heat waves)
    - Rainfall variability (CV, extreme events)
    - Air Quality Index (AQI)
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"CALCULATING EXPOSURE INDEX FOR: {district_name}")
        print(f"{'='*80}")
    
    df_rainfall = data['rainfall']
    df_temp = data['temperature']
    
    # Clean district name for matching
    district_clean = district_name.lower().strip()
    
    # Get AQI value
    aqi_value = DEFAULT_AQI.get(district_name, 100)
    if verbose:
        print(f"  Air Quality Index (AQI): {aqi_value}")
    
    # 1. Rainfall Variability
    rain_district = df_rainfall[df_rainfall['DISTRICT_NAME_clean'] == district_clean].copy()
    
    if len(rain_district) == 0:
        # Try alternative matching
        rain_district = df_rainfall[df_rainfall['DISTRICT_NAME'].str.lower().str.contains(district_clean.split()[0])].copy()
    
    if len(rain_district) == 0:
        if verbose:
            print(f"⚠ No rainfall data found for {district_name}")
        rainfall_cv = 0
        extreme_rain_days = 0
    else:
        rainfall_cv = rain_district['RAINFALL'].std() / rain_district['RAINFALL'].mean() if rain_district['RAINFALL'].mean() > 0 else 0
        rain_95th = rain_district['RAINFALL'].quantile(0.95)
        extreme_rain_days = (rain_district['RAINFALL'] > rain_95th).sum()
        
        if verbose:
            print(f"  Rainfall CV: {rainfall_cv:.3f}")
            print(f"  Extreme rainfall events: {extreme_rain_days}")
    
    # 2. Temperature Extremes
    temp_district = df_temp[df_temp['DISTRICT_NAME'] == district_name].copy()
    
    if len(temp_district) == 0:
        temp_district = df_temp[df_temp['DISTRICT_NAME'].str.lower().str.contains(district_clean.split()[0])].copy()
    
    if len(temp_district) == 0:
        if verbose:
            print(f"⚠ No temperature data found for {district_name}")
        temp_max_mean = 0
        temp_variability = 0
        heat_wave_count = 0
    else:
        temp_max_mean = temp_district['maxT'].mean() if 'maxT' in temp_district.columns else 0
        temp_variability = temp_district['maxT'].std() if 'maxT' in temp_district.columns else 0
        if 'maxT' in temp_district.columns:
            temp_95th = temp_district['maxT'].quantile(0.95)
            heat_wave_count = (temp_district['maxT'] > temp_95th).sum()
        else:
            heat_wave_count = 0
        
        if verbose:
            print(f"  Average Max Temperature: {temp_max_mean:.2f}°C")
            print(f"  Temperature Variability: {temp_variability:.2f}°C")
            print(f"  Heat wave events: {heat_wave_count}")
    
    exposure_components = {
        'rainfall_cv': rainfall_cv,
        'extreme_rainfall_events': extreme_rain_days,
        'avg_max_temp': temp_max_mean,
        'temp_variability': temp_variability,
        'heat_wave_count': heat_wave_count,
        'aqi': aqi_value
    }
    
    # Weighted average with AQI included
    exposure_score = (
        0.25 * rainfall_cv +
        0.15 * (extreme_rain_days / 10) +
        0.15 * (temp_max_mean / 50) +
        0.15 * (temp_variability / 10) +
        0.10 * (heat_wave_count / 20) +
        0.20 * (aqi_value / 400)
    )
    
    if verbose:
        print(f"\n  ➤ EXPOSURE INDEX (E): {exposure_score:.4f}")
    
    return exposure_score, exposure_components

# ============================================================================
# STEP 3: Calculate Sensitivity Index (S)
# ============================================================================

def calculate_sensitivity_index(data, district_name, verbose=False):
    """
    Calculate Sensitivity Index based on:
    - Population density
    - Water stress (groundwater depletion)
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"CALCULATING SENSITIVITY INDEX FOR: {district_name}")
        print(f"{'='*80}")
    
    df_pop = data['population']
    df_gw = data['groundwater']
    
    # 1. Population Density
    # Try to match district name with Area_Name in population data
    # Use name mapping if available
    search_name = DISTRICT_NAME_MAPPING.get(district_name, district_name)
    district_search = search_name.lower().strip()
    
    # First, try exact match
    district_pop = df_pop[
        (df_pop['Area_Name'].str.lower() == district_search) &
        (df_pop['Type'] == 'Total')
    ]
    
    # If no exact match, try partial match with first word
    if len(district_pop) == 0:
        district_first_word = district_search.split()[0]
        district_pop = df_pop[
            (df_pop['Area_Name'].str.lower().str.contains(district_first_word)) &
            (df_pop['Type'] == 'Total')
        ]
    
    # Filter to get district-level data (not sub-district)
    if len(district_pop) > 0:
        district_pop_level = district_pop[district_pop['Level'] == 'DISTRICT']
        if len(district_pop_level) > 0:
            district_pop = district_pop_level
    
    if len(district_pop) == 0:
        if verbose:
            print(f"⚠ No population data found for {district_name}")
        pop_density = 0
    else:
        pop_density = district_pop['Pop_Density'].iloc[0] if 'Pop_Density' in district_pop.columns else 0
        # Handle NaN values
        if pd.isna(pop_density):
            pop_density = 0
        if verbose:
            print(f"  Population Density: {pop_density:.0f} persons/km²")
    
    # 2. Water Stress (Groundwater depletion rate)
    district_clean = district_name.lower().strip()
    gw_district = df_gw[df_gw['district_geojson'].str.lower() == district_clean].copy()
    
    if len(gw_district) == 0:
        for name_part in district_name.split():
            gw_district = df_gw[df_gw['district_geojson'].str.lower().str.contains(name_part.lower())].copy()
            if len(gw_district) > 0:
                break
    
    if len(gw_district) == 0:
        if verbose:
            print(f"⚠ No groundwater data found for {district_name}")
        gw_depletion_rate = 0
        avg_gw_level = 0
    else:
        gw_district = gw_district.sort_values('year')
        if len(gw_district) > 1:
            years = gw_district['year'].values
            levels = gw_district['currentlevel'].values
            slope, intercept, r_value, p_value, std_err = stats.linregress(years, levels)
            gw_depletion_rate = -slope if slope < 0 else 0
        else:
            gw_depletion_rate = 0
        
        avg_gw_level = gw_district['currentlevel'].mean()
        if verbose:
            print(f"  Average Groundwater Level: {avg_gw_level:.2f} m")
            print(f"  Groundwater Depletion Rate: {gw_depletion_rate:.4f} m/year")
    
    sensitivity_components = {
        'population_density': pop_density,
        'gw_depletion_rate': gw_depletion_rate,
        'avg_gw_level': avg_gw_level
    }
    
    # Weighted average
    sensitivity_score = (
        0.6 * (pop_density / 20000) +
        0.4 * (gw_depletion_rate / 2)
    )
    
    if verbose:
        print(f"\n  ➤ SENSITIVITY INDEX (S): {sensitivity_score:.4f}")
    
    return sensitivity_score, sensitivity_components

# ============================================================================
# STEP 4: Calculate Adaptive Capacity Index (AC)
# ============================================================================

def calculate_adaptive_capacity_index(data, district_name, verbose=False):
    """
    Calculate Adaptive Capacity Index based on:
    - Income levels
    - Urbanization rate (proxy for infrastructure)
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"CALCULATING ADAPTIVE CAPACITY INDEX FOR: {district_name}")
        print(f"{'='*80}")
    
    df_income = data['income']
    df_pop = data['population']
    
    # 1. Income Level
    # Use name mapping if available
    search_name = DISTRICT_NAME_MAPPING.get(district_name, district_name)
    district_income = df_income[df_income['DISTRICT'].str.lower().str.contains(search_name.lower().split()[0])]
    
    if len(district_income) == 0:
        if verbose:
            print(f"⚠ No income data found for {district_name}")
        income_level = 0
    else:
        income_level = pd.to_numeric(district_income['INCOME'].iloc[0], errors='coerce')
        if pd.isna(income_level):
            income_level = 0
        if verbose:
            print(f"  Per Capita Income: ₹{income_level:,.0f}")
    
    # 2. Urbanization Rate
    # Try to match district name with Area_Name in population data
    # Use name mapping if available
    search_name = DISTRICT_NAME_MAPPING.get(district_name, district_name)
    district_search = search_name.lower().strip()
    
    # First, try exact match
    district_pop = df_pop[df_pop['Area_Name'].str.lower() == district_search]
    
    # If no exact match, try partial match with first word
    if len(district_pop) == 0:
        district_first_word = district_search.split()[0]
        district_pop = df_pop[df_pop['Area_Name'].str.lower().str.contains(district_first_word)]
    
    if len(district_pop) == 0:
        if verbose:
            print(f"⚠ No population data found for {district_name}")
        urbanization_rate = 0
        total_population = 0
        urban_population = 0
    else:
        # Filter to get district-level data (not sub-district)
        district_pop_level = district_pop[district_pop['Level'] == 'DISTRICT']
        
        # If no district level data, use whatever is available
        if len(district_pop_level) == 0:
            district_pop_level = district_pop
        
        # Get Total and Urban population
        total_pop_row = district_pop_level[district_pop_level['Type'] == 'Total']
        urban_pop_row = district_pop_level[district_pop_level['Type'] == 'Urban']
        
        if len(total_pop_row) > 0 and len(urban_pop_row) > 0:
            total_population = total_pop_row['Population'].iloc[0]
            urban_population = urban_pop_row['Population'].iloc[0]
            
            # Handle cases where population might be 0 or NaN
            if pd.notna(total_population) and pd.notna(urban_population) and total_population > 0:
                urbanization_rate = (urban_population / total_population) * 100
            else:
                urbanization_rate = 0
        else:
            urbanization_rate = 0
            total_population = 0
            urban_population = 0
        
        if verbose:
            print(f"  Total Population: {total_population:,.0f}")
            print(f"  Urban Population: {urban_population:,.0f}")
            print(f"  Urbanization Rate: {urbanization_rate:.2f}%")
    
    ac_components = {
        'income': income_level,
        'urbanization_rate': urbanization_rate
    }
    
    # Weighted average
    ac_score = (
        0.7 * (income_level / 1000000) +
        0.3 * (urbanization_rate / 100)
    )
    
    if verbose:
        print(f"\n  ➤ ADAPTIVE CAPACITY INDEX (AC): {ac_score:.4f}")
    
    return ac_score, ac_components

# ============================================================================
# STEP 5: Calculate CVI for a District
# ============================================================================

def calculate_cvi(district_name, data, alpha=0.5, beta=0.5, delta=0.6, verbose=False):
    """Calculate complete CVI for a district"""
    
    if verbose:
        print(f"\n\n{'#'*80}")
        print(f"# CLIMATE VULNERABILITY INDEX CALCULATION")
        print(f"# District: {district_name}")
        print(f"{'#'*80}\n")
    
    # Calculate component indices
    E, exposure_comp = calculate_exposure_index(data, district_name, verbose)
    S, sensitivity_comp = calculate_sensitivity_index(data, district_name, verbose)
    AC, ac_comp = calculate_adaptive_capacity_index(data, district_name, verbose)
    
    # Step 1: Potential Impact (PI)
    PI = alpha * E + beta * S
    
    # Step 2: OUV Vulnerability
    OUV = PI * (1 - AC)
    
    # Step 3: ESC Potential Impact
    ESC_Dependency = 0.5
    ESC = delta * OUV + (1 - delta) * ESC_Dependency
    
    # Step 4: Community Vulnerability (CV)
    ESC_AC = AC
    CV = ESC * (1 - ESC_AC)
    
    # Classify vulnerability level
    if CV < 0.2:
        vulnerability_level = "LOW"
    elif CV < 0.4:
        vulnerability_level = "MODERATE"
    elif CV < 0.6:
        vulnerability_level = "HIGH"
    else:
        vulnerability_level = "VERY HIGH"
    
    if verbose:
        print(f"\n{'#'*80}")
        print(f"# FINAL CVI SCORE: {CV:.4f} ({vulnerability_level})")
        print(f"{'#'*80}\n")
    
    results = {
        'district': district_name,
        'exposure': E,
        'sensitivity': S,
        'adaptive_capacity': AC,
        'potential_impact': PI,
        'ouv_vulnerability': OUV,
        'esc_impact': ESC,
        'community_vulnerability': CV,
        'cvi_score': CV,  # Alias for easier reference
        'vulnerability_level': vulnerability_level,
        'exposure_components': exposure_comp,
        'sensitivity_components': sensitivity_comp,
        'adaptive_capacity_components': ac_comp
    }
    
    return results

# ============================================================================
# STEP 6: Calculate CVI for All Districts
# ============================================================================

def calculate_all_districts_cvi(data):
    """Calculate CVI for all Delhi NCR districts"""
    
    print("\n" + "="*80)
    print("CALCULATING CVI FOR ALL DELHI NCR DISTRICTS")
    print("="*80 + "\n")
    
    all_results = []
    
    for i, district in enumerate(ALL_DISTRICTS, 1):
        print(f"[{i}/{len(ALL_DISTRICTS)}] Processing: {district}")
        try:
            result = calculate_cvi(district, data, verbose=False)
            all_results.append(result)
            print(f"  ✓ CVI Score: {result['cvi_score']:.4f} ({result['vulnerability_level']})")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            continue
    
    print(f"\n✓ Successfully calculated CVI for {len(all_results)} districts")
    
    return all_results

# ============================================================================
# STEP 7: Create Interactive HTML Map
# ============================================================================

def create_html_map(results_list, geojson_data, output_path):
    """Create an interactive Folium map with CVI scores"""
    
    print("\n" + "="*80)
    print("CREATING INTERACTIVE HTML MAP")
    print("="*80)
    
    # Create a DataFrame for easier manipulation
    df_results = pd.DataFrame(results_list)
    
    # Create a dictionary for quick lookup
    cvi_dict = dict(zip(df_results['district'], df_results['cvi_score']))
    level_dict = dict(zip(df_results['district'], df_results['vulnerability_level']))
    
    # Add CVI scores to GeoJSON properties
    for feature in geojson_data['features']:
        district_name = feature['properties']['dtname']
        feature['properties']['cvi_score'] = cvi_dict.get(district_name, 0)
        feature['properties']['vulnerability_level'] = level_dict.get(district_name, 'UNKNOWN')
    
    # Calculate center of Delhi NCR (approximate)
    center_lat = 28.5
    center_lon = 77.0
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles='OpenStreetMap'
    )
    
    # Define color scale
    colormap = folium.LinearColormap(
        colors=['#2ecc71', '#f39c12', '#e74c3c', '#8b0000'],
        vmin=df_results['cvi_score'].min(),
        vmax=df_results['cvi_score'].max(),
        caption='Climate Vulnerability Index (CVI)'
    )
    
    # Add choropleth layer
    folium.Choropleth(
        geo_data=geojson_data,
        name='CVI Choropleth',
        data=df_results,
        columns=['district', 'cvi_score'],
        key_on='feature.properties.dtname',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.8,
        legend_name='Climate Vulnerability Index (CVI)',
        highlight=True
    ).add_to(m)
    
    # Add interactive tooltips
    style_function = lambda x: {
        'fillColor': colormap(x['properties']['cvi_score']),
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.7
    }
    
    highlight_function = lambda x: {
        'weight': 4,
        'color': 'blue',
        'fillOpacity': 0.9
    }
    
    tooltip = folium.GeoJsonTooltip(
        fields=['dtname', 'cvi_score', 'vulnerability_level'],
        aliases=['District:', 'CVI Score:', 'Vulnerability:'],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )
    
    popup = folium.GeoJsonPopup(
        fields=['dtname', 'cvi_score', 'vulnerability_level'],
        aliases=['District:', 'CVI Score:', 'Vulnerability Level:'],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )
    
    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip,
        popup=popup
    ).add_to(m)
    
    # Add color legend
    colormap.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 600px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:16px; padding: 10px">
        <h3 style="margin:0; text-align:center;">Delhi NCR Climate Vulnerability Index (CVI)</h3>
        <p style="margin:5px 0; text-align:center; font-size:12px;">
            Climate vulnerability assessment based on Exposure, Sensitivity, and Adaptive Capacity
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    m.save(output_path)
    print(f"✓ Interactive map saved: {output_path}")
    
    return m

# ============================================================================
# STEP 8: Visualizations
# ============================================================================

def create_visualizations(results_list, output_dir):
    """Create comprehensive visualizations for CVI results"""
    
    print("\n" + "="*80)
    print("CREATING VISUALIZATIONS")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    df_results = pd.DataFrame(results_list)
    df_results = df_results.sort_values('cvi_score', ascending=False)
    
    # Set style
    sns.set_style("whitegrid")
    
    # 1. CVI Scores Ranking
    plt.figure(figsize=(14, 12))
    colors = df_results['cvi_score'].apply(lambda x: 
        '#8b0000' if x >= 0.6 else '#e74c3c' if x >= 0.4 else '#f39c12' if x >= 0.2 else '#2ecc71')
    
    plt.barh(df_results['district'], df_results['cvi_score'], color=colors)
    plt.xlabel('CVI Score', fontsize=12, fontweight='bold')
    plt.ylabel('District', fontsize=12, fontweight='bold')
    plt.title('Delhi NCR Climate Vulnerability Index - District Ranking', fontsize=14, fontweight='bold', pad=20)
    plt.axvline(x=0.2, color='green', linestyle='--', alpha=0.5, label='Low threshold')
    plt.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5, label='Moderate threshold')
    plt.axvline(x=0.6, color='red', linestyle='--', alpha=0.5, label='High threshold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cvi_ranking_all_districts.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: cvi_ranking_all_districts.png")
    plt.close()
    
    # 2. Component Comparison - Heatmap
    plt.figure(figsize=(12, 16))
    components_data = df_results[['district', 'exposure', 'sensitivity', 'adaptive_capacity', 'cvi_score']].set_index('district')
    sns.heatmap(components_data, annot=True, fmt='.3f', cmap='YlOrRd', cbar_kws={'label': 'Score'})
    plt.title('CVI Components Heatmap - All Districts', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('')
    plt.ylabel('District', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cvi_components_heatmap.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: cvi_components_heatmap.png")
    plt.close()
    
    # 3. Top 10 Most Vulnerable Districts
    plt.figure(figsize=(12, 8))
    top10 = df_results.head(10)
    plt.bar(range(len(top10)), top10['cvi_score'], color='#e74c3c')
    plt.xticks(range(len(top10)), top10['district'], rotation=45, ha='right')
    plt.ylabel('CVI Score', fontsize=12, fontweight='bold')
    plt.title('Top 10 Most Vulnerable Districts', fontsize=14, fontweight='bold', pad=20)
    plt.axhline(y=0.4, color='orange', linestyle='--', alpha=0.5, label='Moderate threshold')
    plt.axhline(y=0.6, color='red', linestyle='--', alpha=0.5, label='High threshold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_10_vulnerable_districts.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: top_10_vulnerable_districts.png")
    plt.close()
    
    # 4. Vulnerability Level Distribution
    plt.figure(figsize=(10, 6))
    level_counts = df_results['vulnerability_level'].value_counts()
    colors_pie = {'LOW': '#2ecc71', 'MODERATE': '#f39c12', 'HIGH': '#e74c3c', 'VERY HIGH': '#8b0000'}
    colors_list = [colors_pie[level] for level in level_counts.index]
    
    plt.pie(level_counts.values, labels=level_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=colors_list, textprops={'fontsize': 12, 'fontweight': 'bold'})
    plt.title('Distribution of Vulnerability Levels Across Delhi NCR', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vulnerability_level_distribution.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: vulnerability_level_distribution.png")
    plt.close()
    
    # 5. Scatter plot: Exposure vs Sensitivity
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df_results['exposure'], df_results['sensitivity'], 
                         c=df_results['cvi_score'], s=100, cmap='YlOrRd', 
                         alpha=0.6, edgecolors='black', linewidth=1.5)
    plt.colorbar(scatter, label='CVI Score')
    plt.xlabel('Exposure Index', fontsize=12, fontweight='bold')
    plt.ylabel('Sensitivity Index', fontsize=12, fontweight='bold')
    plt.title('Exposure vs Sensitivity (colored by CVI)', fontsize=14, fontweight='bold', pad=20)
    
    # Annotate top 5 vulnerable districts
    for idx in range(min(5, len(df_results))):
        row = df_results.iloc[idx]
        plt.annotate(row['district'], (row['exposure'], row['sensitivity']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exposure_vs_sensitivity_scatter.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: exposure_vs_sensitivity_scatter.png")
    plt.close()
    
    # 6. Summary Statistics Table
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    for _, row in df_results.head(20).iterrows():  # Show top 20
        table_data.append([
            row['district'],
            f"{row['exposure']:.3f}",
            f"{row['sensitivity']:.3f}",
            f"{row['adaptive_capacity']:.3f}",
            f"{row['cvi_score']:.3f}",
            row['vulnerability_level']
        ])
    
    table = ax.table(cellText=table_data,
                     colLabels=['District', 'Exposure', 'Sensitivity', 'Adaptive\nCapacity', 'CVI Score', 'Level'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.25, 0.12, 0.12, 0.13, 0.12, 0.13])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Color header
    for i in range(6):
        table[(0, i)].set_facecolor('#3498DB')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color vulnerability levels
    for i, row in enumerate(df_results.head(20).itertuples(), 1):
        level = row.vulnerability_level
        if level == 'LOW':
            color = '#d5f4e6'
        elif level == 'MODERATE':
            color = '#fdeaa8'
        elif level == 'HIGH':
            color = '#fadbd8'
        else:
            color = '#f5b7b1'
        table[(i, 5)].set_facecolor(color)
    
    plt.title('Climate Vulnerability Index - Top 20 Districts Summary', 
              fontsize=14, fontweight='bold', pad=20)
    plt.savefig(os.path.join(output_dir, 'cvi_summary_table_top20.png'), dpi=300, bbox_inches='tight')
    print("✓ Saved: cvi_summary_table_top20.png")
    plt.close()
    
    print(f"\n✓ All visualizations saved in: {output_dir}")

# ============================================================================
# STEP 9: Export Results
# ============================================================================

def export_results(results_list, output_dir):
    """Export results to CSV and JSON formats"""
    
    print("\n" + "="*80)
    print("EXPORTING RESULTS")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to DataFrame
    df_results = pd.DataFrame(results_list)
    
    # Save to CSV
    csv_path = os.path.join(output_dir, 'cvi_results_all_districts.csv')
    df_results.to_csv(csv_path, index=False)
    print(f"✓ CSV saved: {csv_path}")
    
    # Save to JSON (with component details)
    def convert_to_serializable(obj):
        if isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        else:
            return obj
    
    results_serializable = convert_to_serializable(results_list)
    
    json_path = os.path.join(output_dir, 'cvi_results_all_districts.json')
    with open(json_path, 'w') as f:
        json.dump(results_serializable, f, indent=2)
    print(f"✓ JSON saved: {json_path}")
    
    # Create summary statistics
    summary_stats = {
        'total_districts': len(df_results),
        'average_cvi': float(df_results['cvi_score'].mean()),
        'median_cvi': float(df_results['cvi_score'].median()),
        'min_cvi': float(df_results['cvi_score'].min()),
        'max_cvi': float(df_results['cvi_score'].max()),
        'std_cvi': float(df_results['cvi_score'].std()),
        'vulnerability_distribution': {
            'LOW': int((df_results['vulnerability_level'] == 'LOW').sum()),
            'MODERATE': int((df_results['vulnerability_level'] == 'MODERATE').sum()),
            'HIGH': int((df_results['vulnerability_level'] == 'HIGH').sum()),
            'VERY HIGH': int((df_results['vulnerability_level'] == 'VERY HIGH').sum())
        },
        'most_vulnerable': df_results.nlargest(5, 'cvi_score')['district'].tolist(),
        'least_vulnerable': df_results.nsmallest(5, 'cvi_score')['district'].tolist()
    }
    
    summary_path = os.path.join(output_dir, 'cvi_summary_statistics.json')
    with open(summary_path, 'w') as f:
        json.dump(summary_stats, f, indent=2)
    print(f"✓ Summary statistics saved: {summary_path}")
    
    print(f"\n✓ All results exported to: {output_dir}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("\n" + "#"*80)
    print("# DELHI NCR CLIMATE VULNERABILITY INDEX (CVI) CALCULATOR")
    print("# Calculating CVI for ALL Districts")
    print("#"*80 + "\n")
    
    # Load data
    data = load_data()
    
    # Calculate CVI for all districts
    all_results = calculate_all_districts_cvi(data)
    
    # Create output directories
    results_dir = os.path.join(script_dir, 'cvi_results')
    viz_dir = os.path.join(script_dir, 'cvi_visualizations')
    
    # Export results
    export_results(all_results, results_dir)
    
    # Create visualizations
    create_visualizations(all_results, viz_dir)
    
    # Create interactive HTML map
    html_path = os.path.join(results_dir, 'delhi_ncr_cvi_map.html')
    create_html_map(all_results, data['geojson'], html_path)
    
    # Print final summary
    print("\n" + "#"*80)
    print("# CALCULATION COMPLETE!")
    print("#"*80)
    print(f"\nResults saved in: {results_dir}")
    print(f"Visualizations saved in: {viz_dir}")
    print(f"Interactive map: {html_path}")
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    df_results = pd.DataFrame(all_results)
    print(f"Total districts analyzed: {len(df_results)}")
    print(f"Average CVI Score: {df_results['cvi_score'].mean():.4f}")
    print(f"Median CVI Score: {df_results['cvi_score'].median():.4f}")
    print(f"Range: {df_results['cvi_score'].min():.4f} - {df_results['cvi_score'].max():.4f}")
    print("\nVulnerability Distribution:")
    print(df_results['vulnerability_level'].value_counts())
    print("\nTop 5 Most Vulnerable Districts:")
    for i, row in df_results.nlargest(5, 'cvi_score').iterrows():
        print(f"  {row['district']}: {row['cvi_score']:.4f} ({row['vulnerability_level']})")
    
    print("\n" + "#"*80 + "\n")

if __name__ == "__main__":
    main()
