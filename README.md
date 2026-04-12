# ARIA v4.0 — The Accessible Auditor

A network-based disaster accessibility analysis system for Hualien, Taiwan.  
This project extends the previous ARIA workflow by combining road network analysis, rainfall-driven congestion, bottleneck detection, and isochrone shrinkage analysis to evaluate how accessibility collapses during extreme weather events.

---

## 1. Project Goal

This notebook was developed for **Week 7 Assignment: ARIA v4.0**.  
The main objective is to evaluate how Typhoon Fung-wong affects transportation accessibility in **Hualien City / Xiulin Township**, with emphasis on:

1. identifying **road bottlenecks**
2. locating **vulnerable high-centrality transportation nodes**
3. estimating **pre-disaster vs post-disaster accessibility**
4. measuring how much reachable area shrinks for key emergency facilities

The final system integrates:

- OpenStreetMap road network data via **OSMnx**
- shelter / facility data from previous assignments
- terrain risk information
- rainfall station data from `fungwong_202511.json`
- accessibility impact summary tables
- static plots and interactive Folium maps

---

## 2. Repository Structure

```text
.
├── ARIA_v4.ipynb
├── hualien_network.graphml
├── fungwong_202511.json
├── shelters_composite_risk.csv
├── README.md
├── .env                      # optional
└── outputs_aria_v4_clean/
    ├── study_area.geojson
    ├── shelters_filtered_to_network.geojson
    ├── rainfall_stations_filtered.geojson
    ├── road_edge_midpoints_with_rainfall.geojson
    ├── bottleneck_nodes_top5.geojson
    ├── accessibility_impact_table.csv
    ├── isochrone_detailed_results.csv
    ├── accessibility_summary_plots.png
    ├── accessibility_interactive_map.html
    └── isochrone_*.png
```

---

## 3. Study Workflow

The notebook is organized into the following steps:

### Step 1. Road Network Extraction
- fetch the road network from OpenStreetMap using `OSMnx`
- keep `network_type='drive'`
- project the graph to **EPSG:3826**
- compute edge travel time from road length and speed
- archive the result as `hualien_network.graphml`

### Step 2. Bottleneck Detection
- calculate **betweenness centrality**
- identify the **Top 5 bottleneck nodes**
- overlay bottleneck nodes with terrain risk
- determine which high-centrality nodes are also exposed to higher hazard

### Step 3. Rainfall-to-Congestion Integration
- parse rainfall station data from `fungwong_202511.json`
- use **Past1hr precipitation** as the main congestion driver
- convert rainfall intensity to `congestion_factor`
- assign rainfall to road segments by nearest station
- compute adjusted travel time:

```python
travel_time_adj = original_travel_time / (1 - congestion_factor)
```

### Step 4. Dynamic Accessibility Analysis
- select 5 valid facilities inside the study area
- compute **5-minute and 10-minute isochrones**
- compare:
  - pre-disaster accessibility
  - post-disaster accessibility
- calculate area shrinkage:

```python
shrinkage_percent = 100 * (1 - post_area / pre_area)
```

### Step 5. Visualization
- local static isochrone plots for each facility
- summary bar charts and histograms
- interactive Folium map with:
  - road network
  - facilities
  - pre-disaster isochrones
  - post-disaster isochrones
  - layer control

---

## 4. Main Outputs

### 4.1 Accessibility Impact Table
The notebook generates a summary table with the following columns:

| Facility | Pre-Disaster 5min (km²) | Post-Disaster 5min (km²) | Shrinkage % | Pre-Disaster 10min (km²) | Post-Disaster 10min (km²) | Shrinkage % |
|----------|--------------------------|---------------------------|-------------|---------------------------|----------------------------|-------------|

This table is also exported as:

```text
outputs_aria_v4_clean/accessibility_impact_table.csv
```

### 4.2 Static Figures
- `isochrone_<facility>.png`
- `accessibility_summary_plots.png`

### 4.3 Interactive Map
- `accessibility_interactive_map.html`

---

## 5. Environment and Dependencies

Recommended environment: **Python 3.10+**

Install the required packages:

```bash
pip install osmnx geopandas pandas numpy matplotlib folium networkx shapely alphashape python-dotenv
```

Depending on your environment, you may also need:

