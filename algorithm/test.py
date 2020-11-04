# -*- coding: utf-8 -*-
import networkx as nx

G = nx.Graph()
G = nx.read_gml("../datasets/football.gml", label="id")
node_groups = nx.get_node_attributes(G, 'value')
comunity_node_dict = {}
for node, comunity in node_groups.items():
    if comunity_node_dict.has_key(comunity):
        comunity_node_dict.get(comunity).append(node)
    else:
        temp = []
        temp.append(node)
        comunity_node_dict[comunity] = temp

for key, value in comunity_node_dict.items():
    print key
    print value
    print '-----------------------'