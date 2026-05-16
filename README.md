# ARIA v8.0 — The Classification Engine  
### Week 12 Homework｜Post-Earthquake Land Cover Classification in Xiulin / Taroko

本專案為 NTU「遙測與空間資訊之分析與應用」Week 12 作業，延續 ARIA v5.0–v7.0 的災害遙測分析流程，將原本以單一指標與閾值為主的判讀方式，升級為 **ARIA v8.0 — The Classification Engine**。本次以 2024 年 4 月 3 日花蓮地震後的 Sentinel-2 L2A 影像為資料來源，針對秀林／太魯閣研究區建立多類別土地覆蓋分類圖，並比較 K-means 非監督式分類與 Random Forest 監督式分類的表現。

---

## 1. Project Overview

過去 ARIA v7.0 主要透過 pixel-level threshold，例如 NDVI、NDWI 或 SAR backscatter 閾值，判斷哪裡可能出現異常或災害影響。然而，災後應變不只需要知道「哪裡異常」，也需要知道每個像素對應的土地覆蓋類型，例如水體、森林、農田、裸地／崩塌與建物／都市。

因此，本專案將 ARIA 升級為分類器導向的分析流程，使用 Sentinel-2 的六個多光譜波段作為特徵，建立完整的災後土地覆蓋圖，並以內部驗證與 SWCB 官方新生崩塌地資料進行外部驗證。

---

## 2. Study Area and Data

### Study Area

研究區為 **秀林鄉／太魯閣周邊**，包含山區、河谷、蘇花公路沿線與太平洋近海區域。

```python
TAROKO_BBOX = [121.40, 24.10, 121.80, 24.25]
TARGET_EPSG = 32651
RESOLUTION = 20
```

### Satellite Data

本專案使用 Microsoft Planetary Computer STAC API 串流 Sentinel-2 L2A 影像。

Selected scene:

```text
S2A_MSIL2A_20240827T022531_R046_T51QUG_20240827T053853
Datetime: 2024-08-27 02:25:31 UTC
Cloud cover: 8.36%
```

### Classification Bands

使用六個 Sentinel-2 反射率波段：

| Band | Name | Description |
|---|---|---|
| B02 | Blue | 藍光 |
| B03 | Green | 綠光 |
| B04 | Red | 紅光 |
| B08 | NIR | 近紅外光 |
| B11 | SWIR1 | 短波紅外一 |
| B12 | SWIR2 | 短波紅外二 |

並使用 Sentinel-2 L2A 的 `SCL` 進行雲、雲影與雪的遮罩處理。

---

## 3. Target Classes

本次分類共設定五個土地覆蓋類別：

| Class ID | Class Name | 中文說明 |
|---:|---|---|
| 0 | Water | 水體 |
| 1 | Forest | 森林 |
| 2 | Cropland | 農田 |
| 3 | Bare/Landslide | 裸地／崩塌 |
| 4 | Built-up | 建物／都市 |

---

## 4. Workflow

本專案流程如下：

```text
STAC Search
    ↓
Sentinel-2 L2A Image Loading
    ↓
SCL Cloud / Shadow Masking
    ↓
6-band Feature Matrix
    ↓
Task 1: K-means Unsupervised Classification
    ↓
Task 2: Random Forest Supervised Classification
    ↓
Task 3A: Internal Accuracy Assessment
    ↓
Task 3B: SWCB Landslide External Validation
    ↓
Task 4: Area Statistics and AI Classification Report
```

---

## 5. Task 1 — K-means Unsupervised Classification

K-means 使用六個波段的反射率特徵進行非監督式分群，設定 `K = 5`，對應五種可能的土地覆蓋類型。

### Output

```text
outputs/kmeans_classification.png
outputs/kmeans_cluster_spectral_table.csv
```

### Interpretation

K-means 對於光譜特徵明顯的類別，例如水體與森林，具有較好的分群效果。不過，裸地、河床、道路、建物與部分農地在可見光與 SWIR 波段上可能具有相似反射特徵，因此不同地物可能被分到相同 cluster，或同一地物被切成多個 cluster。

K-means 的優點是不需要訓練資料，適合初步探索影像中的光譜結構；缺點是 cluster ID 並不等於真正的土地覆蓋類別，仍需要人工判讀與重新命名。

---

## 6. Task 2 — Random Forest Supervised Classification

Random Forest 使用人工選取的訓練樣本進行監督式分類。每個類別選取約 350 個訓練像素，並使用 train/test split 進行內部驗證。

### Model Settings

```python
RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1,
    oob_score=True
)
```

### Accuracy Summary

| Metric | Value |
|---|---:|
| Training Accuracy | 0.936 |
| Test Accuracy | 0.837 |
| OOB Accuracy | 0.846 |

### Output

```text
outputs/rf_classification.png
outputs/feature_importance.png
outputs/rf_feature_importance.csv
outputs/training_samples_preview.png
outputs/training_sample_counts.csv
```

