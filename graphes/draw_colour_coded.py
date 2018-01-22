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



import matplotlib.pyplot as plt

from matplotlib import rc


import networkx as nx
import ast


import ConfigParser
import json



import numpy as np
import os


import csv

import pandas as pd


config_file = '../placement_alg/run.config'

config_parser = ConfigParser.ConfigParser()

def read_headers (file_nm):
    f = open(file_nm, 'rb')
    reader = csv.reader(f)
    headers = reader.next()
    column = {}
    for h in headers:
           column[h] = []
    f.close()
    return column


def read_file(file_nm,  column, header = False):
    f = open(file_nm, 'rb')
    reader = csv.reader(f)
    headers = reader.next()


    for row in reader:
       for h, v in zip(headers, row):
            column[h].append(v)
    f.close()
    return column


def read_FL_implementation (file_path, affinix, low, high):



    column = []

    frame = pd.DataFrame()

    for fn in range(low, high):
        fileName = file_path +str(fn)+affinix+'.csv'

        if os.path.exists(fileName):
            #print fileName
            df = pd.read_csv(fileName, index_col=None, header=0)

            df['id'] = fn
            column.append(df)

        #column = read_file(fileName,  column)

    frame = pd.concat(column)

    frame.set_index(['id'], inplace=True)

    rel_data = frame['rel'].tolist()

    return rel_data


def sweep_reading_a_topo (bdwidths, directory, graph_name,  affx):

    medians = []

    for bd in bdwidths:
        file_path = directory+'/'+str(bd)+'/'+graph_name+'/'

        rel_data = read_FL_implementation (file_path, affx, 0, 1)

        medians.append( 1- np.median(rel_data))


    return medians









def plot (G, pos, graph_name, file_path, affnix, save_name):

    G = G.copy()

    print file_path


    result_file_p= file_path + str(0)+'_'+affnix+'.csv'

    column = read_headers(result_file_p)


    column = read_file(result_file_p, column)

    controllers = column ['ctrls'][0]

   # print controllers

    controllers  = ast.literal_eval(controllers)


    aggregators = list (set(G.nodes()) - set(controllers))


    nx.draw_networkx_nodes(G,pos,
                           nodelist= controllers,
                           node_color='r',
                           node_size=800,
                           linewidths= 1,
                           alpha=0.5)


    nx.draw_networkx_nodes(G,pos,
                           nodelist= aggregators,
                           node_color='w',
                           node_size=800,
                           linewidths= 1,
                           alpha=1)

    nx.draw_networkx_edges(G,pos,width=1.0,alpha=0.5, arrows=False)


    labels = {}

    clusters = column['cluster'][0]


    clusters  = ast.literal_eval(clusters)

    for nd, ctrl in enumerate(clusters):
        print nd, ctrl

        labels[nd] = str(nd)+ '('+str(ctrl) +')'

    #print labels



    nx.draw_networkx_labels(G,pos,labels,font_size=8)
    print save_name

    plt.axis('off')
    plt.savefig("{}".format(save_name), bbox_inches='tight') # save as png
    #plt.show() # display


def plot_statistics ( m_fl, caps, save_name):

    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
    rc('text', usetex=True)
    plt.rcParams.update({'font.size': 16})


    Ls=[16]

    print m_fl


    fig, axes = plt.subplots(ncols=1, sharey=True, figsize=(8, 4))
    fig.subplots_adjust(wspace=0)
    yname =r"failure probability (1-Rmin)"
    axes.set_ylabel(yname, fontsize=18)

    name = r"bandwidth (Kbytes/s)"
    axes.set_xlabel(xlabel=name)
    #axes.set_xlim([10, 75])
    axes.set_yscale("log")
    data = m_fl

    x =  caps
    #for n in data.keys():
    axes.plot(x, data, marker='o', linestyle='-', color='k')

    #plt.legend(loc='upper right')
    plt.tight_layout()
    #save_name  = 'scale_bd_mci.pdf'
    plt.savefig("{}".format(save_name), bbox_inches='tight')

    #plt.show()



if __name__ == '__main__':

    config_parser.read(config_file)
    graph_name = config_parser.get ('TOPO', 'topoloogy')
    graph_path = '../annotated_topo/' + graph_name+'.graphml'

    #print graph_path
    caps =  json.loads( config_parser.get('CONSTRAINTS', 'linkbandwidth') )


    G= nx.read_graphml(graph_path , node_type=int)

    pos=nx.spring_layout(G) # positions for all nodes
    #print pos
    rstPath= config_parser.get ('PATHS', 'resultpath')

    for cap in caps :
        file_path = '../placement_alg/'+rstPath+ str(cap) +'/'+graph_name+'/'
        affinix = 'fl'

        save_name = '../graphes/'+graph_name+'_'+str(cap)+'.pdf'
        #print save_name

        plot (G, pos, graph_name, file_path, affinix, save_name)


    rst_directory = '../placement_alg/'+rstPath

    affx = '_fl'

    m_fl = sweep_reading_a_topo (caps, rst_directory, graph_name,  affx)

    print m_fl
    save_name = '../graphes/'+graph_name+'_'+'_scale_up'+'.pdf'
    plot_statistics ( m_fl, caps, save_name)

