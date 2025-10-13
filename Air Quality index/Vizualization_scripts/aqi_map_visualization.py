#!/usr/bin/env python3
"""
AQI Map Visualization for Delhi NCR
Creates an interactive map with time slider showing AQI data by district
"""

import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import TimestampedGeoJson
from branca.colormap import LinearColormap
import os
import numpy as np
from shapely.geometry import MultiPolygon

def get_aqi_color_scale():
    """
    Returns AQI color scale based on Indian AQI standards
    """
    # AQI categories and colors (Indian standards)
    aqi_ranges = [
        (0, 50, '#00E400', 'Good'),           # Green
        (51, 100, '#FFFF00', 'Satisfactory'), # Yellow  
        (101, 200, '#FF7E00', 'Moderate'),     # Orange
        (201, 300, '#FF0000', 'Poor'),         # Red
        (301, 400, '#8F3F97', 'Very Poor'),    # Purple
        (401, 500, '#7E0023', 'Severe')        # Maroon
    ]
    return aqi_ranges

def get_aqi_color(aqi_value):
    """
    Get color for AQI value based on Indian AQI standards
    """
    if pd.isna(aqi_value):
        return '#cccccc'  # Gray for missing data
    
    aqi_ranges = get_aqi_color_scale()
    for min_val, max_val, color, category in aqi_ranges:
        if min_val <= aqi_value <= max_val:
            return color
    
    # If AQI is above 500, use the severe color
    return '#7E0023'

def get_aqi_category(aqi_value):
    """
    Get AQI category for given value
    """
    if pd.isna(aqi_value):
        return 'No Data'
    
    aqi_ranges = get_aqi_color_scale()
    for min_val, max_val, color, category in aqi_ranges:
        if min_val <= aqi_value <= max_val:
            return category
    
    return 'Severe+'

