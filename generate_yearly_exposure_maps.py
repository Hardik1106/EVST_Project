import os
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def ensure_output_dir(path="output"):
    os.makedirs(path, exist_ok=True)
    return path


def load_data():
    base = os.path.dirname(__file__)
    # paths (adapted to repo structure)
    geojson_p = os.path.join(base, "GeoJsons", "Delhi_NCR_Districts_final.geojson")
    rainfall_p = os.path.join(base, "Rainfall", "delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv")
    temp_p = os.path.join(base, "Temperature", "delhi_ncr_temp_monthly_avg_2013_2024.csv")
    aqi_p = os.path.join(base, "Air Quality Index", "Vizualization_scripts", "delhi_ncr_aqi_monthly_2018_2024.csv")

    missing = []
    for p in (geojson_p, rainfall_p, temp_p, aqi_p):
        if not os.path.exists(p):
            missing.append(p)
    if missing:
        raise FileNotFoundError("Missing files: " + ", ".join(missing))

    gdf = gpd.read_file(geojson_p)
    rain = pd.read_csv(rainfall_p)
    temp = pd.read_csv(temp_p)
    aqi = pd.read_csv(aqi_p)

    return gdf, rain, temp, aqi


def compute_yearly_exposure(rain_df, temp_df, aqi_df, year, district_col="DISTRICT_NAME"):
    # subset by year
    r = rain_df[rain_df["YEAR"] == year].copy()
    t = temp_df[temp_df["YEAR"] == year].copy()
    a = aqi_df[aqi_df["YEAR"] == year].copy() if "YEAR" in aqi_df.columns else aqi_df.copy()

    # make district-key consistent
    r = r.rename(columns={district_col: "district"})
    t = t.rename(columns={district_col: "district"})
    if "DISTRICT_NAME" in a.columns:
        a = a.rename(columns={"DISTRICT_NAME": "district"})

    # rainfall metrics per district
    rain_grp = r.groupby("district").agg(
        rainfall_mean=("FILLED", "mean"),
        rainfall_std=("FILLED", "std"),
        months_count=("MONTH", "count"),
    )
    rain_grp["rain_cv"] = rain_grp["rainfall_std"] / (rain_grp["rainfall_mean"].replace(0, np.nan))
    # extreme rainfall months (>100 mm)
    extreme = r.groupby("district").apply(lambda df: (df["FILLED"] > 100).sum())
    rain_grp["extreme_months"] = extreme

    # temperature metrics per district
    temp_grp = t.groupby("district").agg(
        maxT_mean=("maxT", "mean"),
        maxT_std=("maxT", "std"),
    )
    temp_grp["temp_cv"] = temp_grp["maxT_std"] / (temp_grp["maxT_mean"].replace(0, np.nan))
    # heat wave months (>40C max)
    heat = t.groupby("district").apply(lambda df: (df["maxT"] > 40).sum())
    temp_grp["heat_months"] = heat

    # aqi metric per district (annual mean)
    if "AQI" in a.columns:
        a_grp = a.groupby("district").agg(aqi_mean=("AQI", "mean"))
    else:
        # try common column names
        possible = [c for c in a.columns if c.lower().startswith("aqi")]
        if possible:
            a_grp = a.groupby("district").agg(aqi_mean=(possible[0], "mean"))
        else:
            a_grp = pd.DataFrame(columns=["aqi_mean"])

    # merge components
    df = rain_grp.join(temp_grp, how="outer").join(a_grp, how="outer")
    df = df.fillna(0)

    # build exposure components and normalize per-year across districts
    # components: rain_cv, extreme_months, temp_cv, heat_months, aqi_mean
    comps = ["rain_cv", "extreme_months", "temp_cv", "heat_months", "aqi_mean"]
    for c in comps:
        if c not in df.columns:
            df[c] = 0.0

    # clip and replace inf
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

    # normalize each component 0-1
    norm = {}
    for c in comps:
        arr = df[c].values.astype(float)
        mn, mx = arr.min(), arr.max()
        if mx - mn <= 0:
            norm[c] = np.zeros_like(arr)
        else:
            norm[c] = (arr - mn) / (mx - mn)

    # equal-weighted exposure score
    stacked = np.vstack([norm[c] for c in comps])
    exposure_score = np.nanmean(stacked, axis=0)
    df = df.reset_index()
    df["exposure_score"] = exposure_score

    df_out = df[["district", "exposure_score"] + comps]
    df_out["YEAR"] = year
    return df_out


