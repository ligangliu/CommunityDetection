# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/12/02
# -------------------------------------------------------------------------------

import networkx as nx
from collections import defaultdict
import random
import math
import numpy as np

from my_evaluation import generate_network
from my_objects import AlgorithmParam
from my_util import transfer_2_gml

u = 0.5

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (1, 4), (2, 3),
                  (2, 4), (3, 4),
                  (4, 5), (4, 6), (4, 7), (4, 8), (5, 7),
                  (6, 8), (7, 8)], weight=1.0)


# G = nx.read_gml("./datasets/karate.gml", label="id")
# # 默认边的权重为1.0
# for edge in G.edges:
#     if G[edge[0]][edge[1]].get('weight', -1000) == -1000:
#         G[edge[0]][edge[1]]['weight'] = 1.0

def calculate_node_KN(NB_i, nodei):
    t = 0
    node_KN_dict = defaultdict(list)
    while len(NB_i) > 0 and t < 2:
        NB_i_dict = defaultdict(list)
        for node in NB_i:
            NB_i_dict[node] = list(nx.common_neighbors(G, node, nodei))
        ni_kN = None
        ni_kN_size = -100
        for key, value in NB_i_dict.items():
            if len(value) > ni_kN_size:
                ni_kN = key
                ni_kN_size = len(value)
        gi_KN = NB_i_dict.get(ni_kN)
        gi_KN.append(ni_kN)
        NB_i = [node for node in NB_i if node not in gi_KN]
        t += 1
        node_KN_dict[ni_kN] = gi_KN
    return node_KN_dict


def calculate_L(G1_KN, G2_KN, need_ls=False, ls_matrix=None):
    if need_ls and ls_matrix==None:
        raise Exception("ls_matrix不能为空")
    l = 0
    for nodei in G1_KN:
        for nodej in G2_KN:
            if G.has_edge(nodei, nodej):
                if need_ls:
                    l += ls_matrix[nodei][nodej]
                else:
                    l += G[nodei][nodej]['weight']
    return float(l / 2.0)


def calculate_LC(G1_KN, G2_KN):
    lc_12 = calculate_L(G1_KN, G2_KN)
    lc_1 = calculate_L(G1_KN, G1_KN)
    lc_2 = calculate_L(G2_KN, G2_KN)
    if lc_1 == 0 or lc_2 == 0:
        # 这种应该默认的不是吧重叠候选节点吧
        return u + 1
    lc = max(lc_12 / lc_1, lc_12 / lc_2)
    return lc


# 找到候选的重叠节点
def find_overlapping_candidates(G):
    overlapping_candidate_nodes = []
    for node in list(G.nodes):
        NB_i = list(nx.neighbors(G, node))
        if len(NB_i) == 0:
            continue
        node_KN_dict = calculate_node_KN(NB_i, node)
        if len(node_KN_dict) < 2:
            continue
        node_KNs = node_KN_dict.values()
        G1_KN = node_KNs[0]
        G2_KN = node_KNs[1]
        lc = calculate_LC(G1_KN, G2_KN)
        if lc <= u:
            overlapping_candidate_nodes.append(node)
    return overlapping_candidate_nodes


# 迭代过程中，应该是将这个两个值作为优化目标
def calculate_kkn_rc(communities):
    n = len(G.nodes)
    k = len(communities)
    all_nodes = set(G.nodes)
    kkn = 0
    rc = 0
    for community in communities:
        community_size = len(community)
        kkn = calculate_L(community, community) / community_size
        temp = list(all_nodes - set(community))
        rc = calculate_L(community, temp) / community_size
    return 2 * (n - k) - kkn, rc


def my_xor(a, b):
    if a == b:
        return 0
    else:
        return 1


def calculate_X_t_1(X_t, V_i, Pbest, Gbest, node_position_dict):
    r1 = random.random()
    r2 = random.random()
    w = random.random()
    c1 = 1.494
    c2 = 1.494
    X = []
    V_i_1 = []
    X_t_1 = []

    for i in range(len(X_t)):
        x_i = X_t[i]
        Gbest_i = Gbest[i]
        Pbest_i = Pbest[i]
        v_i = V_i[i]
        t = w * v_i + c1 * r1 * (my_xor(Pbest_i, x_i)) + c2 * r2 * (my_xor(Gbest_i, x_i))
        X.append(t)
        if random.random() >= 1 / (1 + math.exp(-t)):
            sig_v = 0
        else:
            sig_v = 1
        V_i_1.append(sig_v)
        if sig_v == 0:
            x_i_1 = x_i
        else:
            # 表示是重叠节点
            if x_i in [-1, 0]:
                if x_i == -1:
                    x_i_1 = 0
                elif x_i == 0:
                    x_i_1 = -1
            else:
                # todo 待验证这样是否正确
                nodei = list(G.nodes)[i]
                neighbors = nx.neighbors(G, nodei)
                neighbors_positions = [node_position_dict.get(neighbor) for neighbor in neighbors if
                                       node_position_dict.get(neighbor) > 0]
                majority_neighbor = np.argmax(np.bincount(neighbors_positions))
                x_i_1 = majority_neighbor
                # 需要更新
                node_position_dict[nodei] = majority_neighbor
        X_t_1.append(x_i_1)
    return X_t_1





# 算法二的主框架
def MR_MOEA():
    # 1) 得到候选的重叠节点
    overlapping_candidate_nodes = find_overlapping_candidates()

    # 2) 初始化
    P = []
    count = 1
    node_position_dict = {}
    # 位置矢量初始化
    for node in G.nodes:
        if node in overlapping_candidate_nodes:
            node_position = random.choice([0, 1])
        else:
            node_position = count
            count += 1
        P.append(node_position)
        node_position_dict[node] = node_position
    # 速度矢量初始化 todo 是这样的嘛？
    V = []
    for i in range(len(G.nodes)):
        V.append(0)

    # todo 不知道如何初始化
    Pbest = []

if __name__=='__main__':
    for i in range(20):
        param = AlgorithmParam()
        generate_network(param)
        # 处理LFR数据
        G, true_overlapping_nodes, true_community_num = transfer_2_gml()
        # 默认边的权重为1.0
        for edge in G.edges:
            if G[edge[0]][edge[1]].get('weight', -1000) == -1000:
                G[edge[0]][edge[1]]['weight'] = 1.0
        t = find_overlapping_candidates(G)
        sorted(t)
        print true_overlapping_nodes
        print t
        print len(true_overlapping_nodes), len(t), len(set(true_overlapping_nodes) & set(t))
    # node_position_dict = {1: 2, 2: 2, 3: 3, 4: -1, 5: 4, 6: 5, 7: 4, 8: 5}
    # X_t = [2, 2, 3, -1, 4, 5, 4, 5]
    # Gbest = [1, 2, 2, 0, 4, 4, 4, 4]
    # Pbest = [2, 2, 2, 0, 5, 4, 4, 4]
    # V_i = [0, 0, 0, 0, 0, 0, 0, 0]
    # result = calculate_X_t_1(X_t, V_i, Gbest, Pbest, node_position_dict)
    # print result