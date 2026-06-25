"""
pages/3_Stage_3_Delete_Nodes.py — Simulate network failures by deleting nodes/edges
"""
import streamlit as st
import pandas as pd
from components.graph_vis import build_pyvis, render_pyvis
from core.network_gen import build_networkx_graph

st.markdown("""
<div class="stage-badge">Phase 3</div>
<h2 style="margin:0 0 0.3rem 0; font-size:1.9rem; font-weight:800; color:white;">
    Network Topology Disruption
</h2>
<p style="color:rgba(255,255,255,0.5); margin:0 0 1.5rem 0;">
    Simulate topological disruptions by de-instantiating nodes or links, representing router hardware failure or link propagation degradation.
</p>
""", unsafe_allow_html=True)

if not st.session_state.get("network_loaded"):
    st.markdown("""
    <div class="warn-box">No active topology detected. Initialize topology in Phase 1 first.</div>
    """, unsafe_allow_html=True)
    st.stop()

backend      = st.session_state["backend_instance"]
edges_list   = st.session_state["edges_list"]
nodes_list   = st.session_state["nodes_list"]
deleted_nodes = st.session_state.get("deleted_nodes", set())
deleted_edges  = st.session_state.get("deleted_edges", set())

# Active edges (excluding already deleted)
def get_current_edges():
    try:
        df = backend.get_edges()
        return list(df.itertuples(index=False, name=None))
    except Exception:
        return []

current_edges = get_current_edges()
current_nodes = list({e[0] for e in current_edges} | {e[1] for e in current_edges})

# ── Two-panel layout ─────────────────────────────────────────────────────────
ctrl_col, graph_col = st.columns([1, 1.5], gap="large")

