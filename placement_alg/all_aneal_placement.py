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



import math

import random

from Reliability_calc import Reliability_calc
import networkx as nx

from all_aneal_clustering import Anealing_Clustering_Routing_Problem


from copy import deepcopy

import gen_graph as gg
import math

import numpy as np

import logging
import logging.config

logger = logging.getLogger(__name__)

class Anealing_Placement_Problem(object):

    def __init__(self, graph, seed=500000, **kwargs):
        #super(Placement_Clustering_Routing_Problem, self).__init__(state)
        self.graph = deepcopy(graph)
        self.controllers = []
        self.rt = Reliability_calc (self.graph, 0.999999, 0.9999, 0.9999, 0.9999)
        self.rt.graph_rebuild()
        self.kwargs = kwargs
        self.record = {}

        # seed = seed + self.graph.number_of_nodes()
        # self.rnd = random.Random()
        # self.rnd.seed(seed)

    def gen_init_controller_placement (self):
        G = self.graph

        #self.controllers, Rmin = self.rt.run()

        self.k = int (math.log(G.number_of_nodes(), 2) )
        self.controllers = random.sample (self.graph.nodes(), self.k)


        Rmin, G__ = self.eval_min_Rel (self.controllers)

        return Rmin




    def eval_min_Rel (self, controllers):

        G = self.graph
        G__ = self.rt.graph_rebuild_add_ctrl(controllers)


        Rmin = 1

        for j in G.nodes():
            R, I = self.rt.disjoint_paths_detail(j, G__)
            if R <Rmin:
                Rmin = R
        return Rmin, G__


    def best_record (self):

        Max = -1000000
        maxk = -1
        for k in self.record.keys():
            m = max(self.record[k])
            if m >Max:
                maxk = k
                Max = m

        return maxk, Max

    def add_record (self, k, cost):
        if  k in self.record.keys():
            self.record[k].append(cost)
        else:
            self.record[k] = [cost]


    def decide_next_k (self, current_cost, current_k):
        #p = random.random()

        k = current_k


        best_k, best_cost = self.best_record()

        Delta = 0
        #print best_k, best_cost

        #if current_cost <0:
        if True:
            Tendency = max(self.record[current_k]) - best_cost
            Delta = current_k - best_k

            #print current_k, current_cost, Tendency

            mu = Tendency * Delta

            t = np.random.normal(mu, 1)

            if current_k == self.graph.number_of_nodes():
                k = current_k -1
            elif current_k == 1:
                k = current_k +1


            elif t >0.5:
                k = current_k + 1
            elif t < -0.5:
                k = current_k - 1
            else:
                k = current_k



            logger.info( "tendency T is {}, mu {}, k {}".format(t, mu, k) )
            return k



    def gen_next_controller_placement (self, current_cost):
        G = self.graph
        controllers = deepcopy(self.controllers)

        k  = self.decide_next_k(current_cost, self.k)

        new_one = None
        replaced_one = None

        if k == self.k:

            while (1):
                new_one = random.choice (list(set(self.graph.nodes()) - set(controllers) ))
                replaced_one = random.choice(controllers)

                if new_one != replaced_one:

                    controllers.remove(replaced_one)

                    controllers.append(new_one)
                    break
        elif k < self.k:
            replaced_one = random.choice(controllers)

            controllers.remove(replaced_one)

        else:
            new_one = random.choice ( list(set(self.graph.nodes()) - set(controllers) ) )
            controllers.append(new_one)


        return  k, controllers


    def accept_probability (self, c_old, c_new, T):
        if c_new > c_old:
            return 1.1

        p = math.exp( (c_new - c_old) / T)

        return p

    def continue_probability (self, c_old, c_new, T):
        if c_new > c_old:
            return 1.1
        else:

            p = math.exp( (c_new - c_old) / T)

        return p

    def cost_est (self, Rel, effort):

        if effort >= 1:
            if Rel == 1.0:
                cost = float('inf')
                return cost


            cost = -math.log(1-Rel, 10) /10.0

        else:
            #cost = (1-effort) * math.log(1-Rel, 10)
            cost = effort -1
        return cost



    def anneal_placement(self):
        G = self.graph
        distance_matrix = nx.all_pairs_shortest_path_length(G)

        Rel = self.gen_init_controller_placement()
        AR = Anealing_Clustering_Routing_Problem (G, distance_matrix)

        #print self.controllers

        success, cluster, effort = AR.anneal_clustering(self.controllers)

        logger.info ("#################initialization ####################################################################")
        logger.info("Initialize")

        old_cost = 0

        best_controllers = []
        best_clustering = []

        old_cost = self.cost_est(Rel, effort)

        best_controllers = self.controllers
        best_clustering = cluster
        best_cost = old_cost
        best_rel = Rel
        best_effort = effort

        # print self.k
        # print self.controllers
        # print cluster
        # print Rel
        # print old_cost

        logger.info(" attempt {} {}".format(self.k, self.controllers))
        logger.info(" cluster {}".format(cluster))
        logger.info(" result {} {} {}".format(Rel, effort, old_cost))


        self.add_record(self.k, old_cost)

        T = 1.0
        T_min = 0.001
        alpha = 0.99
        while T > T_min:

            logger.info ("#################current placment temperature is {}####################################################################".format(T))
            logger.info("current placment temperature is {}, k is {}, c".format(T, self.k, self.controllers) )

            k, controllers = self.gen_next_controller_placement(old_cost)
            logger.info("att placment temperature is {}, k is {}, c {}".format(T, k, controllers) )

            Rel, G__ = self.eval_min_Rel(controllers)


            psuedo_new_cost =self.cost_est (Rel, 1.1)

            cp = self.continue_probability(old_cost, psuedo_new_cost, T)
            logger.info("ct prob {}".format(cp))

            if cp <random.random():
                T = T*0.99
                continue

            success, cluster, effort = AR.anneal_clustering(controllers)

            new_cost = self.cost_est (Rel, effort)

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

            if new_cost == float('inf'):
                return best_clustering, best_controllers, best_rel, best_cost, best_effort

            T = T*alpha

        return best_clustering, best_controllers, best_rel, best_cost, best_effort

if __name__ == '__main__':

    logging.config.fileConfig('logging.config')
    logger = logging.getLogger("all_aneal_placement")

    logger.info("Program started")


    G = gg.genGraph_import_graphML('../annotated_topo/Internetmci.graphml', 3000)

    rt = Anealing_Placement_Problem (G)

    best_clustering, best_controllers, best_rel, best_cost, best_effort = rt.anneal_placement()

    #distance_matrix = nx.all_pairs_shortest_path_length(G)

    #AR = Anealing_Clustering_Routing_Problem (G, distance_matrix)


    #success, cluster, effort = AR.anneal_clustering(controllers)

    print " final results "
    print "clustering {}".format(best_clustering)
    print "controllers {}".format(best_controllers)

    print "Log 1-Resilience {}".format(best_rel)
    print"cost {}".format(best_cost)
    print"lambda {}".format(best_effort)


    logger.info(" final results ")
    logger.info("clustering {}".format(best_clustering) )
    logger.info("controllers {}".format(best_controllers) )

    logger.info("Log 1-Resilience {}".format(best_rel) )
    logger.info("cost {}".format(best_cost) )
    logger.info("lambda {}".format(best_effort))