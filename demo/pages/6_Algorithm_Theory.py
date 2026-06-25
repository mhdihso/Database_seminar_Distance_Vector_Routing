"""
pages/6_Algorithm_Theory.py — Formal algorithm analysis, pseudocode, and complexity comparison
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.markdown("""
<div class="stage-badge">Appendix A</div>
<h2 style="margin:0 0 0.3rem 0; font-size:1.9rem; font-weight:800; color:white;">
    Algorithm Theory and Formal Analysis
</h2>
<p style="color:rgba(255,255,255,0.45); margin:0 0 1.5rem 0; font-size:0.92rem;">
    Formal specification of the shortest-path algorithms evaluated in this system,
    including pseudocode, asymptotic complexity bounds, and convergence guarantees.
</p>
""", unsafe_allow_html=True)

# ── Problem Formulation ──────────────────────────────────────────────────────
st.markdown("### 1. Problem Formulation")
st.markdown("""
<div class="card">
<div style="font-size:0.92rem; color:rgba(255,255,255,0.8); line-height:1.8;">

**Definition (All-Pairs Shortest Path Problem):**
Given a weighted directed graph $G = (V, E, w)$ where $w: E \\to \\mathbb{R}^+$,
compute for every ordered pair $(s, t) \\in V \\times V$ the minimum-cost path:

$$d^*(s, t) = \\min_{\\pi \\in \\mathcal{P}(s,t)} \\sum_{e \\in \\pi} w(e)$$

where $\\mathcal{P}(s,t)$ denotes the set of all simple paths from $s$ to $t$.

Additionally, compute the forwarding function $\\text{next}(s, t)$ that returns the
first hop on the optimal path from $s$ to $t$, enabling distributed packet forwarding.

</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
<div style="font-size:0.92rem; color:rgba(255,255,255,0.8); line-height:1.8;">

**Definition (Distance-Vector Routing Protocol):**
Each router $v \\in V$ maintains a distance vector $D_v[\\cdot]$ and periodically
broadcasts it to all neighbors $u \\in \\text{adj}(v)$. Upon receiving an update,
router $u$ applies the Bellman-Ford relaxation:

$$D_u[t] \\leftarrow \\min\\big(D_u[t],\\; w(u,v) + D_v[t]\\big) \\quad \\forall\\, t \\in V$$

The protocol converges in at most $|V| - 1$ rounds if no negative-weight cycles exist.

</div>
</div>
""", unsafe_allow_html=True)

# ── Algorithm Specifications ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 2. Algorithm Specifications")

tab_bf, tab_dj, tab_fw = st.tabs([
    "Bellman-Ford (Distance-Vector)",
    "Dijkstra (Link-State)",
    "Floyd-Warshall (All-Pairs DP)"
])

with tab_bf:
    col_pseudo, col_props = st.columns([1.2, 1])
    with col_pseudo:
        st.markdown("#### Pseudocode")
        st.markdown("""
<div class="sql-block" style="font-size:0.82rem; line-height:1.7;">
BELLMAN-FORD-APSP(G = (V, E, w))
────────────────────────────────────────
  Input:  Directed weighted graph G
  Output: Distance matrix D, next-hop matrix N

  1.  for each s in V do
  2.      for each t in V do
  3.          D[s][t] <- infinity
  4.          N[s][t] <- nil
  5.      D[s][s] <- 0
  6.      for each (s, t, c) in E do
  7.          D[s][t] <- c
  8.          N[s][t] <- t

  9.  for round = 1 to |V| - 1 do
  10.     changed <- false
  11.     for each s in V do
  12.         for each (u, v, c) in E do
  13.             if D[s][u] + c < D[s][v] then
  14.                 D[s][v] <- D[s][u] + c
  15.                 N[s][v] <- N[s][u]
  16.                 changed <- true
  17.     if not changed then break

  18. return (D, N)
</div>
        """, unsafe_allow_html=True)

    with col_props:
        st.markdown("#### Properties")
        st.markdown("""
| Property | Value |
|----------|-------|
| **Paradigm** | Dynamic programming / Relaxation |
| **Time complexity** | $O(|V|^2 \\cdot |E|)$ |
| **Space complexity** | $O(|V|^2)$ |
| **Negative weights** | Supported (detects neg. cycles) |
| **Distributed** | Yes (natural DVR mapping) |
| **Convergence** | At most $|V|-1$ rounds |
| **Optimality** | Exact (no negative cycles) |
""")

        st.markdown("#### Convergence Theorem")
        st.markdown("""
