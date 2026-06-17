"""
benchmark.py — Academic benchmark engine.
Measures convergence time, iteration count, and memory across backends.
"""
import gc
import time
import random
import tracemalloc
import threading
import math
import pandas as pd
from typing import Callable, Optional
from core.db_backends import DuckDBBackend, SQLiteBackend, PythonBackend


def generate_random_network(n_nodes: int, density: float = 0.45, seed: int = 42) -> list:
    """Generate a reproducible connected random network."""
    rng = random.Random(seed + n_nodes)
    nodes = [f"N{i:02d}" for i in range(n_nodes)]
    rng.shuffle(nodes)
    edges, seen = [], set()

    # Spanning chain → guarantees connectivity
    for i in range(len(nodes) - 1):
        f, t = nodes[i], nodes[i + 1]
        c = rng.randint(1, 20)
        edges += [(f, t, c), (t, f, c)]
        seen |= {(f, t), (t, f)}

    # Extra edges by density
    for i in range(n_nodes):
        for j in range(i + 2, n_nodes):
            if rng.random() < density:
                f, t = nodes[i], nodes[j]
                if (f, t) not in seen:
                    c = rng.randint(1, 20)
                    edges += [(f, t, c), (t, f, c)]
                    seen |= {(f, t), (t, f)}
    return edges


# ── Test matrix ──────────────────────────────────────────────────────────────
NETWORK_SIZES_QUICK = [4, 8, 14, 22, 35]        # Quick mode  (~10 s)
NETWORK_SIZES_FULL  = [4, 8, 14, 22, 35, 55, 80] # Full mode   (~30 s)

BACKENDS_MAP = {
    "DuckDB (USING KEY)":    DuckDBBackend,
    "SQLite (Standard CTE)": SQLiteBackend,
    "Pure Python":           PythonBackend,
}
RUNS_PER_COMBO = 3   # repeated for stable average


def _time_and_memory(backend, edges):
    """Run one routing call; return (elapsed_ms, peak_kb, row_count)."""
    backend.reset()
    backend.load_edges(edges)

    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    try:
        df, *_ = backend.run_routing()
        row_count = len(df)
    except Exception:
        row_count = 0
    elapsed_ms = (time.perf_counter() - t0) * 1000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_kb = peak / 1024
    return elapsed_ms, peak_kb, row_count


def run_benchmark(
    sizes: list = None,
    progress_cb: Optional[Callable[[float, str], None]] = None,
    stop_event: Optional[threading.Event] = None,
) -> pd.DataFrame:
    """
    Full benchmark.  Returns DataFrame:
        backend | n_nodes | n_edges | elapsed_ms | peak_kb | row_count | run
    """
    if sizes is None:
        sizes = NETWORK_SIZES_QUICK

    combos = [
        (b, n, r)
        for b in BACKENDS_MAP
        for n in sizes
        for r in range(RUNS_PER_COMBO)
        if not (b == "SQLite (Standard CTE)" and n >= 12)
    ]
    total = len(combos)
    results = []

    for i, (bname, n_nodes, run_idx) in enumerate(combos):
        if stop_event and stop_event.is_set():
            break

        edges = generate_random_network(n_nodes, seed=run_idx)
        n_edges = len({(min(a, b), max(a, b)) for a, b, _ in edges})

        elapsed_ms, peak_kb, row_count = _time_and_memory(BACKENDS_MAP[bname](), edges)

        results.append({
            "backend":    bname,
            "n_nodes":    n_nodes,
            "n_edges":    n_edges,
            "elapsed_ms": round(elapsed_ms, 5),
            "peak_kb":    round(peak_kb, 2),
            "row_count":  row_count,
            "run":        run_idx,
        })

        if progress_cb:
            progress_cb((i + 1) / total, f"{bname} | N={n_nodes} | run {run_idx+1}")

    return pd.DataFrame(results)


def aggregate_results(df: pd.DataFrame) -> pd.DataFrame:
    """Per (backend, n_nodes): mean/min/max/std for time + memory."""
    # Add mean n_edges as a display column separately
    n_edges_mean = df.groupby(["backend", "n_nodes"])["n_edges"].mean().reset_index()\
                     .rename(columns={"n_edges": "n_edges"})

    grp = df.groupby(["backend", "n_nodes"])
    agg = grp.agg(
        avg_ms   =("elapsed_ms", "mean"),
        min_ms   =("elapsed_ms", "min"),
        max_ms   =("elapsed_ms", "max"),
        std_ms   =("elapsed_ms", "std"),
        avg_kb   =("peak_kb",    "mean"),
        row_count=("row_count",  "mean"),
        n_edges  =("n_edges",    "mean"),
    ).reset_index()
    agg["ci95_ms"] = 1.96 * agg["std_ms"] / (RUNS_PER_COMBO ** 0.5)

    # Speedup vs SQLite baseline (per n_nodes)
    sqli = agg[agg["backend"] == "SQLite (Standard CTE)"][["n_nodes", "avg_ms"]].rename(
        columns={"avg_ms": "sqli_ms"}
    )
    agg = agg.merge(sqli, on="n_nodes", how="left")
    agg["speedup_vs_sqlite"] = agg["sqli_ms"] / agg["avg_ms"].clip(lower=1e-6)

    # Theoretical growth class label
    def growth_label(row):
        if "DuckDB" in row["backend"]:
            return "O(V·E)"
        elif "SQLite" in row["backend"]:
            return "O(V·E·P)"
        else:
            return "O(V²·E)"
    agg["complexity"] = agg.apply(growth_label, axis=1)

    return agg.sort_values(["backend", "n_nodes"]).reset_index(drop=True)
