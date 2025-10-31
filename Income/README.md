# Income Data Visualization

This folder contains per-capita income data and visualization scripts for Delhi NCR districts.

## Overview

District-level per-capita income data is visualized through geographic heatmaps to show economic disparities across NCR.

## Folder Structure

```
Income/
├── district_wise.csv          # District per-capita income data
├── viz.py                     # Basic visualization script
└── geo_heatmap_viz.py         # Geographic heatmap generator
```

## Data Sources

- **Source**: State economic surveys, statistical abstracts
- **Variables**: Per-capita income (annual, in ₹)
- **Data Vintage**: Typically 2018-2020 estimates
- **Coverage**: NCR districts

## Processing Workflow

### 1. Basic Visualization (`viz.py`)

**Purpose**: Create simple bar charts and statistical summaries of income distribution.

**Usage**:
```bash
python viz.py
```

**Output**:
- Bar chart showing per-capita income by district
- Statistical summary (mean, median, std dev)

---

### 2. Geographic Heatmap (`geo_heatmap_viz.py`)

**Purpose**: Create choropleth map showing income distribution spatially.

**How it works**:
- Reads `district_wise.csv` (columns: DISTRICT_NAME, Per_Capita_Income)
- Merges with district GeoJSON
- Creates choropleth with color scale (low → high income)
- Adds tooltips and legend

**Usage**:
```bash
python geo_heatmap_viz.py
```

**Output**:
- `income_heatmap.html` - Interactive choropleth map

**Features**:
- Color scale: Reds (light → dark for low → high income)
- Tooltip shows district name and ₹ value
- Legend with income bins

---

## Key Outputs

### CSV Files
- `district_wise.csv` - District per-capita income
  - Columns: DISTRICT_NAME, Per_Capita_Income (₹)

### Interactive Maps
- `income_heatmap.html` - Geographic income distribution map

---

## Interpretation Guide

### Income Categories (NCR Context)
- **High income** (>₹2,00,000): Delhi, Gurugram, Faridabad
- **Upper-middle** (₹1,00,000-₹2,00,000): Ghaziabad, GB Nagar
- **Middle** (₹60,000-₹1,00,000): Most Haryana/UP districts
- **Lower** (<₹60,000): Rural Rajasthan/UP districts

### Economic Disparities
- **Urban-rural gap**: Urban districts typically 2-3× rural per-capita income
- **Interstate variations**: Delhi > Haryana > UP > Rajasthan (general trend)
- **Intra-NCR inequality**: Gurugram has highest, peripheral districts lowest

---

## Common Issues

### Issue 1: Data currency
**Symptom**: Income values seem outdated

**Solution**: 
- Note data vintage in visualization title
- Apply inflation adjustment if comparing across years
- Seek updated state economic survey reports

---

### Issue 2: Missing districts
**Symptom**: Some districts have no income data

**Solution**: 
- Use state-level averages as proxy
- Mark as "No data" in visualization
- Check alternate sources (NITI Aayog, state planning boards)

---

## Technical Notes

### Data Normalization
- Income values are annual per-capita (total district income / population)
- Adjust for Census 2011 population base vs. current estimates
- Handle district reorganization (e.g., Shamli carved out of Muzaffarnagar)

### Choropleth Design
- Uses linear or quantile binning
- Color ramp: YlOrRd or Reds palette
- Bins typically 5-7 classes for readability

---

## Usage Example

```bash
# Generate basic stats and bar chart
python viz.py

# Create geographic heatmap
python geo_heatmap_viz.py

# Open income_heatmap.html in browser
```

---

## Extension Ideas

- Add temporal dimension (income growth trends)
- Overlay with employment data
- Compute Gini coefficient for inequality measurement
- Integrate with CVI analysis (adaptive capacity component)

---

## References

- Economic Survey of Delhi: https://delhi.gov.in/
- Haryana Economic Survey
- UP Statistical Diary
- Rajasthan Socio-Economic Indicators

---

**Last Updated**: October 2025  
**Data Vintage**: 2018-2020 estimates  
**Contact**: See main repository README
