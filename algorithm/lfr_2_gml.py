# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/11/9
# 以下的代码是对LFR网络生成的数据进行的一些操作
# 1) 由于代码是linux上的，所以需要windows和linux(/home/ubuntu/LFR目录)上的一个文件上传下载
# https://blog.csdn.net/maoyuanming0806/article/details/78539655/  (linux与window上传下载文件配置)
# -------------------------------------------------------------------------------

# coding=utf-8
import networkx as nx
from collections import defaultdict
import time
from functools import wraps

def timefn(fn):
    """计算性能的修饰器"""
    @wraps(fn)
    def measure_time(*args, **kwargs):
        t1 = time.time()
        result = fn(*args, **kwargs)
        t2 = time.time()
        print "@timefn: %s: take %d s" %(fn.__name__, t2-t1)
        return result
    return measure_time

@timefn
def transfer_2_gml(need_write_gml=False):
    """--------------------------------------------------------------------------
    function:   将LFR的network.dat和community.dat转化为.gml文件
    parameter:
    return:
    -------------------------------------------------------------------------------"""
    nodes_labels = {}
    k = 0
    overlapping_node_dict = {}
    with open("../datasets/community.dat", "r") as f:
        for line in f.readlines():
            items = line.strip("\r\n").split("\t")
            node = items[0]
            communities = items[1].strip().split(" ")
            if len(communities) > 1:
                overlapping_node_dict[node] = communities
            nodes_labels[node] = communities
        # end-for
    # end-with
    G = nx.Graph()
    for v in nodes_labels.keys():  # 添加所有的节点，并且记录其真实标签
        G.add_node(int(v), value=nodes_labels[v][0]) # 一个节点(重叠节点)可能会存在多个社区标签，所以value应该是一个list
    edges = set()
    with open("../datasets/network.dat", "r") as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue
            # 讲道理这里是不是还应该有一个度啊？？？？
            items = line.strip("\r\n").split("\t")
            a = int(items[0])
            b = int(items[1])
            if (a, b) not in edges or (b, a) not in edges:
                edges.add((a, b))
        # end-for
    # end-with
    for e in edges:
        a, b = e
        G.add_edge(a, b, type="Undirected", weight=1.0)
    if need_write_gml:
        nx.write_gml(G, "../datasets/lfr-1.gml")

    communities = defaultdict(lambda: [])
    for v in nodes_labels.keys():
        node_communites = nodes_labels[v]
        for node_community in node_communites:
            communities[node_community].append(int(v))
    print "总共的节点个数：" + str(len(G.nodes))
    print "总共的边的个数：" + str(len(G.edges))
    print "社区的个数：" + str(len(communities))
    print "重叠节点的个数：" + str(len(overlapping_node_dict))
    print "重叠节点："
    overlapping_nodes = []
    for overlapping_node in overlapping_node_dict.keys():
        overlapping_nodes.append(int(overlapping_node))
    overlapping_nodes = sorted(overlapping_nodes)
    print overlapping_nodes
    for key, value in communities.items():
        # print "community: " + str(key)
        s = ""
        value = sorted(value)
        for x in value:
            s += str(x) + " "
        print s
        # print value
        # print "---------------------------"
    return G, overlapping_nodes

def overlapping_mapping_sum(a=[], b=[]):
    sum = 0
    for node in a:
        if node in b:
            sum += 1
    return sum



if __name__ == '__main__':
    G, overlapping_nodes = transfer_2_gml(True)