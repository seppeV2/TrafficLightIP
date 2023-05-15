from dyntapy.supply_data import road_network_from_place
from dyntapy.demand_data import  add_centroids,od_graph_from_matrix
from dyntapy.visualization import show_network
from dyntapy import relabel_graph
import numpy as np
import os
from pathlib import Path
from networkx import read_gpickle, write_gpickle
from demand.STA import STA_initial_setup, lambert72toWGS84
import geopandas as gpd
import pandas as pd

def retrieve_osm_network(place:str, distance_inner:int):
    path = os.path.join(Path(__file__).parent, 'osm_data', f'{place}_{distance_inner}')
    fileName = f'network_{place}_{distance_inner}.gpickle'

    #OD demand parameters
    place = place.upper() # CAPS
    buffer_N = distance_inner/1000
    buffer_D = buffer_N
    buffer_transit = 45 
    D_sup=1 # kms, use in the range 0-1 (res:0.1) if you want to include some boundary zones
    time_of_day = 9
    ext = 1 # 0 for only internal, 1 for taking external demand w/o transit, 2 for external with transit

    if os.path.isfile(os.path.join(path, fileName)):
        STA_initial_setup(place, buffer_D,buffer_N,buffer_transit, D_sup, time_of_day, ext, path_parent = path)
        g = read_gpickle(os.path.join(path, fileName))

    else:
        os.makedirs(path, exist_ok=True)
        STA_initial_setup(place, buffer_D,buffer_N,buffer_transit, D_sup, time_of_day, ext, path_parent = path)
        g = road_network_from_place(place, buffer_dist_close= distance_inner)
        write_gpickle(g, os.path.join(path,fileName))

    return g

def add_centroid_from_demand_file(g, place, distance):
    
    path = os.path.join(Path(__file__).parent, 'osm_data', f'{place}_{distance}', f'{place.upper()}', f'{place.upper()}.shp')
    shp_file = gpd.read_file(path)
    centroid_y_raw = np.array(list(shp_file['centroid_y']))
    centroid_x_raw = np.array(list(shp_file['centroid_x']))

    centroid_x = []
    centroid_y = []

    # transform the coordinates
    for x, y in zip(centroid_x_raw, centroid_y_raw):
        [y_bis, x_bis] = lambert72toWGS84(x,y)
        centroid_x.append(x_bis)
        centroid_y.append(y_bis)

    g = add_centroids(g, X = np.array(centroid_x), Y = np.array(centroid_y), k = 3,method = 'link')
    g = relabel_graph(g)  # adding link and node ids, connectors and centroids

    return g, np.array(centroid_x), np.array(centroid_y)

def generate_od_graph(place, distance, centroids_x, centroids_y, demandFactor):
    path = os.path.join(Path(__file__).parent, 'osm_data', f'{place}_{distance}', f'{place.upper()}.xlsx')
    df = pd.read_excel(path)
    matrix = df.to_numpy()*demandFactor
    return od_graph_from_matrix(matrix, X=centroids_x, Y=centroids_y)


def create_osm_network(place, distance, demandFactor):
    g = retrieve_osm_network(place, distance)
    g, centroid_x, centroid_y = add_centroid_from_demand_file(g, place, distance)
    od_graph = generate_od_graph(place, distance, centroid_x, centroid_y, demandFactor)

    path_raw = os.path.join(Path(__file__).parent, 'osm_data',f'{place}_{distance}')
    fileName = f'{place}_signalized_nodes.csv'
    path = os.path.join(path_raw, fileName)
    if os.path.isfile(path):
        df = pd.read_csv(path, header = None)
        df = df.T
        signalized_nodes = df.to_numpy()[0]

    else:
        signalized_nodes = []
        show_network(g)
        print('\n No signalized nodes yet! Add them by id_number.')
        while True:
            id = input('node id to signalize, type -1 to end: ')
            if int(id) == -1:
                print('signaled nodes added')
                break
            else:
                signalized_nodes.append(int(id))

        pd.DataFrame(signalized_nodes).to_csv(path, index=False, header = False)
    fileName = f'{place}_centroids.csv'
    path = os.path.join(path_raw, fileName)
    centroids = [(x,y) for (x,y) in zip(centroid_x, centroid_y)]
    pd.DataFrame(centroids).to_csv(path, index = False, header = False)
    return g, od_graph, signalized_nodes, centroids
