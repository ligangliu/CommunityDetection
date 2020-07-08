# -*- coding: utf-8 -*-
from collections import defaultdict
import networkx as nx

'''
paper : <<Uncovering the overlapping community structure of complex networks in nature and society>>
    https://www.cnblogs.com/nolonely/p/6268150.html
    https://zhuanlan.zhihu.com/p/39495154
'''


class CPM():

    def __init__(self, G, k=4):
        self._G = G
        self._k = k

    def execute(self):
        # find_cliques就是寻找最大联通子图，（也就是子图中的节点都是两两相互连接的）
        cliques = list(nx.find_cliques(G))
        vid_cid = defaultdict(lambda: set())
        for i, c in enumerate(cliques):
            if len(c) < self._k:
                continue
            for v in c:
                # 寻找出每个节点被划分至的社区统计
                vid_cid[v].add(i)
        # build clique neighbor
        clique_neighbor = defaultdict(lambda: set())
        remained = set()
        for i, c1 in enumerate(cliques):
            # if i % 100 == 0:
            # print i
            if len(c1) < self._k:
                continue
            remained.add(i)
            s1 = set(c1)
            candidate_neighbors = set()
            # 用于记录每个小团体中与其他有联系的其他小团体
            for v in c1:
                candidate_neighbors.update(vid_cid[v])
            candidate_neighbors.remove(i)
            for j in candidate_neighbors:
                c2 = cliques[j]
                if len(c2) < self._k:
                    continue
                if j < i:
                    continue
                s2 = set(c2)
                if len(s1 & s2) >= min(len(s1), len(s2)) - 1:
                    clique_neighbor[i].add(j)
                    clique_neighbor[j].add(i)

                    # depth first search clique neighbors for communities
        # 到这一步是已经得到了一个重叠矩阵，对重叠矩阵中的元素进行统计
        communities = []
        for i, c in enumerate(cliques):
            if i in remained and len(c) >= self._k:
                # print 'remained cliques', len(remained)
                communities.append(set(c))
                neighbors = list(clique_neighbor[i])
                while len(neighbors) != 0:
                    n = neighbors.pop()
                    if n in remained:
                        # if len(remained) % 100 == 0:
                        # print 'remained cliques', len(remained)
                        communities[len(communities) - 1].update(cliques[n])
                        remained.remove(n)
                        for nn in clique_neighbor[n]:
                            if nn in remained:
                                neighbors.append(nn)
        return communities


if __name__ == '__main__':
    G = nx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (4, 5), (4, 6),
                      (5, 6), (5, 7), (5, 8), (6, 7), (6, 8), (7, 8), (7, 9)])
    algorithm = CPM(G, 3)
    communities = algorithm.execute()
    for community in communities:
        print community
