from math import inf
import numpy as np
from dyntapy.settings import parameters
from ownFunctions import getIntersections


bpr_b = parameters.static_assignment.bpr_beta
bpr_a = parameters.static_assignment.bpr_alpha

def __bpr_green_cost(flows, capacities, ff_tts, g_times):
    number_of_links = len(flows)
    costs = np.empty(number_of_links, dtype=np.float64)
    for it, (f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        costs[it] = __bpr_green_cost_single(f, c, ff_tt,g_time)
    return costs

#building our own bpr funtion 
def __bpr_green_cost_single(flow, capacity, ff_tt, g_time):

    cost = ff_tt * (1.0 + np.multiply(bpr_a, pow((flow / (np.multiply(capacity ,g_time))), bpr_b)))
    return cost

def __webster_two_term_green(flows, capacities, ff_tts, g_times,g):
    number_of_links = len(flows)
    costs = np.empty(number_of_links, dtype=np.float64)
    dos = np.empty(number_of_links, dtype=np.float64)
    signal_links = getIntersections(g)[2]
    print(signal_links)
    for it, (f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        if signal_links[it] == 1:
            costs[it] = __webster_two_term_green_single(f, c, ff_tt,g_time)
        else:
            costs[it] = ff_tts[it]
        dos[it] = f/(c*g_time)
    print("DOS: {}".format(dos))
    print("costs: {}".format(costs))
    return costs

def __webster_two_term_green_single(flow, capacity, ff_tt, g_time):
    dos = flow/(capacity*g_time)
    print(dos)
    if dos >= 1:
        cost = 100
    elif dos <= 0:
        cost = 0
    else:
        term1 = (capacity*(1-g_time)**2)/(1-g_time*dos)
        term2 = (dos**2)/(capacity*g_time*dos*(1-dos))
        cost = ff_tt + (9/20)*(term1+term2)
    return cost


