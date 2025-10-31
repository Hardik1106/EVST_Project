# Temperature Data Processing

This folder contains scripts and data for processing IMD gridded daily minimum and maximum temperature data for Delhi NCR districts (2013-2024).

## Overview

The temperature processing pipeline converts coarse-resolution IMD binary gridded data (1° × 1°) into district-level daily and monthly CSV files. Due to the coarse grid, many districts have no direct grid points and require spatial extrapolation.

## Folder Structure

```
Temperature/
├── minT_GRD/              # IMD binary files for minimum temperature
│   └── Mintemp_MinT_{year}.GRD (2013-2024)
├── maxT_GRD/              # IMD binary files for maximum temperature
│   └── Maxtemp_MaxT_{year}.GRD (2013-2024)
├── minT_csv/              # Extracted district-level min temperature CSVs
│   └── Delhi_MinTemp_Districts_{year}.csv
├── maxT_csv/              # Extracted district-level max temperature CSVs
│   └── Delhi_MaxTemp_Districts_{year}.csv
├── temp_csv/              # Extrapolated daily temperature (min + max combined)
│   ├── temp_extrap.py     # Extrapolation script
│   └── Temperature_{year}.csv (2013-2024)
├── temp_analysis/         # Anomaly analysis and visualizations
│   ├── anomalies_AVGT.csv
│   ├── yearly_trend_slopes_AVGT.csv
│   └── temp_vis1.py, temp_vis2.py
├── bin_to_csv.py          # GRD binary → district CSV converter
├── process_temp.py        # Monthly aggregation across years
├── temp_vis1.py           # Interactive time-series visualizations
├── sd_temp.py             # Standardization (z-scores)
└── delhi_ncr_temp_monthly_avg_2013_2024.csv  # Final monthly output
```

## Data Sources

- **Agency**: India Meteorological Department (IMD)
- **Product**: 1° × 1° daily gridded minimum and maximum temperature
- **Format**: Binary GRD files
- **Coverage**: 2013–2024
- **Spatial Resolution**: ~111 km (coarse)
- **Grid Dimensions**: 31 × 31 (latitude × longitude)

## Processing Pipeline

### 1. Extract Grid Points to District CSVs (`bin_to_csv.py`)

**Purpose**: Read IMD binary GRD files and map grid points to NCR districts.

**How it works**:

- Reads binary files as `float32` arrays reshaped to (days, 31 lat, 31 lon)
- Creates point geometries for each grid cell
- Uses spatial join (intersects) to assign grid points to districts
- Writes per-year district CSVs to `minT_csv/` and `maxT_csv/`

**Usage**:

```bash
python bin_to_csv.py
```

**Output**:

- `minT_csv/Delhi_MinTemp_Districts_{year}.csv` (columns: DISTRICT_NAME, date, value)
- `maxT_csv/Delhi_MaxTemp_Districts_{year}.csv`

**Note**: Many districts will have **no values** due to coarse grid resolution.

---

### 2. Extrapolate Missing Districts (`temp_csv/temp_extrap.py`)

**Purpose**: Fill missing district-day temperature values using spatial extrapolation.

**Method** (two-stage):

1. **Neighbor Averaging**: For each missing district-day, average values from directly adjacent districts (polygon intersects).
2. **Inverse-Distance Weighting (IDW)**: If neighbor averaging fails, use k=5 nearest districts weighted by centroid distance (EPSG:32643 projection).

**How it works**:

- Reads `minT_csv/Delhi_MinTemp_Districts_{year}.csv` and `maxT_csv/Delhi_MaxTemp_Districts_{year}.csv`
- Auto-detects value column names and normalizes to `minT` / `maxT`
- Builds complete index of all (district × date) combinations
- Fills missing values using neighbor mean, then IDW fallback
- Marks filled rows with `FILLED=True` and `FILLED_METHOD='filled'`

**Usage**:

```bash
cd temp_csv
python temp_extrap.py
```

**Output**:

- `temp_csv/Temperature_{year}.csv` for each year (2013-2024)
- Columns: `DISTRICT_NAME`, `DISTRICT_NAME_clean`, `date`, `TIME_ISO`, `minT`, `maxT`, `FILLED`, `FILLED_METHOD`

**Performance**: Processes all 12 years in ~1-2 minutes.

---

