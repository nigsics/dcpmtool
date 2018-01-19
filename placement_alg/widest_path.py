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



import networkx
from copy import deepcopy
import operator
from collections import OrderedDict

import gen_graph as gg
from heapq import heappush, heappop
from itertools import count
def Dijkstra_widest(Graph, source):
    width = {}
    previous ={}
    for v in Graph.nodes():                                 # Initializations
        width[v] = -10000                                 # Unknown width function from
        previous[v] = None                               # Previous node in optimal path

    width[source] = 10000
    Q = OrderedDict(sorted (width.items(), key= operator.itemgetter(1)) )
    #print Q
    while Q :                                                                                   # The main loop
        (u, cap) = max (Q.items(), key= operator.itemgetter(1) )                 # Source node in first case
        Q.pop(u, None)
        if cap == -1:
            break                                             # all remaining vertices are
                                                         # inaccessible from source

        for  v in  Graph.neighbors(u):                              # where v has not yet been
           alt = max(width[v], min(width[u], Graph[u][v]['capacity']))

           if alt > width[v]:                                 # Relax (u,v,a)
                width[v] = alt
                previous[v] = u
                Q[v] =alt
                #decrease-key v in Q;                           # Reorder v in the Queue


    width.pop(source, None)

    paths = {}

   # print previous
    for v in width.keys():
        path = [v]
        pre = v
        while (1):
            pre = previous[pre]
            #print pre
            path.append(pre)

            if pre == source:
                path.reverse()
                # print v, path
                paths[v] = path
                break

    return width, paths




def Dijkstra_widest_dst(Graph, source):
    width = {}
    previous ={}
    for v in Graph.nodes():                                 # Initializations
        width[v] = -10000                                 # Unknown width function from
        previous[v] = None                               # Previous node in optimal path

    width[source] = 10000
    Q = OrderedDict(sorted (width.items(), key= operator.itemgetter(1)) )
    #print Q
    while Q :                                                                                   # The main loop
        (u, cap) = max (Q.items(), key= operator.itemgetter(1) )                 # Source node in first case
        Q.pop(u, None)
        if cap == -1:
            break                                             # all remaining vertices are
                                                         # inaccessible from source

        for  v in  Graph.predecessors(u):                              # where v has not yet been
           alt = max(width[v], min(width[u], Graph[v][u]['capacity']))

           if alt > width[v]:                                 # Relax (u,v,a)
                width[v] = alt
                previous[v] = u
                Q[v] =alt
                #decrease-key v in Q;                           # Reorder v in the Queue


    width.pop(source, None)

    paths = {}

   # print previous
    for v in width.keys():
        path = [v]
        pre = v
        while (1):
            pre = previous[pre]
            #print pre
            path.append(pre)

            if pre == source:
                #path
                # print v, path
                paths[v] = path
                break

    return width, paths

def get_weight(v, u, G, w = 'dweight', dst_mode = False):
        if not dst_mode:
            return G[v][u][w]
        else:
            return G[u][v][w]




def Dijkstra_weight(G, source, dst_mode = False, w='dweight'):
    G_succ = G.succ if not dst_mode else G.pred

    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    seen = {source: 0}
    c = count()
    fringe = []  # use heapq with (distance,label) tuples
    push(fringe, (0, next(c), source))
    paths = {}
    paths[source] = [source]
    while fringe:
        (d, _, v) = pop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d


        for u, e in G_succ[v].items():
            #cost = get_weight(v, u, G, w, dst_mode)
            # if cost is None:
            #     continue
            vu_dist = dist[v] + get_weight(v, u, G, w, dst_mode)
            # if cutoff is not None:
            #     if vu_dist > cutoff:
            #         continue
            if u in dist:
                if vu_dist < dist[u]:
                    raise ValueError('Contradictory paths found:',
                                     'negative weights?')
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                push(fringe, (vu_dist, next(c), u))
                #if paths is not None:
                if not dst_mode:
                    paths[u] = paths[v] + [u]
                else:
                    paths[u] = [u] + paths[v]
                # if pred is not None:
                #     pred[u] = [v]
            # elif vu_dist == seen[u]:
            #     if pred is not None:
            #         pred[u].append(v)

    #if paths is not None:
    return (dist, paths)
    # if pred is not None:
    #     return (pred, dist)
    #return dist

    #return width, paths

