#in here we will calculate the green times according to different policies
#These will be used in the cost function of the static assignment


def websterGreenTimes(caps,flows):
    if 0 == all(flows):
        return flows
        #L=0 assumption for now
    else:
        L = 0
        y = [i / j for i, j in zip(flows, caps)]
        ytot = sum(y)
        c0 = (1.5*L+5)/(1-ytot)
        coef = (c0-L)/ytot
        g_times = []
        for i in range(len(y)):
            g_times.append(coef*y[i])
        return g_times


def P0policyGreenTimes():
    return

def otherPolicy():
    return