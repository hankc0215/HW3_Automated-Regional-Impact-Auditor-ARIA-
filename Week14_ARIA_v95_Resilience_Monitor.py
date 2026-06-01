# Week 14 Homework — ARIA v9.5: The Resilience Monitor
# Converted from Jupyter Notebook

# # Week 14 Homework — ARIA v9.5: The Resilience Monitor
#
# **主題：** Landsat 2000–2026 長期趨勢、桃園埤塘消失、太魯閣植被韌性分析  
# **資料來源：** Google Earth Engine Landsat Collection 2 Level 2  
# **執行方式：** 本 notebook 以 `.env` 讀取 GEE Project ID、研究區、閾值與匯出參數。
#
# ---
#
# ## 作業交付檢查表
#
# - [ ] Task 1：Landsat harmonization + 26 年 NDVI 時序圖
# - [ ] Task 2：像素級 NDVI 線性趨勢圖 + greening / browning / stable 統計
# - [ ] Task 3：桃園埤塘 MNDWI 水頻率圖、消失 / 新增水體面積、223 埤塘驗證
# - [ ] Task 4：太魯閣地震後植被 recovery ratio 韌性圖 + 統計 + 300–500 字整合摘要
# - [ ] Google Drive 匯出 GeoTIFF 截圖，至少包含 NDVI trend map
# - [ ] 100–200 字簡短心得
#
# > 建議先把 `week14_env.example` 複製成 `.env`，填入你的 GEE project ID 後再執行。

# ## 0. Environment Setup：讀取 `.env` 與安裝套件
#
# `.env` 建議格式如下：
#
# ```bash
# GEE_PROJECT_ID=your-project-id
# EXPORT_FOLDER=GEE_Exports
# DO_EXPORT=false
# START_YEAR=2000
# END_YEAR=2026
# SCALE=30
# CRS=EPSG:32651
# WATER_THRESHOLD=0.1
# GREENING_THRESHOLD=0.001
# DAMAGE_THRESHOLD=0.05
# BASELINE_START=2020-01-01
# BASELINE_END=2024-04-03
# IMPACT_START=2024-04-03
# IMPACT_END=2025-01-01
# RECOVERY_START=2025-06-01
# RECOVERY_END=2026-04-01
# ```
#
# `DO_EXPORT=false` 時不會啟動 Google Drive 匯出；作業最後一次正式執行前，請改成 `true`。

# ============================================================
# S0 — Basic setup and dependency check
# ============================================================
import os
import sys
import subprocess
import importlib
import warnings
from pathlib import Path
from datetime import datetime

warnings.filterwarnings('ignore')

# ------------------------------------------------------------
# Install missing packages only when needed
# ------------------------------------------------------------
def ensure_package(import_name, pip_name=None):
    """Import a package; install it if missing."""
    pip_name = pip_name or import_name
    try:
        return importlib.import_module(import_name)
    except ImportError:
        print(f"Installing missing package: {pip_name}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pip_name])
        return importlib.import_module(import_name)

# Earth Engine package is imported as ee but installed as earthengine-api
ensure_package('ee', 'earthengine-api')
ensure_package('geemap', 'geemap')
ensure_package('pandas', 'pandas')
ensure_package('numpy', 'numpy')
ensure_package('matplotlib', 'matplotlib')

import ee
import geemap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from IPython.display import display, Markdown

# Output folder for figures and tables
OUTPUT_DIR = Path('outputs')
OUTPUT_DIR.mkdir(exist_ok=True)

print('Setup complete.')
print(f'Python: {sys.version.split()[0]}')
print(f'Working directory: {Path.cwd().resolve()}')
print(f'Output directory: {OUTPUT_DIR.resolve()}')

# ============================================================
# S1 — Read .env parameters
# ============================================================
def load_simple_env(env_path='.env'):
    """Read key=value pairs from .env without requiring python-dotenv."""
    env_path = Path(env_path)
    if not env_path.exists():
        print(f"No .env found at {env_path.resolve()}. Using default values where available.")
        return
    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value
    print(f"Loaded .env from {env_path.resolve()}")


def parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {'1', 'true', 'yes', 'y', 'on'}


def parse_bbox(value, default):
    """Parse BBOX string as west,south,east,north."""
    if value is None or str(value).strip() == '':
        return default
    vals = [float(x.strip()) for x in str(value).split(',')]
    if len(vals) != 4:
        raise ValueError('BBOX must have four comma-separated numbers: west,south,east,north')
    return vals

load_simple_env('.env')

# Core GEE / export parameters
GEE_PROJECT_ID = os.getenv('GEE_PROJECT_ID', '').strip()
EXPORT_FOLDER = os.getenv('EXPORT_FOLDER', 'GEE_Exports')
DO_EXPORT = parse_bool(os.getenv('DO_EXPORT', 'false'), default=False)

# Temporal parameters
START_YEAR = int(os.getenv('START_YEAR', '2000'))
END_YEAR = int(os.getenv('END_YEAR', '2026'))
START_DATE = f'{START_YEAR}-01-01'
END_DATE_EXCLUSIVE = f'{END_YEAR + 1}-01-01'

# Spatial and threshold parameters
SCALE = int(os.getenv('SCALE', '30'))
CRS = os.getenv('CRS', 'EPSG:32651')
WATER_THRESHOLD = float(os.getenv('WATER_THRESHOLD', '0.1'))
GREENING_THRESHOLD = float(os.getenv('GREENING_THRESHOLD', '0.001'))
DAMAGE_THRESHOLD = float(os.getenv('DAMAGE_THRESHOLD', '0.05'))

# Study areas
DEFAULT_TAROKO_BBOX = [121.34526379253053, 24.046021742135874, 121.85149217685861, 24.35767637905926]
DEFAULT_TAOYUAN_BBOX = [120.94, 24.83, 121.35, 25.08]
DEFAULT_TAOYUAN_URBAN_BBOX = [121.00, 24.88, 121.28, 25.05]

TAROKO_BBOX = parse_bbox(os.getenv('TAROKO_BBOX'), DEFAULT_TAROKO_BBOX)
TAOYUAN_BBOX = parse_bbox(os.getenv('TAOYUAN_BBOX'), DEFAULT_TAOYUAN_BBOX)
TAOYUAN_URBAN_BBOX = parse_bbox(os.getenv('TAOYUAN_URBAN_BBOX'), DEFAULT_TAOYUAN_URBAN_BBOX)

# Resilience period settings. End dates are exclusive in Earth Engine filterDate().
BASELINE_START = os.getenv('BASELINE_START', '2020-01-01')
BASELINE_END = os.getenv('BASELINE_END', '2024-04-03')
IMPACT_START = os.getenv('IMPACT_START', '2024-04-03')
IMPACT_END = os.getenv('IMPACT_END', '2025-01-01')
RECOVERY_START = os.getenv('RECOVERY_START', '2025-06-01')
RECOVERY_END = os.getenv('RECOVERY_END', '2026-04-01')

# Pond validation data
POND_GEOJSON_URL = os.getenv(
    'POND_GEOJSON_URL',
    'https://drive.google.com/uc?id=1qwrIIELIJXbrBL_oCBTcoE-aoWq1bdXw'
)
POND_GEOJSON_PATH = os.getenv('POND_GEOJSON_PATH', 'taoyuan_ponds_223.geojson')

config = {
    'GEE_PROJECT_ID': GEE_PROJECT_ID or '(empty; ee.Initialize() will run without project)',
    'EXPORT_FOLDER': EXPORT_FOLDER,
    'DO_EXPORT': DO_EXPORT,
    'START_YEAR': START_YEAR,
    'END_YEAR': END_YEAR,
    'SCALE': SCALE,
    'CRS': CRS,
    'WATER_THRESHOLD': WATER_THRESHOLD,
    'GREENING_THRESHOLD': GREENING_THRESHOLD,
    'DAMAGE_THRESHOLD': DAMAGE_THRESHOLD,
    'TAROKO_BBOX': TAROKO_BBOX,
    'TAOYUAN_BBOX': TAOYUAN_BBOX,
    'TAOYUAN_URBAN_BBOX': TAOYUAN_URBAN_BBOX,
    'BASELINE': f'{BASELINE_START} to {BASELINE_END} (exclusive end)',
    'IMPACT': f'{IMPACT_START} to {IMPACT_END} (exclusive end)',
    'RECOVERY': f'{RECOVERY_START} to {RECOVERY_END} (exclusive end)',
}

for k, v in config.items():
    print(f'{k}: {v}')

# ============================================================
# S2 — Authenticate and initialize Google Earth Engine
# ============================================================
def initialize_ee(project_id=None):
    """Initialize GEE; authenticate if needed."""
    try:
        if project_id:
            ee.Initialize(project=project_id)
        else:
            ee.Initialize()
        print('Earth Engine initialized successfully.')
    except Exception as e:
        print('Earth Engine is not initialized yet. Starting authentication...')
        ee.Authenticate()
        if project_id:
            ee.Initialize(project=project_id)
        else:
            ee.Initialize()
        print('Earth Engine initialized after authentication.')

initialize_ee(GEE_PROJECT_ID if GEE_PROJECT_ID else None)

aoi = ee.Geometry.Rectangle(TAROKO_BBOX)
aoi_taoyuan = ee.Geometry.Rectangle(TAOYUAN_BBOX)
aoi_taoyuan_urban = ee.Geometry.Rectangle(TAOYUAN_URBAN_BBOX)

year_list = ee.List.sequence(START_YEAR, END_YEAR)
years = list(range(START_YEAR, END_YEAR + 1))

print(f'Study area: Xiulin / Taroko')
print(f'Time range: {START_YEAR}–{END_YEAR}')
print(f'Number of annual frames: {len(years)}')

# ## 1. Landsat Harmonization：L5/L7/L8/L9 波段調和
#
# 不同 Landsat 世代的波段編號不同，因此必須先統一成共同名稱：`Blue, Green, Red, NIR, SWIR1, SWIR2`。  
# 本作業使用 **Collection 2 Level 2 Surface Reflectance**，反射率校正式為：
#
# \[
# \text{Reflectance} = \text{DN} \times 0.0000275 - 0.2
# \]
#
# 同時以 `QA_PIXEL` 的 bit 3 與 bit 4 移除 cloud 與 cloud shadow。

# ============================================================
# S3 — Landsat harmonization and preprocessing functions
# ============================================================
def harmonize_l57(image):
    """Rename Landsat 5/7 bands to a shared naming convention."""
    return (image.select(
        ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL'],
        ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']
    ).copyProperties(image, ['system:time_start', 'SPACECRAFT_ID', 'LANDSAT_PRODUCT_ID']))


def harmonize_l89(image):
    """Rename Landsat 8/9 bands to the same shared naming convention."""
    return (image.select(
        ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL'],
        ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'QA_PIXEL']
    ).copyProperties(image, ['system:time_start', 'SPACECRAFT_ID', 'LANDSAT_PRODUCT_ID']))


