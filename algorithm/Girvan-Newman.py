# -*- coding: utf-8 -*-

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


if __name__ == '__main__':
    G = nx.read_gml('../datasets/karate.gml', label='id')  # Using max_Q to divide communities
    # from modularity_maximization import partition
    # print partition(G)
    # print "---"*20
    nx.write_edgelist(G, "../datasets/temp.txt")
    algorithm = GN(G)
    algorithm.run()
    # algorithm.draw_Q()
    algorithm.add_group()
    # print "---------"
    # print list(algorithm.G_copy.nodes(data=True))
    # print algorithm.partition
    # algorithm.to_gml()

    # G1 = nx.read_gml('../datasets/karate.gml', label='id')  # Dividing communities by the number
    # algorithmByNum = GN(G1)
    # algorithmByNum.run_n(3)

    G2 = nx.read_gml('../datasets/karate.gml',
                     label='id')  # Dividing communities until each node is a community

    algorithmtoOne = GN(G2)
    some = algorithmtoOne.run_to_all()
    print '-----------the result of each division, until each node is a community----------'
    for i in range(1, len(G.nodes()) + 1):
        print '\n划分成{0}个社区：Q值为{1}'.format(i, some[1][i - 1])
        print some[0][i - 1]
