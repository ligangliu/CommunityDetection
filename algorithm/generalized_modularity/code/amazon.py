# -*- coding: utf-8 -*-
"""

This module test the results on Amazon co-purchasing networks

Example:
    Execute the code to test on Amazon co-purchasing network::

        $ python amazon.py

Research article is available at:
   http://google.github.io/styleguide/pyguide.html

"""


import os
import time
import pickle

import networkx as nx
from igraph import Graph as iG
from igraph import * 

from networkx.algorithms.community.modularity_max import * 
from generalized_modularity import multiscale_community_detection
from sklearn import metrics
from sklearn.metrics.cluster import adjusted_rand_score
from heatmap import hist


def loadAmazon():
    # cache graph in .gpickle format for fast reloading
    path =  "../data/amazon/amazon.gpickle"
    if os.path.isfile(path): 
        G = nx.read_gpickle(path)
        return G
    else:
        G = nx.Graph(gnc = {}, membership = {}, top5000 = {}, top5000_membership = {})
        with open("../data/amazon/com-amazon.ungraph.txt", "r") as txt:
            for line in txt:
                if not line[0] == '#':
                    e = line.split()
                    G.add_edge(int(e[0]), int(e[1]))
        with open("../data/amazon/com-amazon.top5000.cmty.txt", "r") as txt:
            count = 0
            for line in txt:
                if not line[0] == '#':
                    e = line.split()
                    G.graph["top5000"][count] = [int(_) for _ in e]
                    for n in G.graph["top5000"][count]:
                        if n in G.graph["top5000_membership"]:
                            G.graph["top5000_membership"][n].append( count )
                        else:
                            G.graph["top5000_membership"][n] = [ count ]
                    count += 1
        with open("../data/amazon/com-amazon.all.dedup.cmty.txt", "r") as txt:
            count = 0
            for line in txt:
                if not line[0] == '#':
                    e = line.split()
                    G.graph["gnc"][count] = [int(_) for _ in e]
                    for n in G.graph["gnc"][count]:
                        if n in G.graph["membership"]:
                            G.graph["membership"][n].append( count )
                        else:
                            G.graph["membership"][n] = [ count ]
                    count += 1
        print("write gpickle file..")
        nx.write_gpickle(G, path)
        return G

def networkx2igraph(G): 
    # G is a networkx graph instance
    # we convert it to igraph instance
    mapping = {v:i for i, v in enumerate(G.nodes())}
    rmapping = {i:v for i, v in enumerate(G.nodes())}

    g = iG() 
    g.add_vertices(len(mapping)) 
    g.add_edges([(mapping[i], mapping[j]) for i, j in G.edges()])
    g.to_undirected()
    gnc = list(G.graph["gnc"].values())
    return g, gnc, rmapping



if __name__ == "__main__":

    verbose = False

    G, gnc, rmapping = networkx2igraph(loadAmazon())
    #convert networkx Graph to igraph Graph
    print("igraph load graph:", summary(G))

    #============

    print("start naive community detection")

    start = time.time()
    vd = iG.community_fastgreedy(G)
    vc = vd.as_clustering()

    end = time.time()
    print("multi-scale", end - start, "seconds")

    txt = open("igraph_fastgreedy", "w+")
    for cc in range(len(vc)):
        if len(vc[cc]) > 1:
            txt.write(" ".join([str(rmapping[_]) for _ in vc[cc]]) + "\n")


    #comms0 = greedy_modularity_communities(G, resolution = 1.0)
    #comms0_sizes = sorted([len(comms0[i]) for i in range(len(comms0))])
    #verbose and print(comms0_sizes)

    #end = time.time()
    #print("naive modularity", end - start, "seconds")

    ## multi-scale community detection
    #print("start multi-scale community detection")
    #start = time.time()

    #comms1 = list(multiscale_community_detection(G, resolution = 0.4, threshold = 2.5, verbose = True))
    #comms1_sizes = sorted([len(comms1[i]) for i in range(len(comms1))])
    #verbose and print(comms1_sizes)

    #pickle.dump( [comms0_sizes, comms1_sizes], open( "save.p", "wb" ) )

    #============
