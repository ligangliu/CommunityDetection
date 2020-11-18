# -*- coding: utf-8 -*-#

#------------------------------------------------------------------------------- 
# Author:       liuligang
# Date:         2020/11/11
#-------------------------------------------------------------------------------
import networkx as nx
import math
import numpy as np
import matplotlib.pyplot as plt
from my_util import timefn
import time
from my_util import transfer_2_gml, path, run_platform

# 展示x,y的二维坐标点，用于后面的数据验证
def show_data(xmin=0, xmax=1, ymin=0, ymax=1, x=None, y=None):
    if x is None or y is None:
        return
    plt.title("I'm a scatter diagram.")
    plt.xlim(xmax=xmax, xmin=xmin)
    plt.ylim(ymax=ymax, ymin=ymin)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.plot(x, y, 'ro')
    plt.show()


# 算法执行开始时间，统计这个算法运行花费时间
start_time = time.time()
# 如果是linux环境，则自动生成网络
if run_platform == "linux":
    from my_evaluation import generate_network
    generate_network()

G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (2, 4), (2, 5),
                  (2, 6), (2, 7),
                  (7, 8), (8, 9), (9, 10), (9, 11), (9, 12),
                  (9, 13), (9, 14), (9, 15), (9, 17), (9, 18), (9, 19), (9, 20),
                  (9, 16), (12, 13), (12, 11),
                  (12, 17), (12, 18), (12, 19), (12, 20), (12, 21), (20, 21)], weight=1.0)
G = nx.read_gml(path+"football.gml", label="id")
for edge in G.edges:
    G[edge[0]][edge[1]]['weight'] = 1.0

overlapping_nodes = []
# 处理LFR数据
# G, overlapping_nodes = transfer_2_gml()


# 1) Distance function
a = 0.1  # 计算cc(i,j)的时候使用的，一个较小的正值，避免分母为0的情况
b = 0.1  # 计算dist(i, j)的时候使用的，表示当i,j时孤立的节点的时候
c = 0.8  # 在second_step()分配重叠节点的时候使用的。 todo 11.10 这个在论文后面的实验中有作对比
dc = 0.2  # todo dc取多少？论文中是当dc取2%效果最佳，因为这个直接影响到计算node_p的值


# 计算G中最大权重
def calculate_maxw(need=False):
    if not need:
        return 1.0
    res = 0.0
    for u, v in G.edges:
        res = max(res, G[u][v]['weight'])
    return res


maxw = calculate_maxw()


# 计算cc(i, j)，表示的是节点i,j的共同节点对节点i和节点j的链接强度的共享，因此这个方法应该是考虑的节点的共同邻居节点
def calculate_cc_ij(nodei, nodej, V_ij=None):
    if V_ij is None:
        V_ij = nx.common_neighbors(G, nodei, nodej)
    t = 0.2  # todo 11.09 后面的实验中，t的值是做了变化的，0.2是最佳的,我们后期也得做个对比
    r = 1.0  # 暂定1.0，todo 没有弄明白论文中的r所指的意思?????
    res = 0.0
    for node in V_ij:
        w_ipj = min(G[nodei][node]['weight'], G[nodej][node]['weight'])
        # 其实这里会发现，针对如果是无权重的图(即有边的)
        temp = math.pow(((w_ipj - maxw) / (r * t + a)), 2)
        res = res + w_ipj * math.exp(-temp)
    return res


def calculate_node_outgoing_weight(node):
    res = 0.0
    for n in G.neighbors(node):
        res = res + G[node][n]['weight']
    return res


node_outgoing_weight_dict = {}
for node in G.nodes:
    outgoing_weight = calculate_node_outgoing_weight(node)
    node_outgoing_weight_dict[node] = outgoing_weight

# 计算整个网络的权重和
all_outgoing_weight = len(G.edges) * 2