### Feature Importance

Random Forest 的 feature importance 顯示，`B12 SWIR2` 是最重要的波段。這是合理的，因為 SWIR 對於裸露地表、乾燥土壤、崩塌地、河床與植被含水狀態差異較敏感，因此有助於區分森林、裸地／崩塌與建物等類別。

---

## 7. Task 3 — Accuracy Assessment

### 7.1 Internal Validation

使用測試資料進行 confusion matrix 與 classification report 分析。

```text
outputs/confusion_matrix.png
outputs/classification_report.csv
outputs/accuracy_summary.csv
```

### Internal Validation Results

| Metric | Value |
|---|---:|
| Macro F1 | 0.837 |
| Weighted F1 | 0.837 |
| Weighted - Macro F1 Gap | 0.000 |

Water、Forest 與 Cropland 的分類表現較穩定；主要混淆發生在 **Bare/Landslide** 與 **Built-up** 之間。這是因為裸露地、道路、河床、建物與部分人工鋪面在 Sentinel-2 的 20 m 解析度下容易形成混合像素，且在可見光與 SWIR 波段上可能具有相似的高反射特徵。

### 7.2 External Validation with SWCB Landslide Inventory

本專案使用 SWCB 官方新生崩塌地 KML 作為外部驗證資料，將官方崩塌地 polygon rasterize 到與 Random Forest 分類圖相同的網格後，與 `Bare/Landslide` 類別進行空間重疊比較。

```text
outputs/swcb_overlay.png
outputs/swcb_overlap_metrics.csv
```

### SWCB Overlap Metrics

| Metric | Value |
|---|---:|
| Recall | 0.590 |
| Precision | 0.003 |
| IoU | 0.003 |

### Interpretation

Recall 約為 0.590，代表模型的 Bare/Landslide 類別有抓到部分 SWCB 官方崩塌地。然而 Precision 與 IoU 很低，代表模型也將大量非官方崩塌地區域判為 Bare/Landslide。這些 false positives 可能包含裸露河床、道路、坡面裸地、建物與其他混合像素。

因此，Bare/Landslide 類別應被解讀為「可能裸露或受擾動地表」，不能直接等同於官方崩塌地。若要進行正式災害決策，仍需要搭配高解析度影像、坡度資料、道路資料與現地調查進一步確認。

---

## 8. Task 4 — Area Statistics and AI Classification Report

### Area Statistics

```text
outputs/class_area_stats.csv
outputs/ai_classification_report.txt
```

| Class | Area (ha) | Percentage |
|---|---:|---:|
| Water | 22224.9 | 35.2% |
| Forest | 11309.0 | 17.9% |
| Cropland | 11545.0 | 18.3% |
| Bare/Landslide | 16692.4 | 26.4% |
| Built-up | 1409.9 | 2.2% |

若將近海區域納入統計，面積最大的類別為 **Water**，約 22224.9 公頃，占有效分類像素的 35.2%。這是因為本研究區 BBOX 包含太平洋近海區域，因此全研究區面積統計會受到海域比例影響。

若聚焦於陸域部分，則 Bare/Landslide、Cropland 與 Forest 是主要類別。其中 Bare/Landslide 面積約 16692.4 公頃，占 26.4%，需要進一步與坡度、河道、道路與官方崩塌地資料交叉比對。

---

## 9. Key Output Files

| File | Description |
|---|---|
| `Homework_Week12_ARIA_v8_complete.ipynb` | 完整 Jupyter Notebook |
| `ARIA_v8_markdown_report.md` | Markdown 報告 |
| `kmeans_classification.png` | K-means 分類圖 |
| `kmeans_cluster_spectral_table.csv` | K-means 各群平均光譜表 |
| `rf_classification.png` | Random Forest 土地覆蓋分類圖 |
| `kmeans_vs_rf.png` | K-means 與 RF 並排比較圖 |
| `preview_true_false_color.png` | True color 與 false color 預覽圖 |
| `training_samples_preview.png` | 訓練樣本位置圖 |
| `training_sample_counts.csv` | 各類別訓練樣本數 |
| `feature_importance.png` | RF 波段重要性圖 |
| `rf_feature_importance.csv` | RF 波段重要性表 |
| `confusion_matrix.png` | Confusion matrix |
| `classification_report.csv` | Classification report |
| `accuracy_summary.csv` | Accuracy summary |
| `swcb_overlay.png` | RF vs SWCB 崩塌地疊圖 |
| `swcb_overlap_metrics.csv` | SWCB overlap metrics |
| `class_area_stats.csv` | 各類別面積統計 |
| `ai_classification_report.txt` | AI 產生之分類報告 |

---

## 10. Repository Structure

建議 GitHub 專案結構如下：