def apply_scale_and_mask(image):
    """Apply C2 L2 scale factor and mask clouds/shadows using QA_PIXEL bits."""
    qa = image.select('QA_PIXEL')

    # QA_PIXEL bitmask: bit 3 = cloud, bit 4 = cloud shadow.
    # Keep pixels where both bits are 0.
    cloud_free = qa.bitwiseAnd(1 << 3).eq(0)
    shadow_free = qa.bitwiseAnd(1 << 4).eq(0)
    mask = cloud_free.And(shadow_free)

    spectral = (image.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'])
                .multiply(0.0000275)
                .add(-0.2)
                .clamp(0, 1))

    return (spectral.updateMask(mask)
            .copyProperties(image, ['system:time_start', 'SPACECRAFT_ID', 'LANDSAT_PRODUCT_ID']))


def get_landsat_collection(geometry, start_date=START_DATE, end_date=END_DATE_EXCLUSIVE):
    """Load, harmonize, merge, scale, and cloud-mask Landsat L5/L7/L8/L9."""
    l5 = (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
          .filterBounds(geometry)
          .filterDate(start_date, min(end_date, '2013-01-01'))
          .map(harmonize_l57))

    l7 = (ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
          .filterBounds(geometry)
          .filterDate(start_date, end_date)
          .map(harmonize_l57))

    l8 = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
          .filterBounds(geometry)
          .filterDate(max(start_date, '2013-01-01'), end_date)
          .map(harmonize_l89))

    l9 = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
          .filterBounds(geometry)
          .filterDate(max(start_date, '2021-01-01'), end_date)
          .map(harmonize_l89))

    return l5.merge(l7).merge(l8).merge(l9).map(apply_scale_and_mask)


def compute_indices(image):
    """Compute NDVI, MNDWI, and NBR from a harmonized Landsat image."""
    ndvi = image.normalizedDifference(['NIR', 'Red']).rename('NDVI')
    mndwi = image.normalizedDifference(['Green', 'SWIR1']).rename('MNDWI')
    nbr = image.normalizedDifference(['NIR', 'SWIR2']).rename('NBR')
    return (ndvi.addBands(mndwi).addBands(nbr)
            .copyProperties(image, ['system:time_start', 'SPACECRAFT_ID', 'LANDSAT_PRODUCT_ID']))


def annual_index_image(year, index_collection, band_name, geometry=None):
    """Create one annual median image with an added time band for linearFit."""
    y = ee.Number(year).int()
    start = ee.Date.fromYMD(y, 1, 1)
    end = start.advance(1, 'year')
    img = index_collection.filterDate(start, end).median().select(band_name)
    if geometry is not None:
        img = img.clip(geometry)
    time_band = ee.Image.constant(y).float().rename('time')
    return img.addBands(time_band).set('system:time_start', start.millis()).set('year', y)


def fc_to_dataframe(fc):
    """Convert a small Earth Engine FeatureCollection to pandas DataFrame."""
    info = fc.getInfo()
    rows = [feat.get('properties', {}) for feat in info.get('features', [])]
    df = pd.DataFrame(rows)
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
        df = df.sort_values('year').reset_index(drop=True)
    return df


def grouped_area_stats(class_image, class_band, geometry, class_labels, scale=SCALE):
    """Compute area and percent by class for an integer class image."""
    area_img = ee.Image.pixelArea().divide(10000).rename('area_ha')
    stats = (area_img.addBands(class_image.rename(class_band))
             .reduceRegion(
                 reducer=ee.Reducer.sum().group(groupField=1, groupName='class'),
                 geometry=geometry,
                 scale=scale,
                 maxPixels=1e13,
                 bestEffort=True
             ).get('groups'))

    groups = stats.getInfo() if stats else []
    rows = []
    for g in groups:
        cls = int(g['class'])
        rows.append({
            'class': cls,
            'label': class_labels.get(cls, f'class_{cls}'),
            'area_ha': float(g.get('sum', 0.0)),
        })
    df = pd.DataFrame(rows)
    if len(df) == 0:
        return pd.DataFrame(columns=['class', 'label', 'area_ha', 'percent'])
    total = df['area_ha'].sum()
    df['percent'] = np.where(total > 0, df['area_ha'] / total * 100, np.nan)
    return df.sort_values('class').reset_index(drop=True)

