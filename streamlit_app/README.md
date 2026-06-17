# 🌐 DVR Network Routing Simulator

A beautiful interactive Streamlit app that simulates **Distance-Vector Routing (DVR)** using
**DuckDB's `USING KEY` recursive CTEs** — the star feature of this seminar.

## Features

| Stage | Description |
|-------|-------------|
| 1️⃣ Network Setup | Install preset or custom topologies into DuckDB/SQLite/Python |
| 2️⃣ Routing Simulation | Watch Bellman-Ford converge step-by-step with live graph |
| 3️⃣ Delete Nodes/Links | Simulate router crashes and cable cuts with real SQL DELETEs |
| 4️⃣ Re-convergence | See how the algorithm finds new paths after failure |
| 📊 Benchmark | Compare all backends across network sizes with Plotly charts |

## Quick Start

```bash
cd streamlit_app
source venv/bin/activate      # activate virtual environment
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Architecture

```
streamlit_app/
├── app.py                      # Main entry + global CSS + landing page
├── core/
│   ├── db_backends.py          # DuckDB (USING KEY), SQLite, Pure Python
│   ├── network_gen.py          # Topology presets + custom edge parser
│   └── benchmark.py           # Background timing benchmark
├── components/
│   └── graph_vis.py           # Pyvis interactive graph renderer
└── pages/
    ├── 1_Stage_1_Network_Setup.py
    ├── 2_Stage_2_Routing_Simulation.py
    ├── 3_Stage_3_Delete_Nodes.py
    ├── 4_Stage_4_Reconvergence.py
    └── 5_Benchmark_Compare.py
```

## Why DuckDB?

Standard SQL recursive CTEs are **append-only** — they can't update rows mid-recursion.
For DVR this means they must enumerate all possible paths and then `GROUP BY MIN(cost)` at the end.

DuckDB's `USING KEY` syntax enables **in-place row updates**, so:
- Each SQL iteration = one broadcast round between routers
- No redundant path storage
- Converges and stops automatically when nothing changes
- It's a 1:1 model of how real routers work!

## Backends Compared

| Backend | SQL Feature | Notes |
|---------|-------------|-------|
| **DuckDB** | `WITH RECURSIVE ... USING KEY` | In-place update, true DVR model |
| **SQLite** | `WITH RECURSIVE` (append-only) | Must post-aggregate with `GROUP BY MIN` |
| **Pure Python** | Bellman-Ford dict | No SQL — baseline for comparison |
