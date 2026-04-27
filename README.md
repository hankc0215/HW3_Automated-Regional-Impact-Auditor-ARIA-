# Week 9 ARIA v6.0 — The Validated Auditor

本專案為 **NTU Remote Sensing & Spatial Information Analysis Week 9 Homework**，主題是以 Sentinel-2 L2A 影像分析 **Matai'an Barrier Lake（馬太鞍堰塞湖）** 事件，從 Week 8 的目視判釋進一步發展成具有驗證資料、精度評估與信心度分區的定量化災害評估流程。

本 notebook 的核心目標是建立一套 **ARIA v6.0: Automated Remote Imaging Auditor** 工作流程，包含：

1. 多光譜變異檢測（ΔNDVI、ΔNDWI、ΔBSI）
2. SCL 雲與陰影遮罩（cloud masking）
3. threshold optimization
4. confusion matrix 與 accuracy metrics
5. phantom water error case 比較
6. confidence zone map
7. Week 8 eyewitness impact table cross-reference
8. AI advisor operational assessment

---

## 專案成果摘要

本次執行使用三期 Sentinel-2 L2A 影像：

| Scene | Sentinel-2 Item ID |
|---|---|
| Pre-event | `S2A_MSIL2A_20250615T023141_R046_T51QUG_20250615T070417` |
| Mid-event | `S2C_MSIL2A_20250911T022551_R046_T51QUG_20250911T055914` |
| Post-event | `S2B_MSIL2A_20251016T022559_R046_T51QUG_20251016T042804` |

主要驗證結果如下：

| Metric | Value |
|---|---:|
| Best ΔNDVI threshold | `-0.20` |
| Overall Accuracy (OA) | `0.787` |
| Producer's Accuracy (PA) | `0.571` |
| User's Accuracy (UA) | `0.923` |
| F1-score | `0.706` |
| Kappa | `0.553` |

Confidence zone 面積統計：

| Zone | Area |
|---|---:|
| High Confidence | `15.03 km²` |
| Low Confidence | `9.70 km²` |
| No Detection | `394.79 km²` |
| Total valid study area | `419.52 km²` |

整體結果顯示，模型對「已偵測為變化區」具有高可信度（UA = 0.923），但仍可能漏掉部分實際變化區（PA = 0.571）。因此，本分析適合用於 **preliminary disaster screening、priority inspection planning、monitoring support**，但不應單獨作為最終撤離或安全決策依據。

---

## Repository Structure

建議 GitHub 專案結構如下：

```text
HW9/
├── README.md
├── Week9_ARIA_v60_Notebook_Structure.ipynb
├── Homework-Week9.md
├── .env.example
├── data/
│   ├── validation_points.geojson
│   └── impact_table_w8.csv
├── outputs/
│   ├── task1_difference_layer_statistics.csv
│   ├── task1_difference_maps_2x2.png
│   ├── task2_threshold_sweep.csv
│   ├── task2_threshold_vs_metrics.png
│   ├── task3_accuracy_metrics.csv
│   ├── task3_confusion_matrix.png
│   ├── task4_confidence_zone_area.csv
│   ├── task4_confidence_zone_map.png
│   └── task4_phantom_water_comparison.png
└── requirements.txt
```

> 注意：實際 `.env` 檔案不要上傳到 GitHub。請使用 `.env.example` 作為範本。

---

## Environment Setup

建議使用 conda 建立環境：

```bash
conda create -n geo-risk python=3.11
conda activate geo-risk
```

安裝需要的套件：

```bash
pip install numpy pandas matplotlib geopandas xarray rioxarray rasterio pyogrio scikit-learn python-dotenv pystac-client planetary-computer stackstac
```

如果需要在 notebook 中顯示圖表與互動環境，也建議安裝：

```bash
pip install jupyter ipykernel
python -m ipykernel install --user --name geo-risk --display-name "Python (geo-risk)"
```

---

## `.env` Configuration

請在專案根目錄建立 `.env`，內容如下：

```bash
STAC_ENDPOINT=https://planetarycomputer.microsoft.com/api/stac/v1
S2_COLLECTION=sentinel-2-l2a

PRE_ITEM_ID=S2A_MSIL2A_20250615T023141_R046_T51QUG_20250615T070417
MID_ITEM_ID=S2C_MSIL2A_20250911T022551_R046_T51QUG_20250911T055914
POST_ITEM_ID=S2B_MSIL2A_20251016T022559_R046_T51QUG_20251016T042804

BBOX_WEST=121.28
BBOX_SOUTH=23.56
BBOX_EAST=121.52
BBOX_NORTH=23.76

TARGET_EPSG=32651
THRESHOLD_BEST=-0.15
```

