import numpy as np
from dyntapy.settings import parameters
bpr_b = parameters.static_assignment.bpr_beta
bpr_a = parameters.static_assignment.bpr_alpha
msa_delta = parameters.static_assignment.msa_delta

#finding the green times at an iterative way
#fixed flows are used 
#the return are the green times 
def msa_green_times(caps, flows, initial_greens, ff_tts, method):
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
            equality = [c*get_link_delay(x,c,ff_tt,g) for c,x,ff_tt,g in zip(caps, flows, ff_tts, greens)]

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

        converged = ((np.linalg.norm(np.subtract(newGreens,greens))+np.linalg.norm(np.subtract(newGreens,previous_greens))) < msa_delta) or (check_for_equality(equality))
        previous_greens = greens
        greens = newGreens

        if check_for_equality(equality):
            converged_reason = 'equality'
        else:
            converged_reason = 'no change in greens' 
        
    print('\nThe reason of green time msa convergence: {}'.format(converged_reason))
    return greens,equality

#in here we will calculate the green times according to different policies
#These will be used in the cost function of the static assignment
def equisaturationGreenTimes(caps, flows, initial_greens, ff_tts, method):
    #now calculate the green times iteratively 
    greens,equality = msa_green_times(caps, flows, initial_greens, ff_tts, method)
    print('check if the policy constraint is satisfied: {}\n'.format(equality))
    print('MSA Equisaturation Green Times = {}'.format(greens))
    

     #this is needed to compare the results
    theoreticalGreenTime = theoreticalEquisaturationGreenTimes(caps, flows)
    print('Theoretical Equisaturation Green Times = {}\n'.format(theoreticalGreenTime))

    return greens

#finding the theoretical equisaturation green times
def theoreticalEquisaturationGreenTimes(caps, flows):
    zero_flow = []
    pop = 0
    change = 0
    #check for flows = 0 (green time always 0)
    for i in range(len(flows)):
        if flows[i-pop] == 0:
            flows.pop(i-pop)
            zero_flow.append(i)
            pop +=1
            change += 0.01
    
    #check if there are still more than one links with flows
    if len(flows) == 1:
        g_times = [1-change]
    else:
        #solving a linear system of equations 
            #for al links per intersection xi/(si*gi) needs to be equal to 
            #sum of g's needs to be 1
        left_side = []
        right_side = []
        last_term = [1]
        for i in range(len(caps)-1):
            left_side.append([(caps[i]/flows[i]),-(caps[i+1]/flows[i+1])])
            right_side.append(0)
            last_term.append(1)
        left_side.append(last_term)
        right_side.append((1-change))

        g_times = np.linalg.solve(left_side,right_side)
    #add the zeros where the flow is zero
    for i in range(len(zero_flow)):
        g_times.insert(zero_flow[i],0.01)
    return g_times

def P0policyGreenTimes(caps, flows, initial_greens, ff_tts, method):

    #now calculate the green times iteratively 
    greens,equality = msa_green_times(caps, flows, initial_greens, ff_tts, method)
    print('check if the policy constraint is satisfied: {}\n'.format(equality))
    print('MSA P0 Green Times = {}'.format(greens))
    

    #this is needed to compare the results
    theoreticalGreenTime = theoreticalP0Greens(caps, flows, ff_tts)
    print('Theoretical P0 Green Times = {}\n'.format(theoreticalGreenTime))
    return greens

#finding the theoretical P0 green times
def theoreticalP0Greens(caps, flows, ff_tts):
    #to make sure no dividing by zero is done
    zero_flow = []
    pop = 0
    change = 0
    #check for flows = 0 (green time always 0.01 -> for safety)
    for i in range(len(flows)):
        if flows[i-pop] == 0:
            flows.pop(i-pop)
            zero_flow.append(i)
            pop +=1
            change += 0.01
    
    #check if there are still more than one links with flows
    if len(flows) == 1:
        g_times = [1-change]
    else:
        #solving a linear system of equations 
                #for al links per intersection si*di needs to be equal to 
                #sum of g's needs to be 1
        left_side = []
        right_side = []
        last_term = [1]
        for i in range(len(caps)-1):
            left_side.append([pow(ff_tts[i]*caps[i],bpr_b)*(caps[i]/flows[i]), - pow(ff_tts[i+1]*caps[i+1],bpr_b)*(caps[i+1]/flows[i+1])])
            right_side.append(0)
            last_term.append(1)
        left_side.append(last_term)
        right_side.append((1-change))
        g_times = np.linalg.solve(left_side,right_side)
    #add the zeros where the flow is zero
    for i in range(len(zero_flow)):
        g_times.insert(zero_flow[i],0.01)

    return g_times

def get_link_delay(flow, cap,  ff_tt, g_time):
    return ff_tt * bpr_a * (flow/(cap*g_time))**bpr_b