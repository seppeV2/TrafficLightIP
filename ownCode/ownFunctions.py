import networkx as nx
import numpy as np

from dyntapy import relabel_graph
from dyntapy.demand_data import od_graph_from_matrix, add_centroids
from osmnx.distance import euclidean_dist_vec

global_signalized_nodes = []
global_signalized_links = []
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
        bottle_neck_capacity_speed =   [
            (1200, 80),
            (400, 80),
            (800, 80),
            (400, 80),
            (800, 80),
            (800, 80),
            (1200, 80),
            (1500, 80),
            (1500, 80),
            (1500, 80),
            (300, 80),
            (200, 80),
            (300, 80),
            (300, 80),
        ]
        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, ebunch_of_edges, bottle_neck_capacity_speed)

        ODcentroids = np.array([np.array([10,30,80]), np.array([35,15,35])])
        g = add_centroids(g, ODcentroids[0], ODcentroids[1], euclidean = True, method = 'link')
        g = relabel_graph(g)  # adding link and node ids, connectors and centroids
        odCsvFile = 'ODmatrixComplex.csv'
        return g, ODcentroids, odCsvFile
    
    elif form == 'merge_two_route':
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

        ODcentroids = np.array([np.array([0,0,35]), np.array([30,0,30])])
        g = add_centroids(g, ODcentroids[0], ODcentroids[1], euclidean=True, method='link')
        g = relabel_graph(g)  # adding link and node ids
        odCsvFile = 'ODmatrixMerge.csv'
        return g, ODcentroids, odCsvFile
    
    elif form == 'simple':
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

        ODcentroids = np.array([np.array([0,30,20,35,0]), np.array([30,30,15,30,0])])
        g = relabel_graph(g)  # adding link and node ids, connectors and centroids
        odCsvFile = 'ODmatrixSimple.csv'
        return g, ODcentroids, odCsvFile

#modified dyntapy function to change the capacity and the speed of each link (this is easy for us to change the network)
def set_network_attributes(g, non_default_link, new_cap_speed):

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
        if (u, v,) in (non_default_link):
            index = non_default_link.index((u,v))
            data["capacity"] = new_cap_speed[index][0]
            data["free_speed"] = new_cap_speed[index][1]
    
        
# method to set the certain nodes as signalized in a network
# !!IMPORTANT!! the node id is the id AFTER relabeling 
# if it is needed to work with the original ids use the return_inverse dictionary
# gained by the extra output of the relabeling function     
# input = g and a list of the nodes that are signalized
def set_signalized_nodes_and_links(g, signalized_nodes = list):
    signalized_edges = []
    signalized_links = []
    global global_signalized_nodes, global_signalized_links
    global_signalized_nodes = signalized_nodes

    for v in g.nodes:
        if g.nodes[v]['node_id'] in signalized_nodes:
            g.nodes[v]['signalized_node'] = 1
            # the connection between the signalized node and his predecessors is a signalized link
            for u in g.pred[g.nodes[v]['node_id']]:
                signalized_edges.append((u,v))
        else:
            g.nodes[v]['signalized_node'] = 0

    for u,v, data in g.edges.data():
        if (u,v) in signalized_edges:
            data['signalized'] = 1
            signalized_links.append(data['link_id'])
        else:
            data['signalized'] = 0
    global_signalized_links = signalized_links
    g.update(edges = g.edges, nodes = g.nodes)
    return g

# generate the first greens for all non connector links 
# also return the list of non connector links (their link id)
def generateFirstGreen(g):
    first_greens = {}
    non_connectors = []

    for _,_,data in g.edges.data():
        #only store the greens of the none connecting links
        try:
            data['connector']
        except KeyError:
            
            non_connectors.append(data['link_id'])
        first_greens[data['link_id']] = 1 if data['signalized'] == 0 else 0.5
    return first_greens, non_connectors



#function to load the OD matrix in from .cvs file to numpy array 
def getODGraph(ODMatrix, ODcentroids):
    xOD = ODcentroids[0]
    yOD = ODcentroids[1]
    matrix = np.genfromtxt(ODMatrix, delimiter=',')
    g = od_graph_from_matrix(matrix, X=xOD, Y=yOD)
    return g

#function to find which nodes are intersection nodes so the links before these nodes have a different cost
#function (including the green times)
def getIntersections(tot_links: int):
    link_signal = {}
    for link_id in range(tot_links):
        if link_id in global_signalized_links:
            link_signal[link_id] = 1
        else:
            link_signal[link_id] = 0
    return global_signalized_nodes, global_signalized_links, link_signal

