import numpy as np

from dyntapy import relabel_graph, show_network
from dyntapy.demand_data import od_graph_from_matrix
from osmnx.distance import euclidean_dist_vec
from dyntapy.demand_data import add_centroids

global_signalized_nodes = []
global_signalized_links = []
signal_node_link_connect = {}

# This function sets the centroids to the coordinates and connects them to the closest node
def addCentroidODNodes(g, O_or_D_nodes):
    centroid_x = np.array([x for (x,_) in O_or_D_nodes])
    centroid_y = np.array([y for (_,y) in O_or_D_nodes])
    g = add_centroids(g, X = centroid_x, Y = centroid_y, method = 'link', euclidean = True)
    g = relabel_graph(g)  # adding link and node ids, connectors and centroids
    return g
            


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
    signal_node_link_connect = {}

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

    global global_signalized_nodes, global_signalized_links
    global_signalized_nodes = signalized_nodes
    global_signalized_links = signalized_links

    g.update(edges = g.edges, nodes = g.nodes)
    return g, signal_node_link_connect

# generate the first greens for all links (equal distribution when signalized, 1 when not) 
# also return the list of non connector links (their link id)
# An optional parameter 'distribution' is included for test purposes (to check if the starting greens have an impact)
def generateFirstGreen(g,signal_node_link_connect ,distribution: str = 'equal'):
    first_greens = {}
    non_connectors = []
    print(f'distribution = {distribution}')
    for _,v,data in g.edges.data():
        # store the non connector links (just for visualization)
        try:
            data['connector']
        except KeyError:
            non_connectors.append(data['link_id'])

        if v in signal_node_link_connect.keys():
            # When more than two links are merging in an intersection, the option
            # of equal split is always chosen 
            if distribution == 'equal' or len(signal_node_link_connect[v]) > 2:
                first_greens[data['link_id']] = 1/len(signal_node_link_connect[v])
            else:
                if distribution == '40-60':
                    dis = [0.40,0.60]
                elif distribution == '20-80':
                    dis = [0.20,0.80]
                elif distribution == '60-40':
                    dis = [0.60,0.40]
                elif distribution == '80-20':
                    dis = [0.80,0.20]
                else:
                    # when a wrong statement is given use the equal distribution (to make the code more robust)
                    dis = [0.5,0.5]
                for idx, id in enumerate(signal_node_link_connect[v]):
                        if id == data['link_id']:
                            first_greens[data['link_id']] = dis[idx]
        else:
            first_greens[data['link_id']] = 1
    return first_greens, non_connectors

#function to load the OD matrix in from .cvs file to numpy array 
def getODGraph(OD_flow, O_or_D):
    centroid_x = np.array([x for (x,_) in O_or_D])
    centroid_y = np.array([y for (_,y) in O_or_D])
    
    matrix = np.zeros((len(O_or_D), len(O_or_D)))
    for demand in OD_flow:
        (o, d, flow) = demand
        matrix[o,d] = flow
    return od_graph_from_matrix(matrix, X=centroid_x, Y=centroid_y)

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