`.env.example` 可以保留在 GitHub，但 `.env` 應加入 `.gitignore`。

建議 `.gitignore`：

```gitignore
.env
.ipynb_checkpoints/
__pycache__/
*.pyc
.DS_Store
```

---

## Input Data

### Sentinel-2 L2A

影像透過 Microsoft Planetary Computer STAC API 取得，使用的 bands 包含：

| Band | Description |
|---|---|
| B02 | Blue |
| B03 | Green |
| B04 | Red |
| B08 | NIR |
| B11 | SWIR |
| SCL | Scene Classification Layer |

### Validation Points

官方驗證資料應放在：

```text
data/validation_points.geojson
```

此檔案用於 threshold optimization、confusion matrix 與 accuracy assessment。

### Week 8 Eyewitness Impact Table

Week 8 的目視判釋表應放在：

```text
data/impact_table_w8.csv
```

此檔案用於 Task 7 的 Week 8 vs. Week 9 comparison。

---

## Methodology

### 1. Cloud Masking with SCL

本專案使用 Sentinel-2 L2A 的 SCL band 進行 cloud masking。保留的 SCL classes 為：

```python
SCL_CLEAR_CLASSES = [2, 4, 5, 6, 7, 11]
```

每個 scene 會先建立個別 mask：

```text
valid_pre
valid_mid
valid_post
```

接著建立三期共同有效的 intersection mask：

```text
valid = valid_pre ∩ valid_mid ∩ valid_post
```

所有 spectral index 與 difference map 都套用此 mask，以減少雲、陰影造成的 false signal。

---

### 2. Spectral Indices

本專案計算三個指標：

#### NDVI

```text
NDVI = (NIR - Red) / (NIR + Red)
```

主要用於偵測 vegetation loss 與 surface disturbance。

#### NDWI

```text
NDWI = (Green - NIR) / (Green + NIR)
```

主要用於偵測 water / inundation signal。

#### BSI

```text
BSI = ((SWIR + Red) - (NIR + Blue)) / ((SWIR + Red) + (NIR + Blue))
```

主要用於偵測 bare soil、sediment、debris exposure。

---

### 3. Difference Layers

本專案計算：

```text
ΔNDVI = NDVI_post - NDVI_pre
ΔNDWI = NDWI_post - NDWI_pre
ΔBSI  = BSI_post  - BSI_pre
```

其中，ΔNDVI 是主要 threshold optimization 的依據。負值代表 NDVI 下降，通常對應植被損失、地表擾動或裸露化。

---

### 4. Threshold Optimization

使用 teacher-provided validation points 測試多個 ΔNDVI threshold：

```python
thresholds = [-0.05, -0.10, -0.15, -0.20, -0.25, -0.30, -0.40]
```

分類規則為：

```text
Change if ΔNDVI < threshold
No Change otherwise
```

每個 threshold 會計算：

- TP
- FP
- TN
- FN
- Producer's Accuracy
- User's Accuracy
- Overall Accuracy
- F1-score
- Kappa

本次最佳 threshold 為：

```text
ΔNDVI < -0.20
```

---

### 5. Accuracy Assessment

使用最佳 threshold 後，confusion matrix 結果為：

|  | Predicted Change | Predicted No Change |
|---|---:|---:|
| Actual Change | 12 | 9 |
| Actual No Change | 1 | 25 |

解讀如下：

- **TP = 12**：實際有變化且成功偵測為變化。
- **FN = 9**：實際有變化但被漏掉。
- **FP = 1**：實際無變化但誤判為變化。
- **TN = 25**：實際無變化且正確判斷為無變化。

模型具有高 User's Accuracy，代表預測為 change 的區域相當可靠；但 Producer's Accuracy 較低，代表仍有 omission error。

---

### 6. Confidence Zones

本專案將 study area 分成三個 operational confidence zones：

| Zone | Meaning |
|---|---|
| High Confidence | 核心變化區，強烈 NDVI 下降 |
| Low Confidence | 需再驗證區，邊界型 NDVI 下降 |
| No Detection | 未偵測顯著變化 |

本次採用 direction-sensitive NDVI decrease rule，而非使用 `abs(ΔNDVI)`，避免把 NDVI 增加區誤判為災害高信心區。

---

## Outputs

### Task 1: Difference Maps

```text
outputs/task1_difference_maps_2x2.png
outputs/task1_difference_layer_statistics.csv
```

內容包含：

- ΔNDVI Pre→Mid
- ΔNDVI Pre→Post
- ΔNDWI Pre→Post
- ΔBSI Pre→Post

