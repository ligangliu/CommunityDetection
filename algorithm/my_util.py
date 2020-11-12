# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/11/9
# 以下的代码是对LFR网络生成的数据进行的一些操作
# 1) 由于代码是linux上的，所以需要windows和linux(/home/ubuntu/LFR目录)上的一个文件上传下载
# https://blog.csdn.net/maoyuanming0806/article/details/78539655/  (linux与window上传下载文件配置)
# -------------------------------------------------------------------------------
'''
CREATE TABLE community_summary (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `c` float(10) DEFAULT 0.0 COMMENT '划分重叠节点满足大于的值',
  `node_g_weight` int(4) DEFAULT 2 COMMENT 'node_g的比重',
  `n` int(4) DEFAULT 1000 COMMENT 'lfr生成的节点个数',
  `k` int(4) DEFAULT 10 COMMENT 'lfr平均度',
  `maxk` int(4) DEFAULT 40 COMMENT 'lfr最大的度',
  `minc` int(4) DEFAULT 80 COMMENT '社区的最小节点个数',
  `maxc` int(4) DEFAULT 100 COMMENT '社区的最多节点个数',
  `mut` float(10) DEFAULT 0.2 COMMENT '',
  `muw` float(10) DEFAULT 0.2 COMMENT '',
  `on` int(4) DEFAULT 50 COMMENT '重叠节点的个数',
  `om` int(4) DEFAULT 2 COMMENT '每个重叠节点所属社区个数',
  `onmi` float(10) DEFAULT 0.0 COMMENT '几轮迭代的平均onmi的值',
  `lg_community_size` float(10) DEFAULT 0.0 COMMENT '几轮迭代的平均算法社区个数大于真实社区个数',
  `le_community_size` float(10) DEFAULT 0.0 COMMENT '几轮迭代的平均算法社区个数小于真实社区个数',
  `lg_overlapping_nodes` float(10) DEFAULT 0.0 COMMENT '几轮迭代的平均算法的重叠节点比真实社区重叠多的个数',
  `le_overlapping_nodes` float(10) DEFAULT 0.0 COMMENT '几轮迭代的平均算法的重叠节点比真实社区重叠少的个数',
  `average_spend_seconds` float(10) DEFAULT 0.0 COMMENT '几轮迭代之后的平均消耗时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE community_detail (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `community_summary_id` bigint(20) NOT NULL COMMENT '每一轮的id',
  `true_community_num` int(4) DEFAULT 0 COMMENT '真实社区的个数',
  `find_community_num` int(4) DEFAULT 0 COMMENT '算法发现的社区个数',
  `ls_zero_size` int(4) DEFAULT 0 COMMENT '到所有中心节点为0的个数',
  `not_enveloped_size` int(4) DEFAULT 0 COMMENT '非包络节点的个数',
  `true_overlapping_size` int(4) DEFAULT 0 COMMENT '真实社区的重叠节点个数',
  `find_overalpping_size` int(4) DEFAULT 0 COMMENT '算法发现的重叠节点个数',
  `mapping_overlapping_size` int(4) DEFAULT 0 COMMENT '算法和真实匹配的重叠节点个数',
  `min_om` int(4) DEFAULT 2 COMMENT '重叠节点最少被划分到的社区个数',
  `max_om` int(4) DEFAULT 2 COMMENT '重叠节点最多被划分到的社区个数',
  `onmi` float(10) DEFAULT 0.0 COMMENT '算法的onmi的值',
  `spend_seconds` int(11) DEFAULT 0 COMMENT '算法执行所耗费的时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''
# coding=utf-8
import networkx as nx
from collections import defaultdict
import time
from functools import wraps
import platform
import pymysql


def init_path():
    run_platform = "windows"
    if platform.system().lower() == 'windows':
        path = "./datasets/"
    elif platform.system().lower() == 'linux':
        path = "/app/datasets/"
        run_platform = "linux"
    return path, run_platform

path, run_platform = init_path()


def timefn(fn):
    """计算性能的修饰器"""

    @wraps(fn)
    def measure_time(*args, **kwargs):
        t1 = time.time()
        result = fn(*args, **kwargs)
        t2 = time.time()
        print "@timefn: %s: take %d s" % (fn.__name__, t2 - t1)
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
    with open(path + "community.nmc", "r") as f:
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
        G.add_node(int(v), value=nodes_labels[v][0])  # 一个节点(重叠节点)可能会存在多个社区标签，所以value应该是一个list
    edges = set()
    with open(path + "community.nse", "r") as f:
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
        nx.write_gml(G, path + "lfr-1.gml")

    communities = defaultdict(lambda: [])
    for v in nodes_labels.keys():
        node_communites = nodes_labels[v]
        for node_community in node_communites:
            communities[node_community].append(int(v))
    # print "总共的节点个数：" + str(len(G.nodes))
    # print "总共的边的个数：" + str(len(G.edges))
    # print "社区的个数：" + str(len(communities))
    # print "重叠节点的个数：" + str(len(overlapping_node_dict))
    # print "重叠节点："
    overlapping_nodes = []
    for overlapping_node in overlapping_node_dict.keys():
        overlapping_nodes.append(int(overlapping_node))
    overlapping_nodes = sorted(overlapping_nodes)
    # print overlapping_nodes
    file_handle = open(path + "/lfr_true.txt", mode="w")
    for key, value in communities.items():
        # print "community: " + str(key)
        value = sorted(value)
        to_join_list = []
        for x in value:
            to_join_list.append(str(x))
        s = " ".join(to_join_list)
        print s
        file_handle.write(s + "\n")
        # print value
        # print "---------------------------"
    return G, overlapping_nodes, len(communities)



HOST = '192.168.230.200'
PORT = 3307
USER = 'root'
PASSWD = '123'
DB = 'test'
CHARSET = 'utf8'

def init_mysql_connection():
    connection = pymysql.connect(host=HOST,
                                 port=PORT,
                                 user=USER,
                                 passwd=PASSWD,
                                 db=DB,
                                 charset=CHARSET)
    return connection

# def select_sql(connection, sql):
#     with connection.cursor() as cursor:
#         sql = 'select * from test'
#         cursor.execute(sql)
#         results = cursor.fetchall()
#         connection.commit()
#     return results


def add_result(connection, sql):
    with connection.cursor() as cursor:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交事务
        connection.commit()
        connection.close()

if __name__ == '__main__':
    G, overlapping_nodes = transfer_2_gml(False)
    print "ffff"
