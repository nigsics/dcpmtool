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


import networkx as nx


from collections import defaultdict
import math
from copy import deepcopy
import logging

from widest_path import Dijkstra_widest
from widest_path import Dijkstra_widest_dst
from widest_path import Dijkstra_weight

import itertools as itt
import time

logger = logging.getLogger(__name__)


# generate a test case #

def genGraph(col, row, capacity = 10):
    G= nx.grid_2d_graph(col, row, create_using=nx.DiGraph())
    G = nx.convert_node_labels_to_integers(G)
    index = 0
    for nd, nb in G.edges(data = False):
        G[nd][nb]['capacity'] = capacity
        #G[nd][nb]['flows'] = []
        G[nd][nb]['weight'] = 1
        G[nd][nb]['index'] = index

        index +=1
    #plt.figure(figsize=(8,8))
    nx.draw(G, node_size=2000, with_labels=True)
    #plt.savefig("../fig/mesh_test"+".png")

    #print G.edges(data=True)
    return G



def genFlows_with_ctrl(G, c):

    print "c : {}".format(c)

    num_ctrl = len(c)


    cf = list (itt.combinations (c, 2))
    print "cf: {}".format(cf)
    print "cf : len {}".format(len(cf))

    flows = []
    for (s, t) in cf:
        f = [(s,t), 10]
        flows.append(f)
        f = [(t,s), 10]
        flows.append(f)

    idx = 0
    for s in G.nodes():
        if s not in c:
            f = [ (s, c[idx % num_ctrl]), 2.5]

            flows.append(f)
            f = [ (c[idx % num_ctrl], s), 2.5]
            flows.append(f)

        idx +=1

    return flows

##################################################################################################
# the routability test algorithm #