<div class="info-box" style="font-size:0.84rem;">
<b>Theorem (Bellman-Ford Convergence):</b> After $k$ iterations of the relaxation step,
$D[s][t]$ equals the minimum cost of any path from $s$ to $t$ using at most $k+1$ edges.
Since any shortest path in a graph with $|V|$ vertices has at most $|V|-1$ edges,
the algorithm terminates correctly after $|V|-1$ iterations.
</div>
""", unsafe_allow_html=True)

with tab_dj:
    col_pseudo, col_props = st.columns([1.2, 1])
    with col_pseudo:
        st.markdown("#### Pseudocode")
        st.markdown("""
<div class="sql-block" style="font-size:0.82rem; line-height:1.7;">
DIJKSTRA-APSP(G = (V, E, w))
────────────────────────────────────────
  Input:  Directed weighted graph G (non-negative weights)
  Output: Distance matrix D, next-hop matrix N

  1.  for each src in V do
  2.      D[src] <- { v: infinity for v in V }
  3.      D[src][src] <- 0
  4.      prev <- { v: nil for v in V }
  5.      Q <- MinPriorityQueue()
  6.      Q.insert(src, 0)

  7.      while Q is not empty do
  8.          u <- Q.extract_min()
  9.          for each (u, v, c) in adj(u) do
  10.             if D[src][u] + c < D[src][v] then
  11.                 D[src][v] <- D[src][u] + c
  12.                 prev[v] <- u
  13.                 Q.decrease_key(v, D[src][v])

  14.     for each t in V \\ {src} do
  15.         N[src][t] <- trace_first_hop(prev, src, t)

  16. return (D, N)
</div>
        """, unsafe_allow_html=True)

    with col_props:
        st.markdown("#### Properties")
        st.markdown("""
| Property | Value |
|----------|-------|
| **Paradigm** | Greedy / Priority queue |
| **Time complexity** | $O(|V| \\cdot (|V| + |E|) \\log |V|)$ |
| **Space complexity** | $O(|V|^2)$ |
| **Negative weights** | Not supported |
| **Distributed** | Requires full topology (link-state) |
| **Convergence** | Single pass per source |
| **Optimality** | Exact (non-negative weights) |
""")

        st.markdown("#### Correctness Invariant")
        st.markdown("""
<div class="info-box" style="font-size:0.84rem;">
<b>Invariant (Dijkstra):</b> At the start of each iteration of the while loop,
$D[v] = d^*(s, v)$ for every vertex $v$ that has been extracted from $Q$.
This is maintained because edge weights are non-negative: once a vertex is extracted
with cost $d$, no future path through unvisited vertices can yield a lower cost.
</div>
""", unsafe_allow_html=True)

with tab_fw:
    col_pseudo, col_props = st.columns([1.2, 1])
    with col_pseudo:
        st.markdown("#### Pseudocode")
        st.markdown("""
<div class="sql-block" style="font-size:0.82rem; line-height:1.7;">
FLOYD-WARSHALL(G = (V, E, w))
────────────────────────────────────────
  Input:  Directed weighted graph G
  Output: Distance matrix D, next-hop matrix N

  1.  D <- |V| x |V| matrix, all infinity
  2.  N <- |V| x |V| matrix, all nil
  3.  for each v in V do
  4.      D[v][v] <- 0
  5.  for each (u, v, c) in E do
  6.      D[u][v] <- c
  7.      N[u][v] <- v

  8.  for each k in V do           // intermediate vertex
  9.      for each i in V do       // source
  10.         for each j in V do   // destination
  11.             if D[i][k] + D[k][j] < D[i][j] then
  12.                 D[i][j] <- D[i][k] + D[k][j]
  13.                 N[i][j] <- N[i][k]

  14. return (D, N)
</div>
        """, unsafe_allow_html=True)

    with col_props:
        st.markdown("#### Properties")
        st.markdown("""
| Property | Value |
|----------|-------|
| **Paradigm** | Dynamic programming |
| **Time complexity** | $O(|V|^3)$ |
| **Space complexity** | $O(|V|^2)$ |
| **Negative weights** | Supported (detects neg. cycles) |
| **Distributed** | No (requires global view) |
| **Convergence** | Exactly $|V|$ outer iterations |
| **Optimality** | Exact (no negative cycles) |
""")

        st.markdown("#### Recurrence Relation")
        st.markdown("""
<div class="info-box" style="font-size:0.84rem;">
<b>Recurrence:</b> Let $d^{(k)}_{ij}$ denote the shortest path from $i$ to $j$
using only vertices $\\{1, \\ldots, k\\}$ as intermediaries. Then:

