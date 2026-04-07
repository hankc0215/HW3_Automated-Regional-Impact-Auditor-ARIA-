#!/usr/bin/env python3
"""
ARIA v4.1 - OSMnx Testing Script
Tests OSMnx functionality for road network extraction
"""

import os
import sys
import traceback

def test_osmnx_import():
    """Test OSMnx import"""
    try:
        import osmnx as ox
        print("?? OSMnx import successful")
        return True, ox
    except ImportError as e:
        print(f"?? OSMnx import failed: {e}")
        return False, None

def test_basic_functionality(ox):
    """Test basic OSMnx functionality"""
    try:
        # Test settings
        print("?? Testing OSMnx settings...")
        ox.settings.log_console = True
        ox.settings.use_cache = True
        print("   Settings configured successfully")
        
        # Test small area extraction
        print("?? Testing network extraction...")
        # Use a small test area (Taipei 101 area)
        north, south, east, west = 25.0340, 25.0330, 121.5645, 121.5635
        
        G = ox.graph_from_bbox(north, south, east, west, network_type="drive")
        print(f"   Extracted graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
        
        # Test graph projection
        print("?? Testing graph projection...")
        G_projected = ox.project_graph(G)
        print("   Graph projection successful")
        
        # Test basic stats
        print("?? Testing basic statistics...")
        stats = ox.basic_stats(G_projected)
        print(f"   Basic stats calculated: {len(stats)} metrics")
        
        return True
        
    except Exception as e:
        print(f"?? OSMnx functionality test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_coordinate_system():
    """Test coordinate system handling"""
    try:
        import osmnx as ox
        print("?? Testing coordinate system...")
        
        # Test Taiwan coordinate system
        north, south, east, west = 25.0340, 25.0330, 121.5645, 121.5635
        G = ox.graph_from_bbox(north, south, east, west, network_type="drive")
        
        # Project to Taiwan CRS
        G_projected = ox.project_graph(G, to_crs="EPSG:3826")
        print("   EPSG:3826 projection successful")
        
        # Get node coordinates
        node_data = list(G_projected.nodes(data=True))[0]
        node_id, node_attrs = node_data
        if 'x' in node_attrs and 'y' in node_attrs:
            print(f"   Sample node coordinates: x={node_attrs['x']:.2f}, y={node_attrs['y']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"?? Coordinate system test failed: {e}")
        return False

def main():
    """Main test function"""
    print("ARIA v4.1 - OSMnx Testing")
    print("=" * 40)
    
    # Test import
    success, ox = test_osmnx_import()
    if not success:
        print("Install OSMnx with: pip install osmnx")
        return 1
    
    # Test basic functionality
    success = test_basic_functionality(ox)
    if not success:
        return 1
    
    # Test coordinate system
    success = test_coordinate_system()
    if not success:
        return 1
    
    print("\n" + "=" * 40)
    print("?? All OSMnx tests passed!")
    print("OSMnx is ready for ARIA v4.1 analysis.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
