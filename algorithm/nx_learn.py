# -*- coding: utf-8 -*-

import networkx as nx
a = set()
b = set([0, 4])
c = set([0])
d = set([0, 4])
e = set([0])
for x in [b, c, d]:
    a.update(x)
print a
#####################
# https://networkx.github.io/documentation/latest/index.html
# NetworkX中支持四种图。按照边是否有方向，
# 两个节点间是否允许多条边两个维度，分为Graph（无向图），
# MultiGrpah（复合无向图），DiGrpah（有向图），
# MultiDiGraph（复合有向图）
#####################
# G = nx.Graph()
# G = nx.DiGraph()
# G = nx.MultiGraph()
# G = nx.MultiDiGraph()
# 构造

# node
print "-----------node-----------"
G = nx.Graph()
# 对于节点增加属性 也可以通过nx.set_node_attributes()和nx.get_node_attributes()设置属性和获取属性
G.add_node('a', group=0, size=10)
G.add_node('b', **{"group": 1, "size": 20})
for node in G.nodes:
    print G.nodes.get(node)
print G.degree('a')
print list(G.nodes)
# 打印出所有的节点和以及节点的属性
print list(G.nodes(data=True))
# 得到节点的属性值
print G.node['a']
print G.nodes['a']
print "--------edge-------------"
# edge
G = nx.Graph()
# 对于边增加属性
G.add_edge('a', 'b', weight=1, color=2)
G.add_edge('b', 'c', **{"weight":2, "color": "black"})
G.add_edge('c', 'a')
G.add_edge('b', 'e')
print list(G.edges)
# 将边的属性也打印出来
print list(G.edges(data=True))
# 设置和得到的属性
G.get_edge_data('a', 'b')['hhh'] = 12
print G.get_edge_data('a', 'b')
# tripset
print '------function中提供了一系列的方法针对graph进行操作，这些方法都是需要nx.xxx进行调用的--------'
print '------节点/边的属性设置和获取--------'
# 节点和边的属性设置和获取
# 设置得到单独节点属性
G.node['a']['label'] = 1
G.node['a']
# 设置和得到单独边的属性
G.get_edge_data('a', 'b')['hhh'] = 12
print G.get_edge_data('a', 'b')

# set_node_attributes 或 set_edge_attributes  value可以是值，也可以是{}, 看下面的例子应该能够看懂
nx.set_node_attributes(G, {"a" : {"color": 'white', "weight": 2}, "b" : {"color": 'red', "weight": 3}})
print nx.get_node_attributes(G, 'color')
nx.set_node_attributes(G, '20', 'size')
print nx.get_node_attributes(G, 'size')
print G.nodes(data=True)

print '------节点/边的邻居节点问题--------'
# 返回节点的邻居节点  其实all_neighbors 和 neighbors返回的对象是同一个 在有向图中有区别
print nx.number_of_nodes(G)
print list(nx.all_neighbors(G, 'a'))
print list(nx.neighbors(G, 'a'))
print list(nx.common_neighbors(G, 'a', 'b'))
print list(nx.non_neighbors(G, 'a'))
# 找出节点之间不存在的边
print list(nx.non_edges(G))

# 复制graph，只复制节点和节点属性，移除所有的边
copy_graph = nx.create_empty_copy(G)
print copy_graph.nodes(data=True)
print copy_graph.edges(data=True)

