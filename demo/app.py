"""
app.py — Main Streamlit entry point for the DVR Network Routing Simulator.
"""
import streamlit as st

st.set_page_config(
    page_title="DVR Network Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1729 50%, #0a1628 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1424 0%, #111828 100%);
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #00D4AA;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.2s;
}
.card:hover { border-color: rgba(0,212,170,0.3); }

/* ── Stage badge ── */
.stage-badge {
    display: inline-block;
    background: linear-gradient(135deg, #00D4AA, #0066FF);
    color: white;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, rgba(0,212,170,0.1), rgba(0,102,255,0.1));
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #00D4AA;
    font-family: 'JetBrains Mono', monospace;
}
.metric-label {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.2rem;
}

/* ── SQL block ── */
.sql-block {
    background: #0d1117;
    border: 1px solid rgba(0,212,170,0.25);
    border-left: 4px solid #00D4AA;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.6;
    color: #c9d1d9;
    overflow-x: auto;
    white-space: pre;
}

/* ── Tables ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00D4AA, #0066FF);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.55rem 1.5rem;
    transition: all 0.2s;
    box-shadow: 0 4px 15px rgba(0,212,170,0.2);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,212,170,0.35);
}

/* ── Tab styling ── */
[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.06);
    gap: 4px;
}
[data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 500 !important;
}
[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,212,170,0.2), rgba(0,102,255,0.2)) !important;
    color: #00D4AA !important;
}

