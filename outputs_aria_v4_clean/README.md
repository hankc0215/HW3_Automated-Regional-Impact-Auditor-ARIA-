# ARIA v4.0 — Clean Rebuild

## Overview
This repository contains a cleaned notebook version of the Week 7 ARIA v4.0 assignment.  
The workflow analyzes how disaster rainfall alters road-network accessibility in **Hualien City, Taiwan**.

## Main Inputs
- `shelters_composite_risk.csv`
- `fungwong_202511.json`
- `hualien_network.graphml` (generated on first successful OSM fetch)

## Main Outputs
- `betweenness_centrality.csv`
- `top5_bottlenecks.csv`
- `bottleneck_terrain_overlay.csv`
- `rainfall_stations_filtered.geojson`
- `road_edge_midpoints_with_rainfall.geojson`
- `accessibility_impact_table.csv`
- `isochrone_detailed_results.csv`
- `isochrone_*.png`
- `accessibility_summary_plots.png`
- `accessibility_interactive_map.html`

## Workflow
1. Fetch or load Hualien road network
2. Project network to EPSG:3826
3. Estimate road speed and baseline travel time
4. Compute betweenness centrality and top-5 bottlenecks
5. Load shelters and filter them to the study network area
6. Overlay bottlenecks with nearest shelter terrain context
7. Parse CWA rainfall JSON and assign rainfall to road segments
8. Adjust travel times using congestion factors
9. Compute 5-minute and 10-minute pre/post-disaster isochrones
10. Compare area shrinkage and create static / interactive outputs

## Diagnostics / Fixes Used
- **CRS mismatch**: all analysis layers are forced to EPSG:3826; Folium conversion happens only at export time.
- **Shelters outside study area**: shelters are clipped to the network convex hull plus buffer.
- **Facility plotting errors**: facility points are drawn using the snapped nearest network node, not raw lon/lat.
- **Messy maps**: static plots use local road windows; Folium isochrones are grouped by facility and hidden by default.
- **Missing road speeds**: a default speed plus highway-type mapping is used when OSM maxspeed is missing.

## Notes
- The notebook includes an optional AI bonus cell that only runs when `GOOGLE_API_KEY` is available.
- If OSM download fails, rerun later or keep a cached GraphML copy in the notebook folder.
