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


def makeOwnToyNetwork():
    g = nx.DiGraph()
    ebunch_of_nodes = [
        (1, {"x_coord": 10, "y_coord": 20}),
        (2, {"x_coord": 10, "y_coord": 10}),
        (3, {"x_coord": 10, "y_coord": 0}),
        (4, {"x_coord": 0, "y_coord": 10}),
        (5, {"x_coord": 20 , "y_coord": 10}),
    ]

    g.add_nodes_from(ebunch_of_nodes)
    ebunch_of_edges = [
        (1, 2),
        (2, 1),
        (4, 2),
        (2, 4),
        (1, 3),
        (3, 1),
        (4, 5),
        (5, 4),
    ]

    bottle_neck_edges = [(2, 4), (4, 2)]
    g.add_edges_from(ebunch_of_edges)
    _set_toy_network_attributes(g, bottle_neck_edges)

    centroid_x = np.array([10])
    centroid_y = np.array([10])
    g = add_centroids(g, centroid_x, centroid_y, k=1, method='turn', euclidean=True)
    # also adds connectors automatically
    g = relabel_graph(g)  # adding link and node ids, connectors and centroids
    # are the first elements
    show_network(g, euclidean=True)
    return g

g = makeOwnToyNetwork()





