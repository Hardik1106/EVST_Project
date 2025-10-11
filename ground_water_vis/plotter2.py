import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import TimestampedGeoJson
from branca.colormap import LinearColormap
from shapely.geometry import Polygon, MultiPolygon

# --- 1. Assign stations to districts by spatial join ---
print("🔄 Loading data and assigning stations to districts...")
df = pd.read_csv('./filtered_ncr_districts.csv')
gdf = gpd.read_file('../GeoJsons/Delhi_NCR_Districts_final.geojson').to_crs(epsg=4326)

# Standardize district names
gdf['dtname'] = gdf['dtname'].str.strip()
df['district_geojson'] = df.get('district_geojson', pd.Series([None]*len(df))).astype(str).str.strip()

stations_gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.longitude, df.latitude),
    crs='EPSG:4326'
)

stations_gdf = gpd.sjoin(
    stations_gdf,
    gdf[['dtname', 'geometry']],
    how='left',
    predicate='within'
)
# Drop the original 'district_geojson' from CSV if present
if 'district_geojson' in stations_gdf.columns:
    stations_gdf = stations_gdf.drop(columns=['district_geojson'])
# Use the one from GeoJSON
stations_gdf = stations_gdf.rename(columns={'dtname': 'district_geojson'})

# --- 2. Aggregate to monthly and yearly CSVs ---
print("📅 Aggregating data by month and year...")
stations_gdf['date'] = pd.to_datetime(stations_gdf['date'])
stations_gdf['month'] = stations_gdf['date'].dt.to_period('M')
stations_gdf['year'] = stations_gdf['date'].dt.year

monthly = stations_gdf.groupby(['district_geojson', 'month']).agg({
    'currentlevel': 'mean',
    'level_diff': 'mean'
}).reset_index()
monthly['TIME_ISO'] = monthly['month'].dt.to_timestamp().dt.strftime('%Y-%m-%dT%H:%M:%S')
monthly.to_csv('ncr_groundwater_monthly.csv', index=False)

yearly = stations_gdf.groupby(['district_geojson', 'year']).agg({
    'currentlevel': 'mean',
    'level_diff': 'mean'
}).reset_index()
yearly['TIME_ISO'] = pd.to_datetime(yearly['year'].astype(str) + '-01-01').dt.strftime('%Y-%m-%dT%H:%M:%S')
yearly.to_csv('ncr_groundwater_yearly.csv', index=False)

# --- Interpolate missing Delhi districts ---
delhi_parts = ['East Delhi', 'South Delhi', 'South East Delhi', 'North East Delhi', 'Shahdara']

def interpolate_delhi_parts(df):
    nd = df[df['district_geojson'] == 'New Delhi']
    wd = df[df['district_geojson'] == 'West Delhi']
    merged = pd.merge(nd, wd, on='TIME_ISO', suffixes=('_nd', '_wd'))
    keep_cols = ['district_geojson', 'currentlevel', 'level_diff', 'TIME_ISO']
    # Add 'month' or 'year' if present
    for col in ['month', 'year']:
        if col in merged.columns:
            keep_cols.append(col)
    for part in delhi_parts:
        part_df = merged.copy()
        part_df['district_geojson'] = part
        part_df['currentlevel'] = part_df[['currentlevel_nd', 'currentlevel_wd']].mean(axis=1)
        part_df['level_diff'] = part_df[['level_diff_nd', 'level_diff_wd']].mean(axis=1)
        part_df = part_df[keep_cols]
        df = pd.concat([df, part_df], ignore_index=True)
    return df

monthly = interpolate_delhi_parts(monthly)
yearly = interpolate_delhi_parts(yearly)

# --- 3. Fixed Visualization function - Explode MultiPolygons ---
def make_map(df, gdf, filename, title, date_options):
    vmin = df['currentlevel'].min()
    vmax = df['currentlevel'].max()
    colormap = LinearColormap(['green', 'lightgreen', 'yellow', 'orange', 'red'],
                             vmin=vmin, vmax=vmax,
                             caption='Groundwater Current Level (meters)')
    features = []
    time_steps = sorted(df['TIME_ISO'].unique())
    
    print(f"\n🔍 Processing {len(time_steps)} time steps...")
    
    for time in time_steps:
        df_time = df[df['TIME_ISO'] == time]
        
        for _, polygon in gdf.iterrows():
            district_name = polygon['dtname']
            geom = polygon.geometry
            
            # Get data for this district
            row = df_time[df_time['district_geojson'] == district_name]
            
            if not row.empty:
                row = row.iloc[0]
                fill_color = colormap(row['currentlevel'])
                popup = (f"<b>{district_name}</b><br>"
                         f"Date: {row['TIME_ISO'][:10]}<br>"
                         f"Groundwater Level: {row['currentlevel']:.2f}m<br>"
                         f"Level Change: {row['level_diff']:+.2f}m")
            else:
                fill_color = "#cccccc"
                popup = f"<b>{district_name}</b><br>No data for this period."
            
            # CRITICAL FIX: Handle MultiPolygon by exploding into individual Polygons
            if isinstance(geom, MultiPolygon):
                # For MultiPolygon, create a separate feature for each polygon part
                for poly in geom.geoms:
                    feature = {
                        "type": "Feature",
                        "geometry": poly.__geo_interface__,
                        "properties": {
                            "time": time,
                            "style": {
                                "color": "black",
                                "weight": 1,
                                "fillColor": fill_color,
                                "fillOpacity": 0.7
                            },
                            "popup": popup
                        }
                    }
                    features.append(feature)
            else:
                # For regular Polygon, add as-is
                feature = {
                    "type": "Feature",
                    "geometry": geom.__geo_interface__,
                    "properties": {
                        "time": time,
                        "style": {
                            "color": "black",
                            "weight": 1,
                            "fillColor": fill_color,
                            "fillOpacity": 0.7
                        },
                        "popup": popup
                    }
                }
                features.append(feature)
    
    print(f"✅ Created {len(features)} features for visualization")
    
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
    # title_html = f'<h3 align="center" style="font-size:16px"><b>{title}</b></h3>'
    # m.get_root().html.add_child(folium.Element(title_html))
    m.save(filename)
    print(f"✅ Saved map: {filename}")

# Debug info
print("\n🔍 Checking MultiPolygon districts:")
for district in ['Faridabad', 'Rewari', 'Bharatpur']:
    geom = gdf[gdf['dtname'] == district].geometry.iloc[0]
    data_count = len(yearly[yearly['district_geojson'] == district])
    print(f"{district}:")
    print(f"  - Geometry type: {geom.geom_type}")
    print(f"  - Number of parts: {len(geom.geoms) if isinstance(geom, MultiPolygon) else 1}")
    print(f"  - Data records: {data_count}")
    if data_count > 0:
        avg = yearly[yearly['district_geojson'] == district]['currentlevel'].mean()
        print(f"  - Avg groundwater level: {avg:.2f}m")

unmatched = stations_gdf[stations_gdf['district_geojson'].isna()]
print(f"\n⚠️ Unmatched points (no district): {len(unmatched)}")

print("\n🗺️ Creating monthly map...")
make_map(monthly, gdf, 'ncr_groundwater_timeseries_monthly.html',
         'NCR Groundwater Levels Time Series (Monthly)', 'YYYY-MM')

print("\n🗺️ Creating yearly map...")
make_map(yearly, gdf, 'ncr_groundwater_timeseries_yearly.html',
         'NCR Groundwater Levels Time Series (Yearly)', 'YYYY')

print("\n🎉 All done! Check the HTML files for interactive maps.")