# Rainfall Data Processing

This folder contains scripts and data for processing IMD gridded daily rainfall data for Delhi NCR districts (2013-2024).

## Overview

The rainfall processing pipeline converts IMD high-resolution NetCDF rainfall data (0.25° × 0.25°) into district-level daily and monthly CSV files. Despite finer resolution than temperature data, some districts still require spatial extrapolation.

## Folder Structure

```
Rainfall/
├── rainfall_NetCDF/           # IMD NetCDF files
│   ├── RF25_ind{year}_rfp25.nc (2009-2024)
│   ├── nc_to_csv.py          # NetCDF → CSV converter (2013-2023)
│   └── nc_to_csv_24.py       # Special converter for 2024 (variable name changes)
├── rainfall_csv/              # Extracted district-level daily rainfall CSVs
│   └── delhi_rainfall_districts_{year}.csv (2013-2024)
├── rainfall_analysis/         # Filled data & analysis
│   ├── rainfall_vis1.py      # Interactive time-series visualizations
│   ├── rainfall_anomalies.csv
│   └── yearly_trend_slopes.csv
├── process_rainfall.py        # Monthly aggregation across years
├── rainfall_extrap.py         # Missing district extrapolation
├── rainfall_vis2.py           # Alternative visualization script
├── sd_rainfall.py             # Standardization (z-scores)
├── delhi_ncr_rainfall_monthly_avg_2013_2024.csv        # Base monthly output
└── delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv # Extrapolated monthly output
```

## Data Sources

- **Agency**: India Meteorological Department (IMD)
- **Product**: 0.25° × 0.25° daily gridded rainfall
- **Format**: NetCDF (`.nc` files)
- **Coverage**: 2013–2024
- **Spatial Resolution**: ~28 km
- **Variable Names**:
  - 2013-2023: `RAINFALL` or `rain`
  - 2024: `rf` (lowercase - requires special handling)

## Processing Pipeline

### 1. Extract NetCDF to District CSVs (`rainfall_csv/nc_to_csv.py` & `nc_to_csv_24.py`)

**Purpose**: Read IMD NetCDF files and map rainfall grid points to NCR districts.

**How it works**:

- Opens NetCDF file using `xarray`
- Auto-detects variable name (`RAINFALL`, `rain`, or `rf`)
- Clips to Delhi NCR bounding box
- Creates point geometries for each grid cell
- Uses spatial join (intersects) to assign grid points to districts
- Writes per-year district CSVs to `rainfall_csv/`

**Usage**:

```bash
cd rainfall_csv
# For years 2013-2023
python nc_to_csv.py

# For year 2024 (if variable names differ)
python nc_to_csv_24.py
```

**Output**:

- `rainfall_csv/delhi_rainfall_districts_{year}.csv`
- Columns: `DISTRICT_NAME`, `date`, `RAINFALL`

**Note**: ~13 districts may have no values due to grid coverage gaps.

---

### 2. Aggregate Monthly Averages (`process_rainfall.py`)

**Purpose**: Compute district-level monthly mean rainfall across all years.

**How it works**:

- Reads `rainfall_csv/delhi_rainfall_districts_{year}.csv` for each year
- Groups by (DISTRICT_NAME, YEAR, MONTH)
- Computes mean rainfall per month
- Combines all years into single CSV

**Usage**:

```bash
python process_rainfall.py
```

**Output**:

- `delhi_ncr_rainfall_monthly_avg_2013_2024.csv`
- Columns: `YEAR`, `MONTH`, `DISTRICT_NAME`, `RAINFALL`
- Some district-months may be missing

---

### 3. Extrapolate Missing Districts (`rainfall_extrap.py` or within `rainfall_analysis/rainfall_vis1.py`)

**Purpose**: Fill missing district-month rainfall values using spatial extrapolation.

**Method** (two-stage):

1. **Neighbor Averaging**: Average values from directly adjacent districts (polygon intersects) for the same month.
2. **Nearest-Neighbor (Centroid)**: Use k-NN from district centroids (EPSG:32643 projection) to copy nearest available value.

**How it works**:

