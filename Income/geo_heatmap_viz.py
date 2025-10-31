import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Read the income data
df = pd.read_csv('district_wise.csv')

# Clean the data
df_clean = df[df['INCOME'] != 'Data Not Available'].copy()
df_clean['INCOME'] = pd.to_numeric(df_clean['INCOME'])

# Read the GeoJSON file
with open('../GeoJsons/Delhi_NCR_Districts_final.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Create a mapping dictionary for district name variations
name_mapping = {
    'West Delhi': 'West',  # GeoJSON has "West", CSV has "West Delhi (NCT of Delhi)"
    'West Delhi (NCT of Delhi)': 'West',
    'Gurgaon': 'Gurugram',  # GeoJSON has "Gurugram"
    'Mewat': 'Nuh',  # Mewat is now called Nuh
}

# Apply name mapping to create a normalized district name
df_clean['District_Normalized'] = df_clean['DISTRICT'].apply(
    lambda x: name_mapping.get(x, x)
)

# Create a dictionary for income lookup
income_dict = dict(zip(df_clean['District_Normalized'], df_clean['INCOME']))
year_dict = dict(zip(df_clean['District_Normalized'], df_clean['YEAR']))

# Add income data to GeoJSON properties
for feature in geojson_data['features']:
    district_name = feature['properties']['dtname']
    feature['properties']['INCOME'] = income_dict.get(district_name, 0)
    feature['properties']['YEAR'] = year_dict.get(district_name, 'N/A')
    feature['properties']['INCOME_TEXT'] = f"₹{income_dict.get(district_name, 0):,.0f}" if income_dict.get(district_name, 0) > 0 else 'No Data'

# Calculate center coordinates for the map
lats = []
lons = []
for feature in geojson_data['features']:
    if feature['geometry']['type'] == 'Polygon':
        coords = feature['geometry']['coordinates'][0]
        for coord in coords:
            lons.append(coord[0])
            lats.append(coord[1])

center_lat = sum(lats) / len(lats)
center_lon = sum(lons) / len(lons)

# Create the choropleth map
fig = px.choropleth_mapbox(
    df_clean,
    geojson=geojson_data,
    locations='District_Normalized',
    featureidkey='properties.dtname',
    color='INCOME',
    color_continuous_scale='YlOrRd',
    range_color=(0, df_clean['INCOME'].max()),
    mapbox_style='carto-positron',
    zoom=7.5,
    center={'lat': center_lat, 'lon': center_lon},
    opacity=0.7,
    labels={'INCOME': 'Income (₹)'},
    hover_name='District_Normalized',
    hover_data={
        'INCOME': ':,.0f',
        'YEAR': True,
        'District_Normalized': False
    }
)

fig.update_layout(
    title={
        'text': 'Delhi NCR District-wise Income Heatmap',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24, 'color': '#2C3E50'}
    },
    height=800,
    margin={'r': 0, 't': 60, 'l': 0, 'b': 0},
    coloraxis_colorbar={
        'title': 'Income (₹)',
        'thicknessmode': 'pixels',
        'thickness': 20,
        'lenmode': 'pixels',
        'len': 300,
        'yanchor': 'middle',
        'y': 0.5,
    }
)

fig.write_html('district_income_heatmap.html')
print("Created: district_income_heatmap.html")

# Create a second version with different color scale
fig2 = px.choropleth_mapbox(
    df_clean,
    geojson=geojson_data,
    locations='District_Normalized',
    featureidkey='properties.dtname',
    color='INCOME',
    color_continuous_scale='Viridis',
    range_color=(0, df_clean['INCOME'].max()),
    mapbox_style='carto-positron',
    zoom=7.5,
    center={'lat': center_lat, 'lon': center_lon},
    opacity=0.7,
    labels={'INCOME': 'Income (₹)'},
    hover_name='District_Normalized',
    hover_data={
        'INCOME': ':,.0f',
        'YEAR': True,
        'District_Normalized': False
    }
)

fig2.update_layout(
    title={
        'text': 'Delhi NCR District-wise Income Heatmap (Viridis)',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24, 'color': '#2C3E50'}
    },
    height=800,
    margin={'r': 0, 't': 60, 'l': 0, 'b': 0},
    coloraxis_colorbar={
        'title': 'Income (₹)',
        'thicknessmode': 'pixels',
        'thickness': 20,
        'lenmode': 'pixels',
        'len': 300,
        'yanchor': 'middle',
        'y': 0.5,
    }
)

fig2.write_html('district_income_heatmap_viridis.html')
print("Created: district_income_heatmap_viridis.html")

