# ARIA v9.0 — The Cloud Engine  
## Cloud-Scale Vegetation Trend Analysis for Xiulin / Taroko AOI

本專案為「遙測與空間資訊之分析與應用」Week 13 Homework，主題為 **ARIA v9.0 — The Cloud Engine**。  
本週將前幾週以單張影像或少量影像為主的 ARIA workflow，升級為使用 **Google Earth Engine (GEE)** 進行雲端時序分析，針對花蓮秀林／太魯閣山區進行 2020–2026 年植被變化與災害事件影響分析。

分析重點包含：

1. Sentinel-2 NDVI 月均時序分析  
2. 震前、震後、堰塞湖事件後的 median composite 比較  
3. Sentinel-1 SAR VV backscatter 時序分析  
4. GeoTIFF 匯出與 W8–W12 ARIA workflow 整合  
5. Bonus：InSAR 干涉圖判讀與 NDVI time-lapse GIF 製作  

---

## 1. Project Overview

過去 W8–W12 的 ARIA 分析多以「snapshot」為主，例如單景 NDVI、兩景差值、單次 SAR 穿雲分析或單張影像分類。  
本專案將分析尺度提升到 **ImageCollection time series**，使用 Google Earth Engine 在雲端處理大量 Sentinel-2 與 Sentinel-1 影像，觀察太魯閣／秀林山區在 2024/04/03 花蓮地震前後，以及後續堰塞湖相關事件後的植被與地表散射變化。

研究區為花蓮秀林／太魯閣山區，與課堂示範的花蓮市平原區不同。山區受地形、雲量、坡向與災害擾動影響較明顯，因此更適合透過時序資料觀察長期趨勢。

---

## 2. Study Area

**Study Area:** Xiulin / Taroko, Hualien, Taiwan  
**AOI BBOX:**  

```python
[121.34526379253053, 24.046021742135874, 121.85149217685861, 24.35767637905926]
```

BBOX 格式為：

```text
[west, south, east, north]
```

---

## 3. Data Sources

| Dataset | GEE Collection ID | Resolution | Purpose |
|---|---|---:|---|
| Sentinel-2 L2A | `COPERNICUS/S2_SR_HARMONIZED` | 10 m | NDVI time series and composite analysis |
| Sentinel-1 GRD | `COPERNICUS/S1_GRD` | 10 m | SAR VV backscatter time series |
| SRTM DEM | `USGS/SRTMGL1_003` | 30 m | Elevation context |

---

## 4. Repository Structure

建議專案結構如下：

```text
Week13_ARIA_v9_CloudEngine/
│
├── Week13_ARIA_v9_CloudEngine_executable.ipynb
├── README.md
├── .env.example
├── .gitignore
│
├── outputs/
│   ├── task1_monthly_ndvi_2020_2026.csv
│   ├── task1_ndvi_time_series.png
│   ├── task2_delta_ndvi_loss_area.csv
│   ├── task2_ndvi_composite_delta_map.html
│   ├── task3_sentinel1_vv_time_series.csv
│   ├── task3_s1_vv_time_series.png
│   ├── task3_sar_delta_vv_high_conf_map.html
│   ├── task4_integration_summary.md
│   └── taroko_ndvi_timelapse.gif
│
└── screenshots/
    └── gee_exports_drive_screenshot.png
```

`.env` 不建議上傳到 GitHub，因為裡面可能包含個人的 GEE Project ID。請只上傳 `.env.example`。

---

## 5. Environment Setup

### 5.1 Python Packages

建議使用 Google Colab 或本機 Jupyter Notebook 執行。主要套件包含：

```bash
pip install earthengine-api geemap python-dotenv pandas numpy matplotlib pillow imageio requests
```

若使用 Google Colab，多數套件已預裝；若缺少套件，notebook 內可直接安裝。

---

### 5.2 Google Earth Engine Authentication

第一次執行時需要登入 Google Earth Engine：

```python
import ee

ee.Authenticate()
ee.Initialize(project="your-gee-project-id")
```

本專案已改為使用 `.env` 管理 GEE Project ID，不會將 project ID 寫死在 notebook 中。

---

### 5.3 `.env` Configuration

請複製 `.env.example`，並重新命名為 `.env`：

```bash
cp .env.example .env
```

`.env` 範例：

```env
GEE_PROJECT_ID=your-gee-project-id

TAROKO_BBOX=121.34526379253053,24.046021742135874,121.85149217685861,24.35767637905926

S2_START_DATE=2020-01-01
S2_END_DATE=2026-03-31
S2_CLOUDY_PIXEL_PERCENTAGE=40

S1_START_DATE=2022-01-01
S1_END_DATE=2026-03-31

EXPORT_FOLDER=GEE_Exports
RUN_EXPORTS=false
```

