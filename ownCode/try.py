from ownFunctions import makeOwnToyNetwork
import networkx as nx
import numpy as np
import pathlib
import matplotlib.pyplot as plt

from dyntapy import show_network

from ownFunctions import makeOwnToyNetwork, getODGraph, get_green_times
from dyntapy_green_time_change import GreenStaticAssignment

    #two cost functions at the moment
    # 'bpr' to use the bpr cost function
    # 'WebsterTwoTerm' to use the webster two term delay cost function
methodCost = 'bpr'

    #two green time policies
    # 'equisaturation' 
    # 'P0'
methodGreen = 'P0'


#setup
print("STARTING SETUP")
g, ODcentroids, odFile = makeOwnToyNetwork('simple')
ODMatrix = str(pathlib.Path(__file__).parent)+'/data/'+str(odFile)
odGraph = getODGraph(ODMatrix, ODcentroids)
assignment = GreenStaticAssignment(g, odGraph)

print("RUNNING FIRST STATIC ASSIGNMENT WITH TRAFFIC LIGHTS (equal distributed)")

#starting with 0.5 at every two link node
    #hardCoded for simple
firstGreen = {0: 0.67670481, 1: 1, 2: 1, 3: 0.32329519}

    
    #hardCoded for complex 
#firstGreen = {0: 1, 1: 1, 2: 0.5, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0.5, 8: 0.5, 9: 1, 10: 1, 11: 1, 12: 0.5, 13: 0.5, 14: 1, 15: 0.5}


#initial msa without traffic lights
        #result2 = assignment.run('msa')
result = assignment.run_greens('msa', firstGreen,methodCost)

print(result.link_costs)

