"""
Climate Vulnerability Index (CVI) Calculator for Delhi NCR Districts

Based on the operational formulas:
1. Potential Impact (PI) = αE + βS
2. OUV Vulnerability = PI × (1 - AC)
3. ESC Potential Impact = δ × OUV + (1 - δ) × ESC_Dependency
4. Community Vulnerability (CV) = ESC × (1 - ESC_AC)

Components:
- Exposure (E): Temperature extremes, rainfall variability
- Sensitivity (S): Population density, water stress
- Adaptive Capacity (AC): Income, literacy, infrastructure
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

# Get absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

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
    
    print()
    
    return {
        'rainfall': df_rainfall,
        'temperature': df_temp,
        'population': df_pop,
        'income': df_income,
        'groundwater': df_groundwater
    }

# ============================================================================
# STEP 2: Calculate Exposure Index (E)
# ============================================================================

def calculate_exposure_index(data, district_name):
    """
    Calculate Exposure Index based on:
    - Temperature extremes (max temp variability, heat waves)
    - Rainfall variability (CV, extreme events)
    - Air Quality Index (AQI)
    """
    print(f"\n{'='*80}")
    print(f"CALCULATING EXPOSURE INDEX FOR: {district_name}")
    print(f"{'='*80}")
    
    df_rainfall = data['rainfall']
    df_temp = data['temperature']
    
    # Clean district name for matching
    district_clean = district_name.lower().strip()
    
    # AQI data (assumed values - ideally from actual measurements)
    # AQI Scale: 0-50 Good, 51-100 Moderate, 101-200 Poor, 201-300 Very Poor, 301+ Severe
    aqi_data = {
        'central delhi': 178,  # Poor air quality
        'alwar': 92           # Moderate air quality
    }
    aqi_value = aqi_data.get(district_clean, 100)  # Default to moderate if not found
    print(f"  Air Quality Index (AQI): {aqi_value} ({'Poor' if aqi_value > 100 else 'Moderate' if aqi_value > 50 else 'Good'})")
    
    # 1. Rainfall Variability
    rain_district = df_rainfall[df_rainfall['DISTRICT_NAME_clean'] == district_clean].copy()
    
    if len(rain_district) == 0:
        print(f"⚠ No rainfall data found for {district_name}")
        rainfall_cv = 0
        extreme_rain_days = 0
    else:
        rainfall_cv = rain_district['RAINFALL'].std() / rain_district['RAINFALL'].mean() if rain_district['RAINFALL'].mean() > 0 else 0
        # Count extreme events (>95th percentile)
        rain_95th = rain_district['RAINFALL'].quantile(0.95)
        extreme_rain_days = (rain_district['RAINFALL'] > rain_95th).sum()
        
        print(f"  Rainfall CV: {rainfall_cv:.3f}")
        print(f"  Extreme rainfall events (>95th percentile): {extreme_rain_days}")
    
    # 2. Temperature Extremes
    temp_district = df_temp[df_temp['DISTRICT_NAME'] == district_name].copy()
    
    if len(temp_district) == 0:
        # Try alternative matching
        temp_district = df_temp[df_temp['DISTRICT_NAME'].str.lower().str.contains(district_clean.split()[0])].copy()
    
    if len(temp_district) == 0:
        print(f"⚠ No temperature data found for {district_name}")
        temp_max_mean = 0
        temp_variability = 0
        heat_wave_count = 0
    else:
        temp_max_mean = temp_district['maxT'].mean() if 'maxT' in temp_district.columns else 0
        temp_variability = temp_district['maxT'].std() if 'maxT' in temp_district.columns else 0
        # Heat waves: days when maxT > 95th percentile
        if 'maxT' in temp_district.columns:
            temp_95th = temp_district['maxT'].quantile(0.95)
            heat_wave_count = (temp_district['maxT'] > temp_95th).sum()
        else:
            heat_wave_count = 0
        
        print(f"  Average Max Temperature: {temp_max_mean:.2f}°C")
        print(f"  Temperature Variability (std): {temp_variability:.2f}°C")
        print(f"  Heat wave events (>95th percentile): {heat_wave_count}")
    
    # Normalize and combine indicators
    # Using min-max normalization (will be done across all districts later)
    exposure_components = {
        'rainfall_cv': rainfall_cv,
        'extreme_rainfall_events': extreme_rain_days,
        'avg_max_temp': temp_max_mean,
        'temp_variability': temp_variability,
        'heat_wave_count': heat_wave_count,
        'aqi': aqi_value
    }
    
    # Weighted average with AQI included
    # Adjusted weights to include AQI (15% weight for AQI)
    # AQI normalized by 400 (Severe threshold)
    exposure_score = (
        0.25 * rainfall_cv +  # Rainfall variability (reduced from 0.3)
        0.15 * (extreme_rain_days / 10) +  # Extreme rainfall (reduced from 0.2)
        0.15 * (temp_max_mean / 50) +  # Temperature extremes (reduced from 0.2)
        0.15 * (temp_variability / 10) +  # Temperature variability (reduced from 0.2)
        0.10 * (heat_wave_count / 20) +  # Heat waves (same as before)
        0.20 * (aqi_value / 400)  # Air Quality Index (NEW - 20% weight)
    )
    
    print(f"\n  ➤ EXPOSURE INDEX (E): {exposure_score:.4f}")
    
    return exposure_score, exposure_components

# ============================================================================
# STEP 3: Calculate Sensitivity Index (S)
# ============================================================================

def calculate_sensitivity_index(data, district_name):
    """
    Calculate Sensitivity Index based on:
    - Population density
    - Water stress (groundwater depletion)
    """
    print(f"\n{'='*80}")
    print(f"CALCULATING SENSITIVITY INDEX FOR: {district_name}")
    print(f"{'='*80}")
    
    df_pop = data['population']
    df_gw = data['groundwater']
    
    # 1. Population Density
    district_pop = df_pop[
        (df_pop['Area_Name'].str.lower().str.contains(district_name.lower().split()[0])) &
        (df_pop['Type'] == 'Total')
    ]
    
    if len(district_pop) == 0:
        print(f"⚠ No population data found for {district_name}")
        pop_density = 0
    else:
        pop_density = district_pop['Pop_Density'].iloc[0] if 'Pop_Density' in district_pop.columns else 0
        print(f"  Population Density: {pop_density:.0f} persons/km²")
    
    # 2. Water Stress (Groundwater depletion rate)
    district_clean = district_name.lower().strip()
    gw_district = df_gw[df_gw['district_geojson'].str.lower() == district_clean].copy()
    
    if len(gw_district) == 0:
        # Try partial match
        for name_part in district_name.split():
            gw_district = df_gw[df_gw['district_geojson'].str.lower().str.contains(name_part.lower())].copy()
            if len(gw_district) > 0:
                break
    
    if len(gw_district) == 0:
        print(f"⚠ No groundwater data found for {district_name}")
        gw_depletion_rate = 0
        avg_gw_level = 0
    else:
        # Calculate groundwater depletion trend
        gw_district = gw_district.sort_values('year')
        if len(gw_district) > 1:
            # Linear regression to find depletion rate
            years = gw_district['year'].values
            levels = gw_district['currentlevel'].values
            slope, intercept, r_value, p_value, std_err = stats.linregress(years, levels)
            gw_depletion_rate = -slope if slope < 0 else 0  # Positive value means depletion
        else:
            gw_depletion_rate = 0
        
        avg_gw_level = gw_district['currentlevel'].mean()
        print(f"  Average Groundwater Level: {avg_gw_level:.2f} m")
        print(f"  Groundwater Depletion Rate: {gw_depletion_rate:.4f} m/year")
    
    # Normalize and combine indicators
    sensitivity_components = {
        'population_density': pop_density,
        'gw_depletion_rate': gw_depletion_rate,
        'avg_gw_level': avg_gw_level
    }
    
    # Weighted average
    sensitivity_score = (
        0.6 * (pop_density / 20000) +  # Normalized by 20,000 persons/km²
        0.4 * (gw_depletion_rate / 2)  # Normalized by 2 m/year depletion
    )
    
    print(f"\n  ➤ SENSITIVITY INDEX (S): {sensitivity_score:.4f}")
    
    return sensitivity_score, sensitivity_components

# ============================================================================
# STEP 4: Calculate Adaptive Capacity Index (AC)
# ============================================================================

def calculate_adaptive_capacity_index(data, district_name):
    """
    Calculate Adaptive Capacity Index based on:
    - Income levels
    - Literacy rate (from population data)
    - Infrastructure (proxied by urbanization rate)
    """
    print(f"\n{'='*80}")
    print(f"CALCULATING ADAPTIVE CAPACITY INDEX FOR: {district_name}")
    print(f"{'='*80}")
    
    df_income = data['income']
    df_pop = data['population']
    
    # 1. Income Level
    district_income = df_income[df_income['DISTRICT'].str.lower().str.contains(district_name.lower().split()[0])]
    
    if len(district_income) == 0:
        print(f"⚠ No income data found for {district_name}")
        income_level = 0
    else:
        income_level = pd.to_numeric(district_income['INCOME'].iloc[0], errors='coerce')
        if pd.isna(income_level):
            income_level = 0
        print(f"  Per Capita Income: ₹{income_level:,.0f}")
    
    # 2. Urbanization Rate (proxy for infrastructure)
    district_pop = df_pop[
        (df_pop['Area_Name'].str.lower().str.contains(district_name.lower().split()[0]))
    ]
    
    if len(district_pop) == 0:
        print(f"⚠ No population data found for {district_name}")
        urbanization_rate = 0
    else:
        total_pop_row = district_pop[district_pop['Type'] == 'Total']
        urban_pop_row = district_pop[district_pop['Type'] == 'Urban']
        
        if len(total_pop_row) > 0 and len(urban_pop_row) > 0:
            total_pop = total_pop_row['Population'].iloc[0]
            urban_pop = urban_pop_row['Population'].iloc[0]
            urbanization_rate = (urban_pop / total_pop) * 100 if total_pop > 0 else 0
        else:
            urbanization_rate = 0
        
        print(f"  Urbanization Rate: {urbanization_rate:.2f}%")
    
    # Normalize and combine indicators
    ac_components = {
        'income': income_level,
        'urbanization_rate': urbanization_rate
    }
    
    # Weighted average (higher income and urbanization = higher adaptive capacity)
    ac_score = (
        0.7 * (income_level / 1000000) +  # Normalized by ₹10 lakh
        0.3 * (urbanization_rate / 100)   # Already in percentage
    )
    
    print(f"\n  ➤ ADAPTIVE CAPACITY INDEX (AC): {ac_score:.4f}")
    
    return ac_score, ac_components

# ============================================================================
# STEP 5: Calculate CVI Components
# ============================================================================

def calculate_cvi(district_name, data, alpha=0.5, beta=0.5, delta=0.6):
    """
    Calculate complete CVI for a district
    
    Parameters:
    - alpha, beta: weights for Exposure and Sensitivity in PI calculation
    - delta: weight for OUV in ESC calculation
    """
    
    print(f"\n\n{'#'*80}")
    print(f"# CLIMATE VULNERABILITY INDEX CALCULATION")
    print(f"# District: {district_name}")
    print(f"{'#'*80}\n")
    
    # Calculate component indices
    E, exposure_comp = calculate_exposure_index(data, district_name)
    S, sensitivity_comp = calculate_sensitivity_index(data, district_name)
    AC, ac_comp = calculate_adaptive_capacity_index(data, district_name)
    
    # Step 1: Potential Impact (PI)
    PI = alpha * E + beta * S
    print(f"\n{'='*80}")
    print(f"STEP 1: POTENTIAL IMPACT (PI)")
    print(f"{'='*80}")
    print(f"  PI = α×E + β×S")
    print(f"  PI = {alpha}×{E:.4f} + {beta}×{S:.4f}")
    print(f"  ➤ PI = {PI:.4f}")
    
    # Step 2: OUV Vulnerability
    OUV = PI * (1 - AC)
    print(f"\n{'='*80}")
    print(f"STEP 2: OUV VULNERABILITY")
    print(f"{'='*80}")
    print(f"  OUV = PI × (1 - AC)")
    print(f"  OUV = {PI:.4f} × (1 - {AC:.4f})")
    print(f"  ➤ OUV = {OUV:.4f}")
    
    # Step 3: ESC Potential Impact
    # ESC_Dependency: Community dependence on OUV (assume 0.5 for now)
    ESC_Dependency = 0.5
    ESC = delta * OUV + (1 - delta) * ESC_Dependency
    print(f"\n{'='*80}")
    print(f"STEP 3: ESC POTENTIAL IMPACT")
    print(f"{'='*80}")
    print(f"  ESC = δ × OUV + (1 - δ) × ESC_Dependency")
    print(f"  ESC = {delta}×{OUV:.4f} + {1-delta}×{ESC_Dependency:.4f}")
    print(f"  ➤ ESC = {ESC:.4f}")
    
    # Step 4: Community Vulnerability (CV)
    # ESC_AC: Economic-Social-Cultural Adaptive Capacity (use same AC for now)
    ESC_AC = AC
    CV = ESC * (1 - ESC_AC)
    print(f"\n{'='*80}")
    print(f"STEP 4: COMMUNITY VULNERABILITY (CV)")
    print(f"{'='*80}")
    print(f"  CV = ESC × (1 - ESC_AC)")
    print(f"  CV = {ESC:.4f} × (1 - {ESC_AC:.4f})")
    print(f"  ➤ CV = {CV:.4f}")
    
    # Final Summary
    print(f"\n\n{'#'*80}")
    print(f"# FINAL CLIMATE VULNERABILITY INDEX RESULTS")
    print(f"# District: {district_name}")
    print(f"{'#'*80}")
    print(f"\n  Component Indices:")
    print(f"  ├─ Exposure (E):              {E:.4f}")
    print(f"  ├─ Sensitivity (S):           {S:.4f}")
    print(f"  └─ Adaptive Capacity (AC):    {AC:.4f}")
    print(f"\n  Calculated Indices:")
    print(f"  ├─ Potential Impact (PI):     {PI:.4f}")
    print(f"  ├─ OUV Vulnerability:         {OUV:.4f}")
    print(f"  ├─ ESC Impact:                {ESC:.4f}")
    print(f"  └─ Community Vulnerability:   {CV:.4f}")
    print(f"\n  ★ FINAL CVI SCORE:            {CV:.4f}")
    
    # Classify vulnerability level
    if CV < 0.2:
        vulnerability_level = "LOW"
    elif CV < 0.4:
        vulnerability_level = "MODERATE"
    elif CV < 0.6:
        vulnerability_level = "HIGH"
    else:
        vulnerability_level = "VERY HIGH"
    
    print(f"  ★ VULNERABILITY LEVEL:        {vulnerability_level}")
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
        'vulnerability_level': vulnerability_level,
        'exposure_components': exposure_comp,
        'sensitivity_components': sensitivity_comp,
        'adaptive_capacity_components': ac_comp
    }
    
    return results

# ============================================================================
# STEP 6: Visualization
# ============================================================================

def visualize_cvi_results(results_list):
    """Create comprehensive visualizations for CVI results"""
    
    output_dir = os.path.join(script_dir, 'cvi_visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    df_results = pd.DataFrame(results_list)
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (15, 10)
    
    # 1. Component Comparison
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Climate Vulnerability Index - Component Analysis', fontsize=16, fontweight='bold')
    
    # Exposure
    axes[0, 0].barh(df_results['district'], df_results['exposure'], color='#FF6B6B')
    axes[0, 0].set_title('Exposure Index (E)', fontweight='bold')
    axes[0, 0].set_xlabel('Score')
    
    # Sensitivity
    axes[0, 1].barh(df_results['district'], df_results['sensitivity'], color='#FFA06B')
    axes[0, 1].set_title('Sensitivity Index (S)', fontweight='bold')
    axes[0, 1].set_xlabel('Score')
    
    # Adaptive Capacity
    axes[1, 0].barh(df_results['district'], df_results['adaptive_capacity'], color='#6BCF7F')
    axes[1, 0].set_title('Adaptive Capacity (AC)', fontweight='bold')
    axes[1, 0].set_xlabel('Score')
    
    # Community Vulnerability
    axes[1, 1].barh(df_results['district'], df_results['community_vulnerability'], color='#9B59B6')
    axes[1, 1].set_title('Community Vulnerability (CV) - Final CVI', fontweight='bold')
    axes[1, 1].set_xlabel('Score')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cvi_components_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Saved: cvi_components_comparison.png")
    
    # 2. Radar Chart for each district
    for result in results_list:
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        categories = ['Exposure', 'Sensitivity', 'Potential\nImpact', 'OUV\nVulnerability', 
                      'ESC\nImpact', 'Adaptive\nCapacity']
        values = [
            result['exposure'],
            result['sensitivity'],
            result['potential_impact'],
            result['ouv_vulnerability'],
            result['esc_impact'],
            result['adaptive_capacity']
        ]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#3498DB')
        ax.fill(angles, values, alpha=0.25, color='#3498DB')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=10)
        ax.set_ylim(0, 1)
        ax.set_title(f"Climate Vulnerability Profile: {result['district']}\nCVI Score: {result['community_vulnerability']:.4f} ({result['vulnerability_level']})",
                     size=14, fontweight='bold', pad=20)
        ax.grid(True)
        
        plt.tight_layout()
        district_safe = result['district'].replace(' ', '_')
        plt.savefig(os.path.join(output_dir, f'cvi_radar_{district_safe}.png'), dpi=300, bbox_inches='tight')
        print(f"✓ Saved: cvi_radar_{district_safe}.png")
        plt.close()
    
    # 3. Summary Table Visualization
    fig, ax = plt.subplots(figsize=(14, len(results_list) * 0.8 + 2))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    for result in results_list:
        table_data.append([
            result['district'],
            f"{result['exposure']:.3f}",
            f"{result['sensitivity']:.3f}",
            f"{result['adaptive_capacity']:.3f}",
            f"{result['community_vulnerability']:.3f}",
            result['vulnerability_level']
        ])
    
    table = ax.table(cellText=table_data,
                     colLabels=['District', 'Exposure (E)', 'Sensitivity (S)', 
                               'Adaptive Capacity (AC)', 'CVI Score', 'Level'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.2, 0.15, 0.15, 0.2, 0.15, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Color code the header
    for i in range(6):
        table[(0, i)].set_facecolor('#3498DB')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Color code vulnerability levels
    for i, result in enumerate(results_list):
        level = result['vulnerability_level']
        if level == 'LOW':
            color = '#6BCF7F'
        elif level == 'MODERATE':
            color = '#FFD93D'
        elif level == 'HIGH':
            color = '#FFA06B'
        else:
            color = '#FF6B6B'
        table[(i+1, 5)].set_facecolor(color)
    
    plt.title('Climate Vulnerability Index - Summary Table', fontsize=14, fontweight='bold', pad=20)
    plt.savefig(os.path.join(output_dir, 'cvi_summary_table.png'), dpi=300, bbox_inches='tight')
    print(f"✓ Saved: cvi_summary_table.png")
    plt.close()
    
    print(f"\n✓ All visualizations saved in: {output_dir}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    # Load data
    data = load_data()
    
    # Calculate CVI for Central Delhi
    results_central_delhi = calculate_cvi('Central Delhi', data)
    
    # Calculate CVI for Alwar
    results_alwar = calculate_cvi('Alwar', data)
    
    # Store results
    all_results = [results_central_delhi, results_alwar]
    
    # Save results to JSON
    output_dir = os.path.join(script_dir, 'cvi_results')
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert numpy types to Python native types for JSON serialization
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
    
    all_results_serializable = convert_to_serializable(all_results)
    
    with open(os.path.join(output_dir, 'cvi_results.json'), 'w') as f:
        json.dump(all_results_serializable, f, indent=2)
    print(f"\n✓ Results saved to: {output_dir}/cvi_results.json")
    
    # Create visualizations
    visualize_cvi_results(all_results)
    
    print("\n" + "="*80)
    print("CVI CALCULATION COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    main()
