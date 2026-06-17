"""
pages/2_Stage_2_Routing_Simulation.py — Academic routing simulation with convergence analysis
"""
import time
import streamlit as st
import pandas as pd
import networkx as nx
from plotly.subplots import make_subplots
from components.graph_vis import build_pyvis, render_pyvis, get_path_from_routing
from core.network_gen import build_networkx_graph

st.markdown("""
<div class="stage-badge">Phase 2</div>
<h2 style="margin:0 0 0.3rem 0; font-size:1.9rem; font-weight:800; color:white;">
    Distance-Vector Convergence Simulation
</h2>
<p style="color:rgba(255,255,255,0.45); margin:0 0 1.5rem 0; font-size:0.92rem;">
    Execute the routing algorithm against the live database and observe iterative convergence
    of the distributed Bellman-Ford relaxation to globally-optimal shortest paths.
</p>
""", unsafe_allow_html=True)

if not st.session_state.get("network_loaded"):
    st.markdown('<div class="warn-box">No active topology detected. Initialize topology in Phase 1 first.</div>',
                unsafe_allow_html=True)
    st.stop()

backend      = st.session_state["backend_instance"]
edges_list   = st.session_state["edges_list"]
nodes_list   = st.session_state["nodes_list"]
backend_name = st.session_state.get("backend_name", "DuckDB (USING KEY)")
deleted_nodes = st.session_state.get("deleted_nodes", set())
deleted_edges  = st.session_state.get("deleted_edges", set())
G = build_networkx_graph(edges_list)

# ── Controls ──────────────────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns([1, 1, 2])
with col_a:
    alive = [n for n in sorted(nodes_list) if n not in deleted_nodes]
    source = st.selectbox("Source router (s)", alive, key="rt_source")
with col_b:
    targets = [n for n in alive if n != source]
    target  = st.selectbox("Destination router (t)", targets, key="rt_target")
with col_c:
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        animate = st.toggle("Step-by-step animation", value=True)
        speed   = st.slider("ms / iteration", 200, 1500, 600, 50,
                            disabled=not animate, label_visibility="collapsed") if animate else 600
    with col_c2:
        if "Pure Python" in backend_name:
            python_algo = st.selectbox(
                "Evaluation Algorithm",
                ["Bellman-Ford", "Dijkstra", "Floyd-Warshall"],
                index=0,
                key="python_algo_choice"
            )
            backend.algo = python_algo
            backend_name = backend.name

st.divider()

# Backend tag
be_color = {"DuckDB (USING KEY)": "#FFCC00", "SQLite (Standard CTE)": "#4A90D9"}
color = "#50C878" if "Pure Python" in backend_name else be_color.get(backend_name, "#888")
n_directed = len(edges_list)
n_undirected = len({(min(a,b), max(a,b)) for a,b,_ in edges_list})
V = len(nodes_list)

st.markdown(f"""
<div style="display:flex; gap:1rem; align-items:center; margin-bottom:1rem;">
  <div style="padding:0.5rem 1rem; background:rgba(255,255,255,0.04);
              border-radius:8px; border-left:3px solid {color}; font-size:0.87rem; flex:1;">
    Engine: <b style="color:{color}">{backend_name}</b> &nbsp;|&nbsp;
    |V| = <b>{V}</b> &nbsp;|&nbsp; |E| = <b>{n_undirected}</b> &nbsp;|&nbsp;
    Directed: <b>{n_directed}</b> &nbsp;|&nbsp;
    Max BF rounds: <b>{V-1}</b>
  </div>
</div>
""", unsafe_allow_html=True)

run_btn = st.button("Execute Routing Algorithm", use_container_width=False)

if run_btn:
    try:
        with st.spinner("Executing SQL query…"):
            routing_df, elapsed, sql_used = backend.run_routing()

        # Compute iteration steps for animation / analysis
        steps = backend.run_routing_steps()

        st.session_state.update({
            "routing_df":        routing_df,
            "routing_df_before": routing_df,
            "routing_done":      True,
            "elapsed_ms":   elapsed * 1000,
            "last_sql":     sql_used,
            "path_source":  source,
            "path_target":  target,
            "conv_steps":   steps,
            "active_path":  get_path_from_routing(routing_df, source, target),
        })
    except Exception as e:
        st.error(f"Execution failed: {str(e)}")
        st.stop()

routing_df  = st.session_state.get("routing_df")
elapsed_ms  = st.session_state.get("elapsed_ms")
last_sql    = st.session_state.get("last_sql", "")
conv_steps  = st.session_state.get("conv_steps", [])

