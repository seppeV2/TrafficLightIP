import networkx as nx
import numpy as np
import pathlib
import matplotlib.pyplot as plt


from visualisation_override import show_network, get_node_list, get_link_list
from network_summary import create_summary, demand_summary, result_summary
from own_networks import makeOwnToyNetwork
from ownFunctions import getODGraph, set_signalized_nodes_and_links, generateFirstGreen, addCentroidODNodes
from dyntapy_green_time_change import GreenStaticAssignment
from greenTimes import get_green_times
from bokeh.resources import CDN
from bokeh.io import export_png




#main function where we merge everything together
def main():

    #assign all variables 
        #two cost functions at the moment
        # 'bpr' to use the bpr cost function
        # 'WebsterTwoTerm' to use the webster two term delay cost function
    methodCost = 'WebsterTwoTerm'

        #two green time policies
        # 'equisaturation' 
        # 'P0'
    methodGreen = 'P0'

    # Chose your network type 
        # complex
        # merge
        # simple
    network_type = 'complex'

    # Every element of this list is a tuple (x,y) with the coordinates of an origin or destination
    # 
    O_or_D = [(10,35),(30,15),(50,35),(90,35)] #this one is saved for the complex network
    #O_or_D = [(0,30),(0,0),(35,30)] #this one is saved for the merge network
    #O_or_D = [(0,30),(35,30)] #this one is saved for the simple network

    # This is a list of tuples (x,y,z) with x the origin, y the destination and z the flow (after relabeling)
    # X and Y = the location of the element in the O_or_D list 
    #
    OD_flow = [(0,3,90),(1,3,50),(2,3,50)] #this one is saved for the complex network
    #OD_flow = [(0,2,90),(1,2,60)] #this one is saved for the merge network
    #OD_flow = [(0,1,120)] #this one is saved for the merge network

    # Signalized nodes id (after relabeling!!)
    signalized_nodes = [10,11] #complex
    #signalized_nodes = [4] #merge
    #signalized_nodes = [3] #simple

    # show the plot in browser or make a summary
    summary = True

    #setup
    print("\nSTARTING SETUP\n")

    g = makeOwnToyNetwork(network_type)
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
    safety_loop = 0
    gap = 1
    prev_flow = np.zeros(len(result.flows))
    while gap > delta and safety_loop < maxLoops:
        safety_loop += 1
        print('\n#### LOOP = {} ###'.format(safety_loop))

        newResult, ff_tt = assignment.run_greens('msa', greens,methodCost)
        #print('flows: {}'.format([(idx, flow) for idx, flow in enumerate(newResult.flows)]))
        #print('link costs: {}'.format([(idx, cost) for idx, cost in enumerate(newResult.link_costs)]))

        newGreens = get_green_times(newResult.flows, assignment, methodGreen, greens, ff_tt, g)
        print('new greens = {}'.format(newGreens))
        #calculating the gap (difference o)
        gap = np.linalg.norm(np.subtract(result.flows, newResult.flows)) + np.linalg.norm(np.subtract(prev_flow, newResult.flows))


        prev_flow = result.flows
        result = newResult
        greens = newGreens

    
    if not summary:
        show_network(g, flows=result.flows, euclidean=True, signalized_nodes=signalized_nodes, O_or_D=O_or_D)
    else:
        graph = show_network(g, flows = result.flows, euclidean=True,return_plot=True, signalized_nodes=signalized_nodes, O_or_D=O_or_D)
        export_png(graph, filename=str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/network.png' )
        listOfPlots = ['network.png']
        summary_string = 'SUMMARY: cost method = {}, heuristic = {}'.format(methodCost, methodGreen)
        summary_string += demand_summary(O_or_D, OD_flow,signalized_nodes )
        demand = sum([flow for (_,_,flow) in OD_flow])
        create_summary(listOfPlots, summary_string, result_summary(result,greens), methodCost, methodGreen, network_type, demand)
        

main()