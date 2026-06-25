"""
pages/5_Benchmark_Compare.py — Academic multi-aspect performance analysis
"""
import math
import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from core.benchmark import (
    run_benchmark, aggregate_results,
    NETWORK_SIZES_QUICK, NETWORK_SIZES_FULL, BACKENDS_MAP
)

# ── palette ──────────────────────────────────────────────────────────────────
BE_COLOR = {
    "DuckDB (USING KEY)":    "#FFCC00",
    "SQLite (Standard CTE)": "#4A90D9",
    "Pure Python":           "#50C878",
}
BE_DASH = {
    "DuckDB (USING KEY)":    "solid",
    "SQLite (Standard CTE)": "dash",
    "Pure Python":           "dot",
}
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,26,0.85)",
    font=dict(family="Inter, sans-serif", color="#c9d1d9", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor="rgba(0,0,0,0.4)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        font=dict(size=11),
    ),
)
GRID = dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stage-badge">Phase 5</div>
<h2 style="margin:0 0 0.2rem 0; font-size:1.9rem; font-weight:800; color:white;">
    Empirical Performance Evaluation
</h2>
<p style="color:rgba(255,255,255,0.45); margin:0 0 1.2rem 0; font-size:0.92rem;">
    Empirical comparison of DuckDB <code>USING KEY</code>, SQLite standard CTEs, and pure Python
    across execution time, memory footprint, scalability ratio, and result-set cardinality.
</p>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.4, 1, 1, 1])
with ctrl1:
    mode = st.radio("Benchmark mode", ["Quick Execution  (~8s)", "Full Evaluation  (~25s)"],
                    horizontal=True, label_visibility="collapsed")
    sizes = NETWORK_SIZES_QUICK if "Quick" in mode else NETWORK_SIZES_FULL
    n_tests = len(BACKENDS_MAP) * len(sizes) * 3
    st.markdown(f"""
    <div style="font-size:0.78rem; color:rgba(255,255,255,0.4); margin-top:0.3rem;">
        {len(BACKENDS_MAP)} backends × {len(sizes)} network sizes × 3 runs = <b style="color:#00D4AA">{n_tests} measurements</b>
    </div>""", unsafe_allow_html=True)
with ctrl2:
    run_btn = st.button("Run Benchmark", use_container_width=True)
with ctrl3:
    clear_btn = st.button("Clear Results", use_container_width=True)
with ctrl4:
    log_scale = st.toggle("Log Y-axis", value=False)

if clear_btn:
    st.session_state["benchmark_results"] = None
    st.session_state["benchmark_running"] = False
    st.rerun()

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    st.session_state["benchmark_running"] = True
    st.session_state["benchmark_results"] = None
    st.rerun()

# If marked as running — execute now (this persists across rerenders)
if st.session_state.get("benchmark_running"):
    prog = st.progress(0.0, text="Initializing...")
    status = st.empty()

    def _cb(pct, label):
        prog.progress(min(pct, 1.0), text=f"{label}  ({pct*100:.0f}%)")

    df_raw = run_benchmark(sizes=sizes, progress_cb=_cb)
    prog.progress(1.0, text="Evaluation complete.")
    status.markdown(f"""
    <div class="info-box" style="font-size:0.84rem; margin-top:0.5rem;">
        Completed <b>{len(df_raw)}</b> measurements across
        <b>{df_raw['backend'].nunique()}</b> backends and
        <b>{df_raw['n_nodes'].nunique()}</b> network sizes.
    </div>""", unsafe_allow_html=True)
    st.session_state["benchmark_results"] = df_raw
    st.session_state["benchmark_running"] = False
    st.rerun()

df_raw = st.session_state.get("benchmark_results")

