import numpy as np
from dyntapy.settings import parameters
from ownFunctions import getIntersections, global_signalized_links, global_signalized_nodes, signal_node_link_connect
from cost_functions import __bpr_green_cost_single
bpr_b = parameters.static_assignment.bpr_beta
bpr_a = parameters.static_assignment.bpr_alpha
msa_delta = 10**-5


def get_green_times(flows, assignment, method, oldGreenTimesDic, ff_tt, g ):
    network = assignment.internal_network
    caps = network.links.capacity

    link_summary = getIntersections(network.tot_links)[2] #dictionary with link id and 1, 0 (signalized or not)
    greenDic = {}


    for _,v,data in g.edges.data():
        if link_summary[data['link_id']] == 0:
            greenDic[data['link_id']] = 1

    for sign_node_id in signal_node_link_connect.keys():
        intersectionCaps = []
        intersectionLinksFlows = []
        oldGreenTimes = []
        intersectionFf_tt = []
        for signal_link_id in signal_node_link_connect[sign_node_id]:
            intersectionCaps.append(caps[signal_link_id])
            intersectionLinksFlows.append(flows[signal_link_id])
            oldGreenTimes.append(oldGreenTimesDic[signal_link_id])
            intersectionFf_tt.append(ff_tt[signal_link_id])

        #reply with the right method
        if method == 'equisaturation':
            greenTimes = equisaturationGreenTimes(intersectionCaps, intersectionLinksFlows, oldGreenTimes, intersectionFf_tt, method, signal_node_link_connect[sign_node_id])
        elif method == 'P0':
            greenTimes = P0policyGreenTimes(intersectionCaps, intersectionLinksFlows, oldGreenTimes, intersectionFf_tt, method)
        
        for link_id in greenTimes.keys():
            greenDic[link_id] = greenTimes[link_id]

    return dict(sorted(greenDic.items()))

#finding the green times at an iterative way
#fixed flows are used 
#the return are the green times 
def msa_green_times(caps, flows, initial_greens, ff_tts, method, link_ids):
    converged = False
    greens = initial_greens
    step = 1
    previous_greens = np.multiply(initial_greens,2)
    while not converged:
        step+=1
        if method =='equisaturation':
            #x/(c*g) needs to equal for every arriving link
            equality = [x/(c*g) for x,c,g in zip(flows, caps, greens)]
        elif method == 'P0':
            #c * d needs to be equal, d = bpr cost - ff_tt
            equality = [c*get_link_delay(x,c,ff_tt,g_time) for c,x,ff_tt,g_time in zip(caps, flows, ff_tts, greens)]

        green_time_aon = np.zeros(len(equality))
        maxIndex = equality.index(max(equality))
        #all to the largest, non to the others but with safety (never assign 0 bc sometimes dividing by gi)
        change = 0
        for i in range(len(equality)):
            if i != maxIndex:
                green_time_aon[i] = 0.01
                change += 0.01
        green_time_aon[maxIndex] = 1-change

        #apply the msa step
        newGreens = [(1 / step * g_aon) + ((step - 1) / step * g) for g_aon, g in zip(green_time_aon, greens)]
        def check_for_equality(list):
            equal = True
            for i in range(len(list)-1):
                if abs(list[i] - list[i+1]) > msa_delta:
                    equal = False
            return equal
        greens = safety_greens(greens)
        converged = ((np.linalg.norm(np.subtract(newGreens,greens))+np.linalg.norm(np.subtract(newGreens,previous_greens))) < 10**-5) or (check_for_equality(equality))
        previous_greens = greens
        greens = newGreens

        if check_for_equality(equality):
            converged_reason = 'equality'
        else:
            converged_reason = 'no change in greens' 
        
    print('MSA Green convergence: {}'.format(converged_reason))
    result_greens = {}
    for i in range(len(greens)):
        result_greens[link_ids[i]] = greens[i]

    return result_greens

#safety function so a green time will never be lower than 0.01 if so it is set to 0.01, the sum of all green times stays 1
def safety_greens(greens):
    newGreens = greens
    change = 0
    adjusted = 0
    for idx,g in enumerate(greens):
        if g < 0.01:
            change += 0.01-g
            newGreens[idx] = 0.01
            adjusted += 1
    #if no adjustments are done return the result
    if adjusted == 0:
        return newGreens
    #only here when adjustments are done 
    div = change/sum([1 if x>0.01 else 0 for x in newGreens])
    for idx,g in enumerate(newGreens): 
        if g>0.01:
            #newGreens[idx] = round(newGreens[idx] - div, 6)
            newGreens[idx] -= div
    #check if after adjustment all values are still larger than 0.01        
    safety_greens(newGreens)

    
#in here we will calculate the green times according to different policies
#These will be used in the cost function of the static assignment
def equisaturationGreenTimes(caps, flows, initial_greens, ff_tts, method, link_ids):
    #now calculate the green times iteratively 
    greens = msa_green_times(caps, flows, initial_greens, ff_tts, method, link_ids)
    
    return greens


def P0policyGreenTimes(caps, flows, initial_greens, ff_tts, method):

    #now calculate the green times iteratively 
    greens,equality = msa_green_times(caps, flows, initial_greens, ff_tts, method)
    print('check if the policy constraint is satisfied: {}\n'.format(equality))
    print('MSA P0 Green Times = {}'.format(greens))
    
    return greens


#delay = bpr function + free flow
def get_link_delay(flow, cap , ff_tt, g_time):
    return __bpr_green_cost_single(flow, cap, ff_tt , g_time)[0] - ff_tt
