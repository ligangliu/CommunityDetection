# -*- coding: utf-8 -*-

'''
https://zhiyzuo.github.io/python-modularity-maximization/doc/quick-start.html
'''

import networkx as nx
from modularity_maximization import partition
from modularity_maximization.utils import get_modularity


G = nx.karate_club_graph()
nx.clustering(G)
# 使用最大模块度的方法划分社区
comm_dict = partition(G)
# for comm in set(comm_dict.values()):
#     print "Community %d" % comm
#     print ", ".join([str(node) for node in comm_dict if comm_dict[node] == comm])
print comm_dict
print "Modularity of such partition for kerate is %.3f " % get_modularity(G, comm_dict)
