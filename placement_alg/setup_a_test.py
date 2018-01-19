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



from networkx.readwrite import json_graph
import json
from iterative_FTCP import run_iterative_FTCP
import networkx as nx

from all_aneal_clustering import Anealing_Clustering_Routing_Problem
from all_aneal_placement  import Anealing_Placement_Problem

from all_aneal_placement_feasibility  import Anealing_Placement_Problem_FBL

from single_FTCP_bdwidth import single_FTCP_frame

from gen_graph import *
import logging
import logging.config
import csv


import time
import os

import math

from copy import deepcopy

logger = logging.getLogger("simulation")








def single_anneal_fl (id, G,  distance_matrix, out_file_handle, *args, **kwarg ) :

        wr = csv.writer(out_file_handle, quoting=csv.QUOTE_ALL)

        start_time = time.time()

        #print ("{{\"tm\": {}, \"msg\":{} }}".format(time.time(), encode))

        rt = Anealing_Placement_Problem_FBL (G)

        (lower, upper), best_I, best_controlers, best_rel,  best_cost, best_lamga = rt.scale_rel()

        end_time = time.time()
        print " lower {}, upper {}, rel {}".format(lower, upper, best_rel)

        cmp = float (1.0 - 10.0**(-lower))
        if best_rel < cmp :
            logger.error (" rel {} smaller than 10 -{} ".format(lower))
            best_rel = cmp





        result = [id, best_I, best_controlers, best_rel, best_cost,  best_lamga, end_time-start_time]
        print result
        wr.writerow (result)


def single_anneal_fl_bdwidth (id, G,  distance_matrix, out_file_handle, relReq=0.99999, initCap =1000, *args, **kwarg ) :

        wr = csv.writer(out_file_handle, quoting=csv.QUOTE_ALL)


        start_time = time.time()


        param = {}

        param['rreq'] = relReq

        rt = Anealing_Placement_Problem_FBL (G, **param)

        (lower, upper), scale, best_I, best_controlers, best_rel,  best_cost, best_lamga = rt.scale_bdwdith()

        #(lower, upper), best_I, best_controlers, best_rel,  best_cost, best_lamga = rt.scale_rel()

        end_time = time.time()
        print " lower {}, upper {}, rel {}".format(lower, upper, best_rel)


        iter =0

        result = [id, scale*initCap, best_I, best_controlers, best_rel, best_cost,  best_lamga, iter, end_time-start_time]
        print result
        wr.writerow (result)




def cmp_run_iterations (G, out_directory, task_id, n, avg_cap):


    dict = out_directory.split('/')
    graph = dict[-2]

    distance_matrix = nx.all_pairs_shortest_path_length(G)



    header = ['id', 'cluster', 'ctrls', 'rel', 'cost', 'lambda', 'time']


    out_file_f = out_directory + str(task_id) + "_fl.csv"

    fd_f = open (out_file_f, 'w')
    wr = csv.writer(fd_f, quoting=csv.QUOTE_ALL)
    wr.writerow(header)


    for i in range(n):

        single_anneal_fl(i, G, distance_matrix, fd_f)
        fd_f.flush()
        logger.info ("graph {} task {} iter {} aneal_fl done".format(graph, task_id, i))
        time.sleep(0.1)


    fd_f.close()


#
if __name__ == '__main__':

#
      task_id =  0
      num_iter = 1
#
      directory='Fixed_usage_tst/'
      cap = 6000
#     if not os.path.exists(directory):
#             os.makedirs(directory)
      G= genGraph_import_graphML('../annotated_topo/Internetmci.graphml', cap)
      cmp_run_iterations(G, directory, task_id, num_iter, cap)
#     #run_rel(G, directory, task_id, num_iter, avg_cap)