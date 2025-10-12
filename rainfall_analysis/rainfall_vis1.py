import os
import folium
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from folium.plugins import TimestampedGeoJson
from branca.colormap import LinearColormap
from shapely.geometry import MultiPolygon

# --- Load GeoJSON boundary and data if not already present in this module ---
boundary_path = "GeoJsons/Delhi_NCR_Districts_final.geojson"
filled_csv = 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv'
base_csv = 'delhi_ncr_rainfall_monthly_avg_2013_2024.csv'

if 'boundary' not in globals():
    if not os.path.exists(boundary_path):
        raise FileNotFoundError(f"Boundary GeoJSON not found: {boundary_path}")
    boundary = gpd.read_file(boundary_path).to_crs(epsg=4326)

if os.path.exists(filled_csv):
    df_filled_final = pd.read_csv(filled_csv)
    # ensure TIME_ISO exists
    if 'TIME_ISO' not in df_filled_final.columns and 'YEAR' in df_filled_final.columns and 'MONTH' in df_filled_final.columns:
        df_filled_final['TIME'] = pd.to_datetime(df_filled_final['YEAR'].astype(str) + '-' + df_filled_final['MONTH'].astype(str) + '-01')
        df_filled_final['TIME_ISO'] = df_filled_final['TIME'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    df = df_filled_final.copy()
else:
    # fallback: load base CSV and assume the module that creates df_filled_final runs separately
    if not os.path.exists(base_csv):
        raise FileNotFoundError(f"Neither filled nor base CSV found: {filled_csv}, {base_csv}")
    df = pd.read_csv(base_csv)
    df['TIME'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')
    df['TIME_ISO'] = df['TIME'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    # If df_filled_final was not created by previous steps, fall back to using df as df_filled_final
    df_filled_final = df.copy()

# --- Normalize district name columns in boundary and data ---
name_col = None
for cand in ["NAME_2", "DISTRICT_NAME", "dtname", "dt_name", "district", "District"]:
    if cand in boundary.columns:
        name_col = cand
        break
if name_col is None:
    boundary['DISTRICT_NAME'] = boundary.index.astype(str)
    name_col = 'DISTRICT_NAME'
else:
    if name_col != 'DISTRICT_NAME':
        boundary = boundary.rename(columns={name_col: 'DISTRICT_NAME'})

boundary['DISTRICT_NAME_clean'] = boundary['DISTRICT_NAME'].astype(str).str.strip().str.lower()

if 'DISTRICT_NAME_clean' not in df_filled_final.columns and 'DISTRICT_NAME' in df_filled_final.columns:
    df_filled_final['DISTRICT_NAME_clean'] = df_filled_final['DISTRICT_NAME'].astype(str).str.strip().str.lower()

# Ensure YEAR and MONTH types exist
if 'YEAR' in df_filled_final.columns:
    df_filled_final['YEAR'] = df_filled_final['YEAR'].astype(int)
if 'MONTH' in df_filled_final.columns:
    df_filled_final['MONTH'] = df_filled_final['MONTH'].astype(int)

# --- Create color scale ---
max_rain = df_filled_final['RAINFALL'].max() if 'RAINFALL' in df_filled_final.columns else (df['RAINFALL'].max() if 'RAINFALL' in df.columns else 1.0)
colormap = LinearColormap(['white', 'blue', 'purple'], vmin=0, vmax=max_rain,
                          caption='Average Monthly Rainfall (mm)')

# --- Build features ---
features = []

# Group polygons by district (handles multi-polygon districts automatically)
for district_name_clean, polygons in boundary.groupby('DISTRICT_NAME_clean'):
    
    # Get rainfall data for this district (including filled values)
    district_data = df_filled_final[df_filled_final['DISTRICT_NAME_clean'] == district_name_clean]
    
    # Iterate over each polygon of the district (handle MultiPolygons)
    for _, polygon in polygons.iterrows():
        geom = polygon.geometry
        district_name = polygon['DISTRICT_NAME']

        # For each time step, create a feature for this polygon
        for _, row in district_data.iterrows():
            rainfall = row.get('RAINFALL')
            time_iso = row.get('TIME_ISO')

            # determine fill color: if missing, use grey
            if pd.isna(rainfall):
                fill_color = '#cccccc'
            else:
                try:
                    fill_color = colormap(float(rainfall))
                except Exception:
                    fill_color = '#cccccc'

            filled_tag = ''
            if row.get('FILLED'):
                method = row.get('FILLED_METHOD') if row.get('FILLED_METHOD') else 'filled'
                filled_tag = f' ({method})'

            popup_text = f"{district_name}<br>Rainfall: {'' if pd.isna(rainfall) else f'{float(rainfall):.2f} mm'}{filled_tag}"

            # If geometry is a MultiPolygon, create a feature per polygon part
            if isinstance(geom, MultiPolygon):
                for part in geom.geoms:
                    feature = {
                        "type": "Feature",
                        "geometry": part.__geo_interface__,
                        "properties": {
                            "time": time_iso,
                            "style": {"color": "black", "weight": 1, "fillColor": fill_color, "fillOpacity": 0.7},
                            "popup": popup_text
                        }
                    }
                    features.append(feature)
            else:
                feature = {
                    "type": "Feature",
                    "geometry": geom.__geo_interface__,
                    "properties": {
                        "time": time_iso,
                        "style": {"color": "black", "weight": 1, "fillColor": fill_color, "fillOpacity": 0.7},
                        "popup": popup_text
                    }
                }
                features.append(feature)
        
    # If no data for the district, we'll add it later as a grey layer

missing_mask = ~boundary['DISTRICT_NAME_clean'].isin(df_filled_final['DISTRICT_NAME_clean'])
missing_gdf = boundary[missing_mask]

# --- Create map centered on NCR ---
try:
    # use union_all() (preferred) instead of deprecated unary_union
    union = boundary.geometry.union_all()
    center = union.centroid
    center_lat, center_lon = center.y, center.x
except Exception:
    # fallback coordinates roughly near Delhi
    center_lat, center_lon = 28.7, 77.2

m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB positron")

# If there are missing districts, add them as a grey layer (so they appear behind the timestamped polygons)
if not missing_gdf.empty:
    def style_no_data(feature):
        return {
            'fillColor': 'lightgrey',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6
        }

    no_data_layer = folium.GeoJson(
        data=missing_gdf.__geo_interface__,
        name='No data (grey)',
        style_function=style_no_data,
        tooltip=folium.GeoJsonTooltip(fields=['DISTRICT_NAME'], aliases=['District:'])
    )
    no_data_layer.add_to(m)

# --- Add TimestampedGeoJson ---
TimestampedGeoJson(
    {"type": "FeatureCollection", "features": features},
    period='P1M',
    add_last_point=False,
    auto_play=False,
    loop=False,
    max_speed=1,
    loop_button=True,
    date_options='YYYY-MM',
    time_slider_drag_update=True
).add_to(m)

# --- Add color legend ---
colormap.add_to(m)

# --- Save map ---
m.save("delhi_ncr_rainfall_timeseries_allpolygons.html")
print("✅ Time-series map saved! All polygons, including multi-polygon districts, are included.")
