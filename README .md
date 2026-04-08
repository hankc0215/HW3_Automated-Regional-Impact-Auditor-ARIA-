# ARIA V4: Rainfall Event Interpolation Analysis

This project implements a comprehensive rainfall spatial interpolation workflow comparing four different methods for weather event analysis in Taiwan.

## 🌟 Project Overview

This repository contains the complete workflow for Week 6 rainfall interpolation analysis, including data preprocessing, spatial interpolation using multiple methods, and comprehensive visualization outputs.

**Key Features:**
- Four interpolation methods comparison (Nearest Neighbor, IDW, Ordinary Kriging, Random Forest)
- Typhoon and heavy rainfall event analysis
- Variogram modeling and uncertainty quantification
- GeoTIFF export for GIS applications
- Comprehensive visualization and statistical analysis

---

## 📁 Project Structure

### Core Analysis Files

#### 1. `prework_prepare_rainfall_data.ipynb`
**Data preprocessing notebook** that prepares raw rainfall data for spatial analysis.

**Functions:**
- Station metadata extraction and processing
- 2022 rainfall CSV data ingestion
- Data filtering for Yilan and Hualien counties
- Quality control and data validation
- Export of prepared datasets

#### 2. `Week6_Shootout_v2.ipynb`
**Main analysis notebook** implementing spatial interpolation methods.

**Functions:**
- Event time selection and analysis
- Four spatial interpolation methods
- Variogram modeling and comparison
- Sigma map generation
- GeoTIFF export functionality

### Data Directories

#### `data/`
- `County/`: Administrative boundary shapefiles (TWD97 EPSG:3826)

#### `prework_outputs/`
- Processed rainfall data for multiple dates
- Station metadata files
- Quality-controlled datasets
- Summary statistics

#### `week6_outputs/`
- Generated GeoTIFF files
- Analysis results and visualizations

#### `2022/`
- Raw rainfall data CSV files from CoLife platform
- Daily rainfall measurements across Taiwan

---

## 🔬 Analysis Workflow

### Phase 1: Data Preprocessing

#### Step 1. Station Metadata Creation
Extract station information from `fungwong_202511.json` to create comprehensive metadata:

- `station_id`: Unique station identifier
- `station_name`: Station name in Chinese
- `county`: Administrative county
- `town`: Administrative township
- `lat`: Latitude (WGS84)
- `lon`: Longitude (WGS84)

This metadata serves as the reference table for merging with 2022 rainfall CSV data.

#### Step 2. Raw Data Ingestion
Read daily rainfall CSV files from 2022, focusing on key events:

- **Typhoon Muifa**: `20220911`–`20220914`
- **1029 Heavy Rainfall**: `20221028`–`20221031`

**Key Data Fields:**
- `station_id`: Station identifier
- `obsTime`: Observation timestamp
- `ELEV`: Station elevation (m)
- `RAIN`: Instantaneous rainfall (mm)
- `MIN_10`: 10-minute cumulative rainfall
- `HOUR_3`: 3-hour cumulative rainfall
- `HOUR_6`: 6-hour cumulative rainfall
- `HOUR_12`: 12-hour cumulative rainfall
- `HOUR_24`: 24-hour cumulative rainfall
- `NOW`: Current accumulated rainfall

#### Step 3. Data Integration
Merge rainfall data with station metadata using `station_id` to add:
- Station names and locations
- Administrative boundaries
- Geographic coordinates

#### Step 4. Spatial Filtering
Filter data to include only target counties:
- **Yilan County** (宜蘭縣)
- **Hualien County** (花蓮縣)

Remove invalid values:
- `-998` (missing data indicator)
- `0` (no rainfall records)

#### Step 5. Export Prepared Data
Preprocessing notebook outputs:
- `station_metadata.csv/json`: Station reference data
- Daily merged datasets (CSV/JSON)
- Filtered Yilan+Hualien valid rainfall data
- `prework_summary.csv/json`: Processing statistics

### Phase 2: Spatial Interpolation Analysis

#### Step 1. Load Prepared Data
Read processed datasets from `prework_outputs/` directory for specified dates.

