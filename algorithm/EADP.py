# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/9/14
# -------------------------------------------------------------------------------


import networkx as nx
import math
import numpy as np

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (1, 4), (1, 8),
                  (2, 3), (2, 4),
                  (3, 5), (3, 6), (3, 7),
                  (4, 5), (4, 7), (4, 9), (4, 10),
                  (5, 7)], weight=1.0)

# 1) Distance function
a = 0.001
b = 0.001


# 计算G中最大权重
def calculate_maxw(need=False):
    if not need:
        return 1.0
    res = 0.0
    for u, v in G.edges:
        res = max(res, G[u][v]['weight'])
    return res


# 计算cc(i, j)
def calculate_cc_ij(nodei, nodej):
    V_ij = nx.common_neighbors(G, nodei, nodej)
    maxw = calculate_maxw()
    t = 0.5
    r = 1.0  # 暂定1.0，没有弄明白论文中的r所指的意思?????
    res = 0.0
    for node in V_ij:
        w_ipj = min(G[nodei][node]['weight'], G[nodej][node]['weight'])
        temp = math.pow(((w_ipj - maxw) / (r * t + a)), 2)
        res = res + w_ipj * math.exp(-temp)
    return res


# 有待确认是否是这么计算的？我看论文大概的意思就是这个
def calculate_node_outgoing_weight(node):
    res = 0.0
    for n in G.neighbors(node):
        res = res + G[node][n]['weight']
    return res


# 计算ls(i, j)
def calculate_ls_ij(nodei, nodej):
    cc_ij = calculate_cc_ij(nodei, nodej)
    V_ij = list(nx.common_neighbors(G, nodei, nodej))
    # i,j之间右边
    if G.has_edge(nodei, nodej):
        A_ij = G[nodei][nodej]['weight']
    else:
        A_ij = 0.0
    # 表示i, j之间没有共同邻居，但是如果两个节点相连呢？？? 这里有待讨论
    if len(V_ij) == 0:
        return 0.0
    I_i = calculate_node_outgoing_weight(nodei)
    I_j = calculate_node_outgoing_weight(nodej)
    res = ((cc_ij + A_ij) * (len(V_ij) + 1)) / min(I_i, I_j)
    return res


# 计算节点i,j的distance
def calculate_dist_ij(nodei, nodej):
    ls_ij = calculate_ls_ij(nodei, nodej)
    res = 1 / (ls_ij + b)
    return res


# 初始化所有的节点之间的距离
def init_dist_martix():
    n = len(G.nodes)
    dist_martix = [[0 for i in xrange(n + 1)] for i in xrange(n + 1)]
    max_dist = -100
    # a = np.zeros([n+1, n+1])
    for nodei in G.nodes:
        for nodej in G.nodes:
            if nodei != nodej and dist_martix[nodei][nodej] == 0:
                temp = calculate_dist_ij(nodei, nodej)
                max_dist = max(max_dist, temp)
                dist_martix[nodei][nodej] = temp
                dist_martix[nodej][nodei] = temp
    return dist_martix, max_dist


dist_martix, max_dist = init_dist_martix()


# for i in range(len(dist_martix)):
#     for j in range(len(dist_martix[i])):
#         print dist_martix[i][j]


# 求网络的平均度
def calculate_knn():
    sum = 0
    # 返回的是每个节点的度的情况
    node_degree_tuple = nx.degree(G)
    for _, degree in node_degree_tuple:
        sum += degree
    return int(sum / len(node_degree_tuple))


# 将节点的所有信息统一定义为一个类，之后节点想过的所有信息应该统一放在NodeInfo中
class NodeInfo(object):

    def __init__(self):
        self.node = None
        self.node_p = 0.0  # 表示的就是节点的揉
        self.node_g = 0.0  # 表示的就是节点的伽马
        self.node_p_1 = 0.0  # 表示的归一化之后的揉
        self.node_g_1 = 0.0  # 表示的归一化之后的伽马
        self.node_r = 0.0  # 表示的就是归一化之后的揉*伽马
        self.node_dr = 0.0

    # 计算每个节点的揉


def calculate_nodep(node, knn):
    dc = 0.5
    node_neighbors = nx.neighbors(G, node)
    # 得到节点的所有邻居节点之间的dist
    node_neighbors_dist_tuple_list = [(x, dist_martix[node][x]) for x in node_neighbors]
    # 对所有的邻居节点进行排序
    node_neighbors_dist_tuple_list = sorted(node_neighbors_dist_tuple_list, key=lambda x: x[1])
    # 找到最小的k个邻居节点
    res = 0.0
    k = len(node_neighbors_dist_tuple_list)
    # 如果不够就取所有的
    if k < knn:
        knn = k
    for i in range(knn):
        temp = math.pow((float(node_neighbors_dist_tuple_list[i][1]) / dc), 2)
        res += math.exp(-temp)
    return res


# 初始化所有的节点的信息
def init_all_nodes_info():
    knn = calculate_knn()
    res = []
    all_node_p = []
    # 1) 初始化所有的
    for node in G.nodes:
        node_p = calculate_nodep(node, knn)
        t = NodeInfo()
        t.node = node
        t.node_p = node_p
        res.append(t)
        all_node_p.append(node_p)
    # 2) 对揉进行归一化
    min_node_p = min(all_node_p)
    max_node_p = max(all_node_p)
    for node_info in res:
        node_p = node_info.node_p
        node_info.node_p_1 = (node_p - min_node_p) / (max_node_p - min_node_p)

    # 3) 初始化所有节点的伽马
    def calculate_node_g(nodei, node_list):
        temp = []
        for nodej in node_list:
            temp.append(dist_martix[nodei][nodej])
        return min(temp)

    # 按照所有节点的揉进行升序排序
    res = sorted(res, key=lambda x: x.node_p)
    all_node_g = []
    for i in range(len(res)):
        # 当揉为最大的时候，取最大的dist
        if i == len(res) - 1:
            res[i].node_g = max_dist
            all_node_g.append(max_dist)
        else:
            node_info = res[i]
            node = node_info.node
            # 因为res是根据揉排好序的，所有i之后的所有节点对应的揉都是大于当前的
            node_list = [res[x].node for x in range(i, len(res))]
            node_g = calculate_node_g(node, node_list)
            all_node_g.append(node_g)
            node_info.node_g = node_g
    # 4) 对所有的节点的伽马进行归一化，并且求出r
    max_node_g = max(all_node_g)
    min_node_g = min(all_node_g)
    for node_info in res:
        node_g = node_info.node_g
        node_info.node_g_1 = (node_g - min_node_g) / (max_node_g - min_node_g)
        # 且顺便计算出node_r
        node_info.node_r = node_info.node_p_1 * node_info.node_g_1
    return res


# all_nodes_info_list 很重要，所有节点的信息统一放在这个list中
all_nodes_info_list = init_all_nodes_info()


# 得到一维的线性拟合的参数a和b
def calculate_linear_fitting_number(list_x, list_y, n):
    z = np.polyfit(list_x, list_y, 1)
    return z[0] * n + z[1]

# list_x = [1, 2, 3, 4, 5, 6]
# list_y = [2.5, 3.51, 4.45, 5.52, 6.47, 7.51]
# print calculate_linear_fitting_number(list_x, list_y, 8)
