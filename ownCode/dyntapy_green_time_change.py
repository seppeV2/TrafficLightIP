from numba import objmode
import numpy as np

from dyntapy.demand import InternalStaticDemand
from dyntapy.settings import parameters
from dyntapy.sta.gap import gap
from dyntapy.sta.utilities import aon
from dyntapy.supply import Network
from dyntapy.results import StaticResult, get_skim
from dyntapy._context import iteration_states
from dyntapy.assignments import StaticAssignment

from cost_functions import __bpr_green_cost, __webster_two_term_green

from dyntapy.graph_utils import (
    dijkstra_all,
    pred_to_paths,
)

import numpy as np
import dyntapy._context
from dyntapy.results import StaticResult, get_skim, DynamicResult
from dyntapy.sta.utilities import aon

gap_definition = "relative gap"
msa_max_iterations = parameters.static_assignment.msa_max_iterations
msa_delta = 10**-4

class GreenStaticAssignment(StaticAssignment):

    def run_greens(self, methodAl, greenTimes , method, store_iterations=False, previous_flow=False, **kwargs):
       
        dyntapy._context.running_assignment = (
            self  # making the current assignment available as global var
        )
        # assignment needs to return at least link_cost and flows, ideally also
        # multi-commodity (origin, destination or origin-destination)

        if methodAl == "msa":
            costs, flows, gap_definition, gap, free_flow = msa_green_flow_averaging(
                self.internal_network, self.internal_demand, greenTimes ,method ,store_iterations
            )
            result = StaticResult(
                costs,
                flows,
                self.internal_demand.origins,
                self.internal_demand.destinations,
                skim=get_skim(costs, self.internal_demand, self.internal_network),
                gap_definition=gap_definition,
                gap=gap,
            )
       
        else:
            raise NotImplementedError(f"{method=} is not defined ")
        if not store_iterations:
            return result, free_flow
        else:
            return result, free_flow,dyntapy._context.iteration_states


def msa_green_flow_averaging(
    network: Network, demand: InternalStaticDemand, greenTimesDic: dict , method: str ,store_iterations=False, 
):
    gaps = []
    converged = False
    k = int(0)
    f1 = np.zeros(network.tot_links)
    f2 = f1.copy()
    
    ff_tt = network.links.length/network.links.free_speed
    greenTimes = list(greenTimesDic.values())
    while not converged:
        k = k + 1
        if k == 1:
            if method == 'bpr':
                costs = __bpr_green_cost(
                    capacities=network.links.capacity,
                    ff_tts=ff_tt,
                    flows=f2,
                    g_times = greenTimes,
                    tot_links = network.tot_links
                )
            elif method == 'WebsterTwoTerm':
                costs = __webster_two_term_green(
                    capacities=network.links.capacity,
                    ff_tts=ff_tt,
                    flows=f2,
                    g_times = greenTimes,
                    tot_links = network.tot_links
                )
        else:
            if method == 'bpr':
                costs = __bpr_green_cost(
                    capacities=network.links.capacity,
                    ff_tts=ff_tt,
                    flows=f2,
                    g_times = greenTimes,
                    tot_links = network.tot_links
                )
            elif method == 'WebsterTwoTerm':
                costs = __webster_two_term_green(
                    capacities=network.links.capacity,
                    ff_tts=ff_tt,
                    flows=f2,
                    g_times = greenTimes,
                    tot_links = network.tot_links
                )
        ssp_costs, f2 = aon(demand, costs, network)

        if k == 1:
            converged = False
            last_gap = 10
            gaps.append(last_gap)

        else:
            f2 = 1 / k * f2 + (k - 1) / k * f1
            current_gap = gap(f1, costs, demand.to_destinations.values, ssp_costs)
            
            converged = current_gap < msa_delta or k == msa_max_iterations


            #to check in terminal if the msa converged or was ended by max iterations
            if converged == True: 
                if current_gap < msa_delta: 
                    print('MSA step: really converged')

                else: 
                    print('MSA step: max iteration reached')
            gaps.append(current_gap)
            if current_gap < last_gap:
                best_flow_vector = f1
                best_costs = costs
                last_gap = current_gap 

        f1 = f2.copy()
        if store_iterations:
            # lists cannot be passed to object mode
            arr_gap = np.zeros(len(gaps))
            for idx, val in enumerate(gaps):
                arr_gap[idx] = val
            with objmode:
                result = StaticResult(
                    costs,
                    f1,
                    demand.origins,
                    demand.destinations,
                    skim=get_skim(costs, demand, network),
                    gap_definition=gap_definition,
                    gap=np.ndarray(arr_gap),
                )
                iteration_states.append(result)
        
    return best_costs, best_flow_vector, gap_definition, gaps, ff_tt

def aon_adjusted(demand: InternalStaticDemand, costs, network: Network):
    out_links = network.nodes.out_links
    flows = np.zeros(len(costs))
    number_of_od_pairs = 0
    for i in demand.to_destinations.get_nnz_rows():
        number_of_od_pairs += demand.to_destinations.get_nnz(i).size
    ssp_costs = np.zeros(number_of_od_pairs)
    counter = 0
    for i in demand.to_destinations.get_nnz_rows():
        destinations = demand.to_destinations.get_nnz(i)
        demands = demand.to_destinations.get_row(i)
        distances, pred = dijkstra_all(
            costs, out_links, source=i, is_centroid=network.nodes.is_centroid
        )
        
        path_costs = np.empty(destinations.size, dtype=np.float32)
        for idx, dest in enumerate(destinations):
            path_costs[idx] = distances[dest]
            # TODO: Check for correctness
        paths = pred_to_paths(pred, i, destinations, out_links)

        for path, path_flow, path_cost in zip(paths, demands, path_costs):
            ssp_costs[counter] = path_cost
            counter += 1
            for link_id in path:
                flows[link_id] += path_flow

    return ssp_costs, flows 