import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import TimestampedGeoJson
from branca.colormap import LinearColormap

# --- 1. Assign stations to districts by spatial join ---
print("🔄 Loading data and assigning stations to districts...")
df = pd.read_csv('./filtered_ncr_districts.csv')
gdf = gpd.read_file('./delhi_ncr_final_districts.geojson').to_crs(epsg=4326)

# Create GeoDataFrame for stations
stations_gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.longitude, df.latitude),
    crs='EPSG:4326'
)

# Spatial join: assign each station to a district polygon
stations_gdf = gpd.sjoin(
    stations_gdf,
    gdf[['NAME_2', 'geometry']],
    how='left',
    predicate='within'
)
stations_gdf.rename(columns={'NAME_2': 'district_geojson'}, inplace=True)



# --- 2. Aggregate to monthly and yearly CSVs ---
print("📅 Aggregating data by month and year...")
stations_gdf['date'] = pd.to_datetime(stations_gdf['date'])
stations_gdf['month'] = stations_gdf['date'].dt.to_period('M')
stations_gdf['year'] = stations_gdf['date'].dt.year

# Monthly aggregation
monthly = stations_gdf.groupby(['district_geojson', 'month']).agg({
    'currentlevel': 'mean',
    'level_diff': 'mean'
}).reset_index()
monthly['TIME_ISO'] = monthly['month'].dt.to_timestamp().dt.strftime('%Y-%m-%dT%H:%M:%S')
monthly.to_csv('groundwater_monthly.csv', index=False)



# Yearly aggregation
yearly = stations_gdf.groupby(['district_geojson', 'year']).agg({
    'currentlevel': 'mean',
    'level_diff': 'mean'
}).reset_index()
yearly['TIME_ISO'] = pd.to_datetime(yearly['year'].astype(str) + '-01-01').dt.strftime('%Y-%m-%dT%H:%M:%S')
yearly.to_csv('groundwater_yearly.csv', index=False)

print(monthly[monthly['district_geojson'] == 'Faridabad'])
print(yearly[yearly['district_geojson'] == 'Faridabad'])

print("Districts in CSV:", sorted(stations_gdf['district_geojson'].dropna().unique()))
print("Districts in GeoJSON:", sorted(gdf['NAME_2'].unique()))
csv_districts = set(stations_gdf['district_geojson'].dropna().unique())
geojson_districts = set(gdf['NAME_2'].unique())
print("Districts in CSV but not GeoJSON:", csv_districts - geojson_districts)
print("Districts in GeoJSON but not CSV:", geojson_districts - csv_districts)

# --- 3. Visualization function ---
def make_map(df, gdf, filename, title, date_options):
    vmin = df['currentlevel'].min()
    vmax = df['currentlevel'].max()
    # Green for shallow (good), red for deep (bad)
    colormap = LinearColormap(['green', 'lightgreen', 'yellow', 'orange', 'red'],
                             vmin=vmin, vmax=vmax,
                             caption='Groundwater Current Level (meters)')
    features = []
    for _, polygon in gdf.iterrows():
        district_name = polygon['NAME_2']
        geom = polygon.geometry
        district_data = df[df['district_geojson'] == district_name]
        for _, row in district_data.iterrows():
            feature = {
                "type": "Feature",
                "geometry": geom.__geo_interface__,
                "properties": {
                    "time": row['TIME_ISO'],
                    "style": {
                        "color": "black",
                        "weight": 1,
                        "fillColor": colormap(row['currentlevel']),
                        "fillOpacity": 0.7
                    },
                    "popup": f"<b>{district_name}</b><br>"
                             f"Date: {row['TIME_ISO'][:10]}<br>"
                             f"Groundwater Level: {row['currentlevel']:.2f}m<br>"
                             f"Level Change: {row['level_diff']:+.2f}m"
                }
            }
            features.append(feature)
    center = gdf.geometry.union_all().centroid
    m = folium.Map(location=[center.y, center.x], zoom_start=8, tiles="CartoDB positron")
    TimestampedGeoJson(
        {"type": "FeatureCollection", "features": features},
        period='P1Y' if date_options == 'YYYY' else 'P1M',
        add_last_point=False,
        auto_play=False,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options=date_options,
        time_slider_drag_update=True
    ).add_to(m)
    colormap.add_to(m)
    title_html = f'<h3 align="center" style="font-size:16px"><b>{title}</b></h3>'
    m.get_root().html.add_child(folium.Element(title_html))
    m.save(filename)
    print(f"✅ Saved map: {filename}")
# --- 4. Make monthly and yearly maps ---
print("🗺️ Creating monthly map...")
make_map(monthly, gdf, 'ncr_groundwater_timeseries_monthly.html',
         'NCR Groundwater Levels Time Series (Monthly)', 'YYYY-MM')

print("🗺️ Creating yearly map...")
make_map(yearly, gdf, 'ncr_groundwater_timeseries_yearly.html',
         'NCR Groundwater Levels Time Series (Yearly)', 'YYYY')

print("🎉 All done! Check the HTML files for interactive maps.")