# 计算ls(i, j)，同时考虑直接链接权重和共同节点的共享，所以讲道理这个函数是考虑的cc(i,j)和i,j的之间的权重值
def calculate_ls_ij(nodei, nodej):
    V_ij = list(nx.common_neighbors(G, nodei, nodej))
    cc_ij = calculate_cc_ij(nodei, nodej, V_ij)
    # i,j之间有边连接
    if G.has_edge(nodei, nodej):
        A_ij = G[nodei][nodej]['weight']
    else:
        A_ij = 0.0
    # 表示i, j之间没有共同邻居, 这里不用管两个节点之前是否又共同邻居
    # if len(V_ij) == 0:
    #     return 0.0
    # I_i = calculate_node_outgoing_weight(nodei)
    I_i = node_outgoing_weight_dict[nodei]
    # I_j = calculate_node_outgoing_weight(nodej)
    I_j = node_outgoing_weight_dict[nodej]
    res = ((cc_ij + A_ij) * (len(V_ij) + 1)) / min(I_i, I_j)
    return res


# 计算节点i,j的distance
def calculate_dist_ij(nodei, nodej):
    # 判断两个节点中是否存在至少一个节点为孤立节点
    if G.degree(nodei) == 0 or G.degree(nodej) == 0:
        ls_ij = 0.0
    else:
        ls_ij = calculate_ls_ij(nodei, nodej)
    res = 1 / (ls_ij + b)
    return res, ls_ij


# 初始化所有的节点之间的距离
@timefn  # 统计一下该函数调用花费的时间
def init_dist_martix():
    n = len(G.nodes)
    # 这里需要注意一点，因为使用了二维数组存储节点之间的dist数据，所以节点必须以数字表示，
    # 并且节点的下标必须是以0或者1开始
    # 对于非数字的graph，需要map转换一下
    dist_martix = [[1 / b for i in range(n + 1)] for i in range(n + 1)]
    ls_martix = [[0 for i in range(n + 1)] for i in range(n + 1)]
    # a = np.zeros([n+1, n+1])
    nodes = sorted(list(G.nodes))
    length = len(nodes)
    for i in range(0, length):
        nodei = nodes[i]
        if G.degree(nodei) == 0:
            continue
        for j in range(i + 1, length):
            nodej = nodes[j]
            if dist_martix[nodei][nodej] == 1 / b:
                dist_ij, ls_ij = calculate_dist_ij(nodei, nodej)
                dist_martix[nodei][nodej] = dist_ij
                dist_martix[nodej][nodei] = dist_ij
                ls_martix[nodei][nodej] = ls_ij
                ls_martix[nodej][nodei] = ls_ij
    return dist_martix, ls_martix


# ls_martix主要在second_step中使用到了，所以在这一步也初始化好
dist_martix, ls_martix = init_dist_martix()


# for i in range(len(dist_martix)):
#     for j in range(len(dist_martix[i])):
#         print i, j, dist_martix[i][j]


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
        self.node_w = 0.0  # 表示某个节点的所占的权重
        self.node_w_1 = 0.0
        self.is_center_node = False  # 表示该节点是否为中心节点，默认都不是，因为中心节点是需要选出来的
        self.is_enveloped_node = True  # 是否为包络节点（讲道理，这里是不是定义为是否为重叠节点更加合适？论文是这么定义的）
        self.communities = []  # 表示每个节点划分的社区编号，因为是重叠社区，一个节点可能隶属多个社区

    def gatherAttrs(self):
        return ",".join("{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())

    # 对节点的信息打印重写，方便程序打印输出
    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gatherAttrs())


# 计算一个节点的knn的邻居节点的集合 todo 这个方法有很严重的歧义，中英文版的论文给的不一样
def calculate_node_knn_neighbor(nodei):
    knn_nodes = nx.neighbors(G, nodei)
    # 我个人觉得这里不一定是邻居节点,应该是将所有的节点的dist进行排序，取最近的k个节点
    # knn_nodes = [node for node in G.nodes if node != nodei]
    # 得到节点的所有邻居节点之间的dist
    node_neighbors_dist_tuple_list = [(x, dist_martix[nodei][x]) for x in knn_nodes]
    # 对所有的邻居节点进行排序········································
    node_neighbors_dist_tuple_list = sorted(node_neighbors_dist_tuple_list, key=lambda x: x[1])
    # 找到最小的k个邻居节点
    res = []
    k = len(node_neighbors_dist_tuple_list)
    knn = calculate_knn()
    # 如果不够就取所有的
    if k < knn:
        knn = k
    for i in range(knn):
        nodej = node_neighbors_dist_tuple_list[i][0]
        res.append(nodej)
    return res


