# -*- coding: utf-8 -*-
from collections import defaultdict
import networkx as nx

"""
    https://blog.csdn.net/wangyibo0201/article/details/52048248
    paper:<<Detect overlapping and hierarchical community structure in networks>>
    G:vertex-neighbors {vertex:list(neighbors)}
"""

# 对于重叠社区的模块度
def cal_EQ(partition, G):
    m = len(G.edges(None, False))
    # 统计每个节点分在共有几个社区
    node_dict = {}
    for node in G.nodes:
        t = 0
        for community in partition:
            if node in community:
                t += 1.0
        node_dict[node] = t

    def cal_ekk(c_k):
        community = partition[c_k]
        sum = 0.0
        for i in range(len(community)):
            for j in range(len(community)):
                if (i != j and G.has_edge(community[i], community[j])):
                    wik = 1.0 / node_dict[community[i]]
                    wjk = 1.0 / node_dict[community[j]]
                    sum += (wik + wjk) / 2
        return sum / 2

    def cal_ekout(c_k):
        sum = 0.0
        for nodei in partition[c_k]:
            for i in range(len(partition)):
                if i != c_k:
                    for nodej in partition[i]:
                        if G.has_edge(nodei, nodej):
                            wik = 1.0 / node_dict[nodei]
                            wjk = 1.0 / node_dict[nodej]
                            sum += (wik + (1-wjk))
        return sum

    a = []
    e = []
    for i in range(len(partition)):
        ekk = cal_ekk(i)
        ekout = cal_ekout(i)
        e.append(ekk / m)
        dk = 2*ekk + ekout
        a.append(dk / (2 * m))

    q = 0.0
    for ei, ai in zip(e, a):
        q += (ei - ai ** 2)
    return q


if __name__=='__main__':
    G = nx.read_gml("../datasets/karate.gml", label="id")
