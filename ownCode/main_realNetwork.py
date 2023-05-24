import numpy as np
from visualisation_override import show_network_own,show_network_own_real
from ownFunctions import set_signalized_nodes_and_links, generateFirstGreen, get_vehicle_hours
from cost_msa_dyntapy import StaticAssignmentIncludingGreen
from greenTimes import get_green_times
from dyntapy import show_network
from osm_networks import create_osm_network
from networkx import read_gpickle, write_gpickle


#main function where we merge everything together
def main(cityName: str, buffer: int, methodGreen: str, greenDistribution = 'equal',demandFactor = 1):

    methodCost = 'hybrid'
    

    #setup
    print("\nSETUP OSM DATA\n")
    g, odGraph, signalized_nodes, OD_points = create_osm_network(cityName, buffer, demandFactor)
    g,signal_node_link_connect = set_signalized_nodes_and_links(g, signalized_nodes)

    #greenDistribution = 'capacity'

    assignment = StaticAssignmentIncludingGreen(g, odGraph)


    # The first greens are automatically set to equal or via capacity when green distribution = capacity 
    firstGreens, non_connectors = generateFirstGreen(g,signal_node_link_connect, distribution = greenDistribution, realLife = True)

    #initial msa without traffic lights
    result, ff_tt = assignment.run_greens('msa', firstGreens, methodCost)
    #show_network_own_real(g, flows = result.flows, signalized_nodes=signalized_nodes, O_or_D=OD_points, show_nodes = False)

    vehicle_hours_start = get_vehicle_hours(result.link_costs, result.flows)
    #calculate the first green times according the first static assignment
    greens = get_green_times(result.flows,assignment, methodGreen, firstGreens, ff_tt, g,signal_node_link_connect,methodCost)


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

        #calculating the gap 
        gap = np.linalg.norm(np.subtract(result.flows, newResult.flows)) + np.linalg.norm(np.subtract(prev_flow, newResult.flows))
        prev_flow = result.flows
        result = newResult
        if gap<delta: break
        newGreens = get_green_times(newResult.flows, assignment, methodGreen, greens, ff_tt, g,signal_node_link_connect,methodCost)
        greens = newGreens

    
    show_network_own_real(g, flows = result.flows, signalized_nodes=signalized_nodes, O_or_D=OD_points, show_nodes = False)
    vehicle_hours_end = get_vehicle_hours(result.link_costs, result.flows)

    print(f'\n\nRESULTS:\nvehicle hours with {greenDistribution} = {round(vehicle_hours_start,5)}\nvehicle after algorithm with {methodGreen} = {round(vehicle_hours_end,5)}')


main('Kortrijk', 3000, 'equisaturation', greenDistribution = 'capacity', demandFactor = 1.5)
#187
#188
#153
#241