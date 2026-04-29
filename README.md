# Week 10 ARIA v7.0 — All-Weather Flood Auditor

本專案為 **NTU Remote Sensing & Spatial Information Analysis Week 10 Homework**，主題是建立 **ARIA v7.0 — The All-Weather Auditor**。本專案以 2025 年 11 月鳳凰颱風後，花蓮馬太鞍溪堰塞湖溢流事件為案例，整合 **Sentinel-1 SAR 雷達資料**、**Sentinel-2 光學 NDWI** 與 **Copernicus DEM 坡度地形校正**，建立多源感測器融合的淹水偵測與確信度分級圖。

相較於 Week 9 的 optical-only ARIA v6.0，本週的重點是加入 SAR 的全天候偵測能力，使系統在颱風期間即使受到雲遮影響，仍能透過雷達後向散射辨識可能淹水區域。

---

## Project Overview

本專案完成以下四個主要任務：

1. **SAR All-Weather Flood Detection**  
   使用 Planetary Computer STAC API 讀取 Sentinel-1 RTC VV band，將線性後向散射轉換為 dB，並透過 median filter、thresholding、morphological cleanup 與 connected component filtering 偵測可能淹水區。

2. **Sensor Fusion Confidence Map**  
   整合 Sentinel-2 NDWI 光學水體偵測結果、SCL cloud mask 與 SAR flood mask，建立四分類確信度圖：
   - High Confidence — SAR + Optical
   - SAR Only — cloudy / review
   - Optical Only — manual review
   - No Detection

3. **Topographic Audit with DEM and Slope**  
   使用 Copernicus DEM 計算坡度，將 slope > 25° 的 SAR / fusion detections 視為可能地形誤報，進行 topographic filtering，降低山區 layover、shadow 或 steep terrain false positives。

4. **AI Strategic Briefing and W9/W10 Comparison**  
   將 ARIA v7.0 的輸出結果提供給 LLM，生成災害應變策略簡報，並與 Week 9 optical-only 結果比較。

---

## Study Area

研究區涵蓋花蓮馬太鞍溪流域、萬榮鄉、光復鄉與鳳林鎮一帶。

```python
HUALIEN_BBOX = [121.2574, 23.6546, 121.4984, 23.7447]
```

時間範圍：

```python
PRE_DATE_RANGE  = "2025-10-01/2025-11-05"
POST_DATE_RANGE = "2025-11-12/2025-11-30"
```

---

## Key Methods

### Sentinel-1 SAR Flood Detection

SAR 的 VV backscatter 會受到地表粗糙度與水面鏡面反射影響。平滑水面通常會將雷達能量反射 away from the sensor，因此在 VV dB 影像中呈現低回波暗色區。本專案使用以下流程偵測 SAR flood mask：

```python
vv_db = 10 * np.log10(vv_linear)
vv_filtered = median_filter(vv_db, size=5)
flood_mask = vv_filtered < SAR_THRESHOLD
```

本次使用：

```python
SAR_THRESHOLD = -18.0  # dB
```

選擇此 threshold 的原因是：低 VV backscatter 代表可能的平滑水面，並且透過 histogram 判斷 -18 dB 可作為較保守的 cutoff，再搭配 morphology cleanup 移除雜訊。

### Optical NDWI Detection

NDWI 使用 Green 與 NIR band 計算：

```python
NDWI = (Green - NIR) / (Green + NIR)
```

本次使用：

```python
NDWI_THRESHOLD = 0.0
```

由於颱風淹水常含有泥沙，水體可能較混濁，因此使用比清水預設值 0.3 更低的 threshold。

### Topographic Filtering

坡度過大的區域通常不可能形成穩定積水，因此使用 DEM 計算 slope 並排除陡坡誤報：

```python
SLOPE_THRESHOLD = 25.0  # degrees
```

---

## Main Results

### Final Topographic-Corrected ARIA v7.0 Results

| Class | Area (km²) | Interpretation |
|---|---:|---|
| High Confidence — SAR + Optical | 0.955 | 雙感測器皆偵測到水體，最適合作為優先應變區 |
| SAR Only — cloudy / review | 0.163 | SAR 偵測但光學未確認，需現地或無人機複查 |
| Optical Only — manual review | 15.304 | 光學偵測區，可能包含混濁水、濕泥沙或光譜混淆，需人工判讀 |
| False positives removed by topographic filter | 6.307 | 由 slope > 25° 排除之地形誤報 |

Additional parameters:

| Parameter | Value |
|---|---:|
| Cloud cover percentage | 7.46% |
| SAR threshold | -18.0 dB |
| NDWI threshold | 0.0 |
| Slope threshold | 25.0° |

---

## Week 9 vs Week 10 Comparison

| Metric | Week 9 Optical Only | Week 10 Fused Final | Interpretation |
|---|---:|---:|---|
| Total detected / review area | 24.732 km² | 16.422 km² | W10 經過 SAR fusion 與 slope filtering 後，面積較小但品質控制較完整 |
| Cloud-covered area analyzed | 0.000 km² | 0.163 km² | W10 透過 SAR 增加雲下偵測能力 |
| False positives removed | 54.494 km² phantom-water artifacts | 6.307 km² steep-slope detections | W9 與 W10 都顯示 QA/QC 對災害判釋非常重要 |
| Confidence levels | 3-zone | 4-class | W10 將 evidence source 分得更細，較適合應變決策 |

