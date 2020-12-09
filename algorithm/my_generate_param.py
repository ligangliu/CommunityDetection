# -*- coding: utf-8 -*-#

#------------------------------------------------------------------------------- 
# Author:       liuligang
# Date:         2020/12/9
#-------------------------------------------------------------------------------


# 生成多组图像，muw为生成图像的控制参数，每幅图中以u对比，横坐标为on重叠节点个数
from my_objects import ShowResultImageParm, AlgorithmParam


def generate_muw_u_on():
    params = []
    show_image_params = []
    n = 1000
    muws = [0.05, 0.1, 0.2]
    us = [0.1, 0.2, 0.5, 1]  # 控制候选重叠节点的个数
    # 可能成为候选节点的控制参数
    ons = [0.01, 0.03, 0.05, 0.1]  # 重叠节点个数
    minc_maxc = 0.04
    for muw in muws:
        show_image_param = ShowResultImageParm()
        show_image_param.need_save = True
        show_image_param.need_show = False
        # 网络图的名称
        show_image_param.title = "muws-{}-u-on".format(muw)
        # 网络图的路径
        show_image_param.fig_path = "muws-{}-u-on.png".format(muw)
        show_image_param.xlable = "on"
        labels = []
        for_1 = []
        for u in us:
            labels.append("u={}".format(u))
            for_2 = []
            for on in ons:
                param = AlgorithmParam()
                param.minc = n * minc_maxc
                param.maxc = n * minc_maxc + 20
                param.u = u
                param.muw = muw
                param.mut = muw
                param.n = n
                param.on = n * on
                for_2.append(param)
            for_1.append(for_2)
        show_image_param.labels = labels
        show_image_param.x_trains = [int(on * n) for on in ons]
        show_image_params.append(show_image_param)
        params.append(for_1)
    return params, show_image_params


# 生成一组图像，在图像中，以muw为对比，横坐标为om重叠节点所属的社区个数
def generate_n_muw_om():
    params = []
    show_image_params = []
    nodes = [1000]
    muws = [0.05, 0.1, 0.2]
    u = 0.2
    on = 0.01
    oms = [2, 4, 6, 8]
    minc_maxc = 0.04
    for n in nodes:
        show_image_param = ShowResultImageParm()
        show_image_param.need_save = True
        show_image_param.need_show = False
        # 网络图的名称
        show_image_param.title = "n-{}-muw-om".format(n)
        # 网络图的路径
        show_image_param.fig_path = "n-{}-muw-om.png".format(n)
        show_image_param.xlable = "om"
        labels = []
        for_1 = []
        for muw in muws:
            labels.append("muw={}".format(muw))
            for_2 = []
            for om in oms:
                param = AlgorithmParam()
                param.minc = n * minc_maxc
                param.maxc = n * minc_maxc + 20
                param.u = u
                param.muw = muw
                param.mut = muw
                param.n = n
                param.on = n * on
                param.om = om
                for_2.append(param)
            for_1.append(for_2)
        show_image_param.labels = labels
        show_image_param.x_trains = [int(om) for om in oms]
        show_image_params.append(show_image_param)
        params.append(for_1)
    return params, show_image_params


# 生成一组图像，在图像中，以muw为对比，横坐标为on重叠节点个数
def generate_n_muw_on():
    params = []
    show_image_params = []
    nodes = [1000]
    muws = [0.05, 0.1, 0.2]
    u = 0.2
    ons = [0.01, 0.03, 0.05, 0.8, 0.1]
    minc_maxc = 0.04
    for n in nodes:
        show_image_param = ShowResultImageParm()
        show_image_param.need_save = True
        show_image_param.need_show = False
        # 网络图的名称
        show_image_param.title = "n-{}-muw-on".format(n)
        # 网络图的路径
        show_image_param.fig_path = "n-{}-muw-on.png".format(n)
        show_image_param.xlable = "om"
        labels = []
        for_1 = []
        for muw in muws:
            labels.append("muw={}".format(muw))
            for_2 = []
            for on in ons:
                param = AlgorithmParam()
                param.minc = n * minc_maxc
                param.maxc = n * minc_maxc + 20
                param.u = u
                param.muw = muw
                param.mut = muw
                param.n = n
                param.on = n * on
                for_2.append(param)
            for_1.append(for_2)
        show_image_param.labels = labels
        show_image_param.x_trains = [int(n * on) for on in ons]
        show_image_params.append(show_image_param)
        params.append(for_1)
    return params, show_image_params


# 生成多组图像，在图像中，以n为对比，横坐标为om重叠节点所属的社区个数
def generate_muw_n_om():
    params = []
    show_image_params = []
    muws = [0.05, 0.1, 0.2]
    nodes = [1000, 3000, 5000]
    u = 0.2
    oms = [2, 4, 6, 8]
    minc_maxc = 0.04
    for muw in muws:
        show_image_param = ShowResultImageParm()
        show_image_param.need_save = True
        show_image_param.need_show = False
        # 网络图的名称
        show_image_param.title = "muw-{}-n-om".format(muw)
        # 网络图的路径
        show_image_param.fig_path = "muw-{}-n-om.png".format(muw)
        show_image_param.xlable = "om"
        labels = []
        for_1 = []
        for n in nodes:
            labels.append("n={}".format(n))
            for_2 = []
            for om in oms:
                param = AlgorithmParam()
                param.minc = n * minc_maxc
                param.maxc = n * minc_maxc + 20
                param.u = u
                param.muw = muw
                param.mut = muw
                param.n = n
                param.on = n * 0.01
                param.om = om
                for_2.append(param)
            for_1.append(for_2)
        show_image_param.labels = labels
        show_image_param.x_trains = [int(om) for om in oms]
        show_image_params.append(show_image_param)
        params.append(for_1)
    return params, show_image_params