$$d^{(k)}_{ij} = \\min\\big(d^{(k-1)}_{ij},\\; d^{(k-1)}_{ik} + d^{(k-1)}_{kj}\\big)$$

The final answer is $d^{(|V|)}_{ij} = d^*(i, j)$.
</div>
""", unsafe_allow_html=True)

# ── Complexity Comparison ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 3. Asymptotic Complexity Comparison")

comp_data = pd.DataFrame({
    "Algorithm": ["Bellman-Ford", "Dijkstra (binary heap)", "Floyd-Warshall",
                  "DuckDB USING KEY CTE", "SQLite Standard CTE"],
    "Time (worst case)": [
        "O(V^2 * E)", "O(V * (V + E) log V)", "O(V^3)",
        "O(V * E)", "O(V * E * P)"
    ],
    "Space": ["O(V^2)", "O(V^2)", "O(V^2)", "O(V^2)", "O(V^2 * P)"],
    "Best for": [
        "Negative weights, DVR simulation",
        "Sparse graphs, single-source",
        "Dense graphs, all-pairs",
        "SQL-native, auto-pruning",
        "Portability, standard SQL"
    ],
    "Distributed": ["Yes", "No", "No", "N/A (DB engine)", "N/A (DB engine)"],
    "Negative Weights": ["Yes", "No", "Yes", "No", "No"],
})
st.dataframe(comp_data, hide_index=True, use_container_width=True)

st.markdown("""
<div class="info-box" style="font-size:0.84rem;">
<b>Note on P (path count):</b> In the SQLite standard CTE column, $P$ denotes the number of
distinct walks enumerated by the recursive CTE before the post-hoc <code>GROUP BY</code> aggregation.
For dense graphs, $P$ can grow exponentially with $|V|$, which explains SQLite's
disproportionate performance degradation on larger topologies.
DuckDB's <code>USING KEY</code> eliminates this factor by pruning suboptimal paths in-place during recursion.
</div>
""", unsafe_allow_html=True)

# ── Theoretical Growth Curves ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 4. Theoretical Growth Curves")

import numpy as np

n_vals = np.arange(4, 60, 1)

fig = go.Figure()

# Assume E ~ 0.45 * V * (V-1) for density 0.45
curves = [
    ("O(V * E) -- DuckDB USING KEY", lambda n: n * (0.45 * n * (n-1)), "#FFCC00", "solid"),
    ("O(V^2 * E) -- Bellman-Ford", lambda n: n**2 * (0.45 * n * (n-1)), "#50C878", "dot"),
    ("O(V^3) -- Floyd-Warshall", lambda n: n**3, "#A78BFA", "dashdot"),
    ("O(V * (V+E) log V) -- Dijkstra", lambda n: n * (n + 0.45*n*(n-1)) * np.log2(n), "#FF6B6B", "dash"),
    ("O(V * E * 2^V) -- SQLite naive", lambda n: n * (0.45*n*(n-1)) * 2**(n*0.3), "#4A90D9", "longdash"),
]

for label, fn, color, dash in curves:
    ys = [fn(n) for n in n_vals]
    # Normalize to make comparable
    y0 = ys[0] if ys[0] > 0 else 1
    ys_norm = [y / y0 for y in ys]
    fig.add_trace(go.Scatter(
        x=n_vals.tolist(), y=ys_norm,
        name=label, mode="lines",
        line=dict(color=color, width=2.5, dash=dash),
    ))

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,26,0.85)",
    font=dict(family="Inter, sans-serif", color="#c9d1d9", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    height=450,
    xaxis=dict(title="Network Size |V|", gridcolor="rgba(255,255,255,0.06)"),
    yaxis=dict(title="Relative Operations (normalized to N=4)", type="log",
               gridcolor="rgba(255,255,255,0.06)"),
    title=dict(text="Theoretical complexity growth (log scale, density = 0.45)", font=dict(size=13)),
    legend=dict(
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="rgba(255,255,255,0.08)",
        borderwidth=1,
        font=dict(size=10),
    ),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="warn-box" style="font-size:0.84rem;">
<b>Observation:</b> The exponential factor in SQLite's naive CTE approach makes it infeasible
for networks beyond approximately 12 nodes. DuckDB's keyed recursion maintains polynomial
growth, making it the only SQL-based approach viable for medium-to-large topologies.
</div>
""", unsafe_allow_html=True)

# ── SQL Approach Comparison ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 5. SQL Recursive CTE: Standard vs Keyed Semantics")

col_std, col_key = st.columns(2)