if df_raw is None:
    # ── Empty state ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:3rem 1rem; background:rgba(255,255,255,0.02);
                border:1px solid rgba(255,255,255,0.06); border-radius:16px; margin-top:1rem;">
        <div style="font-size:1.1rem; font-weight:600; color:rgba(255,255,255,0.7);">
            Dataset Empty: No Evaluation Data
        </div>
        <div style="color:rgba(255,255,255,0.35); font-size:0.88rem; margin-top:0.4rem;">
            Select execution parameters and select <b>Run Benchmark</b>.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Experimental Design")
    rows = []
    for b in BACKENDS_MAP:
        for n in (NETWORK_SIZES_FULL if "Full" in mode else NETWORK_SIZES_QUICK):
            rows.append({"Backend": b, "N (nodes)": n,
                         "Directed edges (approx)": f"~{int(n*(n-1)*0.45*0.9)}", "Runs": 3})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.stop()

# ── Aggregate ─────────────────────────────────────────────────────────────────
agg = aggregate_results(df_raw)

# ── KPI strip ─────────────────────────────────────────────────────────────────
duck = agg[agg["backend"] == "DuckDB (USING KEY)"]
sqli = agg[agg["backend"] == "SQLite (Standard CTE)"]
py   = agg[agg["backend"] == "Pure Python"]

duck_mean = duck["avg_ms"].mean()
sqli_mean = sqli["avg_ms"].mean()
py_mean   = py["avg_ms"].mean()
overall_speedup = sqli_mean / max(duck_mean, 1e-9)

largest_n = agg["n_nodes"].max()
duck_large = duck[duck["n_nodes"] == largest_n]["avg_ms"].values
sqli_large = sqli[sqli["n_nodes"] == largest_n]["avg_ms"].values
peak_speedup = (sqli_large[0] / max(duck_large[0], 1e-9)) if len(duck_large) and len(sqli_large) else 0

duck_mem = duck["avg_kb"].mean()
sqli_mem = sqli["avg_kb"].mean()
mem_ratio = sqli_mem / max(duck_mem, 1e-9)

k1, k2, k3, k4, k5 = st.columns(5)
kpi_data = [
    (f"{overall_speedup:.1f}×", "Avg DuckDB speedup", "#FFCC00"),
    (f"{peak_speedup:.1f}×",    f"Speedup at N={largest_n}", "#FF6B6B"),
    (f"{duck_mean:.3f}",        "DuckDB avg (ms)",    "#00D4AA"),
    (f"{sqli_mean:.3f}",        "SQLite avg (ms)",    "#4A90D9"),
    (f"{mem_ratio:.1f}×",       "Memory efficiency",  "#A78BFA"),
]
for col, (val, label, color) in zip([k1, k2, k3, k4, k5], kpi_data):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  CHART TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_time, tab_scale, tab_mem, tab_box, tab_heat, tab_theory, tab_raw = st.tabs([
    "Execution Latency",
    "Scalability Metrics",
    "Memory Allocations",
    "Latency Distribution",
    "Comparative Heatmap",
    "Complexity Analysis",
    "Raw Measurement Data",
])

yaxis_type = "log" if log_scale else "linear"

