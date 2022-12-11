import networkx as nx
import numpy as np
import pathlib
import matplotlib.pyplot as plt


from dyntapy import show_network
from network_summary import create_summary
from ownFunctions import makeOwnToyNetwork, getODGraph
from dyntapy_green_time_change import GreenStaticAssignment
from greenTimes import get_green_times
from bokeh.resources import CDN
from bokeh.io import export_png




#main function where we merge everything together
def main():
    demands = [105]
    for demand_i in demands:
            #two cost functions at the moment
            # 'bpr' to use the bpr cost function
            # 'WebsterTwoTerm' to use the webster two term delay cost function
        methodCost = 'WebsterTwoTerm'

            #two green time policies
            # 'equisaturation' 
            # 'P0'
        methodGreen = 'equisaturation'

        plot = True

        #setup
        print("STARTING SETUP")
        g, ODcentroids, odFile = makeOwnToyNetwork('simple')
        matrix = np.zeros([4,4])
        matrix[0,3] = demand_i
        ODMatrix_location = str(pathlib.Path(__file__).parent)+'/data/'+str(odFile)
        np.savetxt(ODMatrix_location, matrix, delimiter=",")
        
        ODMatrix = np.genfromtxt(ODMatrix_location, delimiter=',')
        odGraph = getODGraph(ODMatrix_location, ODcentroids)
        
        demand = ODMatrix[np.nonzero(ODMatrix)][0]
        assignment = GreenStaticAssignment(g, odGraph)

        summary_string = 'Cost method: {}\nPolicy: {}\nDemand: {}\n\n'.format(methodCost, methodGreen,demand)

        print("RUNNING FIRST STATIC ASSIGNMENT WITH TRAFFIC LIGHTS (equal distributed)")

        #starting with 0.5 at every two link node
            #hardCoded for simple
        firstGreen = {0: 0.5, 1: 1, 2: 1, 3: 0.5}
            #hardCoded for complex 
        #firstGreen = {0: 1, 1: 1, 2: 0.5, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0.5, 8: 0.5, 9: 1, 10: 1, 11: 1, 12: 0.5, 13: 0.5, 14: 1, 15: 0.5}
        summary_string += "initial greens: link 0 = {},   link 3 = {}\n".format(firstGreen[0], firstGreen[3])

        #initial msa without traffic lights
                #result2 = assignment.run('msa')
        [result, ff_tt, dos] = assignment.run_greens('msa', firstGreen,methodCost,g)
        #calculate the first green times according the first static assignment
        print('\nflows: '+str(result.flows))
        print('free flow cost: {}'.format(ff_tt))
        summary_string += "free flow cost: link 0 = {},   link 3 = {}\n\n".format(round(ff_tt[0],3), round(ff_tt[3],3))
        greens,diff, _ = get_green_times(assignment.internal_network.links.capacity,result.flows,assignment, methodGreen, firstGreen, g, ff_tt)
        print('greens: '+ str(greens))



        #show_network(g, flows = result.flows, euclidean=True)
        #start the loop
        print('START THE LOOP')
            #initialise parameters and variables
        delta = 10**-4
        maxLoops = 100
        safety = 0
        gap = 1
        gap2 = 1
        flows_gap = []
        cost_link_a = [result.link_costs[0]]
        cost_link_b = [result.link_costs[3]]
        green_link_a = [greens[0]]
        green_link_b = [greens[3]]
        dos_link_a = [firstGreen[0],dos[0]]
        dos_link_b = [firstGreen[3],dos[3]]
        diff_l = [diff]
        prev_flow = np.zeros(len(result.flows))
        while gap > delta and safety < maxLoops:
            safety += 1
            print('#### LOOP = '+str(safety))

            newResult, ff_tt, dos = assignment.run_greens('msa', greens,methodCost,g)
            print('flows: {}'.format(newResult.flows))
            print('link costs: {}'.format(newResult.link_costs))
            print('free flow cost: {}'.format(ff_tt))
            dos_link_a.append(dos[0])
            dos_link_b.append(dos[3])

            newGreens, diff, theoreticalGreenTime = get_green_times(assignment.internal_network.links.capacity, newResult.flows, assignment, methodGreen, greens, g, ff_tt)
            diff_l.append(diff)

            green_link_a.append(newGreens[0])
            green_link_b.append(newGreens[3])
            #calculating the gap 
                #use flow gap
            gap = np.linalg.norm(np.subtract(result.flows, newResult.flows)) + np.linalg.norm(np.subtract(prev_flow, newResult.flows))
                #use greens gap
            gap2 = np.linalg.norm(np.subtract(list(greens.values()), list(newGreens.values())))
            print('Gap = {}'.format(gap))
            print('Green gap = {}\n'.format(gap2))


            #add intermediate results to the list to plot
            flows_gap.append(gap)
            cost_link_a.append(newResult.link_costs[0])
            cost_link_b.append(newResult.link_costs[3])

            prev_flow = result.flows
            result = newResult
            greens = newGreens

        summary_string += "link flows: link 0 = {},   link 3 = {}\n".format(round(result.flows[0],3), round(result.flows[3],3))
        summary_string += "link costs: link 0 = {},   link 3 = {}\n".format(round(cost_link_a[-1],3), round(cost_link_b[-1],3))
        summary_string += "final green times: link 0 = {},   link 3 = {}\n".format(round(greens[0],3), round(greens[3],3))
        summary_string += "final 5 dos: link 0 = {}\nfinal 5 dos:   link 3 = {}\n".format(np.round(dos_link_a[-5:],3), np.round(dos_link_a[-5:],3))
        if theoreticalGreenTime != []: 
            summary_string += "final Theoretical green times: link 0 = {},   link 3 = {}\n".format(round(theoreticalGreenTime[0],3), round(theoreticalGreenTime[1],3))
        

        graph = show_network(g, flows = result.flows, euclidean=True,return_plot=True)
        export_png(graph, filename=str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/network.png' )
        listOfPlots = ['network.png']
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
            plt.savefig(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/linkCost.png')
            listOfPlots.append('linkCost.png')

            plt.figure()
            plt.plot(green_link_a)
            plt.plot(green_link_b)
            plt.title('Green time evolution')
            plt.legend(['link 0', 'link 3'])
            plt.savefig(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/greenTime.png')
            listOfPlots.append('greenTime.png')

            """ plt.figure()
            plt.plot(diff_l)
            plt.title("evolution of policy constraint (gap = change between the two)") """

            plt.figure()
            plt.plot(dos_link_a)
            plt.plot(dos_link_b)
            plt.title("Dos evolution through the msa steps")
            plt.legend(['link 0', 'link 3'])
            plt.savefig(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/dos.png')
            listOfPlots.append('dos.png')
                

        print(summary_string)
        create_summary(listOfPlots, summary_string, methodCost, methodGreen, demand )





main()