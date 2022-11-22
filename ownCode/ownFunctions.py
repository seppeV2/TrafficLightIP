import networkx as nx
import numpy as np

from dyntapy import relabel_graph
from dyntapy.demand_data import od_graph_from_matrix
from osmnx.distance import euclidean_dist_vec

#building our own two rout DiGraph route (using nodes)
def makeOwnToyNetwork(form):
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
            (9, {"x_coord": 75 , "y_coord": 0}),
            (10, {"x_coord": 15 , "y_coord": 0}),
            (11, {"x_coord": 30 , "y_coord": 15}),
            (12, {"x_coord": 60 , "y_coord": 40}),#
            (13, {"x_coord": 75 , "y_coord": 45}),
        
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
            (8, 9),
            (9, 10),
            (10, 1),
            (11, 4),
            (4, 11),
            (5, 12),
            (12, 7),
            (12,13),
            (13,8),
        ]

        bottle_neck_edges = [
            (1, 2),
            (2, 3),
            (2, 4),
            (3, 5),
            (4, 6),
            (6, 7),
            (7, 8),
            (8, 9),
            (9, 10),
            (10, 1),
            (5,12),
            (12,7),
            (12,13),
            (13,8),
        ]

        bottle_neck_capacity_speed =   [
            (1200, 80),
            (400, 80),
            ( 800, 80),
            ( 400, 80),
            ( 800, 80),
            ( 800, 80),
            ( 1200, 80),
            ( 1500, 80),
            ( 1500, 80),
            ( 1500, 80),
            ( 300, 80),
            ( 200, 80),
            (300,80),
            (300,80),
        ]
        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, bottle_neck_edges, bottle_neck_capacity_speed)

    
        ODcentroids = np.array([np.array([10,25,35,35,55,55,65,80,75,15,30,60,75]), np.array([35,35,50,20,50,20,35,35,0,0,15,40,45])])
        g = relabel_graph(g)  # adding link and node ids, connectors and centroids
        odCsvFile = 'ODmatrixComplex.csv'
        return g, ODcentroids, odCsvFile
    elif form == 'simple':
        g = nx.DiGraph()
        ebunch_of_nodes = [
            (0, {"x_coord": 0, "y_coord": 30}),
            (1, {"x_coord": 30, "y_coord": 30}),
            (2, {"x_coord": 15, "y_coord": 15}),
            (3, {"x_coord": 35, "y_coord": 30}),
            
        ]

        nodes_signalized = [
            0,
            1,
            0,
            0,
        ]

        is_origin  = [
            1,
            0,
            0,
            0,
        ]
        g.add_nodes_from(ebunch_of_nodes)

        ebunch_of_edges = [
            (0, 1),
            (0, 2),
            (2, 1),
            (1, 3),
            
        ]

        bottle_neck_edges = [
            (0, 1),
            (0, 2),
            (2, 1),
            (1, 3),
            
        ]

        bottle_neck_capacity_speed =   [
            (100, 80),
            (150, 10000),
            (150, 80),
            (250, 80),
            
        ]

        is_signalized = [
            1,
            0,
            1,
            0,
        ]

        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, bottle_neck_edges, bottle_neck_capacity_speed, is_signalized, nodes_signalized, is_origin)

        ODcentroids = np.array([np.array([0,30,20,35]), np.array([30,30,15,30])])
        g = relabel_graph(g)  # adding link and node ids, connectors and centroids
        odCsvFile = 'ODmatrixSimple.csv'
        return g, ODcentroids, odCsvFile

#modified dyntapy function to change the capacity and the speed of each link
def set_network_attributes(g, bottleneck_edges, bottle_neck_capacity_speed, is_signalized = [], nodes_signalized=[], is_origin = []):
    #check links singalized or not
    if is_signalized == []:
        is_signalized = np.zeros(len(bottleneck_edges))

    #check nodes singalized or not
    if nodes_signalized == []:
        nodes_signalized = np.zeros(len(g.nodes))
        
    if is_origin == []:
        is_origin = np.zeros(len(g.nodes))

    #default like this
    capacity = 2000
    free_speed = 80
    lanes = 1
    node_ctrl_type = "none"
    count = 0
    for v in g.nodes:
        g.nodes[v]["ctrl_type"] = node_ctrl_type
        g.nodes[v]["signalized_node"] = nodes_signalized[count]
        g.nodes[v]["is_origin"] = is_origin[count]
        count += 1 
    for u, v, data in g.edges.data():
        y1 = g.nodes[v]["y_coord"]
        x1 = g.nodes[v]["x_coord"]
        y0 = g.nodes[u]["y_coord"]
        x0 = g.nodes[u]["x_coord"]
        data["length"] = euclidean_dist_vec(y0, x0, y1, x1)
        data["capacity"] = capacity
        data["free_speed"] = free_speed
        data["lanes"] = lanes
        if (u, v,) in (bottleneck_edges):
            index = bottleneck_edges.index((u,v))
            data["capacity"] = bottle_neck_capacity_speed[index][0]
            data["free_speed"] = bottle_neck_capacity_speed[index][1]
            data["signalized"] = is_signalized[index]
        

#function to load the OD matrix in from .cvs file to numpy array 
def getODGraph(ODMatrix, ODcentroids):
    xOD = ODcentroids[0]
    yOD = ODcentroids[1]
    matrix = np.genfromtxt(ODMatrix, delimiter=',')
    return od_graph_from_matrix(matrix, X=xOD, Y=yOD)

#function to find which nodes are intersection nodes so the links before these nodes have a different cost
#function (including the green times)
def getIntersections(g):
    intersecting_links = []
    intersections = []
    links = {}
    
    for n in g.nodes:
        if g.nodes[n]["signalized_node"] == 1:
            intersections.append(g.nodes[n]["node_id"])

    for u,v,data in g.edges.data():
        if data["signalized"] == 1:
            intersecting_links.append(data["link_id"])
        links[data["link_id"]] = data["signalized"]
    return intersections, intersecting_links, links



                
    
