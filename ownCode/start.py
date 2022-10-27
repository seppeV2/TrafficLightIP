import networkx as nx
import numpy as np

from dyntapy import show_network, add_centroids, relabel_graph, show_demand, \
    add_connectors
from pytest import mark
from dyntapy.demand_data import od_graph_from_matrix
from dyntapy.supply_data import _set_toy_network_attributes, build_network
from dyntapy.settings import parameters
from dyntapy.demand import build_internal_static_demand, \
    build_internal_dynamic_demand, DynamicDemand, SimulationTime
from osmnx.distance import euclidean_dist_vec


def makeOwnToyNetwork():
    g = nx.DiGraph()
    ebunch_of_nodes = [
        (1, {"x_coord": 10, "y_coord": 35}),
        (2, {"x_coord": 25, "y_coord": 35}),
        (3, {"x_coord": 35, "y_coord": 50}),
        (4, {"x_coord": 35, "y_coord": 20}),
        (5, {"x_coord": 55 , "y_coord": 50}),
        (6, {"x_coord": 55, "y_coord": 20}),
        (7, {"x_coord": 65 , "y_coord": 35}),
        (8, {"x_coord": 80 , "y_coord": 35}),
        (9, {"x_coord": 75 , "y_coord": 0}),
        (10, {"x_coord": 15 , "y_coord": 0}),

    ]

    g.add_nodes_from(ebunch_of_nodes)
    ebunch_of_edges = [
        (1, 2),
        (2, 3),
        (2, 4),
        (3, 5),
        (4, 6),
        (5, 7),
        (6, 7),
        (7, 8),
        (8, 9),
        (9, 10),
        (10, 1),
    ]

    bottle_neck_edges = [
        (1, 2, 1200, 80),
        (2, 3, 400, 80),
        (2, 4, 800, 80),
        (3, 5, 400, 80),
        (4, 6, 800, 80),
        (5, 7, 400, 80),
        (6, 7, 800, 80),
        (7, 8, 1200, 80),
        (8, 9, 1500, 80),
        (9, 10, 1500, 80),
        (10, 1, 1500, 80),
    ]
    g.add_edges_from(ebunch_of_edges)
    set_network_attributes(g, bottle_neck_edges)

    #centroid_x = np.array([10])
    #centroid_y = np.array([10])
    #g = add_centroids(g, centroid_x, centroid_y, k=1, method='turn', euclidean=True)
    # also adds connectors automatically
    g = relabel_graph(g)  # adding link and node ids, connectors and centroids
    # are the first elements
    show_network(g, euclidean=True)
    return g

def set_network_attributes(g, bottleneck_edges):
    #default like this
    capacity = 2000
    free_speed = 80
    lanes = 1
    node_ctrl_type = "none"
    for v in g.nodes:
        g.nodes[v]["ctrl_type"] = node_ctrl_type
    for u, v, data in g.edges.data():
        y1 = g.nodes[v]["y_coord"]
        x1 = g.nodes[v]["x_coord"]
        y0 = g.nodes[u]["y_coord"]
        x0 = g.nodes[u]["x_coord"]
        data["length"] = euclidean_dist_vec(y0, x0, y1, x1)
        data["capacity"] = capacity
        data["free_speed"] = free_speed
        data["lanes"] = lanes
        if (u, v,) in bottleneck_edges:
            print('gank')
            # data["capacity"] = w
            # data["free_speed"] = z

g = makeOwnToyNetwork()
