import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import TimestampedGeoJson
from branca.colormap import LinearColormap
import os
import numpy as np
from shapely.geometry import MultiPolygon

# --- Load GeoJSON boundary ---
boundary_path = "GeoJsons/Delhi_NCR_Districts_final.geojson"
if not os.path.exists(boundary_path):
    raise FileNotFoundError(f"Boundary GeoJSON not found: {boundary_path}")
boundary = gpd.read_file(boundary_path).to_crs(epsg=4326)

# --- Load monthly temperature CSV ---
df = pd.read_csv("delhi_ncr_temp_monthly_avg_2013_2024.csv")
df["MONTH"] = df["MONTH"].astype(int)

# --- Normalize district name columns in boundary and data (handle dtname)
name_col = None
for cand in ['dtname', 'NAME_2', 'DISTRICT_NAME', 'dt_name', 'district', 'District']:
    if cand in boundary.columns:
        name_col = cand
        break
if name_col is None:
    boundary['DISTRICT_NAME'] = boundary.index.astype(str)
else:
    if name_col != 'DISTRICT_NAME':
        boundary = boundary.rename(columns={name_col: 'DISTRICT_NAME'})

boundary['DISTRICT_NAME_clean'] = boundary['DISTRICT_NAME'].astype(str).str.strip().str.lower()

# Normalize CSV side
if 'DISTRICT_NAME' in df.columns:
    df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].astype(str).str.strip().str.lower()
else:
    # if CSV already used a cleaned name, try that
    if 'DISTRICT_NAME_clean' not in df.columns:
        raise ValueError('Temperature CSV missing DISTRICT_NAME column')

# Optional special-case mapping (if needed)
df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME_clean'].replace({'west': 'west delhi', 'west delhi': 'west delhi'})

# --- Prepare time columns ---
df["TIME"] = pd.to_datetime(df["YEAR"].astype(str) + "-" + df["MONTH"].astype(str) + "-01")
df["TIME_ISO"] = df["TIME"].dt.strftime("%Y-%m-%dT%H:%M:%S")

# --- Create output folder ---
os.makedirs("temp_vis_maps", exist_ok=True)

metrics = ["minT", "maxT", "avgT"]

for metric in metrics:
    print(f"🗺️ Generating map for {metric}...")

    # Define color scale, ignoring NaNs
    valid_values = df[metric].dropna()
    if valid_values.empty:
        print(f"⚠️ No valid data for {metric}, skipping...")
        continue
    vmin, vmax = valid_values.min(), valid_values.max()
    colormap = LinearColormap(["blue", "yellow", "red"], vmin=vmin, vmax=vmax,
                              caption=f"Average Monthly {metric.upper()} (°C)")

    features = []

    for district_name_clean, polygons in boundary.groupby('DISTRICT_NAME_clean'):
        # get canonical display name from first polygon
        polygons = polygons.reset_index(drop=True)
        district_name = polygons.loc[0, 'DISTRICT_NAME']

        # Match data rows for this district
        district_data = df[df['DISTRICT_NAME_clean'] == district_name_clean]

        if district_data.empty:
            # create a dummy gray polygon for all months so the district appears
            dummy_time = pd.date_range(start=f"{df['YEAR'].min()}-01-01", end=f"{df['YEAR'].max()}-12-01", freq='MS')
            for _, poly in polygons.iterrows():
                geom = poly.geometry
                for t in dummy_time:
                    if isinstance(geom, MultiPolygon):
                        for part in geom.geoms:
                            feature = {
                                'type': 'Feature',
                                'geometry': part.__geo_interface__,
                                'properties': {
                                    'time': t.strftime('%Y-%m-%dT%H:%M:%S'),
                                    'style': {'color': 'black', 'weight': 1, 'fillColor': '#cccccc', 'fillOpacity': 0.6},
                                    'popup': f"{district_name}<br>No data"
                                }
                            }
                            features.append(feature)
                    else:
                        feature = {
                            'type': 'Feature',
                            'geometry': geom.__geo_interface__,
                            'properties': {
                                'time': t.strftime('%Y-%m-%dT%H:%M:%S'),
                                'style': {'color': 'black', 'weight': 1, 'fillColor': '#cccccc', 'fillOpacity': 0.6},
                                'popup': f"{district_name}<br>No data"
                            }
                        }
                        features.append(feature)
            continue

        # Add features for each time point
        for _, row in district_data.iterrows():
            # determine geometry parts for this district
            for _, poly in polygons.iterrows():
                geom = poly.geometry

                # Handle NaNs gracefully
                val = row[metric] if not pd.isna(row[metric]) else None
                if val is None or pd.isna(val):
                    fill_color = '#cccccc'
                else:
                    try:
                        fill_color = colormap(float(val))
                    except Exception:
                        fill_color = '#cccccc'

                filled_tag = ''
                if 'FILLED' in row and row.get('FILLED'):
                    method = row.get('FILLED_METHOD') if row.get('FILLED_METHOD') else 'filled'
                    filled_tag = f' ({method})'

                popup_text = f"{district_name}<br>{metric.upper()}: {'' if val is None or pd.isna(val) else f'{float(val):.2f} °C'}{filled_tag}<br>{pd.to_datetime(row['TIME']).strftime('%b %Y') if 'TIME' in row else row.get('TIME_ISO')}"

                if isinstance(geom, MultiPolygon):
                    for part in geom.geoms:
                        feature = {
                            'type': 'Feature',
                            'geometry': part.__geo_interface__,
                            'properties': {
                                'time': row.get('TIME_ISO'),
                                'style': {'color': 'black', 'weight': 1, 'fillColor': fill_color, 'fillOpacity': 0.7 if val is not None and not pd.isna(val) else 0.6},
                                'popup': popup_text
                            }
                        }
                        features.append(feature)
                else:
                    feature = {
                        'type': 'Feature',
                        'geometry': geom.__geo_interface__,
                        'properties': {
                            'time': row.get('TIME_ISO'),
                            'style': {'color': 'black', 'weight': 1, 'fillColor': fill_color, 'fillOpacity': 0.7 if val is not None and not pd.isna(val) else 0.6},
                            'popup': popup_text
                        }
                    }
                    features.append(feature)

    # Map centered on NCR
    center = boundary.geometry.union_all().centroid
    m = folium.Map(location=[center.y, center.x], zoom_start=8, tiles="CartoDB positron")

    # Add timestamped layer
    TimestampedGeoJson(
        {"type": "FeatureCollection", "features": features},
        period="P1M",
        add_last_point=False,
        auto_play=False,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options="YYYY-MM",
        time_slider_drag_update=True
    ).add_to(m)

    # Add colormap
    colormap.add_to(m)

    # Save HTML
    output_html = f"temp_vis_maps/delhi_ncr_temp_timeseries_{metric}.html"
    m.save(output_html)
    print(f"✅ Saved: {output_html}")

print("\nAll temperature maps generated successfully!")