若要實際匯出 GeoTIFF 至 Google Drive，請將：

```env
RUN_EXPORTS=true
```

執行完匯出後，建議再改回：

```env
RUN_EXPORTS=false
```

避免重複送出 GEE export tasks。

---

## 6. Methods

### Task 1 — NDVI Time Series Analysis

使用 Sentinel-2 L2A 影像建立 2020–2026 年的月均 NDVI 時序。  
處理流程如下：

1. 依 AOI、日期與雲量比例篩選 Sentinel-2 ImageCollection  
2. 使用 SCL band 進行雲遮罩  
3. 計算 NDVI：  

```text
NDVI = (NIR - Red) / (NIR + Red)
```

4. 依月份進行 median composite  
5. 對 AOI 取 mean NDVI  
6. 繪製 2020–2026 月均 NDVI 時序圖  
7. 標記 2024/04/03 花蓮地震時間點  

輸出：

```text
outputs/task1_monthly_ndvi_2020_2026.csv
outputs/task1_ndvi_time_series.png
```

---

### Task 2 — Pre/Post Earthquake Median Composite

使用 Sentinel-2 NDVI collection 建立三個階段的 median composite：

| Phase | Date Range | Meaning |
|---|---|---|
| Pre-earthquake | 2023-01-01 to 2024-03-31 | 地震前背景狀態 |
| Post-earthquake | 2024-04-01 to 2024-09-30 | 地震後短期變化 |
| Post-dam | 2025-10-01 to 2026-03-31 | 堰塞湖事件後狀態 |

接著計算三組 ΔNDVI：

```python
delta_eq = post_eq - pre_eq
delta_dam = post_dam - post_eq
delta_total = post_dam - pre_eq
```

以 `ΔNDVI < -0.15` 作為 vegetation loss threshold，估算植被損失面積。

輸出：

```text
outputs/task2_delta_ndvi_loss_area.csv
outputs/task2_ndvi_composite_delta_map.html
```

---

### Task 3 — Sentinel-1 SAR VV Time Series

使用 Sentinel-1 GRD 影像進行 SAR VV backscatter 時序分析。  
篩選條件包括：

```text
instrumentMode = IW
orbitProperties_pass = DESCENDING
polarisation = VV
```

分析內容包含：

1. 2022–2026 年 Sentinel-1 VV 時序  
2. 震前與震後 VV median composite  
3. ΔVV map  
4. 光學 NDVI 與 SAR VV 的交叉比對  

高信心變化區定義為：

```text
ΔNDVI < -0.15 AND |ΔVV| > 2 dB
```

輸出：

```text
outputs/task3_sentinel1_vv_time_series.csv
outputs/task3_s1_vv_time_series.png
outputs/task3_sar_delta_vv_high_conf_map.html
```

---

### Task 4 — GeoTIFF Export and Integration Summary

使用 GEE Export API 將至少兩個產品匯出至 Google Drive：

1. Post-earthquake NDVI composite  
2. Earthquake ΔNDVI map  

範例匯出設定：

```python
ee.batch.Export.image.toDrive(
    image=post_eq,
    description="taroko_ndvi_post_eq_2024",
    folder="GEE_Exports",
    region=aoi,
    scale=10,
    crs="EPSG:32651",
    maxPixels=1e9
)
```

輸出產品可作為後續 W12 Random Forest classification 或其他 GIS 分析的輸入資料。

---

## 7. Key Results

### 7.1 Data Scale

本次分析處理：

| Dataset | Number of Images |
|---|---:|
| Sentinel-2 L2A | 291 |
| Sentinel-1 GRD | 146 |

若改成本機下載與逐張處理，估計需花費數小時至十多小時，且尚未包含下載失敗、雲遮罩、重投影、裁切與硬碟空間管理成本。GEE 可直接在雲端完成 ImageCollection 篩選、Reducer、median composite 與匯出，大幅降低資料處理負擔。

---

### 7.2 NDVI Time Series

NDVI 月均時序顯示太魯閣／秀林山區具有明顯季節性起伏。部分月份因山區雲量、梅雨或颱風季影響，可能出現缺值或單月可用影像數偏少的情況。

震後時序中可見 NDVI 波動增加，部分月份出現明顯低值，但單月低值不應直接解釋為地震造成，仍需搭配 Task 2 的 composite-based ΔNDVI 進行判斷。

---

### 7.3 Vegetation Loss Area

以 `ΔNDVI < -0.15` 作為植被損失門檻，估算結果如下：