# Create a categorical version (income brackets)
def categorize_income(income):
    if income == 0:
        return 'No Data'
    elif income < 70000:
        return 'Low (<₹70K)'
    elif income < 150000:
        return 'Medium (₹70K-₹150K)'
    elif income < 500000:
        return 'High (₹150K-₹500K)'
    else:
        return 'Very High (>₹500K)'

df_clean['Income_Category'] = df_clean['INCOME'].apply(categorize_income)

# Define custom colors for categories
category_colors = {
    'No Data': '#CCCCCC',
    'Low (<₹70K)': '#FEE5D9',
    'Medium (₹70K-₹150K)': '#FCAE91',
    'High (₹150K-₹500K)': '#FB6A4A',
    'Very High (>₹500K)': '#CB181D'
}

fig3 = px.choropleth_mapbox(
    df_clean,
    geojson=geojson_data,
    locations='District_Normalized',
    featureidkey='properties.dtname',
    color='Income_Category',
    color_discrete_map=category_colors,
    category_orders={'Income_Category': ['No Data', 'Low (<₹70K)', 'Medium (₹70K-₹150K)', 'High (₹150K-₹500K)', 'Very High (>₹500K)']},
    mapbox_style='carto-positron',
    zoom=7.5,
    center={'lat': center_lat, 'lon': center_lon},
    opacity=0.7,
    labels={'Income_Category': 'Income Category'},
    hover_name='District_Normalized',
    hover_data={
        'INCOME': ':,.0f',
        'YEAR': True,
        'Income_Category': True,
        'District_Normalized': False
    }
)

fig3.update_layout(
    title={
        'text': 'Delhi NCR District-wise Income Categories Map',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24, 'color': '#2C3E50'}
    },
    height=800,
    margin={'r': 0, 't': 60, 'l': 0, 'b': 0},
    legend={
        'title': 'Income Category',
        'yanchor': 'middle',
        'y': 0.5,
        'xanchor': 'left',
        'x': 0.01,
        'bgcolor': 'rgba(255, 255, 255, 0.8)',
        'bordercolor': 'rgba(0, 0, 0, 0.2)',
        'borderwidth': 1
    }
)

fig3.write_html('district_income_categories_map.html')
print("Created: district_income_categories_map.html")

# Create dark theme version
fig4 = px.choropleth_mapbox(
    df_clean,
    geojson=geojson_data,
    locations='District_Normalized',
    featureidkey='properties.dtname',
    color='INCOME',
    color_continuous_scale='Plasma',
    range_color=(0, df_clean['INCOME'].max()),
    mapbox_style='carto-darkmatter',
    zoom=7.5,
    center={'lat': center_lat, 'lon': center_lon},
    opacity=0.8,
    labels={'INCOME': 'Income (₹)'},
    hover_name='District_Normalized',
    hover_data={
        'INCOME': ':,.0f',
        'YEAR': True,
        'District_Normalized': False
    }
)

fig4.update_layout(
    title={
        'text': 'Delhi NCR District-wise Income Heatmap (Dark)',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 24, 'color': '#ECF0F1'}
    },
    height=800,
    margin={'r': 0, 't': 60, 'l': 0, 'b': 0},
    paper_bgcolor='#2C3E50',
    coloraxis_colorbar={
        'title': {'text': 'Income (₹)', 'font': {'color': '#ECF0F1'}},
        'thicknessmode': 'pixels',
        'thickness': 20,
        'lenmode': 'pixels',
        'len': 300,
        'yanchor': 'middle',
        'y': 0.5,
        'tickfont': {'color': '#ECF0F1'}
    }
)

fig4.write_html('district_income_heatmap_dark.html')
print("Created: district_income_heatmap_dark.html")

# Print summary
print("\n" + "="*60)
print("GEOSPATIAL HEATMAP VISUALIZATIONS CREATED")
print("="*60)
print("✓ district_income_heatmap.html - Continuous heatmap (YlOrRd)")
print("✓ district_income_heatmap_viridis.html - Continuous heatmap (Viridis)")
print("✓ district_income_categories_map.html - Categorical income map")
print("✓ district_income_heatmap_dark.html - Dark theme heatmap (Plasma)")
print("="*60)
print(f"\nDistricts mapped: {len(df_clean)}")
print(f"Total districts in GeoJSON: {len(geojson_data['features'])}")
print("\nNote: District name mappings applied:")
for old, new in name_mapping.items():
    print(f"  - {old} → {new}")
print("\nOpen the HTML files in your browser to explore the interactive maps!")
print("You can zoom, pan, and hover over districts for detailed information.")
