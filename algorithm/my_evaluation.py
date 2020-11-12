import os
import commands
import time

from algorithm.my_objects import AlgorithmParam


def generate_network(param):
    community_path = "/app/datasets/community.nmc"
    if os.path.exists(community_path):
        os.remove(community_path)
    networkx_path = "/app/datasets/community.nse"
    if os.path.exists(networkx_path):
        os.remove(networkx_path)
    assert isinstance(param, AlgorithmParam)
    n = param.n
    k = param.k
    maxk = param.maxk
    minc = param.minc
    maxc = param.maxc
    mut = param.mut
    muw = param.muw
    on = param.on
    om = param.om
    args = "-N {n} -k {k} -maxk {maxk} -minc {minc} -maxc {maxc} -mut {mut} -muw {muw} -on {on}  -om {om} -name /app/datasets/community" \
        .format(n=n, k=k, maxk=maxk, minc=minc, maxc=maxc, mut=mut, muw=muw, on=on, om=om)
    os.system("/app/datasets/benchmark {args}".format(args=args))
    while not os.path.exists(community_path):
        time.sleep(1)


def calculate_onmi():
    res = commands.getoutput("/app/datasets/onmi/onmi /app/datasets/lfr_code.txt /app/datasets/lfr_true.txt")
    lines = res.splitlines(True)
    onmi = 0.0
    for line in lines:
        if line.strip().startswith("lfk"):
            onmi = float(line.strip().split("\t")[1])

    return onmi


if __name__ == '__main__':
    res = generate_network()
    print res
