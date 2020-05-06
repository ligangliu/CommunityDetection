# -*- coding: utf-8 -*-

import collections
import random
import networkx as nx

'''
paper : <<Near linear time algorithm to detect community structures in large-scale networks>>
'''
'''
标签传播算法的思想：
    1）为每一个节点指定一个唯一的标签
    2）迭代刷新所有节点的标签，直到收敛为止。对于每一轮刷新，节点标签的刷新规则如下：
        对于某一个节点，考察其所有邻居的标签，并进行统计，将出现个数最多(权重最大的)的那个标签赋予给当前节点。
        当个数最多的标签不唯一时，随机选择一个
    标签传播方式：
        a: 同步更新，在第t次迭代中，每个节点依赖的都是邻居节点上一次迭代t-1时的社区标签。
        b: 异步更新(可防止震荡现象)，在第t次迭代中，每个节点依赖的是当前邻居节点的社区标签，若邻居节点进行了更新，
           则依赖的是t时的社区标签，若未进行更新，则依赖的是t-1时的社区标签
    缺点:
        算法不稳定，随机性强，多次执行可能得到的结果不同
        体现在：
            a: 更新顺序。节点标签更新顺序随机，但是很明显，越重要的节点越早更新会加速收敛过程
            b: 随机选择。如果一个节点的出现次数最大的邻居标签不止一个时，随机选择一个标签作为自己标签。
               很明显，在标签重复次数相同的情况下，与本节点相似度更高或对本节点影响力
               越大的邻居节点的标签有更大的概率被节点选中
        https://juejin.im/post/5e8c1c766fb9a03c5147f61d
        雪崩效应：如有5个节点 a,b,c,d,e分别两两相连，在传播的过程中，c开始随机将a作为自己的随机结果，
                会导致后面的所有的节点最终都会选择a
        震荡效应：存在二分子图的情况，同步更新的时候
            
'''

class LPA(object):

    def __init__(self, G, max_iter=20):
        self._G = G
        self._n = len(G.node)  # number of nodes
        self._max_iter = max_iter

    def can_stop(self):
        # all node has the label same with its most neighbor
        for i in range(self._n):
            node = self._G.node[i]
            label = node["label"]
            max_labels = self.get_max_neighbor_label(i)
            if (label not in max_labels):
                return False
        return True

    def get_max_neighbor_label(self, node_index):
        m = collections.defaultdict(int)
        for neighbor_index in self._G.neighbors(node_index):
            neighbor_label = self._G.node[neighbor_index]["label"]
            m[neighbor_label] += 1
        max_v = max(m.itervalues())
        return [item[0] for item in m.items() if item[1] == max_v]

    '''
        异步更新：能够避免标签签震荡现象，并且相对于同步标签更新策略需要更少的迭代次数
        不确定的节点更新顺序可能会导致算法的稳定性极差
    '''

    def populate_label(self):
        # 类似于洗牌，随机访问
        visitSequence = random.sample(self._G.nodes(), len(self._G.nodes()))
        for i in visitSequence:
            node = self._G.node[i]
            label = node["label"]
            max_labels = self.get_max_neighbor_label(i)
            if (label not in max_labels):
                newLabel = random.choice(max_labels)
                node["label"] = newLabel

    def get_communities(self):
        communities = collections.defaultdict(lambda: list())
        for node in self._G.nodes(True):
            label = node[1]["label"]
            communities[label].append(node[0])
        return communities.values()

    def execute(self):
        # initial label
        for i in range(self._n):
            self._G.node[i]["label"] = i
        iter_time = 0
        # populate label
        while (not self.can_stop() and iter_time < self._max_iter):
            self.populate_label()
            iter_time += 1
        return self.get_communities()


if __name__ == '__main__':
    G = nx.karate_club_graph()
    algorithm = LPA(G)
    communities = algorithm.execute()
    print "----划分社区--------"
    for community in communities:
        print community
