# Week 14 — GEE Advanced: Long-term Trends & Climate Resilience
## ARIA v9.5 — Student Exercise Notebook (學生練習版)

**課程 (Course):** Remote Sensing and Spatial Information Analysis and Applications  
**主題 (Theme):** Landsat Multi-Decadal Trend Analysis & Resilience Monitoring  
**研究區域 (Study Area):**
- **Lab 1, 3, 4:** 花蓮/太魯閣 (Hualien / Taroko) — 26 年植被趨勢與地震韌性分析
- **Lab 2:** 桃園台地 (Taoyuan Plateau) — 26 年埤塘消失分析

---

## 專案概述 (Project Overview)

本專案使用 Google Earth Engine (GEE) 分析 Landsat 衛星影像，探討台灣地區長期環境變遷與生態系韌性。透過 26 年（2000–2026）的時間序列分析，我們可以：

1. **監測植被長期變化趨勢** — 識別綠化 (greening) 與褐化 (browning) 區域
2. **偵測水體變遷** — 分析桃園埤塘在都市化過程中的消失情形
3. **量化生態系韌性** — 評估 2024 年花蓮地震後植被恢復能力
4. **跨感測器分析** — 結合 Landsat (30m, 26年) 與 Sentinel-2 (10m, 6年) 的優勢

---

## 學習目標 (Learning Objectives)

1. 統一多感測器 Landsat 影像波段，進行一致的長期分析
2. 計算像素級線性趨勢，繪製綠化與褐化地圖
3. 使用 MNDWI 偵測水體變化 — 桃園埤塘 26 年消失分析
4. 量化地震後生態系韌性（恢復速率）

---

## 使用說明 (How to Use)

### 環境需求 (Requirements)

- Python 3.x
- Google Earth Engine 帳號與認證
- 必要套件：`ee`, `geemap`, `numpy`, `pandas`, `matplotlib`

### 設定步驟 (Setup)

1. **安裝必要套件**
   ```bash
   pip install earthengine-api geemap numpy pandas matplotlib
   ```

2. **建立 `.env` 檔案**
   
   在 notebook 同層資料夾建立 `.env` 檔案，內容如下：
   ```text
   GEE_PROJECT_ID=your-google-cloud-project-id
   ```
   
   若你的 Earth Engine 已有預設 project，也可以直接執行；若尚未認證，程式會啟動 `ee.Authenticate()`。

3. **執行 Notebook**
   
   - 標記 **COMPLETE** 的區塊可直接執行，不需修改
- 標有 `# TODO:` 的區塊需要填寫後才能執行
- `# HINT:` 註解提供各練習的提示
- **請依序從上到下執行所有區塊**

---

## Notebook 結構 (Notebook Structure)

### S1 — Environment Setup（環境設定）✅ COMPLETE
- 載入環境變數（從 `.env` 讀取 GEE_PROJECT_ID）
- 初始化 Earth Engine
- 設定中文字體
- 定義研究區域 (AOI)

### S2 — Landsat Band Harmonization（Landsat 波段統一）✏️ EXERCISE
- 統一 Landsat 5/7/8/9 的波段命名
- 應用比例因子與雲遮罩
- 合併四個 Landsat 任務的影像集合

### S3 — NDVI & MNDWI Index Calculation（指標計算）✏️ EXERCISE
- 計算 NDVI（植被健康指標）：(NIR − Red) / (NIR + Red)
- 計算 MNDWI（水體偵測指標）：(Green − SWIR1) / (Green + SWIR1)

### S4 — Annual NDVI Time Series（26 年時間序列）✏️ EXERCISE
- 計算 2000–2026 年每年中位數 NDVI
- 繪製時間序列圖，包含趨勢線與事件標記
- 標記 2009 年莫拉克颱風與 2024 年花蓮地震

