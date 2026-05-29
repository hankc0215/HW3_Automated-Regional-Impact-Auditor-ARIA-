# Week 14 Homework — ARIA v9.5: The Resilience Monitor

## 專案概述

本專案使用 Google Earth Engine (GEE) 與 Landsat Collection 2 Level 2 資料，進行 2000–2026 年長期植被趨勢分析、桃園埤塘消失監測，以及太魯閣地震後植被韌性評估。

### 資料來源
- **衛星資料**: Google Earth Engine Landsat Collection 2 Level 2 Surface Reflectance
- **研究區域**: 
  - 太魯閣/秀林地區 (Taroko/Xiulin)
  - 桃園台地 (Taoyuan Plateau)
- **時間範圍**: 2000–2026 年

### 主要功能

#### Task 1: Landsat Harmonization + 26-Year NDVI Time Series
- 合併 Landsat 5/7/8/9 四代衛星影像
- 進行波段調和 (Band Harmonization)
- 計算年度 NDVI 平均值並繪製長期趨勢圖
- 標記 2024 年花蓮地震事件

#### Task 2: Pixel-Level Linear Trend Analysis
- 使用 `ee.Reducer.linearFit()` 進行像素級 NDVI 線性趨勢分析
- 分類為 greening、browning、stable 三類
- 統計各類別面積與百分比
- 匯出 NDVI 趨勢圖至 Google Drive

#### Task 3: Taoyuan Pond Disappearance with MNDWI
- 使用 MNDWI (Modified Normalized Difference Water Index) 偵測水體
- 比較 2000–2005 與 2021–2026 水體變化
- 計算消失埤塘與新增水體面積
- 使用 223 個桃園埤塘 GeoJSON 進行驗證

#### Task 4: Taroko Earthquake Vegetation Recovery Resilience Analysis
- 計算地震後植被恢復比率 (Recovery Ratio)
- 產生韌性地圖 (Resilience Map)
- 統計不同恢復程度的面積分布
- 撰寫 300–500 字整合摘要

## 環境設定

### 必要套件
```bash
pip install earthengine-api geemap pandas numpy matplotlib
```

### .env 檔案設定
複製 `.env.example` 為 `.env` 並填入以下參數：

```bash
GEE_PROJECT_ID=your-project-id
EXPORT_FOLDER=GEE_Exports
DO_EXPORT=false
START_YEAR=2000
END_YEAR=2026
SCALE=30
CRS=EPSG:32651
WATER_THRESHOLD=0.1
GREENING_THRESHOLD=0.001
DAMAGE_THRESHOLD=0.05
BASELINE_START=2020-01-01
BASELINE_END=2024-04-03
IMPACT_START=2024-04-03
IMPACT_END=2025-01-01
RECOVERY_START=2025-06-01
RECOVERY_END=2026-04-01
```

**注意**: 
- `DO_EXPORT=false` 時不會啟動 Google Drive 匯出
- 最後一次正式執行前請將 `DO_EXPORT` 改為 `true`

## 執行方式

1. 確保已安裝必要套件
2. 設定 `.env` 檔案
3. 執行 Jupyter Notebook:
```bash
jupyter notebook Week14_ARIA_v95_Resilience_Monitor.ipynb
```

4. 首次執行時會要求進行 Google Earth Engine 認證

## 輸出檔案

所有輸出檔案會儲存在 `outputs/` 資料夾：

- `task1_taroko_annual_indices_2000_2026.csv` - 年度 NDVI/MNDWI/NBR 統計表
- `task1_taroko_ndvi_trend_2000_2026.png` - NDVI 長期趨勢圖
- `task2_taroko_ndvi_trend_class_stats.csv` - 趨勢分類統計表
- `task3_taoyuan_pond_area_summary.csv` - 桃園埤塘面積變化統計
- `task4_taroko_resilience_stats.csv` - 太魯閣韌性統計表
- 其他分析圖表與 GeoTIFF 檔案

## 技術細節

### Landsat Harmonization
不同 Landsat 世代的波段編號不同，本專案將其統一為共同名稱：
- L5/L7: SR_B1, SR_B2, SR_B3, SR_B4, SR_B5, SR_B7 → Blue, Green, Red, NIR, SWIR1, SWIR2
- L8/L9: SR_B2, SR_B3, SR_B4, SR_B5, SR_B6, SR_B7 → Blue, Green, Red, NIR, SWIR1, SWIR2

反射率校正式：
```
Reflectance = DN × 0.0000275 - 0.2
```

### 雲遮罩
使用 QA_PIXEL 的 bit 3 (cloud) 與 bit 4 (cloud shadow) 移除雲層與雲影。

### 指數計算
- **NDVI** = (NIR - Red) / (NIR + Red)
- **MNDWI** = (Green - SWIR1) / (Green + SWIR1)
- **NBR** = (NIR - SWIR2) / (NIR + SWIR2)

## 作業交付檢查表

- [x] Task 1：Landsat harmonization + 26 年 NDVI 時序圖
- [x] Task 2：像素級 NDVI 線性趨勢圖 + greening / browning / stable 統計
- [x] Task 3：桃園埤塘 MNDWI 水頻率圖、消失 / 新增水體面積、223 埤塘驗證
- [x] Task 4：太魯閣地震後植被 recovery ratio 韌性圖 + 統計 + 300–500 字整合摘要
- [x] Google Drive 匯出 GeoTIFF 截圖
- [x] 100–200 字簡短心得

## 作者
Week 14 Satellite Remote Sensing Homework

## 授權
本專案僅供學術研究使用
