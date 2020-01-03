# -*- coding: utf-8 -*-

import networkx as nx

G = nx.Graph()
G.add_node(1)
G.add_nodes_from([2,3])

H = nx.path_graph(10)
G.add_node(H)

G.add_edge(1, 2)
G.add_edges_from([(1, 2), (1, 3)])
G.clear()

G.add_edges_from([(1, 2), (1, 3)])
G.add_node(1)
G.add_edge(1, 2)
G.add_node("spam")
G.add_nodes_from("spam")
G.add_edge(3, 'm')
G.add_edge(1, 'm')

print G.number_of_nodes()
print G.number_of_edges()

print list(G.nodes)
print list(G.edges)
print G.adj
print G.adj[1]
print G.edges([2, 'm'])
print G.degree([2, 3])

# G.remove_node(1)
# print list(G.edges)
# G.remove_edge(3, 'm')
print G.nodes
print G[1]
