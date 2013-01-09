#!/usr/bin/python

import networkx as nx
import matplotlib.pyplot as plt

area = nx.readwrite.read_yaml('testmap.yaml')
pos = area.cardinal_positions()
nx.draw(area, pos=nx.spring_layout(area, pos=pos, fixed=pos.keys()))
nx.draw_networkx_edge_labels(
    area,
    pos=nx.spring_layout(area, pos=pos,
                         fixed=pos.keys()),
    edge_labels=nx.get_edge_attributes(area, 'exit')
)
plt.show()
