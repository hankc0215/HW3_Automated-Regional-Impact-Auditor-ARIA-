# ARIA v4.1 - Accessible Road Infrastructure Auditor

## Disaster Accessibility Assessment System

A comprehensive network analysis system for evaluating road infrastructure accessibility during disaster events, integrating real-time rainfall data with dynamic congestion modeling.

## Overview

ARIA v4.1 combines OpenStreetMap road networks, rainfall intensity analysis, and graph theory algorithms to assess transportation accessibility changes during extreme weather events. The system identifies critical bottlenecks, calculates dynamic travel times, and generates pre/post-disaster accessibility metrics.

## Key Features

### Network Analysis
- **Road Network Extraction**: OSMnx integration with OpenStreetMap
- **Bottleneck Identification**: Betweenness centrality analysis
- **Dynamic Weighting**: Rainfall-based congestion factors
- **Isochrone Analysis**: Travel time polygons and accessibility mapping

### Disaster Impact Assessment
- **Pre/Post-Disaster Comparison**: Accessibility contraction analysis
- **Rainfall-to-Congestion Mapping**: Threshold-based impact modeling
- **Priority Ranking**: Critical facility vulnerability assessment
- **Rescue Route Planning**: Alternative accessibility analysis

### Technical Implementation
- **Coordinate System**: EPSG:3826 (TWD97/TM2) for Taiwan
- **Graph Algorithms**: NetworkX for centrality and path analysis
- **Geospatial Processing**: GeoPandas and Shapely for spatial operations
- **Visualization**: Matplotlib with Chinese language support

## Project Structure

```
ARIA_v4.1/
?? README.md                    # Project documentation
?? ARIA_v4.ipynb               # Main analysis notebook
?? Lab1_Bottleneck_Analysis.ipynb  # NTU test case
?? Week7-Student.ipynb         # Student worksheet
?? hualien_network.graphml     # Road network data
?? accessibility_benefit_cost_table.csv  # Analysis results
?? .gitignore                  # Git ignore rules
?? generate_network.py         # Network generation script
?? verify_installation.py     # Environment verification
?? test_osmnx.py              # OSMnx testing
?? test_networkx.py           # NetworkX testing
?? data/                       # Data directory
    ?? scenarios/              # Simulation scenarios
```

## Environment Setup

### Prerequisites
- Python 3.8+
- Virtual environment support

### Installation
```bash
# Create virtual environment
python -m venv gis-env

# Activate (Windows)
gis-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

### Configuration
Create a `.env` file (excluded from Git):
```bash
# Week 7 Network Analysis
NETWORK_DIST=5000
NETWORK_CRS=EPSG:3826
CONGESTION_METHOD=threshold

# Congestion thresholds (mm/hr)
CONGESTION_BREAK_1=10
CONGESTION_BREAK_2=40
CONGESTION_BREAK_3=80

# API Keys (optional)
GOOGLE_API_KEY=your-api-key-here
CWA_API_KEY=your-cwa-api-key-here
```

## Usage

### Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/hankc0215/ARIA.git
   cd ARIA
   git checkout ARIA_V4.1
   ```

2. **Setup environment**
   ```bash
   gis-env\Scripts\activate
   python verify_installation.py
   ```

3. **Run analysis**
   ```bash
   jupyter notebook ARIA_v4.ipynb
   ```

### Analysis Workflow
1. **Network Extraction**: Extract road network for target area
2. **Projection**: Convert to EPSG:3826 for meter-based calculations
3. **Centrality Analysis**: Identify critical bottlenecks
4. **Dynamic Weighting**: Apply rainfall-based congestion factors
5. **Isochrone Analysis**: Calculate accessibility changes
6. **Impact Assessment**: Generate contraction metrics and priorities

## Key Algorithms

### Congestion Factor Mapping
```python
def rain_to_congestion(rainfall_mm, method='threshold'):
    if rainfall_mm < 10:    return 0.0   # Normal
    elif rainfall_mm < 40:  return 0.3   # Slightly slow
    elif rainfall_mm < 80:  return 0.6   # Severe delay
    else:                   return 0.9   # Almost impassable
```

### Dynamic Travel Time
```python
travel_time_adj = length / ((speed_kph / 3.6) * (1 - congestion_factor))
```

### Accessibility Contraction
```python
contraction_% = (1 - post_disaster_area / pre_disaster_area) * 100
```

## Results

### Sample Output
- **Network Size**: 2,126 nodes, 6,082 edges (Hualien City)
- **Top Bottleneck**: Node ID with highest betweenness centrality
- **Accessibility Loss**: Average 40-50% contraction during extreme events
- **Priority Facilities**: Ranked by vulnerability and impact

### Generated Files
- `hualien_network.graphml` - Road network data
- `accessibility_benefit_cost_table.csv` - Analysis results
- Interactive visualizations and maps

## Technical Specifications

### Dependencies
- **OSMnx** - Road network analysis
- **NetworkX** - Graph algorithms
- **GeoPandas** - Geospatial data processing
- **Rasterio** - Raster data handling
- **Matplotlib** - Visualization
- **Shapely** - Geometric operations

### Performance
- **Network Size**: Supports up to 10,000 nodes
- **Analysis Time**: 1-2 minutes for typical city networks
- **Memory Usage**: ~500MB for 5,000 node networks
- **Coordinate System**: EPSG:3826 (Taiwan TWD97/TM2)

## Applications

### Disaster Management
- **Emergency Response**: Identify critical evacuation routes
- **Resource Allocation**: Prioritize rescue operations
- **Infrastructure Planning**: Assess network resilience

### Urban Planning
- **Transportation Analysis**: Network bottleneck identification
- **Accessibility Studies**: Service area analysis
- **Development Impact**: Infrastructure change assessment

## Contributing

### Development Setup
```bash
# Install project dependencies
pip install -r requirements.txt

# Run tests
python test_osmnx.py
python test_networkx.py

# Code formatting
black *.py
```

### Submission Guidelines
- Follow PEP 8 style guidelines
- Include comprehensive documentation
- Test with multiple network sizes
- Validate coordinate system consistency

## License

This project is part of academic research in disaster accessibility assessment. Please contact the maintainers for usage permissions.

## Citation

If you use this system in your research, please cite:

```
ARIA v4.1: Accessible Road Infrastructure Auditor
Disaster Accessibility Assessment System
Week 7 Network Analysis & Dynamic Accessibility
```

## Contact

- **Repository**: https://github.com/hankc0215/ARIA/tree/ARIA_V4.1
- **Branch**: ARIA_V4.1
- **Maintainer**: Hank Chen

## Acknowledgments

- OpenStreetMap contributors for road network data
- OSMnx development team for network analysis tools
- NetworkX for graph algorithms implementation
- Taiwan Central Weather Administration for rainfall data

---

**Version**: ARIA v4.1  
**Last Updated**: 2026-04-07  
**Target Region**: Hualien County, Taiwan  
**Coordinate System**: EPSG:3826
