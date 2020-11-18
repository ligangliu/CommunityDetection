# -*- coding: utf-8 -*-
import networkx as nx

# Community.modularity()
# Computing the Q

'''
http://www.yalewoo.com/modularity_community_detection.html
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
        # 表示的是社团内部的边数
        for i in range(len(community)):
            for j in range(len(community)):
                if (G.has_edge(community[i], community[j])):
                    t += 1.0
        e.append(t / (2 * m))

    q = 0.0
    for ei, ai in zip(e, a):
        q += (ei - ai ** 2)
    return q


if __name__ == '__main__':
    G = nx.read_gml("./datasets/karate.gml", label="id")

    print cal_Q([[12, 17, 6, 7, 10, 13, 18, 22, 5, 11, 29, 20, 14, 8, 2, 4, 1],
                 [25, 26, 27, 28, 15, 16, 19, 21, 23, 31, 32, 9, 24, 30, 3, 33, 34]], G)
    # modularity里面的方法是不能用在重叠社区的模块度发现的，
    # 因为内部是有一个判断是否为合适的分区的逻辑，如果是重叠分区，会抛出异常
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (0, 3),
                      (1, 2), (1, 3), (2, 4),
                      (4, 5), (4, 7), (5, 6),
                      (5, 7), (5, 8), (6, 8),
                      (7, 8), (7, 10), (8, 9),
                      (9, 10), (9, 12), (9, 13),
                      (10, 11), (10, 12), (11, 12),
                      (11, 13), (12, 13)])
    paration = [{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}]
    print cal_Q(paration, G)
    print nx.algorithms.community.modularity(G, paration)

    G = nx.read_gml("../datasets/karate.gml", label="id")
    print cal_Q([{12, 17, 6, 7, 10, 13, 18, 22, 5, 11, 29, 20, 14, 8, 2, 4, 1},
                 {25, 26, 27, 28, 15, 16, 19, 21, 23, 31, 32, 9, 24, 30, 3, 33, 34}], G)
    print nx.algorithms.community.modularity(G, [{12, 17, 6, 7, 10, 13, 18, 22, 5, 11, 29, 20, 14, 8, 2, 4, 1},
                                                 {25, 26, 27, 28, 15, 16, 19, 21, 23, 31, 32, 9, 24, 30, 3, 33, 34}])
