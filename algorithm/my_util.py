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
  `overlapping_c` float(10) DEFAULT 0.0 COMMENT '划分重叠节点满足大于的值',
  `node_g_weight` int(4) DEFAULT 2 COMMENT 'node_g的比重',
  `n` int(4) DEFAULT 1000 COMMENT 'lfr生成的节点个数',
  `k` int(4) DEFAULT 10 COMMENT 'lfr平均度',
  `maxk` int(4) DEFAULT 40 COMMENT 'lfr最大的度',
  `minc` int(4) DEFAULT 80 COMMENT '社区的最小节点个数',
  `maxc` int(4) DEFAULT 100 COMMENT '社区的最多节点个数',
  `mut` float(10) DEFAULT 0.2 COMMENT '',
  `muw` float(10) DEFAULT 0.2 COMMENT '',
  `overlapping_size` int(4) DEFAULT 50 COMMENT '重叠节点的个数',
  `om` int(4) DEFAULT 2 COMMENT '每个重叠节点所属社区个数',
  `onmi` float(10) DEFAULT 0.0 COMMENT '几轮迭代的平均onmi的值',
  `error_community_size` float(10) DEFAULT 0.0 COMMENT '几轮迭代的社区个数的相差情况',
  `error_overalpping_size` float(10) DEFAULT 0.0 COMMENT '几轮迭代的多发现的重叠节点个数情况',
  `error_mapping_overalpping_size` float(10) DEFAULT 0.0 COMMENT '几轮迭代之后的每次匹配的重叠节点的个数情况',
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
import os
import math

from my_objects import AlgorithmParam, MyResultInof


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
    file_path = path + "/lfr_true.txt"
    if os.path.exists(file_path):
        os.remove(file_path)
        print "delete lfr_true.txt success..."
    file_handle = open(file_path, mode="w")
    for key, value in communities.items():
        # print "community: " + str(key)
        value = sorted(value)
        to_join_list = []
        for x in value:
            to_join_list.append(str(x))
        s = " ".join(to_join_list)
        file_handle.write(s + "\n")
    print "generate lfr_true.txt again...."
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


@timefn
def calculate_params(nodes=[], oms=[], muws=[], cs=[], node_g_weights=[], ons=[], minc_maxcs=[]):
    params = []
    for n in nodes:
        for om in oms:
            for muw in muws:
                for c in cs:
                    for node_g_weight in node_g_weights:
                        for minc_maxc in minc_maxcs:
                            for on in ons:
                                param = AlgorithmParam()
                                param.minc = n * minc_maxc
                                param.maxc = n * minc_maxc + 20
                                param.node_g_weight = node_g_weight
                                param.c = c
                                param.muw = muw
                                param.mut = muw
                                param.om = om
                                param.n = n
                                param.on = n * on
                                params.append(param)
    return params


