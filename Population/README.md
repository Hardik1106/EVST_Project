# Population Data Processing & Visualization

This folder contains population data and choropleth visualization scripts for Delhi NCR districts.

## Overview

Census 2011 and subsequent population estimates are processed to create district-level population datasets. Interactive choropleth maps show total, urban, and rural population distributions across NCR.

## Folder Structure

```
Population/
├── 2011-IndiaStateDistSbDist-0000.csv                  # Raw census data
├── A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.csv  # Census tables
├── District_Wise_Population.csv                        # Processed district population
├── NCR_District_Wise_Population.csv                    # NCR-specific population data
├── Delhi_NCR_Population_Data_Clean.csv                 # Cleaned final dataset
├── Delhi_NCR_Districts_final.geojson                   # District boundaries (copy)
├── step1_extract_delhi_ncr_clean.py                    # Data extraction & cleaning
├── step2_choropleth_viz.py                             # Choropleth map generation
├── plot.py                                             # Basic plotting utilities
├── filter_by_row.py, filter_csv.py                     # Filtering scripts
├── Delhi_NCR_Choropleth_Map.html                       # Combined population map
├── choropleth_total.html                               # Total population map
├── choropleth_urban.html                               # Urban population map
├── choropleth_rural.html                               # Rural population map
└── Delhi_NCR_Project_Summary.md                        # Summary documentation
```

## Data Sources

- **Source**: Census of India 2011
- **Agency**: Office of the Registrar General & Census Commissioner, India
- **Coverage**: All NCR districts (37 districts across Delhi, Haryana, UP, Rajasthan)
- **Variables**: Total population, urban population, rural population, households, area

## Processing Workflow

### 1. Extract & Clean Census Data (`step1_extract_delhi_ncr_clean.py`)

**Purpose**: Extract NCR districts from all-India census data and clean/normalize.

**How it works**:
- Reads raw census CSV files
- Filters to NCR districts (matches against district list)
- Normalizes district names (handles spelling variations)
- Separates total, urban, and rural population
- Computes population density

**Usage**:
```bash
python step1_extract_delhi_ncr_clean.py
```

**Output**:
- `Delhi_NCR_Population_Data_Clean.csv`
- Columns: `DISTRICT_NAME`, `Total_Population`, `Urban_Population`, `Rural_Population`, `Area_km2`, `Density`

---

### 2. Generate Choropleth Maps (`step2_choropleth_viz.py`)

**Purpose**: Create interactive choropleth maps showing population distribution.

**How it works**:
- Reads cleaned population CSV and district GeoJSON
- Merges population data with geometries
- Creates separate maps for total, urban, and rural population
- Applies quantile-based color scales
- Adds tooltips showing district name and population

**Usage**:
```bash
python step2_choropleth_viz.py
```

**Output**:
- `choropleth_total.html` - Total population map
- `choropleth_urban.html` - Urban population map
- `choropleth_rural.html` - Rural population map
- `Delhi_NCR_Choropleth_Map.html` - Combined overview map

**Features**:
- Color scale: Light → Dark (low → high population)
- Tooltip shows district name, population count
- Handles MultiPolygon districts
- Responsive zoom/pan

---

## Key Outputs

### CSV Files
- `Delhi_NCR_Population_Data_Clean.csv` - Final cleaned population dataset
  - Columns: DISTRICT_NAME, Total_Population, Urban_Population, Rural_Population, Area_km2, Density

### Interactive Maps
- `choropleth_total.html` - Total population distribution
- `choropleth_urban.html` - Urban population distribution
- `choropleth_rural.html` - Rural population distribution

Copies are also saved to `../Interactive Visualizations/` if generated there.

---

## Interpretation Guide

### Population Categories (NCR Context)
- **Mega districts** (>5 million): Delhi districts, Ghaziabad, Faridabad
- **Large** (1-5 million): Gurgaon, Gautam Buddha Nagar, Meerut
- **Medium** (0.5-1 million): Most Haryana/UP NCR districts
- **Small** (<0.5 million): Peripheral Rajasthan districts

### Urbanization Patterns
- **Highly urbanized** (>80% urban): Delhi, Faridabad, Gurgaon
- **Moderately urbanized** (40-80%): Ghaziabad, GB Nagar, Meerut
- **Rural-dominant** (<40% urban): Alwar, Bharatpur, outer UP/Haryana districts

---

## Common Issues

### Issue 1: District name mismatch
**Symptom**: Districts missing in choropleth output

**Solution**: Check district name normalization in `step1_extract_delhi_ncr_clean.py`. Common variations:
- "Gautam Buddha Nagar" vs "Gautambuddhanagar"
- "Gurugram" vs "Gurgaon"
- "Nuh" vs "Mewat"

---

### Issue 2: Population data outdated
**Symptom**: 2011 data doesn't reflect current reality

**Solution**: 
- Use Census 2021 data when officially released
- Apply annual growth rate estimates for intermediate years
- Note: Most official planning still uses Census 2011 baseline

---

### Issue 3: Missing rural/urban split
**Symptom**: Some districts show 0 for urban or rural

**Solution**: Small districts may be entirely classified as one type. Verify against official census tables.

---

## Technical Notes

### District Name Normalization
The cleaning script applies:
```python
# Common mappings
'gurgaon' → 'gurugram'
'gautambuddhanagar' → 'gautam buddha nagar'
'mewat' → 'nuh'
```

### Choropleth Color Scales
- Uses quantile-based binning (equal number of districts per color)
- Color ramps: YlOrRd (Yellow → Orange → Red) for population density
- Legends show bin ranges

### GeoJSON Integration
- Population CSV merged with `Delhi_NCR_Districts_final.geojson`
- Join key: `DISTRICT_NAME` (normalized to lowercase for matching)
- Handles MultiPolygon geometries

---

## Usage Example

```bash
# Step 1: Clean census data
python step1_extract_delhi_ncr_clean.py

# Step 2: Generate maps
python step2_choropleth_viz.py

# Output HTML files will be in current directory
# Open in browser to view interactive maps
```

---

## Extension Ideas

- Add 2021 Census data when available
- Compute decadal growth rates
- Overlay with urbanization/CVI data
- Add sex ratio, literacy rate from census
- Create population pyramid visualizations

---

## References

- Census of India 2011: https://censusindia.gov.in/
- NCR Planning Board: http://ncrpb.nic.in/

---

**Last Updated**: October 2025  
**Data Vintage**: Census 2011  
**Contact**: See main repository README
