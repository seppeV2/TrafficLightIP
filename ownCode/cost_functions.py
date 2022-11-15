from math import inf
import numpy as np
from dyntapy.settings import parameters


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

def __webster_two_term_green(flows, capacities, ff_tts, g_times):
    number_of_links = len(flows)
    costs = np.empty(number_of_links, dtype=np.float64)
    dos = np.empty(number_of_links, dtype=np.float64)
    print('flows inside two term before adjusment = {}'.format(flows))
    #flows = flow_corrector(flows,capacities, g_times,[])
    print('flows inside two term = {}'.format(flows))
    for it, (f, c, ff_tt,g_time) in enumerate(zip(flows, capacities, ff_tts, g_times)):
        assert c != 0
        costs[it] = __webster_two_term_green_single(f, c, ff_tt,g_time)[0]
        dos[it] = __webster_two_term_green_single(f, c, ff_tt,g_time)[1]
    print('dos = {}'.format(dos))
    return costs

def __webster_two_term_green_single(flow, capacity, ff_tt, g_time):
    dos = flow/(capacity*g_time)
    if dos >= 1:
        cost = 50
    elif dos <= 0:
        cost =0
    else:
        term1 = (capacity*(1-g_time)**2)/(1-g_time*dos)
        term2 = (dos**2)/(capacity*g_time*dos*(1-dos))
        cost = ff_tt + (9/20)*(term1+term2)
    return cost, dos


#the safety mech to make sure DOS is never 1
def flow_corrector(flows, capacities, greens, corrected):
    newCorrector = 0
    correct = 0
    newFlow = []
    corrected = []
    for x,c,g in zip(flows, capacities, greens):
        if x > c*g and g != 1:
            correct += x-((c*g))
            flow = x-correct
            newFlow.append(flow)
            corrected.append(1)
            newCorrector +=1
        else:
            newFlow.append(x)
            corrected.append(0)
    #when reassigned check if it is not overcapacitated again
    if newCorrector != 0:
        for i in range(len(corrected)):
            split = correct/sum(corrected)
        if corrected[i] != 1:
            newFlow[i] += split
        newFlow = flow_corrector(newFlow, capacities, greens, corrected)

    return newFlow
