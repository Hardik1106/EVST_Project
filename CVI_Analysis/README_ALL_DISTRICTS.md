# Climate Vulnerability Index (CVI) - All Delhi NCR Districts

## Overview

This comprehensive analysis calculates the Climate Vulnerability Index (CVI) for **all 35 districts** in the Delhi NCR region, providing a complete vulnerability assessment across the entire region.

## Script: `calculate_cvi_all_districts.py`

### What It Does

1. **Calculates CVI for All Districts**: Computes vulnerability scores for all 35 Delhi NCR districts
2. **Component Analysis**: Evaluates Exposure (E), Sensitivity (S), and Adaptive Capacity (AC) for each district
3. **Generates Visualizations**: Creates comprehensive charts and graphs for analysis
4. **Interactive HTML Map**: Produces a choropleth map showing vulnerability across the region
5. **Exports Results**: Saves data in CSV and JSON formats for further analysis

### Methodology

The CVI is calculated using the following operational formulas:

```
1. Potential Impact (PI) = α×E + β×S
2. OUV Vulnerability = PI × (1 - AC)
3. ESC Potential Impact = δ × OUV + (1 - δ) × ESC_Dependency
4. Community Vulnerability (CV) = ESC × (1 - ESC_AC)
```

#### Component Indices

**Exposure Index (E)** - 6 indicators:
- Rainfall variability (CV)
- Extreme rainfall events (>95th percentile)
- Average maximum temperature
- Temperature variability
- Heat wave count (>95th percentile)
- Air Quality Index (AQI)

**Sensitivity Index (S)** - 2 indicators:
- Population density (persons/km²)
- Groundwater depletion rate (m/year)

**Adaptive Capacity Index (AC)** - 2 indicators:
- Per capita income (₹)
- Urbanization rate (%)

### Usage

```bash
cd /home/devkanani/VSCODE/EVST/EVST_Project/CVI_Analysis
python3 calculate_cvi_all_districts.py
```

### Requirements

The script requires the following Python packages:
```
pandas>=1.3
numpy>=1.21
matplotlib>=3.4
seaborn>=0.11
scipy>=1.7
folium>=0.12
```

Install missing packages:
```bash
pip install folium scipy
```

## Results Summary

### Overall Statistics
- **Total Districts Analyzed**: 35
- **Average CVI Score**: 0.3291
- **Median CVI Score**: 0.3533
- **CVI Range**: 0.0252 - 0.5158

### Vulnerability Distribution
- **LOW**: 4 districts (11.4%)
- **MODERATE**: 27 districts (77.1%)
- **HIGH**: 4 districts (11.4%)
- **VERY HIGH**: 0 districts (0%)

### Top 5 Most Vulnerable Districts
1. **Shahdara**: 0.5158 (HIGH)
2. **Charki Dadri**: 0.4870 (HIGH)
3. **Nuh**: 0.4442 (HIGH)
4. **Gurugram**: 0.4306 (HIGH)
5. **North West Delhi**: 0.3799 (MODERATE)

### Top 5 Least Vulnerable Districts
1. **Gautam Buddha Nagar**: 0.0252 (LOW)
2. **Faridabad**: 0.1024 (LOW)
3. **West Delhi**: 0.1340 (LOW)
4. **Panipat**: 0.1560 (LOW)
5. **Ghaziabad**: 0.2416 (MODERATE)

## Output Files

### 1. Results Directory (`cvi_results/`)

**CSV File**: `cvi_results_all_districts.csv`
- Complete CVI scores and component indices for all districts
- Columns: district, exposure, sensitivity, adaptive_capacity, potential_impact, ouv_vulnerability, esc_impact, cvi_score, vulnerability_level

**JSON File**: `cvi_results_all_districts.json`
- Detailed results including all component breakdowns
- Machine-readable format for further processing

**Summary Statistics**: `cvi_summary_statistics.json`
- Overall statistics and distributions
- Most/least vulnerable districts
- Vulnerability level counts

**Interactive Map**: `delhi_ncr_cvi_map.html`
- **Open this file in a web browser to see the interactive map**
- Choropleth visualization with CVI scores
- Hover over districts to see detailed information
- Click for pop-up with vulnerability details

### 2. Visualizations Directory (`cvi_visualizations/`)

1. **`cvi_ranking_all_districts.png`**
   - Horizontal bar chart ranking all 35 districts by CVI score
   - Color-coded by vulnerability level

2. **`cvi_components_heatmap.png`**
   - Heatmap showing Exposure, Sensitivity, Adaptive Capacity, and CVI scores
   - Easy comparison across all districts

3. **`top_10_vulnerable_districts.png`**
   - Bar chart highlighting the 10 most vulnerable districts

4. **`vulnerability_level_distribution.png`**
   - Pie chart showing the distribution of vulnerability levels

5. **`exposure_vs_sensitivity_scatter.png`**
   - Scatter plot showing relationship between Exposure and Sensitivity
   - Points colored by CVI score
   - Top 5 vulnerable districts annotated

6. **`cvi_summary_table_top20.png`**
   - Summary table of top 20 most vulnerable districts
   - Shows all component scores and vulnerability levels

## How to View Results

### Interactive HTML Map
```bash
# Open in your default web browser
xdg-open cvi_results/delhi_ncr_cvi_map.html

# Or open in Firefox/Chrome directly
firefox cvi_results/delhi_ncr_cvi_map.html
google-chrome cvi_results/delhi_ncr_cvi_map.html
```

