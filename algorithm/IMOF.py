# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/12/7
# -------------------------------------------------------------------------------

import networkx as nx
import numpy as np
import random


def get_influence(G, i, w1, w2):
    return w1 * nx.algorithms.degree_centrality(G)[i] + \
           w2 * nx.algorithms.betweenness_centrality(G)[i] + \
           (1 - w1 - w2) * nx.algorithms.closeness_centrality(G)[i]


def get_1hop(G, i):
    return list(G.adj[i])


def get_2hop(G, i):
    lk = []
    lj = get_1hop(G, i)
    for node in lj:
        lk.extend(get_1hop(G, node))
    lk = list(set(lk))
    # lk_copy = lk.copy()
    lk_copy = [x for x in lk]
    for node in lk:
        if (node in lj) or (node == i):
            lk_copy.remove(node)
    return lk_copy


def get_3hop(G, i):
    lj = get_1hop(G, i)
    ll = []
    for node in lj:
        ll.extend(get_2hop(G, node))
    ll = list(set(ll))
    lk = get_2hop(G, i)
    ll_copy = ll.copy()
    for node in ll:
        if (node in lj) or (node in lk) or (node == i):
            ll_copy.remove(node)
    return ll_copy


def get_influence_score(G, i, w1, w2, a):
    Oi = get_1hop(G, i)
    sum_Oi = 0
    for j in Oi:
        Oj = list(set(get_1hop(G, j)) & set(get_2hop(G, i)))
        sum_Oj = 0
        for p in Oj:
            # Op = list(set(get_1hop(G, p)) & set(get_3hop(G, i)))
            # sum_Op = 0
            # for l in Op:
            #    sum_Oj += get_influence(G, p, w1, w2)
            # if len(Oj) != 0:
            #   sum_Op = sum_Op/len(Oj)*(1-σ2)
            sum_Oj += get_influence(G, p, w1, w2)
        if (len(Oj) != 0):
            sum_Oj = sum_Oj / len(Oj) * (1 - a)
        sum_Oi += a * get_influence(G, j, w1, w2) + sum_Oj
    if (len(Oi) != 0):
        RSPN3iup = sum_Oi / len(Oi)
    else:
        return 0
    degOi = []
    # Oi = get_2hop(G, i)
    for node in Oi:
        degOi.append(nx.degree(G)[node])
    if len(degOi) != 0:
        RSPN3i = RSPN3iup / max(degOi)
    else:
        RSPN3i = 0
    return RSPN3i


def get_influence_score2(G, i, w1, w2, a):
    Oi = get_1hop(G, i)
    sum_Oi = 0
    for j in Oi:
        sum_Oi += get_influence(G, j, w1, w2)
    if (len(Oi) != 0):
        RSPN3iup = sum_Oi / len(Oi)
    else:
        return 0
    degOi = []
    # Oi = get_2hop(G, i)
    for node in Oi:
        degOi.append(nx.degree(G)[node])
    if len(degOi) != 0:
        RSPN3i = RSPN3iup / max(degOi)
    else:
        RSPN3i = 0
    return RSPN3i


def discount_strategy(G, Z, m, r, influence_score):
    i = 0
    while i < len(Z):
        j = i + 1
        while j < len(Z):
            if Z[j][0] in list(G.adj[Z[i][0]]):
                influence_score[Z[j][0]] *= r
            j += 1
        i += 1
    newdict = {}
    for node, _ in Z:
        newdict[node] = influence_score[node]
    sorted_newdict = sorted(
        newdict.items(), key=lambda item: item[1], reverse=True)
    return sorted_newdict[0:m]


# G：图；g：迭代次数；w1，w2：求I的系数；μ：意见交换率；m：求前m有影响力的点；
# α1：候选点数为α1*m；α2, α3：初始化意见用；β1, β2：初始化意见用；θ：意见交换中相近界限
# λ：RSPN3的相邻折损率；σ1, σ2：求RSPN3的系数


def IMOF_find_top_m(G, w1, w2, m, a1, r, t1):
    influence = {}
    influence_score = {}
    for node in G.nodes:
        influence[node] = get_influence(G, node, w1, w2)
        influence_score[node] = get_influence_score2(G, node, w1, w2, t1)
    t = sorted(influence.items(), key=lambda item: item[1], reverse=True)
    sortedRSPN3 = sorted(influence_score.items(),
                         key=lambda item: item[1], reverse=True)
    top_m = discount_strategy(
        G, sortedRSPN3[0:int(a1 * m)], m, r, influence_score)
    return top_m, influence


def IMOF_add_informed_agents(G, top_m):
    for node_influence_score in top_m:
        node = node_influence_score[0]
        lastnode = list(G.nodes)[-1] + 1
        G.add_node(lastnode)
        G.add_edge(node, lastnode)


G = nx.Graph()

G = nx.read_gml("./datasets/karate.gml", label="id")

a = nx.algorithms.degree_centrality(G)
a = sorted(a.items(), key=lambda item: item[1], reverse=True)
b = nx.algorithms.betweenness_centrality(G)
b = sorted(b.items(), key=lambda item: item[1], reverse=True)
c = nx.algorithms.closeness_centrality(G)
c = sorted(c.items(), key=lambda item: item[1], reverse=True)
get_influence(G, 1, 0.4, 0.4)

influence = {}
for node in list(G.nodes):
    influence[node] = get_influence(G, node, 0.8, 0.13)
t = sorted(influence.items(), key=lambda item: item[1], reverse=True)
print t
# top_m, influence = IMOF_find_top_m(G=G, w1=0.33, w2=0.33, m=6,
#                                    a1=2, r=0.9, t1=0.5)
# print top_m

# IMOF_add_informed_agents(G, top_m)
# avg_opinion = IMOF_opinion_update(
#     G, top_m, w1=0.33, w2=0.33, g=500, α2=1.2, α3=0.75, β1=0.6, β2=0.3, influence=influence, μ=0.5, θ=0.9
# )
# print avg_opinion
