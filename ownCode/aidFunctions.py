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
from dyntapy.results import StaticResult, get_skim, DynamicResult
from dyntapy.sta.msa import msa_flow_averaging

from dyntapy.demand import (
    InternalDynamicDemand,
    build_internal_static_demand,
    build_internal_dynamic_demand,
)


from ownFunctions import makeOwnToyNetwork, getODGraph
from greenTimes import websterGreenTimes

def getNodeSummary(network):
    xcoord = network.nodes.x_coord
    ycoord = network.nodes.y_coord
    tot_out_links = network.nodes.tot_out_links
    for i in range(len(xcoord)):
        if network.nodes.is_centroid[i]:
            extra = ' is Centroid'
        else:
            extra = ""
        print('x coord '+str(xcoord[i])+' y coord '+str(ycoord[i])+' outgoing links '+str(tot_out_links[i])+extra)