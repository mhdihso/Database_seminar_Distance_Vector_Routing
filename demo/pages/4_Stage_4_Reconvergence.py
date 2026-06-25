"""
pages/4_Stage_4_Reconvergence.py — Re-convergence after network failure
"""
import streamlit as st
import pandas as pd
from components.graph_vis import build_pyvis, render_pyvis, get_path_from_routing
from core.network_gen import build_networkx_graph

st.markdown("""
<div class="stage-badge">Phase 4</div>
<h2 style="margin:0 0 0.3rem 0; font-size:1.9rem; font-weight:800; color:white;">
    Dynamic Re-convergence Analysis
</h2>
<p style="color:rgba(255,255,255,0.5); margin:0 0 1.5rem 0;">
    Evaluate routing updates following a topology alteration. Re-execute the algorithm on the modified dataset to compare pre- and post-failure routing paths.
</p>
""", unsafe_allow_html=True)

if not st.session_state.get("network_loaded"):
    st.markdown('<div class="warn-box">No active topology detected. Initialize topology in Phase 1 first.</div>', unsafe_allow_html=True)
    st.stop()

backend       = st.session_state["backend_instance"]
edges_list    = st.session_state["edges_list"]
nodes_list    = st.session_state["nodes_list"]
deleted_nodes = st.session_state.get("deleted_nodes", set())
deleted_edges  = st.session_state.get("deleted_edges", set())
routing_df_before = st.session_state.get("routing_df_before")

# Check if any failure happened
unique_del = set()
for a, b in deleted_edges:
    unique_del.add((min(a,b), max(a,b)))

has_failures = bool(deleted_nodes or unique_del)

if not has_failures:
    st.markdown("""
    <div class="warn-box">
        No topology disruption has been registered. Perform fault injection in Phase 3 prior to evaluating re-convergence behavior.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Summary of failures ──────────────────────────────────────────────────────
parts = []
if deleted_nodes:
    parts.append(f"**{len(deleted_nodes)} node(s) de-instantiated:** {', '.join(sorted(deleted_nodes))}")
if unique_del:
    parts.append(f"**{len(unique_del)} edge(s) dropped:** {', '.join([f'{a} - {b}' for a,b in sorted(unique_del)])}")

st.markdown(f"""
<div class="deleted-box">
    Injected Disruptions: &nbsp; {'&nbsp;|&nbsp;'.join(parts)}
</div>
""", unsafe_allow_html=True)

# ── Path selector ─────────────────────────────────────────────────────────────
alive_nodes = [n for n in sorted(nodes_list) if n not in deleted_nodes]
if len(alive_nodes) < 2:
    st.markdown('<div class="deleted-box">Insufficient operational nodes for routing computation.</div>',
                unsafe_allow_html=True)
    st.stop()

c1, c2 = st.columns(2)
with c1:
    source = st.selectbox("Source (s)", alive_nodes, key="reconv_source")
with c2:
    targets = [n for n in alive_nodes if n != source]
    target = st.selectbox("Destination (t)", targets, key="reconv_target")

# ── Run re-convergence ────────────────────────────────────────────────────────
if st.button("Execute Routing on Modified Topology", use_container_width=True):
    try:
        with st.spinner("Re-converging…"):
            routing_df_after, elapsed_after, sql_after = backend.run_routing()

        st.session_state["routing_df_after"] = routing_df_after
        st.session_state["elapsed_ms_after"] = elapsed_after * 1000
        st.session_state["last_sql_after"]   = sql_after
        st.rerun()
    except Exception as e:
        st.error(f"Execution failed: {str(e)}")
        st.stop()

routing_df_after = st.session_state.get("routing_df_after")
elapsed_ms_after = st.session_state.get("elapsed_ms_after")
elapsed_ms_before = st.session_state.get("elapsed_ms")

if routing_df_after is None:
    G_full = build_networkx_graph(edges_list)
    net_vis = build_pyvis(G_full, deleted_nodes=deleted_nodes, deleted_edges=deleted_edges)
    render_pyvis(net_vis, key="reconv_preview")
    st.markdown("""
    <div class="info-box">Click <b>Execute Routing on Modified Topology</b> to calculate new paths.</div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Results ────────────────────────────────────────────────────────────────────
active_path_after = get_path_from_routing(routing_df_after, source, target)
path_cost_after = routing_df_after[
    (routing_df_after["from_node"] == source) & (routing_df_after["to_node"] == target)
]["best_cost"].values
cost_after = int(path_cost_after[0]) if len(path_cost_after) > 0 else None

# Before path (if available)
cost_before = None
active_path_before = []
if routing_df_before is not None:
    pb = routing_df_before[
        (routing_df_before["from_node"] == source) & (routing_df_before["to_node"] == target)
    ]["best_cost"].values
    cost_before = int(pb[0]) if len(pb) > 0 else None
    active_path_before = get_path_from_routing(routing_df_before, source, target)

# ── Metrics ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{elapsed_ms_after:.3f}</div>
        <div class="metric-label">Re-conv time (ms)</div>
    </div>""", unsafe_allow_html=True)
with m2:
    cost_display = cost_after if cost_after is not None else "∞"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:{'#FF6B6B' if cost_after != cost_before else '#00D4AA'}">{cost_display}</div>
        <div class="metric-label">New path cost</div>
    </div>""", unsafe_allow_html=True)
