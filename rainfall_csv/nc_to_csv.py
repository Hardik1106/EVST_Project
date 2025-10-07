import xarray as xr
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Paths
file_path = "rainfall_NetCDF/RF25_ind"
geojson_path = "GeoJsons/Delhi_NCR_Districts.geojson"
output_dir = "rainfall_csv/"

# Load GeoJSON
districts = gpd.read_file(geojson_path)
districts = districts.to_crs(epsg=4326)

# ✅ Standardize the district name column
if "NAME_2" in districts.columns:
    districts = districts.rename(columns={"NAME_2": "DISTRICT_NAME"})  # 👈 rename to a common name

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
    joined = gpd.sjoin(gdf, districts, how="inner", predicate="within")
    
    # ✅ Check if TIME exists (some NetCDFs might not have it)
    if "TIME" in joined.columns:
        agg = joined.groupby(["DISTRICT_NAME", "TIME"])["RAINFALL"].mean().reset_index()
    else:
        agg = joined.groupby(["DISTRICT_NAME"])["RAINFALL"].mean().reset_index()
    
    agg.to_csv(f"{output_dir}delhi_rainfall_districts_{year}.csv", index=False)

print("✅ All done!")