- Builds complete index of all (district × year × month) combinations
- Fills missing values using neighbor mean, then centroid nearest-neighbor fallback
- Marks filled rows with `FILLED=True` and `FILLED_METHOD='neighbor'` or `'nearest'`

**Usage**:

```bash
# Integrated into rainfall_vis1.py
cd rainfall_analysis
python rainfall_vis1.py
```

**Output**:

- `delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv`
- `coverage_fill_report.csv` (audit of which values were filled)

---

### 4. Standardize to Z-scores (`sd_rainfall.py`)

**Purpose**: Compute standardized anomalies (z-scores) for rainfall.

**How it works**:

- Reads monthly filled CSV
- Computes global mean and standard deviation of rainfall
- Transforms values to z-scores: `z = (value - mean) / std`
- Saves standardized series

**Usage**:

```bash
python sd_rainfall.py
```

**Output**:

- `delhi_ncr_rainfall_monthly_avg_filled_standardized.csv`
- Columns: `YEAR`, `MONTH`, `DISTRICT_NAME`, `RAINFALL_z`

---

### 5. Generate Interactive Visualizations (`rainfall_analysis/rainfall_vis1.py`)

**Purpose**: Create time-series animated choropleth map for monthly rainfall.

**How it works**:

- Reads filled monthly CSV and district GeoJSON
- Creates TimestampedGeoJson features with monthly time steps
- Handles MultiPolygon districts by creating separate features per polygon part
- Applies color scale (white → blue → purple) based on rainfall range
- Generates interactive HTML map with time slider

**Usage**:

```bash
cd rainfall_analysis
python rainfall_vis1.py
```

**Output**:

- `delhi_ncr_rainfall_timeseries_allpolygons.html`
- Features time slider, popup with rainfall value and fill status

---

## Key Files & Outputs

### Input Files (Raw Data)

- `rainfall_NetCDF/RF25_ind{year}_rfp25.nc` - IMD NetCDF rainfall files
- `../GeoJsons/Delhi_NCR_Districts_final.geojson` - District boundaries

### Intermediate Outputs

- `rainfall_csv/delhi_rainfall_districts_{year}.csv` - Extracted grid points (some missing)
- `delhi_ncr_rainfall_monthly_avg_2013_2024.csv` - Monthly averages (sparse)

### Final Outputs

- `delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv` - Complete monthly data with extrapolation
- `coverage_fill_report.csv` - Fill audit (which districts/months were filled and by which method)
- `delhi_ncr_rainfall_monthly_avg_filled_standardized.csv` - Z-scores
- `rainfall_analysis/delhi_ncr_rainfall_timeseries_allpolygons.html` - Interactive map

---

## Spatial Extrapolation Details

### Why Extrapolation is Needed

IMD rainfall grid is 0.25° × 0.25° (~28 km resolution). While finer than temperature, it still misses **~13 out of 37 districts** due to:

- District boundaries not aligning with grid centers
- Smaller districts falling between grid points
- Edge effects at NCR boundary

### Extrapolation Method

#### Stage 1: Neighbor Averaging

- For each missing district-month value:
  - Find adjacent districts (polygons that intersect the target district)
  - If neighbors have values for that month, assign the mean
- **Advantages**: Assumes local spatial similarity (valid for monsoon rainfall patterns)
- **Limitations**: Fails if all neighbors are also missing

#### Stage 2: Nearest-Neighbor (Centroid)

- For values still missing after Stage 1:
  - Compute district centroids in projected CRS (EPSG:32643)
  - Find nearest district with a value for that month using cKDTree
  - Copy the nearest value
- **Advantages**: Always finds a value if any district has data
- **Limitations**: Assumes nearest district has similar rainfall (may not hold for mountainous regions or rain-shadow effects)

### Data Provenance Flags

Every row in filled CSV includes:

- `FILLED` (boolean): True if value was extrapolated, False if original
- `FILLED_METHOD`: 'original', 'neighbor', or 'nearest'

### Fill Audit

The `coverage_fill_report.csv` records:

