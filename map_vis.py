import os
import json
from pathlib import Path

try:
    import geopandas as gpd
    from shapely.geometry import shape
except Exception:
    gpd = None

import folium
from folium.features import DivIcon
import matplotlib.pyplot as plt


GEOJSON_REL_PATH = os.path.join("GeoJsons", "Delhi_NCR_Districts_final.geojson")


def build_map(geojson_path: str, output_html: str):
    """Builds an interactive folium map from a GeoJSON file and writes an HTML file.

    - Draws the district polygons
    - Adds hover tooltips showing the district name
    - If geopandas is available, adds visible labels placed at polygon centroids
    """

    # Create output dir
    Path(os.path.dirname(output_html)).mkdir(parents=True, exist_ok=True)

    # Default center (approx Delhi NCR)
    default_center = [28.6, 77.2]

    # Try to compute a better center using geopandas if available
    gdf = None
    try:
        if gpd:
            gdf = gpd.read_file(geojson_path)
            if not gdf.empty and gdf.geometry.unary_union is not None:
                centroid = gdf.geometry.unary_union.centroid
                default_center = [centroid.y, centroid.x]
    except Exception:
        gdf = None

    m = folium.Map(location=default_center, zoom_start=9, tiles="CartoDB positron")

    # Load geojson for folium (use json module so folium can accept the python dict)
    with open(geojson_path, "r", encoding="utf-8") as fh:
        geojson_data = json.load(fh)

    def style_function(feature):
        return {
            # lighter fill, darker boundary for better contrast
            "fillColor": "#cfe6ff",
            "color": "#111111",
            "weight": 1,
            "fillOpacity": 0.4,
        }

    gj = folium.GeoJson(
        geojson_data,
        name="Districts",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=["dtname"], aliases=["District:"], localize=True),
    )
    gj.add_to(m)

    # Note: district name labels were removed per user request.
    # If you'd like them restored or shown conditionally (e.g., on zoom),
    # we can add them back behind a flag or implement zoom-dependent logic.

    # Add layer control and save
    folium.LayerControl().add_to(m)
    m.save(output_html)


def main():
    repo_dir = os.path.dirname(__file__)
    geojson_path = os.path.join(repo_dir, GEOJSON_REL_PATH)
    output_image = os.path.join(repo_dir, "output", "delhi_ncr_districts_map.png")

    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"GeoJSON not found at {geojson_path}")

    # Use geopandas + matplotlib to write a static high-resolution PNG
    def save_image(geojson_path: str, output_path: str, dpi: int = 300, base_width_inches: float = 12.0):
        if gpd is None:
            raise RuntimeError(
                "geopandas is required to export an image. Install with: pip install geopandas matplotlib"
            )

        gdf = gpd.read_file(geojson_path)

        # If 'dtname' exists, dissolve by it to avoid duplicated overlapping polygons
        if "dtname" in gdf.columns:
            try:
                gdf = gdf.dissolve(by="dtname")
                # after dissolve, reset index to keep geometry
                gdf = gdf.reset_index()
            except Exception:
                # if dissolve fails, continue with original gdf
                pass

        # Get bounding box to set aspect ratio
        minx, miny, maxx, maxy = gdf.total_bounds
        width = maxx - minx
        height = maxy - miny
        if width <= 0 or height <= 0:
            width_inches = base_width_inches
            height_inches = base_width_inches * 0.75
        else:
            aspect = height / width
            width_inches = base_width_inches
            height_inches = max(4.0, base_width_inches * aspect)

        fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=dpi)
        ax.set_axis_off()

        # Plot with lighter fill and darker borders for contrast.
        gdf.plot(ax=ax, color="#cfe6ff", edgecolor="#111111", linewidth=0.9)

        # Add title label at top center of the image
        ax.text(
            0.5,
            0.99,
            "Delhi NCR",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=20,
            fontweight="bold",
            color="#111111",
            bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=6),
        )

        # Tight layout and save
        fig.tight_layout(pad=0)
        Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)

    save_image(geojson_path, output_image, dpi=300, base_width_inches=12.0)
    print(f"Image written to: {output_image}")


if __name__ == "__main__":
    main()