print('Harmonization and utility functions are ready.')

# # Task 1 — Landsat Harmonization + 26-Year NDVI Time Series
#
# **目標：** 合併 L5/L7/L8/L9，建立 2000–2026 年太魯閣 / 秀林研究區年度 NDVI 平均值，並繪製 2024 地震標記與長期趨勢線。

# ============================================================
# T1-1 — Load Taroko Landsat and compute indices
# ============================================================
landsat_all = get_landsat_collection(aoi)
multi_index_col = landsat_all.map(compute_indices)
ndvi_collection = multi_index_col.select('NDVI')

image_count = landsat_all.size().getInfo()
band_names = landsat_all.first().bandNames().getInfo()

print(f'Total Landsat images used for Taroko ({START_YEAR}–{END_YEAR}): {image_count}')
print(f'Harmonized band names: {band_names}')

# ============================================================
# T1-2 — Build annual mean NDVI / MNDWI / NBR table
# Stable version: run one year at a time to avoid GEE 429
# "Too many concurrent aggregations"
# ============================================================
import time


def safe_getinfo(obj, label='', max_retries=5, base_sleep=8):
    """Run getInfo() with simple retry/backoff for temporary GEE quota errors."""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return obj.getInfo()
        except Exception as e:
            last_error = e
            msg = str(e)
            retryable = (
                'Too many concurrent aggregations' in msg
                or 'Quota exceeded' in msg
                or 'Rate exceeded' in msg
                or '429' in msg
                or 'Internal error' in msg
            )
            if not retryable or attempt == max_retries:
                raise
            sleep_s = base_sleep * attempt
            print(f'  {label} failed on attempt {attempt}/{max_retries}: {msg[:120]}...')
            print(f'  sleeping {sleep_s} seconds then retrying')
            time.sleep(sleep_s)
    raise last_error


def annual_mean_dict_taroko(year):
    """Compute annual area-mean NDVI/MNDWI/NBR for one year only."""
    start = f'{year}-01-01'
    end = f'{year + 1}-01-01'
    yearly_col = multi_index_col.filterDate(start, end)
    annual_img = yearly_col.median()

    stats = annual_img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=aoi,
        scale=SCALE,
        maxPixels=1e13,
        bestEffort=True,
        tileScale=4,
    )

    stats_info = safe_getinfo(stats, label=f'{year} reduceRegion') or {}
    image_count_info = safe_getinfo(yearly_col.size(), label=f'{year} image_count')

    return {
        'year': year,
        'NDVI': stats_info.get('NDVI'),
        'MNDWI': stats_info.get('MNDWI'),
        'NBR': stats_info.get('NBR'),
        'image_count': image_count_info,
    }


rows = []
for year in years:
    print(f'Processing annual statistics for {year} ...')
    try:
        rows.append(annual_mean_dict_taroko(year))
    except Exception as e:
        print(f'  WARNING: {year} failed. Keeping this year as NaN.')
        print('  Error:', repr(e))
        rows.append({
            'year': year,
            'NDVI': np.nan,
            'MNDWI': np.nan,
            'NBR': np.nan,
            'image_count': np.nan,
        })
    time.sleep(0.7)

annual_df = pd.DataFrame(rows).sort_values('year').reset_index(drop=True)

for col in ['NDVI', 'MNDWI', 'NBR', 'image_count']:
    if col in annual_df.columns:
        annual_df[col] = pd.to_numeric(annual_df[col], errors='coerce')

annual_csv = OUTPUT_DIR / 'task1_taroko_annual_indices_2000_2026.csv'
annual_df.to_csv(annual_csv, index=False, encoding='utf-8-sig')

print(f'Saved annual index table: {annual_csv}')
display(annual_df.head())
display(annual_df.tail())

# ============================================================
# T1-3 — Plot 26-year NDVI trend
# ============================================================
plot_df = annual_df.dropna(subset=['NDVI']).copy()

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(plot_df['year'], plot_df['NDVI'], marker='o', linewidth=1.8, label='Annual mean NDVI')
ax.axvline(2024, linestyle='--', linewidth=1.5, label='2024 Hualien earthquake')

# Linear trendline
if len(plot_df) >= 2:
    x = plot_df['year'].astype(float).to_numpy()
    y = plot_df['NDVI'].astype(float).to_numpy()
    slope_1d, intercept = np.polyfit(x, y, 1)
    trend_y = slope_1d * x + intercept
    ax.plot(x, trend_y, linestyle=':', linewidth=2.0, label=f'Linear trend: {slope_1d:+.5f} NDVI/yr')
else:
    slope_1d, intercept = np.nan, np.nan

ax.set_title(f'Taroko / Xiulin Annual NDVI Trend ({START_YEAR}–{END_YEAR})')
ax.set_xlabel('Year')
ax.set_ylabel('Mean NDVI')
ax.set_xticks(years)
ax.tick_params(axis='x', rotation=45)
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()

fig_path = OUTPUT_DIR / 'task1_taroko_ndvi_trend_2000_2026.png'
plt.savefig(fig_path, dpi=160, bbox_inches='tight')
plt.show()

print(f'Saved figure: {fig_path}')
print(f'Full-period area-mean NDVI slope: {slope_1d:+.6f} NDVI/year')

# ============================================================
# T1-4 — Auto-generate Markdown answer for Task 1
# ============================================================
valid = annual_df.dropna(subset=['NDVI']).copy()
if len(valid) >= 3:
    low_years = valid.nsmallest(3, 'NDVI')[['year', 'NDVI']]
    high_years = valid.nlargest(3, 'NDVI')[['year', 'NDVI']]
    ndvi_2024 = valid.loc[valid['year'] == 2024, 'NDVI']
    ndvi_2024_txt = f"{ndvi_2024.iloc[0]:.3f}" if len(ndvi_2024) else "無有效值"
    trend_word = '長期綠化（greening）' if slope_1d > 0 else '長期退化或褐化（browning）' if slope_1d < 0 else '整體穩定'

    low_txt = '、'.join([f"{int(r.year)}（{r.NDVI:.3f}）" for _, r in low_years.iterrows()])
    high_txt = '、'.join([f"{int(r.year)}（{r.NDVI:.3f}）" for _, r in high_years.iterrows()])

    task1_md = f"""
### Task 1 Markdown 作答區：26 年 NDVI 趨勢分析

本次太魯閣 / 秀林研究區共使用 **{image_count:,}** 張 Landsat 影像，時間範圍為 **{START_YEAR}–{END_YEAR}**。四代 Landsat 影像先經過波段調和，將 L5/L7 與 L8/L9 統一為 Blue、Green、Red、NIR、SWIR1、SWIR2，再套用 Collection 2 Level 2 的 scale factor 與 QA_PIXEL 雲 / 雲影遮罩。從年度 NDVI 平均值來看，整體線性斜率為 **{slope_1d:+.5f} NDVI/year**，表示研究區在 26 年尺度上呈現 **{trend_word}** 的方向。

NDVI 較低的年份包括 **{low_txt}**；NDVI 較高的年份包括 **{high_txt}**。2024 年地震年的年度平均 NDVI 為 **{ndvi_2024_txt}**，可用來和過去低值年份比較，以判斷 2024 年是否屬於長期紀錄中的明顯異常。相較於 W13 使用 Sentinel-2 的 6 年資料，本次 Landsat 26 年序列解析度較粗，但能提供更完整的長期背景，避免只用短期資料把單一事件誤判成長期趨勢。
"""
    display(Markdown(task1_md))
else:
    display(Markdown('### Task 1 Markdown 作答區\n\n年度 NDVI 有效資料不足，請檢查 GEE 初始化、AOI 或雲遮罩設定。'))