# def Dijkstra_weight(G, source, dst_mode = False, w='dweight'):
#     G_succ = G.succ if not dst_mode else G.pred
#
#     push = heappush
#     pop = heappop
#     dist = {}  # dictionary of final distances
#     seen = {source: 0}
#     c = count()
#     fringe = []  # use heapq with (distance,label) tuples
#     push(fringe, (0, next(c), source))
#     paths = {}
#     paths[source] = [source]
#     while fringe:
#         (d, _, v) = pop(fringe)
#         if v in dist:
#             continue  # already searched this node.
#         dist[v] = d
#
#
#         for u, e in G_succ[v].items():
#             cost = get_weight(v, u, G, w, dst_mode)
#             if cost is None:
#                 continue
#             vu_dist = dist[v] + get_weight(v, u, G, w, dst_mode)
#             # if cutoff is not None:
#             #     if vu_dist > cutoff:
#             #         continue
#             if u in dist:
#                 if vu_dist < dist[u]:
#                     raise ValueError('Contradictory paths found:',
#                                      'negative weights?')
#             elif u not in seen or vu_dist < seen[u]:
#                 seen[u] = vu_dist
#                 push(fringe, (vu_dist, next(c), u))
#                 #if paths is not None:
#                 if not dst_mode:
#                     paths[u] = paths[v] + [u]
#                 else:
#                     paths[u] = [u] + paths[v]
#                 # if pred is not None:
#                 #     pred[u] = [v]
#             # elif vu_dist == seen[u]:
#             #     if pred is not None:
#             #         pred[u].append(v)
#
#     #if paths is not None:
#     return (dist, paths)



# def Dijkstra_weight(G, source, dst_mode = False, w='dweight'):
#     G_succ = G.succ if not dst_mode else G.pred
#
#     push = heappush
#     pop = heappop
#     dist = {}  # dictionary of final distances
#     seen = {source: 0}
#     c = count()
#     fringe = []  # use heapq with (distance,label) tuples
#     push(fringe, (0, next(c), source))
#     paths = {}
#     paths[source] = [source]
#     while fringe:
#         (d, _, v) = pop(fringe)
#         if v in dist:
#             continue  # already searched this node.
#         dist[v] = d
#
#
#         for u, e in G_succ[v].items():
#             cost = get_weight(v, u, G, w, dst_mode)
#             if cost is None:
#                 continue
#             vu_dist = dist[v] + get_weight(v, u, G, w, dst_mode)
#             # if cutoff is not None:
#             #     if vu_dist > cutoff:
#             #         continue
#             if u in dist:
#                 if vu_dist < dist[u]:
#                     raise ValueError('Contradictory paths found:',
#                                      'negative weights?')
#             elif u not in seen or vu_dist < seen[u]:
#                 seen[u] = vu_dist
#                 push(fringe, (vu_dist, next(c), u))
#                 #if paths is not None:
#                 if not dst_mode:
#                     paths[u] = paths[v] + [u]
#                 else:
#                     paths[u] = [u] + paths[v]
#                 # if pred is not None:
#                 #     pred[u] = [v]
#             # elif vu_dist == seen[u]:
#             #     if pred is not None:
#             #         pred[u].append(v)
#
#     #if paths is not None:
#     return (dist, paths)





if __name__ == '__main__':

    #G= gg.genGraph_triangle(8, 8, 1000)

    G=gg.gen_mesh_Graph(2, 2, 1)
    width, paths = Dijkstra_weight(G, 3, w='capacity')



    print width
    print paths
    print width[0], paths[0]
    p =paths[0]

    print "#########test reverse alg ###################"
    width, paths = Dijkstra_weight(G, 3, dst_mode=True, w='capacity')


    print width
    print paths
    print width[0], paths[0]
    p =paths[0]

