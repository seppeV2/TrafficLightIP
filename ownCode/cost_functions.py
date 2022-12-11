from math import inf
import numpy as np
from dyntapy.settings import parameters
from ownFunctions import getIntersections


bpr_b = parameters.static_assignment.bpr_beta
bpr_a = parameters.static_assignment.bpr_alpha

def __bpr_green_cost(flows, capacities, ff_tts, g_times,g):
    number_of_links = len(flows)
    costs = np.empty(number_of_links, dtype=np.float64)
    dos = np.empty(number_of_links, dtype=np.float64)
    signal_links = getIntersections(g)[2]
    for it, (f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        if signal_links[it] == 1:
            costs[it], dos[it] = __bpr_green_cost_single(f, c, ff_tt,g_time)
            
        else:
            costs[it] = ff_tts[it]
            dos[it] = None
    return costs, dos

#building our own bpr funtion 
def __bpr_green_cost_single(flow, capacity, ff_tt, g_time):
    #print('delay due to flow, {}, cap {}, ff_tt {} and green {} = {}'.format(flow, capacity,  ff_tt,g_time, np.multiply(bpr_a, pow((flow / (np.multiply(capacity ,g_time))), bpr_b))))
    cost = ff_tt * (1.0 + np.multiply(bpr_a, pow((flow / (np.multiply(capacity ,g_time))), bpr_b)))
    dos = flow/(capacity*g_time)
    return cost,dos

def __webster_two_term_green(flows, capacities, ff_tts, g_times,g):
    number_of_links = len(flows)
    costs = np.empty(number_of_links, dtype=np.float64)
    dos = np.empty(number_of_links, dtype=np.float64)
    signal_links = getIntersections(g)[2]
    for it, (f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        if signal_links[it] == 1:
            costs[it] = __webster_two_term_green_single(f, c, ff_tt,g_time)
            dos[it] = f/(c*g_time)
        else:
            costs[it] = ff_tts[it]
            dos[it] = None
    return costs, dos

def __webster_two_term_green_single(flow, capacity, ff_tt, g_time):
    dos = flow/(capacity*g_time)
    if dos >= 0.95:
        cost = 10**10
    elif dos <= 0.1:
        cost = ff_tt
    else:
        #assumption
        cycle_time = 60
        term1 = (cycle_time*(1-g_time)**2)/(1-g_time*dos)
        term2 = (dos**2)/(capacity*g_time*dos*(1-dos))
        cost = ff_tt + (9/20)*(term1+term2)
    return cost


