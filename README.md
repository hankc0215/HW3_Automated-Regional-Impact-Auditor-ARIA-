# ARIA v5.0：馬太鞍三幕稽核器

以 **Sentinel-2 遙測影像** 與 **多圖層空間資料** 為核心，重建 2025 年馬太鞍溪堰塞湖事件的三幕式時序證據，並進一步進行避難設施、瓶頸節點與 Guangfu overlay 的覆蓋缺口稽核。

本專案對應的 notebook 為：

- `Week8-Student-final-fixed.ipynb`

---

## 專案目標

本 notebook 旨在完成以下任務：

1. 以 **Pre / Mid / Post** 三個時期的 Sentinel-2 影像，重建事件三幕：
   - **Act 1 / Pre-event**：堰塞湖形成前，正常森林谷地
   - **Act 2 / Mid-event**：堰塞湖存在期間
   - **Act 3 / Post-event**：潰決後，下游出現新鮮沉積與土石流鋪面

2. 建立三張事件偵測遮罩：
   - **Barrier lake mask**（堰塞湖）
   - **Landslide source scar mask**（上游崩塌源區）
   - **Debris flow footprint mask**（下游土石流鋪面）

3. 向量化三種災害結果，並與外部圖層交叉比對：
   - **W3 shelters**
   - **W7 bottlenecks**
   - **W8 Guangfu overlay**

4. 建立最終成果：
   - **Eyewitness Impact Table**
   - **Coverage Gap Map**
   - **AI Advisor prompt**（供 LLM 生成應變簡報）

---

## 核心概念

本 notebook 的核心是 **ARIA v5.0 的三幕式稽核邏輯**：

### 1. 三幕時序證據
使用三個時間段的影像，建立事件的時序鏈：

- **Pre**：事件前基準狀態
- **Mid**：事件進行中，確認堰塞湖存在
- **Post**：事件後，確認潰決、崩塌與下游沉積擴散

### 2. 三種地表變化規則
不同災害特徵對應不同波段組合：

- **上游崩塌源區**
  - 典型特徵：植被移除、裸岩與乾土暴露
  - 指標：**NIR drop + SWIR surge**

- **下游土石流鋪面**
  - 典型特徵：濕泥沙覆蓋原本的農地與低地植被
  - 指標：**NDVI drop + BSI spike**

- **堰塞湖**
  - 典型特徵：原本高 NIR 的植被區在 Mid-event 轉為低 NIR 水體
  - 指標：以 **NIR + Blue/Green** 進行水體條件判斷

### 3. 覆蓋缺口分析
最後將災害 polygon 與外部設施圖層交叉比對，回答：

- 哪些避難所落入災害影響範圍
- 哪些瓶頸節點被截斷
- Guangfu overlay 是否顯示出原本 ARIA 事前覆蓋未能處理的地方節點

---

## 專案結構

建議專案目錄如下：

```text
.
├─ Week8-Student-final-fixed.ipynb
├─ README.md
├─ .env
├─ data/
│  ├─ shelters.csv
│  ├─ top5_bottlenecks.csv
│  ├─ guangfu_overlay.gpkg
│  └─ ...（其他可選圖層）
└─ outputs/
   ├─ 07_lake_mask.png
   ├─ 08_landslide_mask.png
   ├─ 09_debris_mask.png
   ├─ 10_lake.gpkg
   ├─ 10_landslides.gpkg
   ├─ 10_debris.gpkg
   ├─ impact_table.csv
   ├─ 12_coverage_gap_map.png
   ├─ post_rgb_preview.png
   └─ env_template.txt
```

---

## 環境需求

### Python 套件

建議環境至少包含：

```bash
pip install numpy pandas matplotlib geopandas shapely pyproj rasterio rioxarray xarray stackstac pystac-client planetary-computer python-dotenv
```

若要使用 AI Advisor 範例，可依需求另外安裝：

```bash
pip install openai
pip install google-generativeai
pip install anthropic
```

---

## `.env` 設定

請在專案根目錄建立 `.env`，至少包含：

```env
STAC_ENDPOINT=https://planetarycomputer.microsoft.com/api/stac/v1
S2_COLLECTION=sentinel-2-l2a
S2_CLOUD_MAX=20
S2_BANDS=B02,B03,B04,B08,B11,B12

MATAIAN_BBOX=121.28,23.56,121.52,23.76
TARGET_EPSG=32651

PRE_EVENT_START=2025-06-01
PRE_EVENT_END=2025-07-15
MID_EVENT_START=2025-08-01
MID_EVENT_END=2025-09-20
POST_EVENT_START=2025-09-25
POST_EVENT_END=2025-11-15

OPENAI_API_KEY=your-openai-key-here
# GOOGLE_API_KEY=your-google-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here

AI_API_KEY=your-api-key-here
```