with ctrl_col:
    st.markdown("### Delete Operations")

    op_type = st.radio(
        "Select Deletion Type",
        ["Remove Node", "Remove Link between 2 nodes"],
        horizontal=True,
        key="delete_op_type"
    )

    if op_type == "Remove Node":
        st.markdown("""
        <div class="warn-box" style="font-size:0.85rem;">
            Removing a router node deletes all its connected links from the topology.
        </div>
        """, unsafe_allow_html=True)

        deletable_nodes = [n for n in sorted(current_nodes) if n not in deleted_nodes]
        if not deletable_nodes:
            st.info("No nodes left to delete.")
        else:
            node_to_del = st.selectbox("Select node to remove", deletable_nodes, key="del_node_sel")
            affected = [(f, t, c) for f, t, c in current_edges
                        if f == node_to_del or t == node_to_del]
            st.markdown(f"""
            <div class="info-box" style="font-size:0.83rem;">
                Removing <b style="color:#E74C3C">{node_to_del}</b> will drop
                <b>{len(affected)}</b> connected edge(s):<br>
                <code style="font-size:0.78rem;">
                    {', '.join([f"{f} - {t}" for f, t, _ in affected[:6]])}
                    {'...' if len(affected) > 6 else ''}
                </code>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Remove Node {node_to_del}", use_container_width=True):
                backend.delete_node(node_to_del)
                st.session_state["deleted_nodes"].add(node_to_del)
                st.session_state["routing_done"] = False
                st.session_state["routing_df"]   = None
                st.success(f"Node **{node_to_del}** removed. Connected links deleted.")
                st.rerun()

    else:
        st.markdown("""
        <div class="warn-box" style="font-size:0.85rem;">
            Removing a link deletes the communication channel between the two selected nodes.
        </div>
        """, unsafe_allow_html=True)

        active_nodes_with_edges = sorted(list({e[0] for e in current_edges} | {e[1] for e in current_edges}))

        if not active_nodes_with_edges:
            st.info("No active nodes or links left.")
        else:
            n1 = st.selectbox("Select Node 1", active_nodes_with_edges, key="del_edge_n1")
            neighbors = sorted(list({e[1] for e in current_edges if e[0] == n1} |
                                     {e[0] for e in current_edges if e[1] == n1}))
            if not neighbors:
                st.info(f"No active links connected to Node {n1}.")
            else:
                n2 = st.selectbox("Select Node 2", neighbors, key="del_edge_n2")
                match = [e for e in current_edges if (e[0] == n1 and e[1] == n2) or (e[0] == n2 and e[1] == n1)]
                cost = match[0][2] if match else 0

                st.markdown(f"""
                <div class="deleted-box" style="font-size:0.83rem;">
                    Action: Drop Link: <b style="color:#E74C3C">{n1} - {n2}</b> (cost: {cost})
                </div>
                """, unsafe_allow_html=True)

                del_sql = f"DELETE FROM edges\nWHERE (from_node='{n1}' AND to_node='{n2}')\n   OR (from_node='{n2}' AND to_node='{n1}');"
                st.markdown(f'<div class="sql-block">{del_sql}</div>', unsafe_allow_html=True)

                if st.button(f"Drop Link {n1}-{n2}", use_container_width=True):
                    backend.delete_edge(n1, n2)
                    st.session_state["deleted_edges"].add((n1, n2))
                    st.session_state["deleted_edges"].add((n2, n1))
                    st.session_state["routing_done"] = False
                    st.session_state["routing_df"]   = None
                    st.success(f"Link **{n1} - {n2}** successfully dropped.")
                    st.rerun()

    # ── Deletion log ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Disruption Log")

    if deleted_nodes:
        st.markdown(f"""
        <div class="deleted-box">
            <b>De-instantiated nodes:</b> {', '.join(sorted(deleted_nodes))}
        </div>
        """, unsafe_allow_html=True)

    unique_del_edges = set()
    for a, b in st.session_state.get("deleted_edges", set()):
        unique_del_edges.add((min(a, b), max(a, b)))
    if unique_del_edges:
        link_list = ", ".join([f"{a} - {b}" for a, b in sorted(unique_del_edges)])
        st.markdown(f"""
        <div class="deleted-box">
            <b>Dropped edges:</b> {link_list}
        </div>
        """, unsafe_allow_html=True)

    if not deleted_nodes and not unique_del_edges:
        st.markdown("""
        <div class="info-box">Topology fully connected: no faults injected.</div>
        """, unsafe_allow_html=True)

    # Undo all
    if st.button("Restore Original Topology", use_container_width=True):
        # Reload original edges
        backend.load_edges(edges_list)
        st.session_state["deleted_nodes"] = set()
        st.session_state["deleted_edges"] = set()
        st.session_state["routing_done"]  = False
        st.session_state["routing_df"]    = None
        st.success("Topology successfully restored to initial state.")
        st.rerun()

with graph_col:
    st.markdown("### Topology Connectivity State")

    # Rebuild graph from current (live) edges
    live_edges = get_current_edges()
    all_edges_for_graph = edges_list  # full original for shape
    G_full = build_networkx_graph(all_edges_for_graph)

    net_vis = build_pyvis(
        G_full,
        deleted_nodes=st.session_state.get("deleted_nodes", set()),
        deleted_edges=st.session_state.get("deleted_edges", set()),
        height=460,
    )
    render_pyvis(net_vis, key="delete_graph")

    # Current edge table
    st.markdown("#### Active Edges in Database Relation")
    if live_edges:
        live_df = pd.DataFrame(live_edges, columns=["from_node", "to_node", "cost"])
        st.dataframe(live_df, hide_index=True, use_container_width=True, height=220)
        st.markdown(f"""
        <div style="font-size:0.8rem; color:rgba(255,255,255,0.4); margin-top:0.3rem;">
            {len(live_edges)} directed edge(s) remaining in the database
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="deleted-box">No edges remaining: topology is disconnected.</div>',
                    unsafe_allow_html=True)

    if deleted_nodes or unique_del_edges:
        st.markdown("""
        <div class="info-box" style="margin-top:0.8rem;">
            Topology state modified. Proceed to <b>Phase 4: Dynamic Re-convergence</b> to evaluate path recalculation.
        </div>
        """, unsafe_allow_html=True)
