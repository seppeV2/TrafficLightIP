import networkx as nx
import numpy as np
import pathlib
import operator
import dyntapy
import matplotlib.pyplot as plt

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
    g, ODcentroids, odFile = makeOwnToyNetwork('simple')
    ODMatrix = str(pathlib.Path(__file__).parent)+'/data/'+str(odFile)
    odGraph = getODGraph(ODMatrix, ODcentroids)
    assignment = GreenStaticAssignment(g, odGraph)

    print("RUNNING FIRST STATIC ASSIGNMENT WITH TRAFFIC LIGHTS (equal distributed)")

    #starting with 0.5 at every two link node
        #hardCoded for simple
    firstGreen = {0: 0.5, 1: 1, 2: 1, 3: 0.5}
        #hardCoded for complex 
    #firstGreen = {0: 1, 1: 1, 2: 0.5, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0.5, 8: 0.5, 9: 1, 10: 1, 11: 1, 12: 0.5, 13: 0.5, 14: 1, 15: 0.5}


    #initial msa without traffic lights
            #result2 = assignment.run('msa')
    result = assignment.run_greens('msa', firstGreen)
    #calculate the first green times according the first static assignment
    print('flows: '+str(result.flows))
    greens = get_green_times(assignment.internal_network.links.capacity,result.flows,assignment.internal_network)
    print('greens: '+ str(greens))
    culGreensPerIntersection = ()
    #greens2 = {0:(greens[0]),1:(greens[1]),2:(greens[2])}
    greens2 = {}
    for i in greens.keys():
        greens2[i] = (greens[i],)
    greens = get_green_times(assignment.internal_network.links.capacity,result.flows,assignment.internal_network, 'webster')
    print('greensWebster: '+ str(greens))
    greens2 = get_green_times(assignment.internal_network.links.capacity,result.flows,assignment.internal_network, 'P0')
    print('greensP0: '+ str(greens))
    show_network(g, flows = result.flows, euclidean=True)
            #show_network(g, flows = result2.flows, euclidean = True)
    #start the loop
    print('START THE LOOP')
        #initialise parameters and variables
    delta = 0.001
    maxLoops = 1000
    safety = 0
    gap = 1
    flows_gap = []
    greens_gap = []
    while gap > delta and safety < maxLoops:
        safety += 1
        print('loop = '+str(safety))
        newResult = assignment.run_greens('msa', greens)
        newGreens = get_green_times(assignment.internal_network.links.capacity, newResult.flows, assignment.internal_network, 'webster')
        print('flows: '+str(newResult.flows))
        print('greens: '+ str(newGreens))
        #calculating the gap 
        gap = sum([abs(xi - xj) for xi, xj in zip(result.flows, newResult.flows)])
        flows_gap.append(gap)
        print('Gap = '+ str(gap))
        gap_green = sum([abs(gi - gj) for gi, gj in zip(greens, newGreens)])
        greens_gap.append(gap_green)
        result = newResult
        for i in greens.keys():
            greens2[i] += (newGreens[i],)
        greens = newGreens
        if safety ==70:
            show_network(g, flows=result.flows, euclidean=True)

    #to visualize the green times over the links automatically
    for i in greens2.keys():
        x = np.linspace(1,len(greens2[i]),len(greens2[i]))
        y = list(greens2[i])
        plt.plot(x,y,label=str(i))
    plt.title("Green times of different links over the iterations")
    plt.legend()
    plt.show()

    #to plot the green times of the two routes of a simple network
    #don't know if it's correct to sum the green times cuz they are fractions actually
    x = np.linspace(1,len(greens2[0]), len(greens2[0]))
    y1 = tuple(map(sum,zip(greens2[0],greens2[1],greens2[5]),greens2[4]))
    y2 = tuple(map(sum,zip(greens2[0],greens2[2],greens2[3],greens2[5])))
    plt.plot(x,y1,label = "Route 1")
    plt.plot(x,y2, label = "Route 2")
    plt.legend()
    plt.title("Summation of route green times")
    plt.show()

    show_network(g, flows = result.flows, euclidean=True)
    plt.plot(flows_gap)



main()
