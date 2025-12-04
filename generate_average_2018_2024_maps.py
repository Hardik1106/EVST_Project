import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from generate_yearly_exposure_maps import compute_average_exposure


def clean_name(s):
    if pd.isna(s):
        return ""
    return str(s).strip().lower().replace("_", " ")


def prepare_csv(df, name_col_candidates):
    for c in name_col_candidates:
        if c in df.columns:
            df['district_clean'] = df[c].apply(clean_name)
            break
    if 'district_clean' not in df.columns and 'DISTRICT_NAME' in df.columns:
        df['district_clean'] = df['DISTRICT_NAME'].apply(clean_name)
    return df


def annualize_and_average_temp(df, years=(2018, 2024)):
    # compute annual mean avgT per district, then mean across years
    df['YEAR'] = df['YEAR'].astype(int)
    df = df[df['YEAR'].between(years[0], years[1])]
    annual = df.groupby(['YEAR', 'district_clean'], as_index=False)['avgT'].mean()
    avg = annual.groupby('district_clean', as_index=False)['avgT'].mean().rename(columns={'avgT': 'temp_avg'})
    return avg


def annualize_and_average_rain(df, years=(2018, 2024)):
    # compute annual total rainfall per district, then average across years
    df['YEAR'] = df['YEAR'].astype(int)
    df = df[df['YEAR'].between(years[0], years[1])]
    annual_total = df.groupby(['YEAR', 'district_clean'], as_index=False)['RAINFALL'].sum()
    avg = annual_total.groupby('district_clean', as_index=False)['RAINFALL'].mean().rename(columns={'RAINFALL': 'rain_avg'})
    return avg


def annualize_and_average_aqi(df, years=(2018, 2024)):
    # compute annual mean AQI per district, then average across years
    df['YEAR'] = df['YEAR'].astype(int)
    df = df[df['YEAR'].between(years[0], years[1])]
    annual = df.groupby(['YEAR', 'district_clean'], as_index=False)['AQI'].mean()
    avg = annual.groupby('district_clean', as_index=False)['AQI'].mean().rename(columns={'AQI': 'aqi_avg'})
    return avg


