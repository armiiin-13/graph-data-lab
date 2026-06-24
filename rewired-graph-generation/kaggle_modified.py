import os
import ast
import pandas as pd
import kagglehub
from pyvis.network import Network

# Import Data
handle = "jfreyberg/spotify-artist-feature-collaboration-network"
dataset_path = kagglehub.dataset_download(handle, force_download=True) # download the whole dataset

nodes_path = os.path.join(dataset_path, "nodes.csv") # inner path to nodes.csv

df = pd.read_csv(nodes_path)
df["genres"] = df["genres"].apply(ast.literal_eval)

# Trim dataset
n = 300
trim_nodes = df.head(n)
valid_nodes = set(trim_nodes["spotify_id"].astype(str))

# Establish the edges
def are_connected(node_1, node_2):
    connected = False
    name = ''
    set_node_1 = node_1['genres']
    set_node_2 = node_2['genres']
    for genre in set_node_1:
        if genre in set_node_2:
            connected = True
            if name:
                name = name + '/ '
            name = name + str(genre)
    return connected, name

edges = []
for i in range(0,n):
    for j in range(i+1,n): # graph not directed (given the chosen condition)
        node_1 = trim_nodes.iloc[i]
        node_2 = trim_nodes.iloc[j]
        connected, name = are_connected(node_1, node_2)
        if connected:
            edges.append((node_1['spotify_id'], node_2['spotify_id'], name))

# Create the net
nt = Network(directed = False)
for i in range(0, n):
    node = trim_nodes.iloc[i]
    nt.add_node(node['spotify_id'], label = node['name'], color = 'blue')

for node_1, node_2, name in edges:
    nt.add_edge(node_1, node_2, label = name)

nt.show(name='modified_graph.html', notebook=False)

# DOCUMENTATION
## https://j2logo.com/como-concatenar-y-formatear-strings/
## https://stackoverflow.com/questions/9573244/how-to-check-if-the-string-is-empty-in-python