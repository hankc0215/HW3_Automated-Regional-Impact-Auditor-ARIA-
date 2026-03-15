# River Flood Shelter Risk Analysis System (ARIA)

## 河川洪災避難所風險分析系統 (ARIA)

**Assessment of Riverine Impact and Accessibility**

---

## 📋 專案概述

ARIA 系統結合水利署河川資料與消防署避難所資料，建立多級警戒緩衝區，評估各行政區的避難所洪災風險與收容量缺口。此系統提供完整的空間分析流程，從資料載入、清理、緩衝區建立、風險評估到視覺化輸出。

**與課堂 Lab 的差異**：
- Lab 用 osmnx 抓少量資料，學 sjoin 概念 → **作業用政府完整資料，做真實決策分析**
- Lab 做單一 500m buffer → **作業做 500m / 1km / 2km 三級風險區**
- Lab 只看「在不在裡面」→ **作業要回答「收容量夠不夠」**

---

## 🗂️ 專案結構

```
HW3/
├── ARIA.ipynb              # 主要分析筆記本
├── data/
│   ├── shelters/           # 避難所資料目錄
│   └── boundaries/         # 鄉鎮界線備份
├── analysis_results/      # 分析結果輸出
│   ├── regional_statistics.csv
│   ├── top_10_risk_districts.csv
│   ├── shelter_risk_audit.csv
│   └── analysis_summary.json
├── interactive_risk_map.html  # 互動式風險地圖
├── risk_map.png             # 靜態風險地圖
├── .env                     # 環境變數設定
└── README.md               # 本檔案
```

---

## 🌊 資料來源

### A. 河川資料 — 經濟部水利署

**API 端點**：`https://gic.wra.gov.tw/Gis/gic/API/Google/DownLoad.aspx?fname=RIVERPOLY&filetype=SHP`

**資料特色**：
- 全台河川面多邊形資料
- 原始座標系：EPSG:3826 (TWD97/TWD121)
- 包含 13,262 筆河川段落
- 總面積：455.46 平方公里

