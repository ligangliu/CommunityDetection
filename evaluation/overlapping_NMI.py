# -*- coding: utf-8 -*-

import scipy as sp
import math
from scipy.stats import entropy

################## Helper functions ##############
logBase = 2


def __partial_entropy_a_proba(proba):
    if proba == 0:
        return 0
    return -proba * math.log(proba, logBase)


def __cover_entropy(cover, allNodes):  # cover is a list of set, no com ID
    allEntr = []
    for com in cover:
        fractionIn = len(com) / len(allNodes)
        allEntr.append(sp.stats.entropy([fractionIn, 1 - fractionIn], base=logBase))

    return sum(allEntr)


def __com_pair_conditional_entropy(cl, clKnown, allNodes):  # cl1,cl2, snapshot_communities (set of nodes)
    nbNodes = len(allNodes)

    a = len((set(allNodes) - set(cl)) - set(clKnown)) / nbNodes
    b = len(set(clKnown) - set(cl)) / nbNodes
    c = len(set(cl) - set(clKnown)) / nbNodes
    d = len(set(cl) & set(clKnown)) / nbNodes

    if __partial_entropy_a_proba(a) + __partial_entropy_a_proba(d) > __partial_entropy_a_proba(
            b) + __partial_entropy_a_proba(c):
        entropyKnown = entropy([len(clKnown) / nbNodes, 1 - len(clKnown) / nbNodes], base=logBase)
        conditionalEntropy = entropy([a, b, c, d], base=logBase) - entropyKnown
        # print("normal",entropyKnown,sp.stats.entropy([a,b,c,d],base=logBase))
    else:
        conditionalEntropy = entropy([len(cl) / nbNodes, 1 - len(cl) / nbNodes], base=logBase)
    # print("abcd",a,b,c,d,conditionalEntropy,cl,clKnown)

    return conditionalEntropy  # *nbNodes


def __cover_conditional_entropy(cover, coverRef, allNodes, normalized=False):  # cover and coverRef and list of set
    X = cover
    Y = coverRef

    allMatches = []
    # print(cover)
    # print(coverRef)
    for com in cover:
        matches = [(com2, __com_pair_conditional_entropy(com, com2, allNodes)) for com2 in coverRef]
        bestMatch = min(matches, key=lambda c: c[1])
        HXY_part = bestMatch[1]
        if normalized:
            HX = __partial_entropy_a_proba(len(com) / len(allNodes)) + __partial_entropy_a_proba(
                (len(allNodes) - len(com)) / len(allNodes))
            if HX == 0:
                HXY_part = 1
            else:
                HXY_part = HXY_part / HX
        allMatches.append(HXY_part)
    # print(allMatches)
    to_return = sum(allMatches)
    if normalized:
        to_return = to_return / len(cover)
    return to_return


def onmi(cover, coverRef, allNodes=None, variant="LFK"):  # cover and coverRef should be list of set, no community ID
    if (len(cover) == 0 and len(coverRef) != 0) or (len(cover) != 0 and len(coverRef) == 0):
        return 0
    if cover == coverRef:
        return 1

    if allNodes == None:
        allNodes = {n for c in coverRef for n in c}
        allNodes |= {n for c in cover for n in c}

    if variant == "LFK":
        HXY = __cover_conditional_entropy(cover, coverRef, allNodes, normalized=True)
        HYX = __cover_conditional_entropy(coverRef, cover, allNodes, normalized=True)
    else:
        HXY = __cover_conditional_entropy(cover, coverRef, allNodes)
        HYX = __cover_conditional_entropy(coverRef, cover, allNodes)

    HX = __cover_entropy(cover, allNodes)
    HY = __cover_entropy(coverRef, allNodes)

    NMI = -10
    if variant == "LFK":
        NMI = 1 - 0.5 * (HXY + HYX)
    elif variant == "MGH_LFK":
        NMI = 1 - 0.5 * (HXY / HX + HYX / HY)
    elif variant == "MGH":
        IXY = 0.5 * (HX - HXY + HY - HYX)
        NMI = IXY / (max(HX, HY))
    if NMI < 0 or NMI > 1 or math.isnan(NMI):
        print "NMI: %s  from %s %s %s %s " % (NMI, HXY, HYX, HX, HY)
        raise Exception("incorrect NMI")
    return NMI

if __name__=='__main__':
    cover = [[1, 2, 3, 4],
             [3, 4, 5, 6, 7],
             [6, 7, 8, 9]]
    cover_ref = [[1, 2, 3, 4],
                 [3, 4, 5, 6, 8],
                 [6, 7, 8, 9]]
    print onmi(cover, cover_ref)
    # from sklearn import metrics
    # print metrics.normalized_mutual_info_score(cover, cover_ref)