```bash
pip install pyproj fiona rasterio
```

---

## 6. Suggested `.env` File

You may optionally create a `.env` file to store reusable parameters:

```env
DEFAULT_SPEED_KMH=40
RAIN_SEARCH_RADIUS=5000
ISOCHRONE_ALPHA=0.003
STUDY_BUFFER_METERS=5000
```

---

## 7. How to Run

1. put all required input files in the project folder
2. open `ARIA_v4.ipynb`
3. run the notebook from top to bottom
4. if `hualien_network.graphml` already exists, the notebook will reuse it
5. check exported outputs inside `outputs_aria_v4_clean/`

---

## 8. Important CRS Rules

A major part of the debugging process in this project involved coordinate reference systems.

### Analysis CRS
All network analysis and area calculations are performed in:

```text
EPSG:3826
```

### Web Map CRS
Folium requires latitude/longitude coordinates, so all layers displayed in the interactive map must be converted to:

```text
EPSG:4326
```

### Key Rule
- **Do analysis in EPSG:3826**
- **Convert to EPSG:4326 only for Folium visualization**

---

## 9. AI Diagnostic Log

This section documents key problems encountered during development and how they were fixed.

### Issue 1. Shelter coordinates were interpreted with the wrong CRS
At one stage, shelter coordinates were loaded as if they were EPSG:3826, but the CSV actually stored longitude/latitude values.  
This caused shelters to fall outside the study area and snap incorrectly to the road network.

**Fix**
- detect coordinate ranges before assigning CRS
- if coordinates look like longitude/latitude, load as `EPSG:4326`
- then reproject to `EPSG:3826`

---

### Issue 2. Rainfall JSON parsing failed
The rainfall file did not use a simple flat station list.  
Instead, station information was stored in:

```text
records -> Station
GeoInfo -> Coordinates
RainfallElement -> Past1hr -> Precipitation
```

**Fix**
- parse the CWA JSON structure explicitly
- extract:
  - `StationId`
  - `StationName`
  - `StationLongitude`
  - `StationLatitude`
  - `Past1hr -> Precipitation`

---

### Issue 3. Static isochrone plots looked distorted
Earlier versions plotted the entire road network in each figure, which stretched the axes and made facility points appear misplaced.

**Fix**
- clip the road network to a local bounding box around each facility
- derive the bounding box from the facility point and isochrone polygons
- plot only local roads for each figure

---

### Issue 4. Facility marker and polygons were inconsistent
Some facility points were plotted from raw shelter geometries, while polygons were generated from snapped network nodes.  
This created visible offsets.

**Fix**
- use the snapped `nearest_node` as the canonical facility point
- derive the facility plot location directly from the network node geometry

---

### Issue 5. Folium map layers were misplaced
Folium was initially given EPSG:3826 coordinates, which caused map layers to appear in the wrong place.

**Fix**
- convert all road, facility, and polygon layers to `EPSG:4326` before adding them to Folium

---

### Issue 6. Polygon overlap made the map too cluttered
Showing all isochrones at once created a confusing web map.

**Fix**
- split polygons into facility-specific `FeatureGroup`s
- keep only roads and facility points visible by default
- allow users to toggle individual facility isochrone layers via `LayerControl`

---

## 10. Notes on Interpretation

This project should be interpreted as a **network accessibility model**, not a full traffic simulation.  
The rainfall-to-congestion mapping is a simplified hazard response model that estimates how accessibility may degrade under heavy rainfall.

Therefore:
- results are best used for **relative comparison**
- the shrinkage ratio is more informative than the exact polygon shape
- bottleneck nodes highlight critical transport dependencies under disruption

---

## 11. Bonus AI Strategy Briefing

The assignment also encourages an AI-generated disaster strategy briefing.  
A possible workflow is:

1. export:
   - Top 5 bottleneck nodes
   - accessibility impact table
   - isolated facilities
2. send them to an LLM
3. ask the model to act as:

> Hualien County Disaster Prevention Command Center Transportation Advisor

Suggested outputs:
- priority road segments to clear
- alternative rescue methods
- resource allocation recommendations

---

## 12. Author

Course assignment project for ARIA v4.0  
Graduate-level geospatial / disaster accessibility analysis using Python

---

## 13. License

For academic and educational use only.
