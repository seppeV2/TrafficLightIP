import networkx as nx
import numpy as np
import pathlib
import dyntapy

from dyntapy import show_network, add_centroids, relabel_graph, show_demand, \
    add_connectors
from pytest import mark
from dyntapy.assignments import StaticAssignment
from dyntapy.demand_data import od_graph_from_matrix
from dyntapy.supply_data import _set_toy_network_attributes, build_network
from dyntapy.settings import parameters
from dyntapy.demand import build_internal_static_demand, \
    build_internal_dynamic_demand, DynamicDemand, SimulationTime
from osmnx.distance import euclidean_dist_vec
from dyntapy.sta.utilities import aon, __bpr_cost_single

from greenTimes import websterGreenTimes
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
            (1, {"x_coord": 5, "y_coord": 30}),
            (2, {"x_coord": 20, "y_coord": 15}),
            (3, {"x_coord": 35, "y_coord": 30}),
            (4, {"x_coord": 50, "y_coord": 30}),
            (5, {"x_coord": 20, "y_coord": 45}),
        ]
        g.add_nodes_from(ebunch_of_nodes)

        ebunch_of_edges = [
            (0, 1),
            (1, 5),
            (5, 3),
            (3, 4),
            (1, 2),
            (2, 3),
        ]

        bottle_neck_edges = [
            (0, 1),
            (1, 5),
            (5, 3),
            (3, 4),
            (1, 2),
            (2, 3),
        ]

        bottle_neck_capacity_speed =   [
            (600, 80),
            (150, 80),
            (150, 80),
            (600, 80),
            (100, 80),
            (100, 80),
        ]

        g.add_edges_from(ebunch_of_edges)
        set_network_attributes(g, bottle_neck_edges, bottle_neck_capacity_speed)

        ODcentroids = np.array([np.array([0,5,20,35,50,20]), np.array([30,30,15,30,30,45])])
        g = relabel_graph(g)  # adding link and node ids, connectors and centroids
        odCsvFile = 'ODmatrixSimple.csv'
        return g, ODcentroids, odCsvFile



#modified dyntapy function to change the capacity and the speed of each link
def set_network_attributes(g, bottleneck_edges, bottle_neck_capacity_speed):
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
            index = bottleneck_edges.index((u,v))
            data["capacity"] = bottle_neck_capacity_speed[index][0]
            data["free_speed"] = bottle_neck_capacity_speed[index][1]

#function to load the OD matrix in from .cvs file to numpy array 
def getODGraph(ODMatrix, ODcentroids):
    xOD = ODcentroids[0]
    yOD = ODcentroids[1]
    matrix = np.genfromtxt(ODMatrix, delimiter=',')
    return od_graph_from_matrix(matrix, X=xOD, Y=yOD)

bpr_b = parameters.static_assignment.bpr_beta
bpr_a = parameters.static_assignment.bpr_alpha

def __bpr_green_cost(flows, capacities, ff_tts, g_times):
    number_of_links = len(flows)
    costs = np.empty(number_of_links, dtype=np.float64)
    for it, (f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        costs[it] = __bpr_green_cost_single(f, c, ff_tt,g_time)
    return costs

#building our own bpr funtion 
def __bpr_green_cost_single(flow, capacity, ff_tt, g_time):
    #enlarged the cost for green time to see significant difference 
    #print('bpr normal cost :\t'+str(__bpr_cost_single(flow, capacity, ff_tt)))
    cost = 1.0 * ff_tt + np.multiply(bpr_a, pow((flow / (capacity * g_time )), bpr_b)) * ff_tt
    #print('bpr green time cost:\t'+str(cost)+'\n')
    return cost

#function to find which nodes are intersection nodes so the links before these nodes have a different cost
#function (including the green times)
def getIntersections(network):
    arrivingLinks = {}
    intersections = []
    for i in range(len(network.links.length)):
        if str(network.links.to_node[i]) not in arrivingLinks.keys():
            arrivingLinks[str(network.links.to_node[i])] = 1
        else:
            arrivingLinks[str(network.links.to_node[i])] +=1
            if network.links.to_node[i] not in intersections:
                intersections.append(network.links.to_node[i])
    return intersections


def get_green_times(caps, flows, network):
    #first use a dictionary so we can order the costs to the right links after 
    intersections = getIntersections(network)
    greenDic = {}
    for i in range(len(caps)):
        if network.links.to_node[i] not in intersections:
            if i not in greenDic.keys():
                greenDic[i]= 1
        else:
            #first store all the data in an array of arrays per link
            intersectionLinksFlows = []
            intersectionCaps = []
            intersectionLinkIDs = []
            for j in range(i,len(caps)):
                if network.links.to_node[j] == network.links.to_node[i]:
                    intersectionLinksFlows.append(flows[j])
                    intersectionCaps.append(caps[j])
                    intersectionLinkIDs.append(j)
            intersections.remove(network.links.to_node[i])
            greenTimes = websterGreenTimes(intersectionCaps, intersectionLinksFlows)
            for j in range(len(greenTimes)):
                greenDic[intersectionLinkIDs[j]] = greenTimes[j]
    return dict(sorted(greenDic.items()))
                
    
