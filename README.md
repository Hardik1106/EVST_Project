# Delhi NCR Environmental & Socioeconomic Data Analysis (EVST_Project)

This repository contains a comprehensive analysis of environmental and socioeconomic indicators for the Delhi National Capital Region (NCR) from 2013–2024. The project processes IMD gridded climate data (temperature, rainfall), groundwater levels, population statistics, income data, and computes a Climate Vulnerability Index (CVI) for all NCR districts.

## Project Overview

The project combines multiple environmental and socioeconomic datasets to:

- Convert IMD gridded binary/NetCDF climate data to district-level CSVs
- Fill missing district values using spatial extrapolation (neighbor averaging + inverse-distance weighting)
- Compute monthly averages and standardized anomalies for climate variables
- Analyze groundwater trends and population/income distributions
- Calculate comprehensive Climate Vulnerability Index (CVI) for each district
- Generate interactive time-series visualizations and choropleth maps

## Repository Structure

```
  EVST_Project/
  ├── README.md                          # This file - project overview
  ├── requirements.txt                   # Python dependencies
  ├── .gitattributes                     # Git LFS config for HTML files
  │
  ├── GeoJsons/                          # District boundary files
  │   ├── Delhi_NCR_Districts_final.geojson  # Primary boundary (dtname property)
  │   ├── Delhi_NCR_Districts.geojson        # Legacy boundary
  │   └── *.py                               # Boundary processing scripts
  │
  ├── Temperature/                       # Temperature data processing
  │   ├── README.md                      # Temperature-specific documentation
  │   ├── minT_GRD/, maxT_GRD/          # IMD binary files (2013-2024)
  │   ├── minT_csv/, maxT_csv/          # Extracted district CSVs
  │   ├── temp_csv/                      # Extrapolated daily CSVs per year
  │   ├── temp_analysis/                 # Anomaly analysis & visualizations
  │   ├── bin_to_csv.py                  # GRD → CSV converter
  │   ├── temp_extrap.py                 # Daily extrapolation (neighbor + IDW)
  │   ├── process_temp.py                # Monthly aggregation
  │   ├── temp_vis1.py                   # Interactive time-series maps
  │   └── sd_temp.py                     # Standardization (z-scores)
  │
  ├── Rainfall/                          # Rainfall data processing
  │   ├── README.md                      # Rainfall-specific documentation
  │   ├── rainfall_NetCDF/              # IMD NetCDF files (2013-2024)
  │   ├── rainfall_csv/                  # Extracted district CSVs
  │   ├── rainfall_analysis/             # Filled data & visualizations
  │   ├── process_rainfall.py            # Monthly aggregation
  │   ├── rainfall_extrap.py             # Missing data extrapolation
  │   ├── rainfall_vis2.py               # Interactive visualizations
  │   └── sd_rainfall.py                 # Standardization
  │
  ├── GroundWater/                       # Groundwater level data
  │   ├── README.md                      # Groundwater documentation
  │   ├── ncr_groundwater_monthly.csv    # Monthly groundwater levels
  │   ├── ncr_groundwater_yearly.csv     # Yearly averages
  │   ├── reader.py                      # Data extraction
  │   ├── plotter.py, plotter2.py        # Visualization scripts
  │   └── filter_csv.py                  # NCR district filtering
  │
  ├── Population/                        # Population data & analysis
  │   ├── README.md                      # Population documentation
  │   ├── NCR_District_Wise_Population.csv  # District population data
  │   ├── Delhi_NCR_Population_Data_Clean.csv
  │   ├── step1_extract_delhi_ncr_clean.py  # Data cleaning
  │   ├── step2_choropleth_viz.py           # Choropleth maps
  │   └── *.html                            # Generated visualizations
  │
  ├── Income/                            # Per-capita income data
  │   ├── README.md                      # Income documentation
  │   ├── district_wise.csv              # District income data
  │   ├── viz.py                         # Basic visualization
  │   └── geo_heatmap_viz.py            # Geographic heatmap
  │
  ├── CVI_Analysis/                      # Climate Vulnerability Index
  │   ├── README.md                      # CVI methodology & usage
  │   ├── calculate_cvi_all_districts.py # Main CVI computation
  │   ├── METHODOLOGY.md                 # Detailed methodology
  │   ├── QUICK_START.md                 # Quick usage guide
  │   ├── cvi_results/                   # Output CSVs and maps
  │   └── *.md                           # Various reports
  │
  ├── Interactive Visualizations/        # All generated HTML maps
  │   ├── temp_timeseries/              # Temperature animations
  │   ├── rainfall_time_series/         # Rainfall animations
  │   ├── groundwater_time_series/      # Groundwater trends
  │   └── delhi_ncr_cvi_map.html        # CVI choropleth
  │
  ├── FINAL_VIZ/                         # Final polished visualizations
  │   ├── temp_viz/
  │   └── groundwater_viz/
  │
  └── Sources Used/                      # Data source references
      ├── Delhi_NCR Defination.url
      ├── Rainfall Source.url
      ├── Temp_max Source.url
      └── Temp_min Source.url
  ```

