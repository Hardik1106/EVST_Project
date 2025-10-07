import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import TimestampedGeoJson
from branca.colormap import LinearColormap

# --- Load GeoJSON boundary ---
boundary_path = "GeoJsons/Delhi_NCR_Districts.geojson"
boundary = gpd.read_file(boundary_path)
boundary = boundary.to_crs(epsg=4326)

# --- Load monthly rainfall CSV ---
df = pd.read_csv("delhi_ncr_rainfall_monthly_avg_2013_2024.csv")
df['TIME'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str) + '-01')
df['TIME_ISO'] = df['TIME'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# --- Create color scale ---
max_rain = df['RAINFALL'].max()
colormap = LinearColormap(['white', 'blue', 'purple'], vmin=0, vmax=max_rain,
                          caption='Average Monthly Rainfall (mm)')

# --- Normalize names for matching ---
boundary['DISTRICT_NAME_clean'] = boundary['NAME_2'].str.strip().str.lower()
df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].str.strip().str.lower()

# --- Build features ---
features = []

# Group polygons by district (handles multi-polygon districts automatically)
for district_name_clean, polygons in boundary.groupby('DISTRICT_NAME_clean'):
    
    # Get rainfall data for this district
    district_data = df[df['DISTRICT_NAME_clean'] == district_name_clean]
    
    # Iterate over each polygon of the district
    for _, polygon in polygons.iterrows():
        geom = polygon.geometry
        district_name = polygon['NAME_2']
        
        # For each time step, create a feature for this polygon
        for _, row in district_data.iterrows():
            rainfall = row['RAINFALL']
            time_iso = row['TIME_ISO']
            feature = {
                "type": "Feature",
                "geometry": geom.__geo_interface__,
                "properties": {
                    "time": time_iso,
                    "style": {"color": "black", "weight": 1,
                              "fillColor": colormap(rainfall), "fillOpacity": 0.7},
                    "popup": f"{district_name}<br>Rainfall: {rainfall:.2f} mm"
                }
            }
            features.append(feature)

# --- Create map centered on NCR ---
center = boundary.geometry.union_all().centroid
m = folium.Map(location=[center.y, center.x], zoom_start=8, tiles="CartoDB positron")

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
