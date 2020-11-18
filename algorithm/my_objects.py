# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/11/12
# -------------------------------------------------------------------------------
from collections import defaultdict
import networkx as nx


# 该算法的参数
class AlgorithmParam(object):

    def __init__(self):
        # 生成网络的参数
        self.n = 1000
        self.k = 10
        self.maxk = 40
        self.minc = self.n * 0.04
        self.maxc = self.n * 0.06
        self.mut = 0.2
        self.muw = 0.2
        self.on = 30
        self.om = 2
        # 算法的参数
        self.dataset = "karate.gml"
        self.need_show_image = False
        self.c = 0.8  # 在二次划分的时候[0.2, 0.4, 0.6, 0.8, 1.0]
        self.node_g_weight = 2  # 在node_g_1所占的权重比 [2, 4, 6]
        self.enveloped_weight = 1.0  # 就是是否判断该节点为包络节点占的比重

        self.run_dataset = False
        self.a = 0.5
        self.b = 0.5
        self.need_update_center_nodes = False


# 自定义一个结果集的类，方便后续将实验结果保存到mysql或文件中，甚至方便打印，避免print散落在在各处
class MyResultInof(object):

    def __init__(self):
        self.G = None
        self.true_overlapping_nodes = []  # 网络真实的重叠节点
        self.true_community_num = 0
        self.find_overlapping_nodes = []  # 算法发现的的重叠节点
        self.min_om = 2  # 重叠节点最少划分到的社区个数
        self.max_om = 2  # 重叠节点最多划分到的社区个数
        self.mapping_overlapping_nodes = []  # 真实的重叠节点与网络重叠节点的交集
        self.ascending_nod_p_nodes = []  # 所有按照node_p进行排序之后的nodes
        self.ascending_nod_r_nodes = []  # 所有按照node_r进行排序之后的nodes
        self.center_nodes = []  # 中心节点
        self.ls_zero_nodes = []  # 到所有中心节点的ls都是0的节点
        self.not_enveloped_nodes = []  # 非包络节点
        self.community_nodes_dict = {}  # 每个社区对应的节点集合
        self.not_overlapping_communit_nodes_dict = {}  # 未执行seconde_step(),得到的非重叠节点划分情况
        self.node_community_dict = defaultdict(list)  # 每个节点对应的社区信息

        # 以下是算法的评估值
        self.onmin = 0.0  # 算法得到onmi值

        self.spend_seconds = 0  # 算法执行消耗的时间(单位s)


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


class GN_w:
    def __init__(self, G):
        self.G_copy = G.copy()
        self.G = G
        self.partition = [[n for n in G.nodes()]]
        self.all_Q = [0.0]
        self.max_Q = 0.0

    # Using max_Q to divide communities
    def run(self):
        while len(self.G.edges()) != 0:
            edges = {}
            edges_betweenness_centrality = nx.edge_betweenness_centrality(self.G)

            for e, ebc in edges_betweenness_centrality.items():
                edge_weight = ebc / self.G.get_edge_data(e[0], e[1])['weight']
                edges[e] = edge_weight

            edge = max(edges.items(), key=lambda item: item[1])[0]
            self.G.remove_edge(edge[0], edge[1])
            components = [list(c) for c in list(nx.connected_components(self.G))]
            if len(components) != len(self.partition):
                # compute the Q
                cur_Q = self.cal_Q(components, self.G_copy)
                if cur_Q not in self.all_Q:
                    self.all_Q.append(cur_Q)
                if cur_Q > self.max_Q:
                    self.max_Q = cur_Q
                    self.partition = components

        print('-----------the Max Q and divided communities-----------')
        print('The number of Communites:', len(self.partition))
        print("Communites:", self.partition)
        print('Max_Q:', self.max_Q)
        return self.partition, self.all_Q, self.max_Q

    def run_n(self, k):
        while len(self.G.edges()) != 0:
            edges = {}
            edges_betweenness_centrality = nx.edge_betweenness_centrality(self.G)

            for e, ebc in edges_betweenness_centrality.items():
                edge_weight = ebc / self.G.get_edge_data(e[0], e[1])['weight']
                edges[e] = edge_weight
            edge = max(edges.items(), key=lambda item: item[1])[0]
            self.G.remove_edge(edge[0], edge[1])
            components = [list(c) for c in list(nx.connected_components(self.G))]
            if len(components) <= k:
                # cur_Q = nx.algorithms.community.modularity(self.G_copy, components)
                cur_Q = self.cal_Q(components, self.G_copy)
                if cur_Q not in self.all_Q:
                    self.all_Q.append(cur_Q)
                if cur_Q > self.max_Q:
                    self.max_Q = cur_Q
                    self.partition = components
        print('-----------Using number to divide communities and the Q-----------')
        print('The number of Communites', len(self.partition))
        print("Communites: ", [sorted(paration) for paration in self.partition])
        print('Max_Q: ', self.max_Q)
        return self.partition, self.all_Q, self.max_Q

    # the process of divding the network
    # Return a list containing the result of each division, until each node is a community
    def run_to_all(self):
        divide = []
        all_Q = []
        while len(self.G.edges()) != 0:
            edge = max(nx.edge_betweenness_centrality(self.G).items(), key=lambda item: item[1])[0]
            self.G.remove_edge(edge[0], edge[1])
            components = [list(c) for c in list(nx.connected_components(self.G))]
            if components not in divide:
                divide.append(components)
            cur_Q = self.cal_Q(components, self.G_copy)
            if cur_Q not in all_Q:
                all_Q.append(cur_Q)
        return divide, all_Q


    def add_group(self):
        num = 0
        nodegroup = {}
        for partition in self.partition:
            for node in partition:
                nodegroup[node] = {'group': num}
            num = num + 1
        nx.set_node_attributes(self.G_copy, nodegroup)

    # Computing the Q
    def cal_Q(self, partition, G):
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