node_knn_neighbors_dict = {}
for node in G.nodes:
    knn_neighbors = calculate_node_knn_neighbor(node)
    node_knn_neighbors_dict[node] = knn_neighbors


# 计算每个节点的揉
def calculate_nodep(node):
    # 找到最小的k个邻居节点，这里不按照论文的来，这里就是算所有邻居节点
    # knn_neighbors = calculate_node_knn_neighbor(node)
    # knn_neighbors = node_knn_neighbors_dict.get(node)
    knn_neighbors = list(G.neighbors(node))
    res = 0.0
    # 如果不够就取所有的
    for knn_neighbor in knn_neighbors:
        # a = float(dist_martix[node][knn_neighbor])
        temp = math.pow((float(dist_martix[node][knn_neighbor]) / dc), 2)
        res = res + math.exp(-temp)
    return res


# 初始化所有的节点的信息
@timefn
def init_all_nodes_info():
    res = []
    all_node_p = []
    all_node_w = []
    # 1) 初始化所有的
    for node in G.nodes:
        node_p = calculate_nodep(node)
        # node_w = calculate_node_outgoing_weight(node)
        node_w = node_outgoing_weight_dict[node]
        t = NodeInfo()
        t.node = node
        t.node_p = node_p
        t.node_w = node_w
        res.append(t)
        all_node_p.append(node_p)
        all_node_w.append(node_w)

    # 2) 对揉进行归一化
    min_node_p = min(all_node_p)
    max_node_p = max(all_node_p)
    min_node_w = min(all_node_w)
    max_node_w = max(all_node_w)
    for node_info in res:
        node_p = node_info.node_p
        node_p_1 = (node_p - min_node_p) / (max_node_p - min_node_p)
        node_info.node_p_1 = node_p_1
        node_w = node_info.node_w
        node_w_1 = (node_w - min_node_w) / (max_node_w - min_node_w)
        node_info.node_w_1 = node_w_1

    # 3) 初始化所有节点的伽马
    # 计算每个节点的伽马函数，由于这个方法外部不会调用，就暂且定义在方法内部吧，问题不大！
    def calculate_node_g(nodei, node_list):
        if len(node_list) == 0:
            return 1.0 / b
        temp = []
        for nodej in node_list:
            # todo 11.10 这里乘以2的原因是，在一个社区里面，如果有两个带头大哥，我要尽量的将第二个带太大哥的重要性降低，所以我在这里乘以2将这个重要程度尽量放大
            # 并且这个我已经从实验数据debug证明了
            temp.append(2 * dist_martix[nodei][nodej])
        return min(temp)

    # 按照所有节点的揉进行升序排序
    res = sorted(res, key=lambda x: x.node_p)
    all_node_g = []
    for i in range(len(res)):
        # 当揉为最大的时候，取最大的dist
        if i == len(res) - 1:
            res[i].node_g = max(all_node_g)
            all_node_g.append(res[i].node_g)
        else:
            node_info = res[i]
            node = node_info.node
            # 因为res是根据揉排好序的，所有i之后的所有节点对应的揉都是大于当前的, 这里应该是需要加上后面的if
            node_list = [res[x].node for x in range(i + 1, len(res)) if res[x].node_p > node_info.node_p]
            node_g = calculate_node_g(node, node_list)
            # todo 想不通为什么这里会有计算出node_g = 10.0的情况？？？？
            if node_g == 1.0 / b:
                node_g = res[i - 1].node_g
            all_node_g.append(node_g)
            node_info.node_g = node_g
    # 4) 对所有的节点的伽马进行归一化，并且求出r
    max_node_g = max(all_node_g)
    min_node_g = min(all_node_g)
    for node_info in res:
        node_g = node_info.node_g
        node_g_1 = (node_g - min_node_g) / (max_node_g - min_node_g)
        node_info.node_g_1 = node_g_1
        # 且顺便计算出node_r
        node_r = node_info.node_p_1 * node_info.node_g_1 * node_info.node_w_1
        node_info.node_r = node_r
    return res