/* ── Progress / info boxes ── */
.info-box {
    background: rgba(0,212,170,0.08);
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: rgba(255,255,255,0.85);
    font-size: 0.9rem;
    margin: 0.5rem 0;
}
.warn-box {
    background: rgba(255,204,0,0.08);
    border: 1px solid rgba(255,204,0,0.3);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: rgba(255,255,255,0.85);
    font-size: 0.9rem;
    margin: 0.5rem 0;
}
.deleted-box {
    background: rgba(231,76,60,0.08);
    border: 1px solid rgba(231,76,60,0.3);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: rgba(255,255,255,0.85);
    font-size: 0.9rem;
    margin: 0.5rem 0;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────
defaults = {
    "network_loaded":    False,
    "routing_done":      False,
    "deleted_nodes":     set(),
    "deleted_edges":     set(),
    "routing_df":        None,
    "routing_df_before": None,
    "routing_df_after":  None,
    "edges_list":        [],
    "backend_name":      "DuckDB (USING KEY)",
    "preset_name":       "Seminar (4 nodes)",
    "active_path":       [],
    "path_source":       None,
    "path_target":       None,
    "benchmark_results": None,
    "elapsed_ms":        None,
    "elapsed_ms_after":  None,
    "last_sql":          "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size:1.1rem; font-weight:700; color:#00D4AA; letter-spacing:0.05em;">DVR Evaluation Suite</div>
        <div style="font-size:0.72rem; color:rgba(255,255,255,0.4); margin-top:0.2rem;">
            DuckDB Keyed Recursion Analysis
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Global Settings")

    from core.db_backends import BACKENDS
    backend_choice = st.selectbox(
        "Backend Engine",
        list(BACKENDS.keys()),
        index=0,
        key="sidebar_backend",
        help="Select the database backend for execution. DuckDB utilizes USING KEY for in-place routing updates."
    )
    st.session_state["backend_name"] = backend_choice

    st.divider()
    st.markdown("### Navigation")
    st.markdown("""
    Select a phase from the sidebar to continue:

    | Phase | Focus Area |
    |-------|------------|
    | Phase 1 | Topology Initialization |
    | Phase 2 | Convergence Simulation |
    | Phase 3 | Fault Injection |
    | Phase 4 | Re-Convergence Analysis |
    | Phase 5 | Empirical Evaluation |
    | Appendix A | Algorithm Theory |
    """)

    st.divider()

    # Status indicators
    st.markdown("### Status")
    net_status = "Active" if st.session_state["network_loaded"] else "Inactive"
    rt_status  = "Complete" if st.session_state["routing_done"]   else "Pending"
    del_count  = len(st.session_state["deleted_nodes"]) + len(st.session_state["deleted_edges"])

    st.markdown(f"""
    <div class="card" style="padding:0.8rem 1rem; font-size:0.85rem;">
        <div style="color:rgba(255,255,255,0.5); font-size:0.7rem; margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:0.05em;">Session State</div>
        <div>Topology: <b style="color:#00D4AA">{net_status}</b></div>
        <div>Routing: <b style="color:#00D4AA">{rt_status}</b></div>
        <div>Disruptions: <b style="color:#FFCC00">{del_count}</b></div>
        <div>Backend: <b style="color:#4A90D9">{backend_choice.split('(')[0].strip()}</b></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Reset Session", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v if not isinstance(v, set) else set()
        st.rerun()

# ── Landing page ──────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 3rem 0 2rem 0;">
    <h1 style="font-size:2.8rem; font-weight:800; background:linear-gradient(135deg,#00D4AA,#4A90D9,#FFCC00);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        Distance-Vector Routing Protocol Simulator
    </h1>
    <p style="color:rgba(255,255,255,0.55); font-size:1.05rem; margin-top:0.8rem; max-width:680px; margin-left:auto; margin-right:auto;">
        A comparative evaluation platform for distributed routing convergence. Simulating Distance-Vector convergence utilizing DuckDB's native key-pruning recursive CTEs, SQLite standard recursive query execution, and algorithmic Python reference implementations.
    </p>
</div>
""", unsafe_allow_html=True)

# Feature cards
c1, c2, c3, c4, c5 = st.columns(5)
features = [
    ("Phase 1", "Topology Design", "Initialize network topologies using standard benchmarks or custom edge specifications.", "#00D4AA"),
    ("Phase 2", "Convergence Analysis", "Evaluate distributed Bellman-Ford execution step-by-step through SQL query logs.", "#4A90D9"),
    ("Phase 3", "Fault Injection", "Induce link failures and node crashes to evaluate protocol resilience.", "#FFCC00"),
    ("Phase 4", "Dynamic Re-convergence", "Analyze forwarding information base modifications post-topology disruption.", "#FF6B6B"),
    ("Phase 5", "Empirical Performance", "Compare execution latencies, memory footprints, and scalability under varying graph sizes.", "#A78BFA"),
]
for col, (phase_id, title, desc, color) in zip([c1,c2,c3,c4,c5], features):
    with col:
        st.markdown(f"""
        <div class="card" style="text-align:center; min-height:160px;">
            <div style="font-size:1.1rem; font-weight:700; color:{color}; margin-bottom:0.5rem;">{phase_id}</div>
            <div style="font-weight:600; color:white; font-size:0.95rem;">{title}</div>
            <div style="color:rgba(255,255,255,0.45); font-size:0.78rem; margin-top:0.4rem; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="info-box" style="margin-top:1.5rem; text-align:center;">
    Instructions: Navigate to <b>Phase 1: Network Setup</b> via the sidebar to initialize a topology.
</div>
""", unsafe_allow_html=True)

# ── Key Contributions ────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Key Contributions")

kc1, kc2, kc3 = st.columns(3)

contributions = [
    ("SQL as a Routing Engine", 
     "Demonstrates that SQL recursive CTEs can fully implement distributed routing protocols, "
     "replacing imperative algorithmic code with declarative query specifications.",
     "#00D4AA"),
    ("Keyed vs Standard CTE Analysis",
     "Provides empirical evidence that DuckDB's USING KEY extension eliminates the exponential "
     "path enumeration inherent in standard recursive CTEs, achieving polynomial scaling.",
     "#FFCC00"),
    ("Multi-Algorithm Comparison",
     "Benchmarks three algorithmic paradigms (Bellman-Ford, Dijkstra, Floyd-Warshall) across "
     "three execution engines (DuckDB, SQLite, Pure Python) with statistical rigor.",
     "#4A90D9"),
]

for col, (title, desc, color) in zip([kc1, kc2, kc3], contributions):
    with col:
        st.markdown(f"""
        <div class="card" style="min-height:180px;">
            <div style="font-weight:700; color:{color}; font-size:0.95rem; margin-bottom:0.6rem;
                        border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:0.5rem;">{title}</div>
            <div style="color:rgba(255,255,255,0.55); font-size:0.82rem; line-height:1.7;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── DuckDB Explanation ────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### DuckDB Recursive Key Pruning")
st.markdown("""
<div style="padding:1.5rem; background:rgba(255,204,0,0.06); border:1px solid rgba(255,204,0,0.15);
            border-radius:12px; border-left:4px solid #FFCC00;">
    <b style="color:#FFCC00;">Core Innovation: WITH RECURSIVE ... USING KEY</b><br>
    <span style="color:rgba(255,255,255,0.7); font-size:0.9rem;">
    Standard SQL implementations (e.g. SQLite, PostgreSQL) execute recursive common table expressions (CTEs) in an append-only manner. Because intermediate results cannot be mutated or pruned in-place, the database must generate all valid walks before selecting the shortest path with a final post-hoc grouping step. This leads to exponential row-set growth in dense topologies.<br><br>
    Conversely, DuckDB's proprietary <code>WITH RECURSIVE ... USING KEY</code> syntax enables stateful key-based updates during recursion. By maintaining only the optimal cost for each node pair at each step, DuckDB closely models physical routers exchanging distance-vector tables, preventing walk explosion and terminating convergence automatically.
    </span>
</div>
""", unsafe_allow_html=True)

# ── System Architecture ───────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### System Architecture")
st.markdown("""
<div class="card" style="font-size:0.85rem; line-height:1.8; color:rgba(255,255,255,0.65);">

| Layer | Component | Technology |
|-------|-----------|------------|
| **Presentation** | Interactive UI, graph visualization, charts | Streamlit, Pyvis, Plotly |
| **Application** | Routing simulation, convergence analysis, benchmarking | Python 3.x |
| **Database** | SQL recursive CTE execution, edge storage | DuckDB (in-memory), SQLite |
| **Algorithm** | Bellman-Ford, Dijkstra, Floyd-Warshall | Pure Python reference |

</div>
""", unsafe_allow_html=True)