with col_std:
    st.markdown("#### Standard CTE (SQLite)")
    st.markdown("""
<div class="sql-block" style="font-size:0.78rem; line-height:1.6; border-left-color:#4A90D9;">
WITH RECURSIVE bellman(s, t, cost, hop, iter) AS (
  -- Base: direct edges
  SELECT from_node, to_node, cost, to_node, 0
  FROM edges

  UNION ALL

  -- Recursive: extend paths by one hop
  SELECT b.s, e.to_node,
         b.cost + e.cost,
         b.hop,
         b.iter + 1
  FROM bellman b
  JOIN edges e ON b.t = e.from_node
  WHERE b.s <> e.to_node
    AND b.iter < (SELECT COUNT(DISTINCT from_node)
                  FROM edges) - 1
)
-- POST-HOC aggregation required
SELECT s, t, MIN(cost) AS best_cost, hop
FROM bellman
GROUP BY s, t
ORDER BY s, t
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class="deleted-box" style="font-size:0.82rem;">
The <code>UNION ALL</code> accumulates every walk of every length.
The final <code>GROUP BY ... MIN(cost)</code> discards suboptimal rows.
Result set grows as O(|V| * |E| * iterations).
</div>
""", unsafe_allow_html=True)

with col_key:
    st.markdown("#### Keyed CTE (DuckDB)")
    st.markdown("""
<div class="sql-block" style="font-size:0.78rem; line-height:1.6; border-left-color:#FFCC00;">
WITH RECURSIVE routing_table(s, t, cost, hop)
    USING KEY (s, t) AS (

  -- Base: direct edges
  SELECT from_node, to_node, cost, to_node
  FROM edges

  UNION

  -- Recursive: Bellman-Ford relaxation
  SELECT r.s, e.to_node,
         MIN(r.cost + e.cost),
         arg_min(r.hop, r.cost + e.cost)
  FROM routing_table r
  JOIN edges e ON r.t = e.from_node
  LEFT JOIN recurring.routing_table ex
    ON ex.s = r.s AND ex.t = e.to_node
  WHERE r.s <> e.to_node
    AND (ex.cost IS NULL
         OR r.cost + e.cost < ex.cost)
  GROUP BY r.s, e.to_node
)
-- No post-hoc aggregation needed
SELECT * FROM routing_table
ORDER BY s, t
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class="info-box" style="font-size:0.82rem;">
The <code>USING KEY</code> clause designates <code>(s, t)</code> as a unique key.
During recursion, only improving rows are retained. The working set stays O(|V|^2).
Termination is automatic when no improvement is found.
</div>
""", unsafe_allow_html=True)

# ── Key Differences Table ────────────────────────────────────────────────────
st.markdown("#### Semantic Comparison")
diff_data = pd.DataFrame({
    "Aspect": [
        "Recursion model",
        "Working set size",
        "Row pruning",
        "Aggregation",
        "Termination",
        "Memory scaling",
        "Walk explosion risk",
    ],
    "Standard CTE (SQLite)": [
        "Append-only (UNION ALL)",
        "Grows each iteration",
        "None during recursion",
        "Post-hoc GROUP BY required",
        "Explicit iteration bound",
        "O(V^2 * P) where P = walks",
        "High (exponential on dense graphs)",
    ],
    "Keyed CTE (DuckDB)": [
        "In-place update (UNION + KEY)",
        "Bounded at O(V^2)",
        "Automatic per-key minimum",
        "Built into recursion step",
        "Automatic (empty delta)",
        "O(V^2)",
        "None (pruned by design)",
    ],
})
st.dataframe(diff_data, hide_index=True, use_container_width=True)

# ── References ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### References")
st.markdown("""
<div class="card" style="font-size:0.85rem; line-height:1.8; color:rgba(255,255,255,0.7);">

1. R. Bellman, "On a Routing Problem," *Quarterly of Applied Mathematics*, vol. 16, no. 1, pp. 87-90, 1958.

2. E. W. Dijkstra, "A Note on Two Problems in Connexion with Graphs," *Numerische Mathematik*, vol. 1, pp. 269-271, 1959.

3. R. W. Floyd, "Algorithm 97: Shortest Path," *Communications of the ACM*, vol. 5, no. 6, p. 345, 1962.

4. L. R. Ford and D. R. Fulkerson, *Flows in Networks*, Princeton University Press, 1962.

5. DuckDB Documentation, "Recursive Common Table Expressions with USING KEY," https://duckdb.org/docs/sql/query_syntax/with.html

6. C. E. Perkins and P. Bhagwat, "Highly Dynamic Destination-Sequenced Distance-Vector Routing (DSDV)," *ACM SIGCOMM*, 1994.

</div>
""", unsafe_allow_html=True)