### S5 — Pixel-Level Trend Map（逐像素趨勢圖）✏️ EXERCISE
- 使用 `linearFit` 計算每個像素的 NDVI 趨勢
- 繪製綠化（正斜率）與褐化（負斜率）空間分佈圖

### S6 — Taoyuan Pond Disappearance（桃園埤塘消失偵測）✏️ EXERCISE
- 比較早期 (2000–2005) 與近期 (2021–2026) 的水體分佈
- 偵測存活、消失、新增的埤塘
- 使用真彩色影像驗證變遷結果

### S7 — Vegetation Resilience（植被韌性）✏️ EXERCISE
- 計算三個時期的 NDVI 合成影像：
  - 基準期 (Baseline, 2020–2024/03)
  - 衝擊期 (Impact, 2024/04–2024/12)
  - 恢復期 (Recovery, 2025/06–2026/03)
- 計算恢復比率：Recovery ratio = (Recovery − Impact) / (Baseline − Impact)
- 繪製植被恢復程度地圖

### S8b — Landsat × Sentinel-2 Cross-Sensor Analysis（跨感測器分析）✏️ EXERCISE
- 載入 Sentinel-2 影像（2017–2026）
- 比較 Landsat 與 S2 在地震前後的 ΔNDVI
- 分析兩個感測器的解析度差異（30m vs 10m）
- 討論跨感測器分析的優勢與應用時機

---

## 相較 W13 的升級 (Upgrade from W13)

```
W13: Sentinel-2  (6 年,  10m) → "地震後發生了什麼變化？"
W14: Landsat     (26 年, 30m) → "過去二十多年持續發生什麼變化？"
     + 桃園埤塘消失分析 (MNDWI)
     + 韌性指標（擾動後恢復速率）
```

---

## 研究區域座標 (Study Area Coordinates)

### 太魯閣焦點區 (Lab 1, 3, 4)
```python
TAROKO_BBOX = [121.34526379253053, 24.046021742135874,
               121.85149217685861, 24.35767637905926]
```

### 桃園台地完整範圍 (Lab 2, D6)
```python
TAOYUAN_BBOX = [120.94, 24.83, 121.35, 25.08]
```

### 桃園都市化走廊 (Lab 2, D7)
```python
TAOYUAN_URBAN_BBOX = [121.00, 24.88, 121.28, 25.05]
```

---

## 主要發現 (Key Findings)

### 太魯閣 26 年植被趨勢
- 整體呈現輕微正趨勢（約 +0.00187 NDVI/year）
- 26 年累積變化約 +0.0487，代表長期植被狀態略有增加
- 2024 年地震後出現短期下降，但落在長期波動範圍內

### 桃園埤塘消失
- 紅色消失區域主要集中在中壢、桃園市區周邊及高鐵走廊
- 消失埤塘位置多對應到建物、道路或整地區
- 埤塘消失可能增加都市洪水風險

### 植被韌性
- 高恢復比率區域（綠色）多位於坡度較緩、土壤保留完整的地形
- 低恢復比率區域（紅色）多對應到崩塌裸露地、破碎邊坡或裸岩
- 建議主動復育集中在「恢復慢且風險高」的區域

### 跨感測器分析
- Sentinel-2 NDVI 通常低於 Landsat（因 10m 解析度能捕捉更多細節）
- S2 能看見 Landsat 看不到的細緻崩塌邊界與道路破壞
- Landsat 適合長期趨勢分析，S2 適合近期細節判釋

---

## 檔案說明 (File Description)

- `Week14-Student-executable-filled-checked.ipynb` — 完整填寫並可執行的學生練習版本
- `Week14-Student.ipynb` — 需要學生填寫的練習版本
- `.env` — GEE 專案 ID 設定檔（不上傳至 GitHub）
- `.gitignore` — Git 忽略檔案設定

---

## 授權與引用 (License & Citation)

本專案為教學用途，請依照課程規範使用。

---

## 聯絡資訊 (Contact)

如有問題，請聯繫課程助教或授課教師。
