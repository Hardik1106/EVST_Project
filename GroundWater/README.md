# Groundwater Data Processing & Visualization

This folder contains groundwater level data and visualization scripts for Delhi NCR districts.

## Overview

Groundwater level monitoring data is processed to show temporal trends (monthly and yearly) across NCR districts. The visualizations include interactive time-series maps showing groundwater depth changes over time.

## Folder Structure

```
GroundWater/
├── groundwater_monthly.csv       # Raw monthly groundwater data
├── groundwater_yearly.csv        # Raw yearly groundwater data
├── ncr_groundwater_monthly.csv   # Filtered NCR districts monthly
├── ncr_groundwater_yearly.csv    # Filtered NCR districts yearly
├── filtered_ncr_districts.csv    # List of NCR districts for filtering
├── reader.py                     # Data extraction/processing
├── filter_csv.py                 # Filter data to NCR districts only
├── plotter.py                    # Basic plotting
├── plotter2.py                   # Interactive time-series map generator
└── understand_time_range.py      # Utility to check data coverage
```

## Data Sources

- **Source**: Central Ground Water Board (CGWB) / State monitoring agencies
- **Format**: CSV with district-level groundwater depth measurements
- **Units**: Meters below ground level (mbgl)
- **Temporal Coverage**: Varies by district (typically 2010s-2020s)
- **Measurement Frequency**: Monthly or seasonal

## Processing Workflow

### 1. Filter to NCR Districts (`filter_csv.py`)

**Purpose**: Extract only NCR district records from larger groundwater datasets.

**How it works**:
- Reads `filtered_ncr_districts.csv` (list of 37 NCR districts)
- Filters `groundwater_monthly.csv` and `groundwater_yearly.csv`
- Normalizes district names (case-insensitive matching)
- Writes NCR-only CSVs

**Usage**:
```bash
python filter_csv.py
```

**Output**:
- `ncr_groundwater_monthly.csv`
- `ncr_groundwater_yearly.csv`

---

### 2. Process & Validate Data (`reader.py`)

**Purpose**: Read, clean, and validate groundwater data.

**Functions**:
- Load CSV files
- Parse date columns
- Handle missing values
- Compute summary statistics

**Usage**:
```python
python reader.py
```

---

### 3. Generate Interactive Visualizations (`plotter2.py`)

**Purpose**: Create time-series animated choropleth maps showing groundwater level changes.

**How it works**:
- Reads `ncr_groundwater_monthly.csv` or `ncr_groundwater_yearly.csv`
- Merges with district GeoJSON (`Delhi_NCR_Districts_final.geojson`)
- Handles MultiPolygon districts by creating separate features per polygon part
- Applies color scale (blue → yellow → red) for groundwater depth
- Generates TimestampedGeoJson with time slider

**Usage**:
```bash
python plotter2.py
```

**Output**:
- `ncr_groundwater_timeseries_monthly.html`
- `ncr_groundwater_timeseries_yearly.html`

**Features**:
- Time slider to navigate months/years
- Popup shows district name, groundwater depth, date
- Color scale: Deeper groundwater = more concerning (red)
- Handles non-contiguous polygons (Faridabad, Rewari, Bharatpur)

---

## Key Outputs

### CSV Files
- `ncr_groundwater_monthly.csv` - Monthly groundwater levels for NCR districts
  - Columns: `DISTRICT_NAME`, `date`, `depth_mbgl`, etc.
- `ncr_groundwater_yearly.csv` - Yearly averages
  - Columns: `DISTRICT_NAME`, `year`, `avg_depth_mbgl`, etc.

### Interactive Maps
- `../Interactive Visualizations/groundwater_time_series/ncr_groundwater_timeseries_monthly.html`
- `../Interactive Visualizations/groundwater_time_series/ncr_groundwater_timeseries_yearly.html`

---

## Interpretation Guide

### Groundwater Depth Ranges
- **Shallow** (0-5 m): Good availability, sustainable
- **Moderate** (5-15 m): Adequate, monitor trends
- **Deep** (15-30 m): Stress, conservation needed
- **Critical** (>30 m): Severe depletion, urgent action required

### Trend Analysis
- **Increasing depth** = Depletion (concerning)
- **Decreasing depth** = Recharge improvement (positive)
- **Seasonal variation**: Expect depth increase in summer, decrease after monsoon

---

## Common Issues

### Issue 1: District name mismatch
**Symptom**: Fewer districts than expected in output

**Solution**: Check `filtered_ncr_districts.csv` has correct canonical names matching GeoJSON

---

### Issue 2: Missing time periods
**Symptom**: Gaps in time-series visualization

**Solution**: Groundwater monitoring is often seasonal (pre-monsoon, post-monsoon). Gaps are expected.

---

### Issue 3: Extreme values / outliers
**Symptom**: Unrealistic depth values (negative or >100m)

**Solution**: Filter outliers in `reader.py` before visualization

---

## Technical Notes

### MultiPolygon Handling
`plotter2.py` explicitly handles MultiPolygon districts:
```python
if isinstance(geom, MultiPolygon):
    for part in geom.geoms:
        # Create separate feature for each polygon part
```

This pattern is also used in temperature and rainfall visualizations.

### Color Scale
- Uses diverging colormap (blue → white → red)
- Thresholds configurable based on depth ranges
- Grey for no-data districts

---

## Usage Example

```bash
# Step 1: Filter to NCR districts
python filter_csv.py

# Step 2: Check data coverage
python understand_time_range.py

# Step 3: Generate visualizations
python plotter2.py

# Output maps will be in current directory
# Move to Interactive Visualizations folder if needed
```

---

## References

- CGWB Data: https://www.cgwb.gov.in/
- Groundwater level guidelines: CGWB manual on groundwater resource assessment

---

**Last Updated**: October 2025  
**Contact**: See main repository README