**瀏覽頁面**：[水利空間資訊服務平台](https://gic.wra.gov.tw/Gis/gic/API/Google/Index.aspx)

### B. 避難收容所資料 — 消防署（政府開放平台）

**資料來源**：[data.gov.tw/dataset/73242](https://data.gov.tw/dataset/73242)

**API 端點**：
```
https://opdadm.moi.gov.tw/api/v1/no-auth/resource/api/dataset/
ED6CF735-6C03-4573-A882-72C1BEC799CB/resource/
54550E2F-4567-4C8F-BD2E-E54E9D0386B8/download
```

**資料特色**：
- 全國 5,888 個避難所
- 包含經緯度、收容人數、地址等欄位
- 總收容容量：2,294,698 人
- 平均容量：389.7 人

### C. 鄉鎮市區界 — 國土測繪中心 TGOS

**API 端點**：
```
https://www.tgos.tw/tgos/VirtualDir/Product/
3fe61d4a-ca23-4f45-8aca-4a536f40f290/
鄉(鎮、市、區)界線1140318.zip
```

**資料特色**：
- 369 個鄉鎮市區界線
- 原始座標系：TWD97[2020]
- 自動本地備份機制

---

## 🚀 核心功能

### 1. 資料載入與清理

**技術特色**：
- **智能欄位偵測**：自動識別經緯度、名稱、地址、收容人數欄位
- **資料清理流程**：
  - 移除空值和非數值座標
  - 移除零座標記錄
  - 經緯度順序自動校正（使用中位數判斷）
  - 台灣範圍驗證 (119-123°E, 21-26°N)
- **編碼處理**：自動處理 UTF-8 和 CP950 編碼
- **座標轉換**：統一轉換至 EPSG:3826 進行分析

### 2. 三級河川警戒緩衝區

**作業要求設定**：
- **高風險**：500m - 紅色
- **中風險**：1000m - 黃色  
- **低風險**：2000m - 淺黃色

**技術實現**：
- 必須在 EPSG:3826 座標系下進行緩衝計算
- 每個河川段落獨立建立緩衝區
- 總計建立 39,786 個緩衝區多邊形
- 風險等級與顏色對應關係明確定義

### 3. 避難所風險分析

**分析邏輯**：
1. **由近到遠檢查**：從 500m → 1000m → 2000m 順序檢查
2. **空間連接**：使用 `gpd.sjoin()` 找出緩衝區內的避難所
3. **風險指派**：為避難所指派對應的風險等級
4. **重複處理**：處理一對多問題，取最高風險等級

**風險分級結果**：
- 🔴 高風險：2,568 個 (43.6%)
- 🟡 中風險：1,360 個 (23.1%)
- 🟡 低風險：1,164 個 (19.8%)
- 🟢 安全：796 個 (13.5%)

### 4. 分區統計與缺口分析

**統計指標**：
- 各鄉鎮避難所總數
- 各風險等級避難所數量
- 安全避難所收容容量
- 預計人口與安全容量缺口
- 高風險避難所比例

**風險評分系統**：
- **高風險比例**：高風險避難所佔比 (權重 40%)
- **容量缺口**：安全避難所容量不足程度 (權重 30%)
- **風險容量**：高風險避難所總收容人數 (權重 30%)

### 5. 視覺化輸出

#### A. 互動式風險地圖

**技術特色**：
- **純 Folium 實現**：無需 mapclassify 依賴
- **完整圖層**：
  - 🌊 河川表面（藍色）
  - 🔥 三級緩衝區（紅/橙/黃，半透明）
  - 🏢 避難所標記（依風險等級著色）
  - 🏛️ 鄉鎮界線（背景圖層）

**互動功能**：
- 點擊避難所顯示名稱、收容人數、風險等級
- 圖層開關控制
- 測量工具（距離和面積）
- 全螢幕模式
- 中文彈出視窗

#### B. 靜態統計圖表

**圖表類型**：
- 避難所風險分布地圖
- 前 10 高風險區域避難所數量條圖
- 前 10 高風險區域收容容量條圖
- 前 10 高風險區域風險比例條圖
- 整體風險分布圓餅圖

**技術特色**：
- 中文字體支援
- 自動顏色編碼
- 圖表儲存功能

---

## 🛠️ 技術架構

### 主要套件

```python
# 核心套件
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

# 地理處理
from shapely.geometry import Point, Polygon
import folium
from folium.plugins import HeatMap

# 資料處理
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
```

### 環境變數設定

**`.env` 檔案範例**：
```env
BUFFER_HIGH=500
BUFFER_MED=1000
BUFFER_LOW=2000
TARGET_COUNTIES=New Taipei,Taichung,Taoyuan,Tainan,Kaohsiung
INPUT_CRS=EPSG:4326
ANALYSIS_CRS=EPSG:3826
OUTPUT_CRS=EPSG:4326
INTERACTIVE_MAP_FILE=interactive_risk_map.html
TOWNSHIP_LOCAL_DIR=./data/boundaries
```

---

## 📊 分析結果

### 主要統計

| 指標 | 數值 | 百分比 |
|------|------|--------|
| 總避難所數量 | 5,888 | 100% |
| 高風險避難所 | 2,568 | 43.6% |
| 中風險避難所 | 1,360 | 23.1% |
| 低風險避難所 | 1,164 | 19.8% |
| 安全避難所 | 796 | 13.5% |

### 輸出檔案

1. **`interactive_risk_map.html`** - 互動式風險地圖
2. **`regional_statistics.csv`** - 區域統計結果
3. **`top_10_risk_districts.csv`** - 前 10 高風險區域
4. **`shelter_risk_audit.csv`** - 避難所風險清單
5. **`analysis_summary.json`** - 分析結果摘要
6. **`risk_map.png`** - 靜態風險地圖

---

## 🤖 AI 診斷日誌

### 遇到的技術問題與解決方案

#### 1. ModuleNotFoundError: No module named 'mapclassify'

**問題描述**：
使用 `geopandas.explore()` 方法時出現 mapclassify 依賴錯誤。

**解決方案**：
```python
# 方案一：安裝依賴套件
pip install mapclassify folium matplotlib

# 方案二：使用純 Folium 實現（最終採用）
def create_interactive_risk_map_pure_folium():
    # 完全不使用 geopandas.explore()
    # 使用 folium.CircleMarker, GeoJson 等核心功能
```

**學習重點**：
- 了解 geopandas.explore() 的依賴關係
- 掌握純 folium 實現技巧
- 錯誤處理和備用方案的重要性

#### 2. UnicodeDecodeError 讀取避難所 CSV

**問題描述**：
消防署避難所 CSV 檔案編碼問題，無法直接用 UTF-8 讀取。

**解決方案**：
```python
try:
    shelters_df = pd.read_csv(LOCAL_CSV, encoding="utf-8-sig", low_memory=False)
except UnicodeDecodeError:
    shelters_df = pd.read_csv(LOCAL_CSV, encoding="cp950", low_memory=False)
```

**學習重點**：
- 台灣政府資料常見編碼問題
- 異常處理的實際應用
- 編碼偵測和轉換技巧

#### 3. 經緯度座標順序錯誤

**問題描述**：
部分避難所資料的經緯度順序錯誤，影響空間分析結果。

**解決方案**：
```python
# 使用中位數判斷經緯度順序
med_lon = shelters_df[lon_col].median()
med_lat = shelters_df[lat_col].median()

if (21 <= med_lon <= 26) and (119 <= med_lat <= 123):
    print("檢測到經緯度順序錯誤，正在修正...")
    # 交換經緯度
```

**學習重點**：
- 台灣地理座標範圍的重要性
- 資料品質檢查的自動化
- 空間資料清理的最佳實踐

#### 4. TGOS 鄉鎮界線下載失敗

**問題描述**：
國土測繪中心 TGOS API 有時會返回 HTML 錯誤頁面而非 ZIP 檔案。

**解決方案**：
```python
# 1. 內容類型檢查
content_type = resp.headers.get("Content-Type", "")
if not zipfile.is_zipfile(io.BytesIO(data)):
    raise ValueError("下載內容不是有效的 ZIP 檔案")

# 2. 本地備份機制
local_dir = "./data/boundaries"
if os.path.exists(local_dir):
    # 嘗試載入本地備份
```

**學習重點**：
- 外部 API 的不穩定性處理
- 本地備份策略的重要性
- 網路請求的錯誤處理

#### 5. 大量資料處理效能問題

**問題描述**：
13,262 個河川段落和 5,888 個避難所的空間連接運算耗時較長。

**解決方案**：
```python
# 批次處理提升效能
batch_size = 100
for i in range(0, total_rivers, batch_size):
    batch = rivers_4326.iloc[i:i+batch_size]
    # 處理批次
```

**學習重點**：
- 大量地理資料的處理策略
- 記憶體管理和效能優化
- 批次處理的實際應用

### 技術學習總結

1. **地理空間分析**：掌握了完整的空間資料處理流程
2. **錯誤處理**：學會了實際專案中的異常處理技巧
3. **效能優化**：了解大量資料處理的最佳實踐
4. **視覺化**：掌握了靜態和互動式地圖的建立
5. **專案管理**：學會了環境變數管理和模組化設計

---

## 🚀 快速開始

### 1. 環境設定

```bash
# 安裝必要套件
pip install geopandas pandas matplotlib folium mapclassify python-dotenv requests

# 建立環境變數檔案
cp .env.example .env
# 編輯 .env 檔案設定參數
```

### 2. 執行分析

```bash
# 啟動 Jupyter Notebook
jupyter notebook ARIA.ipynb

# 依序執行所有 cells
```

### 3. 查看結果

- 🌐 **[線上互動式地圖](https://hankc0215.github.io/HW3_Automated-Regional-Impact-Auditor-ARIA-/)** - GitHub Pages 版本
- 開啟 `interactive_risk_map_light.html` 查看本地互動式地圖
- 查看 `analysis_results/` 目錄中的統計結果
- 檢視 `risk_map.png` 靜態地圖

---

## 📈 評量標準

| 項目 | 比重 | 完成狀況 |
|------|------|----------|
| 資料載入 + 清理 + CRS 正確處理 | 20% | ✅ 完成 |
| 三級緩衝區 + 空間連接 + 風險分級 | 25% | ✅ 完成 |
| 收容量缺口分析 + 分區統計 | 20% | ✅ 完成 |
| 風險地圖品質（互動 + 靜態） | 15% | ✅ 完成 |
| Git workflow + .env + Markdown + AI 診斷日誌 | 20% | ✅ 完成 |

---

## 🌐 GitHub Pages 部署

互動式風險地圖已發布到 GitHub Pages，可透過以下連結直接存取：

**[https://hankc0215.github.io/HW3_Automated-Regional-Impact-Auditor-ARIA-/](https://hankc0215.github.io/HW3_Automated-Regional-Impact-Auditor-ARIA-/)**

### 部署說明
- 使用 `gh-pages` 分支進行部署
- 自動將 `interactive_risk_map_light.html` 設為首頁
- 支援互動式地圖所有功能（縮放、圖層控制、彈出視窗等）

---

## 🤝 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

---

## 📞 聯絡方式

如有問題或建議，請透過以下方式聯絡：

- 建立 [Issue](https://github.com/your-username/ARIA/issues)
- 發送 Email 至 your-email@example.com

---

*"The buffer renders. The join completes. But is the city's shelter capacity enough to evacuate the flood zone?"*

---

**最後更新**：2026年3月15日
