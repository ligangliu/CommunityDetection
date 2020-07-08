# -*- coding: utf-8 -*-
import itertools
from collections import defaultdict

import networkx as nx
import matplotlib.pyplot as plt
import sys

sys.path.append('../')

'''
    paper:<<Community structure in social and biological networks>>
'''
'''
GN 算法的思想：
    1. 涉及到的知识 a: 介数和边介数  边: 模块度函数Q
    2. 算法步骤
        1）计算网络中所有所有边的边介数
        2）删除上一步计算出来的最大边介数
        3）重复步骤2，直到每一个节点成为一个独立的社团，即网络中不存在边
'''

class GN:
    def __init__(self, G):
        self.G_copy = G.copy()
        self.G = G
        self.partition = [[n for n in G.nodes()]]
        self.all_Q = [0.0]
        self.max_Q = 0.0

    def run(self):
        while len(self.G.edges()) != 0:
            # nx.edge_betweenness_centrality 返回的是类似于 {('C', 'F'): 0.4} 这种结构
            # 计算每天边界数，寻找边届数最大的边
            edge = max(nx.edge_betweenness_centrality(self.G).items(), key=lambda item: item[1])[0]
            # 移除边界数最大的边
            self.G.remove_edge(edge[0], edge[1])
            # List the the connected nodes
            components = [list(c) for c in list(nx.connected_components(self.G))]
            if len(components) != len(self.partition):
                # compute the Q
                # nx.algorithms.community.modularity(self.G_copy, components) 可以直接调用networkx的库函数 等价于 call_Q()
                cur_Q = self.cal_Q(components, self.G_copy)
                if cur_Q not in self.all_Q:
                    self.all_Q.append(cur_Q)
                    # 还可以在这一步做一个map换成call_Q与components的关系
                if cur_Q > self.max_Q:
                    self.max_Q = cur_Q
                    self.partition = components

        print('-----------the Max Q and divided communities-----------')
        print('The number of Communites:', len(self.partition))
        print("Communites:", self.partition)
        print('Max_Q:', self.max_Q)
        return self.partition, self.all_Q, self.max_Q

    # Dividing communities by number  划分成具体的个数的社区
    def run_n(self, k):
        while len(self.G.edges()) != 0:
            edge = max(nx.edge_betweenness_centrality(self.G).items(), key=lambda item: item[1])[0]
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
        print("Communites: ", self.partition)
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

    # Drawing the graph of Q and divided communities
    def draw_Q(self):
        plt.plot([x for x in range(1, len(self.G.nodes) + 1)], self.all_Q)
        my_x_ticks = [x for x in range(1, len(self.G.nodes) + 1)]
        plt.xticks(my_x_ticks)
        plt.axvline(len(self.partition), color='black', linestyle="--")
        plt.axvline(2, color='black', linestyle="--")
        plt.axhline(self.all_Q[3], color='red', linestyle="--")
        plt.show()

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

    def add_group(self):
        num = 0
        nodegroup = {}
        for partition in self.partition:
            for node in partition:
                nodegroup[node] = {'group': num}
            num = num + 1
        # 为每一个节点增加了一个group的属性
        nx.set_node_attributes(self.G_copy, nodegroup)

    def to_gml(self):
        # note: 这里用的是G_copy 并不是G  因为原图G是在不停的删除边的
        # 在add_group 中已经为图中的节点添加了分组信息
        nx.write_gml(self.G_copy, '../datasets/outputofGN.gml')


