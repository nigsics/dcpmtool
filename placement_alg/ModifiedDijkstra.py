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


class ModifiedDijkstra(object):

    def __init__(self, g, wt="weight"):

        self.dist = {} # A map from nodes to their labels (float)
        self.predecessor = {} # A map from a node to a node
        self.g = g;
        self.wt = wt;
        edges = g.edges()
        # Set the value for infinite distance in the graph
        self.inf = 0.0;
        for e in edges:
            self.inf += abs(g[e[0]][e[1]][wt]);
        self.inf += 1.0;
    
    
    def getPath(self, source, dest, as_nodes = False):

        self.dist = {} # A map from nodes to their labels (float)
        self.predecessor = {} # A map from a node to a node

        # Initialize the distance labels to "infinity"
        vertices = self.g.nodes()
        for vertex in vertices:
            self.dist[vertex] =  self.inf
            self.predecessor[vertex] = source

        # Further set up the distance from the source to itself and
        # to all one hops away.
        self.dist[source] = 0.0
        if self.g.is_directed():
            outEdges = self.g.out_edges([source])
        else:
            outEdges = self.g.edges([source])
        for edge in outEdges:
            self.dist[edge[1]] = self.g[edge[0]][edge[1]][self.wt]
        
        s = set(vertices)
        s.remove(source);
        currentMin = self._findMinNode(s)
        if currentMin == None:
            return None
        s.remove(currentMin)
        while currentMin != dest and (len(s) != 0) and currentMin != None:
            if self.g.is_directed():
                outEdges = self.g.out_edges([currentMin])
            else:
                outEdges = self.g.edges([currentMin])
            for edge in outEdges:
                opposite = edge[1]
                if self.dist[currentMin] + self.g[edge[0]][edge[1]][self.wt] < self.dist[opposite]:
                    self.dist[opposite] = self.dist[currentMin] + self.g[edge[0]][edge[1]][self.wt]
                    self.predecessor[opposite] = currentMin
                    s.add(opposite);
                
            currentMin = self._findMinNode(s)
            #print "Current min node {}, s = {}".format(currentMin, s)
            if currentMin == None:
                return None
            s.remove(currentMin)
        
        # Compute the path as a list of edges
        currentNode = dest;
        predNode = self.predecessor.get(dest);
        node_list = [dest]
        done = False
        path = []
        while not done:
            path.append((predNode, currentNode))
            currentNode = predNode
            predNode = self.predecessor[predNode]
            node_list.append(currentNode)
            done = currentNode == source
        node_list.reverse()
        if as_nodes:
            return node_list
        else:
            return path
    

    def _findMinNode(self, s):

        minNode = None
        minVal = self.inf
        for vertex in s:
            if self.dist[vertex] < minVal:
                minVal = self.dist[vertex]
                minNode = vertex
        return minNode
    
