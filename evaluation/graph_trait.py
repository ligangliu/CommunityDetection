# -*- coding: utf-8 -*-
'''
图分析--聚类系数，节点距离，联通子图和图的稳定性分析
https://alphafan.github.io/posts/graph_analysis.html
'''
import networkx as nx
'''
聚类系数：
Local Cluster Coefficient
简单理解：已经成为朋友/可能成为朋友
已经成为朋友，就是某个节点的三角形的个数
可能成为朋友，就是某个几点的度数N = N*(N-1)/2
Global Cluster Coefficient
    1) 计算每一个节点的Loacl Cluster Coefficient，然后取平均值
    2）是先计算在图中已经关闭上的三角形的个数，除上没有闭上的三角形的个数。这种计算方法叫做 Transitivity。
'''
G = nx.Graph()
G.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'E'), ('C', 'F'), ('G', 'H')])
print nx.clustering(G)
print nx.average_clustering(G)

'''
节点的距离
    Average distance: 所有两两节点之间的最短距离的平均值
    Eccentricity: 输出任意一个节点的能够到达的最大距离
    Diameter: 图中最大两个节点的距离 Periphery: 和Diameter对应，那些最大节点距离等于 diameter 的节点
    Radius: 图中最小两个节点的距离 Center: 和Radius对应，那些最大节点距离等于 radius 的节点
'''
# 计算每一个节点到其他所有节点的最短距离  shortest_path还可以记录路径
for x in nx.shortest_path_length(G):
    print x
# print nx.average_shortest_path_length(G)
# print nx.eccentricity(G)
# print nx.diameter(G), nx.periphery(G)
# print nx.radius(G), nx.center(G)

'''
介数中心性: 是基于最短路径的图中的中心的度量的方法。
对于连通图中的每对顶点，在顶点之间至少存在一条最短路径，而一个节点的介数一般是指通过该节点的最短路径数。
同理，我们可以定义边介数
'''
print '------------'
print nx.betweenness_centrality(G)
print nx.edge_betweenness_centrality(G)
for x in nx.connected_components(G):
    print x
from modularity_maximization import partition
print partition(G)
