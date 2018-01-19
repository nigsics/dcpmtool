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

import gen_graph as gg

from copy import deepcopy
import math
import random

import matplotlib.pyplot as plt



class Reliability_calc ():

    def __init__(self, graph,  rReq, rctrl, rnode, rlink):

        self.G = deepcopy(graph)
        self.RREQ = rReq
        self.RCTRL = rctrl
        self.RNODE = rnode
        self.RLINK = rlink
        self._G = None
        self.Si = {}
        self.rankSi = []
        self.I =  [ [] ]

        self.tau = 5

    def set_Rreq(self, rreq):
        self.RREQ = rreq

    def init_plan (self):

        G= self.G
        for i in G.nodes():
            self.Si[i] = sum ([G.degree(k) for k in G.neighbors(i)])
        self.rankSi = sorted(self.Si.items(), key=lambda x: (-x[1], x[0]))
        self.I = [[] for _ in range (self.G.number_of_nodes() )]

        self.graph_rebuild()
        Rel = 1.0
        for j in G.nodes():
            for (s, r) in self.rankSi:
                self.I[j].append(s)

                G__ =self.graph_rebuild_add_ctrl(self.I[j])

                R, Ij = self.disjoint_paths_detail(j, G__)

                if R >self.RREQ:
                    self.I[j] = Ij
                    #print R, j, Ij
                    if R <Rel:
                        Rel = R
                    break
            for i in self.I[j]:
                self.Si[i] =self.tau *self.Si[i]
            self.rankSi = sorted(self.Si.items(), key=lambda x: (-x[1], x[0]))

        I = []

        for Ij in self.I:
            #print Ij
            I=list(set(I).union(Ij))

        Rmin = self.eval_min_Rel(I)

        return I, Rmin


    def init_plan2 (self):
        G = self.G


        self.k = int (math.log(G.number_of_nodes(), 2) )
        self.controllers = random.sample (G.nodes(), self.k)


        Rmin = self.eval_min_Rel (self.controllers)

        return Rmin



    def graph_rebuild (self):

        G = self.G.copy()
        Num_nodes = G.number_of_nodes()
        assert (Num_nodes <1000)
        for n in G.nodes():
            _n = n + 1000
            G.add_node(_n)
            G.node[_n]['ctrl_rel'] = G.node[n]['ctrl_rel']
            #G.node[_n]['ctrl_rel']  = G.node[_n]['ctrl_rel']
            #G.node[_n]['ctrl_link'] = G.node[_n]['ctrl_link']

            for p in G.successors(n):
                link_rel = G[n][p]['reliability']
                G.remove_edge (n, p )

                G.add_edge (_n, p, pr='L', capacity= 1)
                G[_n][p]['reliability'] = link_rel
            G.add_edge(n, _n, pr='N', capacity= 10000)
            G[n][_n]['reliability'] = G.node[n]['reliability']


        G.add_node('T')



        self._G = G.copy()



    def graph_rebuild_add_ctrl(self, I):
        G = self._G.copy()

        for c in I:
            _n = c+1000
            _c = c+2000
            G.add_node(_c)
            G.add_edge(_n, _c, capacity = 10000)
            G.node[_c]['ctrl_rel'] = G.node[_n]['ctrl_rel']
            G.add_edge(_c, 'T', capacity = 10000)

        return G

    def disjoint_paths(self, s, G):
        s = s+1000
        flow_value, flow_dict = nx.maximum_flow(G, s, 'T')

        #print flow_value, flow_dict
        d = flow_dict
        G_ = nx.DiGraph()
        for key, value in d.iteritems():
            for key2, value2 in value.iteritems():
                if value2:
                    #print key, key2, value2

                    G_.add_edge(key, key2)


        #O = []
        Ij = G_.predecessors('T')

        O = [ [] for _ in range(len(Ij)) ]

        F = []

        i = 0
        for c in Ij:

            for path in nx.all_simple_paths(G_, s, c):
                k = len(path)-2
                assert (k%2==0)
                #if k >0:
                hop = k/2
                # Oi is the individual failure probability
                Oi = 1.0 - (self.RNODE*self.RLINK) ** hop
                # else:
                #     Oi = self.RCTRL

                #print k, path, Oi
                O[i].append(Oi)


            #Fi = reduce(lambda x, y: x*y, O[i]) * self.RLINK*self.RCTRL+ 1- self.RLINK*self.RCTRL
            Fi = reduce(lambda x, y: x*y, O[i]) * self.RCTRL+ 1- self.RCTRL
            F.append(Fi)

            i+= 1
        R = 1 - reduce(lambda x, y: x*y, F)
        #nx.predecessor()
        #Ij = []
        #if R >self.RREQ:

        return R, [i-2000 for i in Ij]
        # else:
        #     return R, Ij

    def eval_min_Rel (self, controllers):

        G = self.G
        G__ = self.graph_rebuild_add_ctrl(controllers)


        Rmin = 1

        for j in G.nodes():
            R, I = self.disjoint_paths_detail(j, G__)
            if R <Rmin:
                Rmin = R
        return Rmin

    def disjoint_paths_detail(self, s, G):
        s = s+1000
        flow_value, flow_dict = nx.maximum_flow(G, s, 'T')

        #print flow_value, flow_dict
        d = flow_dict
        G_ = nx.DiGraph()
        for key, value in d.iteritems():
            for key2, value2 in value.iteritems():
                if value2:
                    #print key, key2, value2

                    G_.add_edge(key, key2)


        #O = []
        Ij = G_.predecessors('T')

        O = [ [] for _ in range(len(Ij)) ]

        F = []

        i = 0
        for c in Ij:
            cRel = G.node[c]['ctrl_rel']
            for p in nx.all_simple_paths(G_, s, c):

                pRel=1.0



                for j in range(1, len(p)-1):
                    rel = G[p[j-1]][p[j]].get('reliability')
                    # print rel
                    # if (rel > 1.0):
                    #     print rel, j-1, j, p

                    assert(rel <=1.0)
                    pRel = pRel *rel



                #assert (k%2==0)
                #if k >0:
                #hop = k/2
                # Oi is the individual failure probability
                Oi = 1.0 - pRel
                # else:
                #     Oi = self.RCTRL

                #print k, path, Oi
                O[i].append(Oi)


            Fi = reduce(lambda x, y: x*y, O[i])*cRel +1-cRel

            F.append(Fi)

            i+= 1
        R = 1 - reduce(lambda x, y: x*y, F)
        #nx.predecessor()
        #Ij = []
        #if R >self.RREQ:

        return R, [i-2000 for i in Ij]









if __name__ == '__main__':


    G= gg.genGraph_import_graphML('../annotated_topo/Internetmci.graphml', 3000)


    rt = Reliability_calc (G, 0.999999999999999, 0.9999, 0.9999, 0.9999)



    rt.graph_rebuild()
    #
    plt.figure(figsize=(8,8))
    nx.draw(rt._G, node_size=2000, with_labels=True)
    plt.savefig("test_regen_1"+".png")
    #
    I = [0]
    #
    G__ = rt.graph_rebuild_add_ctrl(I)

    plt.figure(figsize=(8,8))
    nx.draw(G__, node_size=2000, with_labels=True)
    plt.savefig("test_regen_2"+".png")
