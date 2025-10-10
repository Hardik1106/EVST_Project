import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import TimestampedGeoJson
from branca.colormap import LinearColormap
import os
import numpy as np

# --- Load GeoJSON boundary ---
boundary_path = "GeoJsons/Delhi_NCR_Districts.geojson"
boundary = gpd.read_file(boundary_path).to_crs(epsg=4326)

# --- Load monthly temperature CSV ---
df = pd.read_csv("delhi_ncr_temp_monthly_avg_2013_2024.csv")
df["MONTH"] = df["MONTH"].astype(int)

# --- Standardize district names ---
boundary["DISTRICT_NAME_clean"] = boundary["NAME_2"].str.strip().str.lower()
df["DISTRICT_NAME_clean"] = df["DISTRICT_NAME"].str.strip().str.lower()

# Optional: handle special cases like 'West'
df["DISTRICT_NAME_clean"] = df["DISTRICT_NAME_clean"].replace({"West": "delhi"})

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

    for _, poly_row in boundary.iterrows():
        geom = poly_row.geometry
        district_clean = poly_row["DISTRICT_NAME_clean"]
        district_name = poly_row["NAME_2"]

        # Match data rows for this district
        district_data = df[df["DISTRICT_NAME_clean"] == district_clean]

        if district_data.empty:
            # Fill missing data with NaN
            dummy_time = pd.date_range(start=f"{df['YEAR'].min()}-01-01",
                                       end=f"{df['YEAR'].max()}-12-01", freq='MS')
            for t in dummy_time:
                feature = {
                    "type": "Feature",
                    "geometry": geom.__geo_interface__,
                    "properties": {
                        "time": t.strftime("%Y-%m-%dT%H:%M:%S"),
                        "style": {
                            "color": "black",
                            "weight": 1,
                            "fillColor": "#ffffff",
                            "fillOpacity": 0.3
                        },
                        "popup": f"{district_name}<br>No data"
                    }
                }
                features.append(feature)
            continue

        # Add features for each time point
        for _, row in district_data.iterrows():
            # Handle NaNs gracefully
            val = row[metric] if not pd.isna(row[metric]) else 0
            fill_color = colormap(val) if not pd.isna(row[metric]) else "#ffffff"

            feature = {
                "type": "Feature",
                "geometry": geom.__geo_interface__,
                "properties": {
                    "time": row["TIME_ISO"],
                    "style": {
                        "color": "black",
                        "weight": 1,
                        "fillColor": fill_color,
                        "fillOpacity": 0.7 if not pd.isna(row[metric]) else 0.3
                    },
                    "popup": f"{district_name}<br>{metric.upper()}: {val:.2f} °C<br>{row['TIME'].strftime('%b %Y')}"
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
