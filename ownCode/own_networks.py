import numpy as np
import networkx as nx
from ownFunctions import set_network_attributes
from dyntapy import relabel_graph
from dyntapy.demand_data import add_centroids


#building our own two rout DiGraph route (using nodes)
def makeOwnToyNetwork(form: str):
    if form == 'complex':
        g = nx.DiGraph()
        ebunch_of_nodes = [
            (1, {"x_coord": 10, "y_coord": 35}),
            (2, {"x_coord": 25, "y_coord": 35}),
            (3, {"x_coord": 35, "y_coord": 50}),#
            (4, {"x_coord": 35, "y_coord": 20}),
            (5, {"x_coord": 55 , "y_coord": 50}),#
            (6, {"x_coord": 55, "y_coord": 20}),
            (7, {"x_coord": 65 , "y_coord": 35}),
            (8, {"x_coord": 80 , "y_coord": 35}),
            (9, {"x_coord": 90 , "y_coord": 35}),
            (11, {"x_coord": 30 , "y_coord": 15}),
            (12, {"x_coord": 60 , "y_coord": 40}),#
            (13, {"x_coord": 75 , "y_coord": 45}),
            (14, {"x_coord": 50 , "y_coord": 35}),
        ]
        g.add_nodes_from(ebunch_of_nodes)
        ebunch_of_edges = [
            (1, 2),
            (2, 3),
            (2, 4),
            (3, 5),
            (4, 6),
            (6, 7),
            (7, 8),
            (11, 4),
            (5, 12),
            (12, 7),
            (12,13),
            (13,8),
            (8,9),
            (14,7)
        ]
        bottle_neck_capacity_speed =   [
            (1200, 80),
            (100, 80),
            (150, 80),
            (100, 80),
            (200, 80),
            (200, 80),
            (300, 80),
            (1200, 80),
            (100, 80),
            (100, 80),
            (100, 80),
            (100, 80),
            (1200, 80),
            (100,80)
        ]
        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, ebunch_of_edges, bottle_neck_capacity_speed)
        return g 
    elif form == 'merge':
        g = nx.DiGraph()
        ebunch_of_nodes = [
            (0, {"x_coord": 0, "y_coord": 30}),
            (1, {"x_coord": 30, "y_coord": 30}),
            (2, {"x_coord": 15, "y_coord": 15}),
            (3, {"x_coord": 35, "y_coord": 30}),
            (4, {"x_coord": 0, "y_coord": 0}),   
        ]
        g.add_nodes_from(ebunch_of_nodes)

        ebunch_of_edges = [
            (0, 1),
            (0, 2),
            (2, 1),
            (1, 3),
            (4, 2),
        ]
        edge_capacity_speed =   [
            (100, 80),
            (150, 80),
            (150, 80),
            (250, 80),
            (150, 80),
        ]
        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, ebunch_of_edges, edge_capacity_speed)
        return g
    elif form == 'two-node':
        g = nx.DiGraph()
        ebunch_of_nodes = [
            (0, {"x_coord": 0, "y_coord": 30}),
            (1, {"x_coord": 30, "y_coord": 30}),
            (2, {"x_coord": 15, "y_coord": 15}),
            (3, {"x_coord": 60, "y_coord": 30}),
            (4, {"x_coord": 45, "y_coord": 15}),
            (5, {"x_coord": 65, "y_coord": 30}),

        ]
        g.add_nodes_from(ebunch_of_nodes)
        ebunch_of_edges = [
            (0, 1),
            (0, 2),
            (2, 1),
            (1, 3),
            (1, 4),
            (4, 3),
            (3, 5),
        ]
        edge_capacity_speed =   [
            (100, 80),
            (150, 80),
            (150, 80),
            (150, 80),
            (100, 80),
            (100, 80),
            (250, 80),

        ]
        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, ebunch_of_edges, edge_capacity_speed)
        return g
    elif form == 'simple':
        g = nx.DiGraph()
        ebunch_of_nodes = [
            (0, {"x_coord": 0, "y_coord": 30}),
            (1, {"x_coord": 30, "y_coord": 30}),
            (2, {"x_coord": 15, "y_coord": 15}),
            (3, {"x_coord": 35, "y_coord": 30}),
        ]
        g.add_nodes_from(ebunch_of_nodes)
        ebunch_of_edges = [
            (0, 1),
            (0, 2),
            (2, 1),
            (1, 3),
        ]
        edge_capacity_speed =   [
            (100, 80),
            (150, 80),
            (150, 80),
            (250, 80),
        ]
        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, ebunch_of_edges, edge_capacity_speed)
        return g
