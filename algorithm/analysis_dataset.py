# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt
import time
from functools import wraps

##############################################################################
# 以下的代码是协助我们对网络的数据进行分析，避免每次重复去查找网络图
##############################################################################

G = nx.read_gml("./datasets/football.gml", label="id")
print "总共节点个数：" + str(len(G.nodes))
print "总共边的条数：" + str(len(G.edges))


# 得到每个社区对应的节点集合
def get_community_with_nodes():
    node_groups = nx.get_node_attributes(G, 'value')
    comunity_node_dict = {}
    for node, comunity in node_groups.items():
        if comunity_node_dict.has_key(comunity):
            comunity_node_dict.get(comunity).append(node)
        else:
            temp = []
            temp.append(node)
            comunity_node_dict[comunity] = temp


# 得到每个节点的邻局节点的信息
def get_node_neighbors(community_a=[], community_b=[]):
    node_neighbors_dict = {}
    for node in community_a:
        neighbors = list(nx.neighbors(G, node))
        node_neighbors_dict[node] = neighbors
        sum_self = 0
        sum_another = 0
        for x in neighbors:
            if x in community_a:
                sum_self += 1
            if x in community_b:
                sum_another += 1
        if len(community_b) == 0:
            print "节点： " + str(node) + " 邻居节点：" + str(neighbors) + " " \
                  + str(len(neighbors)) + " " + str(sum_self)
        else:
            print "节点：" + str(node) + " 与自己社区相联系的节点个数: " \
                  + str(sum_self) + "/" + str(len(neighbors)) + \
                  "  与b社区相联的节点个数： " + str(sum_another) + "/" + str(len(neighbors))
    return node_neighbors_dict


# 得到每个节点的度，并且是否需要排序打印
def get_node_degress(nodes=[], is_need_sort=True):
    res = []
    for node in nodes:
        t = (node, nx.degree(G, node))
        res.append(t)
        if not is_need_sort:
            print "节点：" + str(t[0]) + "  度：" + str(t[1])
    if is_need_sort:
        res = sorted(res, key=lambda x: x[1])
        for info in res:
            print "节点：" + str(info[0]) + "  度：" + str(info[1])


def add_douhao(str=""):
    res = []
    for x in str.split(" "):
        res.append(int(x))
    return res


def sub_douhao(nodes=[]):
    res = ""
    for node in nodes:
        res = res + str(node) + " "
    return res


if __name__ == '__main__':
    str1 = "28 46 49 53 58 67 73 83 88 114"
    get_node_neighbors(add_douhao(str1))
