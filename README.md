# ARIA v2.0 - 整合影響評估系統（地形智慧分析）

**第四週作業：地形智慧整合**

升級第三週 ARIA 系統，整合內政部 20m DEM 進行全面地形風險評估，結合高程與坡度分析與現有河川緩衝區風險等級。

## 📋 專案概述

ARIA v2.0 是一個進階地理空間風險評估系統，結合：
- **河川緩衝區分析**（第三週遺留功能）
- **地形智慧分析**（第四週增強功能）
- **複合風險建模**進行避難所安全評估

### 主要功能
- 多重災害風險評估（河川 + 地形）
- 避難所周圍 500 公尺緩衝區分析
- 高程與坡度統計提取
- 複合風險分類（極高風險/高風險/中風險/低風險）
- 互動式視覺化與報告

## 🗂️ 檔案結構

```
HW4/
├── ARIA_v2.ipynb          # 主要分析筆記本
├── .env                   # 環境設定
├── README.md              # 本檔案
├── Homework-Week4.md      # 作業要求
├── outputs/               # 生成輸出
│   ├── shelters_composite_risk.csv
│   └── high_risk_shelters_scatter.png
└── data/                  # 資料目錄
    ├── shelters.csv       # 避難所位置
    └── rivers.shp        # 河川資料
```

## 🛠️ 環境設定

### 必要套件
```python
REQUIRED_PACKAGES = [
    'rioxarray',      # DEM 處理
    'rasterio',       # Raster I/O
    'geopandas',      # 向量資料處理
    'matplotlib',     # 視覺化
    'numpy',          # 數值運算
    'pandas',         # 資料操作
    'scipy',          # 科學計算
    'requests',       # HTTP 請求
    'python-dotenv',  # 環境變數
    'rasterstats'     # 區域統計
]
```


## 📊 方法論

### 1. 資料準備
- **避難所資料**: 篩選至目標縣市（花蓮縣）
- **坐標系統**: 轉換至 EPSG:3826（TWD97）
- **緩衝區建立**: 每個避難所周圍 500 公尺緩衝區

### 2. 地形分析
- **DEM 處理**: 載入內政部 20m DEM
- **坡度計算**: 從高程計算梯度
- **區域統計**: 提取每個緩衝區的平均高程與最大坡度

### 3. 風險分類邏輯

#### 地形風險分類
```python
def classify_terrain_risk(max_slope):
    if max_slope > 30:      return "HIGH"
    elif max_slope >= 20:    return "MEDIUM" 
    else:                   return "LOW"
```

#### 複合風險邏輯
- **極高風險**: 河川距離 < 500m **且** 坡度 > SLOPE_THRESHOLD
- **高風險**: 河川距離 < 500m **或** 坡度 > SLOPE_THRESHOLD  
- **中風險**: 河川距離 < 1000m **且** 高程 < ELEVATION_LOW
- **低風險**: 其他所有情況

### 4. 輸出生成
- **CSV**: `shelters_composite_risk.csv` 包含所有風險指標
- **視覺化**: `high_risk_shelters_scatter.png` 散佈圖
- **摘要**: 高風險避難所統計

## 🎯 主要結果

### 風險分布（分析 198 個避難所）
- **極高風險**: 51 個避難所 (25.8%)
- **高風險**: 73 個避難所 (36.9%)
- **中風險**: 22 個避難所 (11.1%)
- **低風險**: 52 個避難所 (26.3%)

### 高風險避難所範例
| 避難所編號 | 名稱 | 風險等級 | 平均高程 (m) | 最大坡度 (°) | 河川距離 |
|-------------|------|------------|-------------------|---------------|----------|
| SH0046 | 和平國小 | 高風險 | 27.50 | 45.47 | 500-1000m |
| SH1306 | 豐南社區活動中心 | 極高風險 | 299.46 | 41.05 | <=500m |
| SH1350 | 富里老人文康中心 | 極高風險 | 238.32 | 30.53 | <=500m |

## 🧠 AI 診斷日誌

### 問題 1： 「Zonal Stats 回傳 NaN」(CRS 未對齊或像素未覆蓋)

**🔍 症狀**: 初始區域統計回傳高程與坡度統計的 NaN 值。

**🛠️ 根本原因分析**:
1. **CRS 不匹配**: 避難所緩衝區為 EPSG:3826，而 DEM 為原始投影
2. **資料型別問題**: DEM 包含干擾計算的 NaN 值
3. **Nodata 處理**: 資料集間不一致的 nodata 值處理

**✅ 解決方案**:
```python
# 1) 對齊 CRS 到 DEM
buffers_for_stats = shelter_buffers.to_crs(dem.rio.crs)

# 2) 準備 DEM array 並處理 nodata
dem2d = dem.squeeze(drop=True)
dem_arr = dem2d.values.astype("float64")
dem_nodata = -9999.0
dem_arr = np.where(np.isnan(dem_arr), dem_nodata, dem_arr)

# 3) 準備 slope array 並保持一致的 nodata
slope_arr = slope_da.values.astype("float64") 
slope_nodata = -9999.0
slope_arr = np.where(np.isnan(slope_arr), slope_nodata, slope_arr)
```

