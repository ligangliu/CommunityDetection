# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/9/13
# DPC: 基于局部密度聚类算法
# https://blog.csdn.net/itplus/article/details/38926837
# -------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import sklearn.datasets as ds
import matplotlib.colors

min_distance = 4.6  # 邻域半径
points_number = 5  # 随机点个数


# 计算各点间距离、各点点密度(局部密度)大小
def get_point_density(datas, labers, min_distance, points_number):
    # 将numpy.ndarray格式转为list格式，并定义元组大小
    data = datas.tolist()
    laber = labers.tolist()
    distance_all = np.random.rand(points_number, points_number)
    point_density = np.random.rand(points_number)

    # 计算得到各点间距离
    for i in range(points_number):
        for n in range(points_number):
            distance_all[i][n] = np.sqrt(np.square(data[i][0] - data[n][0]) + np.square(data[i][1] - data[n][1]))
    print('距离数组:\n', distance_all, '\n')

    # 计算得到各点的点密度
    for i in range(points_number):
        x = 0
        for n in range(points_number):
            if distance_all[i][n] > 0 and distance_all[i][n] < min_distance:
                x = x + 1
            point_density[i] = x
    print('点密度数组:', point_density, '\n')
    return distance_all, point_density


# 计算点密度最大的点的聚类中心距离
def get_max_distance(distance_all, point_density, laber):
    point_density = point_density.tolist()
    a = int(max(point_density))
    # print('最大点密度',a,type(a))

    b = laber[point_density.index(a)]
    # print("最大点密度对应的索引：",b,type(b))

    c = max(distance_all[b])
    # print("最大点密度对应的聚类中心距离",c,type(c))

    return c


# 计算得到各点的聚类中心距离
def get_each_distance(distance_all, point_density, data, laber):
    nn = []
    for i in range(len(point_density)):
        aa = []
        for n in range(len(point_density)):
            if point_density[i] < point_density[n]:
                aa.append(n)
        # print("大于自身点密度的索引",aa,type(aa))
        ll = get_min_distance(aa, i, distance_all, point_density, data, laber)
        nn.append(ll)
    return nn


# 获得：到点密度大于自身的最近点的距离
def get_min_distance(aa, i, distance_all, point_density, data, laber):
    min_distance = []
    """
    如果传入的aa为空，说明该点是点密度最大的点，该点的聚类中心距离计算方法与其他不同
    """
    if aa != []:
        for k in aa:
            min_distance.append(distance_all[i][k])
        # print('与上各点距离',min_distance,type(nn))
        # print("最小距离：",min(min_distance),type(min(min_distance)),'\n')
        return min(min_distance)
    else:
        max_distance = get_max_distance(distance_all, point_density, laber)
        return max_distance


def get_picture(data, laber, points_number, point_density, nn):
    # 创建Figure
    fig = plt.figure()
    # 用来正常显示中文标签
    matplotlib.rcParams['font.sans-serif'] = [u'SimHei']
    # 用来正常显示负号
    matplotlib.rcParams['axes.unicode_minus'] = False

    # 原始点的分布
    ax1 = fig.add_subplot(211)
    plt.scatter(data[:, 0], data[:, 1], c=laber)
    plt.title(u'原始数据分布')
    plt.sca(ax1)
    for i in range(points_number):
        plt.text(data[:, 0][i], data[:, 1][i], laber[i])

    # 聚类后分布
    ax2 = fig.add_subplot(212)
    plt.scatter(point_density.tolist(), nn, c=laber)
    plt.title(u'聚类后数据分布')
    plt.sca(ax2)
    for i in range(points_number):
        plt.text(point_density[i], nn[i], laber[i])

    plt.show()


def main():
    # 随机生成点坐标
    data, laber = ds.make_blobs(points_number, centers=points_number, random_state=0)
    print('各点坐标：\n', data)
    print('各点索引：', laber, '\n')

    # 计算各点间距离、各点点密度(局部密度)大小
    distance_all, point_density = get_point_density(data, laber, min_distance, points_number)
    # 得到各点的聚类中心距离
    nn = get_each_distance(distance_all, point_density, data, laber)
    print('最后的各点点密度：', point_density.tolist())
    print('最后的各点中心距离：', nn)

    # 画图
    get_picture(data, laber, points_number, point_density, nn)
    """
    距离归一化：就把上面的nn改为：nn/max(nn)
    """


if __name__ == '__main__':
    main()
