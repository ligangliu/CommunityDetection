# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt

G = nx.petersen_graph()
print plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
