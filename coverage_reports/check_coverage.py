import os
import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point


def normalize_district_names(gdf):
    possible = [c for c in gdf.columns]
    name_col = None
    for cand in ["DISTRICT_NAME", "NAME_2", "dtname", "dt_name", "district", "District"]:
        if cand in possible:
            name_col = cand
            break
    if name_col and name_col != "DISTRICT_NAME":
        gdf = gdf.rename(columns={name_col: "DISTRICT_NAME"})
    if "DISTRICT_NAME" not in gdf.columns:
        gdf["DISTRICT_NAME"] = gdf.index.astype(str)
    gdf["DISTRICT_NAME_clean"] = gdf["DISTRICT_NAME"].astype(str).str.strip().str.lower()
    return gdf


def report_netCDF_rainfall_coverage(nc_dir="rainfall_NetCDF", districts_path="GeoJsons/Delhi_NCR_Districts_final.geojson", out_dir="coverage_reports"):
    os.makedirs(out_dir, exist_ok=True)
    districts = gpd.read_file(districts_path).to_crs(epsg=4326)
    districts = normalize_district_names(districts)

    years = [y for y in range(2013, 2025)]
    summary_rows = []

    for year in years:
        nc_path = os.path.join(nc_dir, f"RF25_ind{year}_rfp25.nc")
        if not os.path.exists(nc_path):
            print(f"NetCDF not found for {year}: {nc_path}, skipping")
            continue

        print(f"Processing rainfall NetCDF {nc_path} ...")
        ds = xr.open_dataset(nc_path)

        # find rainfall var and lat/lon coords
        var_name = None
        for v in ds.data_vars:
            if "rain" in v.lower() or "rf" == v.lower() or "rf" in v.lower():
                var_name = v
                break
        if var_name is None:
            print(f"No rainfall variable found in {nc_path}, available vars: {list(ds.data_vars)}")
            continue

        # coordinate names
        lat_name = None
        lon_name = None
        for c in ds.coords:
            cl = c.lower()
            if "lat" in cl:
                lat_name = c
            if "lon" in cl:
                lon_name = c
        if lat_name is None or lon_name is None:
            print(f"Could not detect lat/lon coords in {nc_path} (coords: {list(ds.coords)})")
            continue

        rain = ds[var_name]

        # subset to Delhi NCR bounding box (same as pipeline)
        lat_bounds = slice(27.5, 29.5)
        lon_bounds = slice(76.5, 78.5)
        try:
            sel = rain.sel({lat_name: lat_bounds, lon_name: lon_bounds})
        except Exception:
            # try lowercase coord names
            sel = rain.sel({lat_name: lat_bounds, lon_name: lon_bounds})

        df = sel.to_dataframe().reset_index()
        # find any rows where rainfall is not nan
        if "RAINFALL" in df.columns:
            rain_col = "RAINFALL"
        else:
            rain_col = var_name

        df = df.dropna(subset=[rain_col])
        if df.empty:
            print(f"No rainfall data inside bounding box for {year}")
            continue

        pts = gpd.GeoDataFrame(df[[lat_name, lon_name]].rename(columns={lat_name: 'LATITUDE', lon_name: 'LONGITUDE'}),
                               geometry=gpd.points_from_xy(df[lon_name], df[lat_name]), crs="EPSG:4326")

        joined = gpd.sjoin(pts.drop_duplicates(['LATITUDE', 'LONGITUDE']), districts, how='inner', predicate='intersects')

        counts = joined['DISTRICT_NAME'].value_counts().rename_axis('DISTRICT_NAME').reset_index(name='grid_point_count')
        # merge with full district list to show zeros
        all_dists = districts[['DISTRICT_NAME']].drop_duplicates()
        counts_full = all_dists.merge(counts, on='DISTRICT_NAME', how='left').fillna(0)

        missing = counts_full[counts_full['grid_point_count'] == 0]['DISTRICT_NAME'].tolist()
        print(f"Year {year}: districts with zero grid points (netCDF): {len(missing)}")

        counts_full.to_csv(os.path.join(out_dir, f"rainfall_coverage_{year}.csv"), index=False)

        summary_rows.append({
            'year': year,
            'districts_with_coverage': int((counts_full['grid_point_count'] > 0).sum()),
            'districts_without_coverage': int((counts_full['grid_point_count'] == 0).sum())
        })

    pd.DataFrame(summary_rows).to_csv(os.path.join(out_dir, 'rainfall_coverage_summary.csv'), index=False)
    print(f"Rainfall coverage reports written to {out_dir}")


def report_grd_temp_coverage(grd_dir='minT_GRD', districts_path='GeoJsons/Delhi_NCR_Districts_final.geojson', out_dir='coverage_reports'):
    os.makedirs(out_dir, exist_ok=True)
    districts = gpd.read_file(districts_path).to_crs(epsg=4326)
    districts = normalize_district_names(districts)

    years = [y for y in range(2013, 2025)]
    n_lat, n_lon = 31, 31
    lats = np.linspace(6.5, 38.5, n_lat)
    lons = np.linspace(66.5, 100.0, n_lon)
    lat_grid, lon_grid = np.meshgrid(lats, lons)
    # create points for grid centers
    coords = pd.DataFrame({'LATITUDE': lat_grid.ravel(), 'LONGITUDE': lon_grid.ravel()})
    pts = gpd.GeoDataFrame(coords, geometry=gpd.points_from_xy(coords['LONGITUDE'], coords['LATITUDE']), crs='EPSG:4326')
    # limit to Delhi bounding box
    pts = pts[(pts['LATITUDE'] >= 27.5) & (pts['LATITUDE'] <= 29.5) & (pts['LONGITUDE'] >= 76.5) & (pts['LONGITUDE'] <= 78.5)]

    joined_pts = gpd.sjoin(pts, districts, how='inner', predicate='intersects')
    # The joined_pts tells which grid indices fall into which districts; now check per year if GRD files exist
    summary_rows = []
    for year in years:
        file_path = os.path.join(grd_dir, f"Mintemp_MinT_{year}.GRD")
        if not os.path.exists(file_path):
            print(f"GRD file not found for {year}: {file_path}, skipping")
            continue
        # We just need to know which districts have any grid point (spatially)
        counts = joined_pts['DISTRICT_NAME'].value_counts().rename_axis('DISTRICT_NAME').reset_index(name='grid_point_count')
        all_dists = districts[['DISTRICT_NAME']].drop_duplicates()
        counts_full = all_dists.merge(counts, on='DISTRICT_NAME', how='left').fillna(0)
        missing = counts_full[counts_full['grid_point_count'] == 0]['DISTRICT_NAME'].tolist()
        print(f"Year {year}: districts with zero grid points (GRD grid centers): {len(missing)}")
        counts_full.to_csv(os.path.join(out_dir, f"minT_grid_coverage_{year}.csv"), index=False)
        summary_rows.append({'year': year, 'districts_with_coverage': int((counts_full['grid_point_count'] > 0).sum()), 'districts_without_coverage': int((counts_full['grid_point_count'] == 0).sum())})

    pd.DataFrame(summary_rows).to_csv(os.path.join(out_dir, 'minT_grid_coverage_summary.csv'), index=False)
    print(f"GRD coverage reports written to {out_dir}")


if __name__ == '__main__':
    # produce both reports
    report_netCDF_rainfall_coverage()
    report_grd_temp_coverage()
