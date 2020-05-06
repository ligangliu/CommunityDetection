# -*- coding: utf-8 -*-

import networkx as nx

G = nx.Graph()
E = [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4],
     [2, 6], [2, 5], [5, 6], [2, 8], [8, 9]]
G.add_edges_from(E)
res = list(nx.find_cliques(G))
print res
