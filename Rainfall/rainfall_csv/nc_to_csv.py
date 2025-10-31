import xarray as xr
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Paths
file_path = "rainfall_NetCDF/RF25_ind"
geojson_path = "GeoJsons/Delhi_NCR_Districts_final.geojson"
output_dir = "rainfall_csv/"

# Load GeoJSON
districts = gpd.read_file(geojson_path)
districts = districts.to_crs(epsg=4326)

# ✅ Standardize the district name column
# Normalize common district name fields to `DISTRICT_NAME`
possible_name_cols = [c for c in districts.columns]
name_col = None
for cand in ["DISTRICT_NAME", "NAME_2", "dtname", "dt_name", "district", "District"]:
    if cand in possible_name_cols:
        name_col = cand
        break
if name_col and name_col != "DISTRICT_NAME":
    districts = districts.rename(columns={name_col: "DISTRICT_NAME"})
elif not name_col:
    # If no obvious name column exists, create one from index to avoid KeyErrors later
    districts["DISTRICT_NAME"] = districts.index.astype(str)

# Define Delhi NCR bounding box
lat_bounds = slice(27.5, 29.5)
lon_bounds = slice(76.5, 78.5)

years = [str(y) for y in range(2013, 2024)]

for year in years:
    print(f"Processing {year}...")
    
    ds = xr.open_dataset(f"{file_path}{year}_rfp25.nc")
    rain = ds["RAINFALL"]
    delhi_rain = rain.sel(LATITUDE=lat_bounds, LONGITUDE=lon_bounds)
    
    df = delhi_rain.to_dataframe().reset_index().dropna(subset=["RAINFALL"])
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["LONGITUDE"], df["LATITUDE"]),
        crs="EPSG:4326"
    )
    
    # Spatial join
    # use 'intersects' to be robust for boundary points; fall back to 'within' if needed
    try:
        joined = gpd.sjoin(gdf, districts, how="inner", predicate="intersects")
    except Exception:
        joined = gpd.sjoin(gdf, districts, how="inner", predicate="within")
    
    # Quick sanity: ensure DISTRICT_NAME exists after the join
    if "DISTRICT_NAME" not in joined.columns:
        print("Warning: 'DISTRICT_NAME' column not found in joined GeoDataFrame. Available columns:", joined.columns.tolist())
    
    # ✅ Check if a time-like column exists (case-insensitive)
    time_col = None
    for c in joined.columns:
        if str(c).lower() == "time":
            time_col = c
            break

    if time_col is not None:
        agg = joined.groupby(["DISTRICT_NAME", time_col])["RAINFALL"].mean().reset_index()
        # normalize column name to TIME for downstream consistency
        if time_col != "TIME":
            agg = agg.rename(columns={time_col: "TIME"})
    else:
        agg = joined.groupby(["DISTRICT_NAME"])["RAINFALL"].mean().reset_index()

    # Ensure output directory exists
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    agg.to_csv(f"{output_dir}delhi_rainfall_districts_{year}.csv", index=False)

print("✅ All done!")
