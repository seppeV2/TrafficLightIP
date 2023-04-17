import numpy as np

costs = [0.8,0.2,0.3]
flows = [20,20,80]

veh_hour = sum([cost*flow for cost, flow in zip(costs, flows)])
print(veh_hour)


