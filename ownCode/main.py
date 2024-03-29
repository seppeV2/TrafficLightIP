import numpy as np
import os
from pathlib import Path
from visualisation_override import show_network_own
from network_summary import create_summary, demand_summary, result_summary
from own_networks import makeOwnToyNetwork
from ownFunctions import getODGraph, set_signalized_nodes_and_links, generateFirstGreen, addCentroidODNodes, global_signalized_nodes
from cost_msa_dyntapy import StaticAssignmentIncludingGreen
from greenTimes import get_green_times
from bokeh.resources import CDN
from bokeh.io import export_png


# function to auto generate all the results
def main_loop():
    
    methods = [('hybrid', 'equisaturation'), ('hybrid','P0')]#,('WebsterTwoTerm', 'equisaturation'), ('WebsterTwoTerm', 'P0'),('bpr', 'equisaturation'),('bpr', 'P0')]
    networks = ['twoMerge']#,'merge', 'simple', 'two-node', 'two-node-two-od', 'two-node-three-od', 'complex' ] 
    greenTimes = ['40-60','60-40','20-80','80-20','equal']

    OD_flow = {
        'complex' :[[(0,3,80),(1,3,25),(2,3,25)],[(0,3,100),(1,3,10),(2,3,10)] ,[(0,3,50),(1,3,30),(2,3,30)] ,[(0,3,100),(1,3,20),(2,3,20)] ,[(0,3,40),(1,3,40),(2,3,40)],[(0,3,25),(1,3,25),(2,3,25)],[(0,3,20),(1,3,100),(2,3,10)] ,[(0,3,90),(1,3,15),(2,3,30)] ,[(0,3,70),(1,3,20),(2,3,10)] ,[(0,3,40),(1,3,80),(2,3,40)],[(0,3,105),(1,3,15),(2,3,15)],[(0,3,110),(1,3,10),(2,3,20)]] ,
        'merge' : [[(0,2,60),(1,2,30)],[(0,2,100),(1,2,10)],[(0,2,95),(1,2,25)],[(0,2,100),(1,2,25)],[(0,2,95),(1,2,25)],[(0,2,120),(1,2,10)],[(0,2,30),(1,2,30)],[(0,2,120),(1,2,40)],[(0,2,230),(1,2,40)],[(0,2,145),(1,2,40)],[(0,2,145),(1,2,70)]],
        'simple' : [[(0,1,90)],[(0,1,120)],[(0,1,145)],[(0,1,230)]],
        'twoMerge' : [[(0,3,70),(1,3,10),(2,3,10)],[(0,3,90),(1,3,5),(2,3,5)],[(0,3,80),(1,3,20),(2,3,20)],[(0,3,80),(1,3,20),(2,3,20)],[(0,3,80),(1,3,30),(2,3,20)] ,[(0,3,100),(1,3,20),(2,3,20)],[(0,3,120),(1,3,20),(2,3,20)] ,[(0,3,145),(1,3,20),(2,3,20)],[(0,3,230),(1,3,20),(2,3,20)]],
        'two-node' : [[(0,1,90)],[(0,1,120)],[(0,1,145)],[(0,1,230)]],
        'two-node-two-od' : [[(0,2,60),(1,2,30)],[(0,2,100),(1,2,10)],[(0,2,95),(1,2,25)],[(0,2,100),(1,2,25)],[(0,2,95),(1,2,25)],[(0,2,120),(1,2,10)],[(0,2,30),(1,2,30)],[(0,2,120),(1,2,40)],[(0,2,230),(1,2,40)],[(0,2,145),(1,2,40)],[(0,2,145),(1,2,70)]],
        'two-node-three-od' : [[(0,3,80),(1,3,25),(2,3,25)],[(0,3,100),(1,3,10),(2,3,10)] ,[(0,3,50),(1,3,30),(2,3,30)] ,[(0,3,100),(1,3,20),(2,3,30)] ,[(0,3,40),(1,3,40),(2,3,40)],[(0,3,25),(1,3,25),(2,3,25)],[(0,3,20),(1,3,100),(2,3,10)] ,[(0,3,90),(1,3,15),(2,3,30)] ,[(0,3,70),(1,3,20),(2,3,10)] ,[(0,3,40),(1,3,80),(2,3,40)],[(0,3,105),(1,3,15),(2,3,15)],[(0,3,145),(1,3,10),(2,3,20)],[(0,3,145),(1,3,40),(2,3,70)],[(0,3,230),(1,3,10),(2,3,20)]]
    }

    string = ''
    for network in networks:
        for (cost, policy) in methods:
            for greenTime in greenTimes:
                #for flow in OD_flow[network]:
                    string = main(network, cost, policy, greenTime, [(0,3,80),(1,3,15),(2,3,15)], string = string)

    print(string)

