import osmnx as ox

# Extract a sample network for Hualien
try:
    print('Extracting Hualien road network...')
    G = ox.graph_from_address('Hualien City, Taiwan', dist=3000, network_type='drive')
    G_proj = ox.project_graph(G, to_crs='EPSG:3826')
    
    # Save as GraphML
    ox.save_graphml(G_proj, 'hualien_network.graphml')
    
    print(f'Success! Network saved: {G_proj.number_of_nodes()} nodes, {G_proj.number_of_edges()} edges')
    print(f'CRS: {G_proj.graph["crs"]}')
    
except Exception as e:
    print(f'Extraction failed: {e}')
    print('Using NTU fallback...')
    G = ox.graph_from_address('National Taiwan University, Taipei', dist=2000, network_type='drive')
    G_proj = ox.project_graph(G, to_crs='EPSG:3826')
    ox.save_graphml(G_proj, 'hualien_network.graphml')
    print(f'Fallback network saved: {G_proj.number_of_nodes()} nodes, {G_proj.number_of_edges()} edges')