# all_nodes_info_list 很重要，所有节点的信息统一放在这个list中
all_nodes_info_list = init_all_nodes_info()


# 打印一下初始化之后的节点的信息，所有节点按照p进行排序
def print_node_info():
    for node_info in all_nodes_info_list:
        print "节点： { %s } node_p_1的值: { %f } node_g_1的值：{ %f } node_r的值： { %f } " \
              % (node_info.node, node_info.node_p_1, node_info.node_g_1, node_info.node_r)
# print_node_info()

# all_nodes_info_dict 便于后面从filter_node_list中通过node信息来更新到all_nodes_info_list上的信息
all_nodes_info_dict = {node_info.node: node_info for node_info in all_nodes_info_list}

# 这个保存一下所有节点按照揉进行排序之后的节点编号的变化信息，只是用来清晰的记录那个节点的揉的值是最大的而已
ascending_nod_p_node_id_list = []

# 因为此时的所有的all_nodes_info_list 是按照node_p进行升序的
for node_info in all_nodes_info_list:
    ascending_nod_p_node_id_list.append(node_info.node)

print '-' * 30
print 'ascending_nod_p node: ' + str(ascending_nod_p_node_id_list)
print '-' * 30


def node_p_1_g_1_to_xy(nodes_info_list):
    x = []
    y = []
    z = []
    count = 1
    for node_info in nodes_info_list:
        x.append(count)
        y.append(node_info.node_p_1)
        z.append(node_info.node_g_1)
        # print node_info.node, node_info.node_p_1, node_info.node_g_1
        count += 1
    return x, y, z


x, y, z = node_p_1_g_1_to_xy(all_nodes_info_list)


# show_data(xmax=len(x), x=x, y=y)
# show_data(xmax=len(x), x=x, y=z)

# 讲道理这里应该还需要过滤一些更不不可能成为clustering node的节点
# todo 有待确认论文中的逻辑是否是这样的？？？？
def filter_corredpond_nodes(all_nodes_info_list):
    sum_node_r = 0.0
    all_nodes_info_list = sorted(all_nodes_info_list, key=lambda x: x.node_p)
    count = int(0.8 * len(all_nodes_info_list))
    sum_node_p = 0.0
    for i in range(count):
        sum_node_p += all_nodes_info_list[i].node_p
    averge_eighty_percen_node_p = float(sum_node_p) / count

    sum_node_r = 0.0
    all_nodes_info_list = sorted(all_nodes_info_list, key=lambda x: x.node_r)
    for i in range(count):
        sum_node_r += all_nodes_info_list[i].node_r
    averge_eighty_percen_node_r = float(sum_node_r) / count

    filter_nodes_info_list = []
    for node_info in all_nodes_info_list:
        if node_info.node_p < averge_eighty_percen_node_p or node_info.node_r < averge_eighty_percen_node_r:
            pass
        else:
            filter_nodes_info_list.append(node_info)
            sum_node_r += node_info.node_r
    averge_node_r = sum_node_r / len(filter_nodes_info_list)
    return filter_nodes_info_list, averge_node_r


# 按照node_r进行排序,因为论文的算法二中选择中心节点就是使用的过滤之后的节点进行筛选的
filter_nodes_info_list, averge_node_r = filter_corredpond_nodes(all_nodes_info_list)
# all_nodes_info_list = sorted(all_nodes_info_list, key=lambda x: x.node_r)
filter_nodes_info_list = sorted(filter_nodes_info_list, key=lambda x: x.node_r)

# 这个保存一下所有节点按照node_r进行排序之后的节点编号的变化信息，只是用来清晰的记录那个节点的揉的值是最大的而已
ascending_nod_r_node_id_list = []

# 因为此时的所有的all_nodes_info_list 是按照node_p进行升序的
for node_info in filter_nodes_info_list:
    ascending_nod_r_node_id_list.append(node_info.node)
print '-' * 30
print 'ascending_node_r node: ' + str(ascending_nod_r_node_id_list)
print '-' * 30