def create_aqi_map():
    """
    Create interactive AQI map with time slider
    """
    print("🗺️ Creating AQI visualization map...")
    
    # --- Load GeoJSON boundary ---
    boundary_path = "../../GeoJsons/Delhi_NCR_Districts_final.geojson"
    if not os.path.exists(boundary_path):
        raise FileNotFoundError(f"Boundary GeoJSON not found: {boundary_path}")
    boundary = gpd.read_file(boundary_path).to_crs(epsg=4326)
    
    # --- Load AQI CSV data ---
    aqi_file = "delhi_ncr_aqi_monthly_2018_2024.csv"
    if not os.path.exists(aqi_file):
        raise FileNotFoundError(f"AQI data file not found: {aqi_file}. Run process_aqi_data.py first.")
    
    df = pd.read_csv(aqi_file)
    df["MONTH"] = df["MONTH"].astype(int)
    
    # --- Normalize district names ---
    # Handle boundary file district names
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
    if 'DISTRICT_NAME_clean' not in df.columns:
        df['DISTRICT_NAME_clean'] = df['DISTRICT_NAME'].astype(str).str.strip().str.lower()
    
    # --- Prepare time columns ---
    df["TIME"] = pd.to_datetime(df["YEAR"].astype(str) + "-" + df["MONTH"].astype(str) + "-01")
    df["TIME_ISO"] = df["TIME"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    # --- Create output folder ---
    os.makedirs("aqi_vis_maps", exist_ok=True)
    
    print("🎨 Generating AQI map...")
    
    # Get valid AQI range for color scale (ignore extreme outliers)
    valid_values = df['AQI'].dropna()
    if valid_values.empty:
        print("⚠️ No valid AQI data found!")
        return
    
    # Use full AQI range for better gradient representation
    vmin = 0
    vmax = 500  # Standard AQI maximum
    
    # Create smooth gradient colormap with more color steps for better transitions
    # Based on AQI breakpoints but with smooth gradients between them
    colors = [
        '#00E400',  # 0-50: Good (Green)
        '#7ED321',  # Transition
        '#FFFF00',  # 51-100: Satisfactory (Yellow)  
        '#FFB84D',  # Transition
        '#FF7E00',  # 101-200: Moderate (Orange)
        '#FF4D4D',  # Transition
        '#FF0000',  # 201-300: Poor (Red)
        '#B84DBF',  # Transition  
        '#8F3F97',  # 301-400: Very Poor (Purple)
        '#A61E3D',  # Transition
        '#7E0023'   # 401+: Severe (Maroon)
    ]
    
    # Create positions for the colors to align with AQI breakpoints
    index = [0, 25, 50, 75, 100, 150, 200, 250, 300, 350, 500]
    
    colormap = LinearColormap(colors, index=index, vmin=vmin, vmax=vmax,
                              caption="Air Quality Index (AQI) - Gradient Scale")
    
    features = []
    
    for district_name_clean, polygons in boundary.groupby('DISTRICT_NAME_clean'):
        # Get canonical display name from first polygon
        polygons = polygons.reset_index(drop=True)
        district_name = polygons.loc[0, 'DISTRICT_NAME']
        
        # Match data rows for this district
        district_data = df[df['DISTRICT_NAME_clean'] == district_name_clean]
        
        if district_data.empty:
            # Create dummy gray polygons for districts with no data
            dummy_time = pd.date_range(start=f"{df['YEAR'].min()}-01-01", 
                                     end=f"{df['YEAR'].max()}-12-01", freq='MS')
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
                                    'style': {'color': 'black', 'weight': 1, 
                                            'fillColor': '#cccccc', 'fillOpacity': 0.6},
                                    'popup': f"{district_name}<br>No AQI data available"
                                }
                            }
                            features.append(feature)
                    else:
                        feature = {
                            'type': 'Feature',
                            'geometry': geom.__geo_interface__,
                            'properties': {
                                'time': t.strftime('%Y-%m-%dT%H:%M:%S'),
                                'style': {'color': 'black', 'weight': 1, 
                                        'fillColor': '#cccccc', 'fillOpacity': 0.6},
                                'popup': f"{district_name}<br>No AQI data available"
                            }
                        }
                        features.append(feature)
            continue
        
        # Add features for each time point with AQI data
        for _, row in district_data.iterrows():
            # Determine geometry parts for this district
            for _, poly in polygons.iterrows():
                geom = poly.geometry
                
                # Handle NaNs gracefully
                aqi_val = row['AQI'] if not pd.isna(row['AQI']) else None
                
                if aqi_val is None or pd.isna(aqi_val):
                    fill_color = '#cccccc'
                    aqi_category = 'No Data'
                else:
                    # Use gradient-based color from colormap instead of discrete colors
                    try:
                        fill_color = colormap(float(aqi_val))
                    except Exception:
                        fill_color = '#cccccc'
                    aqi_category = get_aqi_category(float(aqi_val))
                
                # Create popup text
                aqi_text = f"{float(aqi_val):.1f}" if aqi_val is not None and not pd.isna(aqi_val) else "No data"
                popup_text = (f"{district_name}<br>"
                            f"AQI: {aqi_text}<br>"
                            f"Category: {aqi_category}<br>"
                            f"{pd.to_datetime(row['TIME']).strftime('%b %Y')}")
                
                # Create feature for each geometry part
                if isinstance(geom, MultiPolygon):
                    for part in geom.geoms:
                        feature = {
                            'type': 'Feature',
                            'geometry': part.__geo_interface__,
                            'properties': {
                                'time': row.get('TIME_ISO'),
                                'style': {
                                    'color': 'black', 
                                    'weight': 1, 
                                    'fillColor': fill_color, 
                                    'fillOpacity': 0.7 if aqi_val is not None else 0.6
                                },
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
                            'style': {
                                'color': 'black', 
                                'weight': 1, 
                                'fillColor': fill_color, 
                                'fillOpacity': 0.7 if aqi_val is not None else 0.6
                            },
                            'popup': popup_text
                        }
                    }
                    features.append(feature)
    
    # Create map centered on NCR
    center = boundary.geometry.union_all().centroid
    m = folium.Map(location=[center.y, center.x], zoom_start=8, tiles="CartoDB positron")
    
    # Add timestamped layer with auto-scroll features
    timestamped_geojson = TimestampedGeoJson(
        {"type": "FeatureCollection", "features": features},
        period="P1M",
        add_last_point=True,
        auto_play=True,          # Enable auto-play by default
        loop=True,               # Enable looping
        max_speed=3,             # Faster animation speed
        loop_button=True,
        date_options="YYYY-MM",
        time_slider_drag_update=True,
        duration="P1M"           # Duration for each frame
    )
    timestamped_geojson.add_to(m)
    
    # Add custom colormap legend
    colormap.add_to(m)
    
    # Add enhanced AQI category legend with gradient visualization
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 250px; height: 320px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2)">
    <b style="color: #2c3e50; font-size: 15px;">🌈 AQI Gradient Scale</b><br><br>
    
    <!-- Gradient bar visualization -->
    <div style="width: 200px; height: 20px; margin: 10px 0; border-radius: 10px; 
                background: linear-gradient(to right, 
                #00E400 0%, #7ED321 12%, #FFFF00 20%, #FFB84D 35%, 
                #FF7E00 40%, #FF4D4D 60%, #FF0000 65%, #B84DBF 75%, 
                #8F3F97 80%, #A61E3D 90%, #7E0023 100%);
                border: 1px solid #ddd;"></div>
    
    <div style="font-size: 11px; margin-bottom: 15px; color: #666;">
    ← 0 (Good) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 500+ (Severe) →
    </div>
    
    <b style="font-size: 12px;">📊 AQI Categories:</b><br><br>
    <span style="color: #00E400; font-size: 16px;">●</span> 0-50 Good<br>
    <span style="color: #FFFF00; font-size: 16px;">●</span> 51-100 Satisfactory<br>  
    <span style="color: #FF7E00; font-size: 16px;">●</span> 101-200 Moderate<br>
    <span style="color: #FF0000; font-size: 16px;">●</span> 201-300 Poor<br>
    <span style="color: #8F3F97; font-size: 16px;">●</span> 301-400 Very Poor<br>
    <span style="color: #7E0023; font-size: 16px;">●</span> 401+ Severe<br>
    <span style="color: #cccccc; font-size: 16px;">●</span> No Data<br><br>
    
    <div style="margin-top: 10px; padding: 8px; background: #f0f8ff; border-radius: 4px; font-size: 11px;">
    <b>🎨 Gradient Mode:</b> ON<br>
    <b>🎬 Auto-Play:</b> ON<br>
    Smooth color transitions between AQI levels
    </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title and gradient/auto-scroll information
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 10px; width: 380px; height: 85px; 
                background-color: rgba(44, 62, 80, 0.9); border:2px solid #34495e; z-index:9999; 
                font-size:16px; padding: 15px; border-radius: 8px; color: white; box-shadow: 0 2px 10px rgba(0,0,0,0.3)">
    <h3 style="margin: 0 0 8px 0; color: #ecf0f1;">� Delhi NCR AQI Gradient Timeline</h3>
    <p style="margin: 0; font-size: 12px; color: #bdc3c7;">
    📅 2018-2025 | 🎨 Gradient Color Scale | 🔄 Auto-scrolling | 🎯 Click districts for details
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add custom JavaScript for enhanced auto-scroll features
    auto_scroll_js = '''
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Wait for map to load
        setTimeout(function() {
            // Add custom styling to time controls
            var timeControls = document.querySelector('.leaflet-control-timecontrol');
            if (timeControls) {
                timeControls.style.background = 'rgba(255,255,255,0.95)';
                timeControls.style.borderRadius = '8px';
                timeControls.style.padding = '10px';
                timeControls.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
            }
            
            // Add notification about gradient and auto-play
            var notification = document.createElement('div');
            notification.innerHTML = '� Gradient mode active! �🎬 Auto-play started! Smooth color transitions show AQI variations.';
            notification.style.cssText = `
                position: fixed; top: 105px; left: 10px; 
                background: rgba(46, 204, 113, 0.9); color: white; 
                padding: 10px 15px; border-radius: 5px; 
                font-size: 14px; z-index: 10000; max-width: 380px;
                animation: fadeInOut 8s ease-in-out;
            `;
            
            // Add CSS for fade animation
            var style = document.createElement('style');
            style.textContent = `
                @keyframes fadeInOut {
                    0% { opacity: 0; transform: translateX(-20px); }
                    15% { opacity: 1; transform: translateX(0px); }
                    85% { opacity: 1; transform: translateX(0px); }
                    100% { opacity: 0; transform: translateX(-20px); }
                }
            `;
            document.head.appendChild(style);
            document.body.appendChild(notification);
            
            // Remove notification after animation
            setTimeout(() => notification.remove(), 6000);
            
        }, 2000);
    });
    </script>
    '''
    m.get_root().html.add_child(folium.Element(auto_scroll_js))
    
    # Save HTML
    output_html = "aqi_vis_maps/delhi_ncr_aqi_timeseries.html"
    m.save(output_html)
    
    print(f"✅ AQI gradient map saved: {output_html}")
    print("� Enhanced Gradient Features:")
    print(f"   - 🎨 Smooth gradient color transitions (no discrete colors)")
    print(f"   - 🌈 11-point color scale with AQI breakpoint alignment")
    print(f"   - 🎬 Auto-scroll animation (starts automatically)")
    print(f"   - 🔄 Looping timeline with enhanced speed")
    print(f"   - 📱 Interactive time controls (pause/play/speed)")
    print(f"   - ️ District-wise AQI values and categories")
    print(f"   - 📅 Date range: {df['YEAR'].min()}-{df['MONTH'].min():02d} to {df['YEAR'].max()}-{df['MONTH'].max():02d}")
    print(f"   - 🔔 Gradient-aware notifications and enhanced UI")
    
    return output_html

if __name__ == "__main__":
    create_aqi_map()