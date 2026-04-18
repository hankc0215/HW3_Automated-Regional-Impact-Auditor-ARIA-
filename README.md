# ARIA v5.1 — Matai'an Three-Act Auditor

> Week 8 assignment project for reconstructing the 2025 Matai'an barrier-lake event with Sentinel-2 imagery, STAC access, and multi-layer spatial auditing.

## Project overview

This project rebuilds the **three-act evidence chain** of the 2025 Matai'an barrier-lake event in Hualien using **Sentinel-2 L2A**, **Planetary Computer STAC**, and a downstream infrastructure audit.  
The workflow starts from scene selection, then computes reusable change metrics, derives three hazard masks, vectorizes them into polygons, and finally overlays them with ARIA assets from earlier weeks to produce an **Eyewitness Impact Table**, a **coverage gap summary**, and an **AI operational brief prompt**.

Although the notebook filename is `ARIA_v5_mataian_fresh.ipynb` and some internal titles still show **v5.0**, this README is written for the final submitted project version **ARIA v5.1**.

## Assignment goals

This notebook is designed to answer five core questions:

1. Can pre-, mid-, and post-event imagery establish a clear three-act timeline of the Matai'an event?
2. Can a barrier lake be detected before breach using satellite evidence?
3. Can the upstream landslide source and downstream debris footprint be separated with different spectral rules?
4. Which W3 shelters, W7 bottlenecks, and Guangfu overlay nodes intersect the hazard layers?
5. What does the hit pattern reveal about the **coverage gap** of the previous ARIA warning chain?

## Study logic

The project follows this sequence:

1. **Act 1 (Pre-event)**: select a clean forested valley scene before the event.
2. **Act 2 (Mid-event)**: select the key scene that supports the existence of a barrier lake before breach.
3. **Act 3 (Post-event)**: select a post-event scene that supports lake drainage, source scar exposure, and downstream impact.
4. Compute four change metrics: **NIR drop**, **SWIR post brightness**, **BSI change**, and **NDVI change**.
5. Build three masks:
   - **C1** Barrier lake mask
   - **C2** Landslide source scar mask
   - **C3** Debris flow footprint mask
6. Vectorize the masks into polygons.
7. Overlay the hazard polygons with W3 / W7 / Guangfu layers.
8. Export the final map, impact table, geopackage, and AI Advisor prompt.

## Main methods

### 1. Scene selection
Three Sentinel-2 scenes are selected from fixed date windows using STAC search and manual QA. The chosen scenes must not only have acceptable cloud cover, but also visually support the three-act interpretation.

### 2. Change metrics
Four reusable metrics are generated for both **Pre→Mid** and **Pre→Post** comparisons:

- **NIR drop**: highlights conversion from vegetation to water / wet surface / fresh disturbance
- **SWIR post brightness**: emphasizes exposed soil, rock, and dry disturbed surfaces
- **BSI change**: strengthens detection of newly exposed bare ground
- **NDVI change**: highlights vegetation loss and surface disturbance

### 3. Hazard detection rules
The three hazards are intentionally separated because they represent different surface processes.

#### C1. Barrier lake mask
The barrier lake is treated as **turbid water**, not clear water.  
The rule is based on a pre-event vegetated surface that turns into a low-NIR, water-like target during the mid-event scene.

#### C2. Landslide source scar mask
The upstream source scar is mapped with **NIR drop + high SWIR brightness**, because the signal is dominated by exposed rock / dry soil rather than inundation.

#### C3. Debris flow footprint mask
The downstream debris footprint uses **NDVI drop + BSI increase**.  
This is different from C2 because downstream lowlands are more consistent with fresh muddy deposition over previously vegetated surfaces.

### 4. Spatial audit
The vectorized hazard layers are intersected with:

- **W3 shelters**
- **W7 bottlenecks**
- **W8 Guangfu overlay nodes**

This produces the formal **Eyewitness Impact Table** and the **Coverage Gap Analysis**.

## Project structure

Recommended structure:

```text
ARIA_v5.1/
├─ ARIA_v5_mataian_fresh.ipynb
├─ .env
├─ Ground_truth.gpkg                # optional but strongly recommended
├─ data/
│  ├─ shelters_hualien.gpkg         # or shelters.csv
│  ├─ top5_bottlenecks.gpkg         # or top5_bottlenecks.csv
│  └─ guangfu_overlay.gpkg          # or guangfu_overlay.csv
└─ output/
   ├─ 01_nir_drop_pre_mid.png
   ├─ 02_nir_drop_pre_post.png
   ├─ 03_swir_post_mid.png
   ├─ 04_swir_post_post.png
   ├─ 05_bsi_change_pre_mid.png
   ├─ 06_bsi_change_pre_post.png
   ├─ 07_ndvi_change_pre_mid.png
   ├─ 08_ndvi_change_pre_post.png
   ├─ 09_barrier_lake_mask.png
   ├─ 11_debris_mask.png
   ├─ 12_final_impact_map.png
   ├─ chosen_item_ids.json
   ├─ impact_table.csv
   ├─ lake_mask_local.tif
   ├─ mataian_detections.gpkg
   ├─ nir_drop_pre_post.tif
   ├─ ndvi_change_pre_post.tif
   ├─ bsi_change_pre_post.tif
   ├─ swir_post_post.tif
   ├─ pre_b08.tif
   ├─ post_rgb_preview.png
   └─ ai_prompt.txt
```

