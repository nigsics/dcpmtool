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



import csv
import pandas as pd
import os
import numpy as np

import math

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


def sweep_reading_a_topo (bdwidths, directory, graph_name, low, high, affx):

    medians = []

    for bd in bdwidths:
        file_path = directory+'/'+str(bd)+'/'+graph_name+'/'

        rel_data = read_FL_implementation (file_path, affx, low, high)

        medians.append( 1- np.median(rel_data))


    #print medians
    return medians







if __name__ == '__main__':
    # dic= "../control_algs/temp_eht_tst/"
    # file_nm = dic +'0'+'.csv'
    #
    # column = read_headers(file_nm)
    # print column
    # column = read_file(file_nm, column)
    #print column
    # column, column_cmp = merge_data()
    #
    # plot_figure(column, column_cmp)




    low = 0
    high = 100
    bdwidths = [1000, 2000, 3000, 4000, 5000, 6000, 9000]
    graph_name = "Arpanet19728"
    directory = "../control_algs/scaleup_bd/"
    affx='_fl'

    sweep_reading_a_topo (bdwidths, directory, graph_name, low, high, affx)