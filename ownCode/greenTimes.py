#in here we will calculate the green times according to different policies
#These will be used in the cost function of the static assignment


def websterGreenTimes(capacities,ff_tts,flows):
        #L=0 assumption for now
    L = 0
    y = flows/capacities
    ytot = sum(y)
    c0 = (1.5*L+5)/(1-ytot)
    g_times = (y*(c0-L))/ytot
    return g_times


def P0policyGreenTimes():
    return

def otherPolicy():
    return