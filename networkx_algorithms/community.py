# -*- coding: utf-8 -*-
import networkx as nx
from networkx.algorithms import community

G = nx.barbell_graph(5, 1)
# print G.nodes
# print G.edges
# kernighan_lin_bisection 用于计算Kernighan-Lin二部算法的函数
res = community.kernighan_lin_bisection(G)
print res

# 利用渗透法在图中寻找k族群落
res = community.k_clique_communities(G, 2)
print res

# 使用Clauest Newman-Moore贪婪的模块化最大化在图中寻找社区
res = community.greedy_modularity_communities(G)
print res
