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

import networkx as nx


from approx_linear_routing_faster import Linear_routing

from copy import deepcopy

import gen_graph as gg

import logging
import logging.config

import time
import ConfigParser


config_file = 'run.config'

config_parser = ConfigParser.ConfigParser()


logger = logging.getLogger(__name__)


class Anealing_Clustering_Routing_Problem( object):
    def __init__(self, graph, distance_matrix, seed = 500000):
        self.graph = deepcopy(graph)

        self.controllers = None

        self.I = [ -1 for _ in range (self.graph.number_of_nodes() )]           # for current node-controller map
        self.c = [ [] for _ in range (self.graph.number_of_nodes() )]           # for current controller-nodes map
        #self.flows = []
        self.distance_matrix = distance_matrix

        self.rt = Linear_routing (self.graph,  0.1)
        self.rnd = random.Random()
        self.rnd.seed(seed)

        config_parser.read(config_file)

        self.T_rel =  config_parser.getfloat('TRAFFIC_PARAMS', 'T_rel')
        self.T_req =  config_parser.getfloat('TRAFFIC_PARAMS', 'T_req')
        self.T_state =  config_parser.getfloat('TRAFFIC_PARAMS', 'T_state')



        #self.rt.preCompute_KShortest()

    def _reset (self):

        self.controllers = None

        self.I = [ -1 for _ in range (self.graph.number_of_nodes() )]           # for current node-controller map
        self.c = [ [] for _ in range (self.graph.number_of_nodes() )]           # for current controller-nodes map
        #self.flows = []



    def gen_init_clustering (self):
        G= self.graph
        for i in G.nodes():
            d = {}
            for ci in self.controllers:
                d[ci] = self.distance_matrix[i][ci]

            cmin = min (d, key=d.get)
            #print cmin
            self.I[i] = cmin

            self.c[cmin].append(i)


    def gen_next_clustering(self):
        I = deepcopy(self.I)
        c = deepcopy(self.c)
        rest_nodes = []
        chosen_one = None



        while(1):
            chosen_one = self.rnd.choice(self.controllers)
            logger.info( "chosen one is {}, c {}, len {}".format(chosen_one, self.controllers, len(self.c[chosen_one])) )
            rest_nodes = list(set(self.graph.nodes()) - set(self.c[chosen_one]))
            if rest_nodes:
                break
        new_mem = None
        minDist = 10000

        for r in rest_nodes:
            d = self.distance_matrix[chosen_one][r]
            if d < minDist:
                minDist =d

        while(1):
            new_mem = self.rnd.choice(rest_nodes)
            dist = self.distance_matrix[chosen_one][new_mem] - minDist +1

            if  1/float(dist) > self.rnd.random():             # the larger the distance the lower the probability
                break
        ctrl_old = self.I[new_mem]

        I[new_mem] = chosen_one
        c[ctrl_old].remove(new_mem)
        c[chosen_one].append(new_mem)

        sumLen =0
        for ci in self.controllers:
            #logger.info( ci, c[ci], len(c[ci]) )
            sumLen += len(c[ci])

        if sumLen != self.graph.number_of_nodes():
            logger.error( "error")
            exit(1)
        return I, c



    # def model_flows (self, c):
    #     num_c = len (c)
    #     nnodes = self.graph.number_of_nodes()
    #     nlinks = self.graph.number_of_edges()
    #     flows = []
    #
    #     for ci in self.controllers:
    #         #print ci,
    #         ci_total = 10* len (c[ci]) * num_c + 1*(nnodes+nlinks)
    #         ci_each = ci_total/num_c
    #
    #         for cj in self.controllers:
    #            if cj != ci:
    #                f = [(ci, cj), ci_each]
    #                flows.append(f)
    #
    #         for si in c[ci]:
    #            if si!=ci:
    #                f = [(si, ci), 10]
    #                flows.append (f)
    #
    #                f = [(ci, si), 10]
    #                flows.append (f)
    #     return flows

    def model_flows2 (self, c, load_graph):
        #num_c = len (c)
        #nnodes = self.graph.number_of_nodes()
        #nlinks = self.graph.number_of_edges()
        flows = []
        #G = load_graph



        T_rel = self.T_rel      # KByte/s
        T_req = self.T_req      # KByte/s
        T_state = self.T_state      # KByte/s

        c_num_reqs = {}

        for ci in self.controllers:
            #print ci

            for si in c[ci]:
               if si!=ci:
                   f = [(si, ci), T_req * load_graph[si]]
                   flows.append (f)

                   f = [(ci, si), T_rel * load_graph [si]]
                   flows.append (f)
               c_num_reqs [ci] = c_num_reqs.get (ci, 0) + load_graph[si]

        #print c_num_reqs

        for ci in self.controllers:
            for cj in self.controllers:
                if cj != ci:
                       nReq = c_num_reqs.get (ci, 0)
                       if nReq:
                            f = [(ci, cj),nReq * T_state]

                            flows.append(f)
        #print flows

        return flows






    def accept_probability(self, c_old, c_new, T):

        if c_new >= c_old:
            return 1.0+c_new - c_old

        p = math.exp ( (c_new - c_old) / T)

        logger.debug ( " accept prob {}".format(p) )
        return p

    def continue_probability (self, c_old, c_new, T):

        if c_new >= c_old:
            return 1.0+c_new - c_old


        p = math.exp( (c_new - c_old) / T)
        return p

    def gen_service_load (self):
        service_load = {}

        for n in self.graph.nodes():
            service_load[n] = 300

        return service_load

    def gen_service_load_dist (self, fl=500):

        G = self.graph
        service_load = {}
        # random.seed(10000)
        for n, d in G.nodes(data = True):
             service_load[n] = d['load']

        return service_load



    def verify(self, flows):
        self.rt.initiate_run(flows)
        low, high =self.rt.est(1.0, self.controllers)

        r, cost =self.rt.auto_scale_run(low, high)
        return r, cost



    def run_single(self, controllers):
        self._reset()
        self.controllers = controllers
        self.gen_init_clustering()

        #load_graph = self.gen_service_load()
        load_graph = self.gen_service_load_dist()

        flows= self.model_flows2(self.c, load_graph)

        logger.info ( "##########flows generated################")
        #print flows

        #rt = integer_routing (self.graph, flows, 8)

        self.rt.initiate_run(flows)


        low, high =self.rt.est(1.0, self.controllers)

        if high < 0.8:
                    r = True
                    old_cost = (low+high)/2.0
        elif low > 1.5:
                    r = True
                    old_cost = (low+high)/2.0
        else:


            r, old_cost =self.rt.auto_scale_run(low, high)




        logger.debug ("#############initialization finished ")
        best_cost = old_cost

        best_I = self.I
        best_c = self.c
        best_flows = flows


        return old_cost>=1.0, best_I, old_cost



    def anneal_clustering(self, controllers):
        self._reset()
        self.controllers = controllers
        self.gen_init_clustering()

        #load_graph = self.gen_service_load()
        load_graph = self.gen_service_load_dist()

        flows= self.model_flows2(self.c, load_graph)

        logger.info ( "##########flows generated################")
        #print flows

        #rt = integer_routing (self.graph, flows, 8)

        self.rt.initiate_run(flows)


        low, high =self.rt.est(1.0, self.controllers)

        r, old_cost =self.rt.auto_scale_run(low, high)


        logger.debug ("#############initialization finished ")
        best_cost = old_cost

        best_I = self.I
        best_c = self.c
        best_flows = flows


        if r and old_cost >= 1:
            return True, best_I, old_cost
        elif len (self.controllers) ==1:

            return old_cost>=1, best_I, old_cost
        else:
            T = 1.0
            T_min = 0.001
            alpha = 0.90
            self.rt.reset_Delta_And_Co(0.1)
            while T > T_min:
                I, c = self.gen_next_clustering()

                flows = self.model_flows2(c, load_graph)

                self.rt.initiate_run(flows)
                low, high =self.rt.est(1.0, self.controllers)

                if high < 1.0:
                    r = True
                    new_cost = (low+high)/2.0
                elif low > 1.01:
                    r = True
                    new_cost = (low+high)/2.0
                else:


                    r, new_cost = self.rt.auto_scale_run(low, high)

                if r and new_cost >= 1:

                     #r, co= self.verify(flows)
                     # logger.debug( "verify {} {}".format(r, co) )
                     # assert (r)
                     return True, I, new_cost

                else:
               #     print "cost {} new {}".format(old_cost, new_cost)
                    logger.debug ("cost {} new {}".format(old_cost, new_cost) )
                    ap = self.accept_probability(old_cost, new_cost, T)
                    if ap > self.rnd.random():

                        old_cost = new_cost
                        self.I = I
                        self.c = c

                    if new_cost > best_cost:
                        best_cost = new_cost
                        best_I = I
                        best_c = c
                        best_flows = flows

                T = T*alpha

             #   print "current temprature {}".format(T)
                logger.info ("current temprature {}".format(T))

            #r, co= self.verify(best_flows)
            return False, best_I, new_cost


