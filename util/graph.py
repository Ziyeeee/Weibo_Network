import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm
import numpy as np
import random


def build_graph(depth):
    data = []
    interior_nodes_id = []
    outer_nodes_id = []
    G = nx.DiGraph()
    users_dict = {3479691367: '周邹揪'}
    for i in range(0, depth + 1):
        with open('../data/relatives-depth{}.json'.format(i), 'r') as f:
            user_info = json.load(f)
            if i == depth:
                for info in user_info:
                    for fan in info['fans_info']:
                        outer_nodes_id.append(int(fan['fan_id']))
                    for follower in info['followers_info']:
                        outer_nodes_id.append(int(follower['follower_id']))
            else:
                for info in user_info:
                    for fan in info['fans_info']:
                        interior_nodes_id.append(int(fan['fan_id']))
                    for follower in info['followers_info']:
                        interior_nodes_id.append(int(follower['follower_id']))
        for info in user_info:
            user_id = int(info['user_id'])
            if not G.has_node(user_id):
                G.add_node(user_id, name=users_dict[user_id])
            for fan in info['fans_info']:
                fan_id = int(fan['fan_id'])
                if not G.has_node(fan_id):
                    G.add_node(fan_id, name=fan['fan_name'])
                G.add_edge(user_id, fan_id)
            for follower in info['followers_info']:
                follower_id = int(follower['follower_id'])
                if not G.has_node(follower_id):
                    G.add_node(follower_id, name=follower['follower_name'])
                G.add_edge(follower_id, user_id)
    return data


def draw_distribution(cnt_list, cut_num, x_label='', y_label='', title='', log=False):
    plt.hist(cnt_list, bins=cut_num, rwidth=0.8, log=log)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()


def draw_scatter(data, alpha, x_label='', y_label='', title='', xlog=False, ylog=False):
    for label, value in data.items():
        plt.scatter(value[0], value[1], s=20, alpha=alpha, label=label)
    if xlog:
        plt.xscale('log')
    if ylog:
        plt.ylabel('log')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    if len(data)>1:
        plt.legend()
    plt.show()


depth = 2
G, interior_nodes_id, outer_nodes_id = build_graph(depth)
G_un = nx.Graph(G)

zombies_id = []
for node in G.nodes(data=True):
    if node[0] in interior_nodes_id:
        if '用' in node[1]['name'] and '户' in node[1]['name']:
            zombies_id.append(node[0])

# in_degree = []
# for x in G.in_degree:
#     if x[0] in interior_nodes_id:
#         in_degree.append(x[1])
# draw_distribution(in_degree, 50, x_label='in degree', y_label='number of nodes', title='In Degree Distribution', log=True)
# out_degree = []
# for x in G.out_degree:
#     if x[0] in interior_nodes_id:
#         out_degree.append(x[1])
# draw_distribution(out_degree, 50, x_label='out degree', y_label='number of nodes', title='Out Degree Distribution', log=True)
# degree = []
# for x in G_un.degree:
#     if x[0] in interior_nodes_id:
#         degree.append(x[1])
# draw_distribution(degree, 50, x_label='degree', y_label='number of nodes', title='Degree Distribution of Undirected Graph', log=True)

# draw_scatter(in_degree, out_degree, alpha=0.1, x_label='in degree', y_label='out degree')

# average_shortest_path_length = nx.algorithms.shortest_paths.generic.average_shortest_path_length(G)
# print(average_shortest_path_length)
# average_shortest_path_length = nx.algorithms.shortest_paths.generic.average_shortest_path_length(G_un)
# print(average_shortest_path_length)

# length_dict = {}
# length = []
# shortest_path_length = nx.algorithms.shortest_paths.generic.shortest_path_length(G_un)
# for path in tqdm(shortest_path_length, total=len(G)):
#     # length_dict[path[0]] = path[1]
#     if len(list(path[1].values())[1:-1]) > 0:
#         length.append(np.sum(list(path[1].values())[1:-1])/(len(G)-1))
#     # else:
#     #     print(path[0])
# # with open('shortest path length.json', 'w') as f:
# #     json.dump(length_dict, f)
# # draw_distribution(length, 50, x_label='shortest path length', y_label='number of nodes', title='Average Shortest Path Length Distribution')
# draw_distribution(length, 50, x_label='shortest path length', y_label='number of nodes', title='Average Shortest Path Length Distribution', log=True)
# print(np.sum(length)/len(G))

# length = []
# shortest_path_length = nx.algorithms.shortest_paths.generic.shortest_path_length(G, list(interior_nodes_id)[0])
# for path_length in tqdm(shortest_path_length.values()):
#     length.append(path_length)
# draw_distribution(length, 50)

