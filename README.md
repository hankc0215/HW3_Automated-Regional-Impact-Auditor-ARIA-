# ARIA V7 - SAR Sensor Fusion for Flood Detection

## Project Overview

This project demonstrates SAR (Synthetic Aperture Radar) sensor fusion techniques for flood detection using Sentinel-1 and Sentinel-2 data. The analysis focuses on detecting water bodies and flood extent using multi-sensor approaches as part of the ARIA V7 framework.

## Repository Structure

```
ARIA_V7/
├── Week10_Student_Completed_ARIA_v7.ipynb     # Main analysis notebook
├── Week10_SAR_Sensor_Fusion_ARIA_v7_PreLab.ipynb  # Pre-lab exercises
├── README.md                                   # This file
├── requirements.txt                            # Python dependencies
├── setup.py                                   # Package setup
├── .gitignore                                 # Git ignore file
└── output/                                    # Generated visualizations
    ├── W10_L1_sar_flood.png
    ├── W10_L2_confidence_map.png
    ├── W10_optical_vs_sar.png
    └── W10_sar_before_after.png
```

傳統光學遙測資料容易受到雲層、雲影與日照條件影響，特別是在颱風、豪雨或山區災害情境下，災後影像常有大面積雲覆蓋，導致水體與崩塌區難以即時判讀。因此，本作業使用 **Sentinel-1 SAR** 作為主要資料來源之一，利用 SAR 可穿透雲層、日夜皆可觀測的特性，進行災前與災後水體變化分析。

本專案主要完成以下任務：

1. 使用 Microsoft Planetary Computer STAC API 搜尋 Sentinel-1 RTC 資料。
2. 讀取 Sentinel-1 VV band，並將 linear backscatter 轉換為 dB。
3. 比較災前與災後 SAR backscatter 變化。
4. 使用 median filter 降低 SAR speckle noise。
5. 以 SAR threshold 偵測堰塞湖水體。
6. 使用 Sentinel-2 NDWI 與 cloud mask 進行 optical comparison。
7. 建立 SAR + Optical 的 4-class sensor fusion confidence map。
8. 使用 Copernicus DEM 作為地形脈絡展示，討論山區 SAR false positives 的限制。

---

## 2. Repository Structure

建議的 GitHub 檔案結構如下：

```text
.
├── Week10_Student_Completed_ARIA_v7_SAR_Sensor_Fusion.ipynb
├── README.md
└── outputs/
    ├── W10_sar_before_after.png
    ├── W10_L1_sar_flood.png
    ├── W10_L2_confidence_map.png
    └── W10_optical_vs_sar.png
```

---

## 3. Data Sources

本作業使用的資料來源如下：

| Data | Source | Usage |
|---|---|---|
| Sentinel-1 RTC | Microsoft Planetary Computer STAC | SAR VV backscatter, flood / water detection |
| Sentinel-2 L2A | Microsoft Planetary Computer STAC | NDWI, optical water detection, cloud mask |
| Copernicus DEM GLO-30 | Microsoft Planetary Computer STAC | Terrain context and slope discussion |

其中 Sentinel-1 RTC 已完成 radiometric terrain correction，因此本作業主要處理：

```python
dB = 10 * np.log10(linear_backscatter)
```

---

## 4. Environment

主要使用 Python 與 Jupyter Notebook 執行。建議套件如下：

```bash
pip install numpy pandas matplotlib scipy scikit-learn rasterio rioxarray pystac-client planetary-computer stackstac xarray shapely geopandas
```

