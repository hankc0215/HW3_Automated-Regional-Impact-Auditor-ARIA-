# ARIA v3.0 — 第 5 週作業
## 鳳凰颱風動態受災衝擊監測系統

本專案的目標，是建立 **ARIA v3.0（The Living Auditor）**，做出一套可以即時判讀風險的監測系統，用來回答：

**「現在最危險的地方在哪裡？」**

這套系統整合了以下幾部分資料與分析流程：
1. 第 3 週避難所的河川距離風險
2. 第 4 週避難所的地形風險
3. LIVE / SIMULATION 兩種模式的雨量資料
4. 雨量影響範圍的空間疊合
5. 避難所的動態風險分級
6. Folium 互動式地圖呈現

最終輸出檔案為：
- `ARIA_v3_Week5.ipynb`
- `ARIA_v3_Fungwong.html`

---

## 一、專案目標

這份 Notebook 是以 **2025 年鳳凰颱風（Typhoon Fung-wong）** 的情境作為壓力測試案例。  
和課堂上的 Lab 相比，這次作業不只是單純畫圖，而是要完成一套從資料讀取、格式整理、空間分析，到互動式地圖輸出的完整流程。

主要工作包括：

1. 從 `.env` 讀取設定值
2. 在 **LIVE** 與 **SIMULATION** 模式間切換
3. 將不同格式的雨量 JSON 正規化（normalize）
4. 將雨量站整理成 GeoDataFrame
5. 把雨量站與避難所統一投影到 `EPSG:3826`
6. 建立雨量影響範圍的 buffer
7. 用 `gpd.sjoin()` 找出受影響避難所
8. 套用動態風險分級邏輯
9. 建立具有圖例、圖層切換與 popup 的 Folium 地圖

---

## 二、檔案說明

### 主要檔案
- `ARIA_v3_Week5.ipynb`：主分析 Notebook
- `ARIA_v3_Fungwong.html`：最終輸出的互動式地圖
- `.env`：環境設定檔
- `shelters_composite_risk.csv`：前幾週整合完成的避難所風險資料
- `fungwong_202511.json`：鳳凰颱風模擬雨量快照

### 補充檔案
- `terrain_risk_audit.json`：地形風險稽核清單，可作為檢查用資料

---

## 三、環境設定

本專案使用 `.env` 管理主要設定值，這樣比較方便切換模式，也比較符合作業要求。

範例如下：

```ini
APP_MODE=SIMULATION
CWA_API_KEY=your-cwa-api-key-here
SIMULATION_DATA=fungwong_202511.json
SHELTER_FILE=shelters_composite_risk.csv
BUFFER_METERS=5000
RAIN_URGENT=40
RAIN_CRITICAL=80
TARGET_CENTER_LAT=23.987
TARGET_CENTER_LON=121.601
OUTPUT_HTML=ARIA_v3_Fungwong.html
```

### 模式切換說明
- `APP_MODE=SIMULATION`  
  使用本地的鳳凰颱風雨量快照

- `APP_MODE=LIVE`  
  呼叫中央氣象署 CWA API，取得即時雨量資料

### fallback 機制
若 `LIVE` 模式因為 API timeout、金鑰錯誤或請求失敗而無法取得資料，程式會自動 fallback 到本地模擬檔案，以確保 Notebook 仍然可以執行。

---

## 四、資料來源

### 1. 避難所與地形風險資料
這部分延續前幾週成果，包括：
- 第 3 週的河川距離風險
- 第 4 週的地形風險

並整合成：
- `shelters_composite_risk.csv`

### 2. 雨量資料
- **LIVE 模式：** CWA `O-A0002-001` API
- **SIMULATION 模式：** `fungwong_202511.json`

---

## 五、分析流程摘要

### Step 1 — 載入避難所基礎風險資料
首先從 `shelters_composite_risk.csv` 載入避難所資料，並整理主要欄位，例如：
- shelter ID
- shelter name
- latitude / longitude
- terrain risk

由於不同週次輸出的欄位名稱可能略有差異，所以在 Notebook 中也有做欄位標準化處理。

