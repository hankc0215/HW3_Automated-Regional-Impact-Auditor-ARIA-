# Week 6 空間預測對決專案說明

本專案包含兩份主要 Notebook，用於整理 2022 年雨量事件資料，並完成 Week 6 作業中的空間預測比較分析。

---

## 一、專案內容

本專案的核心目標是比較不同降雨事件下的空間內插結果，並分析各方法在不同情境中的表現差異。  
目前流程分成兩個階段：

1. **前處理（prework）**
2. **主分析（shootout）**

---

## 二、主要檔案

### 1. `prework_prepare_rainfall_data.ipynb`
前處理 Notebook，負責整理原始資料，建立可供主分析直接使用的 prepared files。

### 2. `Week6_Shootout_v2.ipynb`
主分析 Notebook，負責挑選事件時刻、執行空間內插、比較不同方法、繪製 Sigma Map，並輸出 GeoTIFF。

---

## 三、整體流程

### Step 1：建立測站 metadata
使用 `fungwong_202511.json` 中的測站資訊建立測站對照表，欄位包括：

- `station_id`
- `station_name`
- `county`
- `town`
- `lat`
- `lon`

這份 metadata 主要用來補足 2022 年雨量 CSV 中缺少的測站座標與縣市資訊。

---

### Step 2：讀取 2022 年雨量 CSV
從 CoLife 下載並解壓後的每日雨量 CSV 中讀取候選日期資料，例如：

#### 梅花颱風候選日
- `20220911`
- `20220912`
- `20220913`
- `20220914`

#### 1029 豪雨候選日
- `20221028`
- `20221029`
- `20221030`
- `20221031`

原始 CSV 主要欄位包括：

- `station_id`
- `obsTime`
- `ELEV`
- `RAIN`
- `MIN_10`
- `HOUR_3`
- `HOUR_6`
- `HOUR_12`
- `HOUR_24`
- `NOW`

---

### Step 3：合併 metadata
將每日雨量資料依 `station_id` 與測站 metadata 進行 merge，補上：

- 測站名稱
- 縣市
- 鄉鎮市區
- 經度
- 緯度

這一步完成後，雨量資料才具備後續空間分析所需的地理資訊。

---

### Step 4：篩選研究區與有效資料
依作業需求，目前研究區限定為：

- `宜蘭縣`
- `花蓮縣`

同時移除無效資料值：

- `-998`
- `0`

這一步完成後，會得到可供主分析使用的「宜蘭＋花蓮有效雨量資料」。

---

### Step 5：輸出前處理成果
前處理 Notebook 會輸出以下內容：

#### 測站資料
- `station_metadata.csv`
- `station_metadata.json`

#### 每個日期的完整 merge 結果
- `rain_YYYYMMDD_merged.csv`
- `rain_YYYYMMDD_merged.json`

#### 每個日期的宜蘭＋花蓮有效資料
- `rain_YYYYMMDD_yl_hl_valid.csv`
- `rain_YYYYMMDD_yl_hl_valid.json`

#### 前處理摘要表
- `prework_summary.csv`
- `prework_summary.json`

---

## 四、主分析 Notebook 功能

`Week6_Shootout_v2.ipynb` 會讀取前處理輸出後的 prepared files，並完成後續分析。

### Step 1：讀取 prework 輸出
從 `prework_outputs/` 中讀取指定日期的 prepared CSV。

---

### Step 2：建立時間摘要表
依每個 `obsTime` 統計：

- 有效站數
- 平均雨量
- 最大雨量
- 標準差

用來判斷哪一個時刻最適合作為正式分析時間。

---

### Step 3：選定正式事件時刻
為每個事件選出一個最具代表性的 `obsTime`，例如：

- 梅花颱風的一個主要降雨高峰時刻
- 1029 豪雨的一個主要降雨高峰時刻

---

### Step 4：轉為 GeoDataFrame 並投影
將資料轉為 GeoDataFrame，並投影到：

- `EPSG:3826`

同時建立：

- `easting`
- `northing`

供後續 Kriging、IDW、RF 等方法使用。

---

### Step 5：執行四種空間內插方法
主分析 Notebook 目前比較以下四種方法：

