import numpy as np


#in here we will calculate the green times according to different policies
#These will be used in the cost function of the static assignment


def websterGreenTimes(caps, flows):
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
    
    #check for not to small green times
    
    print('greens times in webster loop= '+str(g_times))
    return g_times


def P0policyGreenTimes(caps, flows):
    #solving a linear system of equations 
            #for al links per intersection si*di needs to be equal to 
            #sum of g's needs to be 1
    left_side = []
    right_side = []
    last_term = [1]
    for i in range(len(caps)-1):
        left_side.append([1,-1])
        right_side.append((flows[i]/caps[i])-(flows[i+1]/caps[i+1]))
        last_term.append(1)
    left_side.append(last_term)
    right_side.append((1))
    g_times = np.linalg.solve(left_side,right_side)
    return g_times

def otherPolicy():
    return