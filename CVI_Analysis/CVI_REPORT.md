# Climate Vulnerability Index (CVI) Analysis Report
## Delhi NCR Districts: Central Delhi & Alwar

---

## Executive Summary

This report presents the Climate Vulnerability Index (CVI) calculations for **Central Delhi** and **Alwar** districts based on the operational formulas for the CVI process. The analysis integrates multiple data sources including temperature, rainfall, population, income, and groundwater data.

---

## Methodology

### Operational Formulas Used

#### 1. Potential Impact (PI)
```
PI = αE + βS
```
Where:
- E = Exposure index (temperature extremes, rainfall variability)
- S = Sensitivity index (population density, water stress)
- α, β = Weights (0.5 each)

#### 2. OUV Vulnerability
```
OUV = PI × (1 - AC)
```
Where:
- AC = Adaptive Capacity index (income, urbanization)

#### 3. ESC Potential Impact
```
ESC = δ × OUV + (1 - δ) × ESC_Dependency
```
Where:
- δ = Weighting factor (0.6)
- ESC_Dependency = Community dependence (0.5)

#### 4. Community Vulnerability (CV) - Final CVI
```
CV = ESC × (1 - ESC_AC)
```
Where:
- ESC_AC = Economic-Social-Cultural Adaptive Capacity

---

## Data Sources

### Exposure Indicators
| Indicator | Data Source | Details |
|-----------|-------------|---------|
| Temperature Extremes | IMD/NASA | Monthly max/min temperatures (2013-2024) |
| Rainfall Variability | IMD | Monthly rainfall data (2013-2024) |
| Heat Waves | Calculated | Days >95th percentile temperature |
| Extreme Rainfall | Calculated | Days >95th percentile rainfall |

### Sensitivity Indicators
| Indicator | Data Source | Details |
|-----------|-------------|---------|
| Population Density | Census 2011 | Persons per km² |
| Water Stress | CGWB | Groundwater levels and depletion rates |

### Adaptive Capacity Indicators
| Indicator | Data Source | Details |
|-----------|-------------|---------|
| Per Capita Income | District Reports | Annual income data |
| Urbanization Rate | Census 2011 | Urban population percentage |
| Infrastructure | Proxied by urbanization | - |

---

## Results

### Central Delhi

#### Component Indices
- **Exposure (E)**: 0.8612
- **Sensitivity (S)**: 0.8319
- **Adaptive Capacity (AC)**: 0.3000

#### Detailed Exposure Components
- Rainfall Coefficient of Variation: 1.341
- Extreme Rainfall Events: 8 events
- Average Max Temperature: 31.77°C
- Temperature Variability: 6.59°C (std)
- Heat Wave Count: 8 events

#### Detailed Sensitivity Components
- Population Density: 27,730 persons/km²
- Average Groundwater Level: 4.20 m
- Groundwater Depletion Rate: 0.00 m/year

#### Detailed Adaptive Capacity Components
- Per Capita Income: Data not available
- Urbanization Rate: 100.00%

#### Calculated Vulnerability Indices
- **Potential Impact (PI)**: 0.8465
- **OUV Vulnerability**: 0.5926
- **ESC Impact**: 0.5555
- **Community Vulnerability (CV)**: 0.3889

#### **Final CVI Score: 0.3889**
#### **Vulnerability Level: MODERATE**

---

### Alwar

#### Component Indices
- **Exposure (E)**: 0.8960
- **Sensitivity (S)**: 0.0131
- **Adaptive Capacity (AC)**: 0.1496

#### Detailed Exposure Components
- Rainfall Coefficient of Variation: 1.465
- Extreme Rainfall Events: 8 events
- Average Max Temperature: 32.06°C
- Temperature Variability: 6.41°C (std)
- Heat Wave Count: 8 events

#### Detailed Sensitivity Components
- Population Density: 438 persons/km²
- Average Groundwater Level: 21.89 m
- Groundwater Depletion Rate: 0.00 m/year

#### Detailed Adaptive Capacity Components
- Per Capita Income: ₹137,313
- Urbanization Rate: 17.81%

#### Calculated Vulnerability Indices
- **Potential Impact (PI)**: 0.4546
- **OUV Vulnerability**: 0.3866
- **ESC Impact**: 0.4319
- **Community Vulnerability (CV)**: 0.3673

#### **Final CVI Score: 0.3673**
#### **Vulnerability Level: MODERATE**

---

## Comparative Analysis

### Key Findings

| Metric | Central Delhi | Alwar | Winner |
|--------|--------------|-------|--------|
| **Exposure (E)** | 0.8612 | 0.8960 | Central Delhi (lower is better) |
| **Sensitivity (S)** | 0.8319 | 0.0131 | Alwar (much lower) |
| **Adaptive Capacity (AC)** | 0.3000 | 0.1496 | Central Delhi (higher is better) |
| **Final CVI** | 0.3889 | 0.3673 | Alwar (lower is better) |

