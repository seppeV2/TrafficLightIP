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
from aidFunctions import getNodeSummary



#main function where we merge everything together
def main():
    g, ODcentroids = makeOwnToyNetwork()
    ODMatrix = str(pathlib.Path(__file__).parent)+'/data/ODmatrix.csv'
    odGraph = getODGraph(ODMatrix, ODcentroids)
    assignment = StaticAssignment(g, odGraph)
    result = assignment.run('msa')
    show_network(g,flows = result.flows, euclidean = True)
    network = build_network(g)
    getNodeSummary(network)
    costs, flows, gap_definition, gap = msa_flow_averaging(network, build_internal_static_demand(odGraph), False)

main()