# # Task 2 — Pixel-Level Linear Trend Analysis
#
# **目標：** 對每個像素使用 `ee.Reducer.linearFit()` 估計 2000–2026 年 NDVI slope，並區分：
#
# - `slope > GREENING_THRESHOLD`：greening
# - `slope < -GREENING_THRESHOLD`：browning
# - 其餘：stable
#
# 本 notebook 預設 `GREENING_THRESHOLD = 0.001 NDVI/year`，可由 `.env` 修改。

# ============================================================
# T2-1 — Pixel-level NDVI linear trend using ee.Reducer.linearFit()
# ============================================================
annual_ndvi_col = ee.ImageCollection(
    year_list.map(lambda y: annual_index_image(y, multi_index_col, 'NDVI', geometry=aoi))
)

# linearFit expects independent variable first, dependent variable second.
trend = annual_ndvi_col.select(['time', 'NDVI']).reduce(ee.Reducer.linearFit()).clip(aoi)
slope = trend.select('scale').rename('ndvi_slope_per_year')
offset = trend.select('offset').rename('ndvi_intercept')

print('Trend image bands:', trend.bandNames().getInfo())
print('Slope unit: NDVI per year')

# ============================================================
# T2-2 — Classify greening / browning / stable and compute area statistics
# ============================================================
greening = slope.gt(GREENING_THRESHOLD)
browning = slope.lt(-GREENING_THRESHOLD)
stable = slope.gte(-GREENING_THRESHOLD).And(slope.lte(GREENING_THRESHOLD))

# Class codes: 1 = browning, 2 = stable, 3 = greening
trend_class = (ee.Image(0)
               .where(browning, 1)
               .where(stable, 2)
               .where(greening, 3)
               .updateMask(slope.mask())
               .rename('trend_class')
               .clip(aoi))

trend_labels = {
    1: 'browning / degradation',
    2: 'stable',
    3: 'greening / recovery',
}
trend_stats_df = grouped_area_stats(trend_class, 'trend_class', aoi, trend_labels, scale=SCALE)
trend_stats_csv = OUTPUT_DIR / 'task2_taroko_ndvi_trend_class_stats.csv'
trend_stats_df.to_csv(trend_stats_csv, index=False, encoding='utf-8-sig')

print(f'Saved trend statistics: {trend_stats_csv}')
display(trend_stats_df)

# ============================================================
# T2-3 — Interactive map: NDVI slope and trend classes
# ============================================================
Map = geemap.Map(center=[(TAROKO_BBOX[1] + TAROKO_BBOX[3]) / 2, (TAROKO_BBOX[0] + TAROKO_BBOX[2]) / 2], zoom=10)
Map.add_basemap('HYBRID')
Map.addLayer(aoi, {'color': 'white'}, 'Taroko AOI')
Map.addLayer(
    slope,
    {'min': -0.006, 'max': 0.006, 'palette': ['8c510a', 'd8b365', 'f6e8c3', 'c7eae5', '5ab4ac', '01665e']},
    'NDVI slope: browning ↔ greening'
)
Map.addLayer(
    trend_class,
    {'min': 1, 'max': 3, 'palette': ['brown', 'lightgray', 'green']},
    'Trend class'
)
Map

# ============================================================
# T2-4 — Export trend map to Google Drive
# ============================================================
trend_export_img = slope.addBands(offset).addBands(trend_class).float().clip(aoi)

if DO_EXPORT:
    task = ee.batch.Export.image.toDrive(
        image=trend_export_img,
        description='taroko_ndvi_trend_26yr_week14',
        folder=EXPORT_FOLDER,
        fileNamePrefix='taroko_ndvi_trend_26yr_week14',
        region=aoi,
        scale=SCALE,
        crs=CRS,
        maxPixels=1e13,
    )
    task.start()
    print('Export started.')
    print('Task ID:', task.id)
    print('Task status:', task.status())
else:
    print('DO_EXPORT=false, so no export was started.')
    print('Set DO_EXPORT=true in .env and rerun this cell for final submission.')

# ============================================================
# T2-5 — Auto-generate Markdown answer for Task 2
# ============================================================
def stat_value(df, label_keyword, col='percent'):
    if df is None or len(df) == 0:
        return np.nan
    m = df['label'].str.contains(label_keyword, case=False, na=False)
    return df.loc[m, col].iloc[0] if m.any() else np.nan

browning_pct = stat_value(trend_stats_df, 'browning')
stable_pct = stat_value(trend_stats_df, 'stable')
greening_pct = stat_value(trend_stats_df, 'greening')

browning_ha = stat_value(trend_stats_df, 'browning', 'area_ha')
stable_ha = stat_value(trend_stats_df, 'stable', 'area_ha')
greening_ha = stat_value(trend_stats_df, 'greening', 'area_ha')

answer = f"""
### Task 2 Markdown 作答區：像素級 greening / browning 趨勢

以 `ee.Reducer.linearFit()` 對 {START_YEAR}–{END_YEAR} 年的年度 NDVI 中值影像進行像素級線性回歸後，slope 的單位為 **NDVI/year**。本分析以 ±{GREENING_THRESHOLD:.4f} NDVI/year 作為分類門檻：大於此值為 greening，小於負值為 browning，其餘為 stable。統計結果顯示，研究區約 **{browning_pct:.1f}%（{browning_ha:,.1f} ha）** 屬於 browning，約 **{stable_pct:.1f}%（{stable_ha:,.1f} ha）** 屬於 stable，約 **{greening_pct:.1f}%（{greening_ha:,.1f} ha）** 屬於 greening。

與 W13 的 6 年 Sentinel-2 趨勢相比，W14 的 26 年 Landsat 趨勢更適合判斷長期方向，因為它可以降低單一年份災害、雲量、季節差異造成的短期雜訊。若某些區域在 2020–2026 呈現 browning，但在 2000–2026 仍為 greening，代表近期事件可能只是長期恢復過程中的短期擾動；相反地，若短期與長期都呈現 browning，則可能是持續性退化或反覆擾動的熱區。作業繳交時，請附上 Google Drive 中 `taroko_ndvi_trend_26yr_week14.tif` 的匯出截圖。
"""

display(Markdown(answer))

# # Task 3 — Taoyuan Pond Disappearance with MNDWI
#
# **目標：** 使用 MNDWI 偵測桃園台地 2000–2026 年的水體出現頻率，並比較 2000–2005 與 2021–2026 的水體變化。
#
# \[
# MNDWI = \frac{Green - SWIR1}{Green + SWIR1}
# \]
#
# 預設水體閾值：`MNDWI > 0.1`，可由 `.env` 的 `WATER_THRESHOLD` 修改。

# ============================================================
# T3-1 — Load Taoyuan Landsat and compute MNDWI
# ============================================================
landsat_taoyuan = get_landsat_collection(aoi_taoyuan)
index_taoyuan = landsat_taoyuan.map(compute_indices)
mndwi_taoyuan = index_taoyuan.select('MNDWI')

ty_count = landsat_taoyuan.size().getInfo()
print(f'Total Landsat images used for Taoyuan ({START_YEAR}–{END_YEAR}): {ty_count}')

# ============================================================
# T3-2 — Build annual water maps and water frequency
# ============================================================
def yearly_water(year):
    y = ee.Number(year).int()
    start = ee.Date.fromYMD(y, 1, 1)
    end = start.advance(1, 'year')
    median_mndwi = mndwi_taoyuan.filterDate(start, end).median()
    water = median_mndwi.gt(WATER_THRESHOLD).rename('water')
    return water.set('system:time_start', start.millis()).set('year', y)

