# -*- coding: utf-8 -*-
import networkx as nx

# Community.modularity()
# Computing the Q

'''
https://blog.csdn.net/wangyibo0201/article/details/52048248
模块度的取值应在0-1之间，Q值越大说明网络划分的社区结构准确度越高
from networkx.algorithms.community.quality import modularity, performance
print modularity(G, partition)
'''


def cal_Q(partition, G):
    m = len(G.edges(None, False))
    a = []
    e = []
    for community in partition:
        t = 0.0
        for node in community:
            t += len([x for x in G.neighbors(node)])
        a.append(t / (2 * m))

    for community in partition:
        t = 0.0
        for i in range(len(community)):
            for j in range(len(community)):
                if (G.has_edge(community[i], community[j])):
                    t += 1.0
        e.append(t / (2 * m))

    q = 0.0
    for ei, ai in zip(e, a):
        q += (ei - ai ** 2)
    return q


# def modularity(community, G):
#     """
#     Compute modularity of communities of network
#
#     Parameters
#     --------
#     G : networkx.Graph
#         an undirected graph
#     community : dict
#         the communities result of community detection algorithms
#     """
#     V = [node for node in G.nodes()]
#     m = G.size(weight='weight')  # if weighted
#     n = G.number_of_nodes()
#     A = nx.to_numpy_array(G)
#     Q = 0
#     for i in range(n):
#         node_i = V[i]
#         com_i = community[node_i]
#         degree_i = G.degree(node_i)
#         for j in range(n):
#             node_j = V[j]
#             com_j = community[node_j]
#             if com_i != com_j:
#                 continue
#             degree_j = G.degree(node_j)
#             Q += A[i][j] - degree_i * degree_j / (2 * m)
#     return Q / (2 * m)


if __name__ == '__main__':
    G = nx.barbell_graph(3, 0)
    print cal_Q([[0, 1, 2], [3, 4, 5]], G)
    print nx.algorithms.community.modularity(G, [{0, 1, 2}, {3, 4, 5}])