### Insights

#### Central Delhi
**Strengths:**
- ✅ Higher adaptive capacity due to 100% urbanization
- ✅ Better infrastructure and services
- ✅ Lower groundwater depletion

**Vulnerabilities:**
- ⚠️ Extremely high population density (27,730/km²)
- ⚠️ High sensitivity to climate impacts
- ⚠️ Shallow groundwater levels (4.20 m)
- ⚠️ No income data available for comprehensive AC assessment

**Risk Factors:**
- Dense urban population makes it highly sensitive to heat waves
- Limited space for climate adaptation measures
- High dependence on external resources

#### Alwar
**Strengths:**
- ✅ Much lower population density (438/km²)
- ✅ Deeper groundwater levels (21.89 m)
- ✅ Lower sensitivity overall
- ✅ Income data available for better AC assessment

**Vulnerabilities:**
- ⚠️ Slightly higher exposure to climate extremes
- ⚠️ Lower adaptive capacity (14.96%)
- ⚠️ Low urbanization (17.81%)
- ⚠️ Limited infrastructure

**Risk Factors:**
- Rural areas may lack early warning systems
- Limited healthcare and emergency services
- Agricultural dependence vulnerable to climate variability

---

## Vulnerability Classification

| CVI Score Range | Vulnerability Level | Color Code |
|-----------------|-------------------|------------|
| 0.00 - 0.20 | LOW | 🟢 Green |
| 0.21 - 0.40 | MODERATE | 🟡 Yellow |
| 0.41 - 0.60 | HIGH | 🟠 Orange |
| 0.61 - 1.00 | VERY HIGH | 🔴 Red |

Both districts fall in the **MODERATE** vulnerability category but with different underlying factors.

---

## Recommendations

### For Central Delhi
1. **Reduce Sensitivity:**
   - Implement green infrastructure to reduce urban heat island effect
   - Improve drainage systems for extreme rainfall events
   - Create more urban green spaces

2. **Enhance Adaptive Capacity:**
   - Develop heat action plans
   - Strengthen emergency response systems
   - Improve public awareness and preparedness

3. **Manage Water Resources:**
   - Implement rainwater harvesting
   - Reduce groundwater extraction
   - Improve water conservation measures

### For Alwar
1. **Increase Adaptive Capacity:**
   - Improve rural infrastructure
   - Enhance access to climate information
   - Develop livelihood diversification programs

2. **Address Exposure:**
   - Implement climate-resilient agricultural practices
   - Develop early warning systems
   - Create weather-based crop insurance

3. **Strengthen Community Resilience:**
   - Build local capacity for disaster management
   - Improve access to healthcare
   - Enhance education and awareness

---

## Visualization Outputs

The following visualizations have been generated:

1. **cvi_components_comparison.png** - Side-by-side comparison of all CVI components
2. **cvi_radar_Central_Delhi.png** - Radar chart showing Central Delhi's vulnerability profile
3. **cvi_radar_Alwar.png** - Radar chart showing Alwar's vulnerability profile
4. **cvi_summary_table.png** - Comprehensive summary table with color-coded vulnerability levels

All visualizations are available in: `/CVI_Analysis/cvi_visualizations/`

---

## Data Files

- **Input Data**: Multiple CSV files from rainfall, temperature, population, income, and groundwater datasets
- **Output Results**: `cvi_results.json` contains detailed numerical results
- **Script**: `calculate_cvi.py` contains the complete methodology and calculations

---

## Limitations and Future Work

### Current Limitations
1. **Income data missing for Central Delhi** - Affects AC calculation accuracy
2. **Literacy data not available** - Important AC component missing
3. **Limited temporal coverage** - Some datasets from different years
4. **No AQI data integration** - Air quality is an important exposure factor

### Future Enhancements
1. Integrate air quality index (AQI) data into exposure calculations
2. Include literacy and education indicators
3. Add healthcare infrastructure metrics
4. Incorporate land use and green cover data
5. Extend analysis to all Delhi NCR districts
6. Develop time-series CVI tracking (2013-2024)
7. Create interactive dashboard for real-time monitoring

---

## Conclusion

Both Central Delhi and Alwar face **MODERATE** climate vulnerability, but the underlying factors differ significantly:

- **Central Delhi** has high exposure and high sensitivity but benefits from better adaptive capacity through urbanization and infrastructure.

- **Alwar** faces similar exposure levels but much lower sensitivity due to lower population density, partially offset by lower adaptive capacity.

The CVI framework successfully captures these nuances and provides a quantitative basis for prioritizing climate adaptation interventions in both districts.

---

**Report Generated:** October 14, 2025
**Analysis Period:** 2013-2024
**Districts Analyzed:** Central Delhi, Alwar
**Methodology:** CVI Operational Formulas (PI, OUV, ESC, CV)