# networkx -> 边模型转换
def node_networxk_to_edge_networkx(G):
    edge_to_node_dict = defaultdict(tuple)
    node_to_edge_dict = defaultdict(int)
    count = 1
    new_G = nx.Graph()
    for edge in G.edges:
        edge_to_node_dict.setdefault(count, edge)
        node_to_edge_dict.setdefault(edge, count)
        new_G.add_node(count)
        count = count + 1
    # 为新的图构造边
    # 当节点的度大于等于2的时候，才可能构造出边来
    for node in G.nodes:
        if G.degree(node) >= 2:
            nodes_tmp = []
            for edge in G.edges(node):
                if node_to_edge_dict.has_key(edge):
                    nodes_tmp.append(node_to_edge_dict.get(edge))
                if node_to_edge_dict.has_key((edge[1], edge[0])):
                    nodes_tmp.append(node_to_edge_dict.get((edge[1], edge[0])))
            nodes_tmp = list(set(nodes_tmp))
            for (u, v) in list(itertools.combinations(nodes_tmp, 2)):
                new_G.add_edge(u, v)
    return new_G, node_to_edge_dict, edge_to_node_dict


# 将得到结果-> 转换为networkx
def node_to_edge_dict_to_networkx(node_to_edge_dict, paritions):
    G = nx.Graph()
    community_num = 1
    for parition in paritions:
        # 这里的node就是对应原networkx的一条边
        for node in parition:
            edge = node_to_edge_dict.get(node)
            G.add_edge(edge[0], edge[1])
            for temp in [edge[0], edge[1]]:
                groups = G.node[temp].get('group', [])
                groups.append(community_num)
                G.node[temp]['group'] = list(set(groups))
                G.node[temp]['label'] = int(temp)
        community_num = community_num + 1
    return G


if __name__ == '__main__':
    G = nx.Graph()
    # G.add_edges_from([(1, 2), (1, 3), (1, 4), (2, 3), (2, 4),
    #                   (3, 4), (4, 5), (4, 6), (4, 7), (5, 6),
    #                   (7, 8), (7, 9), (8, 9)])
    G = nx.read_gml("../datasets/karate.gml", label="id")
    def clone_graph(G):
        cloned_g = nx.Graph()
        for edge in G.edges():
            cloned_g.add_edge(edge[0], edge[1])
        return cloned_g
    G = clone_graph(G)
    print len(G.nodes)
    G, node_to_edge_dict, edge_to_node_dict = node_networxk_to_edge_networkx(G)
    algorithmtoOne = GN(G)
    some = algorithmtoOne.run_to_all()
    print '-----------the result of each division, until each node is a community----------'
    for i in range(1, len(G.nodes()) + 1):
        print '\n划分成{0}个社区：Q值为{1}'.format(i, some[1][i - 1])
        print len(some[0][i - 1]), some[0][i - 1]
    # G_temp = node_to_edge_dict_to_networkx(edge_to_node_dict, [[128, 1, 130, 3, 133, 149, 129, 136, 137, 138, 139, 140, 141, 142, 144, 131, 148, 21, 150, 33, 38, 135, 52, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 74, 75, 76, 77, 98, 99, 122, 123, 124, 125, 126, 127], [2, 5, 6, 48, 113, 147], [4, 22, 151, 152, 153, 156, 157, 39, 50, 51, 68, 69, 70, 71, 72, 73, 84, 85, 87, 88, 89, 100, 101, 102, 103, 105, 106, 107, 108, 114, 115, 116, 117, 118], [104, 132, 92, 134, 7], [8, 9, 10, 11, 12, 13, 14, 143, 145, 146, 23, 24, 25, 26, 27, 28, 29, 30, 159, 32, 34, 155, 37, 43, 44, 45, 46, 47, 53, 54, 55, 56, 57, 31, 79, 80, 81, 82, 83, 91], [17, 15, 16, 49, 18, 158], [41, 42, 19, 20], [35, 109, 110, 111], [112, 120, 90, 36, 119], [96, 97, 40, 78, 86, 93, 94, 95], [121], [154]])
    # pos = nx.spring_layout(G_temp)
    # node_groups = nx.get_node_attributes(G_temp, 'group')
    # result = defaultdict(list)
    # for key, value in node_groups.items():
    #     for x in value:
    #         a = result.get(x, [])
    #         a.append(key)
    #         result[x] = a
    # for key, value in result.items():
    #     print key
    #     print " ".join(value)


