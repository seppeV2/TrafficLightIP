from networkx import read_gpickle, write_gpickle
from visualisation_override import show_network_own_real
import pandas as pd
from pathlib import Path
import os

g = read_gpickle('test_g.gpickle')

path = os.path.join(Path(__file__).parent, 'osm_data',f'leuven_3000', f'leuven_signalized_nodes.csv')
df = pd.read_csv(path, header = None)
df = df.T
signalized_nodes = df.to_numpy()[0]

path = os.path.join(Path(__file__).parent, 'osm_data',f'leuven_3000', f'leuven_centroids.csv')
df = pd.read_csv(path, header = None)
df = df.T
signalized_nodes_cor = df.to_numpy()

signalized_nodes_cor = [(x,y) for (x,y) in zip(signalized_nodes_cor[0],signalized_nodes_cor[1])]


show_network_own_real(g,signalized_nodes = signalized_nodes, O_or_D=signalized_nodes_cor, return_plot=False, show_nodes=False)