### Step 2 — 載入雨量資料
程式會先從 `.env` 讀取 `APP_MODE`：
- 若為 `LIVE`，則呼叫 CWA API
- 若為 `SIMULATION`，則讀取本地 JSON 快照

這樣可以在同一份 Notebook 中切換不同資料來源，而不需要改動後面的分析邏輯。

### Step 3 — 正規化雨量 JSON
由於 LIVE 與 SIMULATION 模式的 JSON 結構並不完全相同，因此需要透過 `normalize_cwa_json()` 先把兩者整理成一致格式。

整理後的欄位包含：
- `station_id`
- `station_name`
- `county_name`
- `town_name`
- `lat`
- `lon`
- `rain_1hr`
- `rain_24hr`
- `rain_10min`

### Step 4 — 投影轉換
雨量站原始資料使用 `EPSG:4326`，但進行 buffer 與空間分析時，必須使用以公尺為單位的投影座標，因此需將雨量站與避難所一律轉為 `EPSG:3826`。

這一步很重要，因為如果直接在 `EPSG:4326` 下做 buffer，距離單位會錯誤，分析結果也會失真。

### Step 5 — 建立雨量影響範圍
接著挑出時雨量超過門檻的雨量站，並建立 5 km buffer，作為暴雨影響範圍。

### Step 6 — 空間疊合避難所
利用 `gpd.sjoin()` 找出位於高雨量 buffer 範圍內的避難所，判斷哪些避難所正受到暴雨影響。

### Step 7 — 動態風險分級
根據作業規範，避難所動態風險分為四級：

- **CRITICAL**  
  時雨量 `rain_1hr > 80 mm`，且避難所位於暴雨影響範圍內

- **URGENT**  
  時雨量 `rain_1hr > 40 mm`，且 `terrain_risk == HIGH`

- **WARNING**  
  時雨量 `rain_1hr > 40 mm`，或 `terrain_risk == HIGH`

- **SAFE**  
  其餘情況

這樣的設計可以同時考慮短時間強降雨與地形風險，而不是只看單一因子。

### Step 8 — 最近雨量站
為了讓 popup 資訊更完整，另外使用 `gpd.sjoin_nearest()` 為每個避難所附上最近的雨量站名稱與時雨量資訊。

### Step 9 — 建立互動式地圖
最後用 Folium 輸出互動式監測地圖，內容包含：
- 雨量站 `CircleMarker`
- 雨量 `HeatMap`
- 避難所動態風險 `CircleMarker`
- `LayerControl`
- 自訂圖例
- popup 詳細資訊

---

## 六、地圖設計

### 1. 雨量站圖層
雨量站使用 `CircleMarker` 顯示，並依照時雨量著色：

- 綠色：`0–10 mm`
- 黃色：`10–40 mm`
- 橘色：`40–80 mm`
- 紅色：`>80 mm`

### 2. 避難所圖層
避難所也使用 `CircleMarker`，顏色則依動態風險等級顯示：

- 綠色：`SAFE`
- 橘色：`WARNING`
- 紅色：`URGENT`
- 深紅色：`CRITICAL`

### 3. HeatMap
雨量熱區使用 `HeatMap` 呈現，作為輔助視覺化圖層，並設為 **預設關閉**，避免一開始遮住底圖細節。

### 4. 顯示範圍
為了讓地圖更聚焦，本次作業最後僅顯示：
- 花蓮縣
- 宜蘭縣

的雨量站與避難所資料。

---

## 七、執行方式

### 1. 安裝必要套件
建議先安裝以下套件：

```bash
pip install pandas numpy geopandas shapely folium requests python-dotenv
```

### 2. 將檔案放在同一資料夾
至少需要以下檔案：
- `ARIA_v3_Week5.ipynb`
- `.env`
- `shelters_composite_risk.csv`
- `fungwong_202511.json`

### 3. 修改 `.env`
根據需求設定：
- `APP_MODE=SIMULATION`
- 或 `APP_MODE=LIVE`

