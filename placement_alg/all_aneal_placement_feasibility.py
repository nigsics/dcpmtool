__author__ = 'lsteng'

# Copyright 2018  Shaoteng Liu

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import random

import networkx as nx

from all_aneal_clustering import Anealing_Clustering_Routing_Problem

import gen_graph as gg
import math

import logging
import logging.config

from all_aneal_placement import Anealing_Placement_Problem

from copy import deepcopy

logger = logging.getLogger(__name__)


class Anealing_Placement_Problem_FBL(Anealing_Placement_Problem):
    def __init__(self, graph, **kwargs):
        super(Anealing_Placement_Problem_FBL, self).__init__(graph, **kwargs)

        self.RReq = self.kwargs.get('rreq')

        self.bk_G = deepcopy(self.graph)

        self.distance_matrix = nx.all_pairs_shortest_path_length(self.bk_G)

    def gen_init_controller_placement(self):
        G = self.graph

        self.rt.set_Rreq(self.RReq)

        self.controllers, Rmin = self.rt.init_plan()

        self.k = len(self.controllers)

        return Rmin


    def cost_est2(self, Rel, effort):
        if Rel >= 1.0:
            cost = min(0, effort - 1)
            return cost
        #print "{0:.17f}".format(self.RReq)
        cost = min(min(0, -(math.log((1 - Rel) / (1 - self.RReq), 10) / 10.0)), min(0, effort - 1))
        return cost


    def adjust_bandwidth(self, sc):
        self.graph = gg.scale_cap(self.bk_G, sc)

    def get_upper(self, scale, best_clustering, best_controllers, best_rel, best_cost, best_effort):

        lower = scale
        upper = scale
        while (best_cost < 0):
            lower = scale
            scale = max(scale * (1.0 / best_effort) + 0.1, scale * 2)

            self.adjust_bandwidth(scale)
            best_clustering, best_controllers, best_rel, best_cost, best_effort = self.anneal_placement()

            if best_cost >= 0:
                upper = scale
                break

            logger.info("get upp fail lower {}, upper {}".format(lower, upper))

            lower = scale
            scale = scale * 2

        return (lower, upper), best_clustering, best_controllers, best_rel, best_cost, best_effort

    def scale_down(self, lower, upper, best_clustering, best_controllers, best_rel, best_cost, best_effort):

        cost = best_cost
        scale = upper

        while (1):
            if upper - lower < 0.1:
                break

            if cost >= 0:
                upper = scale
                scale = (upper + lower) / 2.0

            else:
                lower = scale
                scale = (upper + lower) / 2.0

            logger.info("scale continue lower {}, upper {}".format(lower, upper))
            self.adjust_bandwidth(scale)
            clustering, controllers, rel, cost, effort = self.anneal_placement()

            if cost >= 0:
                best_cost = cost
                best_rel = rel
                best_clustering = clustering
                best_controllers = controllers
                best_effort = effort

        return (lower, upper), scale, best_clustering, best_controllers, best_rel, best_cost, best_effort


    def scale_bdwdith(self):
        best_clustering, best_controllers, best_rel, best_cost, best_effort = self.anneal_placement()

        logger.info(" final results ")
        logger.info("clustering {}".format(best_clustering))
        logger.info("controllers {}".format(best_controllers))

        logger.info("Log 1-Resilience {}".format(best_rel))
        logger.info("cost {}".format(best_cost))
        logger.info("lambda {}".format(best_effort))

        scale = 1.0

        if best_cost < 0:
            (lower, upper), best_clustering, best_controllers, best_rel, best_cost, best_effort = self.get_upper(scale,
                                                                                                                 best_clustering,
                                                                                                                 best_controllers,
                                                                                                                 best_rel,
                                                                                                                 best_cost,
                                                                                                                 best_effort)
        else:
            upper = scale
            lower = 0

        (lower, upper), scale, best_clustering, best_controllers, best_rel, best_cost, best_effort \
            = self.scale_down(lower, upper, best_clustering, best_controllers, best_rel, best_cost, best_effort)

        return (lower, upper), scale, best_clustering, best_controllers, best_rel, best_cost, best_effort


    def get_upper_rel(self, best_clustering, best_controllers, best_rel, cost, best_effort, cur_log_i, ri):

        lower = max(ri, cur_log_i)
        upper = max(ri, cur_log_i)

        best_cost = cost
        while cost >= 0 and upper < 16.0:
            lower = upper
            upper = upper * 2

            if upper >= 16.0:
                upper = 16.0

            ri = upper
            self.RReq = float(1.0 - 10.0 ** (-ri))

            logger.info("scale up lower {}, upper {}, rreq {}, ri {}".format(lower, upper, self.RReq, ri))
            clustering, controllers, rel, cost, effort = self.anneal_placement()

            if best_rel < 1.0:
                cur_log_i = -math.log(1 - best_rel, 10)
            else:
                cur_log_i = 16.0

            if cost >= 0 and rel > best_rel:
                best_cost = cost
                best_rel = rel
                best_clustering = clustering
                best_controllers = controllers
                best_effort = effort

            if cost >= 0 and upper >= 16.0:
                lower = upper
                break

            upper = max(ri, cur_log_i)
            #print ri, cur_log_i, upper

        return (lower, upper), best_clustering, best_controllers, best_rel, best_cost, best_effort

    def scale_rel_down(self, lower, upper, best_clustering, best_controllers, best_rel, best_cost, best_effort):
        cost = best_cost
        ri = upper
        cur_log_i = lower
        #ri = (upper+lower)/2.0
        if best_cost < 0:
            best_rel = -1

        while (1):
            if upper - lower <= 0.25:
                break

            ri = (upper + lower) / 2.0
            # if scale < lower:
            #     scale = (upper-lower)/2.0
            logger.info("scale continue lower {}, upper {}".format(lower, upper))

            self.RReq = float(1.0 - 10.0 ** (-ri))

            clustering, controllers, rel, cost, effort = self.anneal_placement()

            if rel < 1.0:
                cur_log_i = -math.log(1 - rel, 10)
            else:
                cur_log_i = 16.0

            if cost >= 0:
                lower = ri

            else:
                upper = ri
                #ri = (upper+lower)/2.0

            if cost >= 0 and rel > best_rel:
                best_cost = cost
                best_rel = rel
                best_clustering = clustering
                best_controllers = controllers
                best_effort = effort

        return (lower, upper), best_clustering, best_controllers, best_rel, best_cost, best_effort


    def scale_rel(self):
        r_i = 6.0

        self.RReq = float(1.0 - 10.0 ** (-r_i))

        best_clustering, best_controllers, best_rel, best_cost, best_effort = self.anneal_placement()

        cur_log_i = 0
        if best_rel < 1.0:
            cur_log_i = -math.log(1 - best_rel, 10)
        else:
            cur_log_i = 16.0

        if best_cost >= 0:
            #print best_cost
            (lower, upper), best_clustering, best_controllers, best_rel, best_cost, best_effort \
                = self.get_upper_rel(best_clustering, best_controllers, best_rel, best_cost, best_effort, cur_log_i,
                                     r_i)

            if lower >= 16.0 and upper >= 16.0:
                return (lower, upper), best_clustering, best_controllers, 1.0, best_cost, best_effort

        else:
            upper = max(r_i, cur_log_i)
            lower = 0

        print " begin scale lower {} upper {}, cost {}, rel {}".format(lower, upper, best_cost, best_rel)

        (lower, upper), best_clustering, best_controllers, best_rel, best_cost, best_effort \
            = self.scale_rel_down(lower, upper, best_clustering, best_controllers, best_rel, best_cost, best_effort)

        return (lower, upper), best_clustering, best_controllers, best_rel, best_cost, best_effort


    def anneal_placement(self):
        G = self.graph

        Rel = self.gen_init_controller_placement()
        AR = Anealing_Clustering_Routing_Problem(G, self.distance_matrix)

        #print self.controllers

        success, cluster, effort = AR.anneal_clustering(self.controllers)

        #print "#################initialization ####################################################################"
        logger.info("Initialize")

        old_cost = 0

        best_controllers = []
        best_clustering = []

        old_cost = self.cost_est2(Rel, effort)

        best_controllers = self.controllers
        best_clustering = cluster
        best_cost = old_cost
        best_rel = Rel
        best_effort = effort

        logger.info(" attempt {} {}".format(self.k, self.controllers))
        logger.info(" cluster {}".format(cluster))
        logger.info(" result {} {} {}".format(Rel, effort, old_cost))

        self.add_record(self.k, old_cost)

        T = 1.0
        T_min = 0.001
        alpha = 0.95

        if best_cost >= 0:
            return best_clustering, best_controllers, best_rel, best_cost, best_effort

        while T > T_min:


            #print "#################current placment temperature is {}####################################################################".format(T)
            logger.info("current placment temperature is {}, k is {}, c".format(T, self.k, self.controllers))

            k, controllers = self.gen_next_controller_placement(old_cost)
            logger.info("att placment temperature is {}, k is {}, c {}".format(T, k, controllers))

            Rel, G__ = self.eval_min_Rel(controllers)

            psuedo_new_cost = self.cost_est2(Rel, 1.0)
            #
            cp = self.continue_probability(old_cost, psuedo_new_cost, T)
            logger.info("ct prob {} oldcost {}, newcost {}".format(cp, old_cost, psuedo_new_cost))

            if cp < random.random():
                T = T * 0.98
                continue

            success, cluster, effort = AR.anneal_clustering(controllers)

            new_cost = self.cost_est2(Rel, effort)

            logger.info(" attempt {} {}".format(k, controllers))
            logger.info(" cluster {}".format(cluster))
            logger.info(" result {} {} {}".format(Rel, effort, new_cost))
            # print Rel
            # print effort
            # print new_cost

            self.add_record(k, new_cost)

            ap = self.accept_probability(old_cost, new_cost, T)
            logger.debug(" ap prob {}".format(ap))

            if ap > random.random():
                self.k = k
                self.controllers = controllers

                old_cost = new_cost

            if new_cost > best_cost:
                best_cost = new_cost
                best_rel = Rel
                best_clustering = cluster
                best_controllers = controllers
                best_effort = effort

            if best_cost >= 0:
                return best_clustering, best_controllers, best_rel, best_cost, best_effort

            T = T * alpha

        return best_clustering, best_controllers, best_rel, best_cost, best_effort


if __name__ == '__main__':
    logging.config.fileConfig('logging.config')
    logger = logging.getLogger("all_aneal_placement_feasibility")

    logger.info("Program started")
    G = gg.genGraph_import_graphML('../annotated_topo/Internetmci.graphml', 3000)
    # rnd_sl= gg.randomize_service_load(G, seed = 0)
    #
    # rnd_sl.next()
    #
    # rnd_cap = gg.randomize_cap (G, 3000, seed =1)
    # rnd_cap.next()
    #
    # ran_rel = gg.randomize_reliability(G)

    #ran_rel.next()

    param = {}

    param['rreq'] = 0.99999
    rt = Anealing_Placement_Problem_FBL(G, **param)

    (lower, upper), scale, best_clustering, best_controllers, best_rel, best_cost, best_effort = rt.scale_bdwdith()

    logger.info("lower {}, upper {}, scale {}".format(lower, upper, scale))

    logger.info(" final results ")
    logger.info("clustering {}".format(best_clustering))
    logger.info("controllers {}".format(best_controllers))

    logger.info("Log 1-Resilience {}".format(best_rel))
    logger.info("cost {}".format(best_cost))
    logger.info("lambda {}".format(best_effort))