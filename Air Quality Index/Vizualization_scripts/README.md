# Delhi NCR Air Quality Index (AQI) Visualization

## Overview
This folder contains a comprehensive AQI visualization system for Delhi NCR region, featuring interactive maps, data analysis, and temporal trends from 2018-2025.

## 📁 File Structure

### Main Files
- **`aqi_dashboard.html`** - Main dashboard with overview and links to visualizations
- **`delhi_ncr_aqi_monthly_2018_2024.csv`** - Processed AQI data (monthly averages by district)

### Scripts
- **`process_aqi_data.py`** - Consolidates Excel files into single CSV
- **`aqi_map_visualization.py`** - Creates interactive time-series map
- **`aqi_analysis.py`** - Generates statistical analysis and summaries

### Generated Content
- **`aqi_vis_maps/`** - Contains the interactive HTML map
- **`aqi_analysis/`** - Statistical analysis outputs (CSV files)

### Data Sources
- **`AQI_Data_Final/`** - Original Excel files organized by year and month

## 🚀 Quick Start

1. **View the Dashboard:**
   ```bash
   # Open the main dashboard
   open aqi_dashboard.html
   ```

2. **Generate/Update Visualizations:**
   ```bash
   # Process raw data
   python3 process_aqi_data.py
   
   # Create map visualization
   python3 aqi_map_visualization.py
   
   # Generate analysis
   python3 aqi_analysis.py
   ```

## 🗺️ Interactive Map Features

### Time Navigation
- **Monthly slider:** Navigate through data from 2018-2025
- **Auto-play:** Automatic animation through time periods
- **Date picker:** Jump to specific months

### Visual Elements
- **Color coding:** Districts colored by AQI category (Indian standards)
- **Interactive tooltips:** Click districts for detailed information
- **Legend:** AQI categories and color scale
- **Responsive design:** Works on desktop and mobile

### AQI Categories (Indian Standards)
- 🟢 **0-50:** Good
- 🟡 **51-100:** Satisfactory  
- 🟠 **101-200:** Moderate
- 🔴 **201-300:** Poor
- 🟣 **301-400:** Very Poor
- 🔴 **401+:** Severe

## 📊 Data Summary

### Coverage
- **Time period:** January 2018 - March 2025
- **Geographic scope:** 36 districts in Delhi NCR
- **Data points:** 2,392 valid AQI readings
- **Coverage rate:** 79% of expected data points

### Key Statistics
- **Average AQI:** 179.9 (Moderate category)
- **Most polluted district:** Shahdara (225.7 average)
- **Best air quality:** Rural districts in monsoon months
- **Seasonal pattern:** Higher pollution in winter (Oct-Jan)

### Data Quality
- Missing data primarily in rural districts
- Most complete coverage for Delhi districts
- Recent years have better data availability

## 🔧 Technical Details

### Dependencies
```bash
pip install folium geopandas pandas numpy branca
```

### Data Processing Pipeline
1. **Raw Excel files** → Consolidated CSV
2. **District name normalization** → GeoJSON matching
3. **Time series preparation** → Interactive visualization
4. **Statistical analysis** → Summary reports

### Coordinate System
- **Projection:** WGS84 (EPSG:4326)
- **Boundary data:** Delhi NCR district polygons
- **Map tiles:** CartoDB Positron (clean, readable)

## 📈 Analysis Outputs

### Generated Reports
1. **`district_aqi_statistics.csv`** - District-wise AQI statistics
2. **`monthly_aqi_trends.csv`** - Time series of monthly averages
3. **`aqi_category_distribution.csv`** - Breakdown by AQI categories

### Key Insights
- **Temporal patterns:** Clear seasonal variation with winter peaks
- **Spatial patterns:** Urban core districts consistently higher AQI
- **Trend analysis:** No significant long-term improvement trend
- **Data gaps:** Rural districts with limited monitoring coverage

## 🌐 Usage Instructions

### For End Users
1. Open `aqi_dashboard.html` in any modern web browser
2. Click "Open Interactive AQI Map" to view the visualization
3. Use the time slider to explore different time periods
4. Click on districts for detailed information

### For Developers
1. Modify color schemes in `aqi_map_visualization.py`
2. Add new analysis metrics in `aqi_analysis.py`
3. Update district boundaries by replacing the GeoJSON file
4. Extend time range by adding new Excel files to `AQI_Data_Final/`

## 🚨 Data Limitations

### Known Issues
- **Missing data:** Some rural districts lack consistent monitoring
- **Data quality:** Variations in measurement standards across years
- **Geographic coverage:** Limited to NCR region only
- **Temporal gaps:** Some months missing for certain districts

### Validation Notes
- AQI calculations follow Indian CPCB standards
- District boundaries based on official administrative maps
- Time zones normalized to Indian Standard Time (IST)

## 📞 Support

For technical issues or data questions:
1. Check the generated analysis files for data quality metrics
2. Verify GeoJSON district names match CSV district names
3. Ensure all required Python packages are installed
4. Review console output for specific error messages

---

*Last updated: October 2024*
*Data source: Central Pollution Control Board (CPCB) and state monitoring networks*