# 将算法结果插入到数据库中
@timefn
def add_result_to_mysql(param, step_results=[], summary_table="community_summary2", detail_table="community_detail2"):
    if len(step_results) == 0 or param is None:
        return
    connection = init_mysql_connection()
    insert_summary_sql = "insert into {} (overlapping_c, node_g_weight, n, k, maxk, " \
                         "minc, maxc, mut, muw, overlapping_size, om) values ({}, {}, {}, {}, {}, {}," \
                         " {}, {}, {}, {}, {})".format(summary_table, param.c, param.node_g_weight, param.n,
                                                       param.k, param.maxk, param.minc,
                                                       param.maxc, param.mut, param.muw, param.on, param.om)
    try:
        cursor = connection.cursor()
        cursor.execute(insert_summary_sql)
        id = connection.insert_id()
        # sum_lg_community_size = 0.0
        # sum_le_community_size = 0.0

        sum_error_community_size_percent = 0.0  # 每次算法发现的社区个数 与 真实社区个数 的绝对差之和

        # sum_lg_overlapping_nodes = 0.0
        # sum_le_overalpping_nodes = 0.0
        sum_error_overlapping_size_percent = 0.0  # 每次算法发现的重叠节点的个数 与 真实重叠节点的个数 的绝对差之和

        # sum_mapping_overlapping_nodes = 0.0
        sum_error_mapping_overlapping_size_percent = 0.0

        sum_onmi = 0.0
        sum_spend_seconds = 0.0

        for step_result in step_results:
            assert isinstance(step_result, MyResultInof)
            true_community_num = step_result.true_community_num
            find_community_num = len(step_result.center_nodes)
            # if find_community_num > true_community_num:
            #     sum_lg_community_size += (find_community_num - true_community_num)
            # else:
            #     sum_le_community_size += (true_community_num - find_community_num)
            sum_error_community_size_percent += math.fabs(find_community_num - true_community_num) / true_community_num

            ls_zero_size = len(step_result.ls_zero_nodes)
            not_enveloped_size = len(step_result.not_enveloped_nodes)
            true_overlapping_size = len(step_result.true_overlapping_nodes)
            find_overalpping_size = len(step_result.find_overlapping_nodes)
            # if find_overalpping_size > true_overlapping_size:
            #     sum_lg_overlapping_nodes += (find_overalpping_size - true_overlapping_size)
            # else:
            #     sum_le_overalpping_nodes += (true_overlapping_size - find_overalpping_size)

            sum_error_overlapping_size_percent += math.fabs(
                find_overalpping_size - true_community_num) / true_overlapping_size

            mapping_overlapping_size = len(step_result.mapping_overlapping_nodes)
            # sum_mapping_overlapping_nodes += mapping_overlapping_size
            sum_error_mapping_overlapping_size_percent += mapping_overlapping_size / true_overlapping_size

            onmi = step_result.onmin
            sum_onmi += onmi

            min_om = step_result.min_om
            max_om = step_result.max_om

            spend_seconds = step_result.spend_seconds
            sum_spend_seconds += spend_seconds

            insert_detail_slq = "insert into {} (community_summary_id, " \
                                "true_community_num, find_community_num, ls_zero_size, not_enveloped_size, " \
                                "true_overlapping_size, find_overalpping_size, " \
                                "mapping_overlapping_size, min_om, max_om, onmi, spend_seconds) values " \
                                "({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})". \
                format(detail_table, id, true_community_num, find_community_num, ls_zero_size,
                       not_enveloped_size, true_overlapping_size, find_overalpping_size,
                       mapping_overlapping_size, min_om, max_om, onmi, spend_seconds)

            cursor.execute(insert_detail_slq)

        length = len(step_results)
        update_summary_sql = "update {} set error_community_size = {}, " \
                             "error_overalpping_size = {}, error_mapping_overalpping_size = {}," \
                             "average_spend_seconds = {}, onmi = {} where id = {}" \
            .format(summary_table, sum_error_community_size_percent / length,
                    sum_error_overlapping_size_percent / length,
                    sum_error_mapping_overlapping_size_percent / length,
                    sum_spend_seconds / length, sum_onmi / length, id)
        cursor.execute(update_summary_sql)
        connection.commit()
        print "add to mysql success......."
    except Exception as e:
        print e
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


# 主要用于将一个集合中的所有节点进行排序，并且返回一个只包含空格的字符串(因为计算onmi的时候是这种各式)
def trans_community_nodes_to_str(community_nodes):
    community_nodes = sorted(community_nodes)
    to_join_list = []
    for node in community_nodes:
        to_join_list.append(str(node))
    s = " ".join(to_join_list)
    return s


