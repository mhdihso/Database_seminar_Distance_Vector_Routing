"""
pages/1_Stage_1_Network_Setup.py — Network Installation
"""
import streamlit as st
import pandas as pd
import networkx as nx
from core.network_gen import PRESETS, preset_to_directed_edges, build_networkx_graph, custom_edges_to_list
from core.db_backends import BACKENDS
from components.graph_vis import build_pyvis, render_pyvis

st.markdown("""
<div class="stage-badge">Phase 1</div>
<h2 style="margin:0 0 0.3rem 0; font-size:1.9rem; font-weight:800; color:white;">
    Network Topology Initialization
</h2>
<p style="color:rgba(255,255,255,0.5); margin:0 0 1.5rem 0;">
    Define and instantiate the network graph topology within the active database backend.
</p>
""", unsafe_allow_html=True)

# ── Topology selection ───────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.6], gap="large")

with col_left:
    st.markdown("### Topology Selection")

    mode = st.radio(
        "Input mode",
        ["Preset topology", "Custom edges"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "Preset topology":
        preset_name = st.selectbox(
            "Select a preset network",
            list(PRESETS.keys()),
            index=0,
        )
        preset = PRESETS[preset_name]
        st.markdown(f"""
        <div class="info-box">
            <b>{preset_name}</b><br>
            <span style="color:rgba(255,255,255,0.55); font-size:0.85rem;">{preset['description']}</span>
        </div>
        """, unsafe_allow_html=True)
        edges_directed = preset_to_directed_edges(preset_name)
        edges_display = preset["edges"]   # undirected for display
        nodes = preset["nodes"]

    else:
        st.markdown("""
        <div class="info-box" style="font-size:0.83rem;">
            Enter one edge per line: <code style="color:#00D4AA">FROM  TO  COST</code><br>
            Note: Edges are directed. For bidirectional links, specify both directions.
        </div>
        """, unsafe_allow_html=True)

        default_custom = "A B 3\nA C 23\nB C 2\nC D 5"
        custom_text = st.text_area(
            "Custom edges", default_custom, height=160,
            placeholder="A B 3\nB C 5\nC D 2",
            label_visibility="collapsed",
        )
        custom_edges, err = custom_edges_to_list(custom_text)
        if err:
            st.error(f"Parse error: {err}")
            st.stop()
        
        edges_directed = custom_edges
        edges_display = custom_edges
        nodes = list({e[0] for e in edges_directed} | {e[1] for e in edges_directed})
        preset_name = "Custom"

    st.markdown("---")

    # Edge table preview
    st.markdown("#### Edge Table Preview")
    preview_df = pd.DataFrame(edges_display, columns=["from_node", "to_node", "cost"])
    st.dataframe(
        preview_df.style.set_properties(**{
            "background-color": "rgba(0,0,0,0)",
            "color": "white",
        }),
        use_container_width=True, hide_index=True, height=200
    )

    st.markdown(f"""
    <div style="display:flex; gap:1rem; margin-top:0.5rem;">
        <div class="metric-card" style="flex:1;">
            <div class="metric-value">{len(nodes)}</div>
            <div class="metric-label">Nodes</div>
        </div>
        <div class="metric-card" style="flex:1;">
            <div class="metric-value">{len(edges_display)}</div>
            <div class="metric-label">Links</div>
        </div>
        <div class="metric-card" style="flex:1;">
            <div class="metric-value">{len(edges_directed)}</div>
            <div class="metric-label">Directed Edges</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    backend_name = st.session_state.get("backend_name", "DuckDB (USING KEY)")

    if st.button(f"Commit Topology to {backend_name.split('(')[0].strip()}", use_container_width=True):
        BackendCls = BACKENDS[backend_name]
        backend = BackendCls()
        backend.load_edges(edges_directed)

        st.session_state["backend_instance"] = backend
        st.session_state["edges_list"]       = edges_directed
        st.session_state["edges_display"]    = edges_display
        st.session_state["nodes_list"]       = nodes
        st.session_state["network_loaded"]   = True
        st.session_state["routing_done"]     = False
        st.session_state["routing_df"]       = None
        st.session_state["routing_df_before"] = None
        st.session_state["routing_df_after"] = None
        st.session_state["deleted_nodes"]    = set()
        st.session_state["deleted_edges"]    = set()
        st.session_state["preset_name"]      = preset_name

        st.success(f"Graph instantiated: {len(edges_directed)} directed edges committed to {backend_name}.")

with col_right:
    st.markdown("### Graph Visualization")
    G = build_networkx_graph(edges_directed)
    net = build_pyvis(G, height=440)
    render_pyvis(net, key="setup_graph")

    if st.session_state["network_loaded"]:
        st.markdown("""
        <div class="info-box">
            Topology is instantiated. Proceed to <b>Phase 2: Convergence Simulation</b> to execute the routing protocol.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warn-box">
            Action required: Click <b>"Commit Topology"</b> to write this graph definition into the selected database.
        </div>
        """, unsafe_allow_html=True)

# ── SQL preview ─────────────────────────────────────────────────────────────
st.markdown("### Generated Schema and Insertion SQL")
if edges_directed:
    values = ",\n    ".join([f"('{f}', '{t}', {c})" for f, t, c in edges_directed])
    sql_preview = f"""CREATE TABLE edges (
    from_node TEXT,
    to_node   TEXT,
    cost      INTEGER
);

INSERT INTO edges VALUES
    {values};"""
    st.markdown(f'<div class="sql-block">{sql_preview}</div>', unsafe_allow_html=True)

# ── Network Statistics ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Graph-Theoretic Properties")

G_stats = build_networkx_graph(edges_directed)
G_undirected = G_stats.to_undirected()

n_nodes_g = G_stats.number_of_nodes()
n_edges_g = G_undirected.number_of_edges()
max_possible = n_nodes_g * (n_nodes_g - 1) / 2 if n_nodes_g > 1 else 1
density = n_edges_g / max_possible if max_possible > 0 else 0

# Degree distribution
degrees = [d for _, d in G_undirected.degree()]
avg_degree = sum(degrees) / len(degrees) if degrees else 0

# Diameter and avg shortest path (only if connected)
try:
    if nx.is_connected(G_undirected):
        diameter = nx.diameter(G_undirected)
        avg_path = nx.average_shortest_path_length(G_undirected, weight="weight")
    else:
        diameter = "N/A (disconnected)"
        avg_path = "N/A"
except Exception:
    diameter = "N/A"
    avg_path = "N/A"

# Clustering coefficient
try:
    clustering = nx.average_clustering(G_undirected)
except Exception:
    clustering = 0

stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
stat_items = [
    (f"{density:.3f}", "Graph Density", "#00D4AA"),
    (f"{avg_degree:.1f}", "Avg Degree", "#FFCC00"),
    (str(diameter), "Diameter", "#4A90D9"),
    (f"{avg_path:.2f}" if isinstance(avg_path, float) else str(avg_path), "Avg Path Length", "#A78BFA"),
    (f"{clustering:.3f}", "Clustering Coeff.", "#FF6B6B"),
]
for col, (val, label, c) in zip([stat_col1, stat_col2, stat_col3, stat_col4, stat_col5], stat_items):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{c}; font-size:1.5rem;">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

# Degree distribution chart
import plotly.graph_objects as _go_s1

degree_counts = {}
for d in degrees:
    degree_counts[d] = degree_counts.get(d, 0) + 1

fig_deg = _go_s1.Figure(_go_s1.Bar(
    x=list(degree_counts.keys()),
    y=list(degree_counts.values()),
    marker=dict(
        color=list(degree_counts.keys()),
        colorscale=[[0, "#00D4AA"], [1, "#4A90D9"]],
    ),
    text=list(degree_counts.values()),
    textposition="outside",
    textfont=dict(color="white"),
))
fig_deg.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,26,0.85)",
    font=dict(family="Inter, sans-serif", color="#c9d1d9"),
    height=280,
    margin=dict(l=10, r=10, t=35, b=10),
    xaxis=dict(title="Degree (k)", gridcolor="rgba(255,255,255,0.06)", dtick=1),
    yaxis=dict(title="Frequency", gridcolor="rgba(255,255,255,0.06)"),
    title=dict(text="Node Degree Distribution P(k)", font=dict(size=13)),
)
st.plotly_chart(fig_deg, use_container_width=True)

st.markdown("""
<div class="info-box" style="font-size:0.84rem;">
<b>Graph density</b> measures the ratio of actual edges to the maximum possible edges in the graph.
A density of 1.0 indicates a complete graph. The <b>clustering coefficient</b> measures the tendency
of nodes to cluster together, indicating network redundancy. Higher clustering implies more
alternative paths, which improves fault tolerance during re-convergence (Phase 4).
</div>
""", unsafe_allow_html=True)