```text
ARIA-v8-Classification-Engine/
│
├── README.md
├── Homework_Week12_ARIA_v8_complete.ipynb
├── ARIA_v8_markdown_report.md
├── .env.example
│
├── data/
│   └── 20240802新生崩塌地.kml
│
├── outputs/
│   ├── kmeans_classification.png
│   ├── kmeans_cluster_spectral_table.csv
│   ├── rf_classification.png
│   ├── kmeans_vs_rf.png
│   ├── preview_true_false_color.png
│   ├── training_samples_preview.png
│   ├── training_sample_counts.csv
│   ├── feature_importance.png
│   ├── rf_feature_importance.csv
│   ├── confusion_matrix.png
│   ├── classification_report.csv
│   ├── accuracy_summary.csv
│   ├── swcb_overlay.png
│   ├── swcb_overlap_metrics.csv
│   ├── class_area_stats.csv
│   └── ai_classification_report.txt
│
└── requirements.txt
```

---

## 11. How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ARIA-v8-Classification-Engine.git
cd ARIA-v8-Classification-Engine
```

### 2. Install Required Packages

```bash
pip install -r requirements.txt
```

若沒有 `requirements.txt`，可手動安裝：

```bash
pip install numpy pandas matplotlib scikit-learn scipy geopandas rasterio shapely pystac-client planetary-computer stackstac python-dotenv google-generativeai
```

### 3. Prepare `.env`

請複製 `.env.example` 並改名為 `.env`：

```bash
cp .env.example .env
```

`.env` 範例：

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.0-flash

STAC_ENDPOINT=https://planetarycomputer.microsoft.com/api/stac/v1
S2_COLLECTION=sentinel-2-l2a

TAROKO_BBOX=121.40,24.10,121.80,24.25
TARGET_EPSG=32651
RESOLUTION=20

BANDS=B02,B03,B04,B08,B11,B12
BANDS_ALL=B02,B03,B04,B08,B11,B12,SCL
VALID_SCL_CLASSES=4,5,6,7

OUTPUT_DIR=outputs
SWCB_KML_PATH=data/20240802新生崩塌地.kml

KMEANS_N_CLUSTERS=5
RANDOM_STATE=42
RF_N_ESTIMATORS=200
TEST_SIZE=0.2
```

> 注意：請不要將真正的 `.env` 上傳到 GitHub。  
> GitHub 上只需要放 `.env.example`。

### 4. Prepare SWCB KML

請將 `20240802新生崩塌地.kml` 放入：

```text
data/20240802新生崩塌地.kml
```

### 5. Run the Notebook

開啟並依序執行：

```text
Homework_Week12_ARIA_v8_complete.ipynb
```

執行完成後，所有圖表與表格會輸出到 `outputs/`。

---

## 12. Limitations

本專案結果仍有以下限制：

1. **Sentinel-2 空間解析度限制**  
   本次分類使用 20 m 解析度，單一像素可能包含植被、裸地、道路、河床或建物等混合資訊。

2. **Bare/Landslide 類別定義較廣**  
   Random Forest 的 Bare/Landslide 類別代表光譜上類似裸露地表的像素，不等於官方崩塌地 polygon。

3. **影像日期與官方資料日期不同**  
   Sentinel-2 影像日期與 SWCB 官方判釋資料日期可能不同，因此地表狀態可能已有變化。

4. **訓練樣本品質影響分類結果**  
   Random Forest 的分類品質高度依賴訓練樣本是否純淨、分散且具有代表性。

5. **近海區域影響面積統計**  
   因為 BBOX 包含太平洋近海區域，Water 類別在全研究區統計中占比最高。若要分析陸域災害，建議後續加入陸域遮罩。

---

## 13. ARIA v8.0 Upgrade Reflection

ARIA v8.0 的核心升級，是從單一閾值判斷轉向多波段分類器。閾值法簡單、透明，適合快速偵測特定現象，例如水體擴張或植被減少；但它通常只能處理單一指標，難以同時區分多種土地覆蓋類型。

相較之下，Random Forest 可以同時利用 Blue、Green、Red、NIR、SWIR1 與 SWIR2 等多個波段，建立完整的土地覆蓋分類圖。這讓分類結果更適合後續 GIS 疊圖分析，例如避難所風險評估、道路可達性分析、崩塌熱區盤點與現地複查規劃。

不過，分類器並不會自動保證結果正確。模型表現仍受到訓練樣本品質、類別定義、空間解析度與地表異質性的影響。在太魯閣山區案例中，水體與森林較容易辨識，但裸地、道路、建物、河床與崩塌地之間仍容易混淆。因此，ARIA v8.0 的分類結果應被視為災後快速判讀與決策輔助圖層，而不是取代官方判釋或現地調查的最終成果。

---

## 14. Author

Prepared for Week 12 Homework:  
**ARIA v8.0 — The Classification Engine**

Course: Remote Sensing & Spatial Information Analysis  
Case Study: Xiulin / Taroko Post-Earthquake Land Cover Classification
