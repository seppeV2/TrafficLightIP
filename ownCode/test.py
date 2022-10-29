from numpy import *
import os
import pathlib

from dyntapy.supply_data import get_toy_network
from dyntapy import show_network, relabel_graph

network = get_toy_network('siouxfalls')
g = relabel_graph(network)
show_network(g, euclidean=True)