1. **Nearest Neighbor**
2. **IDW**
3. **Ordinary Kriging**
4. **Random Forest**

---

### Step 6：Variogram 比較
Kriging 會比較至少兩種 variogram 模型，例如：

- `spherical`
- `exponential`

再選擇其中較適合的模型作為正式分析使用。

---

### Step 7：圖片輸出
主分析 Notebook 會產出以下圖件：

- 降雨分布圖
- 四方法 2×2 比較圖
- Kriging vs RF 差異圖
- Sigma Map
- Variogram summary table
- Writing Area（作業文字撰寫區）

---

### Step 8：GeoTIFF 輸出
主分析 Notebook 預設可輸出以下 raster 檔：

- `kriging_rainfall.tif`
- `kriging_variance.tif`
- `rf_rainfall.tif`

---

## 五、必要輸入資料

請先確認以下資料已準備完成。

### 1. 測站 metadata 來源
- `fungwong_202511.json`

### 2. 2022 年每日雨量 CSV
需先從 CoLife 日資料 ZIP 解壓後取得，例如：

- `rain_20220911.csv`
- `rain_20220912.csv`
- `rain_20220913.csv`
- `rain_20220914.csv`
- `rain_20221028.csv`
- `rain_20221029.csv`
- `rain_20221030.csv`
- `rain_20221031.csv`

### 3. 縣市界底圖（選用）
如果要在圖上疊加縣市界，可使用：

- `COUNTY_MOI_1090820.shp`

---

## 六、輸出資料夾說明

### `prework_outputs/`
前處理資料夾，內容包括：

- 測站 metadata
- 每日 merged 資料
- 宜蘭／花蓮有效資料
- prework summary

### `week6_outputs/`
主分析輸出資料夾，內容包括：

- GeoTIFF 檔案
- 可自行擴充存放圖片輸出

---

## 七、建議執行順序

### 第一步：先執行前處理
先執行：

- `prework_prepare_rainfall_data.ipynb`

確認成功產出：

- `prework_outputs/`

---

### 第二步：再執行主分析
再執行：

- `Week6_Shootout_v2.ipynb`

並確認下列步驟正常：

- 成功讀取 prepared CSV
- 成功建立時間摘要表
- 成功選定正式事件時刻
- 成功轉換為 EPSG:3826
- 成功完成四種內插
- 成功繪製比較圖與 Sigma Map
- 成功輸出 GeoTIFF

---

## 八、套件需求

建議 Python 環境包含以下套件：

- `pandas`
- `numpy`
- `geopandas`
- `matplotlib`
- `scipy`
- `scikit-learn`
- `pykrige`
- `rasterio`

---

## 九、注意事項

1. `station_id` 並不是 100% 都能與 metadata 成功對上，但目前對應率已足夠進行分析。  
2. 主分析時建議優先使用較穩定的累積雨量欄位，例如：
   - `HOUR_3`
   - `HOUR_6`
   不建議直接使用瞬時 `RAIN`。  
3. 若 Kriging 結果出現負值，建議在視覺化前裁切為 0。  
4. 四方法比較圖建議使用一致的色階範圍，才方便比較不同方法的差異。  
5. 若要在圖上疊加縣市界底圖，請先確認底圖已轉為 `EPSG:3826`。  
6. Variogram summary table 與 variogram comparison figure 建議後續再補齊，以符合 Week 6 作業完整要求。

---

## 十、可延伸的期末專題方向

本流程也適合延伸成期末專題，例如：

- 不同降雨事件下空間預測方法比較
- 颱風與豪雨事件之降雨場差異分析
- 降雨空間預測在避難所風險評估上的應用
- 結合地形、河川與降雨的防災決策支援分析

---

## 十一、建議檔案清單

- `prework_prepare_rainfall_data.ipynb`
- `Week6_Shootout_v2.ipynb`
- `fungwong_202511.json`
- 2022 年每日雨量 CSV
- （選用）`COUNTY_MOI_1090820.shp`

---

## 十二、備註

本 README 是依照目前兩份 Notebook 的流程整理而成。  
若後續有新增以下內容，建議同步更新 README：

- variogram comparison figure
- 自動存圖功能
- 底圖疊加
- 自動挑選最佳事件時刻的邏輯
