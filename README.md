# Week 13 GEE Hualien Earthquake Analysis

This project contains a Google Earth Engine (GEE) notebook workflow for cloud-scale satellite time-series analysis around the 2024-04-03 Hualien earthquake in Taiwan.

The analysis compares optical Sentinel-2 NDVI signals and Sentinel-1 SAR VV backscatter to observe vegetation change, landslide-related disturbance, and cross-sensor damage indicators before and after the earthquake.

## Project Files

- `Week13-Student.ipynb` - original student exercise notebook with blanks and TODO sections.
- `Week13-Student-executable-v2-GEE-fixed.ipynb` - executable version with the main TODO code filled in.
- `outputs/` - exported CSV tables and PNG figures generated from the notebook.

## Main Analysis

The notebook covers:

1. Google Earth Engine authentication and initialization.
2. Sentinel-2 Level-2A image filtering for the Hualien AOI.
3. NDVI calculation with cloud masking.
4. Monthly NDVI time-series statistics for broad Hualien.
5. Scale comparison between broad Hualien and Taroko Gorge.
6. Pre/post-earthquake delta NDVI statistics.
7. Sentinel-1 SAR VV time-series analysis.
8. Cross-sensor comparison between optical and SAR indicators.
9. A custom NDVI time-series example for Taipei city center.

## Key Event

- Hualien earthquake: `2024-04-03`
- Study area: Hualien and Taroko Gorge, Taiwan

## Requirements

The executable notebook installs or imports the main Python packages it needs, including:

- `earthengine-api`
- `geemap`
- `numpy`
- `pandas`
- `matplotlib`

You also need a Google account with Earth Engine access. If your account requires a Google Cloud project, set it in the notebook variable `GEE_PROJECT` or define an environment variable named `GEE_PROJECT`.

## Running The Notebook

1. Open `Week13-Student-executable-v2-GEE-fixed.ipynb` in Jupyter, VS Code, or Google Colab.
2. Run the setup and authentication cells first.
3. Run the remaining cells in order from top to bottom.
4. Review generated tables and figures in the `outputs/` folder.

## Outputs

The `outputs/` folder includes:

- `s4_monthly_ndvi_broad_hualien.csv`
- `s4_hualien_ndvi_timeseries.png`
- `s4b_monthly_ndvi_taroko_focus.csv`
- `s4b_scale_comparison_hualien_vs_taroko.png`
- `s5_delta_ndvi_statistics.csv`
- `s6_sentinel1_vv_timeseries.csv`
- `s6_sentinel1_vv_timeseries.png`
- `s7_cross_sensor_damage_summary.csv`
- `s10_custom_timeseries.csv`
- `s10_custom_timeseries.png`

## Notes

This repository is intended as an independent class exercise project. It does not modify or depend on the original ARIA project source code.
