import os
import commands
import time

def generate_network():
    community_path = "/app/datasets/community.nmc"
    if os.path.exists(community_path):
        os.remove(community_path)
    networkx_path = "/app/datasets/community.nse"
    if os.path.exists(networkx_path):
        os.remove(networkx_path)
    n = 1000
    k = 10
    maxk = 40
    minc = 80
    maxc = 100
    mut = 0.2
    muw = 0.2
    on = 30
    om = 2
    args = "-N {n} -k {k} -maxk {maxk} -minc {minc} -maxc {maxc} -mut {mut} -muw {muw} -on {on}  -om {om} -name /app/datasets/community"\
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