| Change Phase | Vegetation Loss Area |
|---|---:|
| Earthquake impact | 7740.15 ha |
| Post-dam change | 6257.68 ha |
| Total change | 6839.04 ha |

注意：`total change` 並不是前兩階段面積相加，而是直接比較 `post_dam - pre_eq`。因此若中間有部分區域恢復，或不同階段損失位置不完全重疊，總累積損失面積可能小於兩階段面積總和。

---

### 7.4 SAR VV Time Series

Sentinel-1 VV backscatter 時序提供光學 NDVI 之外的地表散射變化證據。  
SAR 對雲霧較不敏感，因此可補足 Sentinel-2 在多雲山區的限制。若某些區域同時符合 `ΔNDVI < -0.15` 與 `|ΔVV| > 2 dB`，表示該區域同時出現植被衰退與雷達散射變化，可視為較高信心的災害或地表擾動區。

---

## 8. Bonus Outputs

### Bonus 1 — InSAR Interferogram Reading

本專案包含 InSAR 干涉圖判讀練習，重點在於理解干涉環數量、半波長位移量、LOS displacement 與 SAR amplitude analysis 的差異。

SAR 振幅分析能看出地表散射強弱變化，但 InSAR 干涉圖能進一步提供地表位移方向與位移量估算，這是單純 backscatter change detection 難以做到的。

---

### Bonus 2 — NDVI Time-Lapse GIF

使用半年度 NDVI composite 製作 2020–2026 年 NDVI time-lapse animation：

```text
outputs/taroko_ndvi_timelapse.gif
```

動畫能以連續視覺化方式呈現季節循環、地震後變化、堰塞湖事件後狀態與可能的植被恢復趨勢。  
圖中紅棕色通常代表低 NDVI 區域，例如水體、裸露地或低植被覆蓋區；綠色則代表植被覆蓋較高區域。

---

## 9. How to Run

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/Week13_ARIA_v9_CloudEngine.git
cd Week13_ARIA_v9_CloudEngine
```

### Step 2 — Create `.env`

```bash
cp .env.example .env
```

Edit `.env` and fill in your GEE Project ID:

```env
GEE_PROJECT_ID=your-gee-project-id
```

### Step 3 — Run Notebook

Open the notebook:

```text
Week13_ARIA_v9_CloudEngine_executable.ipynb
```

Run all cells from top to bottom.

### Step 4 — Export GeoTIFF

If GeoTIFF export is required, set:

```env
RUN_EXPORTS=true
```

Then run the export cells.  
After the tasks finish, check Google Drive:

```text
Google Drive / GEE_Exports/
```

Take a screenshot of the exported `.tif` files for homework submission.

---

## 10. Notes and Limitations

1. **Cloud contamination:**  
   太魯閣山區雲量高，部分月份可能資料不足。即使使用 SCL cloud mask，仍可能有殘留雲、陰影或 haze 影響 NDVI。

2. **AOI-level mean may smooth local damage:**  
   月均 NDVI 是整個 AOI 的平均，可能會稀釋局部崩塌或河谷變化。因此需要搭配 ΔNDVI map 觀察空間分布。

3. **SAR interpretation is not always straightforward:**  
   VV backscatter 可能受到坡向、入射角、地形陰影、土壤濕度與植被結構影響。ΔVV 應與 NDVI、DEM 或現地資料交叉判讀。

4. **GEE export is asynchronous:**  
   `task.start()` 只代表送出匯出任務，不代表檔案已完成。需到 GEE Tasks 或 Google Drive 確認結果。

5. **GEE vs local workflow:**  
   GEE 適合大範圍、長時序、標準化流程；若需要高度客製化模型、完整中間資料控制或大量非 GEE 資料整合，仍可使用 STAC API 加本機處理流程。

---

## 11. Suggested `.gitignore`

建議加入以下 `.gitignore`，避免誤傳私人設定與暫存資料：

```gitignore
# Environment variables
.env

# Jupyter
.ipynb_checkpoints/

# Python cache
__pycache__/
*.pyc

# Large outputs
*.tif
*.tiff
*.zip

# OS files
.DS_Store
Thumbs.db
```

---

## 12. Assignment Submission Checklist

- [x] Notebook with Task 1–4 code and results  
- [x] NDVI monthly time series plot  
- [x] NDVI composite and ΔNDVI map  
- [x] ΔNDVI vegetation loss area table  
- [x] Sentinel-1 VV time series plot  
- [x] SAR ΔVV and high-confidence change map  
- [x] Integration summary report  
- [x] NDVI time-lapse GIF  
- [ ] Google Drive GeoTIFF export screenshot  

---

## 13. Author

Created for NTU Remote Sensing & Spatial Information Analysis — Week 13 Homework.

