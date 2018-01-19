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
import matplotlib.pyplot as plt
import math
import random
from copy import deepcopy
import numpy as np




def genGraph_import_graphML (input_file_path, capacity):

    H = nx.read_graphml(input_file_path, node_type=int)

    name = input_file_path.split('/')[-1]
    name = name.split('.')[0]




    G = H
    index = 0

    for nd, nb in G.edges(data = False):

        G[nd][nb]['capacity'] = capacity

    return G

def scale_cap(G_, sc):
    G = deepcopy (G_)

    for nd, nb in G.edges(data = False):


        G[nd][nb]['capacity'] = G[nd][nb]['capacity']*sc


    return G
