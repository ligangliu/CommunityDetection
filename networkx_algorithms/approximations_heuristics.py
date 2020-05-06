# -*- coding: utf-8 -*-

import networkx as nx
from networkx.algorithms import approximation

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 5), (1, 5), (5, 6), (7, 8), (3, 7)])
# 两个不同节点和非相邻节点之间的成对或本地节点连接是断开它们时必须删除的节点的最小数目（最小分离切割集）
res = approximation.all_pairs_node_connectivity(G)
print res
