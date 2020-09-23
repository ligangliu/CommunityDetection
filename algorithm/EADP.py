# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/9/14
# -------------------------------------------------------------------------------


import networkx as nx
import math
import numpy as np
import sys

G = nx.Graph()
# G.add_edges_from([(1, 2), (1, 3), (1, 4), (1, 8),
#                   (2, 3), (2, 4),
#                   (3, 5), (3, 6), (3, 7),
#                   (4, 5), (4, 7), (4, 9), (4, 10),
#                   (5, 7)], weight=1.0)
G = nx.read_gml("../datasets/karate.gml", label="id")
for edge in G.edges:
    G[edge[0]][edge[1]]['weight'] = 1.0

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
    t = 0.3
    r = 1.0  # 暂定1.0，todo 没有弄明白论文中的r所指的意思?????
    res = 0.0
    for node in V_ij:
        w_ipj = min(G[nodei][node]['weight'], G[nodej][node]['weight'])
        temp = math.pow(((w_ipj - maxw) / (r * t + a)), 2)
        res = res + w_ipj * math.exp(-temp)
    return res


# todo 有待确认是否是这么计算的？我看论文大概的意思就是这个
def calculate_node_outgoing_weight(node):
    res = 0.0
    for n in G.neighbors(node):
        res = res + G[node][n]['weight']
    return res


# 计算ls(i, j)
def calculate_ls_ij(nodei, nodej):
    cc_ij = calculate_cc_ij(nodei, nodej)
    V_ij = list(nx.common_neighbors(G, nodei, nodej))
    # i,j之间有边连接
    if G.has_edge(nodei, nodej):
        A_ij = G[nodei][nodej]['weight']
    else:
        A_ij = 0.0
    # 表示i, j之间没有共同邻居，todo 但是如果两个节点相连呢？？? 这里有待讨论
    # if len(V_ij) == 0:
    #     return 0.0
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
        self.is_center_node = False  # 表示该节点是否为中心节点，默认都不是，因为中心节点是需要选出来的
        self.is_enveloped_node = True  # 是否为包络节点（讲道理，这里是不是定义为是否为重叠节点更加合适？论文是这么定义的）
        self.communities = []  # 表示每个节点划分的社区编号，因为是重叠社区，一个节点可能隶属多个社区


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
    # 计算每个节点的伽马函数，由于这个方法外部不会调用，就暂且定义在方法内部吧，问题不大！
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
            node_list = [res[x].node for x in range(i + 1, len(res))]
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


# 讲道理这里应该还需要过滤一些更不不可能成为clustering node的节点，暂未实现
def filter_corredpond_nodes(all_nodes_info_list):
    pass


# 按照node_r进行排序
all_nodes_info_list = sorted(all_nodes_info_list, key=lambda x: x.node_r)


# 初始化所有的节点的node_dr信息，并返回最大的node_dr以及对应的index
def init_all_nodes_dr():
    # 第一个节点应该是没有node_dr的，所以从第二个节点开始
    for i in range(1, len(all_nodes_info_list)):
        a = all_nodes_info_list[i - 1]
        b = all_nodes_info_list[i]
        node_dr = b.node_r - a.node_r
        b.node_dr = node_dr


# 初始化所有节点的d伽马
init_all_nodes_dr()


# ================================================================================
# 以上的所有代码应该是初始化好了所有的节点的信息，
# 包括揉，伽马，还有d伽马等信息。那么讲道理下面的步骤就应该是自动计算中心节点
# 以及将节点划分到对应的社区
# ================================================================================

# 得到一维的线性拟合的参数a和b
def calculate_predict_node_dr(node_info_list, node_x):
    list_x = []
    list_y = []
    for i in range(len(node_info_list)):
        node_info = node_info_list[i]
        list_x.append(i + 1)
        list_y.append(node_info.node_dr)
    z = np.polyfit(list_x, list_y, 1)
    return z[0] * node_x + z[1]


# list_x = [1, 2, 3, 4, 5, 6]
# list_y = [2.5, 3.51, 4.45, 5.52, 6.47, 7.51]
# print calculate_linear_fitting_number(list_x, list_y, 8)

# 算法二的核心，自动计算出node center
def selec_center(node_info_list):
    def calculate_max_node_dr(node_info_list):
        max_index = -1
        max_node_dr = -1
        for i in range(1, len(node_info_list)):
            node_info = node_info_list[i];
            t = node_info.node_dr
            if max_node_dr < t:
                max_node_dr = t
                max_index = i
        return max_node_dr, max_index

    res = -1
    # 这里的循环的过程不就会导致一种结果，那就是只要某个max_index是center，
    # 那么之后的所有节点不就肯定都是啦？？？
    # todo 论文上的重复逻辑没有看懂，不知道是不是我代码所写的这个意思，需要讨论一下？？？？
    while len(node_info_list) > 3:
        _, max_index = calculate_max_node_dr(node_info_list)
        temp_node_info = node_info_list[max_index]
        true_node_dr = temp_node_info.node_dr
        # 将所有的前面的进行你和
        node_info_list = node_info_list[1:max_index]
        predict_node_dr = calculate_predict_node_dr(node_info_list, max_index)
        # todo 这么定义和论文不一样，到时候一起讨论一下？？？？
        if 2 * (true_node_dr - predict_node_dr) > true_node_dr:
            res = max_index
        else:
            break
    return res


# todo 使用空手道的数据，跑出的结果简直不能忍受？？？，有32个节点都是中心节点？？？？肯定上面的某些初始化参数有问题，需要好好讨论一下？？/
res = selec_center(all_nodes_info_list)
print res


# 初始化所有的中心节点,因为后面的节点划分社区都需要用到这个
def init_center_node():
    center_node_dict = {}
    comunity = 1
    for i in range(res, len(all_nodes_info_list)):
        node_info = all_nodes_info_list[i]
        node_info.is_center_node = True
        # 设置中心节点的社区，从编号1开始
        node_info.communities.append(comunity)
        # 将center_node的信息加入到center_node_list中，因为first_step会使用到该信息
        center_node_dict[node_info.node] = comunity
        comunity += 1
    return center_node_dict


center_node_dict = init_center_node()


# 第一步将所有的非中心节点进行划分
def first_step():
    node_community_dict = center_node_dict.copy()
    for node_info in all_nodes_info_list:
        if node_info.is_center_node == False:
            community = -1
            min_dist = sys.maxsize
            # todo 这里什么叫距离最近，局部密度更改的节点？先按距离排序，再按局部密度排序？？？
            for node in center_node_dict.keys():
                if min_dist > dist_martix[node_info.node][node]:
                    community = center_node_dict.get(node)
            node_info.communities.append(community)
            # 这个结构主要是下面判断一个节点是否为包络节点需要使用到，所以在这里返回出去
            node_community_dict[node_info.node] = community
    return node_community_dict


# 讲道理到了这一步之后，所有的节点都是已经划分了一个社区的，然后通过second_step()进行二次划分，将重叠节点找出来，并划分
node_community_dict = first_step()


# 划分重叠节点出来
def second_step():
    for node_info in all_nodes_info_list:
        if node_info.is_center_node == False:
            # 计算该节点是否为包络节点
            node_neighbors = nx.neighbors(G, node_info.node)
            community = node_info.communities[0]
            for node_neighbor in node_neighbors:
                if community != node_community_dict.get(node_neighbor):
                    # 就不是包络节点
                    node_info.is_enveloped_node = False
                    break
            # 如果不是包络节点，那么会进行二次划分
            if node_info.is_enveloped_node == False:
                pass