## Data Sources & Metadata

All primary data used in this project are published by the India Meteorological Department (IMD) and the National Capital Region Planning Board (NCRPB). Data source shortcuts are saved under `Sources Used/`:

1. **Delhi NCR constituent districts definition**
   - Agency: National Capital Region Planning Board (NCRPB)
   - Reference: NCRPB constituent districts page

2. **Rainfall data** (IMD high spatial resolution gridded rainfall)
   - Agency: India Meteorological Department (IMD)
   - Product: 0.25° × 0.25° daily gridded rainfall (NetCDF format)
   - Years: 2013–2024

3. **Maximum temperature** (IMD daily gridded maximum temperature)
   - Agency: India Meteorological Department (IMD)
   - Product: 1° × 1° daily gridded max temperature (GRD binary format)
   - Years: 2013–2024

4. **Minimum temperature** (IMD daily gridded minimum temperature)
   - Agency: India Meteorological Department (IMD)
   - Product: 1° × 1° daily gridded min temperature (GRD binary format)
   - Years: 2013–2024

5. **Groundwater levels**
   - Source: Central Ground Water Board (CGWB) / State monitoring data
   - Format: CSV with monthly/yearly district averages

6. **Population & Income**
   - Source: Census 2011, state statistical bulletins
   - Format: CSV district-wise tabular data

## Key Features & Methods

### Spatial Extrapolation for Missing Districts

When gridded climate data do not cover certain districts (due to coarse resolution or district boundaries not aligning with grid points), we use a two-stage extrapolation:

1. **Neighbor Averaging**: For missing district-day values, average the values of directly adjacent districts (polygon intersects).
2. **Inverse-Distance Weighting (IDW)**: If neighbor averaging fails, compute a weighted average from the k nearest districts (based on centroid distance in EPSG:32643 projection), where closer districts contribute more.

All filled values are flagged with `FILLED=True` and `FILLED_METHOD` to preserve data provenance.

### Monthly Aggregation & Standardization

- Daily district values are aggregated to monthly averages.
- Standardized (z-score) series are computed globally and per-district to identify anomalies and trends.
- Output CSVs include columns: YEAR, MONTH, DISTRICT_NAME, value, and flags.

### Interactive Visualizations

- **TimestampedGeoJson** maps allow time-slider navigation through monthly data.
- **Choropleth maps** show spatial distribution of population, income, CVI scores.
- MultiPolygon districts (Faridabad, Rewari, Bharatpur) are handled by creating separate features for each polygon part.
- All HTML outputs use Git LFS (see `.gitattributes`).

### Climate Vulnerability Index (CVI)

The CVI integrates multiple indicators across exposure, sensitivity, and adaptive capacity dimensions:

- **Exposure**: Temperature anomalies, rainfall variability, groundwater depletion
- **Sensitivity**: Population density, urbanization rate
- **Adaptive Capacity**: Per-capita income, infrastructure access

See `CVI_Analysis/METHODOLOGY.md` for detailed calculation steps and `CVI_Analysis/QUICK_START.md` for usage.

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

Required Python packages:

- `pandas`, `numpy`, `geopandas`, `shapely`
- `xarray`, `netCDF4`, `rioxarray` (for NetCDF processing)
- `scipy` (for spatial operations)
- `folium`, `branca` (for interactive maps)
- `scikit-learn` (for standardization)

### Basic Workflow

1. **Process Temperature Data**

   ```bash
   cd Temperature
   # See Temperature/README.md for detailed steps
   python bin_to_csv.py          # Extract from GRD files
   python temp_extrap.py          # Fill missing districts
   python process_temp.py         # Monthly aggregation
   python temp_vis1.py            # Generate visualizations
   ```

2. **Process Rainfall Data**

   ```bash
   cd Rainfall
   # See Rainfall/README.md for detailed steps
   python rainfall_csv/nc_to_csv.py    # Extract from NetCDF
   python rainfall_extrap.py           # Fill missing districts
   python process_rainfall.py          # Monthly aggregation
   python rainfall_vis2.py             # Generate visualizations
   ```

3. **Calculate Climate Vulnerability Index**

   ```bash
   cd CVI_Analysis
   # See CVI_Analysis/QUICK_START.md for detailed usage
   python calculate_cvi_all_districts.py
   ```

### Output Files

