# ARIA v8.0 — Classification Engine Report

## Abstract

This project upgrades ARIA from threshold-based change detection to a multi-class classification engine. Using post-earthquake Sentinel-2 L2A imagery over the Xiulin / Taroko study area, I applied SCL cloud masking, K-means unsupervised clustering, and Random Forest supervised classification to map five land-cover classes: water, forest, cropland, bare/landslide, and built-up areas. Internal validation was conducted using a train/test split, confusion matrix, OOB accuracy, and macro/weighted F1 comparison. External validation compared the Random Forest bare/landslide class against the SWCB official post-earthquake landslide inventory. Results show that supervised classification provides more operationally interpretable land-cover information than single-index thresholds, but its reliability depends strongly on training sample quality and class definition. The SWCB comparison highlights uncertainty caused by temporal gaps, 20 m spatial resolution, mixed pixels, and differences between broad bare-land classification and official landslide mapping.

## Study Area and Data

The study area is Xiulin / Taroko, defined by BBOX `[121.4, 24.1, 121.8, 24.25]`. Sentinel-2 L2A imagery was selected through a progressive STAC search after the 2024 Hualien earthquake. Classification used B02, B03, B04, B08, B11, and B12. SCL was used to mask cloud, cloud shadow, cirrus, and snow pixels.

Selected scene: `S2A_MSIL2A_20240827T022531_R046_T51QUG_20240827T053853`  
Datetime: `2024-08-27 02:25:31.024000+00:00`  
Cloud cover: `8.36%`

## Task 1: K-means

K-means with K=5 was applied to standardized 6-band reflectance features. The output map is saved as `kmeans_classification.png`, and the mean spectral table is saved as `kmeans_cluster_spectral_table.csv`. K-means was useful for exploring spectral clusters, especially water and forest, but built-up, cropland, bare riverbed, and landslide surfaces were harder to interpret because they can share high visible and SWIR reflectance.

## Task 2: Random Forest

Random Forest was trained with five classes: Water, Forest, Cropland, Bare/Landslide, and Built-up. The classification map is saved as `rf_classification.png`. Training accuracy was 0.936, test accuracy was 0.837, and OOB accuracy was 0.846. The most important band was `B12` (SWIR2).

## Task 3: Accuracy Assessment and SWCB Validation

The confusion matrix is saved as `confusion_matrix.png`, and the classification report is saved as `classification_report.csv`. Macro F1 was 0.837, weighted F1 was 0.837, and the weighted-minus-macro gap was 0.000. For SWCB validation, recall was 0.590, precision was 0.003, and IoU was 0.003. Perfect overlap is unlikely because of temporal gap, Sentinel-2 20 m mixed pixels, cloud/shadow effects, and class definition differences.

## Task 4: AI Classification Report

Area statistics are saved as `class_area_stats.csv`, and the AI-style report is saved as `ai_classification_report.txt`.

本次分析以 Sentinel-2 L2A 災後影像建立秀林／太魯閣周邊土地覆蓋分類圖，分類方法為 Random Forest，使用 Blue、Green、Red、NIR、SWIR1 與 SWIR2 六個波段，並以 SCL 遮罩排除雲、雲影與雪等不可靠像素。分類結果顯示，若將近海區域納入統計，全研究區面積最大的類別為 Water，面積約為 22224.9 公頃，占有效分類像素的 35.2%。其中 Water 面積約為 22224.9 公頃，占 35.2%，主要可能分布於太平洋沿岸與河道區域。由於本研究區 BBOX 同時包含山區與海域，因此解讀土地覆蓋概況時應區分「全研究區」與「陸域部分」。

在陸域部分，排除 Water 後面積最大的類別為 Bare/Landslide，面積約為 16692.4 公頃，占有效分類像素的 26.4%。Forest 面積約為 11309.0 公頃，占 17.9%，反映太魯閣周邊仍具有大面積山區植被覆蓋。

Bare/Landslide 類別面積約為 16692.4 公頃，占有效分類像素的 26.4%。此類別在空間上可能集中於山區坡面、河谷兩側、道路邊坡與裸露河床，反映地震後崩塌、新裸露坡面、河道堆積或部分道路與建物混合像素。不過，這個類別不應直接等同於官方崩塌地，因為 Sentinel-2 解析度為 20 m，單一像素可能混合植被、陰影、裸露地表與人工構造物。

與 SWCB 官方新生崩塌地資料比對後，IoU 為 0.003。若此數值偏低，代表模型與官方判釋之間仍存在空間差異，可能原因包含影像日期與官方判釋日期不同、Sentinel-2 空間解析度較粗，以及 Random Forest 的 Bare/Landslide 類別定義比「官方崩塌地」更廣。建議後續將此分類圖作為初步篩選圖層，優先疊合道路、避難所、坡度、河道距離與聚落位置，以找出需要現地複查或高解析影像補充的高風險區域。

## ARIA v8.0 Upgrade Reflection

Threshold methods are transparent and simple, but they usually measure only one spectral dimension at a time. ARIA v8.0 improves the workflow by using multi-band classifiers, which can produce a complete land-cover map for operational overlay analysis. However, classifiers are not automatically more reliable. Their results depend on training sample quality, class balance, and whether classes are spectrally separable. In the Taroko case, forest and water are relatively clear, while landslides, bare riverbeds, roads, and built-up pixels can be similar. Therefore, the Random Forest map should be used as a decision-support layer and combined with SWCB inventory, terrain slope, road networks, shelters, and field verification.
