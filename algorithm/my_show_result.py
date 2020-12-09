# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Author:       liuligang
# Date:         2020/11/21
# 主要是用来自动化协助我们画实验结果图
# -------------------------------------------------------------------------------
from my_util import init_path

path, run_platform = init_path()
if run_platform == "linux":
    import matplotlib
    matplotlib.use('Agg')
from matplotlib import pyplot
from my_objects import ShowResultImageParm


def show_result_image(image_param):
    import matplotlib.pyplot as plt
    assert isinstance(image_param, ShowResultImageParm)
    x_trains = image_param.x_trains
    y_trains = image_param.y_trains
    labels = image_param.labels
    xlable = image_param.xlable
    ylable = image_param.ylable
    title = image_param.title
    names = [str(x) for x in list(x_trains)]
    temp = ['o', '*', '^', '+', 'p', '<', 'h', 'd', '1', '2']
    x = range(len(names))
    for i in range(0, len(labels)):
        plt.plot(x, y_trains[i], marker=temp[i], ms=10, label=labels[i])
    plt.legend()  # 让图例生效
    plt.xticks(x, names, rotation=2)
    plt.margins(0)
    plt.subplots_adjust(bottom=0.10)
    plt.xlabel(xlable)  # X轴标签
    plt.ylabel(ylable)  # Y轴标签
    yticks = get_yticks(y_trains)
    pyplot.yticks(yticks)
    plt.title(title)  # 标题
    if image_param.need_save:
        path = "./result_images/"+image_param.fig_path
        plt.savefig(path, dpi=900)
    if image_param.need_show:
        plt.show()
    plt.close()


def get_yticks(y_trains):
    temp = []
    for y_train in y_trains:
        for x in y_train:
            temp.append(float(x))
    min_y = min(temp)
    max_y = max(temp)
    temp_a = [0, 0.05, 0.1, 0.15, 0.20, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9,
              0.95, 1.0]
    for i in range(1, len(temp_a)):
        if min_y < temp_a[i]:
            min_y = i - 1
            break
    for i in range(1, len(temp_a)):
        if max_y <= temp_a[i]:
            max_y = i
            break
    return temp_a[min_y:max_y + 1]

if __name__=='__main__':
    x_trains = [10, 30, 50, 80, 100]
    y_train_1 = [0.955212, 0.80293, 0.766985, 0.560851, 0.693094]
    y_train_2 = [0.687154, 0.835161, 0.768803, 0.41646, 0.39768]
    y_train_3 = [0.849364, 0.664035, 0.654224, 0.492962, 0.482282]
    y_train_4 = [0.756983, 0.740806, 0.761683, 0.511095, 0.602937]
    y_train_5 = [0.796661, 0.832886, 0.736865, 0.643563, 0.470698]
    y_trains = [y_train_1, y_train_2, y_train_3, y_train_4, y_train_5]
    labels = ['t=0.2', 't=0.4', 't=0.6', 't=0.8', 't=1.0']
    image_param = ShowResultImageParm()
    image_param.x_trains = x_trains
    image_param.y_trains = y_trains
    image_param.labels = labels

    image_param.need_show = True
    image_param.need_save = False
    image_param.title = "test"
    image_param.fig_path = "b.png"
    show_result_image(image_param)