- **Monthly climate CSVs**: `Temperature/delhi_ncr_temp_monthly_avg_2013_2024.csv`, `Rainfall/delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv`
- **Interactive maps**: `Interactive Visualizations/` (temperature, rainfall, groundwater time-series)
- **CVI results**: `CVI_Analysis/cvi_results/cvi_results_all_districts.csv` and map

## Detailed Documentation

For detailed information about each data type and processing workflow, see the README files in each subdirectory:

- **Temperature**: [Temperature/README.md](Temperature/README.md)
- **Rainfall**: [Rainfall/README.md](Rainfall/README.md)
- **Groundwater**: [GroundWater/README.md](GroundWater/README.md)
- **Population**: [Population/README.md](Population/README.md)
- **Income**: [Income/README.md](Income/README.md)
- **CVI Analysis**: [CVI_Analysis/README.md](CVI_Analysis/README.md)

## Project Structure Conventions

- **Naming**: District names are normalized to lowercase (`DISTRICT_NAME_clean`) for robust joins across datasets.
- **GeoJSON**: `GeoJsons/Delhi_NCR_Districts_final.geojson` uses `dtname` property; legacy files use `NAME_2`.
- **Filled Data**: All extrapolated/filled values include `FILLED` (boolean) and `FILLED_METHOD` ('neighbor', 'idw', or 'original') columns.
- **Time Format**: Date columns use `YYYY-MM-DD` format; `TIME_ISO` uses ISO 8601 format for visualization compatibility.

## Known Issues & Limitations

1. **Temperature grid resolution**: IMD temperature data is 1° × 1° (coarse), leading to ~33 districts with no direct grid points. Extrapolation fills these gaps but introduces uncertainty.
2. **Rainfall coverage**: 0.25° grid is finer but still misses ~13 districts; neighbor/IDW fills applied.
3. **MultiPolygon rendering**: Districts with non-contiguous parts (Faridabad, Rewari, Bharatpur) are handled by creating separate features per polygon part.
4. **Git LFS**: HTML visualization files use Git LFS; ensure `git lfs pull` after cloning.
5. **Performance**: Feature generation for time-series maps can be slow for large date ranges; consider geometry simplification or caching.

## Contributing & Extensions

Potential improvements:

- Add elevation/terrain-weighted IDW for temperature extrapolation
- Incorporate land-use/land-cover data into CVI
- Automate data updates (e.g., fetch latest IMD products)
- Add statistical tests for trend significance
- Implement uncertainty quantification for filled values

---

**Last Updated**: October 2025  
**Data Coverage**: 2013–2024 (Climate), 2011+ (Socioeconomic)  
**Spatial Extent**: Delhi NCR (37 districts across Delhi, Haryana, Uttar Pradesh, Rajasthan)

- `sd_temp.py` computes global z-scores for `minT`, `maxT` and `avgT` and district-wise standardized values saved to `delhi_ncr_temp_monthly_avg_standardized.csv`.
- `sd_rainfall.py` computes global and district-wise standardized rainfall series and writes `delhi_ncr_rainfall_monthly_avg_standardized.csv`.

## Assumptions and limitations

- The scripts assume the IMD gridded products use the documented lat/lon grid and that the `.GRD` binary ordering matches the reshape used in `bin_to_csv.py` and the test script `test_temp.py`. If IMD changes ordering/shape, outputs will be incorrect.

- The code handles leap years by using a hardcoded `lpyears = [2016, 2020, 2024]`. If you process other years, update the list accordingly or compute leap years dynamically.

- The approach maps grid cell center points to district polygons using a spatial join. Edge cases where a grid point falls on a polygon boundary depend on the geopandas predicate (e.g., `within` vs `intersects`). Verify `GeoJsons/Delhi_NCR_Districts.geojson` CRS matches the grid (EPSG:4326) before joining.

- Some districts may have zero grid points (if the region extent or grid resolution excludes them). The `process_temp.py` and `process_rainfall.py` scripts merge with the full district list so missing values appear as NaN; downstream analysis should handle these.

- The `.url` files in `Sources Used/` point to IMD landing pages. For strict provenance, record the exact file names, download dates and checksums for each GRD/NetCDF file and add them to a manifest.

- Rainfall in the NetCDF/CSV is assumed to be in millimeters (verify with IMD product metadata). Temperature is assumed to be in degrees Celsius. Confirm units in raw files before use.

- Using `test_temp.py` we observed that the min/max temperature binary (`.GRD`) files only contain grid points that fall within 3 Delhi-NCR district polygons (i.e., only 3 districts have direct grid coverage from the binary files). The rest of the Delhi-NCR districts are outside the sparse grid coverage present in those GRD files.