with m3:
    cost_b_display = cost_before if cost_before is not None else "N/A"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:rgba(255,255,255,0.5)">{cost_b_display}</div>
        <div class="metric-label">Old path cost</div>
    </div>""", unsafe_allow_html=True)
with m4:
    hops_after = len(active_path_after) - 1 if active_path_after else 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{hops_after}</div>
        <div class="metric-label">New hops</div>
    </div>""", unsafe_allow_html=True)
with m5:
    delta = ""
    if cost_before is not None and cost_after is not None:
        diff = cost_after - cost_before
        delta = f"+{diff}" if diff > 0 else str(diff)
        delta_color = "#FF6B6B" if diff > 0 else "#00D4AA"
    else:
        delta = "N/A"
        delta_color = "#888"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="color:{delta_color}">{delta}</div>
        <div class="metric-label">Cost delta</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Path comparison banner ─────────────────────────────────────────────────────
if active_path_before:
    old_path_str = " → ".join(active_path_before)
else:
    old_path_str = "Unknown"

if active_path_after:
    new_path_str = " → ".join(active_path_after)
    st.markdown(f"""
    <div class="info-box">
        <b>Path prior to disruption:</b> <code style="color:rgba(255,255,255,0.6)">{old_path_str}</code>
        (cost: {cost_before if cost_before else "N/A"})<br>
        <b>Path post-reconvergence:</b>
        <code style="color:#00D4AA; font-weight:bold">{new_path_str}</code>
        (cost: {cost_after if cost_after is not None else '∞'})
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="deleted-box">
        <b>No path found</b> from {source} to {target} — network is partitioned.<br>
        Path prior to disruption was: <code>{old_path_str}</code>
    </div>
    """, unsafe_allow_html=True)

# ── Side-by-side before/after graphs ─────────────────────────────────────────
g_before, g_after = st.columns(2)
G_full = build_networkx_graph(edges_list)

with g_before:
    st.markdown("#### Initial Topology")
    net_before = build_pyvis(
        G_full,
        active_path=active_path_before,
        source=source, target=target, height=380,
    )
    render_pyvis(net_before, key="before_graph")

with g_after:
    st.markdown("#### Disrupted Topology (Post-Convergence)")
    net_after = build_pyvis(
        G_full,
        active_path=active_path_after,
        deleted_nodes=deleted_nodes,
        deleted_edges=deleted_edges,
        source=source, target=target, height=380,
    )
    render_pyvis(net_after, key="after_graph")

# ── Routing table diff ────────────────────────────────────────────────────────
st.markdown("### Routing Table Comparison")
t1, t2 = st.columns(2)

with t1:
    st.markdown("**Baseline Routing State (Full Network)**")
    if routing_df_before is not None:
        df_b = routing_df_before.copy()
        df_b.columns = ["From", "To", "Cost", "Next Hop"]
        st.dataframe(df_b, hide_index=True, use_container_width=True, height=260)
    else:
        st.info("Execute convergence simulation in Phase 2 to view baseline state.")

