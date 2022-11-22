import networkx as nx
import numpy as np
import pathlib
import matplotlib.pyplot as plt


from dyntapy import show_network

from ownFunctions import makeOwnToyNetwork, getODGraph
from dyntapy_green_time_change import GreenStaticAssignment
from greenTimes import get_green_times



#main function where we merge everything together
def main():
        #two cost functions at the moment
        # 'bpr' to use the bpr cost function
        # 'WebsterTwoTerm' to use the webster two term delay cost function
    methodCost = 'bpr'

        #two green time policies
        # 'equisaturation' 
        # 'P0'
    methodGreen = 'equisaturation'

    plot = True

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
    [result, ff_tt, dos] = assignment.run_greens('msa', firstGreen,methodCost,g)
    #calculate the first green times according the first static assignment
    print('\nflows: '+str(result.flows))
    print('free flow cost: {}'.format(ff_tt))

    greens,diff = get_green_times(assignment.internal_network.links.capacity,result.flows,assignment, methodGreen, firstGreen, g, ff_tt)
    print('greens: '+ str(greens))


    #show_network(g, flows = result.flows, euclidean=True)
    #start the loop
    print('START THE LOOP')
        #initialise parameters and variables
    delta = 0.001
    maxLoops = 50
    safety = 0
    gap = 1
    flows_gap = []
    cost_link_a = [result.link_costs[0]]
    cost_link_b = [result.link_costs[3]]
    green_link_a = [greens[0]]
    green_link_b = [greens[3]]
    if methodCost == 'WebsterTwoTerm':
        dos_link_a = [dos[0]]
        dos_link_b = [dos[3]]
    diff_l = [diff]
    prev_flow = np.zeros(len(result.flows))
    while gap > delta and safety < maxLoops:
        safety += 1
        print('####\tLOOP = '+str(safety))

        newResult, ff_tt, dos = assignment.run_greens('msa', greens,methodCost,g)
        print('flows: {}'.format(newResult.flows))
        print('link costs: {}'.format(newResult.link_costs))
        print('free flow cost: {}'.format(ff_tt))
        if methodCost == 'WebsterTwoTerm':
            dos_link_a.append(dos[0])
            dos_link_b.append(dos[3])

        newGreens, diff = get_green_times(assignment.internal_network.links.capacity, newResult.flows, assignment, methodGreen, greens, g, ff_tt)
        diff_l.append(diff)

        green_link_a.append(newGreens[0])
        green_link_b.append(newGreens[3])
        #calculating the gap 
        gap = np.linalg.norm(np.subtract(result.flows, newResult.flows)) + np.linalg.norm(np.subtract(prev_flow, newResult.flows))
        print('Gap = {}\n'.format(gap))


        #add intermediate results to the list to plot
        flows_gap.append(gap)
        cost_link_a.append(newResult.link_costs[0])
        cost_link_b.append(newResult.link_costs[3])

        prev_flow = result.flows
        result = newResult
        greens = newGreens

    show_network(g, flows = result.flows, euclidean=True)

    if plot:
        ## graph plots 
        """ plt.figure()
        plt.plot(flows_gap)
        plt.title('Evolution of the gap during the iterations') """
        
        plt.figure()
        plt.plot(cost_link_a)
        plt.plot(cost_link_b)
        plt.title('Evolution of the link costs on the two intersection links')
        plt.legend(['link 0','link 3'])

        plt.figure()
        plt.plot(green_link_a)
        plt.plot(green_link_b)
        plt.title('Green time evolution')
        plt.legend(['link 0', 'link 3'])
        """ plt.figure()
        plt.plot(diff_l)
        plt.title("evolution of policy constraint (gap = change between the two)") """

        if methodCost == 'WebsterTwoTerm':
            plt.figure()
            plt.plot(dos_link_a)
            plt.plot(dos_link_b)
            plt.title("Dos evolution through the msa steps")
            plt.legend(['link 0', 'link 3'])


        plt.show()




main()