class Linear_routing ():
    def __init__(self, graph, s,  **kwargs):
        self.G = graph
        self.flows = None
        #self.Kshortest = K
        self.preComputedPaths = None
        self.flows_dict = defaultdict (dict)
        self.flows_dict_routed = defaultdict (dict)

        self.reset_Delta_And_Co(s)

        self.scale = 1

        self.accuracy_level = 0

        self.s = s
        self.dist_cap_mt_src = {}
        self.dist_cap_mt_dst = {}
        self.calc_dist_map()

    def calc_dist_map (self):
        G = self.G
        for src in G.nodes():
            width_all, p_all = Dijkstra_widest(G, src)
            self.dist_cap_mt_src[src] = (width_all, p_all)


        for dst in G.nodes():
            width_all, p_all = Dijkstra_widest_dst(G, dst)

            self.dist_cap_mt_dst[dst] = (width_all, p_all)


    def initiate_run(self, flows):
        self.flows = flows
        self.flows_dict = defaultdict (dict)
        self.flows_dict_routed = defaultdict (dict)
        self.flows_dict_tp= defaultdict (dict)

        num_flows =0

        for (src, dst), demand in flows:
            if src in self.flows_dict and dst in self.flows_dict[src]:
                self.flows_dict[src][dst] += demand
                self.flows_dict_tp[dst][src] += demand


            else:
                self.flows_dict[src][dst] = demand
                self.flows_dict_tp[dst][src] = demand
                num_flows+=1


            self.flows_dict_routed[src][dst]  = 0.0
        self.num_flows = num_flows

        #print self.flows_dict
        #print self.flows_dict_tp

    def reset_Delta_And_Co (self, s):
        m = self.G.number_of_edges()
        delta = ( 1/ ( (1+s)**( (1-s)/s) ) )  * ( ( (1-s)/m   ) ** (1/s) )

        self.delta = delta
        self.co  = math.log( (1+s)/delta, (1+s) )
        self.Tmax =  2*self.co

    def preCompute_KShortest(self):
        logger.debug("psedu code")
        pass


    def re_weight_edges(self, G, nd, nb, w):
        G[nd][nb]['dweight'] = w

    def calcDL (self, G):
        summ = 0.0
        for nd, nb in G.edges(data = False):
             cap = G[nd][nb]['capacity']
             l =  G [nd][nb]['dweight']
             summ += cap*l

        return summ

    def resetScale(self):
        self.scale = 1

    def reset_accuracy (self, a):
        self.accuracy_level=a



    def auto_scale_run(self, lowbound, highbound):
        low = lowbound
        high = highbound
        if self.s <= 0.1:
            scale = (low+high)/2.0
        else:
            scale  = high/2.0
        self.scale =  scale


        while (1):

            beta, lamga = self.main(self.scale, self.controllers)
            #print "{}, {}, {}".format (beta, lamga, self.scale)

            logger.info("{}, {}, {}".format (beta, lamga, self.scale ) )

            if not beta:
                self.scale = self.scale*2.0

            elif beta and lamga/self.scale <1.0:
                self.scale = self.scale/2.0
            else:
                return beta, lamga



    def est(self, scale, controllers):

        G = self.G.copy()
        self.controllers = controllers


        for nd, nb in G.edges(data = False):
            G [nd][nb]['util'] =0

        flows_dict = self.flows_dict
        flows_dict_tp = self.flows_dict_tp
        #print flows_dict
        #print flows_dict_tp

        edge_util = {}

        ifCapRatio_src = {}
        ifCapRatio_dst = {}
        max_single = {}

        for src in controllers:
            f_dsts = flows_dict[src].keys()
            d_src_i = deepcopy(flows_dict[src])
            (width_all, p_all) = self.dist_cap_mt_src[src]

            c = 0
            for n in G.neighbors(src):
                c += G[src][n]['capacity']
            d = 0
            for dst in f_dsts:

                p = p_all[dst]
                demand = d_src_i[dst]
                max_single[(src , dst)] = width_all[dst]/demand

                d += demand

                for i in range(1, len(p)):

                    cap = float (G[p[i-1]][p[i]]['capacity'])


                    edge_util[ (p[i-1], p[i])] =edge_util.get((p[i-1], p[i]), 0)+demand/cap

            ifCapRatio_src[src] = c/d

        for dst in controllers:

            f_srcs = flows_dict_tp[dst].keys()
            d_dst_i = deepcopy(flows_dict_tp[dst])

            #print d_dst_i

            (width_all, p_all) = self.dist_cap_mt_src[dst]

            c =0

            for n in G.predecessors(dst):
                c += G[n][dst]['capacity']


            d = 0
            for src in f_srcs:

                demand = d_dst_i[src]
                max_single[(src , dst)] = width_all[src]/demand
                d += demand


                if src not in controllers:
                    p = p_all[src]
                    for i in range(1, len(p)):

                        cap = float (G[p[i-1]][p[i]]['capacity'])
                        edge_util[ (p[i-1], p[i])] =edge_util.get((p[i-1], p[i]), 0)+demand/cap

            ifCapRatio_dst[dst] = c/d


        #print edge_util

        hb = min (max_single.values())

        #print hb, self.num_flows

        hr = min (ifCapRatio_src.values()+ifCapRatio_dst.values() )


        sigma =  max(edge_util.values())

        logger.debug ( "sigma is {}".format(sigma) )

        m = G.number_of_edges()

        lowbound = max(1/sigma, hb/self.num_flows)


        highbound = min (m*hb, hr)

        logger.debug ( " {}, {}".format(lowbound, highbound) )

        return [lowbound, highbound]


    def src_iter(self, DL, G, d_src_i, f_dsts, s, src, d_dst_i, f_srcs, dsti, controllers, dist_mode):
        #print src, dist_mode
        while (DL < 1):
            edge_util = {}
            # all_edges = []
            routes_src_i = {}
            width, p_all = Dijkstra_weight(G, src, dst_mode=False, w='dweight')


            for dst in f_dsts:

                if d_src_i[dst] > 0:
                    p = p_all[dst]
                    #print (nx.shortest_path_length(G,source=src,target=dst ,weight='dweight'))

                    #p = nx.shortest_path(G, source=src, target=dst, weight='dweight')
                    routes_src_i[dst] = p
                    #cap_min_src_i[dst] = 1000
                    #print p
                    for i in range(1, len(p)):
                        cap = float(G[p[i - 1]][p[i]]['capacity'])
                        edge_util[(p[i - 1], p[i])] = edge_util.get((p[i - 1], p[i]), 0) + d_src_i[dst] / cap

            # if not edge_util:
            #     break
            if f_srcs:
                width, p_all = Dijkstra_weight(G, dsti, dst_mode=True, w='dweight')
            # print dsti
            # print p_all
            #print dist_mode


            for sr in f_srcs:

                #if sr not in controllers and d_dst_i[sr] > 0:
                if d_dst_i[sr] > 0:
                    p = p_all[sr]
                    #print (nx.shortest_path_length(G,source=src,target=dst ,weight='dweight'))

                    #p = nx.shortest_path(G, source=src, target=dst, weight='dweight')
                    #routes_src_i[dst] = p
                    #cap_min_src_i[dst] = 1000
                    #print p
                    for i in range(1, len(p)):
                        cap = float(G[p[i - 1]][p[i]]['capacity'])
                        edge_util[(p[i - 1], p[i])] = edge_util.get((p[i - 1], p[i]), 0) + d_dst_i[sr] / cap

            if not edge_util:
                break




            #print "edge util halfway is {}".format(edge_util)
            sigma = float(max(1.0, max(edge_util.values())))


            for dst in f_dsts:
                if d_src_i[dst] > 0:
                    # _fsd = min (d_src_i[dst],  cap_min_src_i[dst])

                    fsd = d_src_i[dst] / sigma
                    #print d_src_i[dst], sigma
                    d_src_i[dst] = d_src_i[dst] - fsd


                    self.flows_dict_routed[src][dst] += fsd
                    # else:
                    #     self.flows_dict_routed[dst][src] += fsd
            for sr in f_srcs:
                #if d_dst_i[sr] > 0 and sr not in controllers:
                if d_dst_i[sr] > 0:
                    # _fsd = min (d_src_i[dst],  cap_min_src_i[dst])

                    fsd = d_dst_i[sr] / sigma
                    #print d_dst_i[sr], sigma
                    d_dst_i[sr] = d_dst_i[sr] - fsd

                    self.flows_dict_routed[sr][dsti] += fsd







            for (nd, nb) in edge_util.keys():

                t = edge_util[(nd, nb)] / sigma
                edge_util[(nd, nb)] = t
                #print

                G[nd][nb]['dweight'] = G[nd][nb]['dweight'] * (1 + s * (t) )

                G[nd][nb]['util'] += edge_util[(nd, nb)]

            DL = self.calcDL(G)


        return DL




    def main(self, scale, controllers):
        delta = self.delta
        s = self.s
        #print "delta is {}".format(delta)
        DL = 0
        G = self.G.copy()

        for nd, nb in G.edges(data = False):

            cap = G[nd][nb]['capacity']
            l = delta/cap
            G [nd][nb]['dweight'] = l

            #print  "edge nd {}, nb {} w {} ".format(nd, nb,  G[nd][nb]['dweight'])
            #rou [(nd, nb)] = 0
            G [nd][nb]['util'] =0


        flows_dict = deepcopy(self.flows_dict)
        flows_dict_tp = deepcopy (self.flows_dict_tp)

        for src in flows_dict:
            for dst in flows_dict[src]:
                flows_dict[src][dst] *= scale
                self.flows_dict_routed[src][dst]  = 0.0
                if src not in controllers:
                    flows_dict_tp[dst][src] *= scale
                else:
                    flows_dict_tp[dst].pop(src, None)




        T = 0
        while (DL < 1):
            T+=1
            if T > self.Tmax:
                return False, 0


            for src in controllers:
                f_dsts = flows_dict[src].keys()
                d_src_i = deepcopy(flows_dict[src])                      # it will be slow here

                dsti = src
                f_srcs = flows_dict_tp[dsti].keys()
                d_dst_i = deepcopy(flows_dict_tp[dsti])

                DL = self.src_iter(DL, G, d_src_i, f_dsts, s, src, d_dst_i, f_srcs, dsti, controllers, False)

        lamga_list = []
        co = self.co





        for src in flows_dict.keys():
             for dst in flows_dict[src].keys():
                demand = flows_dict[src][dst]

                #print self.flows_dict_routed[src][dst] / demand
                xp = self.flows_dict_routed[src][dst] / co
                #xp = self.flows_dict_routed[src][dst]
                #print " flow {} {}, share {}".format(src, dst, xp/demand)

                lamga_list.append ( xp/demand )
                #self.flows_dict_routed[src][dst] = 0.0

        #print lamga_list
        lamga = min (lamga_list)*scale

        #print lamga, scale

        return True, lamga



if __name__ == '__main__':
    G= genGraph(8, 8, 50.0)

    c = [18, 42, 0, 59, 26, 48, 16, 10]
    flows = genFlows_with_ctrl(G, c)
    #print flows
    rt = Linear_routing (G, 0.1)
    rt.preCompute_KShortest()
    print rt.preComputedPaths
    rt.initiate_run(flows)
    low, high =rt.est(1.0, c)
    start_time = time.time()
    T, lamga=rt.auto_scale_run(low, high)
    end_time = time.time()

    print low, high

    print T, lamga
    print end_time - start_time
