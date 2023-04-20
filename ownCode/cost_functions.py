from math import inf
import numpy as np
from dyntapy.settings import parameters
from ownFunctions import getIntersections
from dyntapy.sta.utilities import __bpr_cost_single

bpr_b = parameters.static_assignment.bpr_beta #4
bpr_a = parameters.static_assignment.bpr_alpha #0.15

def __bpr_green_cost(flows, capacities, ff_tts, g_times, tot_links):
    costs = np.empty(tot_links, dtype=np.float64)
    signal_links = getIntersections(tot_links)[2]
    for it,(f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        if signal_links[it] == 1:
            costs[it] = __bpr_green_cost_single(f, c, ff_tt,g_time)
        else:
            costs[it] = __bpr_cost_single(f, c, ff_tt)
    return costs

#building our own bpr funtion 
def __bpr_green_cost_single(flow, capacity, ff_tt, g_time):
    #print('delay due to flow, {}, cap {}, ff_tt {} and green {} = {}'.format(flow, capacity,  ff_tt,g_time, np.multiply(bpr_a, pow((flow / (np.multiply(capacity ,g_time))), bpr_b))))
    cost = ff_tt * (1.0 + np.multiply(bpr_a, pow((flow / (np.multiply(capacity ,g_time))), bpr_b)))
    return cost

def __webster_two_term_green(flows, capacities, ff_tts, g_times, tot_links):
    costs = np.empty(tot_links, dtype=np.float64)
    signal_links = getIntersections(tot_links)[2]
    for it, (f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        if signal_links[it] == 1:
            costs[it] = __webster_two_term_green_single(f, c, ff_tt,g_time)
        else:
            costs[it] = __webster_two_term_green_single(f, c, ff_tt,1)
    return costs

def __webster_two_term_green_single(flow, capacity, ff_tt, g_time):
    dos = flow/(capacity*g_time)
    if dos >= 1:
        cost = 10**10
    elif dos <= 0.01:
        cost = ff_tt
    else:
        #assumption
        cycle_time = 1
        term1 = (cycle_time*(1-g_time)**2)/(1-g_time*dos)
        term2 = (dos**2)/(capacity*g_time*dos*(1-dos))
        cost = ff_tt + (9/20)*(term1+term2)
    return cost


def __modified_bpr_cost_single(flow, capacity, ff_tt):
    modified_bpr_b = 4
    modifief_bpr_a = 0.5
    return 1.0 * ff_tt + np.multiply(modifief_bpr_a, pow(flow / capacity, modified_bpr_b)) * ff_tt


def __hybrid_cost(flows, capacities, ff_tts, g_times, tot_links):
    costs = np.empty(tot_links, dtype=np.float64)
    signal_links = getIntersections(tot_links)[2]
    for it,(f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        if signal_links[it] == 1:
            costs[it] = __modified_bpr_cost_single(f, c, ff_tt) + __webster_two_term_green_single(f, c, ff_tt, g_time)
        else:
            costs[it] = __modified_bpr_cost_single(f, c, ff_tt)
    return costs
