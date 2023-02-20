from ownFunctions import makeOwnToyNetwork, getODGraph
from dyntapy import show_network, relabel_graph
from dyntapy.assignments import StaticAssignment
import pathlib

g, centroids, od_location = makeOwnToyNetwork('complex')
show_network(g, euclidean = True)
ODMatrix_location = str(pathlib.Path(__file__).parent)+'/data/'+str(od_location)
od_graph = getODGraph(ODMatrix_location,centroids)


assignment = StaticAssignment(g, od_graph)
results = assignment.run('msa')
show_network(g, flows = results.flows,  euclidean = True)