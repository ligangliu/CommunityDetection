# -*- coding: utf-8 -*-

'''

使用python库函数生成LFR网络
https://networkx.github.io/documentation/latest/reference/generated/networkx.generators.community.LFR_benchmark_graph.html?highlight=lfr#networkx.generators.community.LFR_benchmark_graph

生成工具各参数的意义：
-N：number of nodes
-k：average degree
-maxk：maximum degree
-mu：mixing parameter
-t1：    minus exponent for the degree sequence
-t2：    minus exponent for the community size distribution
-minc：    minimum for the community sizes
-maxc：    maximum for the community sizes
-on：    number of overlapping nodes
-om：number of memberships of the overlapping nodes

LFR_benchmark_graph: 需要在networkx >= 2.4 而networkx又需要 >= python3
G = LFR_benchmark_graph(n, tau1, tau2, mu, average_degree=None,
                        min_degree=None, max_degree=None, min_community=None,
                        max_community=None, tol=1.0e-7, max_iters=500,
                        seed=None)
参数说明:
    n: 创建的节点
    tau1 （ 浮动 ）--创建图的度分布的幂律指数。此值必须严格大于1。
    tau2 （ 浮动 ）--创建的图中社区大小分布的幂律指数。此值必须严格大于1。
    mu （ 浮动 ）--每个节点上的社区内边缘部分。此值必须在间隔中 [0, 1] .
    average_degree （ 浮动 ）--所创建图形中节点的所需平均程度。此值必须在间隔中 [0, n] .
        正是其中之一 min_degree 必须指定，否则 NetworkXError 提高了。
    min_degree （ int ）--所创建图形中节点的最小程度。此值必须在间隔中 [0, n] .
        正是其中之一 average_degree 必须指定，否则 NetworkXError 提高了。
    max_degree （ int ）--所创建图形中节点的最大程度。如果未指定，则将其设置为 n ，图中的节点总数。
    min_community （ int ）--图中社区的最小大小。如果未指定，则将其设置为 min_degree .
    max_community （ int ）--图中社区的最大大小。如果未指定，则将其设置为 n ，图中的节点总数。
    tol （ 浮动 ）--比较浮点数时的公差，特别是比较平均度数时的公差。
    max_iters （ int ）--尝试创建社区大小、度分布和社区关联的最大迭代次数。
    seed （ integer, random_state, or None (default) ）--随机数生成状态的指示器。见 Randomness .

返回：
    G --根据指定参数生成的LFR基准图。图中的每个节点都有一个节点属性 'community'
    它存储包含它的社区（即节点集）。
'''
import csv
import sys
import networkx as nx
from networkx.generators.community import LFR_benchmark_graph

n = 250
tau1 = 3
tau2 = 1.5
mu = 0.1
G = LFR_benchmark_graph(n, tau1, tau2, mu, average_degree=5,
                                    min_community=20, seed=10)
communities = {frozenset(G.nodes[v]['community']) for v in G}
# print(G.nodes)
# print(communities)
def community_layout(g, partition):
    """
    Compute the layout for a modular graph.


    Arguments:
    ----------
    g -- networkx.Graph or networkx.DiGraph instance
        graph to plot

    partition -- dict mapping int node -> int community
        graph partitions


    Returns:
    --------
    pos -- dict mapping int node -> (float x, float y)
        node positions

    """

    pos_communities = _position_communities(g, partition, scale=3.)

    pos_nodes = _position_nodes(g, partition, scale=1.)

    # combine positions
    pos = dict()
    for node in g.nodes():
        pos[node] = pos_communities[node] + pos_nodes[node]

    return pos

def _position_communities(g, partition, **kwargs):

    # create a weighted graph, in which each node corresponds to a community,
    # and each edge weight to the number of edges between communities
    between_community_edges = _find_between_community_edges(g, partition)

    communities = set(partition.values())
    hypergraph = nx.DiGraph()
    hypergraph.add_nodes_from(communities)
    for (ci, cj), edges in between_community_edges.items():
        hypergraph.add_edge(ci, cj, weight=len(edges))

    # find layout for communities
    pos_communities = nx.spring_layout(hypergraph, **kwargs)

    # set node positions to position of community
    pos = dict()
    for node, community in partition.items():
        pos[node] = pos_communities[community]

    return pos

def _find_between_community_edges(g, partition):

    edges = dict()

    for (ni, nj) in g.edges():
        ci = partition[ni]
        cj = partition[nj]

        if ci != cj:
            try:
                edges[(ci, cj)] += [(ni, nj)]
            except KeyError:
                edges[(ci, cj)] = [(ni, nj)]

    return edges

def _position_nodes(g, partition, **kwargs):
    """
    Positions nodes within communities.
    """

    communities = dict()
    for node, community in partition.items():
        try:
            communities[community] += [node]
        except KeyError:
            communities[community] = [node]

    pos = dict()
    for ci, nodes in communities.items():
        subgraph = g.subgraph(nodes)
        pos_subgraph = nx.spring_layout(subgraph, **kwargs)
        pos.update(pos_subgraph)

    return pos

import matplotlib.pyplot as plt
from networkx.algorithms import community
g = nx.karate_club_graph()


