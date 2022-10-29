import pandas as pd
import pathlib
from ownFunctions import makeOwnToyNetwork, getODGraph
from dyntapy.supply_data import build_network
""" edge_file = str(pathlib.Path(__file__).parents[1])+'/dyntapy-master/dyntapy/toy_networks/siouxfalls_net.tntp'
node_file = str(pathlib.Path(__file__).parents[1])+'/dyntapy-master/dyntapy/toy_networks/siouxfalls_node.tntp'

edge_df = pd.read_csv(edge_file, skiprows=8, sep="\t")
node_file = pd.read_csv(node_file, skiprows=8, sep="\t")
 """

g, ODcentroids = makeOwnToyNetwork()
ODMatrix = str(pathlib.Path(__file__).parent)+'/data/ODmatrix.csv'
odGraph = getODGraph(ODMatrix, ODcentroids)

network = build_network(g, u_turns = False)

print(network.links)