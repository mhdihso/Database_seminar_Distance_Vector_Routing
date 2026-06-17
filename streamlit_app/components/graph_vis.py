"""
graph_vis.py — Pyvis-based interactive graph visualizer.
Renders network topology with highlighted paths and deleted links.
"""
import networkx as nx
import pandas as pd
import streamlit.components.v1 as components
from pyvis.network import Network
from typing import List, Optional, Tuple, Set


# Color palette
COLORS = {
    "node_default":   "#4A90D9",
    "node_highlight": "#FFCC00",
    "node_deleted":   "#E74C3C",
    "node_source":    "#00D4AA",
    "node_target":    "#FF6B6B",
    "edge_default":   "#555577",
    "edge_active":    "#00D4AA",
    "edge_deleted":   "#E74C3C",
    "bg":             "#0F1117",
    "label":          "#FFFFFF",
}


def build_pyvis(
    G: nx.Graph,
    active_path: Optional[List[str]] = None,
    deleted_nodes: Optional[Set[str]] = None,
    deleted_edges: Optional[Set[Tuple[str, str]]] = None,
    source: Optional[str] = None,
    target: Optional[str] = None,
    height: int = 480,
    show_weights: bool = True,
) -> Network:
    deleted_nodes = deleted_nodes or set()
    deleted_edges = deleted_edges or set()
    active_path = active_path or []

    # Build active path edge set
    path_edges = set()
    for i in range(len(active_path) - 1):
        path_edges.add((active_path[i], active_path[i + 1]))
        path_edges.add((active_path[i + 1], active_path[i]))

    net = Network(
        height=f"{height}px",
        width="100%",
        bgcolor=COLORS["bg"],
        font_color=COLORS["label"],
        directed=False,
    )
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 120},
        "barnesHut": {"gravitationalConstant": -8000, "springLength": 140}
      },
      "nodes": {
        "font": {"size": 16, "face": "Inter, sans-serif", "bold": true}
      },
      "edges": {
        "smooth": {"type": "dynamic"},
        "font": {"size": 12, "face": "Inter, sans-serif", "align": "middle"}
      },
      "interaction": {"hover": true, "tooltipDelay": 100}
    }
    """)

    for node in G.nodes():
        if node in deleted_nodes:
            color = COLORS["node_deleted"]
            size = 22
            border = "#FF0000"
        elif node == source:
            color = COLORS["node_source"]
            size = 28
            border = "#00FFD4"
        elif node == target:
            color = COLORS["node_target"]
            size = 28
            border = "#FF4444"
        elif node in active_path:
            color = COLORS["node_highlight"]
            size = 26
            border = "#FFA500"
        else:
            color = COLORS["node_default"]
            size = 22
            border = "#2255AA"

        net.add_node(
            node,
            label=str(node),
            color={"background": color, "border": border, "highlight": {"background": COLORS["node_highlight"]}},
            size=size,
            title=f"Router: {node}",
            shadow=True,
        )

    for u, v, data in G.edges(data=True):
        weight = data.get("weight", 1)
        is_deleted = (u, v) in deleted_edges or (v, u) in deleted_edges
        is_active = (u, v) in path_edges

        if is_deleted:
            edge_color = COLORS["edge_deleted"]
            dashes = True
            width = 2
        elif is_active:
            edge_color = COLORS["edge_active"]
            dashes = False
            width = 5
        else:
            edge_color = COLORS["edge_default"]
            dashes = False
            width = 2

        net.add_edge(
            u, v,
            label=str(weight) if show_weights else "",
            color=edge_color,
            width=width,
            dashes=dashes,
            title=f"Cost: {weight}" + (" [DELETED]" if is_deleted else ""),
        )

    return net


def render_pyvis(net: Network, key: str = "graph") -> None:
    """Render Pyvis network as an HTML component in Streamlit."""
    html = net.generate_html()
    components.html(html, height=500, scrolling=False)


def get_path_from_routing(
    routing_df: pd.DataFrame,
    source: str,
    target: str,
) -> List[str]:
    """Reconstruct the actual hop-by-hop path from routing table."""
    path = [source]
    current = source
    visited = {source}
    for _ in range(50):  # safety cap
        row = routing_df[
            (routing_df["from_node"] == current) &
            (routing_df["to_node"] == target)
        ]
        if row.empty:
            break
        next_hop = row.iloc[0]["next_hop"]
        if next_hop in visited:
            break
        path.append(next_hop)
        if next_hop == target:
            break
        current = next_hop
        visited.add(next_hop)
    return path