if routing_df is None:
    net_vis = build_pyvis(G, deleted_nodes=deleted_nodes, deleted_edges=deleted_edges)
    render_pyvis(net_vis, key="pre_routing_graph")
    st.markdown('<div class="info-box">Click <b>Execute Routing Algorithm</b> to begin convergence computations.</div>',
                unsafe_allow_html=True)
    st.stop()

active_path = get_path_from_routing(routing_df, source, target)
st.session_state["active_path"] = active_path

path_rows = routing_df[
    (routing_df["from_node"] == source) & (routing_df["to_node"] == target)
]
path_cost = int(path_rows["best_cost"].values[0]) if not path_rows.empty else None
hops = len(active_path) - 1 if active_path else 0
n_routes = len(routing_df)
conv_iters = len(conv_steps)

# ── KPI strip ──────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
kpis = [
    (f"{elapsed_ms:.4f}", "Query time (ms)",     "#00D4AA"),
    (f"{path_cost if path_cost is not None else '∞'}", f"d({source},{target})", "#FFCC00"),
    (str(hops),          "Hops",                  "#4A90D9"),
    (str(conv_iters),    "Convergence rounds",    "#A78BFA"),
    (str(n_routes),      "|FIB| entries",         "#50C878"),
]
for col, (val, label, c) in zip([m1, m2, m3, m4, m5], kpis):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{c}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

