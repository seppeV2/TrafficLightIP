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


from ownFunctions import makeOwnToyNetwork, getODGraph, getIntersections, get_green_times
from greenTimes import websterGreenTimes
from aidFunctions import getNodeSummary
from dyntapy_green_time_change import GreenStaticAssignment



#main function where we merge everything together
def main():
    #setup
    print("STARTING SETUP")
    g, ODcentroids = makeOwnToyNetwork()
    ODMatrix = str(pathlib.Path(__file__).parent)+'/data/ODmatrix.csv'
    odGraph = getODGraph(ODMatrix, ODcentroids)
    assignment = GreenStaticAssignment(g, odGraph)

    print("RUNNING FIRST STATIC ASSIGNMENT WITHOUT TRAFFIC LIGHTS")
    #initial msa without traffic lights
    result = assignment.run('msa')
    #calculate the first green times according the first static assignment
    print('flows: '+str(result.flows))
    greens = get_green_times(assignment.internal_network.links.capacity,result.flows,assignment.internal_network)
    print('greens: '+ str(greens))
    show_network(g, flows = result.flows, euclidean=True)
    #start the loop
    print('START THE LOOP')
        #initialise parameters and variables
    delta = 0.001
    maxLoops = 100
    safety = 0
    gap = 1
    while gap > delta and safety < maxLoops:
        safety += 1
        print('loop = '+str(safety))
        newResult = assignment.run_greens('msa', greens)
        newGreens = get_green_times(assignment.internal_network.links.capacity, newResult.flows, assignment.internal_network)
        print('flows: '+str(newResult.flows))
        print('greens: '+ str(newGreens))
        #calculating the gap 
        gap = sum([abs(gi - gj) for gi, gj in zip(result.flows, newResult.flows)])
        print('Gap = '+ str(gap))
        result = newResult
        greens = newGreens

    show_network(g, flows = result.flows, euclidean=True)



main()