with t2:
    st.markdown("**Post-Convergence State (Disrupted Network)**")
    df_a = routing_df_after.copy()
    df_a.columns = ["From", "To", "Cost", "Next Hop"]

    # Highlight changed rows
    if routing_df_before is not None:
        before_map = {
            (r["from_node"], r["to_node"]): (r["best_cost"], r["next_hop"])
            for _, r in routing_df_before.iterrows()
        }

        def highlight_changed(row):
            key = (row["From"], row["To"])
            old = before_map.get(key)
            if old is None:
                return ["background-color: rgba(0,212,170,0.15)"] * 4  # new route
            if old[0] != row["Cost"] or old[1] != row["Next Hop"]:
                return ["background-color: rgba(255,107,107,0.15)"] * 4  # changed
            return [""] * 4

        styled = df_a.style.apply(highlight_changed, axis=1)
        st.dataframe(styled, hide_index=True, use_container_width=True, height=260)
    else:
        st.dataframe(df_a, hide_index=True, use_container_width=True, height=260)

st.markdown("""
<div style="font-size:0.8rem; color:rgba(255,255,255,0.4); margin-top:0.5rem;">
    Highlighted rows: Green indicates newly discovered paths; Red indicates paths with cost or next-hop modifications.
</div>
""", unsafe_allow_html=True)

# ── Cost Impact Analysis ─────────────────────────────────────────────────────
if routing_df_before is not None and routing_df_after is not None:
    st.markdown("---")
    st.markdown("### Cost Impact Analysis")

    import plotly.graph_objects as _go_r

    # Build comparison
    before_map = {
        (r["from_node"], r["to_node"]): r["best_cost"]
        for _, r in routing_df_before.iterrows()
    }
    after_map = {
        (r["from_node"], r["to_node"]): r["best_cost"]
        for _, r in routing_df_after.iterrows()
    }

    all_pairs = set(before_map.keys()) | set(after_map.keys())
    impact_rows = []
    for pair in sorted(all_pairs):
        cost_b = before_map.get(pair)
        cost_a = after_map.get(pair)
        if cost_b is not None and cost_a is not None:
            delta = cost_a - cost_b
            if delta != 0:
                impact_rows.append({
                    "Route": f"{pair[0]} -> {pair[1]}",
                    "Before": int(cost_b),
                    "After": int(cost_a),
                    "Delta": int(delta),
                })
        elif cost_b is not None and cost_a is None:
            impact_rows.append({
                "Route": f"{pair[0]} -> {pair[1]}",
                "Before": int(cost_b),
                "After": None,
                "Delta": None,
            })

    if impact_rows:
        impact_df = pd.DataFrame(impact_rows)
        valid_deltas = impact_df[impact_df["Delta"].notna()]

        if not valid_deltas.empty:
            colors = ["#FF6B6B" if d > 0 else "#00D4AA" for d in valid_deltas["Delta"]]
            fig_impact = _go_r.Figure(_go_r.Bar(
                x=valid_deltas["Route"],
                y=valid_deltas["Delta"],
                marker_color=colors,
                text=[f"+{d}" if d > 0 else str(d) for d in valid_deltas["Delta"]],
                textposition="outside",
                textfont=dict(color="white", size=11),
            ))
            fig_impact.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,17,26,0.85)",
                font=dict(family="Inter, sans-serif", color="#c9d1d9"),
                height=340,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(title="Affected Route", gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(title="Cost Delta (after - before)", gridcolor="rgba(255,255,255,0.06)"),
                title=dict(text="Per-Route Cost Change After Topology Disruption", font=dict(size=13)),
            )
            fig_impact.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
            st.plotly_chart(fig_impact, use_container_width=True)

        # Lost routes
        lost = impact_df[impact_df["Delta"].isna()]
        if not lost.empty:
            st.markdown(f"""
            <div class="deleted-box" style="font-size:0.84rem;">
                <b>Routes lost due to network partition ({len(lost)}):</b><br>
                {', '.join(lost["Route"].tolist())}
            </div>
            """, unsafe_allow_html=True)

        # Summary statistics
        if not valid_deltas.empty:
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color:#FF6B6B">{len(impact_rows)}</div>
                    <div class="metric-label">Routes affected</div>
                </div>""", unsafe_allow_html=True)
            with sc2:
                avg_delta = valid_deltas["Delta"].mean()
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color:#FFCC00">{avg_delta:+.1f}</div>
                    <div class="metric-label">Avg cost change</div>
                </div>""", unsafe_allow_html=True)
            with sc3:
                max_delta = valid_deltas["Delta"].max()
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-value" style="color:#E74C3C">{max_delta:+d}</div>
                    <div class="metric-label">Max cost increase</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box" style="font-size:0.84rem;">
            No route cost changes detected. All paths remain optimal after topology disruption.
        </div>
        """, unsafe_allow_html=True)