# 初始化所有的节点的node_dr信息，并返回最大的node_dr以及对应的index
def init_filter_nodes_dr():
    # 第一个节点应该是没有node_dr的，所以从第二个节点开始
    for i in range(1, len(filter_nodes_info_list)):
        a = filter_nodes_info_list[i - 1]
        b = filter_nodes_info_list[i]
        node_dr = b.node_r - a.node_r
        b.node_dr = node_dr


# 初始化所有没有被过滤的节点的d伽马
init_filter_nodes_dr()


def nodes_r_node_dr_to_xy(nodes_info_list):
    x = []
    y = []
    z = []
    count = 1
    for node_info in nodes_info_list:
        x.append(count)
        y.append(node_info.node_r)
        if count == 1:
            z.append(1.0)
        else:
            z.append(node_info.node_dr)
        count += 1
    return x, y, z


x, y, z = nodes_r_node_dr_to_xy(filter_nodes_info_list)

# show_data(xmax=len(x), x=x, y=y)
# show_data(xmax=len(x), x=x, y=z)


# ================================================================================
# 以上的所有代码应该是初始化好了所有的节点的信息，
# 包括揉，伽马，还有d伽马等信息。那么讲道理下面的步骤就应该是
# 1) 自动计算中心节点
# 2) 将节点划分到对应的社区
# ================================================================================

# 得到一维的线性拟合的参数a和b
def calculate_predict_node_dr(node_info_list, node_index):
    list_x = []
    list_y = []
    for i in range(len(node_info_list)):
        node_info = node_info_list[i]
        list_x.append(i + 1)
        list_y.append(node_info.node_dr)
    z = np.polyfit(list_x, list_y, 1)
    return z[0] * node_index + z[1]


# list_x = [1, 2, 3, 4, 5, 6]
# list_y = [2.5, 3.51, 4.45, 5.52, 6.47, 7.51]
# print calculate_linear_fitting_number(list_x, list_y, 8)
# 可以在这一步打印出节点的一些信息，进行验证
# for node in all_nodes_info_list:
#     print node.node, node.node_r, node.node_dr

# 算法二的核心，自动计算出node center
@timefn
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
        # 将所有的前面的进行拟合
        node_info_list = node_info_list[0:max_index]
        if len(node_info_list) < 3 or temp_node_info.node_dr < averge_node_r:
            break
        predict_node_dr = calculate_predict_node_dr(node_info_list, max_index)
        # todo 这么定义和论文不一样，到时候一起讨论一下？？？？
        if 2 * (true_node_dr - predict_node_dr) > true_node_dr:
            res = max_index
        else:
            break
    return res


# filter_nodes_info_list_index 表示的是过滤的节点的list的下标之后的所有节点为中心节点
filter_nodes_info_list_index = selec_center(filter_nodes_info_list)
print filter_nodes_info_list_index, len(filter_nodes_info_list)


# 初始化所有的中心节点,因为后面的节点划分社区都需要用到这个
def init_center_node():
    center_node_dict = {}
    comunity = 1
    for i in range(filter_nodes_info_list_index, len(filter_nodes_info_list)):
        filter_node_info = filter_nodes_info_list[i]
        node_info = all_nodes_info_dict.get(filter_node_info.node)
        node_info.is_center_node = True
        # 设置中心节点的社区，从编号1开始
        node_info.communities.append(comunity)
        # 将center_node的信息加入到center_node_list中，因为first_step会使用到该信息
        center_node_dict[node_info.node] = comunity
        comunity += 1
    return center_node_dict


center_node_dict = init_center_node()

center_nodes = sorted(list(center_node_dict.keys()))
# 第一步将所有的非中心节点进行划分
@timefn
def first_step():
    node_community_dict = center_node_dict.copy()
    for node_info in all_nodes_info_list:
        if node_info.is_center_node == False:
            community = -1
            min_dist = -1000000
            # todo 这里什么叫距离最近，局部密度更改的节点？先按距离排序，再按局部密度排序？？？
            for node in center_node_dict.keys():
                # todo 11.8 这里明显有点问题，不能这么弄，因为dist的值只是表示两个节点通过邻居节点进行的一种联系，讲道理这里不应该只是这个，比如两个节点之间直接相连反而会低于有邻居的情况
                # todo 11.8 在这里加上一个节点i和节点j之间的权重，因为在first_step()对于一些边上的节点可能会导致因为有一个公共邻居而使得结果反而优先于直接相连的情况
                node_ij_weight = 0.0
                if G.has_edge(node_info.node, node):
                    node_ij_weight = G[node_info.node][node]['weight']
                ls_ij = ls_martix[node_info.node][node] + node_ij_weight
                if ls_ij > min_dist:
                    community = center_node_dict.get(node)
                    min_dist = ls_ij
            node_info.communities.append(community)
            # 这个结构主要是下面判断一个节点是否为包络节点需要使用到，所以在这里返回出去
            node_community_dict[node_info.node] = community
    return node_community_dict


