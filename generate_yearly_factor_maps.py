import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def clean_name(s):
    if pd.isna(s):
        return ""
    return str(s).strip().lower().replace("_", " ")


def prepare_csv(df, name_col_candidates):
    # pick first available candidate column for cleaned district name
    for c in name_col_candidates:
        if c in df.columns:
            df['district_clean'] = df[c].apply(clean_name)
            break
    if 'district_clean' not in df.columns and 'DISTRICT_NAME' in df.columns:
        df['district_clean'] = df['DISTRICT_NAME'].apply(clean_name)
    return df


def aggregate_factor(df, year_range, year_col, value_col, agg='mean'):
    df[year_col] = df[year_col].astype(int)
    df = df[df[year_col].between(year_range[0], year_range[1])]
    if agg == 'sum':
        g = df.groupby([year_col, 'district_clean'], as_index=False)[value_col].sum()
    else:
        g = df.groupby([year_col, 'district_clean'], as_index=False)[value_col].mean()
    g = g.rename(columns={value_col: 'value'})
    return g


def plot_maps(geodf, agg_df, factor_name, cmap, unit, outdir, vmin=None, vmax=None):
    os.makedirs(outdir, exist_ok=True)
    years = sorted(agg_df['YEAR'].unique())
    for yr in years:
        data_year = agg_df[agg_df['YEAR'] == yr]
        merged = geodf.merge(data_year, left_on='dtname_clean', right_on='district_clean', how='left')

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        merged.plot(column='value', cmap=cmap, linewidth=0.6, ax=ax,
                    edgecolor='0.25', vmin=vmin, vmax=vmax)
        ax.axis('off')
        ax.set_title(f"{factor_name} — {yr}", fontsize=16)

        # colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=(vmin if vmin is not None else merged['value'].min()),
                                                                 vmax=(vmax if vmax is not None else merged['value'].max())))
        sm._A = []
        cbar = fig.colorbar(sm, ax=ax, fraction=0.036, pad=0.04)
        cbar.set_label(unit)

        # label
        ax.annotate('Delhi NCR', xy=(0.02, 0.95), xycoords='axes fraction', fontsize=12, fontweight='bold')

        out_path = os.path.join(outdir, f"{yr}_{factor_name.replace(' ', '_').lower()}.png")
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print('Wrote', out_path)


def main():
    base = os.path.dirname(__file__)
    # File paths (adjust if your files are in different locations)
    temp_csv = os.path.join(base, 'Temperature', 'delhi_ncr_temp_monthly_avg_2013_2024.csv')
    rain_csv = os.path.join(base, 'Rainfall', 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv')
    aqi_csv = os.path.join(base, 'Air Quality Index', 'Vizualization_scripts', 'delhi_ncr_aqi_monthly_2018_2024.csv')
    geojson = os.path.join(base, 'GeoJsons', 'Delhi_NCR_Districts_final.geojson')

    years = (2018, 2024)

    # read geometry
    gdf = gpd.read_file(geojson)
    gdf['dtname_clean'] = gdf['dtname'].apply(clean_name)

    # --- Temperature ---
    df_temp = pd.read_csv(temp_csv)
    df_temp = prepare_csv(df_temp, ['DISTRICT_NAME_clean', 'district_name_clean', 'DISTRICT_NAME'])
    df_temp_agg = aggregate_factor(df_temp, years, 'YEAR', 'avgT', agg='mean')
    # rename YEAR column for consistency
    df_temp_agg = df_temp_agg.rename(columns={'YEAR': 'YEAR'}) if 'YEAR' in df_temp_agg.columns else df_temp_agg

    # --- Rainfall (annual total) ---
    df_rain = pd.read_csv(rain_csv)
    df_rain = prepare_csv(df_rain, ['DISTRICT_NAME_clean', 'district_name_clean', 'DISTRICT_NAME'])
    df_rain_agg = aggregate_factor(df_rain, years, 'YEAR', 'RAINFALL', agg='sum')

    # --- AQI ---
    df_aqi = pd.read_csv(aqi_csv)
    df_aqi = prepare_csv(df_aqi, ['DISTRICT_NAME_clean', 'district_name_clean', 'DISTRICT_NAME'])
    df_aqi_agg = aggregate_factor(df_aqi, years, 'YEAR', 'AQI', agg='mean')

    # Compute consistent color ranges across years for each factor
    # Temperature
    temp_vmin, temp_vmax = df_temp_agg['value'].min(), df_temp_agg['value'].max()
    rain_vmin, rain_vmax = df_rain_agg['value'].min(), df_rain_agg['value'].max()
    aqi_vmin, aqi_vmax = df_aqi_agg['value'].min(), df_aqi_agg['value'].max()

    outdir = os.path.join(base, 'output', 'yearly_maps')

    plot_maps(gdf, df_temp_agg, 'Temperature', cmap='coolwarm', unit='°C (annual mean)', outdir=outdir,
              vmin=temp_vmin, vmax=temp_vmax)

    plot_maps(gdf, df_rain_agg, 'Rainfall', cmap='PuBu', unit='mm (annual total)', outdir=outdir,
              vmin=rain_vmin, vmax=rain_vmax)

    plot_maps(gdf, df_aqi_agg, 'AQI', cmap='YlOrRd', unit='AQI (annual mean)', outdir=outdir,
              vmin=aqi_vmin, vmax=aqi_vmax)


if __name__ == '__main__':
    main()