### 3. Aggregate Monthly Averages (`process_temp.py`)

**Purpose**: Compute district-level monthly averages of minT, maxT, and avgT across all years.

**How it works**:

- Reads `temp_csv/Temperature_{year}.csv` for each year
- Groups by (DISTRICT_NAME, YEAR, MONTH)
- Computes mean of `minT`, `maxT`, and `avgT = (minT + maxT) / 2`
- Combines all years into single CSV

**Usage**:

```bash
python process_temp.py
```

**Output**:

- `delhi_ncr_temp_monthly_avg_2013_2024.csv`
- Columns: `YEAR`, `MONTH`, `DISTRICT_NAME`, `minT`, `maxT`, `avgT`
- Rows: 37 districts × 12 months × 12 years = 5,328 rows

---

### 4. Standardize to Z-scores (`sd_temp.py`)

**Purpose**: Compute standardized anomalies (z-scores) for temperature metrics.

**How it works**:

- Reads monthly CSV
- For each metric (minT, maxT, avgT):
  - Computes global mean and standard deviation
  - Transforms values to z-scores: `z = (value - mean) / std`
- Saves standardized series

**Usage**:

```bash
python sd_temp.py
```

**Output**:

- `delhi_ncr_temp_monthly_avg_standardized.csv`
- Columns: `YEAR`, `MONTH`, `DISTRICT_NAME`, `minT_z`, `maxT_z`, `avgT_z`

---

### 5. Generate Interactive Visualizations (`temp_vis1.py`)

**Purpose**: Create time-series animated choropleth maps for minT, maxT, and avgT.

**How it works**:

- Reads monthly CSV and district GeoJSON
- For each metric, creates TimestampedGeoJson features with monthly time steps
- Handles MultiPolygon districts by creating separate features per polygon part
- Applies color scale (blue → yellow → red) based on temperature range
- Generates interactive HTML maps with time slider

**Usage**:

```bash
python temp_vis1.py
```

**Output**:

- `temp_vis_maps/delhi_ncr_temp_timeseries_minT.html`
- `temp_vis_maps/delhi_ncr_temp_timeseries_maxT.html`
- `temp_vis_maps/delhi_ncr_temp_timeseries_avgT.html`

**Features**:

- Time slider to navigate months (2013-01 to 2024-12)
- Popup shows district name, temperature value, date
- Grey color for missing/no-data districts
- Handles MultiPolygon geometries (Faridabad, Rewari, Bharatpur)

---

## Key Files & Outputs

### Input Files (Raw Data)

- `minT_GRD/Mintemp_MinT_{year}.GRD` - IMD binary min temp (one per year)
- `maxT_GRD/Maxtemp_MaxT_{year}.GRD` - IMD binary max temp (one per year)
- `../GeoJsons/Delhi_NCR_Districts_final.geojson` - District boundaries

### Intermediate Outputs

- `minT_csv/Delhi_MinTemp_Districts_{year}.csv` - Extracted grid points (sparse)
- `maxT_csv/Delhi_MaxTemp_Districts_{year}.csv` - Extracted grid points (sparse)
- `temp_csv/Temperature_{year}.csv` - Extrapolated daily data (complete)

### Final Outputs

- `delhi_ncr_temp_monthly_avg_2013_2024.csv` - Monthly averages (all districts, all years)
- `delhi_ncr_temp_monthly_avg_standardized.csv` - Standardized z-scores
- `temp_vis_maps/*.html` - Interactive time-series maps

---

## Spatial Extrapolation Details

### Why Extrapolation is Needed

IMD temperature grid is 1° × 1° (~111 km resolution). Delhi NCR districts are much smaller. Result: **~33 out of 37 districts have zero grid points** in their boundaries.

### Extrapolation Method

#### Stage 1: Neighbor Averaging

- For each missing district-day value:
  - Find adjacent districts (polygons that intersect the target district)
  - If neighbors have values for that date, assign the mean
- **Advantages**: Assumes local spatial similarity
- **Limitations**: Fails if all neighbors are also missing

#### Stage 2: Inverse-Distance Weighting (IDW)

- For values still missing after Stage 1:
  - Compute district centroids in projected CRS (EPSG:32643 for metric distances)
  - Find k=5 nearest districts with values for that date
  - Compute weighted average: `value = Σ(w_i × v_i) / Σ(w_i)` where `w_i = 1 / distance_i`