# 讲道理到了这一步之后，所有的节点都是已经划分了一个社区的，然后通过second_step()进行二次划分，将重叠节点找出来，并划分
node_community_dict = first_step()


# 计算每个节点的knn个邻居节点的ls的值之和
def calculate_node_knn_neighboor_ls(nodei, knn_node_neighbors, comminity=None):
    res = 0.0
    for nodej in knn_node_neighbors:
        if comminity is None:
            res += ls_martix[nodei][nodej]
        else:
            if node_community_dict.get(nodej) == comminity:
                res += ls_martix[nodei][nodej]
    return res


# 计算非包络节点的membership, 用于二次划分时将该节点划分到一个新的社区
def calculate_node_membership(nodei):
    # 得到nodei的knn的邻居节点
    # nodei_knn = calculate_node_knn_neighbor(nodei)
    nodei_knn = node_knn_neighbors_dict[nodei]
    # 得到nodei的knn个邻居节点以及它们的划分社区信息
    # node_knn_node_to_community_dict = [{node: node_community_dict.get(node)} for node in nodei_knn_neighbors]
    node_knn_community_to_node_dict = {}
    for nodej in nodei_knn:
        nodej_community = node_community_dict.get(nodej)
        if node_knn_community_to_node_dict.has_key(nodej_community):
            node_knn_community_to_node_dict.get(nodej_community).append(nodej)
        else:
            node_knn_community_to_node_dict[nodej_community] = [nodej]
    node_membership_dict = {}
    # 对于每一个接待你进行划分
    for community_c in node_knn_community_to_node_dict.keys():
        res = 0.0
        node_knn_c = node_knn_community_to_node_dict.get(community_c)
        for nodej in node_knn_c:
            # nodej_knn = calculate_node_knn_neighbor(nodej)
            nodej_knn = node_knn_neighbors_dict[nodej]
            a = calculate_node_knn_neighboor_ls(nodej, nodej_knn, community_c)
            b = calculate_node_knn_neighboor_ls(nodej, nodej_knn)
            res += ls_martix[nodei][nodej] * (a / b)
        # 更新结果
        node_membership_dict[community_c] = res
    return node_membership_dict


# 非包络节点
not_enveloped_nodes = []


# 划分重叠节点出来
@timefn
def second_step():
    for node_info in all_nodes_info_list:
        nodei = node_info.node
        if not node_info.is_center_node:
            # 计算该节点是否为包络节点
            node_neighbors = list(nx.neighbors(G, nodei))
            community = node_info.communities[0]
            # 统计一下它的所有邻居节点和自身在同一个社区的情况
            same_community_sum = 0
            community_set = set()
            for node_neighbor in node_neighbors:
                community_set.add(node_community_dict.get(node_neighbor))
                if node_community_dict.get(node_neighbor) == community:
                    same_community_sum += 1
            # 说明改节点和周围的所有节点在一个社区中,或者它和它的邻居有一半的社区是相同的(todo 11.10 后面这一点是我添加的)
            if same_community_sum == len(node_neighbors) or \
                    same_community_sum > len(node_neighbors) * 0.5:
                pass
            else:
                # 说明该节点就不是包络节点
                node_info.is_enveloped_node = False
                not_enveloped_nodes.append(node_info.node)
            # 如果不是包络节点，那么会进行二次划分
            if not node_info.is_enveloped_node:
                # 1) 如果该节点和它的所有邻居划分社区都不相同，那么该节点先不管 # todo 论文中归感觉没有考虑这一点
                # 说明该节点和所有的邻居节点的社区中不包含该节点划分的社区，这种情况不管
                # nodei_knn_neighbors = calculate_node_knn_neighbor(nodei)
                nodei_knn_neighbors = node_knn_neighbors_dict[nodei]
                # 得到该节点的knn个最近的邻居节点的所有社区信息
                node_knn_neighbors_community = set([node_community_dict.get(node) for node in nodei_knn_neighbors])
                if community not in node_knn_neighbors_community:
                    pass
                else:
                    node_membership_dict = calculate_node_membership(nodei)
                    # 遍历所有的knn节点的membership值，判断该节点是否划分到多个社区
                    nodei_community = node_community_dict.get(nodei)
                    nodei_membership = node_membership_dict.get(nodei_community)
                    node_membership_dict.pop(nodei_community)
                    for community_c in node_membership_dict:
                        if nodei_membership == 0.0:
                            # todo 这里会存在nodei_membership为0的情况，到时候再排查一下原因，先暂定跳过
                            break
                        t = node_membership_dict.get(community_c) / nodei_membership
                        if (t >= c):
                            # 说明需要将该节点划分到对应的社区
                            node_info.communities.append(community_c)
        else:
            pass


