# EVST_Project

This repository contains code and processed data for analysis and visualization of daily and monthly temperature and rainfall for the Delhi National Capital Region (NCR) across 2013–2024. The project converts IMD gridded binary/NetCDF products to district-level CSVs, computes monthly averages, and standardizes the series for anomaly/ trend analysis.

## Contents

- `minT_GRD/`, `maxT_GRD/` - original IMD binary/GRD files for min/max temperature (one file per year).
- `minT_csv/`, `maxT_csv/` - district-level CSV outputs created by the extraction scripts (one CSV per year).
- `rainfall_NetCDF/` - IMD rainfall NetCDF files (one file per year).
- `rainfall_csv/` - intermediate CSV conversions from NetCDF to point/district values.
- `rainfall_gjs/`, `temp_gjs/` - GeoJSON outputs (district-level) per year.
- `rainfall_sd_gjs/`, `temp_sd_gjs/` - standardized GeoJSONs (z-scores) for mapping anomalies.
- `temp_csv/` - processed temperature CSVs used to compute monthly district averages (Temperature_{year}.csv).
- `GeoJsons/Delhi_NCR_Districts.geojson` - boundary file with district polygons for Delhi NCR used for spatial extraction.
- `process_temp.py`, `process_rainfall.py` - scripts to aggregate per-district monthly averages across years.
- `sd_temp.py`, `sd_rainfall.py` - scripts to compute global and district-wise standardized (z-score) series.
- `bin_to_csv.py`, `nc_to_csv.py`, `nc_to_csv_24.py`, `csv_to_gjs.py`, `sd_rainfall_gjs.py`, `sd_temp_gjs.py` - assorted helper scripts used in the binary/NetCDF to CSV/GeoJSON conversion (see script header docstrings for details).

## Metadata & Data sources

The primary data used in this project are published by the India Meteorological Department (IMD) and the National Capital Region Planning Board (NCRPB) for boundary definitions. The exact sources used (saved under `Sources Used/`) are:

1. Delhi NCR constituent districts / definition (NCRPB)
    - Agency: National Capital Region Planning Board (NCRPB)
    - Source: NCRPB constituent districts page [NCRPB definition][ncrpb-url]

2. Rainfall (IMD high spatial resolution rainfall products)
    - Agency: India Meteorological Department (IMD)
    - Source: IMD rainfall NetCDF product landing page [IMD rainfall][imd-rain-url]

3. Maximum temperature (IMD daily maximum temperature grid)
    - Agency: India Meteorological Department (IMD)
    - Source: IMD max temperature grid product page [IMD maxT][imd-maxt-url]

4. Minimum temperature (IMD daily minimum temperature grid)
    - Agency: India Meteorological Department (IMD)
    - Source: IMD min temperature grid product page [IMD minT][imd-mint-url]

If you need citation-ready metadata (DOIs, version numbers or file checksums) we can add them for each file later — those are not included in the saved `.url` shortcuts.

## Processing workflow (high-level)

This project follows a reproducible pipeline from raw gridded sources to district-level monthly standardized outputs. Steps and primary scripts:

1. Data acquisition (manual / IMD website downloads)
    - IMD GRD/NetCDF files for each year are placed into `minT_GRD/`, `maxT_GRD/`, and `rainfall_NetCDF/`.

2. Binary / NetCDF -> CSV extraction
    - Temperature GRD binary conversion: `bin_to_csv.py` (reads `MinTemp_MinT_{year}.GRD` and `Maxtemp_MaxT_{year}.GRD`, maps grid points to district polygons in `GeoJsons/Delhi_NCR_Districts.geojson`, and outputs per-year district CSVs into `minT_csv/` and `maxT_csv/`).
    - Rainfall NetCDF conversion: `rainfall_NetCDF/nc_to_csv.py` (or `rainfall_csv/nc_to_csv_24.py`) converts daily rainfall NetCDF to point/district CSVs and saves GeoJSONs under `rainfall_gjs/`.

3. Monthly averaging and combining across years
    - Temperature monthly averages: `process_temp.py` reads the per-year `Temperature_{year}.csv` in `temp_csv/`, computes district-by-month averages (minT/maxT and avgT), and combines all years into `delhi_ncr_temp_monthly_avg_2013_2024.csv`.
    - Rainfall monthly averages: `process_rainfall.py` aggregates district-by-month mean rainfall from GeoJSONs saved in `rainfall_gjs/` and writes `delhi_ncr_rainfall_monthly_avg_2013_2024.csv`.

4. Standardization and anomaly calculation
    - `sd_temp.py` computes global z-scores for `minT`, `maxT` and `avgT` and district-wise standardized values saved to `delhi_ncr_temp_monthly_avg_standardized.csv`.
    - `sd_rainfall.py` computes global and district-wise standardized rainfall series and writes `delhi_ncr_rainfall_monthly_avg_standardized.csv`.

5. GeoJSON generation for mapping
    - `csv_to_gjs.py` (in `temp_gjs/` and `rainfall_gjs/`) converts the combined CSVs into per-year GeoJSONs suitable for mapping time-series and anomalies.
    - Standardized GeoJSONs are saved under `temp_sd_gjs/` and `rainfall_sd_gjs/` for visualization.

6. Analysis & visualization
    - Scripts in `temp_analysis/` and `rainfall_analysis/` create timeseries, anomaly plots and district trend slopes. Output maps are saved under `*_vis_maps/`.

## Script-level details and how to run

Below are the main runnable scripts and a brief description and minimal usage examples.

- `process_temp.py`
  - Purpose: combine per-year temperature CSVs to create the monthly district averages CSV.
  - Inputs: `temp_csv/Temperature_{year}.csv` files, `GeoJsons/Delhi_NCR_Districts.geojson`
- Output: `delhi_ncr_temp_monthly_avg_2013_2024.csv`
- Run: python process_temp.py

- `process_rainfall.py`
- Purpose: aggregate district/month mean rainfall from GeoJSONs to one combined CSV.
- Inputs: `rainfall_gjs/delhi_ncr_rainfall_{year}.geojson`
- Output: `delhi_ncr_rainfall_monthly_avg_2013_2024.csv`
- Run: python process_rainfall.py

- `sd_temp.py`, `sd_rainfall.py`
  - Purpose: compute z-scores (global and district-wise) and save standardized CSVs.
- Input: combined monthly CSVs created by `process_*` scripts.
- Run: python sd_temp.py

- `bin_to_csv.py` / `nc_to_csv.py` / `nc_to_csv_24.py` / `csv_to_gjs.py`
- Purpose: lower-level extraction scripts for converting gridded data to point/district values and GeoJSONs.
- Note: these scripts rely on consistent grid definitions (lat/lon arrays), correct shape for binary `.GRD` files, and a matching boundary GeoJSON. Inspect the top of each script for input paths and grid parameters.

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

[ncrpb-url]: https://ncrpb.nic.in/ncrconstituent.html
[imd-rain-url]: https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html
[imd-maxt-url]: https://imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html
[imd-mint-url]: https://imdpune.gov.in/cmpg/Griddata/Min_1_Bin.html