def make_4panel_map(gdf, temp_df, rain_df, aqi_df, exposure_df, outpath):
    # merge
    m = gdf.copy()
    m = m.merge(temp_df, left_on='dtname_clean', right_on='district_clean', how='left')
    m = m.merge(rain_df, left_on='dtname_clean', right_on='district_clean', how='left')
    m = m.merge(aqi_df, left_on='dtname_clean', right_on='district_clean', how='left')
    # exposure_df expected to have column 'district' and 'exposure_score'
    if exposure_df is not None and not exposure_df.empty:
        exposure_df = exposure_df.copy()
        exposure_df['district_clean'] = exposure_df['district'].apply(clean_name)
        exposure_map = dict(zip(exposure_df['district_clean'], exposure_df['exposure_score']))
        m['exposure_score'] = m['dtname_clean'].map(exposure_map)

    # vmin/vmax per panel (handle NaNs)
    tmin, tmax = m['temp_avg'].min(), m['temp_avg'].max()
    rmin, rmax = m['rain_avg'].min(), m['rain_avg'].max()
    amin, amax = m['aqi_avg'].min(), m['aqi_avg'].max()
    emin, emax = (m['exposure_score'].min(), m['exposure_score'].max()) if 'exposure_score' in m.columns else (None, None)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    # Temperature
    ax = axes[0]
    m.plot(column='temp_avg', cmap='coolwarm', linewidth=0.4, ax=ax, edgecolor='0.25', vmin=tmin, vmax=tmax)
    ax.set_title('Temperature (°C) — average 2018–2024', fontsize=12)
    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(vmin=tmin, vmax=tmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.046)
    cbar.set_label('°C')

    # Rainfall
    ax = axes[1]
    m.plot(column='rain_avg', cmap='PuBu', linewidth=0.4, ax=ax, edgecolor='0.25', vmin=rmin, vmax=rmax)
    ax.set_title('Rainfall (mm) — average annual 2018–2024', fontsize=12)
    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap='PuBu', norm=plt.Normalize(vmin=rmin, vmax=rmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.046)
    cbar.set_label('mm (annual)')

    # AQI
    ax = axes[2]
    # first draw a base layer in light grey so districts with missing AQI appear grey
    m.plot(color='lightgrey', edgecolor='0.25', linewidth=0.4, ax=ax)
    # then overlay districts that have AQI values
    has_aqi = m[~m['aqi_avg'].isna()]
    if not has_aqi.empty:
        has_aqi.plot(column='aqi_avg', cmap='YlOrRd', linewidth=0.4, ax=ax, edgecolor='0.25', vmin=amin, vmax=amax)
    ax.set_title('AQI — average 2018–2024', fontsize=12)
    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin=amin, vmax=amax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.046)
    cbar.set_label('AQI')

    # Exposure average
    ax = axes[3]
    m.plot(color='lightgrey', edgecolor='0.25', linewidth=0.4, ax=ax)
    if 'exposure_score' in m.columns and not m['exposure_score'].isna().all():
        have_e = m[~m['exposure_score'].isna()]
        vmin, vmax = emin, emax
        have_e.plot(column='exposure_score', cmap='Reds', linewidth=0.4, ax=ax, edgecolor='0.25', vmin=vmin, vmax=vmax)
    ax.set_title('Exposure score — average 2018–2024', fontsize=12)
    ax.axis('off')
    if 'exposure_score' in m.columns and emin is not None and emax is not None:
        sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=emin, vmax=emax))
        sm._A = []
        cbar = fig.colorbar(sm, ax=ax, fraction=0.046)
        cbar.set_label('Exposure (0–1)')

    # main title
    fig.suptitle('Delhi NCR — Average exposure & vulnerability 2018–2024', fontsize=16, fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('Wrote', outpath)


def main():
    base = os.path.dirname(__file__)
    temp_csv = os.path.join(base, 'Temperature', 'delhi_ncr_temp_monthly_avg_2013_2024.csv')
    rain_csv = os.path.join(base, 'Rainfall', 'delhi_ncr_rainfall_monthly_avg_2013_2024_filled.csv')
    aqi_csv = os.path.join(base, 'Air Quality Index', 'Vizualization_scripts', 'delhi_ncr_aqi_monthly_2018_2024.csv')
    geojson = os.path.join(base, 'GeoJsons', 'Delhi_NCR_Districts_final.geojson')

    years = (2018, 2024)

    # read geometry
    gdf = gpd.read_file(geojson)
    gdf['dtname_clean'] = gdf['dtname'].apply(clean_name)

    # Temperature
    df_temp = pd.read_csv(temp_csv)
    df_temp = prepare_csv(df_temp, ['DISTRICT_NAME_clean', 'district_name_clean', 'DISTRICT_NAME'])
    temp_avg = annualize_and_average_temp(df_temp, years=years)

    # Rainfall
    df_rain = pd.read_csv(rain_csv)
    df_rain = prepare_csv(df_rain, ['DISTRICT_NAME_clean', 'district_name_clean', 'DISTRICT_NAME'])
    rain_avg = annualize_and_average_rain(df_rain, years=years)

    # AQI
    df_aqi = pd.read_csv(aqi_csv)
    df_aqi = prepare_csv(df_aqi, ['DISTRICT_NAME_clean', 'district_name_clean', 'DISTRICT_NAME'])
    aqi_avg = annualize_and_average_aqi(df_aqi, years=years)

    # compute average exposure across years using helper from generate_yearly_exposure_maps
    try:
        exposure_avg = compute_average_exposure(pd.read_csv(rain_csv), pd.read_csv(temp_csv), pd.read_csv(aqi_csv), years=range(years[0], years[1] + 1))
    except Exception:
        exposure_avg = None

    outpath = os.path.join(base, 'output', 'final_average_2018_2024_4panel.png')
    make_4panel_map(gdf, temp_avg, rain_avg, aqi_avg, exposure_avg, outpath)


if __name__ == '__main__':
    main()
