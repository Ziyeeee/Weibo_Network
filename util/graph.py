import json
import networkx as nx
import matplotlib.pyplot as plt


def build_graph(depth):
    data = []
    G = nx.DiGraph()
    users_dict = {3479691367: '周邹揪'}
    for i in range(0, depth+1):
        with open('../data/relatives-depth{}.json'.format(i), 'r') as f:
            data += json.load(f)
    for info in data:
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
    return G


G = build_graph(1)