**📋 經驗教訓**:
- 區域操作前務必驗證 CRS 相容性
- 為 raster arrays 實作強健的 nodata 處理
- 使用明確的資料型別轉換以防止隱含問題

---

### 問題 2： 「坡度計算結果不合理」(gradient 的 spacing 參數需與解析度匹配)

**🔍 症狀**: 初始坡度計算顯示不合理的數值（極高或極低角度）。

**🛠️ 根本原因分析**:
1. **錯誤 Spacing**: 使用預設 spacing 參數而非 DEM 解析度
2. **單位不匹配**: 梯度結果為弧度而非預期的度數
3. **解析度忽略**: 未考慮 20m DEM 像素間距

**✅ 解決方案**:
```python
# 使用正確 spacing 進行坡度計算
dem_20m = dem.rio.reproject(dem.rio.crs, resolution=20)
slope_rad = np.gradient(dem_20m, spacing=20, axis=(0,1))
slope_deg = np.degrees(np.arctan(np.sqrt(slope_rad[0]**2 + slope_rad[1]**2)))
slope_da = xr.DataArray(slope_deg, coords=dem_20m.coords, dims=dem_20m.dims)
```

**📋 經驗教訓**:
- Spacing 參數必須符合實際 DEM 解析度（MOI 資料為 20m）
- 梯度結果為弧度 - 需轉換為度數以便解釋
- 務必根據已知地形特徵驗證坡度計算

---

### 問題 3： 「DEM 太大導致 Colab 記憶體不足」(需先裁切)

**🔍 症狀**: 在 Colab 環境中載入完整 DEM 時發生記憶體錯誤。

**🛠️ 根本原因分析**:
1. **完整 DEM 載入**: 嘗試載入整個台灣 DEM
2. **記憶體限制**: 超過 Colab RAM 限制
3. **不必要資料**: 處理目標縣市外的區域

**✅ 解決方案**:
```python
# 處理前將 DEM 裁切至目標區域
target_bounds = shelters.total_bounds
dem_clipped = dem.rio.clip_box(
    xmin=target_bounds[0]-1000,  # 加入緩衝邊界
    ymin=target_bounds[1]-1000,
    xmax=target_bounds[2]+1000, 
    ymax=target_bounds[3]+1000
)
```

**📋 經驗教訓**:
- 處理前務必裁切 raster 資料至感興趣區域
- 為緩衝區加入安全邊界以確保完整覆蓋
- 在雲端環境中監控記憶體使用量

## 🚀 使用說明

### 1. 環境設定
```bash
# 安裝必要套件
pip install rioxarray rasterio geopandas matplotlib numpy pandas scipy requests python-dotenv rasterstats

# 設定環境變數
cp .env.example .env
# 編輯 .env 與您的設定
```

### 2. 執行分析
```python
# 按順序執行筆記本儲存格
jupyter notebook ARIA_v2.ipynb
```

### 3. 檢視結果
- 檢查 `outputs/` 目錄中的生成檔案
- 開啟 `high_risk_shelters_scatter.png` 進行視覺化
- 檢視 `shelters_composite_risk.csv` 獲得詳細結果

## 📈 效能指標

- **處理時間**: 198 個避難所約 2-3 分鐘
- **記憶體使用**: DEM 裁切後約 500MB
- **精確度**: 20m 解析度地形分析
- **覆蓋範圍**: 完整花蓮縣避難所評估

## 🔧 技術規格

### 坐標參考系統
- **輸入**: EPSG:4326 (WGS84) 避難所坐標
- **分析**: EPSG:3826 (TWD97) 緩衝區操作
- **DEM**: 原始內政部投影，按需重投影

### 資料來源
- **避難所**: 國家災害防救科技中心災害避難所資料庫
- **DEM**: 內政部 20m 數值高程模型
- **河川**: 國家河川網路資料

### 品質保證
- 每個處理步驟的 CRS 驗證
- NaN 偵測與處理
- 空間操作的邊界檢查
- 已知位置的結果驗證

## 🤝 貢獻指南

1. 遵循現有程式碼結構
2. 為新功能加入 Captain's Log 條目
3. 更新 AI診斷日誌 記錄遇到的任何問題
4. 提交前驗證所有輸出

## 📝 授權

本專案為 [課程名稱] 課程的一部分，僅供教育目的使用。

---

**ARIA v2.0 開發團隊**  
第四週：地形智慧整合  
日期：2026年3月

## 🎯 任務狀態：✅ 完成

所有第四週目標已達成：
- ✅ DEM 整合與地形分析
- ✅ 複合風險建模
- ✅ 視覺化與報告
- ✅ AI 診斷文件
- ✅ 專業基礎設施標準