### 4. 由上到下執行 Notebook
建議不要跳著跑，避免前面設定值或中間資料尚未建立。

### 5. 開啟輸出地圖
Notebook 執行完成後，會輸出：

`ARIA_v3_Fungwong.html`

打開後即可檢視互動式地圖。

---

## 八、AI 診斷日誌

本段記錄本次實作中遇到的主要問題，以及對應的修正方式。

### 問題 1 — 雨量 JSON 解析後變成 0 個有效站點
**現象：**  
一開始執行 `normalize_cwa_json()` 時，結果顯示 `Valid rainfall stations: 0`。

**原因：**  
模擬 JSON 中的 `Past1hr` 並不是直接數字，而是巢狀結構，例如：

```json
"Past1hr": {
  "Precipitation": 0.0
}
```

原本程式直接把整個 dict 轉成 float，因此全部變成 `NaN`。

**修正方式：**  
新增 helper function，專門提取：
- 直接數值
- 或 `Precipitation` 欄位中的數值

修正後即可正確讀出所有雨量站。

---

### 問題 2 — `sjoin()` 結果為空或不合理
**現象：**  
空間疊合結果可能為空，或明顯不合理。

**原因：**  
雨量站與避難所若 CRS 不一致，`sjoin()` 就可能失敗。

**修正方式：**  
在 buffer、`sjoin()`、`sjoin_nearest()` 前，先將兩者都轉成 `EPSG:3826`，並加入 CRS 檢查：

```python
assert str(rain_gdf_3826.crs) == str(shelters_3826.crs), "CRS MISMATCH!"
```

---

### 問題 3 — 最近站點空間連接後欄位名稱衝突
**現象：**  
在執行 `gpd.sjoin_nearest()` 之後，出現 `KeyError: 'station_name'`。

**原因：**  
左右兩個 GeoDataFrame 都包含 `station_name` 與 `rain_1hr`，GeoPandas 會自動改名為：
- `station_name_left`
- `station_name_right`
- `rain_1hr_left`
- `rain_1hr_right`

但原本程式仍使用舊欄位名稱。

**修正方式：**  
改成：
- 優先使用 `station_name_left`
- 若為空再 fallback 到 `station_name_right`

雨量欄位也採用同樣處理方式。

---

### 問題 4 — 地圖顯示過於擁擠
**現象：**  
第一版地圖顯示所有站點後，畫面過於密集，不容易閱讀。

**修正方式：**  
最後版本改成：
1. 使用 `CircleMarker`
2. 加入 `HeatMap`
3. 只顯示花蓮與宜蘭資料
4. 補上圖例
5. 保留 `LayerControl` 供使用者切換圖層

---

### 問題 5 — HeatMap 不適合預設開啟
**現象：**  
HeatMap 預設開啟時，容易遮住地圖上的其他資訊。

**修正方式：**  
將 HeatMap 圖層設為：

```python
folium.FeatureGroup(name="Rainfall HeatMap", show=False)
```

讓地圖初始畫面更清楚。

---

## 九、注意事項

- Folium 的座標順序必須是 `[latitude, longitude]`
- buffer 一定要在 `EPSG:3826` 下進行
- CWA 缺值例如 `-998` 必須先轉成 `NaN`
- 模擬快照中的 `GeoInfo.Coordinates` 通常只有一組座標
- LIVE 與 SIMULATION 的 JSON 結構相似，但不完全相同，因此一定要先做 normalize

---

## 十、繳交內容

本專案繳交內容包括：
1. `ARIA_v3_Week5.ipynb`
2. `ARIA_v3_Fungwong.html`
3. `README.md`
4. `.env`

---

## 十一、結論

ARIA v3.0 的重點，不只是產出一張靜態風險圖，而是建立一套可以動態切換資料來源、整合多種風險資訊、並透過互動式地圖呈現結果的監測流程。

透過避難所基礎風險、地形條件與暴雨影響範圍的整合，本專案能在鳳凰颱風情境下提供更貼近防災判斷需求的監測儀表板，也更符合本次 Week 5 Assignment 對「動態監測版」ARIA 系統的要求。
