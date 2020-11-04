# -*- coding: utf-8 -*-

"""
  将各种文件导出生成gml文件
"""
import networkx as nx

# G_temp = node_to_edge_dict_to_networkx(edge_to_node_dict, [[1, 2, 3, 4, 5, 6, 7, 8, 9], [10], [11, 12, 13]])
# pos = nx.spring_layout(G_temp)
# nx.draw(G_temp, pos)
# node_labels = nx.get_node_attributes(G_temp, 'group')
# nx.draw_networkx_labels(G_temp, pos, labels=node_labels)
# node_groups = nx.get_node_attributes(G_temp, 'group')
# nx.draw_networkx_labels(G, pos, labels=node_groups)
# node_labels = {}
# plt.show()
G = nx.read_gml("../datasets/karate.gml", label="id")
print G.nodes(data=True)
print len(G.edges)
for edge in G.edges:
    print edge
node_groups = nx.get_node_attributes(G, 'value')
print node_groups
# print list(G.nodes)
# print list(G.edges)
# def clone_graph(G):
#     cloned_g = nx.Graph()
#     for edge in G.edges():
#         cloned_g.add_edge(edge[0], edge[1])
#     return cloned_g
# G = clone_graph(G)
# print list(G.nodes(data=True))

