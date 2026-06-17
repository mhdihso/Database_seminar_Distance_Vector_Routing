"""
network_gen.py — Preset topologies and custom network builder.
"""
import networkx as nx
from typing import List, Tuple, Dict

# Each preset returns a list of (from_node, to_node, cost) tuples (bidirectional)
PRESETS: Dict[str, Dict] = {
    "Seminar (4 nodes)": {
        "description": "The exact network from the seminar — A,B,C,D with Bellman-Ford convergence example.",
        "edges": [
            ("A", "B", 3), ("A", "C", 23),
            ("B", "C", 2), ("C", "D", 5),
        ],
        "nodes": ["A", "B", "C", "D"],
    },
    "Star (5 nodes)": {
        "description": "Central hub connected to 4 leaves — simulates a simple ISP hub.",
        "edges": [
            ("Hub", "R1", 1), ("Hub", "R2", 2),
            ("Hub", "R3", 4), ("Hub", "R4", 7),
            ("R1", "R2", 6),
        ],
        "nodes": ["Hub", "R1", "R2", "R3", "R4"],
    },
    "ISP Backbone (8 nodes)": {
        "description": "Medium-sized ISP backbone with redundant paths and asymmetric costs.",
        "edges": [
            ("NYC", "CHI", 4),  ("NYC", "WDC", 2),
            ("CHI", "DEN", 5),  ("CHI", "ATL", 6),
            ("WDC", "ATL", 3),  ("DEN", "LAX", 3),
            ("ATL", "DAL", 4),  ("DAL", "LAX", 5),
            ("DAL", "DEN", 2),  ("LAX", "NYC", 15),
        ],
        "nodes": ["NYC", "CHI", "WDC", "ATL", "DEN", "DAL", "LAX"],
    },
    "Ring (6 nodes)": {
        "description": "Ring topology — each node connected only to its two neighbors.",
        "edges": [
            ("R1", "R2", 2), ("R2", "R3", 3),
            ("R3", "R4", 1), ("R4", "R5", 4),
            ("R5", "R6", 2), ("R6", "R1", 5),
        ],
        "nodes": ["R1", "R2", "R3", "R4", "R5", "R6"],
    },
    "Mesh (6 nodes)": {
        "description": "Densely connected mesh — many redundant paths for stress testing.",
        "edges": [
            ("A", "B", 1), ("A", "C", 4), ("A", "D", 7),
            ("B", "C", 2), ("B", "E", 5),
            ("C", "D", 1), ("C", "F", 6),
            ("D", "E", 3), ("D", "F", 2),
            ("E", "F", 1),
        ],
        "nodes": ["A", "B", "C", "D", "E", "F"],
    },
}

def preset_to_directed_edges(preset_name: str) -> List[Tuple[str, str, int]]:
    """Expand bidirectional preset edges into directed pairs."""
    edges = PRESETS[preset_name]["edges"]
    directed = []
    for (f, t, c) in edges:
        directed.append((f, t, c))
        directed.append((t, f, c))
    return directed

def build_networkx_graph(edges: List[Tuple[str, str, int]]) -> nx.Graph:
    """Build an undirected NetworkX graph from edge list."""
    G = nx.Graph()
    for f, t, c in edges:
        if not G.has_edge(f, t):
            G.add_edge(f, t, weight=c)
    return G

def get_preset_names() -> List[str]:
    return list(PRESETS.keys())

def custom_edges_to_list(text: str) -> Tuple[List[Tuple[str, str, int]], str]:
    """
    Parse custom edge text.  Format per line:  A B 5
    Returns (edges_list, error_message).
    """
    edges = []
    for i, line in enumerate(text.strip().splitlines(), 1):
        parts = line.strip().split()
        if not parts:
            continue
        if len(parts) != 3:
            return [], f"Line {i}: expected 'FROM TO COST', got: '{line.strip()}'"
        f, t = parts[0].upper(), parts[1].upper()
        try:
            c = int(parts[2])
            if c <= 0:
                return [], f"Line {i}: cost must be positive, got {c}"
        except ValueError:
            return [], f"Line {i}: cost must be an integer, got '{parts[2]}'"
        edges.append((f, t, c))
    return edges, ""