def main():


    G= gg.genGraph_import_graphML('../annotated_topo/Internetmci.graphml', 3000)


    # rnd_sl= gg.randomize_service_load(G, seed = 0)
    #
    # rnd_sl.next()
    #
    # rnd_cap = gg.randomize_cap (G, 6000, seed =1)
    # rnd_cap.next()
    #
    # rt = FTCP_placement (G, 0.9999, 0.9999, 0.9999, 0.9999)
    #
    # for nd, nb in G.edges(data = False):
    #     print G[nd][nb]['capacity']
    #
    # controllers, Rmin = rt.run()

    controllers = [0, 1, 2]



    distance_matrix = nx.all_pairs_shortest_path_length(G)

    AR = Anealing_Clustering_Routing_Problem (G, distance_matrix)

    start_time =  time.time()
    success, cluster, effort = AR.anneal_clustering(controllers)
    end_time = time.time()

    print "time consumed:", end_time -start_time
    print " clustering results "
    print success
    print cluster

    print effort




if __name__ == '__main__':

    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s.%(msecs)03d> %(name)-12s :%(message)s',
    #                     datefmt='%Y-%m-%d <%H:%M:%S',
    #                     # filename='logs/node_[id].log',
    #                     filename=file_nm,
    #                     filemode='w')
    logging.config.fileConfig('logging.config')
    logger = logging.getLogger("approx_linear_routing")

    logger.info("Program started")



    main()





