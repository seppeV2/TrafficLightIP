import networkx as nx
import numpy as np
import pathlib
import matplotlib.pyplot as plt
from bokeh.models import Circle, ColumnDataSource, Grid, LinearAxis, Plot



from visualisation_override import show_network_own, get_node_list, get_link_list
from network_summary import create_summary, demand_summary, result_summary
from own_networks import makeOwnToyNetwork
from ownFunctions import getODGraph, set_signalized_nodes_and_links, generateFirstGreen, addCentroidODNodes
from cost_msa_dyntapy import StaticAssignmentIncludingGreen
from dyntapy import show_network
from greenTimes import get_green_times
from bokeh.resources import CDN
from bokeh.io import export_png






#main function where we merge everything together
def main():

    #assign all variables 
        #two cost functions at the moment
        # 'bpr' to use the bpr cost function
        # 'WebsterTwoTerm' to use the webster two term delay cost function
    methodCost = 'bpr'

        #two green time policies
        # 'equisaturation' 
        # 'P0'
    methodGreen = 'equisaturation'

    # Chose your network type 
        # complex
        # merge
        # simple
        # two-node
        # two-node-two-od
        # two-node-three-od
    network_type = 'merge'

    # Every element of this list is a tuple (x,y) with the coordinates of an origin or destination
    
    O_or_D = {
        'complex' :[(10,35),(30,15),(50,35),(90,35)], #this one is saved for the complex network
        'merge' :[(0,30),(0,0),(35,30)], #this one is saved for the merge network
        'simple' :[(0,30),(35,30)], #this one is saved for the simple network
        'two-node' :[(0,30),(65,30)], #this one is saved for the two node signal network
        'two-node-two-od' :[(0,30),(30,0),(65,30)], #this one is saved for the two node signal two od network
        'two-node-three-od' :[(0,30),(30,0),(0,0),(65,30)] #this one is saved for the two node signal three od network
    }

    # This is a list of tuples (x,y,z) with x the origin, y the destination and z the flow (after relabeling)
    # X and Y = the location of the element in the O_or_D[network_type] list 
    
    OD_flow = {
        'complex' :[(0,3,30),(1,3,30),(2,3,35)], #this one is saved for the complex network
        'merge' : [(0,2,145),(1,2,100)], #this one is saved for the merge network
        'simple' : [(0,1,120)], #this one is saved for the merge network
        'two-node' : [(0,1,120)], #this one is saved for the two node signal network
        'two-node-two-od' : [(0,2,105),(1,2,25)], #this one is saved for the two node signal two od network
        'two-node-three-od' : [(0,3,80),(1,3,25),(2,3,25)] #this one is saved for the two node signal three od network
    }

    # Signalized nodes id (after relabeling!!)
    signalized_nodes = {
        'complex' : [10,11], #complex
        'merge' : [4], #merge
        'simple' : [3], #simple
        'two-node' : [3,5], #two node
        'two-node-two-od' : [4,6], #two node two od
        'two-node-three-od' : [5,7] #two node three od
    }

    # show the plot in browser or make a summary
    summary = True

    #setup
    print("\nSTARTING SETUP\n")

    g = makeOwnToyNetwork(network_type)
    g = addCentroidODNodes(g, O_or_D[network_type])
    g = set_signalized_nodes_and_links(g, signalized_nodes[network_type])

    odGraph = getODGraph(OD_flow[network_type], O_or_D[network_type])
    assignment = StaticAssignmentIncludingGreen(g, odGraph)


    # The first greens are automatically set to 0.5 to for all the intersecting links
    # For the 'two link merge intersections' a different distribution can be chosen for the initial green times
    # the more link merge intersections are always equal distributed no mather what argument is given, the argument is  
    # a string type, chose one of the following: '[40,60]','[60,40]','[20,80]','[80,20]' or 'equal' for the respective distribution (in percentage)
    firstGreens, non_connectors = generateFirstGreen(g,distribution = i)
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
        print('link costs: {}'.format([(idx, cost) for idx, cost in enumerate(newResult.link_costs)]))

        newGreens = get_green_times(newResult.flows, assignment, methodGreen, greens, ff_tt, g)
        print('new greens = {}'.format(newGreens))
        #calculating the gap (difference o)
        gap = np.linalg.norm(np.subtract(result.flows, newResult.flows)) + np.linalg.norm(np.subtract(prev_flow, newResult.flows))
        print('current gap = {}'.format(round(gap,5)))

        prev_flow = result.flows
        result = newResult
        greens = newGreens

    
    if not summary:
        show_network_own(g, flows=result.flows, euclidean=True, signalized_nodes=signalized_nodes[network_type], O_or_D=O_or_D[network_type])
    else:
        graph = show_network_own(g, flows = result.flows, euclidean=True,return_plot=True, signalized_nodes=signalized_nodes[network_type], O_or_D=O_or_D[network_type])
        export_png(graph, filename=str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/network.png' )
        listOfPlots = ['network.png']
        summary_string = 'SUMMARY: cost method = {}, heuristic = {}'.format(methodCost, methodGreen)
        summary_string += demand_summary(O_or_D[network_type], OD_flow[network_type],signalized_nodes[network_type] )
        demand = sum([flow for (_,_,flow) in OD_flow[network_type]])
        result_summary_string = result_summary(result,greens,assignment.internal_network.links.capacity,non_connectors)
        create_summary(listOfPlots, summary_string, result_summary_string, methodCost, methodGreen, network_type, demand,i)

distributions = ['[40,60]','[60,40]','[20,80]','[80,20]','equal']
for i in distributions:
    main()