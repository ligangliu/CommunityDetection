# -*- coding: utf-8 -*-

import numpy as np
import math

from sklearn import metrics

'''
     https://www.cnblogs.com/ziqiao/archive/2011/12/13/2286273.html
     例子：
     A = [1 2 1 1 1 1 1 2 2 2 2 3 1 1 3 3 3]
     B = [1 1 1 1 1 1 2 2 2 2 2 2 3 3 3 3 3]
     
'''


# A: 社区发现的节点对应的社团编号
# B: 对应节点的真实社区编号
def NMI(A, B):
    # len(A) should be equal to len(B)
    total = len(A)
    A_ids = set(A)
    B_ids = set(B)
    # Mutual information
    MI = 0
    eps = 1.4e-45
    for idA in A_ids:
        for idB in B_ids:
            idAOccur = np.where(A == idA)
            idBOccur = np.where(B == idB)
            idABOccur = np.intersect1d(idAOccur, idBOccur)
            px = 1.0 * len(idAOccur[0]) / total
            py = 1.0 * len(idBOccur[0]) / total
            pxy = 1.0 * len(idABOccur) / total
            MI = MI + pxy * math.log(pxy / (px * py) + eps, 2)
    # Normalized Mutual information
    Hx = 0
    for idA in A_ids:
        idAOccurCount = 1.0 * len(np.where(A == idA)[0])
        Hx = Hx - (idAOccurCount / total) * math.log(idAOccurCount / total + eps, 2)
    Hy = 0
    for idB in B_ids:
        idBOccurCount = 1.0 * len(np.where(B == idB)[0])
        Hy = Hy - (idBOccurCount / total) * math.log(idBOccurCount / total + eps, 2)
    MIhat = 2.0 * MI / (Hx + Hy)
    return MIhat


def NMI_2(com, real_com):
    """
    Compute the Normalized Mutual Information(NMI)

    Parameters
    --------
    com, real_com : list or numpy.array
        number of community of nodes
    """
    if len(com) != len(real_com):
        return ValueError('len(A) should be equal to len(B)')

    com = np.array(com)
    real_com = np.array(real_com)
    total = len(com)
    com_ids = set(com)
    real_com_ids = set(real_com)
    # Mutual information
    MI = 0
    eps = 1.4e-45
    for id_com in com_ids:
        for id_real in real_com_ids:
            idAOccur = np.where(com == id_com)
            idBOccur = np.where(real_com == id_real)
            idABOccur = np.intersect1d(idAOccur, idBOccur)
            px = 1.0 * len(idAOccur[0]) / total
            py = 1.0 * len(idBOccur[0]) / total
            pxy = 1.0 * len(idABOccur) / total
            MI = MI + pxy * math.log(pxy / (px * py) + eps, 2)
    # Normalized Mutual information
    Hx = 0
    for idA in com_ids:
        idAOccurCount = 1.0 * len(np.where(com == idA)[0])
        Hx = Hx - (idAOccurCount / total) * math.log(idAOccurCount / total + eps, 2)
    Hy = 0
    for idB in real_com_ids:
        idBOccurCount = 1.0 * len(np.where(real_com == idB)[0])
        Hy = Hy - (idBOccurCount / total) * math.log(idBOccurCount / total + eps, 2)
    MIhat = 2.0 * MI / (Hx + Hy)
    return MIhat


if __name__ == '__main__':
    A = np.array([2, 2, 2])
    B = np.array([1, 1, 1])
    # print NMI(A, B)  # 0.364561771857
    # print NMI_2(A, B)
    print metrics.normalized_mutual_info_score(A, B, average_method='arithmetic')
