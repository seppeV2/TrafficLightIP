from dyntapy.supply_data import road_network_from_place
from dyntapy.demand_data import auto_configured_centroids, generate_od_xy, add_centroids, parse_demand
from dyntapy.visualization import show_network
from dyntapy import relabel_graph
from dyntapy.assignments import StaticAssignment
from cost_msa_dyntapy import StaticAssignmentIncludingGreen
import numpy as np

def make_osm_network(place: str, distance_outer: int, distance_inner:int):

    g = road_network_from_place(place, buffer_dist_close= distance_inner, buffer_dist_extended=distance_outer)
    X,Y, names, places = auto_configured_centroids(place, buffer_dist_close = distance_inner, buffer_dist_extended=distance_outer)
    res = generate_od_xy(100,place,1000)
    
    auto_centroid = {'X':[], 'Y':[],'name':[], 'place':[]}
    for x,y,_place,_name in zip(X, Y, places, names):
        if _place != '-':
            auto_centroid['X'].append(x)
            auto_centroid['Y'].append(y)
    g = add_centroids(g, np.array(auto_centroid['X']),np.array(auto_centroid['Y']),k = 3, method = 'link')
    
    #g = add_centroids(g, X, Y, k=2, method = 'link')
    g = relabel_graph(g)
    od_graph = parse_demand(res, g)
    

    #assignment = StaticAssignment(g, od_graph)
    #result = assignment.run('msa')
    #show_network(g, flows = result.flows)

    return g, od_graph
make_osm_network('Veurne', 0,5000)