### Task 2: Threshold Optimization

```text
outputs/task2_threshold_sweep.csv
outputs/task2_threshold_vs_metrics.png
```

內容包含 threshold vs. F1 / PA / UA 的變化。

### Task 3: Accuracy Assessment

```text
outputs/task3_accuracy_metrics.csv
outputs/task3_confusion_matrix.png
```

內容包含 confusion matrix 與 accuracy metrics。

### Task 4: Confidence Map and Phantom Water Comparison

```text
outputs/task4_confidence_zone_area.csv
outputs/task4_confidence_zone_map.png
outputs/task4_phantom_water_comparison.png
```

其中 phantom water comparison 顯示：

1. raw ΔNDWI without cloud mask
2. masked ΔNDWI with SCL intersection mask
3. potential phantom water artifacts

此比較顯示如果沒有 cloud masking，雲與陰影會產生 artificial water signal，造成 inundation overestimation。

---

## Key Findings

### 1. ΔNDVI 是最主要的變化偵測指標

ΔNDVI Pre→Post 在湖區、河道與下游沉積區出現明顯負值，反映植被損失與地表擾動。

### 2. ΔNDWI 支持水體與濕潤地表變化

ΔNDWI Pre→Post 在 river corridor 與 barrier lake 附近出現正值，支持水體或濕潤地表增加的判釋。

### 3. BSI 可作為 debris / exposed sediment 的輔助證據

ΔBSI 的空間訊號較分散，但仍能輔助判斷裸露土壤、沉積物或 debris field。

### 4. Cloud masking 是必要步驟

Phantom water comparison 顯示，未經遮罩的 ΔNDWI 容易受到 clouds 與 cloud shadows 影響，產生 false water signal。

### 5. Validated result 適合做初步災害篩選

本次模型具有高 UA，但 PA 較低，因此適合用於確認高信心影響區，不適合單獨用來排除所有可能災害區。

---

## How to Run

1. Clone repository

```bash
git clone <your-repository-url>
cd HW9
```

2. Create and activate environment

```bash
conda activate geo-risk
```

3. Create `.env`

```bash
cp .env.example .env
```

確認 `.env` 中的 Sentinel-2 item ID 與 bbox 設定正確。

4. Open Jupyter Notebook

```bash
jupyter notebook Week9_ARIA_v60_Notebook_Structure.ipynb
```

或使用 VS Code 開啟 notebook。

5. Run all cells from top to bottom.

---

## Notes and Limitations

1. **Validation sample reduction**  
   雖然原始 teacher validation points 有 60 個，但經過 SCL intersection mask 與 raster sampling 後，部分點可能落在 masked pixels 上，因此最終 accuracy assessment 使用的樣本數可能少於 60。

2. **PA lower than UA**  
   本次結果中 UA 很高，但 PA 較低，代表預測為 change 的區域可靠，但仍可能漏掉實際變化區。

3. **Cloud and shadow uncertainty**  
   SCL mask 可以降低 phantom water，但嚴格遮罩也可能移除部分有用資訊。

4. **Operational caution**  
   本結果應作為災害監測與初步判斷輔助，不應單獨作為撤離、安全或工程決策依據。

5. **No independent bonus validation**  
   本專案目前主要使用 teacher-provided validation points。若要提高可信度，可額外建立 `my_validation_points.geojson`，使用 Google Earth Pro、UAV imagery 或 news reports 建立獨立驗證點。

---

## Suggested Future Improvements

後續可改進方向包括：

1. 加入 SAR imagery，以降低雲遮罩造成的資料缺口。
2. 使用 UAV 或 very-high-resolution satellite imagery 驗證 low-confidence zones。
3. 增加更多 no-change 與 change validation points。
4. 比較不同 thresholding approaches，例如 NDVI + NDWI + BSI composite rule。
5. 使用 object-based image analysis 減少 pixel-level noise。
6. 建立 time-series monitoring workflow，追蹤災後恢復與沉積區變化。

---

## Academic Responsibility

本專案所有圖表與指標皆需進行 sanity check。若出現下列情況，應重新檢查流程：

- OA 接近 1.0 但圖像明顯不合理
- Kappa 接近 0 但 accuracy 很高
- confidence map 大範圍隨機雜訊
- ΔNDWI 大量出現不合理水體訊號
- validation points 只剩單一類別

本專案特別強調：**remote sensing output should be validated before being used for disaster decision-making**。

---

## Author

Po-Wei Huang  
NTU Remote Sensing & Spatial Information Analysis  
Week 9 Homework — ARIA v6.0

---

## License

This repository is for course assignment and educational use only.