#main function where we merge everything together
def main(network_type, methodCost,methodGreen, greenDistribution, flow, summary = True, string = ''):

    #assign all variables 
        #two cost functions at the moment
        # 'bpr' to use the bpr cost function
        # 'WebsterTwoTerm' to use the webster two term delay cost function
    #methodCost = 'WebsterTwoTerm'

        #two green time policies
        # 'equisaturation' 
        # 'P0'
    #methodGreen = 'equisaturation'

    ## Chose your network type
        # complex
        # merge
        # twoMerge
        # simple
        # two-node
        # two-node-two-od
        # two-node-three-od
    #network_type = 'two-node-two-od'

    # Every element of this list is a tuple (x,y) with the coordinates of an origin or destination
    
    O_or_D = {
        'complex' :[(10,35),(30,15),(50,35),(90,35)], #this one is saved for the complex network
        'merge' :[(0,30),(0,0),(35,30)], #this one is saved for the merge network
        'twoMerge' : [(0,30),(0,0),(0,60),(35,30)],#two merge
        'simple' :[(0,30),(35,30)], #this one is saved for the simple network
        'two-node' :[(0,30),(65,30)], #this one is saved for the two node signal network
        'two-node-two-od' :[(0,30),(30,0),(65,30)], #this one is saved for the two node signal two od network
        'two-node-three-od' :[(0,30),(30,0),(0,0),(65,30)] #this one is saved for the two node signal three od network
    }

    # This is a list of tuples (x,y,z) with x the origin, y the destination and z the flow (after relabeling)
    # X and Y = the location of the element in the O_or_D[network_type] list 
    
    OD_flow = {
        'complex' :[(0,3,30),(1,3,30),(2,3,35)], #this one is saved for the complex network
        'merge' : [(0,2,100),(1,2,50)], #this one is saved for the merge network
        'twoMerge': [(0,3,70),(1,3,20),(2,3,20)],#two merge
        'simple' : [(0,1,150)], #this one is saved for the merge network
        'two-node' : [(0,1,120)], #this one is saved for the two node signal network
        'two-node-two-od' : [(0,2,105),(1,2,25)], #this one is saved for the two node signal two od network
        'two-node-three-od' : [(0,3,80),(1,3,25),(2,3,25)] #this one is saved for the two node signal three od network
    }

    # Signalized nodes id (after relabeling!!)
    signalized_nodes = {
        'complex' : [10,11], #complex
        'merge' : [4], #merge
        'twoMerge': [5], #two merge
        'simple' : [3], #simple
        'two-node' : [3,5], #two node
        'two-node-two-od' : [4,6], #two node two od
        'two-node-three-od' : [5,7] #two node three od
    }

    # show the plot in browser or make a summary
    #summary = True

    #setup
    print("\nSTARTING SETUP\n")

    g = makeOwnToyNetwork(network_type) 
    g = addCentroidODNodes(g, O_or_D[network_type])
    g,signal_node_link_connect = set_signalized_nodes_and_links(g, signalized_nodes[network_type])

    #flow = OD_flow[network_type]
    print(f'network = {network_type}')
    print(f'green time distribution = {greenDistribution}')
    print(f'Asked for Demand = {flow}\n')
    odGraph = getODGraph(flow, O_or_D[network_type])
    assignment = StaticAssignmentIncludingGreen(g, odGraph)


    # The first greens are automatically set to 0.5 to for all the intersecting links
    # For the 'two link merge intersections' a different distribution can be chosen for the initial green times
    # the more link merge intersections are always equal distributed no mather what argument is given, the argument is  
    # a string type, chose one of the following: '40-60','60-40','20-80','80-20' or 'equal' for the respective distribution (in percentage)
    #greenDistribution = 'equal'
    firstGreens, non_connectors = generateFirstGreen(g,signal_node_link_connect,distribution = greenDistribution)
    print('first greens = {}'.format(firstGreens))
    print('non_connector links = {}'.format(non_connectors))
    
    #initial msa without traffic lights
    result, ff_tt = assignment.run_greens('msa', firstGreens, methodCost)
    #calculate the first green times according the first static assignment
    greens = get_green_times(result.flows,assignment, methodGreen, firstGreens, ff_tt, g,signal_node_link_connect)


    #start the loop
    print('\nSTART THE LOOP\n')
        #initialise parameters and variables
    delta = 10**-4
    maxLoops = 200
    safety_loop = 0
    gap = 1
    prev_flow = np.zeros(len(result.flows))
    while gap > delta and safety_loop < maxLoops:
        safety_loop += 1
        print('\n#### LOOP = {} ###'.format(safety_loop))

        newResult, ff_tt = assignment.run_greens('msa', greens,methodCost)
        #print('flows: {}'.format([(idx, flow) for idx, flow in enumerate(newResult.flows)]))
        print('link costs: {}'.format([(idx, cost) for idx, cost in enumerate(newResult.link_costs)]))

        #calculating the gap (difference o)
        gap = np.linalg.norm(np.subtract(result.flows, newResult.flows)) + np.linalg.norm(np.subtract(prev_flow, newResult.flows))
        print('current gap = {}'.format(round(gap,5)))

        prev_flow = result.flows
        result = newResult
        if gap<delta: break
        newGreens = get_green_times(newResult.flows, assignment, methodGreen, greens, ff_tt, g,signal_node_link_connect)
        print('new greens = {}'.format(newGreens))
        
        greens = newGreens

    
    if not summary:
        show_network_own(g, flows=result.flows, euclidean=True, signalized_nodes=signalized_nodes[network_type], O_or_D=O_or_D[network_type])
        veh_hours = 0
        final_flow = {}
        final_cost = {}
        final_green = {}
        for idx, (flow, cost) in enumerate(zip(result.flows, result.link_costs)):
            if idx in non_connectors:
                veh_hours += flow*cost  
                final_flow[idx] = round(flow,3)
                final_cost[idx] = round(cost,3)
                final_green[idx] = round(greens[idx],3)
        string += f'\nFINAL RESULTS:\n\nCost function = {methodCost}, Policy = {methodGreen}\nFinal greens = {final_green}\nFinal flows = {final_flow}\nFinal costs = {final_cost}\nFinal vehicle hours = {round(veh_hours,4)}/n'
        print(f'\nFINAL RESULTS:\n\nCost function = {methodCost}, Policy = {methodGreen}\nFinal greens = {final_green}\nFinal flows = {final_flow}\nFinal costs = {final_cost}\nFinal vehicle hours = {round(veh_hours,4)}')
    else:
        graph = show_network_own(g, flows = result.flows, euclidean=True,return_plot=True, signalized_nodes=signalized_nodes[network_type], O_or_D=O_or_D[network_type])
        path = str(Path(__file__).parent)+'/summaryFiles/rawFigures/'
        os.makedirs(path, exist_ok=True)
        export_png(graph, filename=path+'network.png' )
        listOfPlots = ['network.png']
        summary_string = 'SUMMARY: cost method = {}, heuristic = {}'.format(methodCost, methodGreen)
        summary_string += demand_summary(O_or_D[network_type], flow,signalized_nodes[network_type] )
        #demand = sum([flow for (_,_,flow) in OD_flow[network_type]])
        result_summary_string = result_summary(result,greens,assignment.internal_network.links.capacity, non_connectors,safety_loop, firstGreens, ff_tt, methodGreen)
        create_summary(listOfPlots, summary_string, result_summary_string, methodCost, methodGreen, network_type, str(flow), greenDistribution)

    return string
#main('twoMerge', 'hybrid', 'P0', '20-80', [(0,3,80),(1,3,15),(2,3,15)], True )        
main_loop()