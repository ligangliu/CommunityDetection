# -*- coding: utf-8 -*-#

import os
import commands
import time

from my_objects import AlgorithmParam
import networkx as nx


def generate_network(param):
    community_path = "/app/datasets/community.nmc"
    if os.path.exists(community_path):
        os.remove(community_path)
        print '*' * 30
        print "delete community.nmc success..."
        print '*' * 30
    networkx_path = "/app/datasets/community.nse"
    if os.path.exists(networkx_path):
        print '*' * 30
        print "delete community.nse success..."
        print '*' * 30
        os.remove(networkx_path)
    assert isinstance(param, AlgorithmParam)
    n = param.n
    k = param.k
    maxk = param.maxk
    minc = param.minc
    maxc = param.maxc
    mut = param.mut
    muw = param.muw
    on = param.on
    om = param.om
    args = "-N {n} -k {k} -maxk {maxk} -minc {minc} -maxc {maxc} -mut {mut} -muw {muw} -on {on}  -om {om} -name /app/datasets/community" \
        .format(n=n, k=k, maxk=maxk, minc=minc, maxc=maxc, mut=mut, muw=muw, on=on, om=om)
    print "generate network success..."
    commands.getoutput("/app/datasets/benchmark {args}".format(args=args))
    while not os.path.exists(community_path):
        time.sleep(1)


def calculate_onmi():
    res = commands.getoutput("/app/datasets/onmi/onmi /app/datasets/lfr_code.txt /app/datasets/lfr_true.txt")
    lines = res.splitlines(True)
    onmi = 0.0
    for line in lines:
        if line.strip().startswith("lfk"):
            onmi = float(line.strip().split("\t")[1])

    return onmi

# 感觉此种评估的意义不大，比如karate的数据，我使用完全真实的社区结构计算模块度，也就是0.371466140697
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
        community = list(community)
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


def calcualte_EQ(partition, G):
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
                            sum += (wik + (1 - wjk))
        return sum

    a = []
    e = []
    for i in range(len(partition)):
        ekk = cal_ekk(i)
        ekout = cal_ekout(i)
        e.append(ekk / m)
        dk = 2 * ekk + ekout
        a.append(dk / (2 * m))

    q = 0.0
    for ei, ai in zip(e, a):
        q += (ei - ai ** 2)

    return q


if __name__ == '__main__':
    from analysis_dataset import add_douhao

    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (0, 3), (2, 3), (4, 6), (4, 8), (6, 7), (9, 11), (10, 13),
                      (1, 2), (1, 3), (2, 4),
                      (4, 5), (4, 7), (5, 6),
                      (5, 7), (5, 8), (6, 8),
                      (7, 8), (7, 10), (8, 9),
                      (9, 10), (9, 12), (9, 13),
                      (10, 11), (10, 12), (11, 12),
                      (11, 13), (12, 13)])
    paration = [{0, 1, 2, 3}, {4, 5, 6, 7, 8}, {9, 10, 11, 12, 13}]
    print cal_Q(paration, G)
    print nx.algorithms.community.modularity(G, paration)

    G = nx.read_gml("./datasets/karate.gml", label="id")
    true_paration = [{1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 17, 18, 20, 22},
                     {9, 10, 15, 16, 19, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                      34}]

    print cal_Q(true_paration, G)
    print nx.algorithms.community.modularity(G, true_paration)


    G = nx.read_gml("./datasets/karate.gml", label="id")
    a = "1 2 3 4 5 6 7 8 10 11 12 13 14 17 18 20 22"
    b = "9 10 15 16 19 21 23 24 25 26 27 28 29 30 31 32 33 34"
    c = add_douhao(a)
    d = add_douhao(b)
    paration = [c, d]
    print calcualte_EQ(paration, G)
