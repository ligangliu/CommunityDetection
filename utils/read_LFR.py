# -*- coding: utf-8 -*-
import csv
import networkx as nx
from CommunityDetection.evaluation.Modularity import cal_Q, modularity


def read_LFR():
    """
        基于LFR——benchmark生成后的数据进行处理，生成预览及GML文件
        执行命令后，会生成三个文件
        network.data：包含网络中的边，但是生成文件的时候，第一行会出现一些总结信息，在程序读取它的时候需要排除
        community.data：包含每一个节点所属的类
        statistics.data：包含度分布，社团大小分布，混合参数分布

    """
    G = nx.Graph()

    # 定义边文件和社团文件
    edge_file = '../datasets/LFR/network.dat'
    community_file = '../datasets/LFR/community.dat'

    # 读取数据，并以tab键分割
    data = csv.reader(open(edge_file, 'r'), delimiter='\t')
    # 加边
    edges = [(d[0], d[1]) for d in data]
    G.add_edges_from(edges)
    # 读社团
    community = csv.reader(open(community_file, 'r'), delimiter='\t')
    # 标记社团
    labels = {d[0]: d[1] for d in community}
    for n in G.nodes():
        G.nodes[n]['group'] = labels[n]

    groups = labels.values()
    nodes = labels.keys()
    partition = [[n for n in nodes if labels[n] == g] for g in groups]

    # 绘图
    # draw_communities(G, partition)

    # 另存为gml文件，可以注册NEUSNCP账号后上传gml文件，使用 https://neusncp.com/api/cd 的可视化工具验证
    nx.write_gml(G, '../datasets/lft.gml')

    # 计算一下模块度
    # from networkx.algorithms.community.quality import modularity, performance
    # print modularity(G, partition)
    print cal_Q(partition, G)
    print modularity(partition, G)


if __name__ == '__main__':
    read_LFR()
