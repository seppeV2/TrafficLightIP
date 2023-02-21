import networkx as nx
import numpy as np
import pathlib
import matplotlib.pyplot as plt


from dyntapy import show_network
from network_summary import create_summary
from own_networks import makeOwnToyNetwork
from ownFunctions import getODGraph, set_signalized_nodes_and_links, generateFirstGreen, addCentroidODNodes
from dyntapy_green_time_change import GreenStaticAssignment
from greenTimes import get_green_times
from bokeh.resources import CDN
from bokeh.io import export_png




#main function where we merge everything together
def main():
        #two cost functions at the moment
        # 'bpr' to use the bpr cost function
        # 'WebsterTwoTerm' to use the webster two term delay cost function
    methodCost = 'WebsterTwoTerm'

        #two green time policies
        # 'equisaturation' 
        # 'P0'
    methodGreen = 'P0'

    # every element of this list is a tuple (x,y) with the coordinates of an origin or destination
    O_or_D = [(10,35),(30,15),(50,35),(90,35)]

    # This is a list of tuples (x,y,z) with x the origin, y the destination and z the flow (after relabeling)
    # X and Y = the location of the element in the O_or_D list 
    OD_flow = [(0,3,90),(1,3,50),(2,3,50)]

    # Signalized nodes id (after relabeling!!)
    signalized_nodes = [10,11]

    #setup
    print("\nSTARTING SETUP\n")
    g = makeOwnToyNetwork('complex')
    g = addCentroidODNodes(g, O_or_D)
    g = set_signalized_nodes_and_links(g, signalized_nodes)

    odGraph = getODGraph(OD_flow, O_or_D)
    assignment = GreenStaticAssignment(g, odGraph)

    # The first greens are automatically set to 0.5 to for all the intersecting links
    firstGreens, non_connectors = generateFirstGreen(g)
    print('first greens = {}'.format(firstGreens))
    print('non_connector links = {}'.format(non_connectors))
    
    #initial msa without traffic lights
    result, ff_tt = assignment.run_greens('msa', firstGreens, methodCost)
    #calculate the first green times according the first static assignment
    greens = get_green_times(result.flows,assignment, methodGreen, firstGreens, ff_tt, g)


    #start the loop
    print('\nSTART THE LOOP\n')
        #initialise parameters and variables
    delta = 10**-4
    maxLoops = 100
    safety = 0
    gap = 1
    flows_gap = []
    prev_flow = np.zeros(len(result.flows))
    while gap > delta and safety < maxLoops:
        safety += 1
        print('\n#### LOOP = {} ###'.format(safety))

        newResult, ff_tt = assignment.run_greens('msa', greens,methodCost)
        #print('flows: {}'.format([(idx, flow) for idx, flow in enumerate(newResult.flows)]))
        print('link costs: {}'.format([(idx, cost) for idx, cost in enumerate(newResult.link_costs)]))
        newGreens = get_green_times(newResult.flows, assignment, methodGreen, greens, ff_tt, g)
        print('new greens = {}'.format(newGreens))
        #calculating the gap (difference o)
        gap = np.linalg.norm(np.subtract(result.flows, newResult.flows)) + np.linalg.norm(np.subtract(prev_flow, newResult.flows))

        #add intermediate results to the list to plot
        flows_gap.append(gap)

        prev_flow = result.flows
        result = newResult
        greens = newGreens

    
    show_network(g, flows=result.flows, euclidean=True)

main()