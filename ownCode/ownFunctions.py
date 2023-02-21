import numpy as np

from dyntapy import relabel_graph, show_network
from dyntapy.demand_data import od_graph_from_matrix
from osmnx.distance import euclidean_dist_vec

global_signalized_nodes = []
global_signalized_links = []
signal_node_link_connect = {}

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
            try:
                data["capacity"] = new_cap_speed[index][0]
                data["free_speed"] = new_cap_speed[index][1]
            except IndexError:
                data["capacity"] = capacity
                data["free_speed"] = free_speed
    
        
# method to set the certain nodes as signalized in a network
# !!IMPORTANT!! the node id is the id AFTER relabeling 
# if it is needed to work with the original ids use the return_inverse dictionary
# gained by the extra output of the relabeling function     
# input = g and a list of the nodes that are signalized
def set_signalized_nodes_and_links(g, signalized_nodes = list):
    signalized_edges = []
    signalized_links = []
    global global_signalized_nodes, global_signalized_links, signal_node_link_connect
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
            try:
                signal_node_link_connect[v].append(data['link_id'])
            except KeyError:
                signal_node_link_connect[v] = [data['link_id']]
        else:
            data['signalized'] = 0
    global_signalized_links = signalized_links
    g.update(edges = g.edges, nodes = g.nodes)
    return g

# generate the first greens for all links (equal distribution when signalized, 1 when not) 
# also return the list of non connector links (their link id)
def generateFirstGreen(g):
    first_greens = {}
    non_connectors = []

    for _,v,data in g.edges.data():
        # store the non connector links (just for visualization)
        try:
            data['connector']
        except KeyError:
            non_connectors.append(data['link_id'])

        if v in signal_node_link_connect.keys():
            first_greens[data['link_id']] = 1/len(signal_node_link_connect[v])
        else:
            first_greens[data['link_id']] = 1
    return first_greens, non_connectors



#function to load the OD matrix in from .cvs file to numpy array 
def getODGraph(ODMatrix, ODcentroids):
    xOD = ODcentroids[0]
    yOD = ODcentroids[1]
    matrix = np.genfromtxt(ODMatrix, delimiter=',')
    return od_graph_from_matrix(matrix, X=xOD, Y=yOD)

# Not necessary anymore as the results are global variables but it is used in the code
# so for the moment it is kept
def getIntersections(tot_links: int):
    link_signal = {}
    for link_id in range(tot_links):
        if link_id in global_signalized_links:
            link_signal[link_id] = 1
        else:
            link_signal[link_id] = 0
    return global_signalized_nodes, global_signalized_links, link_signal