# ── 1. Execution time with CI bands ──────────────────────────────────────────
with tab_time:
    st.markdown("#### Execution Time vs Network Size  *(with 95% Confidence Intervals)*")
    fig = go.Figure()
    for bname in agg["backend"].unique():
        sub = agg[agg["backend"] == bname].sort_values("n_nodes")
        c = BE_COLOR.get(bname, "#888")
        xs = sub["n_nodes"].tolist()
        ys = sub["avg_ms"].tolist()
        ci = sub["ci95_ms"].fillna(0).tolist()

        # CI band
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        fig.add_trace(go.Scatter(
            x=xs + xs[::-1],
            y=[y + e for y, e in zip(ys, ci)] + [y - e for y, e in zip(ys, ci)][::-1],
            fill="toself",
            fillcolor=f"rgba({r},{g},{b},0.10)",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ))
        # Main line
        fig.add_trace(go.Scatter(
            x=xs, y=ys, name=bname,
            mode="lines+markers",
            line=dict(color=c, width=2.5, dash=BE_DASH.get(bname, "solid")),
            marker=dict(size=8, color=c, line=dict(width=1.5, color="#0a0e1a")),
            error_y=dict(type="data", array=ci, color=c, thickness=1.5, width=5),
        ))

    fig.update_layout(
        **PLOT_LAYOUT,
        height=420,
        xaxis=dict(title="Network size  (number of nodes)", **GRID),
        yaxis=dict(title="Execution time  (ms)", type=yaxis_type, **GRID),
        title=dict(text="Routing convergence time — mean ± 95% CI", font=dict(size=13)),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="info-box" style="font-size:0.84rem;">
    <b>Interpretation:</b> DuckDB's <code>USING KEY</code> terminates the recursive CTE as soon
    as no row improves, yielding O(V·E) iterations in the best case. SQLite's append-only CTE
    must enumerate <em>all acyclic paths</em> before the final GROUP BY aggregation,
    producing super-linear growth with network density.
    </div>""", unsafe_allow_html=True)

# ── 2. Scalability ratio ──────────────────────────────────────────────────────
with tab_scale:
    st.markdown("#### Scalability Ratio  *(time at N / time at N_min)*")

    fig2 = go.Figure()
    n_min = agg["n_nodes"].min()

    for bname in agg["backend"].unique():
        sub = agg[agg["backend"] == bname].sort_values("n_nodes")
        base = sub[sub["n_nodes"] == n_min]["avg_ms"].values
        if not len(base) or base[0] < 1e-9:
            continue
        ratio = (sub["avg_ms"] / base[0]).tolist()
        c = BE_COLOR.get(bname, "#888")
        fig2.add_trace(go.Scatter(
            x=sub["n_nodes"].tolist(), y=ratio, name=bname,
            mode="lines+markers",
            line=dict(color=c, width=2.5, dash=BE_DASH.get(bname, "solid")),
            marker=dict(size=8, color=c, line=dict(width=1.5, color="#0a0e1a")),
        ))

    # Reference lines: linear, quadratic, cubic
    ns = sorted(agg["n_nodes"].unique())
    n0 = ns[0]
    for label, exp, color, dash in [
        ("O(N) — linear",    1, "rgba(255,255,255,0.2)", "longdashdot"),
        ("O(N²) — quadratic",2, "rgba(255,200,100,0.2)", "dash"),
        ("O(N³) — cubic",   3, "rgba(255,100,100,0.2)", "dot"),
    ]:
        fig2.add_trace(go.Scatter(
            x=ns, y=[(n/n0)**exp for n in ns], name=label,
            mode="lines", line=dict(color=color, width=1.5, dash=dash),
        ))

    fig2.update_layout(
        **PLOT_LAYOUT, height=420,
        xaxis=dict(title="Network size  (nodes)", **GRID),
        yaxis=dict(title=f"Relative time  (×  time at N={n_min})", type=yaxis_type, **GRID),
        title=dict(text="Scalability — growth relative to smallest network", font=dict(size=13)),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Speedup DuckDB vs SQLite
    st.markdown("#### DuckDB Speedup Advantage over SQLite")
    merged = agg[agg["backend"].isin(["DuckDB (USING KEY)", "SQLite (Standard CTE)"])].copy()
    pivot_sp = merged.pivot(index="n_nodes", columns="backend", values="avg_ms").reset_index()
    pivot_sp.columns.name = None
    if "DuckDB (USING KEY)" in pivot_sp.columns and "SQLite (Standard CTE)" in pivot_sp.columns:
        pivot_sp["speedup"] = pivot_sp["SQLite (Standard CTE)"] / pivot_sp["DuckDB (USING KEY)"].clip(lower=1e-6)
        fig_sp = go.Figure(go.Bar(
            x=pivot_sp["n_nodes"], y=pivot_sp["speedup"],
            marker=dict(
                color=pivot_sp["speedup"],
                colorscale=[[0,"#4A90D9"],[0.5,"#FFCC00"],[1,"#00D4AA"]],
                showscale=True,
                colorbar=dict(title=dict(text="×", font=dict(color="white")), tickfont=dict(color="white")),
            ),
            text=[f"{v:.1f}×" if not pd.isna(v) else "N/A" for v in pivot_sp["speedup"]],
            textposition="outside", textfont=dict(color="white", size=11),
        ))
        fig_sp.update_layout(
            **PLOT_LAYOUT, height=320,
            xaxis=dict(title="Network size (nodes)", **GRID),
            yaxis=dict(title="Speedup factor  (SQLite time / DuckDB time)", **GRID),
            title=dict(text="DuckDB USING KEY speedup over SQLite standard CTE", font=dict(size=13)),
        )
        st.plotly_chart(fig_sp, use_container_width=True)

# ── 3. Memory ─────────────────────────────────────────────────────────────────
with tab_mem:
    st.markdown("#### Peak Memory Consumption  (KB)")

    fig3 = go.Figure()
    for bname in agg["backend"].unique():
        sub = agg[agg["backend"] == bname].sort_values("n_nodes")
        c = BE_COLOR.get(bname, "#888")
        fig3.add_trace(go.Bar(
            x=sub["n_nodes"].astype(str), y=sub["avg_kb"],
            name=bname, marker_color=c, opacity=0.85,
        ))

    fig3.update_layout(
        **PLOT_LAYOUT, height=380, barmode="group",
        xaxis=dict(title="Network size (nodes)", **GRID),
        yaxis=dict(title="Peak memory  (KB)", type=yaxis_type, **GRID),
        title=dict(text="Peak heap allocation during routing query", font=dict(size=13)),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Memory vs time scatter
    st.markdown("#### Memory–Time Trade-off  *(per backend × network size)*")
    fig4 = px.scatter(
        agg, x="avg_ms", y="avg_kb",
        color="backend", size="n_nodes",
        color_discrete_map=BE_COLOR,
        hover_data=["n_nodes", "n_edges", "row_count"],
        labels={"avg_ms": "Avg time (ms)", "avg_kb": "Avg peak memory (KB)"},
        size_max=28,
    )
    fig4.update_layout(
        **PLOT_LAYOUT, height=380,
        xaxis=dict(**GRID, type=yaxis_type),
        yaxis=dict(**GRID, type=yaxis_type),
        title=dict(text="Time–Memory Pareto frontier (bubble size = network size)", font=dict(size=13)),
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
    <div class="info-box" style="font-size:0.84rem;">
    <b>Observation:</b> SQLite's append-only recursion accumulates <em>all intermediate paths</em> in
    memory before aggregation — causing super-linear memory growth. DuckDB's keyed CTE maintains
    only the current best route per (from, to) pair, holding memory close to O(V²).
    </div>""", unsafe_allow_html=True)