#### Step 2. Temporal Analysis
Generate time-series summaries for each event:
- Active station count per timestamp
- Mean rainfall statistics
- Maximum rainfall intensity
- Standard deviation analysis

Used to select representative event moments for spatial analysis.

#### Step 3. Event Time Selection
Choose optimal analysis timestamps:
- **Typhoon Muifa**: Peak rainfall moment
- **1029 Heavy Rainfall**: Maximum intensity period

#### Step 4. Coordinate Transformation
Convert data to GeoDataFrame and project to:
- **EPSG:3826** (TWD97)
- Generate `easting` and `northing` coordinates for spatial interpolation

#### Step 5. Interpolation Methods Comparison
Implement and compare four spatial interpolation methods:

1. **Nearest Neighbor**: Simple proximity-based interpolation
2. **Inverse Distance Weighting (IDW)**: Distance-weighted averaging
3. **Ordinary Kriging**: Geostatistical interpolation with variogram modeling
4. **Random Forest**: Machine learning-based spatial prediction

#### Step 6. Variogram Modeling
Test multiple variogram models for optimal kriging:
- `spherical`: Traditional spherical variogram
- `exponential`: Exponential decay model
- Select best-fitting model based on statistical criteria

#### Step 7. Visualization Outputs
Generate comprehensive analysis visualizations:
- Rainfall distribution maps for both events
- 2×2 method comparison plots
- Kriging vs. Random Forest difference maps
- Uncertainty (sigma) maps
- Variogram model comparison tables
- Statistical interpretation summaries

#### Step 8. GIS Export
Export raster outputs (default: Event 1):
- `kriging_rainfall.tif`: Kriging-interpolated rainfall
- `kriging_variance.tif`: Kriging uncertainty estimates
- `rf_rainfall.tif`: Random Forest predictions

---

## 📋 Requirements

### Input Data

#### Essential Files
- **`fungwong_202511.json`**: Station metadata reference
- **2022 Rainfall CSVs**: Daily rainfall data from CoLife platform
  - `rain_20220911.csv` through `rain_20220914.csv` (Typhoon Muifa)
  - `rain_20221028.csv` through `rain_20221031.csv` (1029 Heavy Rainfall)

#### Optional Data
- **Administrative Boundaries**: County shapefiles for base mapping
  - `COUNTY_MOI_1090820.shp` (TWD97 EPSG:3826)

### Software Requirements

#### Python Environment
```bash
pip install pandas numpy geopandas matplotlib scipy scikit-learn pykrige rasterio
```

**Required Packages:**
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing
- `geopandas`: Geospatial data processing
- `matplotlib`: Data visualization
- `scipy`: Scientific computing (interpolation)
- `scikit-learn`: Machine learning (Random Forest)
- `pykrige`: Kriging interpolation
- `rasterio`: raster file I/O

---

## 🚀 Getting Started

### Step 1: Data Preprocessing
Execute the preprocessing notebook:
```bash
jupyter notebook prework_prepare_rainfall_data.ipynb
```

**Verify Outputs:**
- `prework_outputs/` directory created
- Station metadata files generated
- Processed rainfall datasets available

### Step 2: Main Analysis
Run the main analysis notebook:
```bash
jupyter notebook Week6_Shootout_v2.ipynb
```

**Verification Checklist:**
- ✅ Successful data loading from prework outputs
- ✅ Time series summaries generated
- ✅ Event timestamps selected
- ✅ Coordinate transformation to EPSG:3826
- ✅ Four interpolation methods executed
- ✅ Comparison visualizations created
- ✅ Sigma maps generated
- ✅ GeoTIFF files exported

---

## 📊 Output Directory Structure

### `prework_outputs/`
```
prework_outputs/
├── station_metadata.csv          # Station reference data
├── station_metadata.json         # Station reference (JSON)
├── prework_summary.csv           # Processing statistics
├── prework_summary.json          # Processing statistics (JSON)
├── 20220911/                     # Typhoon Muifa data
│   ├── rain_20220911_merged.csv
│   ├── rain_20220911_yl_hl_valid.csv
│   └── ...
└── 20221029/                     # 1029 Heavy Rainfall data
    ├── rain_20221029_merged.csv
    ├── rain_20221029_yl_hl_valid.csv
    └── ...
```

