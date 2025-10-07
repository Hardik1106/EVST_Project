import folium
import geopandas as gpd

# --- Load GeoJSON ---
geojson_path = "GeoJsons/Delhi_NCR_Districts.geojson"
gdf = gpd.read_file(geojson_path)

# --- Get center of map ---
center = gdf.geometry.unary_union.centroid  # deprecated, works for now
# For future versions, you can use: gdf.geometry.union_all().centroid

# --- Create map ---
m = folium.Map(location=[center.y, center.x], zoom_start=8, tiles="CartoDB positron")

# --- Add GeoJSON layer ---
folium.GeoJson(
    geojson_path,
    name="Delhi NCR Districts",
    style_function=lambda feature: {
        "color": "black",
        "weight": 1,
        "fillColor": "lightblue",
        "fillOpacity": 0.5,
    }
).add_to(m)

# --- Add layer control ---
folium.LayerControl().add_to(m)

# --- Save map ---
m.save("delhi_ncr_simple_map.html")
print("✅ Map saved as delhi_ncr_simple_map.html")