water_col = ee.ImageCollection(year_list.map(yearly_water))
water_freq = water_col.mean().rename('water_frequency').clip(aoi_taoyuan)

# Early and recent period water maps
early_water = (mndwi_taoyuan
               .filterDate('2000-01-01', '2006-01-01')
               .median()
               .gt(WATER_THRESHOLD)
               .rename('early_water')
               .clip(aoi_taoyuan))

recent_water = (mndwi_taoyuan
                .filterDate('2021-01-01', '2027-01-01')
                .median()
                .gt(WATER_THRESHOLD)
                .rename('recent_water')
                .clip(aoi_taoyuan))

lost_ponds = early_water.And(recent_water.Not()).rename('lost_ponds').clip(aoi_taoyuan)
new_water = recent_water.And(early_water.Not()).rename('new_water').clip(aoi_taoyuan)
pond_change_class = (ee.Image(0)
                     .where(lost_ponds, 1)
                     .where(new_water, 2)
                     .updateMask(lost_ponds.Or(new_water))
                     .rename('pond_change_class')
                     .clip(aoi_taoyuan))

print('Water frequency and pond change maps are ready.')

# ============================================================
# T3 — Estimate pond change area, memory-safe tiled version
# Replace the original failed area-estimation cell with this cell
# ============================================================
import os
import time
import numpy as np
import pandas as pd


# 面積統計可以用比地圖更粗的 scale，降低 GEE 記憶體壓力
# 地圖本身仍然是 Landsat 30 m；這裡只是統計面積用
AREA_SCALE = int(os.getenv("AREA_SCALE", "90"))

print(f"Area statistics scale: {AREA_SCALE} m")


def safe_getinfo(obj, label='', max_retries=5, base_sleep=8):
    """Run getInfo with retry/backoff for temporary GEE errors."""
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return obj.getInfo()

        except Exception as e:
            last_error = e
            msg = str(e)

            retryable = (
                'User memory limit exceeded' in msg
                or 'Too many concurrent aggregations' in msg
                or 'Quota exceeded' in msg
                or 'Rate exceeded' in msg
                or '429' in msg
                or 'Internal error' in msg
                or 'Computation timed out' in msg
            )

            if (not retryable) or attempt == max_retries:
                raise

            sleep_s = base_sleep * attempt
            print(f"  {label} failed on attempt {attempt}/{max_retries}")
            print(f"  {msg[:160]}...")
            print(f"  sleeping {sleep_s} seconds then retrying")
            time.sleep(sleep_s)

    raise last_error


def make_bbox_tiles(bbox, nx=4, ny=3):
    """
    Split a lon/lat bbox into smaller ee.Geometry.Rectangle tiles.
    bbox format: [xmin, ymin, xmax, ymax]
    """
    xmin, ymin, xmax, ymax = bbox
    xs = np.linspace(xmin, xmax, nx + 1)
    ys = np.linspace(ymin, ymax, ny + 1)

    tiles = []
    for i in range(nx):
        for j in range(ny):
            tile_bbox = [float(xs[i]), float(ys[j]), float(xs[i + 1]), float(ys[j + 1])]
            tiles.append(ee.Geometry.Rectangle(tile_bbox))

    return tiles


def masked_area_ha_one_tile(mask_img, geometry, scale=AREA_SCALE, label=''):
    """
    Compute masked area in hectares for one small tile.
    Using a small geometry reduces GEE memory usage.
    """
    area_img = (
        ee.Image.pixelArea()
        .divide(10000)
        .rename('area_ha')
        .updateMask(mask_img)
    )

    stat = area_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=scale,
        crs='EPSG:4326',
        maxPixels=1e9,
        bestEffort=True,
        tileScale=16,
    )

    value = safe_getinfo(stat.get('area_ha'), label=label)

    if value is None:
        return 0.0

    return float(value)


def masked_area_ha_tiled(mask_img, bbox, nx=4, ny=3, scale=AREA_SCALE, label='area'):
    """
    Compute total masked area by summing smaller bbox tiles.
    This avoids running reduceRegion over the full AOI at once.
    """
    tiles = make_bbox_tiles(bbox, nx=nx, ny=ny)

    total = 0.0
    tile_values = []

    for k, tile in enumerate(tiles, start=1):
        tile_label = f"{label} tile {k}/{len(tiles)}"
        print(f"Processing {tile_label} ...")

        try:
            value = masked_area_ha_one_tile(
                mask_img=mask_img,
                geometry=tile,
                scale=scale,
                label=tile_label,
            )
        except Exception as e:
            print(f"  WARNING: {tile_label} failed, recorded as NaN")
            print("  Error:", repr(e))
            value = np.nan

        tile_values.append(value)

        if np.isfinite(value):
            total += value

        time.sleep(0.5)

    return total, tile_values


# ------------------------------------------------------------
# Full Taoyuan plateau
# ------------------------------------------------------------
lost_area_ha_full, lost_tiles_full = masked_area_ha_tiled(
    lost_ponds,
    TAOYUAN_BBOX,
    nx=4,
    ny=3,
    scale=AREA_SCALE,
    label='full Taoyuan lost ponds'
)

new_area_ha_full, new_tiles_full = masked_area_ha_tiled(
    new_water,
    TAOYUAN_BBOX,
    nx=4,
    ny=3,
    scale=AREA_SCALE,
    label='full Taoyuan new water'
)

net_change_ha_full = new_area_ha_full - lost_area_ha_full


# ------------------------------------------------------------
# Focused urbanization corridor
# ------------------------------------------------------------
lost_area_ha_urban, lost_tiles_urban = masked_area_ha_tiled(
    lost_ponds,
    TAOYUAN_URBAN_BBOX,
    nx=4,
    ny=3,
    scale=AREA_SCALE,
    label='urban corridor lost ponds'
)

new_area_ha_urban, new_tiles_urban = masked_area_ha_tiled(
    new_water,
    TAOYUAN_URBAN_BBOX,
    nx=4,
    ny=3,
    scale=AREA_SCALE,
    label='urban corridor new water'
)

net_change_ha_urban = new_area_ha_urban - lost_area_ha_urban


# ------------------------------------------------------------
# Save and display summary
# ------------------------------------------------------------
pond_area_summary = pd.DataFrame([
    {
        'area': 'Full Taoyuan plateau',
        'lost_pond_area_ha': lost_area_ha_full,
        'new_water_area_ha': new_area_ha_full,
        'net_change_ha': net_change_ha_full,
        'area_scale_m': AREA_SCALE,
    },
    {
        'area': 'Urbanization corridor',
        'lost_pond_area_ha': lost_area_ha_urban,
        'new_water_area_ha': new_area_ha_urban,
        'net_change_ha': net_change_ha_urban,
        'area_scale_m': AREA_SCALE,
    },
])

pond_area_csv = OUTPUT_DIR / 'task3_taoyuan_pond_area_summary.csv'
pond_area_summary.to_csv(pond_area_csv, index=False, encoding='utf-8-sig')

print("\nPond change area summary:")
display(pond_area_summary)

print(f"Saved: {pond_area_csv}")

# ============================================================
# T3-4 — Interactive map: water frequency and pond change
# ============================================================
Map_ty = geemap.Map(center=[(TAOYUAN_BBOX[1] + TAOYUAN_BBOX[3]) / 2, (TAOYUAN_BBOX[0] + TAOYUAN_BBOX[2]) / 2], zoom=11)
Map_ty.add_basemap('HYBRID')
Map_ty.addLayer(aoi_taoyuan, {'color': 'white'}, 'Taoyuan AOI')
Map_ty.addLayer(aoi_taoyuan_urban, {'color': 'yellow'}, 'Urbanization corridor')
Map_ty.addLayer(
    water_freq,
    {'min': 0, 'max': 1, 'palette': ['ffffff', 'd0e6ff', '74a9cf', '0570b0', '023858']},
    '26-year water frequency'
)
Map_ty.addLayer(
    pond_change_class,
    {'min': 1, 'max': 2, 'palette': ['red', 'lime']},
    'Pond change: lost=red, new=green'
)
Map_ty