- **Advantages**: Always finds values if any donors exist
- **Limitations**: Assumes smooth spatial variation (may not hold for abrupt local changes)

### Data Provenance Flags

Every row includes:

- `FILLED` (boolean): True if value was extrapolated, False if original
- `FILLED_METHOD`: 'original' or 'filled' (can be refined to 'neighbor' vs 'idw')

---

## Common Issues & Troubleshooting

### Issue 1: Missing CSV files

**Error**: `FileNotFoundError: minT_csv/Delhi_MinTemp_Districts_{year}.csv`

**Solution**: Run `bin_to_csv.py` first to extract from GRD files.

---

### Issue 2: Column name mismatch

**Error**: `ValueError: Temperature CSV missing DISTRICT_NAME column`

**Solution**: Ensure CSV has `DISTRICT_NAME` column. The script auto-detects value columns but requires district name.

---

### Issue 3: GeoJSON property name mismatch

**Symptom**: Districts missing in output or name-join failures

**Solution**: The scripts detect multiple property name variants (`dtname`, `NAME_2`, `DISTRICT_NAME`). Use `Delhi_NCR_Districts_final.geojson` which has `dtname`.

---

### Issue 4: Slow visualization generation

**Symptom**: `temp_vis1.py` takes long time

**Solution**:

- Reduce date range (edit script to filter years/months)
- Simplify geometries: `boundary.geometry.simplify(tolerance=0.01)`
- Process one metric at a time

---

## Technical Notes

### Binary GRD Format

- Layout: `float32` array, little-endian
- Shape: `(n_days, 31, 31)` where n_days = 365 or 366 (leap years)
- Grid coordinates: lats = 6.5° to 38.5°, lons = 66.5° to 100.0°
- Missing values: typically represented as very large negative or NaN

### Coordinate Reference Systems

- **Input GeoJSON**: EPSG:4326 (WGS84)
- **Distance calculations**: EPSG:32643 (UTM Zone 43N) for accurate metric distances
- **Visualization output**: EPSG:4326 (required by folium)

### Performance Considerations

- `temp_extrap.py` uses row-wise iteration (iterrows) which is acceptable for ~13,000 rows (37 districts × 365 days). For larger datasets, vectorize using KDTree bulk queries.
- Spatial index (rtree/pygeos) is used for neighbor lookups to reduce O(n²) comparisons.

---

## Verification & Quality Checks

### Check 1: District coverage

```python
import pandas as pd
df = pd.read_csv('delhi_ncr_temp_monthly_avg_2013_2024.csv')
print(df['DISTRICT_NAME'].nunique())  # Should be 37
```

### Check 2: Completeness (no missing months)

```python
expected_rows = 37 * 12 * 12  # 5,328
print(len(df))  # Should match
```

### Check 3: Reasonable temperature ranges

```python
print(df[['minT', 'maxT', 'avgT']].describe())
# minT: ~5-30°C, maxT: ~20-45°C, avgT: ~15-35°C
```

### Check 4: Fill rate

```python
filled_df = pd.read_csv('temp_csv/Temperature_2023.csv')
print(filled_df['FILLED'].value_counts())
# Most should be filled (due to coarse grid)
```

---

## Advanced Usage

### Customize extrapolation parameters

Edit `temp_csv/temp_extrap.py`:

- Change `k=5` in IDW function to use more/fewer donors
- Add distance threshold cutoff
- Weight by shared border length instead of centroid distance

### Add more detailed fill provenance

Modify extrapolation script to record:

- Which specific donors contributed
- Distance to each donor
- Whether neighbor or IDW was used

### Optimize for large-scale processing

- Vectorize IDW using cKDTree batch queries
- Cache centroid coordinates and spatial index
- Use Dask for parallel year processing

---

## References & Further Reading

- IMD gridded temperature documentation: See `../Sources Used/Temp_min Source.url` and `Temp_max Source.url`
- Spatial interpolation methods: Shepard (1968), "A two-dimensional interpolation function for irregularly-spaced data"
- GeoPandas spatial joins: <https://geopandas.org/en/stable/docs/user_guide/mergingdata.html>

---

**Last Updated**: October 2025  
**Data Coverage**: 2013-2024  
**Contact**: See main repository README
