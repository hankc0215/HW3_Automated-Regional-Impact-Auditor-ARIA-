# ARIA v3.0 - Dynamic Risk Monitoring System

## Overview
ARIA v3.0 is an advanced rainfall risk monitoring system that processes real-time or simulated weather data to assess shelter safety and provide emergency response recommendations.

## Features
- **Dual Mode Operation**: Live API mode or Simulation mode
- **Dynamic Risk Assessment**: Real-time risk categorization (CRITICAL/URGENT/WARNING/SAFE)
- **Interactive Mapping**: Folium-based visualization with heatmaps and markers
- **Shelter Analysis**: Spatial analysis of shelter locations relative to rainfall stations
- **Emergency Recommendations**: Automated commander suggestions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hankc0215/ARIA.git
cd ARIA
git checkout ARIA_V3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Create a `.env` file with the following variables:

```env
APP_MODE=SIMULATION  # or LIVE
CWA_API_KEY=your-cwa-api-key
SIMULATION_DATA=data/scenarios/fungwong_202511.json
SHELTER_FILE=data/shelters/shelters_composite_risk.csv
BUFFER_METERS=5000
RAIN_URGENT=40
RAIN_CRITICAL=80
TARGET_CENTER_LAT=23.987
TARGET_CENTER_LON=121.601
OUTPUT_HTML=ARIA_v3_Fungwong.html
```

## Usage

Run the Jupyter notebook:
```bash
jupyter notebook ARIA_v3_Week5.ipynb
```

The notebook contains cells for:
1. Mode switching (SIMULATION/LIVE)
2. Data loading (shelters and rainfall)
3. Data normalization and processing
4. Spatial analysis and risk assessment
5. Interactive map generation

## Data Sources

### Simulation Mode
- Uses historical typhoon data from CoLife database
- Sample file: `fungwong_202511.json`

### Live Mode
- Connects to Central Weather Agency API (O-A0002-001)
- Real-time rainfall station data

## Risk Assessment Logic

- **CRITICAL**: 1hr rainfall ≥ 80mm
- **URGENT**: 1hr rainfall ≥ 40mm
- **WARNING**: 1hr rainfall ≥ 20mm
- **SAFE**: Below warning threshold

## Output

- Interactive HTML map with shelter risk levels
- Rainfall heatmaps
- Station markers with detailed information
- Emergency commander recommendations

## File Structure

```
ARIA_V3/
├── ARIA_v3_Week5.ipynb      # Main analysis notebook
├── ARIA_v3_Fungwong.html    # Generated interactive map
├── data/
│   ├── scenarios/           # Simulation data files
│   └── shelters/           # Shelter location data
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
└── README_ARIA_V3.md       # This file
```

## Dependencies

- pandas: Data processing
- geopandas: Spatial analysis
- folium: Interactive mapping
- python-dotenv: Environment management
- requests: API calls
- numpy: Numerical operations

## License

This project is part of the ARIA (Advanced Risk Intelligence and Assessment) system.

## Contributing

When contributing to this branch:
1. Do not modify the master branch
2. Test both SIMULATION and LIVE modes
3. Ensure .env file is never committed
4. Follow the existing code structure
