# Delhi NCR Air Quality Index (AQI) Analysis Project

## 🌬️ Project Overview

This comprehensive project analyzes Air Quality Index (AQI) data for the Delhi National Capital Region (NCR) from 2018-2025, providing insights into pollution patterns, health impacts, and temporal trends across 36 districts. The project combines data processing, interactive visualizations, and statistical analysis to understand air quality dynamics in one of India's most polluted metropolitan regions.

## 📊 Dataset Overview

- **Geographic Coverage**: 36 districts across Delhi NCR (Delhi, Haryana, Uttar Pradesh, Rajasthan)
- **Temporal Span**: January 2018 - March 2025 (7+ years)
- **Data Points**: 2,392 valid monthly AQI measurements
- **Data Coverage**: 79% completeness across all districts and time periods
- **Key Metrics**: Average AQI, seasonal variations, district-wise patterns

## 🔧 Data Cleaning & Processing

### Raw Data Sources
- **Primary Source**: Monthly AQI data from Excel files (2018-2025)
- **Format**: Yearly folders containing monthly Excel files
- **Structure**: District-wise average AQI values per month
- **Quality**: Variable completeness with better coverage in urban areas

### Data Cleaning Pipeline

#### 1. **District Standardization**
- **Script**: `reorganize_by_districts_corrected.py`
- **Purpose**: Standardized district names and mapping across datasets
- **Process**: Corrected mapping of monitoring stations to official administrative districts
- **Output**: Consistent district nomenclature for analysis

#### 2. **Missing Data Handling**
- **Script**: `add_missing_new_districts.py`
- **Purpose**: Addressed gaps in district coverage and data availability
- **Process**: Identified and documented missing district data patterns
- **Treatment**: Flagged missing values for appropriate visualization

#### 3. **Data Consolidation**
- **Script**: `process_aqi_data.py`
- **Purpose**: Combined all yearly Excel files into single analytical dataset
- **Process**: 
  - Extracted data from 84+ Excel files
  - Standardized column names and formats
  - Created time series structure
  - Generated `delhi_ncr_aqi_monthly_2018_2024.csv`

#### 4. **Quality Validation**
- **Station Mapping**: 37 monitoring stations across Delhi NCR documented in `stations_with_districts.txt`
- **Spelling Corrections**: Fixed district name inconsistencies (`fix_charki_dadri_spelling.py`)
- **Data Integrity**: Validated AQI ranges and temporal consistency

## 🎨 Visualizations & Analysis

### Interactive Map System

#### **Gradient-Based AQI Map**
- **Technology**: Folium with TimestampedGeoJson
- **Features**: 
  - Smooth gradient color transitions (replacing discrete colors)
  - Auto-scroll temporal animation
  - 11-point color scale aligned with AQI breakpoints
  - Interactive district information popups
  - Enhanced legend with gradient visualization

#### **Key Innovations**:
- **Auto-Scroll**: Automatically cycles through time periods at 3x speed
- **Gradient Colors**: Professional visualization with smooth color transitions
- **Responsive Design**: Works across desktop and mobile devices
- **Loop Functionality**: Continuous playback for presentation purposes

### Static Analysis Visualizations

#### **Comprehensive Visualization Suite** (10 High-Resolution Images)

1. **📊 Monthly AQI Heatmap**
   - Temporal-spatial patterns across all districts and months
   - Clear identification of seasonal pollution cycles
   - Missing data visualization and coverage analysis

2. **🌱 Seasonal Analysis**
   - District-wise seasonal variations (Winter, Spring, Summer, Monsoon)
   - Climate impact on air quality patterns
   - Monsoon improvement vs winter degradation

3. **📈 Time Series Analysis**
   - Long-term trends with moving averages (6-month, 12-month)
   - Statistical confidence intervals
   - Data availability and quality metrics over time

4. **🔍 Anomaly Detection**
   - Machine learning-based outlier identification using Isolation Forest
   - 4.93% anomaly detection rate across dataset
   - Temporal and spatial anomaly distribution patterns

5. **🏛️ District Comparison**
   - Ranking of most polluted districts (Shahdara tops with 225.7 avg AQI)
   - State-wise comparisons (Delhi > Haryana ≈ Uttar Pradesh)
   - AQI category distribution analysis

6. **🔗 Statistical Correlation Analysis**
   - Mathematical relationships between variables
   - Year-over-year trend validation
   - Monthly statistics with error bars and confidence intervals

7. **📊 Trend Decomposition**
   - Signal processing using Savitzky-Golay filtering
   - Separation of trend, seasonal, and residual components
   - Advanced time series analysis for forecasting

8. **📋 Executive Summary Report**
   - Comprehensive overview with key findings
   - Health implications and policy recommendations
   - Data quality assessment and limitations

9. **🚨 Pollution Severity Analysis**
   - Composite risk scoring methodology
   - Multi-dimensional severity ranking
   - Population exposure estimates

10. **🏥 Health Impact Assessment**
    - Population health risk categorization
    - AQI threshold exceedance analysis
    - Health advisory distribution over time

## 📈 Key Findings & Analysis

### Temporal Patterns

#### **Seasonal Variations**
- **Winter Peak**: December-February shows highest pollution levels (avg 250+ AQI)
- **Monsoon Relief**: July-September demonstrates significant improvement (avg 100-150 AQI)
- **Transition Periods**: Spring and post-monsoon show moderate pollution levels
- **Annual Cycle**: Clear and consistent seasonal pattern across all years