---

## Figures

主要輸出圖包含：

```text
outputs/
├── task1_sar_2x2_detection.png
├── task1_sar_histogram_threshold.png
├── task2_fusion_confidence_map.png
├── task3_before_topographic_correction.png
├── task3_after_topographic_correction.png
└── task3_dem_slope_maps.png
```

若圖片已放入 `outputs/` 資料夾，可在 GitHub README 中顯示：

```markdown
![Task 1 SAR Detection](outputs/task1_sar_2x2_detection.png)
![Task 2 Fusion Confidence Map](outputs/task2_fusion_confidence_map.png)
![Task 3 DEM and Slope](outputs/task3_dem_slope_maps.png)
```

---

## Repository Structure

建議的 GitHub 專案結構如下：

```text
Week10_ARIA_v70/
├── README.md
├── Week10_ARIA_v70_hankc.ipynb
├── .env.example
├── requirements.txt
├── outputs/
│   ├── task1_sar_2x2_detection.png
│   ├── task1_sar_histogram_threshold.png
│   ├── task2_fusion_confidence_map.png
│   ├── task3_before_topographic_correction.png
│   ├── task3_after_topographic_correction.png
│   ├── task3_dem_slope_maps.png
│   ├── task1_sar_stats.csv
│   ├── task2_fusion_area_stats.csv
│   ├── task3_fusion_topo_corrected_stats.csv
│   ├── task3_slope_false_positive_removed.csv
│   └── task4_w9_w10_comparison.csv
└── .gitignore
```

---

## Environment Setup

建議使用 conda 或 venv 建立獨立環境。

```bash
conda create -n aria-v70 python=3.11 -y
conda activate aria-v70
pip install -r requirements.txt
```

若沒有 `requirements.txt`，可先安裝以下套件：

```bash
pip install numpy pandas matplotlib scipy scikit-image rasterio rioxarray xarray geopandas shapely pystac-client planetary-computer stackstac python-dotenv
```

---

## `.env.example`

請勿將真正的 `.env` 上傳到 GitHub。可以建立 `.env.example` 供他人參考：

```env
# Study area
BBOX_WEST=121.2574
BBOX_SOUTH=23.6546
BBOX_EAST=121.4984
BBOX_NORTH=23.7447

# Date ranges
PRE_DATE_RANGE=2025-10-01/2025-11-05
POST_DATE_RANGE=2025-11-12/2025-11-30

# Thresholds
SAR_THRESHOLD=-18.0
NDWI_THRESHOLD=0.0
SLOPE_THRESHOLD=25.0
MIN_WATER_PIXELS=50

# STAC settings
STAC_ENDPOINT=https://planetarycomputer.microsoft.com/api/stac/v1
S1_COLLECTION=sentinel-1-rtc
S2_COLLECTION=sentinel-2-l2a
DEM_COLLECTION=cop-dem-glo-30
TARGET_EPSG=32651
```

`.gitignore` 建議加入：

```gitignore
.env
.ipynb_checkpoints/
__pycache__/
*.tif
*.tiff
*.nc
*.zip
```

---

## How to Run

1. Clone repository:

```bash
git clone https://github.com/YOUR_USERNAME/Week10_ARIA_v70.git
cd Week10_ARIA_v70
```

2. Create environment and install packages:

```bash
conda create -n aria-v70 python=3.11 -y
conda activate aria-v70
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

4. Open notebook:

```bash
jupyter notebook Week10_ARIA_v70_hankc.ipynb
```

5. Run all cells from top to bottom.

---

## Notes on Interpretation

本專案結果應被視為 **decision-support layer**，而不是最終災損清冊。原因包括：

1. SAR threshold-based flood detection 可能受到 speckle、地形陰影、layover、smooth non-water surfaces 影響。
2. Optical NDWI 在混濁水、濕泥沙、陰影與裸露地表附近可能產生誤判。
3. Copernicus DEM 可能無法完全反映災後崩塌、土石流堆積或河道改變後的新地形。
4. 最終應變決策仍需結合現地回報、無人機影像、道路封閉資料、雨量與水位資料。

---

## Operational Summary

ARIA v7.0 支持以下應變策略：

- **High Confidence zones**：優先進行撤離、封路與資源部署。
- **SAR Only zones**：因 SAR 可穿透雲層，應視為高優先複查區，適合派遣無人機或地面巡查。
- **Optical Only zones**：需人工判讀與交叉驗證，避免將濕泥沙或光譜混淆直接解讀為確定淹水。
- **Steep-slope detections**：應透過 DEM slope audit 或 morphology cleaning 排除不合理水體。

---

## Author

**Hank / Po-Wei Huang**  
Course: NTU Remote Sensing & Spatial Information Analysis  
Assignment: Week 10 Homework — ARIA v7.0

---

## Acknowledgement

This project uses open satellite data and cloud-native geospatial workflows provided by:

- Microsoft Planetary Computer STAC API
- Sentinel-1 RTC
- Sentinel-2 L2A
- Copernicus DEM

---

## Disclaimer

This repository is created for academic coursework. The mapped flood extent and operational briefing are for educational analysis only and should not be used as an official emergency response product without field validation and expert review.
