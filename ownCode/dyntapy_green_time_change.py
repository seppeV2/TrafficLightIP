from numba import objmode, njit
import numpy as np

from dyntapy.demand import InternalStaticDemand
from dyntapy.settings import parameters
from dyntapy.sta.gap import gap
from dyntapy.sta.utilities import aon
from dyntapy.supply import Network
from dyntapy.results import StaticResult, get_skim
from dyntapy._context import iteration_states
from dyntapy.assignments import StaticAssignment

from ownFunctions import __bpr_green_cost
from greenTimes import websterGreenTimes

import networkx
import numpy as np

import dyntapy._context
from dyntapy.demand import (
    InternalDynamicDemand,
    build_internal_static_demand,
    build_internal_dynamic_demand,
)
from dyntapy.demand_data import _check_centroid_connectivity
from dyntapy.dta.i_ltm_aon import i_ltm_aon
from dyntapy.dta.incremental_assignment import incremental
from dyntapy.sta.dial_stochastic_assignment import dial_sue
from dyntapy.sta.dial_b import dial_b
from dyntapy.sta.msa import msa_flow_averaging
from dyntapy.sta.uncongested_dial import sun
from dyntapy.supply_data import build_network
from dyntapy.utilities import log
from dyntapy.results import StaticResult, get_skim, DynamicResult
from dyntapy.sta.utilities import aon, __bpr_cost

gap_definition = "relative gap"
msa_max_iterations = parameters.static_assignment.msa_max_iterations
msa_delta = parameters.static_assignment.msa_delta

class GreenStaticAssignment(StaticAssignment):

    def run(self, method, store_iterations=False, **kwargs):
       
        dyntapy._context.running_assignment = (
            self  # making the current assignment available as global var
        )
        # assignment needs to return at least link_cost and flows, ideally also
        # multi-commodity (origin, destination or origin-destination)
        if method == "dial_b":
            costs, origin_flows, gap_definition, gap = dial_b(
                self.internal_network, self.internal_demand, store_iterations
            )
            flows = np.sum(origin_flows, axis=0)
            result = StaticResult(
                costs,
                flows,
                self.internal_demand.origins,
                self.internal_demand.destinations,
                skim=get_skim(costs, self.internal_demand, self.internal_network),
                gap_definition=gap_definition,
                gap=gap,
                origin_flows=origin_flows,
            )
        elif method == "msa":
            costs, flows, gap_definition, gap = msa_green_flow_averaging(
                self.internal_network, self.internal_demand, store_iterations
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
        elif method == "sun":
            assert not store_iterations
            # no iterations in uncongested assignments
            costs, flows, origin_flows = sun(
                self.internal_network, self.internal_demand
            )
            result = StaticResult(
                costs,
                flows,
                self.internal_demand.origins,
                self.internal_demand.destinations,
                skim=get_skim(costs, self.internal_demand, self.internal_network),
                origin_flows=origin_flows,
            )
        elif method == "sue":
            assert not store_iterations  # not supported for SUE yet
            # check for turn connectors, they are required since this algorithm
            # is defined on the line graph
            assert _turn_connectors(self.internal_network)
            costs, flows, destination_flows = dial_sue(
                network=self.internal_network, demand=self.internal_demand, **kwargs
            )
            result = StaticResult(
                costs,
                flows,
                self.internal_demand.origins,
                self.internal_demand.destinations,
                skim=get_skim(costs, self.internal_demand, self.internal_network),
                destination_flows=destination_flows,
            )

        else:
            raise NotImplementedError(f"{method=} is not defined ")
        if not store_iterations:
            return result
        else:
            return result, dyntapy._context.iteration_states


def msa_green_flow_averaging(
    network: Network, demand: InternalStaticDemand, store_iterations=False
):
    gaps = []
    converged = False
    k = int(0)
    f1 = np.zeros(network.tot_links)
    f2 = f1.copy()
    ff_tt = network.links.length / network.links.free_speed
    while not converged:
        k = k + 1
        if k == 1:
            print(websterGreenTimes(network.links.capacity,ff_tt,f2))
            costs = __bpr_cost(
                capacities=network.links.capacity,
                ff_tts=ff_tt,
                flows=f2,
                #g_times = websterGreenTimes(network.links.capacity,ff_tt,f2),
            )
        else:
            print(websterGreenTimes(network.links.capacity,ff_tt,f2))
            costs = __bpr_cost(
                capacities=network.links.capacity,
                ff_tts=ff_tt,
                flows=f2,
                #g_times = websterGreenTimes(network.links.capacity,ff_tt,f2),
            )
        ssp_costs, f2 = aon(demand, costs, network)
        # print("done")
        if k == 1:
            converged = False
            last_gap = 1
            gaps.append(last_gap)

        else:
            f2 = 1 / k * f2 + (k - 1) / k * f1
            current_gap = gap(f1, costs, demand.to_destinations.values, ssp_costs)
            converged = current_gap < msa_delta or k == msa_max_iterations
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
    return best_costs, best_flow_vector, gap_definition, gaps