# 打印输出一些结果值，方便掌握算法执行情况
def print_result(result, need_print):
    if not result or not isinstance(result, MyResultInof):
        raise Exception("你想干啥。。。。。")
    if not need_print:
        return
    # 打印一些真实网络的情况
    print '-' * 30
    print "总共的节点个数：" + str(len(result.G.nodes))
    print "总共的边的个数：" + str(len(result.G.edges))
    print '-' * 30
    print

    # 打印输出中心节点
    print '-' * 30
    print "true communities：" + str(result.true_community_num)
    print "find communities: " + str(len(result.center_nodes))
    print "center nodes: " + str(result.center_nodes)
    print "not enveloped nodes: " + str(result.not_enveloped_nodes)
    print "ls ero nodes: " + str(result.ls_zero_nodes)
    print '-' * 30
    print

    # 打印算法划分的结果
    # 1) 打印非重叠社区划分的信息
    print "--------------not overlapping nodes----------------------"
    for community, community_nodes in result.not_overlapping_community_node_dict.items():
        s = trans_community_nodes_to_str(community_nodes)
        print s
    print "---------------------------------------------------------"

    # 2) 打印重叠社区划分的信息
    print "-----------------overlapping nodes-----------------------"
    for community, community_nodes in result.community_nodes_dict.items():
        s = trans_community_nodes_to_str(community_nodes)
        print s
    print "---------------------------------------------------------"
    print

    # 打印重叠节点的情况
    # print '-' * 30
    # print "真实社区重叠节点个数: " + str(len(result.true_overlapping_nodes))
    # # print sorted(result.true_overlapping_nodes)
    print "算法发现的重叠节点个数: " + str(len(result.find_overlapping_nodes))
    print sorted(list(result.find_overlapping_nodes))
    # print "与原重叠节点的mapping个数: " + str(len(result.mapping_overlapping_nodes))
    # # print sorted(list(result.mapping_overlapping_nodes))
    print "重叠节点最多划分到的社区个数: " + str(result.max_om)
    print "重叠节点最少划分到的社区个数: " + str(result.min_om)
    # print "算法执行花费时间: " + str(result.spend_seconds)
    # print '-' * 30


# 展示x,y的二维坐标点，用于后面的数据验证
def show_data(xmin=0, xmax=1, ymin=0, ymax=1, x=None, y=None):
    if x is None or y is None:
        return
    import matplotlib.pyplot as plt
    plt.title("I'm a scatter diagram.")
    plt.xlim(xmax=xmax, xmin=xmin)
    plt.ylim(ymax=ymax, ymin=ymin)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.plot(x, y, 'ro')
    plt.show()


def node_p_1_g_1_to_xy(nodes_info_list):
    x = []
    y = []
    z = []
    count = 1
    for node_info in nodes_info_list:
        x.append(count)
        y.append(node_info.node_p_1)
        z.append(node_info.node_g_1)
        # print node_info.node, node_info.node_p_1, node_info.node_g_1
        count += 1
    return x, y, z


def nodes_r_node_dr_to_xy(nodes_info_list):
    x = []
    y = []
    z = []
    count = 1
    for node_info in nodes_info_list:
        x.append(count)
        y.append(node_info.node_r)
        if count == 1:
            z.append(1.0)
        else:
            z.append(node_info.node_dr)
        count += 1
    return x, y, z


# 输出一个二维node_p_1,node_g_1, node_r,node_dr等二维图像供debug使用(不重要)
def need_show_data(all_nodes_info_list, filter_nodes_info_list, need=False):
    if need:
        # (debug时使用)输出一个二维图像，按照node_p_1进行排序的节点(即参与可能被选择为中心节点的那些节点的node_p_1 和 node_g_1的图像)
        x, y, z = node_p_1_g_1_to_xy(all_nodes_info_list)
        show_data(xmax=len(x), x=x, y=y)
        show_data(xmax=len(x), x=x, y=z)

        # (debug时使用) 输出可能被选择为节点的noder 和 node_dr
        x, y, z = nodes_r_node_dr_to_xy(filter_nodes_info_list)
        show_data(xmax=len(x), x=x, y=y)
        show_data(xmax=len(x), x=x, y=z)


if __name__ == '__main__':
    G, overlapping_nodes = transfer_2_gml(False)
    print "ffff"
