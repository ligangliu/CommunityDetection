# -*- coding: utf-8 -*-
import random
import networkx as nx
import collections

'''
基于LPA稳定的标签传播
1）异步更新
2）更新顺序因节点的重要性以此排序
3）当多个标签相同时，将节点的影响值引入，从而避免因随机选择而得不到一个稳定的收敛状态
'''
class SLPA(object):

    def __init__(self, G, max_iter=20):
        self._G = G
        self._n = len(G.node)  # number of nodes
        self._max_iter = max_iter
        self._G_copy = G.copy()
        temp = self.kshell(G.copy())
        # 字典转换成 {node:kshell}的格式
        import_dict = {}
        for k, v in temp.items():
            for node in v:
                import_dict.setdefault(node, k)
        self._import_dict = import_dict
        self._ni = self.NI(G.copy())

    def can_stop(self):
        # all node has the label same with its most neighbor
        for i in self._G_copy.nodes:
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

    def get_max_Li(self, node, max_lables):
        li_dict = {}
        for label in max_lables:
            li_dict[label] = self.LI(node, label)
            # li_dict.setdefault(label, self.LI(node, label))
        max_li = max(li_dict.itervalues())
        return [item[0] for item in li_dict.items() if item[1] == max_li]
    '''
        异步更新：能够避免标签签震荡现象，并且相对于同步标签更新策略需要更少的迭代次数
        不确定的节点更新顺序可能会导致算法的稳定性极差
    '''

    def populate_label(self):
        # random visit
        # visitSequence = random.sample(self._G.nodes(), len(self._G.nodes()))
        visitSequence = [item[0] for item in sorted(self._ni.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)]
        for i in visitSequence:
            # self._G.node[i] 是为了得到节点的属性值
            node = self._G.node[i]
            # label = node["label"]
            max_labels = self.get_max_neighbor_label(i)
            if len(max_labels) == 1:
                node['label'] = max_labels[0]
            # 返回多个标签的时候
            elif len(max_labels) > 1:
                max_li = self.get_max_Li(i, max_labels)
                if len(max_li) == 1:
                    node['lable'] = max_li[0]
                else:
                    # 保持原标签
                    pass

    def get_communities(self):
        communities = collections.defaultdict(lambda: list())
        for node in self._G.nodes(True):
            label = node[1]["label"]
            communities[label].append(node[0])
        return communities.values()

    def execute(self):
        # initial label
        i = 0
        for node in self._G_copy.nodes:
            self._G.node[node]["label"] = i
            i = i + 1
        iter_time = 0
        # populate label
        while not self.can_stop() and iter_time < self._max_iter:
            self.populate_label()
            iter_time += 1
        return self.get_communities()

    def kshell(self, G_copy):
        """
        根据Kshell算法计算节点的重要性
        :return: importance_dict{ks:[nodes]}
        """
        importance_dict = {}
        ks = 1
        while G_copy.nodes():
            # 暂存度为ks的顶点
            temp = []
            node_degrees = G_copy.degree()
            # 每次删除度值最小的节点而不能删除度为ks的节点否则产生死循环
            kks = min([node[1] for node in node_degrees])
            while True:
                for k, v in list(node_degrees):
                    if v == kks:
                        temp.append(k)
                        G_copy.remove_node(k)
                node_degrees = G_copy.degree()
                # 删除节点之后(会改变一些节点的度，从而使得可能会存在新的节点度等于kks)，看是否还有节点的度=kks的，没有则退出这次的循环
                if kks not in [node[1] for node in node_degrees]:
                    break
            importance_dict[ks] = temp
            ks += 1
        return importance_dict

    def NI(self, G_copy):
        ni_dict = {}
        a = 0.1
        for node in G_copy.nodes:
            ks = self._import_dict.get(node)
            negihbor_nodes = G_copy.neighbors(node)
            sum = 0.0
            for node_neighbor in negihbor_nodes:
                degree = G_copy.degree(node_neighbor)
                ks_neighbor = self._import_dict.get(node_neighbor)
                sum += ks_neighbor/degree
            ni_dict.setdefault(node, ks + a * sum)
        return ni_dict

    def LI(self, node, label):
        '''
        标示的是标签l对节点的影响强度
        '''
        for node in self.get_neighbor_label(node, label):
            sum = 0.0
            degree = self._G_copy.degree(node)
            ni = self._ni.get(node)
            sum += ni/degree
        return sum

    def get_neighbor_label(self, node, lable):
        negihbor_nodes = self._G_copy.neighbors(node)
        nodes = []
        for node in negihbor_nodes:
            if self._G.node[node]['label'] == lable:
                nodes.append(node)
        return nodes


if __name__ == '__main__':
    G = nx.karate_club_graph()
    # G = nx.Graph()
    # G.add_edge('a', 'b', weight=1, color=2)
    # G.add_edge('b', 'c', **{"weight":2, "color": "black"})
    # G.add_edge('c', 'a')
    # G.add_edge('b', 'e')
    algorithm = SLPA(G)
    communities = algorithm.execute()
    print '------划分社区------'
    for community in communities:
        print community