# ============================================================
# T3-5 — Validation with 223 known pond locations
# ============================================================
import json

pond_path = Path(POND_GEOJSON_PATH)

if not pond_path.exists():
    try:
        ensure_package('gdown', 'gdown')
        import gdown
        print(f'Downloading known pond GeoJSON to {pond_path} ...')
        gdown.download(POND_GEOJSON_URL, str(pond_path), quiet=False)
    except Exception as e:
        print('Could not download pond validation data automatically.')
        print('Please manually download the GeoJSON and place it at:', pond_path.resolve())
        print('Error:', repr(e))

pond_detection_rate = np.nan
pond_total = np.nan
pond_detected = np.nan
ponds_fc = None

if pond_path.exists():
    with open(pond_path, encoding='utf-8') as f:
        ponds_geojson = json.load(f)

    pond_features = []
    for feat in ponds_geojson.get('features', []):
        geom = feat.get('geometry', {})
        if geom.get('type') == 'Point':
            coords = geom.get('coordinates')
            pond_features.append(ee.Feature(ee.Geometry.Point(coords), feat.get('properties', {})))

    ponds_fc = ee.FeatureCollection(pond_features)
    pond_total = len(pond_features)
    print(f'Loaded {pond_total} known pond locations')

    validation_samples = recent_water.unmask(0).sampleRegions(
        collection=ponds_fc,
        scale=SCALE,
        geometries=True
    )
    pond_detected = validation_samples.filter(ee.Filter.eq('recent_water', 1)).size().getInfo()
    pond_detection_rate = pond_detected / pond_total * 100 if pond_total else np.nan

    validation_df = pd.DataFrame([{
        'known_ponds': pond_total,
        'mndwi_detected': pond_detected,
        'detection_rate_percent': pond_detection_rate,
        'threshold': WATER_THRESHOLD,
    }])
    validation_csv = OUTPUT_DIR / 'task3_taoyuan_pond_validation_223.csv'
    validation_df.to_csv(validation_csv, index=False, encoding='utf-8-sig')

    print(f'Known ponds: {pond_total}')
    print(f'MNDWI detected: {pond_detected}')
    print(f'Detection rate: {pond_detection_rate:.1f}%')
    print(f'Saved validation table: {validation_csv}')
    display(validation_df)
else:
    print('Validation skipped because pond GeoJSON is not available.')

# ============================================================
# T3-6 — Optional export for Taoyuan water frequency and pond change
# ============================================================
if DO_EXPORT:
    ty_export_img = (water_freq
                     .addBands(lost_ponds.rename('lost_ponds'))
                     .addBands(new_water.rename('new_water'))
                     .addBands(pond_change_class.rename('pond_change_class'))
                     .float()
                     .clip(aoi_taoyuan))
    task_ty = ee.batch.Export.image.toDrive(
        image=ty_export_img,
        description='taoyuan_pond_change_mndwi_week14',
        folder=EXPORT_FOLDER,
        fileNamePrefix='taoyuan_pond_change_mndwi_week14',
        region=aoi_taoyuan,
        scale=SCALE,
        crs=CRS,
        maxPixels=1e13,
    )
    task_ty.start()
    print('Taoyuan export started.')
    print('Task ID:', task_ty.id)
    print('Task status:', task_ty.status())
else:
    print('DO_EXPORT=false, so no Taoyuan export was started.')

# ============================================================
# T3-7 — Auto-generate Markdown answer for Task 3
# Fixed final version
# ============================================================
from IPython.display import Markdown, display
import pandas as pd
import numpy as np


def fmt_ha(x):
    try:
        if x is None or pd.isna(x):
            return "NA"
        return f"{float(x):,.1f}"
    except Exception:
        return "NA"


def fmt_rate(x):
    try:
        if x is None or pd.isna(x):
            return "NA"
        return f"{float(x):.1f}%"
    except Exception:
        return "NA"


lost_full = globals().get("lost_area_ha_full", np.nan)
new_full = globals().get("new_area_ha_full", np.nan)
net_full = globals().get("net_change_ha_full", np.nan)

lost_urban = globals().get("lost_area_ha_urban", np.nan)
new_urban = globals().get("new_area_ha_urban", np.nan)
net_urban = globals().get("net_change_ha_urban", np.nan)

area_scale_used = globals().get("AREA_SCALE", "NA")

pond_detection_rate_value = globals().get("pond_detection_rate", np.nan)
pond_detected_value = globals().get("pond_detected", np.nan)
pond_total_value = globals().get("pond_total", np.nan)

has_validation = False
try:
    has_validation = pd.notna(pond_detection_rate_value)
except Exception:
    has_validation = False

if has_validation:
    validation_text = (
        f"MNDWI 在 223 個已知埤塘中心點中的偵測率為 "
        f"**{fmt_rate(pond_detection_rate_value)}**"
        f"（{int(pond_detected_value)}/{int(pond_total_value)}）。"
    )
else:
    validation_text = (
        "由於尚未成功載入或完成 223 個埤塘驗證點，本次先完成水頻率圖、"
        "埤塘變化圖與面積估算；正式繳交前需補上 detection rate。"
    )

task3_md = f"""
### Task 3 Markdown 作答區：桃園埤塘消失與都市防洪韌性

本分析使用 Landsat {START_YEAR}–{END_YEAR} 年影像計算 MNDWI，並以 **MNDWI > {WATER_THRESHOLD:.2f}** 作為水體判定門檻。為降低 Google Earth Engine 在大範圍面積統計時的記憶體負擔，本次面積估算採用 **{area_scale_used} m** 的統計尺度，但水體判釋與圖層仍以 Landsat 30 m 影像為基礎。

桃園台地全區中，早期為水體、近期轉為非水體的 lost pond area 約為 **{fmt_ha(lost_full)} ha**，新增水體約為 **{fmt_ha(new_full)} ha**，淨變化為 **{fmt_ha(net_full)} ha**。若聚焦於都市化走廊，lost pond area 約為 **{fmt_ha(lost_urban)} ha**，新增水體約為 **{fmt_ha(new_urban)} ha**，淨變化約為 **{fmt_ha(net_urban)} ha**。結果顯示 lost pond area 明顯大於 new water area，代表桃園台地的埤塘景觀在都市化過程中呈現淨損失趨勢。

{validation_text} 未被偵測到的埤塘可能來自三個原因：第一，部分埤塘面積小於 Landsat 30 m 像素，產生 mixed pixel；第二，水面被水生植物、陰影或周邊建物影響，使 MNDWI 值降低；第三，部分埤塘可能具有季節性乾涸或水位變動，年度 median composite 會降低其水體訊號。若要提高偵測率，可以降低 MNDWI 閾值、改用多季節最大水體頻率、結合 Sentinel-2 10 m 影像，或加入人工埤塘向量資料進行 object-based correction。埤塘消失代表都市地景中的滯洪、入滲與蓄水空間減少，可能降低極端降雨下的都市防洪韌性。
"""

display(Markdown(task3_md))

