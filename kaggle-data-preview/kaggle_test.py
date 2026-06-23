import os
import pandas as pd
import kagglehub
from pyvis.network import Network

# Import Data
handle = "jfreyberg/spotify-artist-feature-collaboration-network"
dataset_path = kagglehub.dataset_download(handle) # download the whole dataset

nodes_path = os.path.join(dataset_path, "nodes.csv") # inner path to nodes.csv
edges_path = os.path.join(dataset_path, "edges.csv") # inner path to edges.csv

df_nodes = pd.read_csv(nodes_path)
df_edges = pd.read_csv(edges_path)

# Trim dataset
n = 300
trim_nodes = df_nodes.head(n)
valid_nodes = set(trim_nodes["spotify_id"].astype(str))

# Create the net
nt = Network(directed = False)
for i in range(0, n):
    node = trim_nodes.iloc[i]
    nt.add_node(node['spotify_id'], label = node['name'], color = 'blue')

for i in range(0, len(df_edges)):
    edge = df_edges.iloc[i]
    if edge['id_0'] in valid_nodes and edge['id_1'] in valid_nodes:
        nt.add_edge(edge['id_0'], edge['id_1'])

nt.show(name='test_graph.html', notebook=False)


# DOCUMENTATION
## https://github.com/Kaggle/kagglehub/blob/main/README.md
## https://pyvis.readthedocs.io/en/latest/documentation.html
## https://www.kaggle.com/code/residentmario/creating-reading-and-writing
## https://pandas.pydata.org/docs/user_guide/10min.html