## Environment and dependencies

### Python packages
The notebook imports these main libraries:

- `numpy`
- `pandas`
- `matplotlib`
- `geopandas`
- `xarray`
- `rioxarray`
- `rasterio`
- `shapely`
- `python-dotenv`
- `pystac-client`
- `planetary-computer`
- `stackstac`

Recommended installation:

```bash
pip install numpy pandas matplotlib geopandas xarray rioxarray rasterio shapely python-dotenv pystac-client planetary-computer stackstac tabulate
```

> `tabulate` is recommended because `pandas.to_markdown()` in the AI prompt section depends on it.

## `.env` settings

Example `.env` file:

```env
STAC_ENDPOINT=https://planetarycomputer.microsoft.com/api/stac/v1
S2_COLLECTION=sentinel-2-l2a
S2_BANDS=B02,B03,B04,B08,B11,B12
S2_CLOUD_MAX=20

MATAIAN_BBOX=121.28,23.56,121.52,23.76
TARGET_EPSG=32651

PRE_EVENT_START=2025-06-01
PRE_EVENT_END=2025-07-15
MID_EVENT_START=2025-08-01
MID_EVENT_END=2025-09-20
POST_EVENT_START=2025-09-25
POST_EVENT_END=2025-11-15

PRE_CLOUD_MAX=20
MID_CLOUD_MAX=40
POST_CLOUD_MAX=30
```

## Input data

### Required inputs

1. **Sentinel-2 L2A scenes** from the Planetary Computer STAC API
2. **W3 shelter layer**
3. **W7 bottleneck layer**
4. **Guangfu overlay layer**

### Optional input

5. **Ground truth file**: `Ground_truth.gpkg`

The truth layer should contain a `Class` column, with points representing positive and negative samples, such as:

- `landslide`, `ls`, `positive`
- `stable`, `negative`, `veg`

This truth set is used to tune the landslide thresholds.

## How to run

Run the notebook from top to bottom in order. Do not skip cells.

Suggested execution order:

1. Environment and parameter setup
2. Helper functions
3. Pre-event scene search and QA
4. Mid-event scene search and QA
5. Post-event scene search and QA
6. Cube streaming
7. Change metrics
8. Barrier lake mask tuning
9. Landslide threshold tuning
10. Debris flow mask
11. Vectorization
12. Asset loading and impact table generation
13. Coverage gap summary
14. Final impact map
15. AI Advisor prompt export

## Final selected scenes

The executed notebook fixed the following three scene IDs:

- **PRE_ITEM_ID**: `S2A_MSIL2A_20250615T023141_R046_T51QUG_20250615T070417`
- **MID_ITEM_ID**: `S2C_MSIL2A_20250911T022551_R046_T51QUG_20250911T055914`
- **POST_ITEM_ID**: `S2B_MSIL2A_20251016T022559_R046_T51QUG_20251016T042804`

Observed cloud cover from the executed notebook:

- Pre-event: **8.50%**
- Mid-event: **13.52%**
- Post-event: **2.54%**

## Key outputs

### Raster / figure outputs

- Change maps for Pre→Mid and Pre→Post comparisons
- Barrier lake mask figure
- Debris flow mask figure
- Post-event RGB preview
- Final impact map

### Table / vector outputs

- `chosen_item_ids.json`
- `impact_table.csv`
- `mataian_detections.gpkg`
- `ai_prompt.txt`

### Geopackage layers

`mataian_detections.gpkg` contains three layers:

- `barrier_lake`
- `landslide_source`
- `debris_flow`

## Main results summary

Based on the executed notebook:

- Estimated **barrier lake area**: **0.599 km²**
- Estimated **landslide source area**: **23.607 km²**
- Estimated **debris flow footprint area**: **14.094 km²**

Vectorized output counts:

- `barrier_lake`: **117 polygons**
- `landslide_source`: **1493 polygons**
- `debris_flow`: **358 polygons**

Study-area asset counts:

- W3 shelters in study area: **38**
- W7 bottlenecks in study area: **0**
- Guangfu overlay nodes in study area: **5**

Hit summary:

- **W3 hits**: **13**
- **W7 hits**: **0**
- **Guangfu hits**: **4 / 5**

## Coverage gap discussion