# # Task 4 — Vegetation Resilience Metrics + Summary
#
# **目標：** 定義 baseline、impact、recovery 三個時期，計算地震後植被恢復比率：
#
# \[
# Recovery\ Ratio = \frac{Recovery\ NDVI - Impact\ NDVI}{Baseline\ NDVI - Impact\ NDVI}
# \]
#
# 解讀：
#
# - `RR < 0`：continued degradation
# - `0 ≤ RR < 0.5`：slow / limited recovery
# - `0.5 ≤ RR < 1`：partial recovery
# - `RR ≥ 1`：full recovery or exceeded baseline
#
# 本 notebook 預設使用較精確的地震切分，可由 `.env` 修改日期。

# ============================================================
# T4-1 — Baseline, impact, recovery NDVI composites
# ============================================================
baseline_ndvi = (ndvi_collection
                 .filterDate(BASELINE_START, BASELINE_END)
                 .median()
                 .rename('baseline_ndvi')
                 .clip(aoi))

impact_ndvi = (ndvi_collection
               .filterDate(IMPACT_START, IMPACT_END)
               .median()
               .rename('impact_ndvi')
               .clip(aoi))

recovery_ndvi = (ndvi_collection
                 .filterDate(RECOVERY_START, RECOVERY_END)
                 .median()
                 .rename('recovery_ndvi')
                 .clip(aoi))

print('Baseline period:', BASELINE_START, 'to', BASELINE_END, '(exclusive end)')
print('Impact period:', IMPACT_START, 'to', IMPACT_END, '(exclusive end)')
print('Recovery period:', RECOVERY_START, 'to', RECOVERY_END, '(exclusive end)')

# ============================================================
# T4-2 — Recovery ratio and resilience classes
# ============================================================
numerator = recovery_ndvi.subtract(impact_ndvi)
denominator = baseline_ndvi.subtract(impact_ndvi)

# Use loss-only mask: baseline must be meaningfully higher than impact.
damage_mask = denominator.gt(DAMAGE_THRESHOLD)

recovery_ratio = (numerator.divide(denominator)
                  .updateMask(damage_mask)
                  .rename('recovery_ratio')
                  .clamp(-1, 2)
                  .clip(aoi))

# Class codes: 1 = degrading, 2 = slow recovery, 3 = recovering, 4 = exceeded baseline
resilience_class = (ee.Image(0)
                    .where(recovery_ratio.lt(0), 1)
                    .where(recovery_ratio.gte(0).And(recovery_ratio.lt(0.5)), 2)
                    .where(recovery_ratio.gte(0.5).And(recovery_ratio.lt(1.0)), 3)
                    .where(recovery_ratio.gte(1.0), 4)
                    .updateMask(recovery_ratio.mask())
                    .rename('resilience_class')
                    .clip(aoi))

resilience_labels = {
    1: 'continued degradation (RR < 0)',
    2: 'slow / limited recovery (0–0.5)',
    3: 'partial recovery (0.5–1.0)',
    4: 'full recovery or exceeded baseline (RR ≥ 1)',
}

resilience_stats_df = grouped_area_stats(resilience_class, 'resilience_class', aoi, resilience_labels, scale=SCALE)
resilience_stats_csv = OUTPUT_DIR / 'task4_taroko_resilience_class_stats.csv'
resilience_stats_df.to_csv(resilience_stats_csv, index=False, encoding='utf-8-sig')

print(f'Saved resilience statistics: {resilience_stats_csv}')
display(resilience_stats_df)

# ============================================================
# T4-3 — Interactive map: recovery ratio and resilience classes
# ============================================================
Map_rr = geemap.Map(center=[(TAROKO_BBOX[1] + TAROKO_BBOX[3]) / 2, (TAROKO_BBOX[0] + TAROKO_BBOX[2]) / 2], zoom=10)
Map_rr.add_basemap('HYBRID')
Map_rr.addLayer(aoi, {'color': 'white'}, 'Taroko AOI')
Map_rr.addLayer(
    recovery_ratio,
    {'min': -1, 'max': 2, 'palette': ['8b0000', 'ffcc66', '66bd63', '2b83ba']},
    'Recovery ratio'
)
Map_rr.addLayer(
    resilience_class,
    {'min': 1, 'max': 4, 'palette': ['red', 'yellow', 'green', 'blue']},
    'Resilience class'
)
Map_rr

# ============================================================
# T4-4 — Optional export for recovery ratio map
# ============================================================
if DO_EXPORT:
    rr_export_img = (baseline_ndvi
                     .addBands(impact_ndvi)
                     .addBands(recovery_ndvi)
                     .addBands(recovery_ratio)
                     .addBands(resilience_class)
                     .float()
                     .clip(aoi))
    task_rr = ee.batch.Export.image.toDrive(
        image=rr_export_img,
        description='taroko_recovery_ratio_week14',
        folder=EXPORT_FOLDER,
        fileNamePrefix='taroko_recovery_ratio_week14',
        region=aoi,
        scale=SCALE,
        crs=CRS,
        maxPixels=1e13,
    )
    task_rr.start()
    print('Recovery ratio export started.')
    print('Task ID:', task_rr.id)
    print('Task status:', task_rr.status())
else:
    print('DO_EXPORT=false, so no recovery ratio export was started.')

# ============================================================
# T4-5 — Auto-generate Markdown answer and integration summary
# ============================================================
def get_pct(df, class_code):
    if df is None or len(df) == 0 or class_code not in set(df['class']):
        return 0.0
    return float(df.loc[df['class'] == class_code, 'percent'].iloc[0])

def get_area(df, class_code):
    if df is None or len(df) == 0 or class_code not in set(df['class']):
        return 0.0
    return float(df.loc[df['class'] == class_code, 'area_ha'].iloc[0])

rr_degrade_pct = get_pct(resilience_stats_df, 1)
rr_slow_pct = get_pct(resilience_stats_df, 2)
rr_partial_pct = get_pct(resilience_stats_df, 3)
rr_full_pct = get_pct(resilience_stats_df, 4)
rr_recovering_total_pct = rr_partial_pct + rr_full_pct

rr_degrade_ha = get_area(resilience_stats_df, 1)
rr_slow_ha = get_area(resilience_stats_df, 2)
rr_partial_ha = get_area(resilience_stats_df, 3)
rr_full_ha = get_area(resilience_stats_df, 4)

summary = f"""
### Task 4 Markdown 作答區：植被韌性與跨週整合摘要

本研究以 Landsat {START_YEAR}–{END_YEAR} 年長期資料建立太魯閣 / 秀林研究區的植被韌性監測。方法上，baseline 設為 {BASELINE_START} 至 {BASELINE_END} 前，impact 設為 {IMPACT_START} 至 {IMPACT_END} 前，recovery 設為 {RECOVERY_START} 至 {RECOVERY_END} 前，並以 Recovery Ratio 衡量受損像素是否回到地震前水準。統計結果顯示，在 baseline NDVI 明顯高於 impact NDVI 的受損像素中，約 **{rr_degrade_pct:.1f}%（{rr_degrade_ha:,.1f} ha）** 仍呈 continued degradation，約 **{rr_slow_pct:.1f}%（{rr_slow_ha:,.1f} ha）** 為 slow / limited recovery，約 **{rr_partial_pct:.1f}%（{rr_partial_ha:,.1f} ha）** 為 partial recovery，約 **{rr_full_pct:.1f}%（{rr_full_ha:,.1f} ha）** 已 full recovery 或超過 baseline。合計約 **{rr_recovering_total_pct:.1f}%** 的受損像素具有明顯恢復跡象。

從跨週方法來看，W6 的 Kriging 強調點資料如何推估連續空間分布，而 W14 的長期時序則補上時間維度，兩者合併後能形成 space-time picture。W8 的 single-scene NDVI 只能回答某一時點的植被狀況，W9 的 two-scene change detection 能看見事件前後差異，但 W14 的 26 年 pixel-level trend 能把快照轉成長期電影，辨識一個區域是短期受損、長期恢復，或是持續退化。W10 與 W13 的 SAR 分析可補足山區常見雲遮問題，特別是在颱風或豪雨後，SAR 能提供光學影像缺失時的地表變化線索；W12 的土地覆蓋分類則可利用 W14 匯出的長期 composite 與 trend layer 作為輔助特徵，提高分類的生態解釋力。

W13 Sentinel-2 的優勢是 10 m 解析度，適合觀察小尺度崩塌、道路邊坡與河谷細節；W14 Landsat 的優勢是 26 年時間深度，適合判斷災害是否為長期紀錄中的異常事件。因此，若問題是「哪裡受損最細」，應優先使用 Sentinel-2；若問題是「這個受損是否前所未有、是否正在恢復」，則 Landsat 更有價值。限制方面，Landsat 30 m 會遺失小尺度地貌細節，L7 2003 年後的 SLC-off 條帶可能影響年度合成，且太魯閣山區雲量高，部分年份有效觀測數較少。整體而言，韌性分析能將災害評估從單次損失量提升為恢復能力判斷，對防災管理更接近決策所需。
"""