主要 Python libraries：

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pystac_client
import planetary_computer as pc
import stackstac
import xarray as xr
from scipy.ndimage import median_filter
```

---

## 5. Workflow

### 5.1 Sentinel-1 SAR Search

本作業使用 STAC 搜尋 Sentinel-1 RTC 影像。與 Sentinel-2 不同，SAR 為 active remote sensing，不需要太陽光，也不需要雲量篩選。

使用的 collection：

```python
collection = "sentinel-1-rtc"
asset = "vv"
```

災前與災後影像分別用於比較 backscatter 變化：

| Scene | Date | Sensor |
|---|---|---|
| Pre-event | 2025-06-26 | Sentinel-1 VV |
| Post-event | 2025-09-18 | Sentinel-1 VV |

---

### 5.2 Linear Backscatter to dB

Sentinel-1 RTC 讀入後為 linear scale，需要轉換為 dB scale，方便解讀與 thresholding：

```python
sar_db = 10 * np.log10(sar_linear)
```

水體通常會因為 mirror-like specular reflection，使雷達回波能量反射離開感測器，因此在 SAR 影像中呈現低 backscatter，也就是較暗的區域。

---

### 5.3 SAR Before / After Comparison

災前與災後 SAR 影像可用於觀察水體或地表狀態的變化。Post–Pre difference map 可協助辨識災後回波降低或增加的區域。

![SAR Before and After](outputs/W10_sar_before_after.png)

從結果可以看到，災後堰塞湖附近出現明顯低 backscatter 區域，代表該區可能由原本的陸地、植被或裸露地轉變為水體、濕潤沉積物，或受到地形陰影影響。

---

### 5.4 Speckle Filtering and Water Detection

SAR 影像具有 speckle noise，若直接 threshold raw SAR，容易產生大量破碎的假水體像素。因此本作業先使用 median filter 進行平滑：

```python
sar_filtered = median_filter(sar_db, size=5)
```

接著使用 SAR threshold 偵測水體：

```python
sar_water = sar_filtered < -14
```

其中 `VV < -14 dB` 為本案例使用的較寬鬆 threshold，目的是在防災早期預警中提高 sensitivity，避免漏掉潛在水體。

![SAR Flood Detection](outputs/W10_L1_sar_flood.png)

結果顯示，SAR 可以大致偵測堰塞湖主體；但山區也出現部分零散低 backscatter 區域，可能是 radar shadow、陡坡地形或濕潤地表造成的 false positives。

---

## 6. Optical Comparison and Sensor Fusion

### 6.1 Optical NDWI and Cloud Mask

光學資料使用 Sentinel-2 L2A 進行 NDWI 分析：

```python
NDWI = (Green - NIR) / (Green + NIR)
```

光學影像可以提供水體的光譜資訊，但在颱風與災後情境下常受雲層遮蔽。因此本作業加入 cloud mask，用來標示光學資料不可靠的區域。

![Optical vs SAR](outputs/W10_optical_vs_sar.png)

從比較圖可以看出：

- SAR water detection 不受雲層影響。
- Optical NDWI 在水體邊界與光譜判讀上有優勢。
- 雲層或雲影會造成 optical detection 的不確定性。
- SAR 與 optical 結果不一致的區域，需要進一步檢查地形、雲層與混合像元。

---

### 6.2 Four-Class Fusion Map

本作業建立 4-class confidence map，將 SAR 與 optical water detection 結合：

| Class | Meaning | Interpretation |
|---|---|---|
| 0 | No Detection | SAR 與 optical 都未偵測到水體 |
| 1 | Optical Only | 只有 optical 偵測到水體 |
| 2 | SAR Only | 只有 SAR 偵測到水體 |
| 3 | High Confidence | SAR 與 optical 都偵測到水體 |

其中 `High Confidence` 代表兩種感測器皆支持該區為水體，因此可信度較高；`SAR Only` 在雲覆蓋區具有重要價值，但也可能包含 radar shadow false positives；`Optical Only` 則可能受到雲影、光譜混淆或 SAR 幾何限制影響。

![Confidence Map](outputs/W10_L2_confidence_map.png)

---

## 7. DEM and Topographic Audit

本作業使用 Copernicus DEM GLO-30 作為地形脈絡展示，並計算 slope map 輔助理解山區環境。

然而，本案例不直接使用 DEM 進行地形校正，原因是 Copernicus DEM 為災前地形資料。堰塞湖形成通常伴隨崩塌、堆積與河道阻塞，災後地形可能已經大幅改變。若直接使用災前 slope 過濾水體，可能錯誤移除真正的災後水體或新形成的堆積區。

因此，本作業的 DEM 只作為：

1. 地形背景展示。
2. 山區 radar shadow false positives 的討論依據。
3. 說明災後若要進行更可靠的 SAR 地形校正，應使用更新的 DEM。

可用於災後 DEM 更新的方法包括：

- Airborne LiDAR
- UAV photogrammetry
- InSAR
- Stereo satellite imagery
- Field survey

---

## 8. Main Results

本作業的主要結果如下：

1. **SAR 成功偵測堰塞湖主體**  
   Sentinel-1 VV backscatter 在災後堰塞湖區域呈現較暗訊號，符合水體在 SAR 中低 backscatter 的特徵。

2. **Median filter 有效降低 speckle noise**  
   經過 5×5 median filtering 後，SAR 影像較平滑，水體遮罩也較容易判讀。

3. **寬鬆 SAR threshold 適合早期預警，但會增加 false positives**  
   `VV < -14 dB` 可以提高偵測敏感度，但山區陰影與陡坡區也可能被誤判為水體。

4. **Sensor fusion 提高判讀可信度**  
   SAR 與 optical 同時偵測到的區域可信度較高；不一致區域則可作為人工檢查或後續驗證的優先區。

5. **DEM 不應直接用於本案例地形校正**  
   因為使用的是災前 DEM，不代表崩塌後實際地形，只適合用於地形脈絡與限制討論。

---

## 9. Threshold Challenge

本作業比較兩種 SAR threshold 策略：

| Threshold | Strategy | Strength | Limitation |
|---|---|---|---|
| `VV < -14 dB` | Loose threshold | 較不容易漏掉潛在水體 | false positives 較多 |
| `VV < -18 dB` | Strict threshold | 偵測結果較保守 | 可能低估混濁水或粗糙水面 |

在防災早期預警情境下，較適合使用 **寬鬆門檻 + morphological cleanup**。原因是早期預警更重視不要漏掉潛在水體，尤其山區堰塞湖可能具有混濁水面、粗糙水面、濕泥沙與地形陰影，若直接使用嚴格 threshold 可能低估災害範圍。

不過，寬鬆門檻必須搭配以下方法降低 false positives：

- Median filtering
- Morphological opening / closing
- Connected component filtering
- Optical NDWI comparison
- Cloud mask
- DEM or slope context
- Manual interpretation

---

## 10. Conclusion

本作業顯示 Sentinel-1 SAR 在災害監測中具有重要價值，特別是在光學影像受到雲層遮蔽時，SAR 仍能提供全天候、日夜皆可用的觀測資訊。透過災前與災後 SAR backscatter 比較，可以快速偵測可能的水體擴張或地表變化。

然而，在山區堰塞湖情境中，SAR threshold detection 也容易受到 radar shadow、坡度、地形幾何與地表粗糙度影響。因此，單一感測器或單一 threshold 不足以支撐完整判讀。較可靠的災害監測流程應整合 SAR、optical NDWI、cloud mask、DEM context 與人工驗證，才能建立更穩定的 operational decision support。

In conclusion, SAR provides a valuable all-weather observation source for rapid disaster monitoring, especially when optical imagery is affected by cloud cover. However, in mountainous barrier-lake environments, SAR-based water detection is vulnerable to radar shadow and terrain-induced false positives. Therefore, the most reliable interpretation should combine SAR, optical NDWI, cloud masking, DEM context, and manual validation rather than relying on a single sensor or threshold.

---

## 11. How to Run

1. Clone this repository.

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

2. Install required packages.

```bash
pip install numpy pandas matplotlib scipy scikit-learn rasterio rioxarray pystac-client planetary-computer stackstac xarray shapely geopandas
```

3. Open the notebook.

```bash
jupyter notebook Week10_Student_Completed_ARIA_v7_SAR_Sensor_Fusion.ipynb
```

4. Run all cells from top to bottom.

Because the notebook streams remote sensing data from Microsoft Planetary Computer, internet connection is required. If remote COG reading fails temporarily, re-run the cell or restart the notebook kernel and try again.

---

## 12. Notes

- SAR water detection threshold is scene-dependent.
- `VV < -18 dB` is often used as a general reference, but may be too strict for muddy or rough flood water.
- `VV < -14 dB` is more sensitive and useful for early warning, but needs post-processing.
- Optical NDWI is useful for spectral confirmation but can be blocked by clouds.
- DEM-based terrain correction should use post-disaster DEM if available.
- In this notebook, DEM is used for context only, not for removing detected water pixels.
