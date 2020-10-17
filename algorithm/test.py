# -*- coding: utf-8 -*-
import networkx as nx

G = nx.Graph()
G = nx.read_gml("../datasets/karate.gml", label="id")
knn_nodes = nx.neighbors(G, 13)
for x in knn_nodes:
    print x