if active_path:
    path_str = " → ".join(active_path)
    st.markdown(f"""
    <div class="info-box" style="margin-top:1rem;">
        <b>Shortest path</b> {source} → {target}: &nbsp;
        <code style="color:#00D4AA; font-size:0.95rem;">{path_str}</code>
        &nbsp; (cost = <b style="color:#00D4AA">{path_cost}</b>, hops = <b>{hops}</b>)
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f'<div class="deleted-box">No path found from {source} to {target}.</div>',
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main panels ────────────────────────────────────────────────────────────────
g_col, t_col = st.columns([1.4, 1], gap="large")

with g_col:
    st.markdown("#### Forwarding Information Base Visualisation")
    net_vis = build_pyvis(G, active_path=active_path,
                          deleted_nodes=deleted_nodes, deleted_edges=deleted_edges,
                          source=source, target=target)
    render_pyvis(net_vis, key="routing_graph")

with t_col:
    if animate and conv_steps:
        st.markdown(f"#### Iterative Convergence  *({conv_iters} rounds)*")
        placeholder = st.empty()
        note = st.empty()
        for i, step_df in enumerate(conv_steps):
            disp = step_df.copy()
            disp.columns = ["From", "To", "d*", "Next Hop"]
            note.markdown(f"""
            <div style="font-size:0.78rem; color:rgba(255,255,255,0.4); margin-bottom:0.3rem;">
                Round <b>{i+1}</b> of {conv_iters} &nbsp;—&nbsp; {len(step_df)} routes in FIB
            </div>""", unsafe_allow_html=True)
            placeholder.dataframe(disp, hide_index=True, use_container_width=True, height=340)
            time.sleep(speed / 1000)
        note.markdown(f"""
        <div style="font-size:0.78rem; color:#00D4AA; margin-bottom:0.3rem;">
            Convergence achieved after <b>{conv_iters}</b> iteration(s) — distance metrics minimized.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("#### Forwarding Information Base (FIB)")
        disp = routing_df.copy()
        disp.columns = ["From", "To", "d*", "Next Hop"]

        def _hl(row):
            if row["From"] == source and row["To"] == target:
                return ["background-color:rgba(0,212,170,0.2);font-weight:700"] * 4
            if row["From"] == source:
                return ["background-color:rgba(0,212,170,0.07)"] * 4
            return [""] * 4

        st.dataframe(disp.style.apply(_hl, axis=1),
                     hide_index=True, use_container_width=True, height=380)

# ── SQL + Analysis tabs ────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
tab_sql, tab_analysis, tab_matrix, tab_conv_evo, tab_all = st.tabs([
    "SQL Compilation", "Path Analysis", "Distance Matrix", "Convergence Evolution", "Forwarding Information Base"
])

with tab_sql:
    st.markdown(f'<div class="sql-block">{last_sql}</div>', unsafe_allow_html=True)
    be_notes = {
        "DuckDB (USING KEY)": (
            "**DuckDB `USING KEY`** -- Each recursive iteration only holds the *delta* rows "
            "(those whose best_cost improved in the last round). `recurring.routing_table` "
            "gives access to the full accumulated FIB. The query terminates when the delta is empty."
        ),
        "SQLite (Standard CTE)": (
            "**SQLite (append-only)** -- All acyclic paths are accumulated with `UNION ALL`. "
            "A `visited` column prevents cycle re-entry. The final `GROUP BY ... MIN(cost)` "
            "discards suboptimal paths post-hoc -- this step is unnecessary in DuckDB."
        ),
        "Pure Python (Bellman-Ford)": (
            "**Pure Python** -- Classic Bellman-Ford: distance matrix relaxed V-1 times. "
            "Early-exit on no improvement. O(V^2 * E) worst case."
        ),
    }
    note = be_notes.get(backend_name, "")
    if note:
        st.markdown(f'<div class="info-box" style="font-size:0.84rem; margin-top:0.8rem;">{note}</div>',
                    unsafe_allow_html=True)

with tab_analysis:
    if routing_df is not None and not routing_df.empty:
        # Eccentricity histogram
        from_source = routing_df[routing_df["from_node"] == source].copy()
        from_source = from_source.sort_values("best_cost")

        import plotly.graph_objects as _go
        fig_bar = _go.Figure(_go.Bar(
            x=from_source["to_node"], y=from_source["best_cost"],
            marker=dict(
                color=from_source["best_cost"],
                colorscale=[[0,"#00D4AA"],[0.5,"#FFCC00"],[1,"#E74C3C"]],
                showscale=True,
                colorbar=dict(title=dict(text="d*", font=dict(color="white")),
                              tickfont=dict(color="white")),
            ),
            text=from_source["best_cost"], textposition="outside",
            textfont=dict(color="white"),
        ))
        fig_bar.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,17,26,0.85)",
            font=dict(family="Inter", color="#c9d1d9"),
            height=320, margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(title=f"Destination", gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title=f"d*({source}, v)", gridcolor="rgba(255,255,255,0.06)"),
            title=dict(text=f"Shortest-path distances from {source}", font=dict(size=13)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Summary stats
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Distance vector from selected source**")
            st.dataframe(from_source[["to_node","best_cost","next_hop"]].rename(
                columns={"to_node":"Destination","best_cost":"d*","next_hop":"Next Hop"}),
                hide_index=True, use_container_width=True)
        with col2:
            costs = from_source["best_cost"]
            stats_df = pd.DataFrame({
                "Metric": ["Min d*", "Max d*", "Mean d*", "Std d*",
                           "Diameter (max)", "Nodes reachable"],
                "Value":  [
                    f"{costs.min():.0f}", f"{costs.max():.0f}",
                    f"{costs.mean():.2f}", f"{costs.std():.2f}",
                    f"{costs.max():.0f}", str(len(costs)),
                ]
            })
            st.dataframe(stats_df, hide_index=True, use_container_width=True)

with tab_matrix:
    import plotly.graph_objects as _go2
    st.markdown("#### All-Pairs Shortest-Path Distance Matrix  $D^*$")
    st.markdown("""
    <div class="info-box" style="font-size:0.84rem; margin-bottom:1rem;">
    The distance matrix $D^*[i][j]$ contains the optimal cost from router $i$ to router $j$.
    This is the converged result of the Bellman-Ford relaxation. Darker cells indicate higher cost.
    Diagonal entries are zero (self-loops).
    </div>
    """, unsafe_allow_html=True)

    if routing_df is not None and not routing_df.empty:
        sorted_nodes = sorted(nodes_list)
        INF_VAL = 9999
        matrix = []
        for s in sorted_nodes:
            row = []
            for t in sorted_nodes:
                if s == t:
                    row.append(0)
                else:
                    match = routing_df[(routing_df["from_node"] == s) & (routing_df["to_node"] == t)]
                    row.append(int(match["best_cost"].values[0]) if not match.empty else INF_VAL)
            matrix.append(row)

        labels = [[str(v) if v < INF_VAL else "inf" for v in row] for row in matrix]

        fig_mat = _go2.Figure(_go2.Heatmap(
            z=matrix,
            x=sorted_nodes,
            y=sorted_nodes,
            text=labels,
            texttemplate="%{text}",
            textfont=dict(size=13, color="white"),
            colorscale=[[0, "#0a1628"], [0.3, "#00D4AA"], [0.6, "#FFCC00"], [1, "#E74C3C"]],
            showscale=True,
            colorbar=dict(
                title=dict(text="d*", font=dict(color="white")),
                tickfont=dict(color="white"),
            ),
            hoverongaps=False,
        ))
        fig_mat.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,17,26,0.85)",
            font=dict(family="Inter, sans-serif", color="#c9d1d9"),
            height=max(350, 60 * len(sorted_nodes)),
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis=dict(title="Destination (t)", side="bottom"),
            yaxis=dict(title="Source (s)", autorange="reversed"),
            title=dict(text="Distance Matrix D*[s][t] — Converged Shortest-Path Costs", font=dict(size=13)),
        )
        st.plotly_chart(fig_mat, use_container_width=True)

        # Next-hop matrix
        st.markdown("#### Next-Hop Forwarding Matrix  $N[s][t]$")
        hop_rows = []
        for s in sorted_nodes:
            hop_row = {}
            for t in sorted_nodes:
                if s == t:
                    hop_row[t] = "-"
                else:
                    match = routing_df[(routing_df["from_node"] == s) & (routing_df["to_node"] == t)]
                    hop_row[t] = str(match["next_hop"].values[0]) if not match.empty else "-"
            hop_rows.append(hop_row)
        hop_df = pd.DataFrame(hop_rows, index=sorted_nodes)
        hop_df.index.name = "From \\ To"
        st.dataframe(hop_df, use_container_width=True, height=max(200, 40 * len(sorted_nodes)))

        st.markdown("""
        <div class="info-box" style="font-size:0.84rem; margin-top:0.8rem;">
        The next-hop matrix $N[s][t]$ specifies the first router on the optimal path
        from $s$ to $t$. This is the operational forwarding table used by each router
        to make local forwarding decisions without global topology knowledge.
        </div>
        """, unsafe_allow_html=True)

