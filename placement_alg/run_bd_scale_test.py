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


import multiprocessing
import time
import setup_a_test as sgTest
import gen_graph as gg
#
import logging
from copy import deepcopy
import os
import ConfigParser
import json
config_file = 'run.config'

config_parser = ConfigParser.ConfigParser()

def mp_worker ( (G, out_directory, task_id, n, avg_cap) ):
    sgTest.cmp_run_iterations (G, out_directory, task_id, n, avg_cap)





def mp_handler(data):
    p = multiprocessing.Pool(processes= 4)
    p.map(mp_worker, data)




if __name__ == '__main__':

    # logging.config.fileConfig('/run/user/1000/gvfs/sftp:host=192.168.122.1,port=2300,user=osboxes/home/osboxes/Applications/controlPlane/control_algs/logging.config')
    # logger = logging.getLogger("all_aneal_placement_feasibility")
    #
    # logger.info("Program started")
    logging.config.fileConfig('logging.config')
    logger = logging.getLogger("simulation")

    logger.info("Program started")

    config_parser.read(config_file)

    rstPath= config_parser.get ('PATHS', 'resultpath')

    print rstPath

    directory_r= rstPath

    topoPath = config_parser.get ('PATHS', 'topopath')


    if not os.path.exists(directory_r):
            os.makedirs(directory_r)

    data = []

    linkbandwidth = json.loads( config_parser.get('CONSTRAINTS', 'linkbandwidth') )

    print linkbandwidth

    caps = linkbandwidth


    topo = config_parser.get ('TOPO', 'topoloogy')
    graph_names = [topo] *len (caps)

    for (cap, graph_name) in zip(caps, graph_names):

        directory = directory_r +str(cap)+'/'

        if not os.path.exists(directory):
                os.makedirs(directory)

        directory_g = directory +graph_name +'/'
        if not os.path.exists(directory_g):

            os.makedirs(directory_g)


        graph_path = topoPath + graph_name+'.graphml'

        print graph_path
        G= gg.genGraph_import_graphML(graph_path, cap)


        for task_id in range(0, 1):
             d = [deepcopy(G), directory_g, task_id, 1, cap]
             data.append(d)

    mp_handler(data)

    # jobs = []
    # for i in range(2):
    #     d = [deepcopy(G), directory, i, 25, 1000]
    #     p = multiprocessing.Process(target=mp_worker, args=(d,))
    #     #jobs.append(p)
    #     p.start()


    #cmp_run_iterations(G, directory, 1, 1, 1000)