# ── 4. Box / distribution ─────────────────────────────────────────────────────
with tab_box:
    st.markdown("#### Run-to-Run Variance  *(raw measurements)*")

    fig5 = go.Figure()
    for bname in df_raw["backend"].unique():
        sub = df_raw[df_raw["backend"] == bname]
        c = BE_COLOR.get(bname, "#888")
        fig5.add_trace(go.Box(
            y=sub["elapsed_ms"], x=sub["n_nodes"].astype(str),
            name=bname, marker_color=c,
            line=dict(color=c, width=1.5),
            fillcolor=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.25)",
            boxmean="sd",
        ))

    fig5.update_layout(
        **PLOT_LAYOUT, height=420, boxmode="group",
        xaxis=dict(title="Network size (nodes)", **GRID),
        yaxis=dict(title="Execution time (ms)", type=yaxis_type, **GRID),
        title=dict(text="Distribution of execution times — boxplot with mean±SD", font=dict(size=13)),
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Coefficient of variation (stability)
    st.markdown("#### Coefficient of Variation  *(lower = more deterministic)*")
    agg2 = agg.copy()
    agg2["cv_pct"] = (agg2["std_ms"] / agg2["avg_ms"].clip(lower=1e-9) * 100).round(1)

    fig6 = go.Figure()
    for bname in agg2["backend"].unique():
        sub = agg2[agg2["backend"] == bname].sort_values("n_nodes")
        c = BE_COLOR.get(bname, "#888")
        fig6.add_trace(go.Scatter(
            x=sub["n_nodes"].tolist(), y=sub["cv_pct"].tolist(),
            name=bname, mode="lines+markers",
            line=dict(color=c, width=2, dash=BE_DASH.get(bname, "solid")),
            marker=dict(size=7, color=c),
        ))

    fig6.update_layout(
        **PLOT_LAYOUT, height=320,
        xaxis=dict(title="Network size (nodes)", **GRID),
        yaxis=dict(title="CV  (%)", **GRID),
        title=dict(text="Coefficient of Variation — execution time stability", font=dict(size=13)),
    )
    st.plotly_chart(fig6, use_container_width=True)

# ── 5. Heatmap ────────────────────────────────────────────────────────────────
with tab_heat:
    heat_metric = st.radio(
        "Metric", ["avg_ms", "avg_kb", "speedup_vs_sqlite"],
        format_func={"avg_ms": "Exec time (ms)", "avg_kb": "Memory (KB)",
                     "speedup_vs_sqlite": "Speedup vs SQLite"}.get,
        horizontal=True, label_visibility="collapsed"
    )
    pivot_h = agg.pivot(index="backend", columns="n_nodes", values=heat_metric)
    labels_h = [[f"{v:.3f}" if not pd.isna(v) else "N/A" for v in row] for row in pivot_h.values]

    colorscales = {
        "avg_ms":             [[0,"#0a1628"],[0.4,"#0066FF"],[0.8,"#FFCC00"],[1,"#E74C3C"]],
        "avg_kb":             [[0,"#0a1628"],[0.4,"#4A90D9"],[1,"#A78BFA"]],
        "speedup_vs_sqlite":  [[0,"#E74C3C"],[0.5,"#FFCC00"],[1,"#00D4AA"]],
    }

    fig7 = go.Figure(go.Heatmap(
        z=pivot_h.values,
        x=[f"N={n}" for n in pivot_h.columns],
        y=pivot_h.index.tolist(),
        text=labels_h, texttemplate="%{text}",
        colorscale=colorscales[heat_metric],
        showscale=True,
        colorbar=dict(tickfont=dict(color="white")),
    ))
    fig7.update_layout(
        **PLOT_LAYOUT, height=310,
        xaxis=dict(side="top"),
        title=dict(text=f"Heatmap — {heat_metric.replace('_', ' ')}", font=dict(size=13)),
    )
    st.plotly_chart(fig7, use_container_width=True)

# ── 6. Theoretical complexity overlay ────────────────────────────────────────
with tab_theory:
    st.markdown("#### Empirical vs Theoretical Complexity")
    st.markdown("""
    <div class="info-box" style="font-size:0.84rem; margin-bottom:1rem;">
    Each backend is fitted to its expected asymptotic growth class. The fitted curve uses
    least-squares regression in log-log space. Deviation from the reference line indicates
    constant-factor overhead (JIT warm-up, query planning, etc.).
    </div>""", unsafe_allow_html=True)

    fig8 = go.Figure()
    ref_classes = {
        "DuckDB (USING KEY)":    (1.5, "O(V·E)"),
        "SQLite (Standard CTE)": (2.2, "O(V·E·P)"),
        "Pure Python":           (3.0, "O(V²·E)"),
    }

    ns_all = sorted(agg["n_nodes"].unique())

    for bname in agg["backend"].unique():
        sub = agg[agg["backend"] == bname].sort_values("n_nodes")
        c   = BE_COLOR.get(bname, "#888")
        xs  = sub["n_nodes"].tolist()
        ys  = sub["avg_ms"].tolist()
        exp, label = ref_classes.get(bname, (2, "O(?)"))

        # Empirical points
        fig8.add_trace(go.Scatter(
            x=xs, y=ys, name=f"{bname} (measured)",
            mode="markers",
            marker=dict(size=10, color=c, symbol="circle",
                        line=dict(width=1.5, color="#0a0e1a")),
        ))

        # Fitted power-law curve
        log_xs = np.log(np.array(xs, dtype=float))
        log_ys = np.log(np.clip(np.array(ys, dtype=float), 1e-9, None))
        if len(log_xs) >= 2:
            coeffs = np.polyfit(log_xs, log_ys, 1)
            fit_exp = coeffs[0]
            fit_scale = math.exp(coeffs[1])
            xs_fine = np.linspace(min(xs), max(xs), 80)
            ys_fine = fit_scale * xs_fine ** fit_exp
            fig8.add_trace(go.Scatter(
                x=xs_fine.tolist(), y=ys_fine.tolist(),
                name=f"{bname} fit  (α={fit_exp:.2f})",
                mode="lines",
                line=dict(color=c, width=1.5, dash=BE_DASH.get(bname, "dash")),
            ))

    fig8.update_layout(
        **PLOT_LAYOUT, height=440,
        xaxis=dict(title="Network size (nodes)", type="log", **GRID),
        yaxis=dict(title="Execution time (ms)", type="log", **GRID),
        title=dict(
            text="Log–log plot: empirical points + fitted power-law  (slope ≈ complexity exponent)",
            font=dict(size=13)
        ),
    )
    st.plotly_chart(fig8, use_container_width=True)

    # Complexity table
    complexity_rows = []
    for bname in agg["backend"].unique():
        sub = agg[agg["backend"] == bname].sort_values("n_nodes")
        xs  = np.log(np.array(sub["n_nodes"].tolist(), dtype=float))
        ys  = np.log(np.clip(sub["avg_ms"].tolist(), 1e-9, None))
        if len(xs) >= 2:
            exp_fit = np.polyfit(xs, ys, 1)[0]
        else:
            exp_fit = float("nan")
        theo_exp, theo_class = ref_classes.get(bname, (0, "—"))
        complexity_rows.append({
            "Backend": bname,
            "Theoretical class": theo_class,
            "Fitted exponent α": f"{exp_fit:.3f}",
            "Avg time (ms)": f"{sub['avg_ms'].mean():.4f}",
            "Memory (KB)":   f"{sub['avg_kb'].mean():.1f}",
        })

    st.dataframe(pd.DataFrame(complexity_rows), hide_index=True, use_container_width=True)

    st.markdown("""
    <div class="warn-box" style="font-size:0.84rem; margin-top:0.8rem;">
    <b>Note:</b> Fitted exponents on small N are sensitive to constant factors.
    The log–log slope converges to the true asymptotic exponent as N → ∞.
    SQLite's exponent exceeds DuckDB's because path-set enumeration grows faster than
    the bounded iteration of the keyed CTE.
    </div>""", unsafe_allow_html=True)

# ── 7. Raw data ───────────────────────────────────────────────────────────────
with tab_raw:
    st.markdown("#### Aggregated Results")
    disp_agg = agg.copy()
    disp_agg.columns = [c.replace("_", " ").title() for c in disp_agg.columns]
    st.dataframe(
        disp_agg.style.format({
            "Avg Ms": "{:.5f}", "Min Ms": "{:.5f}", "Max Ms": "{:.5f}",
            "Std Ms": "{:.5f}", "Ci95 Ms": "{:.5f}",
            "Avg Kb": "{:.2f}", "Speedup Vs Sqlite": "{:.2f}",
        }, na_rep="—"),
        hide_index=True, use_container_width=True
    )

    st.markdown("#### All Individual Runs")
    st.dataframe(df_raw.sort_values(["backend","n_nodes","run"]).reset_index(drop=True),
                 hide_index=True, use_container_width=True)

    # Download
    csv = df_raw.to_csv(index=False)
    st.download_button(
        "Download CSV Dataset",
        data=csv, file_name="dvr_benchmark_results.csv", mime="text/csv",
    )
