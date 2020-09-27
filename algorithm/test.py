# -*- coding: utf-8 -*-

import networkx as nx

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (1, 4), (1, 8),
                  (2, 3), (2, 4),
                  (3, 5), (3, 6), (3, 7),
                  (4, 5), (4, 7), (4, 9), (4, 10),
                  (5, 7)], weight=1.0)
G.add_node(12)

print G.degree(12)