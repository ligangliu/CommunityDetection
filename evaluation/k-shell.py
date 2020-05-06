# -*- coding: utf-8 -*-

import networkx as nx

def kshell(graph):
    """
    根据Kshell算法计算节点的重要性
    :param graph: 图
    :return: importance_dict{ks:[nodes]}
    """
    importance_dict = {}
    ks = 1
    while graph.nodes():
        # 暂存度为ks的顶点
        temp = []
        node_degrees = graph.degree()
        # 每次删除度值最小的节点而不能删除度为ks的节点否则产生死循环
        kks = min([node[1] for node in node_degrees])
        while True:
            for k, v in list(node_degrees):
                if v == kks:
                    temp.append(k)
                    graph.remove_node(k)
            node_degrees = graph.degree()
            # 删除节点之后(会改变一些节点的度，从而使得可能会存在新的节点度等于kks)，看是否还有节点的度=kks的，没有则退出这次的循环
            if kks not in [node[1] for node in node_degrees]:
                break
        importance_dict[ks] = temp
        ks += 1
    return importance_dict


if __name__ == "__main__":
    graph = nx.Graph()
    # graph.add_edges_from(
    #     [(1, 4), (2, 4), (3, 4), (4, 5), (5, 6), (5, 7), (3, 5), (6, 7)])
    graph.add_edges_from(
        [(1, 13), (2, 13), (3, 9), (4, 9), (5, 12), (6, 7), (6, 12), (8, 16),
         (9, 13), (9, 15), (10, 13), (10, 11), (11, 13), (12, 15),
         (12, 16), (13, 14), (13, 15), (13, 16), (14, 15), (14, 16), (15, 16)])
    print kshell(graph)