def plot_year_exposure(geo_gdf, exposure_df, year, out_dir="output", cmap="Reds"):
    # merge exposure into geojson
    merged = geo_gdf.merge(exposure_df, left_on="DISTRICT", right_on="district", how="left")

    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=300)
    # draw base layer in light grey for all districts
    geo_gdf.plot(color='lightgrey', edgecolor='0.6', linewidth=0.4, ax=ax)

    # overlay districts that have exposure values
    have = merged[~merged['exposure_score'].isna()]
    if not have.empty:
        vmin = have['exposure_score'].min()
        vmax = have['exposure_score'].max()
        have.plot(column="exposure_score", cmap=cmap, linewidth=0.4, edgecolor="0.6", ax=ax, legend=True,
                  legend_kwds={"shrink": 0.5}, vmin=vmin, vmax=vmax)

    ax.set_title(f"Exposure {year} — Delhi NCR", fontsize=16)
    ax.axis("off")

    out_path = os.path.join(out_dir, f"exposure_{year}.png")
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return out_path


def compute_average_exposure(rain_df, temp_df, aqi_df, years=range(2018, 2025)):
    # compute annual exposure for each year, then average exposure_score across years per district
    yearly = []
    for y in years:
        try:
            df_y = compute_yearly_exposure(rain_df, temp_df, aqi_df, y)
            yearly.append(df_y[['district', 'exposure_score']])
        except Exception:
            # skip years with errors
            continue
    if not yearly:
        return pd.DataFrame(columns=['district', 'exposure_score'])
    combined = pd.concat(yearly, ignore_index=True)
    avg = combined.groupby('district', as_index=False)['exposure_score'].mean()
    return avg


def plot_average_exposure(geo_gdf, avg_df, out_dir="output", cmap="Reds"):
    # merge average exposure into geojson
    merged = geo_gdf.merge(avg_df, left_on="DISTRICT", right_on="district", how="left")

    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=300)
    # base grey layer for districts without data
    geo_gdf.plot(color='lightgrey', edgecolor='0.6', linewidth=0.4, ax=ax)

    have = merged[~merged['exposure_score'].isna()]
    if not have.empty:
        vmin = have['exposure_score'].min()
        vmax = have['exposure_score'].max()
        have.plot(column='exposure_score', cmap=cmap, linewidth=0.4, edgecolor='0.6', ax=ax, legend=True,
                  legend_kwds={"shrink": 0.5}, vmin=vmin, vmax=vmax)

    ax.set_title(f"Average Exposure 2018–2024 — Delhi NCR", fontsize=16)
    ax.axis('off')

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'exposure_2018_2024_avg.png')
    fig.savefig(out_path, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return out_path


def main(years=range(2018, 2025)):
    ensure_output_dir()
    try:
        gdf, rain, temp, aqi = load_data()
    except FileNotFoundError as e:
        print("Error loading data:", e)
        return

    # Inspect district naming in geojson
    # Expecting district name field to be 'DISTRICT' in geojson; adjust if needed
    geo_district_col = None
    for c in ["DISTRICT", "DISTRICT_NAME", "district", "name"]:
        if c in gdf.columns:
            geo_district_col = c
            break
    if geo_district_col is None:
        warnings.warn("Could not find district name column in GeoJSON; using first property as key")
        geo_district_col = gdf.columns[0]

    # ensure geojson has a consistent column name
    gdf = gdf.rename(columns={geo_district_col: "DISTRICT"})

    all_years = []
    for y in years:
        print("Processing year", y)
        try:
            df_y = compute_yearly_exposure(rain, temp, aqi, y)
        except Exception as e:
            print(f"Skipping year {y} due to error:", e)
            continue

        out_png = plot_year_exposure(gdf, df_y, y)
        print("Saved:", out_png)
        all_years.append(df_y)

    if all_years:
        combined = pd.concat(all_years, ignore_index=True)
        combined.to_csv(os.path.join("output", "exposure_by_district_by_year.csv"), index=False)
        print("Wrote combined exposure CSV to output/")
        # compute and plot average exposure across the requested years
        try:
            avg = compute_average_exposure(rain, temp, aqi, years=years)
            avg_out = plot_average_exposure(gdf, avg, out_dir="output")
            print("Wrote average exposure map:", avg_out)
        except Exception as e:
            print("Failed to compute/plot average exposure:", e)


if __name__ == "__main__":
    main()