### `week6_outputs/`
```
week6_outputs/
├── kriging_rainfall.tif          # Kriging interpolation result
├── kriging_variance.tif           # Kriging uncertainty estimates
└── rf_rainfall.tif               # Random Forest predictions
```

---

## ⚠️ Important Notes

### Data Quality Considerations
1. **Station ID Matching**: Not all `station_id` values perfectly match metadata, but current matching rate is sufficient for analysis.
2. **Rainfall Field Selection**: Recommend using cumulative rainfall fields for stability:
   - `HOUR_3`: 3-hour cumulative
   - `HOUR_6`: 6-hour cumulative
   Rather than instantaneous `RAIN` values.
3. **Negative Values**: Kriging may produce negative values; clip to 0 for visualization.
4. **Color Scale Consistency**: Use consistent color ranges across all four method comparisons.
5. **Base Map Projection**: Ensure administrative boundaries are projected to EPSG:3826 for overlay.

### Performance Considerations
- Large JSON files (>50MB) may trigger GitHub warnings but function correctly
- Memory usage increases with grid resolution; adjust `GRID_RES` parameter as needed
- Random Forest cross-validation can be computationally intensive

---

## 🎯 Applications

This workflow is suitable for various research and operational applications:

### Academic Research
- Comparative analysis of spatial interpolation methods
- Typhoon vs. heavy rainfall event characterization
- Rainfall field uncertainty quantification
- Topography-rainfall relationship studies

### Operational Applications
- Real-time rainfall mapping systems
- Emergency response decision support
- Flood risk assessment
- Agricultural planning
- Water resource management

### Integration Opportunities
- Shelter risk assessment systems
- Disaster early warning platforms
- Climate impact analysis
- GIS-based decision support tools

---

## 📚 File Inventory

### Core Analysis Files
- `prework_prepare_rainfall_data.ipynb` - Data preprocessing workflow
- `Week6_Shootout_v2.ipynb` - Main spatial interpolation analysis
- `Homework-Week6.md` - Assignment specifications

### Data Files
- `fungwong_202511.json` - Station metadata reference
- `2022/` - Raw rainfall CSV files
- `data/County/` - Administrative boundary shapefiles

### Output Files
- `prework_outputs/` - Processed datasets and metadata
- `week6_outputs/` - Analysis results and GeoTIFF exports

---

## 🔧 Customization

### Event Selection
Modify date parameters in the notebooks to analyze different rainfall events:

```python
# Event folders from prework outputs
EVENT1_DATE = "20220912"   # Typhoon Muifa candidate
EVENT2_DATE = "20221029"   # 1029 heavy rainfall candidate
```

### Interpolation Parameters
Adjust method-specific parameters:

```python
# Random Forest parameters
RF_N_ESTIMATORS = 200
RF_MIN_SAMPLES_LEAF = 3

# Grid resolution
GRID_RES = 1000  # meters
```

### Variogram Models
Test additional variogram models beyond spherical and exponential:
- `gaussian`
- `linear`
- `power`

---

## 📈 Future Enhancements

Potential improvements for subsequent versions:

### Automated Features
- Automatic event time selection algorithms
- Dynamic variogram model optimization
- Integrated quality control metrics
- Batch processing capabilities

### Advanced Analysis
- Machine learning hyperparameter tuning
- Ensemble interpolation methods
- Temporal interpolation analysis
- Cross-validation frameworks

### Visualization Enhancements
- Interactive web-based maps
- 3D rainfall surface visualization
- Animated rainfall evolution
- Real-time dashboard integration

---

## 📞 Support

For questions or issues regarding this workflow:
1. Check the notebook comments for detailed explanations
2. Verify input data format and structure
3. Ensure all required packages are installed
4. Review the troubleshooting section in each notebook

---

## 📄 License

This project is part of the ARIA (Advanced Rainfall Interpolation Analysis) framework. Please refer to the main repository for licensing information.

---

**Last Updated**: April 2026
**Version**: ARIA_V4
**Maintainer**: ARIA Development Team