display(Markdown(summary))

# # Bonus 1 — Multi-Index Dashboard（NDVI + MNDWI + NBR）
#
# 此 bonus 使用前面已經建立好的 `annual_df`，同時繪製 NDVI、MNDWI 與 NBR 的 26 年時序。

# ============================================================
# B1 — Multi-index dashboard
# ============================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
indices = ['NDVI', 'MNDWI', 'NBR']

for ax, idx in zip(axes, indices):
    if idx not in annual_df.columns:
        continue
    df_idx = annual_df.dropna(subset=[idx])
    ax.plot(df_idx['year'], df_idx[idx], linewidth=1.6, marker='o', markersize=4, label=idx)
    ax.axvline(2024, linestyle='--', alpha=0.8, label='2024 earthquake')
    ax.set_ylabel(idx)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

axes[-1].set_xlabel('Year')
axes[-1].set_xticks(years)
axes[-1].tick_params(axis='x', rotation=45)
fig.suptitle(f'Taroko Multi-Index Dashboard ({START_YEAR}–{END_YEAR})', fontsize=14)
plt.tight_layout()

bonus1_path = OUTPUT_DIR / 'bonus1_taroko_multi_index_dashboard.png'
plt.savefig(bonus1_path, dpi=160, bbox_inches='tight')
plt.show()

print(f'Saved bonus figure: {bonus1_path}')

# ============================================================
# B1 answer generator
# ============================================================
index_slopes = {}
for idx in ['NDVI', 'MNDWI', 'NBR']:
    df_idx = annual_df.dropna(subset=[idx])
    if len(df_idx) >= 2:
        s, b = np.polyfit(df_idx['year'].astype(float), df_idx[idx].astype(float), 1)
        index_slopes[idx] = s
    else:
        index_slopes[idx] = np.nan

bonus1_md = f"""
### Bonus 1 Markdown 作答區：多指標儀表板分析

NDVI 的長期斜率為 **{index_slopes['NDVI']:+.5f}/yr**，MNDWI 的長期斜率為 **{index_slopes['MNDWI']:+.5f}/yr**，NBR 的長期斜率為 **{index_slopes['NBR']:+.5f}/yr**。三個指標代表的生態意義不同：NDVI 主要反映植被綠度，NBR 對植被結構受損、裸露地與災後 disturbance 較敏感，MNDWI 則偏向水體或地表濕潤訊號。因此，若三者在 2024 年附近同時出現轉折，代表地震可能同時影響植被覆蓋、裸露地與水文環境；若只有 NDVI 或 NBR 變化，則可能主要是植被與崩塌擾動。對太魯閣山區而言，NDVI 適合作為長期植被恢復的核心指標，但 NBR 可作為災害擾動的輔助判讀指標。
"""

display(Markdown(bonus1_md))

# NBR 在 2021 年後明顯下降，且 2024–2026 維持低值，顯示 NBR 對災害擾動、裸露地或地表水分狀態變化比 NDVI 更敏感。

# # Bonus 2 — NDVI 26-Year Time-Lapse Animation（選做）
#
# 此段會透過 `getThumbURL()` 下載每一年 NDVI 縮圖並合成 GIF。若執行時間太長，可以跳過。
#
# 若要執行，請將下一格中的 `RUN_BONUS2 = False` 改成 `True`。

# ============================================================
# B2 — Optional NDVI time-lapse animation
# ============================================================
RUN_BONUS2 = True

if RUN_BONUS2:
    import io
    import requests
    from PIL import Image, ImageDraw
    import imageio.v2 as imageio

    frames = []
    ndvi_palette = ['brown', 'yellow', 'green', 'darkgreen']

    for year in years:
        composite = ndvi_collection.filterDate(f'{year}-01-01', f'{year + 1}-01-01').median()
        thumb_url = composite.getThumbURL({
            'region': aoi,
            'dimensions': 512,
            'min': 0,
            'max': 0.8,
            'palette': ndvi_palette,
        })
        response = requests.get(thumb_url, timeout=60)
        img = Image.open(io.BytesIO(response.content)).convert('RGB')
        draw = ImageDraw.Draw(img)
        label = str(year) + (' ★ Earthquake' if year == 2024 else '')
        draw.rectangle((6, 6, 230, 34), fill=(0, 0, 0))
        draw.text((12, 12), label, fill=(255, 255, 255))
        frames.append(np.array(img))
        print(f'{year}: OK')

    gif_path = OUTPUT_DIR / 'bonus2_taroko_ndvi_26yr_timelapse.gif'
    imageio.mimsave(gif_path, frames, duration=0.8, loop=0)
    print(f'Saved GIF: {gif_path}')
else:
    print('Bonus 2 skipped. Set RUN_BONUS2=True to generate the GIF.')

# # Bonus 3 — Landsat × Sentinel-2 Cross-Sensor Change Detection（方法框架）
#
# 此段提供 bonus 3 的可擴充框架。由於 Sentinel-2 L2A 讀取與跨感測器比較較耗時，建議在完成 core tasks 後再執行。
#
# 作答重點：
#
# 1. Landsat 適合長期趨勢，Sentinel-2 適合事件細節。
# 2. 2017–2026 是兩者可重疊比較的區間。
# 3. Sentinel-2 NDVI 可能較高，原因是 10 m 像素較純，較不容易混入裸地、道路或陰影。
# 4. 對地震損害面積，30 m Landsat 會平滑化小面積崩塌，10 m Sentinel-2 通常能抓到更細碎的受損斑塊。

# # Final Short Reflection（100–200 字）
#
# 從 W13 的 6 年 Sentinel-2 到 W14 的 26 年 Landsat，我最大的感受是時間尺度會改變我們對災害的判斷。6 年資料能看見 2024 地震前後的短期變化，但 26 年資料能判斷這次變化是否真的是長期異常，或只是山區生態系在多次颱風、崩塌與恢復循環中的一部分。本次太魯閣 / 秀林研究區的長期 NDVI 斜率約為 +0.00279 NDVI/year，顯示整體具有 greening trend；但 recovery ratio 也顯示仍有部分受損像素恢復有限，代表長期趨勢和災後局部衝擊必須一起判讀。「韌性」在防災管理中很重要，因為它不只問災害造成多少損失，也問系統是否有能力恢復、哪些地方恢復較慢、哪些地方可能需要優先治理。從 W8 到 W14，ARIA 系統逐漸從單張影像判讀，發展成支援長期監測與決策的韌性分析工具。