The final audit shows that the event is not only an upstream landslide problem. It also creates a downstream operational problem that becomes visible when the Guangfu overlay is added. In the study area, **13 W3 shelters were flagged as impacted**, while **4 of 5 Guangfu overlay nodes were hit**. This means the event footprint extends into a populated downstream corridor that cannot be understood from source-area detection alone.

The most important signal is that **W7 bottlenecks contribute no study-area nodes at all (`top5_sub = 0`)**. This is not just a null result. It is itself evidence of a **coverage gap**. The previous ARIA chain did not place enough strategic monitoring or transport-critical nodes inside the actual downstream impact corridor around Guangfu.

Operationally, this suggests that future ARIA versions should not rely only on upstream hazard-source mapping. The system should explicitly extend the audit zone from the barrier-lake source area into probable downstream runout and settlement corridors, especially where schools, township offices, shelters, and transport-linked community nodes cluster close together.

## AI diagnostic log

This project includes an AI-ready operational prompt saved as `output/ai_prompt.txt`.  
The diagnostic logic embedded in the notebook can be summarized as follows:

### Scene logic

- **Act 1** proves a normal forested pre-event valley.
- **Act 2** provides direct satellite support for the existence of a barrier lake before breach.
- **Act 3** supports lake drainage, source-scar exposure, and downstream disturbance.

### Threshold tuning log

#### Barrier lake
Candidate `nir_mid_max` thresholds tested:

| `nir_mid_max` | Lake area (km²) |
|---|---:|
| 0.12 | 0.5992 |
| 0.15 | 1.2442 |
| 0.18 | 1.7159 |

The notebook selected **`nir_mid_max = 0.12`**, using proximity to the reference target area.

#### Landslide source scar
Candidate threshold pairs tested:

| `nir_drop_min` | `swir_post_min` | Accuracy | Precision | Recall | F1 | Area (km²) |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 0.20 | 0.619 | 1.000 | 0.200 | 0.333 | 23.6072 |
| 0.15 | 0.25 | 0.571 | 1.000 | 0.100 | 0.182 | 4.7296 |
| 0.15 | 0.30 | 0.571 | 1.000 | 0.100 | 0.182 | 1.3534 |
| 0.20 | 0.30 | 0.524 | 0.000 | 0.000 | 0.000 | 0.5319 |
| 0.20 | 0.25 | 0.524 | 0.000 | 0.000 | 0.000 | 2.0921 |

The best row was selected by sorting on **F1**, then **accuracy**, then **precision**.

### Ground-truth log

The executed notebook used:

- **10 landslide truth points**
- **11 stable truth points**

## Interpretation notes

### Why the debris rule is different from C2
The upstream source scar is spectrally closer to freshly exposed rock and dry disturbed soil, so **NIR drop + high SWIR** is a reasonable rule.  
The downstream runout zone is more consistent with fresh muddy deposition over previously vegetated floodplain surfaces, so **NDVI drop + BSI increase** is more appropriate.

### Why W3 / W7 missed Guangfu
The downstream Guangfu corridor is where the coverage gap becomes visible. W3 captures shelters, but W7 does not place any study-area bottlenecks inside the actual audited extent. As a result, the system under-represents downstream disruption even though Guangfu overlay nodes clearly show exposure.

## Known issues and practical notes

1. The notebook title still says **ARIA v5.0**, but this submission is organized as **ARIA v5.1**.
2. The AI prompt cell uses `DataFrame.to_markdown()`, so missing `tabulate` may raise an import error.
3. Some highlight labels in the final map code use names like `W3_shelter` / `W7_bottleneck` / `W8_guangfu_node`, while the impact table stores labels as `W3 Shelter` / `W7 Bottleneck` / `W8 Guangfu Overlay`. If symbol highlighting appears missing, check the string labels before plotting.
4. The `west_gate` note in the barrier-lake section is left as a symbolic placeholder, but the final mask currently uses a full-scene boolean gate.

## Deliverables checklist

Before submission, confirm that the following are included:

- [x] Fixed `PRE_ITEM_ID`, `MID_ITEM_ID`, and `POST_ITEM_ID`
- [x] Change metric figures in `output/`
- [x] Hazard mask outputs in `output/`
- [x] `12_final_impact_map.png`
- [x] `mataian_detections.gpkg` with three layers
- [x] `impact_table.csv`
- [x] `ai_prompt.txt`
- [x] README with item IDs, AI diagnostic log, and coverage-gap discussion

## Conclusion

ARIA v5.1 demonstrates that the Matai'an event can be reconstructed as a coherent three-act satellite narrative: a normal pre-event valley, a detectable pre-breach barrier lake, and a post-breach landscape marked by source-scar exposure and downstream impact. The strongest planning lesson is that the previous ARIA chain did not adequately represent the **Guangfu downstream corridor**, making the coverage gap itself one of the most important findings of the project.
