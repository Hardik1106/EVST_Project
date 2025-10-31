# Climate Vulnerability Index (CVI) - Technical Documentation

## Complete Methodology, Assumptions, and Calculations

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [Component Indices Calculation](#component-indices-calculation)
4. [CVI Formula Implementation](#cvi-formula-implementation)
5. [Assumptions and Limitations](#assumptions-and-limitations)
6. [Normalization Methods](#normalization-methods)
7. [Results Interpretation](#results-interpretation)
8. [How to Run](#how-to-run)

---

## 🎯 Overview

This implementation calculates the **Climate Vulnerability Index (CVI)** for Delhi NCR districts using the operational CVI formulas. The analysis integrates multiple datasets spanning 2011-2024 to assess climate vulnerability across three dimensions:

- **Exposure (E)**: Degree of climate stress (temperature, rainfall extremes)
- **Sensitivity (S)**: Degree to which the system is affected (population, water stress)
- **Adaptive Capacity (AC)**: Ability to cope and adapt (income, infrastructure)

### Operational Formulas Applied

```
1. Potential Impact (PI) = α×E + β×S
2. OUV Vulnerability = PI × (1 - AC)
3. ESC Impact = δ×OUV + (1-δ)×ESC_Dependency
4. Community Vulnerability (CV) = ESC × (1 - ESC_AC)
```

**Final Output:** CV (Community Vulnerability) = **CVI Score**

---

## 📊 Data Sources

### 1. Rainfall Data
- **File**: `delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv`
- **Source**: IMD (India Meteorological Department)
- **Period**: 2013-2024 (144 months per district)
- **Records**: 5,184 monthly observations
- **Fields Used**: `RAINFALL`, `DISTRICT_NAME_clean`, `YEAR`, `MONTH`

### 2. Temperature Data
- **File**: `delhi_ncr_temp_monthly_avg_2013_2024.csv`
- **Source**: IMD/NASA
- **Period**: 2013-2024 (144 months per district)
- **Records**: 5,184 monthly observations
- **Fields Used**: `maxT`, `minT`, `avgT`, `DISTRICT_NAME`

### 3. Population Data
- **File**: `Delhi_NCR_Population_Data_Clean.csv`
- **Source**: Census of India 2011
- **Records**: 162 district-level entries
- **Fields Used**: `Population`, `Pop_Density`, `Area_sq_km`, `Type` (Rural/Urban/Total)

### 4. Income Data
- **File**: `district_wise.csv`
- **Source**: District statistical reports, NSSO
- **Records**: 23 districts
- **Fields Used**: `DISTRICT`, `INCOME`, `YEAR`
- **Note**: Per capita income in Indian Rupees (₹)

### 5. Groundwater Data
- **File**: `ncr_groundwater_yearly.csv`
- **Source**: Central Ground Water Board (CGWB)
- **Period**: 2013-2021
- **Records**: 262 yearly observations
- **Fields Used**: `district_geojson`, `currentlevel`, `level_diff`, `year`

---

## 🔬 Component Indices Calculation

### 1. EXPOSURE INDEX (E)

**Definition**: Measures the degree of climate stress a district faces.

#### Indicators and Weights

| Indicator | Weight | Normalization | Rationale |
|-----------|--------|---------------|-----------|
| Rainfall Coefficient of Variation | 25% | Direct value | Higher CV = more variability = higher exposure |
| Extreme Rainfall Events | 15% | Divide by 10 | Count of days > 95th percentile |
| Average Maximum Temperature | 15% | Divide by 50°C | Higher temps = more heat stress |
| Temperature Variability (Std Dev) | 15% | Divide by 10°C | Higher variability = less predictability |
| Heat Wave Count | 10% | Divide by 20 | Days when maxT > 95th percentile |
| **Air Quality Index (AQI)** | **20%** | **Divide by 400** | **Poor air quality amplifies climate vulnerability** |

#### Calculation Steps

```python
# 1. Calculate Rainfall Variability
rainfall_cv = std(rainfall) / mean(rainfall)

# 2. Identify Extreme Rainfall Events
rain_95th = percentile(rainfall, 95)
extreme_rain_days = count(rainfall > rain_95th)

# 3. Calculate Temperature Metrics
avg_max_temp = mean(maxT)
temp_variability = std(maxT)

# 4. Identify Heat Waves
temp_95th = percentile(maxT, 95)
heat_wave_count = count(maxT > temp_95th)

# 5. Get Air Quality Index (AQI)
# AQI values for Delhi NCR districts
# Central Delhi: 178 (Poor), Alwar: 92 (Moderate)
aqi_value = district_aqi_data[district_name]

# 6. Combine with Weights
E = (0.25 × rainfall_cv) + 
    (0.15 × extreme_rain_days/10) + 
    (0.15 × avg_max_temp/50) + 
    (0.15 × temp_variability/10) + 
    (0.10 × heat_wave_count/20) +
    (0.20 × aqi_value/400)
```

#### Results

**Central Delhi:**
- Rainfall CV: 1.341
- Extreme rainfall: 8 events
- Avg max temp: 31.77°C
- Temp variability: 6.59°C
- Heat waves: 8 events
- **AQI: 178 (Poor air quality)**
- **E = 0.7784** (HIGH)

**Alwar:**
- Rainfall CV: 1.465
- Extreme rainfall: 8 events
- Avg max temp: 32.06°C
- Temp variability: 6.41°C
- Heat waves: 8 events
- **AQI: 92 (Moderate air quality)**
- **E = 0.7646** (HIGH)

---

### 2. SENSITIVITY INDEX (S)

**Definition**: Measures how vulnerable the system is to climate impacts.

#### Indicators and Weights

| Indicator | Weight | Normalization | Rationale |
|-----------|--------|---------------|-----------|
| Population Density | 60% | Divide by 20,000/km² | More people = more sensitivity |
| Groundwater Depletion Rate | 40% | Divide by 2 m/year | Faster depletion = higher water stress |

#### Calculation Steps

```python
# 1. Extract Population Density
pop_density = population_data[Type='Total']['Pop_Density']

# 2. Calculate Groundwater Depletion Rate
# Linear regression on yearly groundwater levels
years = [2013, 2014, ..., 2021]
levels = [level_2013, level_2014, ..., level_2021]
slope = linear_regression(years, levels).slope

# Only count negative slopes (depletion)
gw_depletion_rate = -slope if slope < 0 else 0

# 3. Combine with Weights
S = (0.6 × pop_density/20000) + 
    (0.4 × gw_depletion_rate/2)
```

#### Normalization Rationale

- **20,000/km²**: Typical high urban density threshold
  - Delhi average: ~11,000/km²
  - Mumbai: ~20,000/km²
  - Rural areas: <500/km²

- **2 m/year**: Severe groundwater depletion threshold
  - Normal fluctuation: ±0.5 m/year
  - Critical depletion: >1 m/year
  - Severe crisis: >2 m/year

#### Results

**Central Delhi:**
- Population density: 27,730/km²
- GW depletion: 0 m/year (stable)
- **S = 0.8319** (HIGH - driven by population)

**Alwar:**
- Population density: 438/km²
- GW depletion: 0 m/year (stable)
- **S = 0.0131** (LOW)

---

### 3. ADAPTIVE CAPACITY INDEX (AC)

**Definition**: Measures the ability to cope with and adapt to climate change.

#### Indicators and Weights

| Indicator | Weight | Normalization | Rationale |
|-----------|--------|---------------|-----------|
| Per Capita Income | 70% | Divide by ₹10,00,000 | Higher income = better coping ability |
| Urbanization Rate | 30% | Divide by 100% | Urban = better infrastructure/services |

#### Calculation Steps

```python
# 1. Extract Per Capita Income
income = income_data['INCOME']  # in Rupees

# 2. Calculate Urbanization Rate
total_pop = population_data[Type='Total']['Population']
urban_pop = population_data[Type='Urban']['Population']
urbanization_rate = (urban_pop / total_pop) × 100

# 3. Combine with Weights
AC = (0.7 × income/1000000) + 
     (0.3 × urbanization_rate/100)
```

#### Normalization Rationale

- **₹10,00,000 (10 lakhs)**: High income threshold
  - National average: ~₹1.5 lakhs
  - Middle class: ₹2-5 lakhs
  - High income: >₹10 lakhs
  
- **100%**: Maximum urbanization
  - 0% = Completely rural
  - 50% = Semi-urban
  - 100% = Fully urban

#### Results

**Central Delhi:**
- Income: ₹0 (data not available)
- Urbanization: 100%
- **AC = 0.3000** (MODERATE - only urbanization counted)

**Alwar:**
- Income: ₹137,313
- Urbanization: 17.81%
- **AC = 0.1496** (LOW)

**Note**: Higher AC is GOOD - it reduces vulnerability!

---

## 🧮 CVI Formula Implementation

### Formula 1: Potential Impact (PI)

**Purpose**: Combine exposure and sensitivity into overall potential impact.

```
PI = α×E + β×S
```

**Parameters:**
- α (alpha) = 0.5 (Exposure weight)
- β (beta) = 0.5 (Sensitivity weight)

**Assumption**: Exposure and sensitivity are equally important.

**Calculation:**

**Central Delhi:**
```
PI = 0.5 × 0.8612 + 0.5 × 0.8319
PI = 0.4306 + 0.4160
PI = 0.8465
```

**Alwar:**
```
PI = 0.5 × 0.8960 + 0.5 × 0.0131
PI = 0.4480 + 0.0066
PI = 0.4546
```

**Interpretation**: Alwar's PI is much lower despite similar exposure because its sensitivity is very low (low population density).

---

### Formula 2: OUV Vulnerability

**Purpose**: Adjust potential impact by adaptive capacity.

```
OUV = PI × (1 - AC)
```

**Logic:**
- (1 - AC) represents the "vulnerability factor"
- High AC → Low (1-AC) → Lower OUV
- Low AC → High (1-AC) → Higher OUV

**Calculation:**

**Central Delhi:**
```
OUV = 0.8465 × (1 - 0.3000)
OUV = 0.8465 × 0.7000
OUV = 0.5926
```

**Alwar:**
```
OUV = 0.4546 × (1 - 0.1496)
OUV = 0.4546 × 0.8504
OUV = 0.3866
```

**Interpretation**: Central Delhi's higher AC (30% vs 15%) helps reduce its OUV more effectively than Alwar despite higher PI.

---

### Formula 3: ESC Potential Impact

**Purpose**: Incorporate community dependence on ecosystem services.

```
ESC = δ×OUV + (1-δ)×ESC_Dependency
```

**Parameters:**
- δ (delta) = 0.6 (OUV weight)
- ESC_Dependency = 0.5 (baseline dependency)

**Assumption**: ESC_Dependency set at 0.5 (moderate) as actual ecosystem dependency data not available. Could be calculated from:
- Agricultural land use
- Forest cover
- Water body access
- Green space percentage

**Calculation:**

**Central Delhi:**
```
ESC = 0.6 × 0.5926 + 0.4 × 0.5000
ESC = 0.3556 + 0.2000
ESC = 0.5555
```

**Alwar:**
```
ESC = 0.6 × 0.3866 + 0.4 × 0.5000
ESC = 0.2320 + 0.2000
ESC = 0.4319
```

**Interpretation**: ESC represents economic-social-cultural impacts from climate change, combining direct vulnerability with environmental dependence.

---

### Formula 4: Community Vulnerability (CV) - FINAL CVI

**Purpose**: Calculate final vulnerability considering socio-economic adaptive capacity.

```
CV = ESC × (1 - ESC_AC)
```

**Parameters:**
- ESC_AC = Economic-Social-Cultural Adaptive Capacity
- Using same AC value (conservative approach)

**Assumption**: ESC_AC = AC (socio-economic adaptive capacity applies to ecosystem-dependent impacts too). Ideally should include:
- Social capital
- Community networks
- Traditional knowledge
- Institutional support

**Calculation:**

**Central Delhi:**
```
CV = 0.5555 × (1 - 0.3000)
CV = 0.5555 × 0.7000
CV = 0.3889 → MODERATE 🟡
```

**Alwar:**
```
CV = 0.4319 × (1 - 0.1496)
CV = 0.4319 × 0.8504
CV = 0.3673 → MODERATE 🟡
```

**Final CVI Classification:**
- 0.00 - 0.20 = LOW 🟢
- 0.21 - 0.40 = MODERATE 🟡
- 0.41 - 0.60 = HIGH 🟠
- 0.61 - 1.00 = VERY HIGH 🔴

---

## 📌 Assumptions and Limitations

### Key Assumptions

#### 1. **Equal Weights for E and S in PI**
- **Assumption**: α = β = 0.5
- **Rationale**: Both exposure and sensitivity contribute equally to potential impact
- **Alternative**: Could calibrate based on expert judgment or empirical data

#### 2. **Normalization Factors**
| Factor | Value | Justification |
|--------|-------|---------------|
| Rainfall CV | Direct | Already normalized metric |
| Extreme events | 10 events | Reasonable maximum for monthly data over 12 years |
| Max temperature | 50°C | Extreme heat threshold |
| Temp variability | 10°C | High variability threshold |
| Heat waves | 20 events | Severe heat stress threshold |
| **AQI** | **400** | **Severe air quality threshold (India AQI scale)** |
| Population density | 20,000/km² | High urban density |
| GW depletion | 2 m/year | Severe depletion rate |
| Income | ₹10,00,000 | High income threshold |

#### 3. **ESC Dependency = 0.5**
- **Assumption**: Moderate dependence on ecosystem services
- **Rationale**: No actual data available; 0.5 is neutral baseline
- **Improvement**: Calculate from land use, agriculture, forest cover data

#### 4. **ESC_AC = AC**
- **Assumption**: Economic adaptive capacity applies to ecosystem impacts
- **Rationale**: Conservative approach; same coping mechanisms
- **Improvement**: Add social capital, community resilience metrics

#### 5. **Missing Data = 0**
- **Assumption**: Missing data treated as zero
- **Impact**: Conservative approach; underestimates if actual value is high
- **Example**: Central Delhi income = 0 → AC underestimated

#### 6. **Temporal Consistency**
- **Assumption**: 2011 census data still representative for 2024
- **Reality**: Population, urbanization changed significantly
- **Impact**: May overestimate or underestimate current sensitivity

#### 7. **Linear Relationships**
- **Assumption**: Linear relationships between indicators and vulnerability
- **Reality**: May have non-linear thresholds
- **Example**: Population density impact may be exponential, not linear

#### 8. **District Name Matching**
- **Assumption**: Fuzzy matching captures all variations
- **Method**: Lowercase, partial matching, manual mapping
- **Limitation**: Some districts may be missed or mismatched

#### 9. **AQI Values**
- **Assumption**: Using assumed/representative AQI values for districts
- **Central Delhi**: 178 (Poor) - typical urban Delhi air quality
- **Alwar**: 92 (Moderate) - cleaner rural/semi-urban air quality
- **Limitation**: Actual AQI varies seasonally and needs real-time monitoring data
- **Improvement**: Integrate with CPCB real-time AQI data or calculate average from historical monitoring

### Limitations

#### 1. **Data Gaps**
- **Income**: Missing for Central Delhi, several other districts
- **Literacy**: Not included (data not in available datasets)
- **Healthcare**: No data available
- **Infrastructure**: Proxied by urbanization only
- **AQI**: Using assumed values; need real-time/historical AQI monitoring data

#### 2. **Temporal Misalignment**
- **Population**: 2011 Census
- **Income**: Mixed years (2011-12 to 2024-25)
- **Climate**: 2013-2024
- **Groundwater**: 2013-2021

#### 3. **Spatial Resolution**
- **Analysis Level**: District level
- **Limitation**: Within-district variation not captured
- **Impact**: Urban-rural differences within district hidden

#### 4. **Single Threshold for Classification**
- **Current**: Fixed thresholds (0.2, 0.4, 0.6, 0.8)
- **Limitation**: May not capture regional context
- **Improvement**: Context-specific thresholds

#### 5. **No Future Projections**
- **Current**: Historical data only
- **Missing**: Climate change projections, population growth
- **Improvement**: Integrate climate models for future scenarios

#### 6. **Limited Exposure and Sensitivity Indicators**
- **Current Exposure**: Rainfall, temperature, heat waves, AQI
- **Current Sensitivity**: Population density, groundwater
- **Missing**: Age demographics, health status, building quality, land use, flood risk, drought frequency

#### 7. **No Validation**
- **Current**: No ground-truth validation
- **Missing**: Field surveys, disaster impact data
- **Improvement**: Validate against actual climate disaster impacts

---

## 📏 Normalization Methods

### Min-Max Normalization

For most indicators, we use **ratio normalization**:

```python
normalized_value = actual_value / reference_maximum
```

**Example:**
```python
pop_density_normalized = 27730 / 20000 = 1.387
# Capped at 1.0 in final calculation: min(1.387, 1.0) = 1.0
```

### Percentile-Based Extremes

For identifying extreme events:

```python
threshold_95th = percentile(data, 95)
extreme_count = count(data > threshold_95th)
```

**Rationale**: 95th percentile captures truly extreme events (top 5%)

### Coefficient of Variation

For rainfall variability:

```python
CV = standard_deviation / mean
```

**Rationale**: CV is already normalized, independent of units

---

## 📊 Results Interpretation

### Component-Level Analysis

| District | E (Exposure) | S (Sensitivity) | AC (Adapt. Capacity) | Interpretation |
|----------|--------------|-----------------|---------------------|----------------|
| Central Delhi | 0.78 (HIGH) | 0.83 (HIGH) | 0.30 (MOD) | High climate + air pollution threat, high sensitivity, moderate coping |
| Alwar | 0.76 (HIGH) | 0.01 (LOW) | 0.15 (LOW) | High climate threat but cleaner air, low sensitivity, low coping |

### CVI-Level Analysis

| District | PI | OUV | ESC | CV (CVI) | Level | Key Driver |
|----------|----|----|-----|----------|-------|------------|
| Central Delhi | 0.81 | 0.56 | 0.54 | **0.38** | MOD 🟡 | High pop density + poor air quality |
| Alwar | 0.39 | 0.33 | 0.40 | **0.34** | MOD 🟡 | Low adaptive capacity, cleaner air advantage |

### Why Both Are "MODERATE" But Different

**Central Delhi**: 
- ⚠️ High climate exposure + Poor air quality (AQI 178) + High sensitivity = High potential impact
- ✅ Moderate adaptive capacity partially mitigates
- 🔑 **Key Issues**: Extreme population density (27,730/km²) + Poor air quality
- 🌡️ **Combined Stress**: Heat waves + air pollution create amplified health risks

**Alwar**:
- ⚠️ High climate exposure + Moderate air quality (AQI 92) + Low sensitivity = Moderate potential impact
- ⚠️ Low adaptive capacity provides little mitigation
- ✅ **Advantage**: Cleaner air (AQI 92 vs 178) reduces exposure
- 🔑 **Key Issue**: Low income (₹1.37 lakhs) and low urbanization (18%)

---

## 🚀 How to Run

### Prerequisites

```bash
pip install pandas numpy matplotlib seaborn scipy
```

### Execute Analysis

```bash
cd /path/to/EVST_Project/CVI_Analysis
python3 calculate_cvi.py
```

### Expected Outputs

```
CVI_Analysis/
├── calculate_cvi.py
├── cvi_results/
│   └── cvi_results.json          # Machine-readable results
└── cvi_visualizations/
    ├── cvi_components_comparison.png
    ├── cvi_radar_Central_Delhi.png
    ├── cvi_radar_Alwar.png
    └── cvi_summary_table.png
```

### Adding More Districts

Modify the `main()` function:

```python
def main():
    data = load_data()
    
    # Add more districts
    results_district1 = calculate_cvi('District1', data)
    results_district2 = calculate_cvi('District2', data)
    
    all_results = [results_district1, results_district2]
    # ... rest of code
```

---

## 🔧 Customization Options

### 1. Adjust Weights

```python
# In calculate_cvi() function parameters
calculate_cvi(district_name, data, 
              alpha=0.6,    # Increase exposure weight
              beta=0.4,     # Decrease sensitivity weight
              delta=0.7)    # Increase OUV weight in ESC
```

### 2. Change Normalization Factors

```python
# In calculate_exposure_index()
exposure_score = (
    0.3 * rainfall_cv +
    0.2 * (extreme_rain_days / 15) +    # Changed from 10
    0.2 * (temp_max_mean / 45) +        # Changed from 50
    0.2 * (temp_variability / 8) +      # Changed from 10
    0.1 * (heat_wave_count / 25)        # Changed from 20
)
```

### 3. Add New Indicators

```python
# In calculate_exposure_index()
# AQI is already integrated at 20% weight

# To add more indicators to sensitivity:
# Example: flood risk
flood_risk_score = calculate_flood_risk(district_name)

sensitivity_score = (
    0.4 * (pop_density / 20000) +
    0.3 * (gw_depletion_rate / 2) +
    0.3 * (flood_risk_score / 100)       # New indicator
)
```

---

## 📚 References

### Methodological Framework
- IPCC AR6 Climate Vulnerability Framework
- CVI Operational Formulas (Project Documentation)

### Data Sources
- India Meteorological Department (IMD)
- Census of India 2011
- Central Ground Water Board (CGWB)
- District Statistical Handbooks
- National Sample Survey Organisation (NSSO)

---

## 📝 Version History

- **v1.0** (2024-10-14): Initial implementation
  - Districts: Central Delhi, Alwar
  - Indicators: 5 (E) + 2 (S) + 2 (AC)
  - Formulas: Complete 4-step CVI process

- **v2.0** (2024-10-14): AQI Integration
  - Added Air Quality Index as 6th exposure indicator (20% weight)
  - Rebalanced other exposure weights (25%, 15%, 15%, 15%, 10%, 20%)
  - AQI normalization by 400 (Severe threshold)
  - Updated results: Central Delhi CVI=0.3767, Alwar CVI=0.3388

---

## 🤝 Contributing

To improve this analysis:

1. **Add more districts**: Expand coverage to all Delhi NCR
2. **Include more indicators**: Literacy, healthcare, land use
3. **Temporal analysis**: Track CVI changes 2013-2024
4. **Validation**: Compare with actual disaster impacts
5. **Calibration**: Adjust weights based on expert input

---

## 📧 Contact

For questions or collaboration:
- Repository: EVST_Project
- Analysis Date: October 14, 2025

---

**Status**: ✅ COMPLETE (v2.0 with AQI)  
**Districts Analyzed**: 2 (Central Delhi, Alwar)  
**CVI Score Range**: 0.34 - 0.38 (Both MODERATE)  
**Latest Update**: AQI integrated as exposure indicator (20% weight)
**Next Steps**: Expand to all Delhi NCR districts, integrate real-time AQI data, add validation data
