import unicodedata
import re
import pandas as pd
from pyvis.network import Network

# Import data
df = pd.read_csv("output/artists.csv")

# Establish data types to attributes
def normalize_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # Remove accents
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Clean extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

def genres_to_set(value):
    if pd.isna(value) or value == "":
        return set()

    genre_list = value.split(',')
    genres = set()

    for genre in genre_list:
        clean_text = genre.strip().lower()
        if clean_text != "":
            genres.add(clean_text)

    return genres

df["artist_name"] = df["artist_name"].apply(normalize_text)
df['genres'] = df['genres'].apply(genres_to_set)

# Establish edges
    ## Edges are established if the similarity between two artists is higher than a threshold
    ## There are two types of connections: strongly connected artists (red) and related artists (gray)
    ## The edge label shows the shared genres between both artists

CONNECTION_THRESHOLD = 3.0

class Edge:
    STRONG_CONNECTION_THRESHOLD = 4.0

    def __init__(self, node_1, node_2, genres, value):
        self.node_1 = node_1
        self.node_2 = node_2
        self.genres = genres
        if value < Edge.STRONG_CONNECTION_THRESHOLD:
            self.color = "gray"
        else:
            self.color = "red"

def connection(node_1, node_2):
    genre_intersection = node_1['genres'].intersection(node_2['genres'])
    equal_language = node_1['language'] == node_2['language']

    value = 1 if equal_language else 0
    value += len(genre_intersection)

    if value < CONNECTION_THRESHOLD:
        return None
    else:
        return Edge(node_1['artist_name'], node_2['artist_name'], ','.join(genre_intersection), value)

edges = []

for i in range(0,len(df)):
    for j in range(i+1,len(df)): # graph not directed (for now)
        node_1 = df.iloc[i]
        node_2 = df.iloc[j]
        edge = connection(node_1, node_2)
        if edge:
            edges.append(edge)

# Assign node colors
GENRE_COLORS = {
    "pop": "#ff7eb6",
    "rock": "#ff6b6b",
    "hip-hop": "#f4a261",
    "r&b": "#9b5de5",
    "latin": "#ffb703",
    "classical": "#90be6d",
    "jazz": "#577590",
    "folk": "#43aa8b",
    "country": "#bc6c25",
    "reggae": "#2a9d8f",
    "k-pop": "#c77dff",
    "french": "#4895ef",
    "italian": "#06d6a0",
    "ambient": "#adb5bd",
    "metal": "#343a40",
    "punk": "#d00000"
}

def get_node_color(node):
    intersection = node["genres"].intersection(set(GENRE_COLORS.keys()))

    if len(intersection) == 1:
        return GENRE_COLORS[next(iter(intersection))]
    else:
        return 'gray'

# Create the net
nt = Network(
    height="750px",
    width="100%",
    directed=False,
    cdn_resources="in_line"
)

for i in range(len(df)):
    node = df.iloc[i]

    nt.add_node(
        node["artist_name"],
        label=node["artist_name"],
        color=get_node_color(node),
        size=15
    )

VISIBLE_EDGE_COLOR = "gray"

for edge in edges:
    if edge.color == "red":
        nt.add_edge(
            edge.node_1,
            edge.node_2,
            color=VISIBLE_EDGE_COLOR,
            physics=True,
            width=1
        )

nt.set_options("""
var options = {
  "edges": {
    "smooth": false
  },
  "interaction": {
    "hideEdgesOnDrag": true,
    "hideNodesOnDrag": false
  },
  "physics": {
    "enabled": true,
    "solver": "forceAtlas2Based",
    "forceAtlas2Based": {
      "gravitationalConstant": -80,
      "centralGravity": 0.01,
      "springLength": 180,
      "springConstant": 0.02,
      "damping": 0.4,
      "avoidOverlap": 0.5
    },
    "stabilization": {
      "enabled": true,
      "iterations": 300,
      "updateInterval": 25,
      "fit": true
    }
  }
}
""")

import webbrowser

html = nt.generate_html(notebook=False)

with open("custom_net.html", "w", encoding="utf-8") as f:
    f.write(html)

webbrowser.open("custom_net.html")