#### **Long-term Trends**
- **No Significant Improvement**: No substantial long-term reduction in average AQI
- **Variability**: High year-to-year variability with episodic severe pollution events
- **Data Quality**: Improving monitoring coverage and data availability in recent years

### Spatial Patterns

#### **Geographic Hotspots**
- **Most Polluted**: Shahdara district (225.7 average AQI - Very Poor category)
- **Urban Core**: Delhi districts consistently show higher pollution than suburban areas
- **State Comparison**: Delhi > Haryana ≈ Uttar Pradesh in terms of average pollution levels
- **Rural-Urban Divide**: Limited data for rural areas but generally better air quality

#### **District Rankings** (Top 5 Most Polluted)
1. **Shahdara**: 225.7 AQI (Very Poor)
2. **North West Delhi**: 219.7 AQI (Poor)
3. **West Delhi**: 214.3 AQI (Poor)
4. **Ghaziabad**: 211.6 AQI (Poor)
5. **Gautam Buddha Nagar**: 208.5 AQI (Poor)

### Health & Environmental Implications

#### **Population Exposure**
- **Good Air Quality**: Only 0.9% of all measurements
- **Unhealthy Levels**: 63.4% of readings exceed moderate category (>100 AQI)
- **Severe Episodes**: 0.1% of readings reach severe category (>400 AQI)
- **Vulnerable Populations**: Millions exposed to poor air quality regularly

#### **Seasonal Health Risks**
- **Winter Crisis**: Highest health risks during December-February period
- **Respiratory Impact**: Prolonged exposure to moderate-to-poor air quality
- **Vulnerable Groups**: Children, elderly, and those with respiratory conditions at highest risk

### Statistical Insights

#### **Anomaly Detection Results**
- **Anomaly Rate**: 4.93% of readings identified as statistical outliers
- **Geographic Distribution**: Shahdara district shows highest anomaly frequency
- **Temporal Clustering**: Anomalies often coincide with weather events or festivals
- **Severity**: Most anomalies represent extremely high pollution episodes

#### **Data Quality Assessment**
- **Coverage**: 79% data completeness across expected measurements
- **Missing Data**: Primarily in rural districts and early study years
- **Reliability**: Strong consistency in urban monitoring stations
- **Validation**: Cross-referenced with official CPCB data sources

## 🎯 Technical Implementation

### Technologies Used
- **Data Processing**: Python, Pandas, NumPy
- **Visualization**: Folium, Matplotlib, Seaborn, Plotly
- **Geospatial**: GeoPandas, GeoJSON processing
- **Machine Learning**: Scikit-learn (Isolation Forest for anomaly detection)
- **Statistical Analysis**: SciPy, advanced time series analysis
- **Web Technologies**: HTML5, CSS3, JavaScript for interactive elements

### Key Innovation: Gradient Color System
- **Smooth Transitions**: 11-point gradient scale instead of discrete color blocks
- **AQI Alignment**: Colors positioned at official AQI category breakpoints
- **Professional Appearance**: Research-grade visualization standards
- **Enhanced Discrimination**: Better visual separation of similar AQI values

## 🚀 Usage & Applications

### For Researchers
- **Academic Studies**: Publication-ready visualizations and statistical analysis
- **Trend Analysis**: Long-term air quality pattern identification
- **Forecasting**: Historical data foundation for predictive modeling
- **Comparative Studies**: Multi-district and multi-temporal analysis framework

### For Policymakers
- **Evidence-Based Policy**: Data-driven insights for air quality interventions
- **Resource Allocation**: Prioritization of pollution control measures by district
- **Seasonal Planning**: Timing of restrictions and health advisories
- **Progress Monitoring**: Baseline establishment for improvement tracking

### For Public Health
- **Risk Assessment**: Population exposure analysis and health impact evaluation
- **Advisory Systems**: Data foundation for air quality alerts and recommendations
- **Vulnerable Population Protection**: Targeted health protection strategies
- **Awareness Campaigns**: Visual tools for public education and engagement

## 📁 Repository Structure

```
Air Quality Index/
├── AQI_Data_Final/              # Raw Excel data files (2018-2025)
├── Data cleaning scripts/       # Data processing and cleaning tools
├── Vizualizations/             # Interactive maps and static visualizations
│   ├── aqi_vis_maps/           # Interactive HTML maps
│   ├── aqi_visualizations/     # Static PNG analysis charts
│   └── Documentation/          # Technical documentation
└── README.md                   # This comprehensive overview
```

## 🔮 Future Scope

### Immediate Extensions
- **Real-time Integration**: Connect with live monitoring APIs
- **Forecasting Models**: Develop predictive air quality models
- **Mobile Application**: Create smartphone-friendly visualization tools
- **Policy Impact Analysis**: Assess effectiveness of pollution control measures

### Advanced Research Directions
- **Causal Analysis**: Identify pollution sources and contributing factors
- **Economic Valuation**: Quantify economic costs of air pollution
- **Health Correlation**: Link air quality data with health outcomes
- **Climate Integration**: Incorporate weather and climate data for enhanced analysis

---

**Project Period**: 2018-2025 | **Data Coverage**: 36 Districts | **Analysis Type**: Comprehensive Multi-dimensional | **Output Format**: Interactive + Static Visualizations

*This project provides a foundation for understanding air quality dynamics in Delhi NCR and supports evidence-based environmental policy and public health decision-making.*