- To obtain district-level daily minT/maxT for all districts, the repository includes an extrapolation routine `temp_csv/temp_extrap.py` which:
  - computes district centroids (projected to UTM for accuracy),
  - builds a KDTree of the gridded points and finds the nearest grid point for each district centroid,
  - assigns the nearest grid cell's daily min/max values to the district for each day, and writes per-year `temp_csv/Temperature_{year}.csv` files.
  - This nearest-grid extrapolation is a pragmatic approach when grid coverage is sparse, but it assumes the nearest grid cell is representative of the district; treat values for extrapolated districts as lower-confidence compared to directly-covered districts.

- Grid alignment and resolution
  - The scripts assume the IMD gridded products use the documented lat/lon grid and that the `.GRD` binary ordering matches the reshape used in `bin_to_csv.py` and the test script `test_temp.py`. If IMD changes ordering/shape, outputs will be incorrect.

- Leap years and day counts
  - The code handles leap years by using a hardcoded `lpyears = [2016, 2020, 2024]`. If you process other years, update the list accordingly or compute leap years dynamically.

- Spatial join and point-to-district mapping
  - The approach maps grid cell center points to district polygons using a spatial join. Edge cases where a grid point falls on a polygon boundary depend on the geopandas predicate (e.g., `within` vs `intersects`). Verify `GeoJsons/Delhi_NCR_Districts.geojson` CRS matches the grid (EPSG:4326) before joining.

- Missing districts and incomplete coverage
  - Some districts may have zero grid points (if the region extent or grid resolution excludes them). The `process_temp.py` and `process_rainfall.py` scripts merge with the full district list so missing values appear as NaN; downstream analysis should handle these.

- Data provenance and versions
  - The `.url` files in `Sources Used/` point to IMD landing pages. For strict provenance, record the exact file names, download dates and checksums for each GRD/NetCDF file and add them to a manifest.

- Time and unit conventions
  - Rainfall in the NetCDF/CSV is assumed to be in millimeters (verify with IMD product metadata). Temperature is assumed to be in degrees Celsius. Confirm units in raw files before use.

- Binary coverage and extrapolation (Delhi NCR specific)
  - Using `test_temp.py` we observed that the min/max temperature binary (`.GRD`) files only contain grid points that fall within 3 Delhi-NCR district polygons (i.e., only 3 districts have direct grid coverage from the binary files). The rest of the Delhi-NCR districts are outside the sparse grid coverage present in those GRD files.
  - To obtain district-level daily minT/maxT for all districts, the repository includes an extrapolation routine `temp_csv/temp_extrap.py` which:
    - computes district centroids (projected to UTM for accuracy),
    - builds a KDTree of the gridded points and finds the nearest grid point for each district centroid,
    - assigns the nearest grid cell's daily min/max values to the district for each day, and writes per-year `temp_csv/Temperature_{year}.csv` files.
  - This nearest-grid extrapolation is a pragmatic approach when grid coverage is sparse, but it assumes the nearest grid cell is representative of the district; treat values for extrapolated districts as lower-confidence compared to directly-covered districts.

## Reproducibility and quick start

1. Create a Python virtual environment and install dependencies (see `requirements.txt`).

2. Place raw files in:
    - `minT_GRD/` and `maxT_GRD/` for temperature .GRD files
    - `rainfall_NetCDF/` for rainfall NetCDF files

3. Run the conversion scripts (order matters):
    - (optional) Convert NetCDF -> CSV: `python rainfall_NetCDF/nc_to_csv.py`
    - Convert GRD binaries -> per-year district CSVs: `python bin_to_csv.py`
    - Combine per-year CSVs: `python process_temp.py` and `python process_rainfall.py`
    - Standardize and compute anomalies: `python sd_temp.py` and `python sd_rainfall.py`

## Minimal dependencies

See `requirements.txt` for the main Python packages used in the repository. Install them with:

  powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt

## Project structure

Top-level files and folders relevant to running the pipeline:

- `bin_to_csv.py` - GRD binary -> CSV extractor for temperature
- `process_temp.py` - combine Temperature_{year}.csv -> monthly averages CSV
- `process_rainfall.py` - combine rainfall GeoJSONs -> monthly averages CSV
- `sd_temp.py`, `sd_rainfall.py` - standardization
- `temp_csv/`, `minT_csv/`, `maxT_csv/` - intermediate CSV outputs
- `temp_gjs/`, `rainfall_gjs/` - GeoJSON outputs
- `GeoJsons/Delhi_NCR_Districts.geojson` - district boundaries (Delhi NCR)

## Contact

- Hardik Chadha (<hardik.chadha@research.iiit.ac.in>)
- Arnav Sharma (<arnav.sharma@research.iiit.ac.in>)
- Jatin Agrawal (<jatin.agrawal@research.iiit.ac.in>)