### CSV Data
```python
import pandas as pd

# Load results
df = pd.read_csv('cvi_results/cvi_results_all_districts.csv')

# View top 10 vulnerable districts
print(df.nlargest(10, 'cvi_score'))

# Filter by vulnerability level
high_vuln = df[df['vulnerability_level'] == 'HIGH']
print(high_vuln)
```

### JSON Data
```python
import json

# Load detailed results
with open('cvi_results/cvi_results_all_districts.json', 'r') as f:
    results = json.load(f)

# Access specific district
for district in results:
    if district['district'] == 'Shahdara':
        print(district)
        break
```

## Key Findings

### High Vulnerability Districts (CVI > 0.4)

1. **Shahdara (0.5158)**
   - Highest vulnerability in Delhi NCR
   - High exposure to climate hazards
   - Dense population with limited adaptive capacity

2. **Charki Dadri (0.4870)**
   - Rural district with limited infrastructure
   - Water stress concerns
   - Lower adaptive capacity

3. **Nuh (0.4442)**
   - High sensitivity to climate impacts
   - Limited economic resources
   - Rural area with development challenges

4. **Gurugram (0.4306)**
   - Despite being economically developed
   - High exposure to air pollution (AQI)
   - Rapid urbanization stress

### Low Vulnerability Districts (CVI < 0.2)

1. **Gautam Buddha Nagar (0.0252)**
   - Lowest vulnerability in the region
   - Good infrastructure and adaptive capacity
   - Balanced development

2. **Faridabad (0.1024)**
   - Strong adaptive capacity
   - Industrial development
   - Better infrastructure

3. **West Delhi (0.1340)**
   - Lower exposure compared to other Delhi districts
   - Good connectivity and resources

4. **Panipat (0.1560)**
   - Moderate climate exposure
   - Decent adaptive capacity

## District-Level Analysis

All 35 districts analyzed:
```
Alwar, Baghpat, Bharatpur, Bhiwani, Bulandshahr,
Central Delhi, Charki Dadri, East Delhi, Faridabad,
Gautam Buddha Nagar, Ghaziabad, Gurugram, Hapur,
Jhajjar, Jind, Karnal, Mahendragarh, Meerut,
Muzaffarnagar, New Delhi, North Delhi, North East Delhi,
North West Delhi, Nuh, Palwal, Panipat, Rewari,
Rohtak, Shahdara, Shamli, Sonipat, South Delhi,
South East Delhi, South West Delhi, West Delhi
```

## Data Sources

The CVI calculation uses the following datasets:
1. **Rainfall Data**: `delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv`
2. **Temperature Data**: `delhi_ncr_temp_monthly_avg_2013_2024.csv`
3. **Population Data**: `population_data_and_vis/Delhi_NCR_Population_Data_Clean.csv`
4. **Income Data**: `Income/district_wise.csv`
5. **Groundwater Data**: `ground_water_vis/ncr_groundwater_yearly.csv`
6. **GeoJSON**: `GeoJsons/Delhi_NCR_Districts_final.geojson`

## Customization

### Adjust Weights

Edit the following parameters in the `calculate_cvi()` function:
```python
alpha=0.5,  # Weight for Exposure in PI calculation
beta=0.5,   # Weight for Sensitivity in PI calculation
delta=0.6   # Weight for OUV in ESC calculation
```

### Modify AQI Values

Update the `DEFAULT_AQI` dictionary with actual measured values:
```python
DEFAULT_AQI = {
    'Central Delhi': 178,
    'New Delhi': 175,
    # ... add more districts
}
```

### Change Vulnerability Thresholds

Modify classification thresholds in the `calculate_cvi()` function:
```python
if CV < 0.2:
    vulnerability_level = "LOW"
elif CV < 0.4:
    vulnerability_level = "MODERATE"
elif CV < 0.6:
    vulnerability_level = "HIGH"
else:
    vulnerability_level = "VERY HIGH"
```

## Future Enhancements

1. **Real-time AQI Integration**: Connect to live AQI monitoring APIs
2. **Time-series Analysis**: Track CVI changes over multiple years
3. **Additional Indicators**: Include literacy rate, healthcare access, etc.
4. **Sub-district Analysis**: Calculate CVI at ward/block level
5. **Predictive Modeling**: Forecast future vulnerability trends

## Comparison with Previous Analysis

### Original Script (`calculate_cvi.py`)
- Calculated CVI for 2 districts (Central Delhi & Alwar)
- Detailed verbose output for each district
- Educational focus with step-by-step explanations

### New Script (`calculate_cvi_all_districts.py`)
- Calculates CVI for all 35 districts
- Batch processing with progress indicators
- Comprehensive visualizations and comparisons
- Interactive HTML map generation
- Export to multiple formats

## Troubleshooting

### Missing Dependencies
```bash
pip install folium scipy matplotlib seaborn pandas numpy
```

### Data File Not Found
Ensure all data files are in the correct locations relative to the script:
```
EVST_Project/
├── CVI_Analysis/
│   └── calculate_cvi_all_districts.py
├── delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv
├── delhi_ncr_temp_monthly_avg_2013_2024.csv
├── population_data_and_vis/
│   └── Delhi_NCR_Population_Data_Clean.csv
├── Income/
│   └── district_wise.csv
├── ground_water_vis/
│   └── ncr_groundwater_yearly.csv
└── GeoJsons/
    └── Delhi_NCR_Districts_final.geojson
```

### GeoJSON Not Loading
Check that the GeoJSON file has the correct structure with `dtname` property matching district names exactly.

## Contact & Support

For questions or issues related to this CVI analysis, please refer to the main project documentation or contact the project team.

---

**Generated by**: CVI All Districts Calculator
**Date**: October 2025
**Version**: 1.0
