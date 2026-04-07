#!/usr/bin/env python3
"""
ARIA v4.1 - NetworkX Testing Script
Tests NetworkX functionality for graph analysis
"""

import sys
import traceback

def test_networkx_import():
    """Test NetworkX import"""
    try:
        import networkx as nx
        print("?? NetworkX import successful")
        return True, nx
    except ImportError as e:
        print(f"?? NetworkX import failed: {e}")
        return False, None

def test_basic_graph_operations(nx):
    """Test basic NetworkX operations"""
    try:
        print("?? Testing basic graph operations...")
        
        # Create test graph
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (2, 4)])
        print(f"   Created graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
        
        # Test basic properties
        print(f"   Graph is connected: {nx.is_connected(G)}")
        print(f"   Graph density: {nx.density(G):.3f}")
        
        return True
        
    except Exception as e:
        print(f"?? Basic operations test failed: {e}")
        return False

def test_centrality_measures(nx):
    """Test centrality measures"""
    try:
        print("?? Testing centrality measures...")
        
        # Create test graph
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (2, 4), (4, 5), (5, 6)])
        
        # Betweenness centrality
        betweenness = nx.betweenness_centrality(G)
        print(f"   Betweenness centrality calculated for {len(betweenness)} nodes")
        
        # Closeness centrality
        closeness = nx.closeness_centrality(G)
        print(f"   Closeness centrality calculated for {len(closeness)} nodes")
        
        # Degree centrality
        degree = nx.degree_centrality(G)
        print(f"   Degree centrality calculated for {len(degree)} nodes")
        
        # Find bottleneck (highest betweenness)
        bottleneck = max(betweenness, key=betweenness.get)
        print(f"   Top bottleneck node: {bottleneck} (betweenness: {betweenness[bottleneck]:.3f})")
        
        return True
        
    except Exception as e:
        print(f"?? Centrality measures test failed: {e}")
        return False

def test_path_analysis(nx):
    """Test path analysis"""
    try:
        print("?? Testing path analysis...")
        
        # Create test graph
        G = nx.Graph()
        G.add_edges_from([(1, 2, {'weight': 1.0}), (2, 3, {'weight': 2.0}), 
                         (3, 4, {'weight': 1.5}), (1, 4, {'weight': 3.0})])
        
        # Shortest path
        path = nx.shortest_path(G, 1, 4, weight='weight')
        print(f"   Shortest path 1->4: {path}")
        
        # Shortest path length
        length = nx.shortest_path_length(G, 1, 4, weight='weight')
        print(f"   Shortest path length: {length}")
        
        # All pairs shortest paths
        paths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))
        print(f"   All-pairs shortest paths calculated for {len(paths)} nodes")
        
        return True
        
    except Exception as e:
        print(f"?? Path analysis test failed: {e}")
        return False

def test_graph_algorithms(nx):
    """Test advanced graph algorithms"""
    try:
        print("?? Testing advanced algorithms...")
        
        # Create test graph
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1)])
        
        # Test connected components
        components = list(nx.connected_components(G))
        print(f"   Connected components: {len(components)}")
        
        # Test clustering
        clustering = nx.clustering(G)
        print(f"   Clustering coefficient calculated for {len(clustering)} nodes")
        
        # Test diameter
        if nx.is_connected(G):
            diameter = nx.diameter(G)
            print(f"   Graph diameter: {diameter}")
        
        return True
        
    except Exception as e:
        print(f"?? Advanced algorithms test failed: {e}")
        return False

def main():
    """Main test function"""
    print("ARIA v4.1 - NetworkX Testing")
    print("=" * 40)
    
    # Test import
    success, nx = test_networkx_import()
    if not success:
        print("Install NetworkX with: pip install networkx")
        return 1
    
    # Run tests
    tests = [
        test_basic_graph_operations,
        test_centrality_measures,
        test_path_analysis,
        test_graph_algorithms
    ]
    
    for test in tests:
        success = test(nx)
        if not success:
            return 1
    
    print("\n" + "=" * 40)
    print("?? All NetworkX tests passed!")
    print("NetworkX is ready for ARIA v4.1 analysis.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