with tab_conv_evo:
    import plotly.graph_objects as _go3
    st.markdown("#### Convergence Evolution per Iteration")

    if conv_steps and len(conv_steps) > 0:
        st.markdown("""
        <div class="info-box" style="font-size:0.84rem; margin-bottom:1rem;">
        This chart tracks two metrics across Bellman-Ford iterations:
        (1) the number of entries in the forwarding information base (FIB size), and
        (2) the number of entries that were updated (improved) in each round.
        Convergence is achieved when the update count reaches zero.
        </div>
        """, unsafe_allow_html=True)

        # Track routes discovered and updates per round
        fib_sizes = [len(step) for step in conv_steps]
        updates = [fib_sizes[0]]  # first round = all new
        for i in range(1, len(conv_steps)):
            prev = conv_steps[i - 1]
            curr = conv_steps[i]
            prev_map = {(r["from_node"], r["to_node"]): r["best_cost"] for _, r in prev.iterrows()}
            changed = 0
            for _, r in curr.iterrows():
                key = (r["from_node"], r["to_node"])
                if key not in prev_map or prev_map[key] != r["best_cost"]:
                    changed += 1
            updates.append(changed)

        rounds = list(range(1, len(conv_steps) + 1))

        fig_evo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_evo.add_trace(
            _go3.Bar(
                x=rounds, y=fib_sizes,
                name="FIB size (entries)",
                marker_color="rgba(0,212,170,0.6)",
                marker_line=dict(color="#00D4AA", width=1),
            ),
            secondary_y=False,
        )
        fig_evo.add_trace(
            _go3.Scatter(
                x=rounds, y=updates,
                name="Updates (improvements)",
                mode="lines+markers",
                line=dict(color="#FFCC00", width=2.5),
                marker=dict(size=9, color="#FFCC00", line=dict(width=1.5, color="#0a0e1a")),
            ),
            secondary_y=True,
        )

        fig_evo.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,17,26,0.85)",
            font=dict(family="Inter, sans-serif", color="#c9d1d9"),
            height=380,
            margin=dict(l=10, r=10, t=40, b=10),
            title=dict(text="FIB growth and update count per relaxation round", font=dict(size=13)),
            legend=dict(
                bgcolor="rgba(0,0,0,0.4)",
                bordercolor="rgba(255,255,255,0.08)",
                borderwidth=1,
            ),
        )
        fig_evo.update_xaxes(title_text="Iteration (round)", gridcolor="rgba(255,255,255,0.06)")
        fig_evo.update_yaxes(title_text="FIB entries", gridcolor="rgba(255,255,255,0.06)", secondary_y=False)
        fig_evo.update_yaxes(title_text="Updates in round", gridcolor="rgba(255,255,255,0.06)", secondary_y=True)

        st.plotly_chart(fig_evo, use_container_width=True)

        # Convergence table
        conv_table = pd.DataFrame({
            "Round": rounds,
            "FIB Entries": fib_sizes,
            "Updates": updates,
            "Converged": ["Yes" if u == 0 else "No" for u in updates],
        })
        st.dataframe(conv_table, hide_index=True, use_container_width=True)
    else:
        st.markdown('<div class="warn-box">No convergence step data available. Execute routing first.</div>',
                    unsafe_allow_html=True)

with tab_all:
    st.markdown(f"**Complete FIB -- {len(routing_df)} entries across {len(nodes_list)} routers**")
    full_disp = routing_df.copy()
    full_disp.columns = ["Router (From)", "Destination", "d*", "Next Hop"]
    st.dataframe(full_disp, hide_index=True, use_container_width=True, height=460)
