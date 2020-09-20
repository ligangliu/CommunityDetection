# -*- coding: utf-8 -*-#

#------------------------------------------------------------------------------- 
# Author:       liuligang
# Date:         2020/9/8
# networkx的底层数据结构 dict of dict of dict
# G.adj：
#   {'a':{}} a没有与其他节点连成边
#   {'a':{'b':{}}} a与b连成边，但是边没有属性
#   {'a':{'b':{'weight':2, 'size'=12}}} a与b连成边，且该边有两个属性
#   {'a':{'b':{'weight':2, 'size'=12}, 'd':{}}}, a与b和a与d连成边
#   也就是adj中维护的就是每个节点与其他节点有边连接的情况。
# G.nodes(不知道为啥还有一个node,但是好像效果和nodes的效果差不多)：
#   {'a':{}}
#   {'a':{'size':10}}
#-------------------------------------------------------------------------------

import networkx as nx


G1 = nx.Graph()  # 无向图
G2 = nx.DiGraph()  # 有向图
G3 = nx.MultiGraph()  # 多重无向图
G4 = nx.MultiDiGraph()  # 多重有向图

G1.add_nodes_from(['a', 'b', 'c', 'd', 'e'], time='5')
print type(G1['a'])
# G1['a']['size'] = 10
# G1['b']['lenght'] = 10
G1.add_edge('b', 'c', weight=12, size=23)
G1.add_edge('c', 'd', size=12)
G1.add_edge('b', 'd')
G1.nodes['a']['size'] = 10
print G1.nodes['a']
print G1.node['a']
print G1['a']
print G1.adj

