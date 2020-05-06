# -*- coding: utf-8 -*-

# coding=utf-8
import collections
import string
import random
import networkx as nx
from CommunityDetection.evaluation.Modularity import cal_Q

'''
    paper : <<Fast unfolding of communities in large networks>>
    Louvain算法核心：优化关系图模块度目标
    1）算法扫描数据中的所有节点，针对每个节点遍历该节点的所有邻居节点，衡量把该节点加入其邻居节点
       所在社区所带来的模块度的收益。并选择对应最大收益的邻居节点，加入所在的社区。
       这一过程化重复进行指导每一个节点的社区归属都不再发生变化
    2）对步骤1中形成的社区进行折叠，把每个社区折叠成一个单点，分别计算这些新生成的“社区点”
       之间的连边权重，以及社区内的所有点之间的连边权重之和。用于下一轮的步骤1。
    
    模块度：首先modularity是针对一个社区的所有节点进行了累加计算。
    modularity Q的计算公式背后体现了这种思想：社区内部边的权重减去所有与社区节点相连的边的权重和，
    对无向图更好理解，即社区内部边的度数减去社区内节点的总度数。
    可以直观去想象一下，如果一个社区节点完全是“封闭的
    （即所有节点都互相内部连接，但是不和社区外部其他节点有连接，则modularity公式的计算结果为1）”
    https://www.cnblogs.com/LittleHann/p/9078909.html
'''

def load_graph(path):
    G = collections.defaultdict(dict)
    G_1 = nx.Graph()
    with open(path) as text:
        for line in text:
            vertices = line.strip().split()
            v_i = string.atoi(vertices[0])
            v_j = string.atoi(vertices[1])
            G[v_i][v_j] = 1.0
            G[v_j][v_i] = 1.0
            G_1.add_edge(v_i, v_j, weight=1.0)
    return G, G_1


def add_group(G_1, communities):
    num = 0
    nodegroup = {}
    for community in communities:
        for node in community:
            nodegroup[node] = {'group': num}
        num = num + 1
    nx.set_node_attributes(G_1, nodegroup)


def to_gml(G_1, path):
    nx.write_gml(G_1, path)


class Vertex(object):

    def __init__(self, vid, cid, nodes, k_in=0):
        self._vid = vid # 节点id
        self._cid = cid # 节点所属社区id
        self._nodes = nodes
        self._kin = k_in  # 结点内部的边的权重


class Louvain(object):

    def __init__(self, G):
        self._G = G
        self._m = 0  # 边数量
        self._cid_vertices = {}  # 需维护的关于社区的信息(社区编号,其中包含的结点编号的集合)
        self._vid_vertex = {}  # 需维护的关于结点的信息(结点编号，相应的Vertex实例)
        for vid in self._G.keys():
            self._cid_vertices[vid] = set([vid])
            self._vid_vertex[vid] = Vertex(vid, vid, set([vid]))
            self._m += sum([1 for neighbor in self._G[vid].keys() if neighbor > vid])

    def first_stage(self):
        mod_inc = False  # 用于判断算法是否可终止
        visit_sequence = self._G.keys()
        random.shuffle(visit_sequence)
        while True:
            can_stop = True  # 第一阶段是否可终止
            for v_vid in visit_sequence:
                v_cid = self._vid_vertex[v_vid]._cid
                k_v = sum(self._G[v_vid].values()) + self._vid_vertex[v_vid]._kin
                cid_Q = {}
                for w_vid in self._G[v_vid].keys():
                    w_cid = self._vid_vertex[w_vid]._cid
                    if w_cid in cid_Q:
                        continue
                    else:
                        tot = sum([sum(self._G[k].values()) + self._vid_vertex[k]._kin for k in
                                   self._cid_vertices[w_cid]])
                        if w_cid == v_cid:
                            tot -= k_v
                        k_v_in = sum([v for k, v in self._G[v_vid].items() if
                                      k in self._cid_vertices[w_cid]])
                        delta_Q = k_v_in - k_v * tot / self._m  # 由于只需要知道delta_Q的正负，所以少乘了1/(2*self._m)
                        cid_Q[w_cid] = delta_Q

                cid, max_delta_Q = sorted(cid_Q.items(), key=lambda item: item[1], reverse=True)[0]
                if max_delta_Q > 0.0 and cid != v_cid:
                    self._vid_vertex[v_vid]._cid = cid
                    self._cid_vertices[cid].add(v_vid)
                    self._cid_vertices[v_cid].remove(v_vid)
                    can_stop = False
                    mod_inc = True
            if can_stop:
                break
        return mod_inc

    def second_stage(self):
        cid_vertices = {}
        vid_vertex = {}
        for cid, vertices in self._cid_vertices.items():
            if len(vertices) == 0:
                continue
            new_vertex = Vertex(cid, cid, set())
            for vid in vertices:
                new_vertex._nodes.update(self._vid_vertex[vid]._nodes)
                new_vertex._kin += self._vid_vertex[vid]._kin
                for k, v in self._G[vid].items():
                    if k in vertices:
                        new_vertex._kin += v / 2.0
            cid_vertices[cid] = set([cid])
            vid_vertex[cid] = new_vertex

        G = collections.defaultdict(dict)
        for cid1, vertices1 in self._cid_vertices.items():
            if len(vertices1) == 0:
                continue
            for cid2, vertices2 in self._cid_vertices.items():
                if cid2 <= cid1 or len(vertices2) == 0:
                    continue
                edge_weight = 0.0
                for vid in vertices1:
                    for k, v in self._G[vid].items():
                        if k in vertices2:
                            edge_weight += v
                if edge_weight != 0:
                    G[cid1][cid2] = edge_weight
                    G[cid2][cid1] = edge_weight

        self._cid_vertices = cid_vertices
        self._vid_vertex = vid_vertex
        self._G = G

    def get_communities(self):
        communities = []
        for vertices in self._cid_vertices.values():
            if len(vertices) != 0:
                c = set()
                for vid in vertices:
                    c.update(self._vid_vertex[vid]._nodes)
                communities.append(c)
        return communities

    def execute(self):
        iter_time = 1
        while True:
            iter_time += 1
            mod_inc = self.first_stage()
            if mod_inc:
                self.second_stage()
            else:
                break
        return self.get_communities()


if __name__ == '__main__':
    G, G_1 = load_graph('../datasets/temp.txt')
    algorithm = Louvain(G)
    communities = algorithm.execute()
    for c in communities:
        print c
    # add_group(G_1, communities)
    # path = "../datasets/outputofLouvain.gml"
    # to_gml(G_1, path)
    # communities = [list(c) for c in communities]
    # print cal_Q(communities, G_1)
    # print modularity(communities, G_1)