second_step()

# 打印输出中心节点
print '-' * 30
print "center nodes: " + str(center_nodes)
print "not enveloped nodes: " + str(not_enveloped_nodes)
print '-' * 30

# 打印社区划分的节点
print "==================================="
community_nodes_dict = {}
for node_info in all_nodes_info_list:
    node = node_info.node
    communities = node_info.communities
    for community in communities:
        if community_nodes_dict.has_key(community):
            community_nodes_dict.get(community).append(node)
        else:
            community_nodes_dict[community] = [node]
# 打印每个社区编号，以及分配到该社区的节点信息
print "发现的社区个数： " + str(len(community_nodes_dict))
# 用于统计一下我的算法发现了多少个重叠节点
communities_nodes = []

# 将结果集合写入文件
file_handle = open(path+"lfr_code.txt", mode="w")
for key, value in community_nodes_dict.items():
    # print "community: " + str(key)
    value = sorted(value)
    communities_nodes.append(value)
    to_join_list = []
    for x in value:
        to_join_list.append(str(x))
    s = " ".join(to_join_list)
    file_handle.write(s + "\n")
    print s
    # print "---------------------------"

find_overlapping_nodes_dict = {}
# 记录一下重叠节点被划分到的最多的社区个数和最小的社区个数
min_overlapping_communites = 10000
max_overlapping_communites = -10000
for node in G.nodes:
    temp = 0
    for community in communities_nodes:
        if node in community:
            temp += 1
    if temp >= 2:
        if temp < min_overlapping_communites:
            min_overlapping_communites = temp
        if temp > max_overlapping_communites:
            max_overlapping_communites = temp
        # 记录每个重叠节点被划分到了几个社区
        find_overlapping_nodes_dict[node] = temp


# # 重叠节点统计发现的情况
# print overlapping_nodes_dict.keys()
# # 每个重叠节点被划分到的社区个数
# print overlapping_nodes_dict

# 统计一下算法发现的重叠节点和真实的重叠节点的匹配个数
def overlapping_mapping_sum(a=[], b=[]):
    sum = 0
    for node in a:
        if node in b:
            sum += 1
    return sum


print "真实社区重叠节点个数: " + str(len(overlapping_nodes))
print sorted(overlapping_nodes)
print "算法发现的重叠节点个数: " + str(len(find_overlapping_nodes_dict))
print sorted(list(find_overlapping_nodes_dict.keys()))
print "与原重叠节点的mapping个数: " + str(overlapping_mapping_sum(list(find_overlapping_nodes_dict.keys()), overlapping_nodes))
print "重叠节点最多划分到的社区个数: " + str(max_overlapping_communites)
print "重叠节点最少划分到的社区个数: " + str(min_overlapping_communites)

if run_platform == "linux":
    from my_evaluation import calculate_onmi
    print "该程序的onmi的值：" + str(calculate_onmi())

end_time = time.time()
print "程序总共花费的时间：" + str(end_time - start_time)


