import pandas as pd
import geopandas as gpd
import folium
from branca.colormap import LinearColormap

# Load population data
pop_df = pd.read_csv('NCR_District_Wise_Population.csv')
pop_df['Name'] = pop_df['Name'].str.strip().str.lower()
pop_df['Level'] = pop_df['Level'].str.strip()
pop_df['TRU'] = pop_df['TRU'].str.strip().str.lower()

# Load GeoJSON
gdf = gpd.read_file('../GeoJsons/Delhi_NCR_Districts_final.geojson')
gdf['dtname'] = gdf['dtname'].str.strip().str.lower()

# Calculate percentage
pop_df['P_06_pct'] = pop_df['P_06'] / pop_df['TOT_P'] * 100

# Pivot so each district has columns for Total, Urban, Rural using TRU column
pivot_df = pop_df.pivot_table(index='Name', columns='TRU', values='P_06_pct').reset_index()

# Merge with GeoDataFrame
merged_gdf = gdf.merge(pivot_df, left_on='dtname', right_on='Name', how='left')

def make_choropleth(gdf, value_col, title, filename):
    # Create colormap
    values = gdf[value_col].dropna()
    if len(values) > 0:
        vmin, vmax = values.min(), values.max()
    else:
        vmin, vmax = 0, 1
    
    colormap = LinearColormap(['#ffffcc', '#a1dab4', '#41b6c4', '#225ea8', '#081d58'],
                             vmin=vmin, vmax=vmax,
                             caption=title)
    
    m = folium.Map(location=[28.6, 77.2], zoom_start=8, tiles="CartoDB positron")
    
    # Create features with popups (similar to plotter2.py approach)
    for _, row in gdf.iterrows():
        district_name = row['dtname']
        geom = row.geometry
        value = row.get(value_col, None)
        
        if pd.notna(value):
            fill_color = colormap(value)
            popup = f"<b>{district_name.title()}</b><br>{title}: {value:.2f}%"
        else:
            fill_color = "#cccccc"
            popup = f"<b>{district_name.title()}</b><br>No data available"
        
        # Add GeoJson feature with popup (like plotter2.py)
        folium.GeoJson(
            geom,
            style_function=lambda x, fill_color=fill_color: {
                "color": "black",
                "weight": 1,
                "fillColor": fill_color,
                "fillOpacity": 0.7
            },
            popup=folium.Popup(popup, max_width=300)
        ).add_to(m)
    
    # Add colormap
    colormap.add_to(m)
    
    # Add title
    title_html = (
        f'<div style="text-align:center; margin-top:5px; margin-bottom:0px;">'
        f'<h4 style="font-size:15px; font-weight:bold; margin:0; padding:0;">{title}</h4></div>'
    )
    m.get_root().html.add_child(folium.Element(title_html))
    
    m.save(filename)
    print(f"✅ Saved map: {filename}")

print("Districts with NaN values in total:", merged_gdf[merged_gdf['total'].isna()]['dtname'].tolist())
print("Districts with NaN values in urban:", merged_gdf[merged_gdf['urban'].isna()]['dtname'].tolist())
print("Districts with NaN values in rural:", merged_gdf[merged_gdf['rural'].isna()]['dtname'].tolist())

make_choropleth(merged_gdf, 'total', 'Total: % Children Age 0-6', 'choropleth_total.html')
make_choropleth(merged_gdf, 'urban', 'Urban: % Children Age 0-6', 'choropleth_urban.html')
make_choropleth(merged_gdf, 'rural', 'Rural: % Children Age 0-6', 'choropleth_rural.html')