# clusters = nx.algorithms.cluster.clustering(G)
# draw_distribution(list(clusters.values()), 50, x_label='clustering coefficient', title='Clustering Coefficient Distribution', log=True)
# print(nx.algorithms.cluster.average_clustering(G))
#
# clusters = nx.algorithms.cluster.clustering(G, list(interior_nodes_id))
# draw_distribution(list(clusters.values()), 50, x_label='clustering coefficient', title='Clustering Coefficient Distribution of Undirected Graph', log=True)
# print(nx.algorithms.cluster.average_clustering(G_un))

# coreness = nx.algorithms.core.core_number(G)
# draw_distribution(list(coreness.values()), 50, x_label='coreness', title='Coreness Distribution', log=True)
#
# G_un.remove_edges_from(nx.selfloop_edges(G_un))
# coreness = nx.algorithms.core.core_number(G_un)
# draw_distribution(list(coreness.values()), 50, x_label='coreness', title='Coreness Distribution of Undirected Graph', log=True)

# nodes_id = G_un.nodes()
# sample_times = 100
# x = [0]
# y = [1]
# nodes_num = len(G_un)
# remove_num = int(1/sample_times*len(G_un))
# for i in range(0, sample_times):
#     remain_nodes_num = []
#     x.append(i*1/sample_times)
#     remove_nodes_id = random.sample(nodes_id, remove_num)
#     G_un.remove_nodes_from(remove_nodes_id)
#     # print(nx.algorithms.components.number_connected_components(G_un))
#     nodes = list(nx.algorithms.components.connected_components(G_un))
#     for node in nodes:
#         remain_nodes_num.append(len(node))
#     remain_nodes_num = max(remain_nodes_num)
#     y.append(remain_nodes_num/nodes_num)
# data = {'random attack': (x, y)}
#
# x = [0]
# y = [1]
# G, interior_nodes_id, outer_nodes_id = build_graph(depth)
# G_un = nx.Graph(G)
# node_degree = sorted(dict(G_un.degree).items(), key=lambda kv:(kv[1], kv[0]), reverse=True)
# for i in range(0, sample_times):
#     remain_nodes_num = []
#     remove_nodes_id = []
#     x.append(i*1/sample_times)
#     for node in node_degree[i*remove_num: (i+1)*remove_num]:
#         remove_nodes_id.append(node[0])
#     G_un.remove_nodes_from(remove_nodes_id)
#     # print(nx.algorithms.components.number_connected_components(G_un))
#     nodes = list(nx.algorithms.components.connected_components(G_un))
#     for node in nodes:
#         remain_nodes_num.append(len(node))
#     remain_nodes_num = max(remain_nodes_num)
#     y.append(remain_nodes_num/nodes_num)
# data['intentional attack'] = (x, y)
#
# draw_scatter(data, 0.5, x_label='removed percentage', y_label='connected percentage', title='robustness analysis')



in_degree = []
out_degree = []
degree = []
path_length = []
cluster = []
coreness = []
data = {}

clusters_dict = nx.algorithms.cluster.clustering(G)
coreness_dict = nx.algorithms.core.core_number(G)

for id in G.nodes():
    in_degree.append(G.in_degree(id))
    out_degree.append(G.out_degree(id))
    degree.append(G_un.degree(id))
    # shortest_path_length = nx.algorithms.shortest_paths.generic.shortest_path_length(G, id)
    # path_length.append(np.sum(list(shortest_path_length.values())[1:-1])/len(G)-1)
    cluster.append(clusters_dict[id])
    coreness.append(coreness_dict[id])

data['interior nodes'] = (cluster, coreness)

in_degree = []
out_degree = []
degree = []
path_length = []
cluster = []
coreness = []

for id in zombies_id:
    in_degree.append(G.in_degree(id))
    out_degree.append(G.out_degree(id))
    degree.append(G_un.degree(id))
    # shortest_path_length = nx.algorithms.shortest_paths.generic.shortest_path_length(G, id)
    # path_length.append(np.sum(list(shortest_path_length.values())[1:-1])/len(G)-1)
    cluster.append(clusters_dict[id])
    coreness.append(coreness_dict[id])

    # if G.in_degree(id) > 175:
    #     print(id, G.in_degree(id))

data['zombie nodes'] = (cluster, coreness)


# draw_scatter(path_length, cluster, 0.2)
# draw_scatter(degree, cluster, 0.2)
# draw_scatter(degree, path_length, 0.2)
# draw_scatter(in_degree, out_degree, alpha=0.1, x_label='in degree', y_label='out degree')
draw_scatter(data, 0.5, x_label='cluster', y_label='coreness', xlog=False, ylog=True)

# clusters = nx.algorithms.cluster.clustering(G, list(zombies_id))
# for key, value in clusters.items():
#     if value > 0:
#         print(key, value)
# draw_distribution(list(clusters.values()), 50, log=True)