---

## Notebook 內容概覽

### Lab 1：Three-Act Scene Selection
- 設定環境與 STAC 參數
- 搜尋三個時期的 Sentinel-2 scene
- 選出 pre / mid / post 三張代表影像
- 建立 `cube_pre`、`cube_mid`、`cube_post`

### Lab 2：Three Detection Masks
- 建立四個可重用 change metrics
- 偵測：
  - 堰塞湖
  - 崩塌源區
  - 土石流鋪面
- 進行 threshold tuning
- 向量化結果

### Lab 2（續）：Multi-Layer Audit
- 讀入 W3 / W7 / W8 圖層
- 與災害 polygon 交叉比對
- 產生：
  - `impact_df`
  - `impact_table.csv`
  - `12_coverage_gap_map.png`

### Challenge：AI Advisor
- 將三幕證據與 impact table 整理成 prompt
- 可串接 OpenAI / Gemini / Claude 生成簡報摘要

---

## 主要輸出成果

### 1. 遮罩圖
- `07_lake_mask.png`
- `08_landslide_mask.png`
- `09_debris_mask.png`

### 2. 向量化圖層
- `10_lake.gpkg`
- `10_landslides.gpkg`
- `10_debris.gpkg`

### 3. 事件稽核表
- `impact_table.csv`

包含欄位如：
- `asset`
- `type`
- `location`
- `W4_terrain_risk`
- `W7_centrality_rank`
- `lake_hit`
- `landslide_hit`
- `debris_hit`

### 4. 最終覆蓋缺口圖
- `12_coverage_gap_map.png`

### 5. 本地快取底圖
- `post_rgb_preview.png`

此檔案用於避免後續 cell 因 Planetary Computer 的 signed URL 過期而導致底圖失敗。

---

## 執行順序建議

請依照 notebook 原始順序執行，不要跳格，特別注意以下流程：

1. **S1** 環境設定
2. **S2–S4** 選取 pre / mid / post item
3. **S5** 建立三個 cube 並做讀取測試
4. **S7–S9** 建立三張 mask
5. **S10** 向量化
6. **S11–S12** 讀圖層、做 impact audit、輸出 final map
7. **S13–S14** 建立 AI Advisor prompt

---

## 常見問題

### 1. 為什麼底圖有時候讀不到？
Planetary Computer 的 signed URL 有時間限制。若看到類似：

- `AuthenticationFailed`
- `Signature not valid in the specified time frame`

代表簽名網址已過期。解法：

- 重新執行 pre / mid / post 的 scene 搜尋與 cube 建立
- 或直接使用 notebook 已保存的 `post_rgb_preview.png`

### 2. 為什麼 `imshow` 顯示全白？
通常是 RGB 值域問題。若 visual asset 是 float 但範圍仍在 `0–255`，必須先轉成 `0–1` 再畫。

### 3. 為什麼 `stackstac` 報 `fill_value` 錯誤？
若使用 `dtype="float32"`，請搭配：

```python
fill_value=np.float32(np.nan)
```

### 4. 為什麼 legend 會出 warning？
`geopandas.plot()` 產生的 polygon layer 常無法直接交給 `matplotlib` 自動 legend。  
本 notebook 已改為手動建立 legend handles。

---

## 本版本修正重點

此版本 notebook 已針對先前常見問題進行修正，包括：

- 修正 `preview_item_visual()` 的 RGB 顯示
- 強化 `stream_cube()` 的 signed URL 重建與讀取穩定性
- 加入 cube quick read test
- 加入本地 `post_rgb_preview.png` 快取
- 修正 landslide threshold tuning 中的 `NaN -> int` warning
- 改善 S11 對 csv / gpkg / shp / WKT 的讀取支援
- 改善 S12 的 study-area clipping、manual legend 與底圖 fallback

---

## 使用情境

本 notebook 適合用於：

- 遙測與災害地形變化教學
- 河谷堰塞湖事件的三幕式稽核
- 多圖層空間覆蓋缺口分析
- 作為 ARIA 系列 notebook 的進階實作版本

---

## License

若要公開至 GitHub，建議自行補上專案授權資訊，例如：

- MIT License
- Apache-2.0
- 或課程 / 作業使用限定條款

---

## 作者備註

本 notebook 是一份以課堂實作為基礎、針對馬太鞍溪事件設計的三幕式稽核流程。若後續要擴充，可考慮加入：

- 更穩定的本地 cache 機制
- 多事件批次處理
- 更完整的 road network interruption 分析
- 自動化報表輸出
