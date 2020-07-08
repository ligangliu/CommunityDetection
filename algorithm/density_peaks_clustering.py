# -*- coding: utf-8 -*-

import numpy as np
from scipy.spatial import distance
import matplotlib.pyplot as plt


def clustering(dw, gamma=0.02, decision_graph=False,
               alpha=0.5, beta=0.5, cluster=True, metric='euclidean'):
    # step1: pairwise distance
    condensed_distance = distance.pdist(dw, metric=metric)
    d_c = np.sort(condensed_distance)[int(len(condensed_distance) * gamma)]
    redundant_distance = distance.squareform(condensed_distance)
    # step2: calculate local density
    rho = np.sum(np.exp(-(redundant_distance / d_c) ** 2), axis=1)
    # step3: calculate delta
    order_distance = np.argsort(redundant_distance, axis=1)
    delta = np.zeros_like(rho)
    nn = np.zeros_like(rho).astype(int)
    for i in range(len(delta)):
        mask = rho[order_distance[i]] > rho[i]
        if mask.sum() > 0:  # not the highest density point
            nn[i] = order_distance[i][mask][0]
            delta[i] = redundant_distance[i, nn[i]]
        else:  # the highest density point
            nn[i] = order_distance[i, -1]
            delta[i] = redundant_distance[i, nn[i]]
    if decision_graph:
        plt.scatter(rho, delta)
        plt.show()

    rho_c = min(rho) + (max(rho) - min(rho)) * alpha
    delta_c = min(delta) + (max(delta) - min(delta)) * beta
    centers = np.where(np.logical_and(rho > rho_c, delta > delta_c))[0]
    if not cluster:
        return centers
    else:
        labels = np.zeros_like(rho)
        for i, v in enumerate(centers):
            labels[v] = i
        order_rho = np.argsort(rho)[::-1]
        for p in order_rho:
            if p not in centers:
                labels[p] = labels[nn[p]]
        return centers, labels