- `YEAR`, `MONTH`, `district` (which district was filled)
- `method` ('neighbor' or 'nearest')
- `source` (which district provided the value)

Example:

```
YEAR,MONTH,district,method,source
2013,1,west,nearest,west delhi
2013,1,faridabad,nearest,south delhi
```

---

## Common Issues & Troubleshooting

### Issue 1: NetCDF variable not found

**Error**: `KeyError: 'RAINFALL'` or `'rain'`

**Solution**: IMD changed variable naming across years. Use:

- `nc_to_csv.py` for most years (tries `RAINFALL`, `rain`, `rf`)
- `nc_to_csv_24.py` for 2024 specifically (handles lowercase `rf`)

---

### Issue 2: Missing district names in output

**Symptom**: Fewer than 37 districts in monthly CSV

**Solution**: Check GeoJSON property name. Scripts detect `dtname`, `NAME_2`, `DISTRICT_NAME`. Use `Delhi_NCR_Districts_final.geojson`.

---

### Issue 3: Large HTML file size

**Symptom**: Visualization HTML is >100 MB

**Solution**:

- Use Git LFS (already configured in `.gitattributes`)
- Simplify geometries before visualization
- Reduce time range (filter specific years)

---

### Issue 4: Duplicate districts after fill

**Symptom**: Multiple rows for same district-month

**Solution**: Run harmonization script to collapse duplicates preferring original values. Example from temperature pipeline can be adapted.

---

## Technical Notes

### NetCDF Format

- **Dimensions**: `time`, `latitude`, `longitude`
- **Variables**:
  - 2013-2023: `RAINFALL` or `rain` (units: mm/day)
  - 2024: `rf` (lowercase)
- **Coordinate system**: WGS84 (EPSG:4326)
- **Time encoding**: Days since epoch or datetime64

### Coordinate Reference Systems

- **Input NetCDF & GeoJSON**: EPSG:4326 (WGS84)
- **Distance calculations**: EPSG:32643 (UTM Zone 43N) for accurate metric distances
- **Visualization output**: EPSG:4326 (required by folium)

### Performance Considerations

- NetCDF reading with `xarray` is memory-efficient (lazy loading)
- Spatial joins are accelerated with rtree/pygeos spatial index
- Time-series visualization feature generation can be slow for 12 years × 37 districts × 12 months = 5,328 features

---

## Verification & Quality Checks

### Check 1: District coverage

```python
import pandas as pd
df = pd.read_csv('delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv')
print(df['DISTRICT_NAME'].nunique())  # Should be 37
```

### Check 2: Completeness (no missing months)

```python
expected_rows = 37 * 12 * 12  # 5,328
print(len(df))  # Should match
```

### Check 3: Reasonable rainfall ranges

```python
print(df['RAINFALL'].describe())
# Typical range: 0-500 mm/month (monsoon peaks can be higher)
```

### Check 4: Fill audit summary

```python
audit = pd.read_csv('../coverage_fill_report.csv')
print(audit['method'].value_counts())
print(f"Fill rate: {len(audit) / expected_rows * 100:.1f}%")
```

---

## Advanced Usage

### Customize extrapolation parameters

Edit `rainfall_analysis/rainfall_vis1.py`:

- Change k in nearest-neighbor search
- Add inverse-distance weighting instead of simple copy
- Weight by shared border length

### Generate anomaly maps

Use `sd_rainfall.py` output to visualize standardized anomalies:

- Positive z-scores = wetter than average
- Negative z-scores = drier than average
- Thresholds: |z| > 1.5 (moderate), |z| > 2.0 (extreme)

### Trend analysis

See `rainfall_analysis/yearly_trend_slopes.csv` for linear trend slopes per district.

---

## References & Further Reading

- IMD gridded rainfall documentation: See `../Sources Used/Rainfall Source.url`
- NetCDF format: <https://www.unidata.ucar.edu/software/netcdf/>
- GeoPandas: <https://geopandas.org/>
- Folium TimestampedGeoJson: <https://python-visualization.github.io/folium/plugins.html>

---

**Last Updated**: October 2025  
**Data Coverage**: 2013-2024  
**Contact**: See main repository README
