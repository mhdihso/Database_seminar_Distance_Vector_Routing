"""
db_backends.py — Database backends for routing simulation.
Supports: DuckDB (USING KEY), SQLite (standard CTE), Pure Python.
"""
import time
import sqlite3
import duckdb
import pandas as pd
from typing import List, Tuple, Optional


def _simulate_routing_steps(edges_df: pd.DataFrame) -> List[pd.DataFrame]:
    """Simulate step-by-step convergence by running Bellman-Ford iteratively in Python."""
    if edges_df.empty:
        return []

    # Build initial routing table (base case)
    current = edges_df.rename(columns={"cost": "best_cost"}).copy()
    current["next_hop"] = current["to_node"]
    current = current[["from_node", "to_node", "best_cost", "next_hop"]]

    steps = [current.copy()]
    nodes = set(edges_df["from_node"]) | set(edges_df["to_node"])
    max_iter = len(nodes)

    for _ in range(max_iter):
        updated = False
        round_updates = {}

        for _, r in current.iterrows():
            neighbors = edges_df[edges_df["from_node"] == r["to_node"]]
            for _, e in neighbors.iterrows():
                if r["from_node"] == e["to_node"]:
                    continue
                new_cost = r["best_cost"] + e["cost"]
                
                # Check existing cost in current table
                existing_rows = current[
                    (current["from_node"] == r["from_node"]) &
                    (current["to_node"] == e["to_node"])
                ]
                existing_cost = existing_rows.iloc[0]["best_cost"] if not existing_rows.empty else float("inf")
                
                # Check if we already found a cheaper path in this round
                key = (r["from_node"], e["to_node"])
                best_round_cost = round_updates[key][0] if key in round_updates else float("inf")
                
                if new_cost < existing_cost and new_cost < best_round_cost:
                    round_updates[key] = (new_cost, r["next_hop"])
                    updated = True

        if not updated:
            break

        # Apply all updates accumulated in this round
        for (f, t), (cost, hop) in round_updates.items():
            mask = (current["from_node"] == f) & (current["to_node"] == t)
            if mask.any():
                current.loc[mask, "best_cost"] = cost
                current.loc[mask, "next_hop"] = hop
            else:
                new_row = pd.DataFrame([{"from_node": f, "to_node": t, "best_cost": cost, "next_hop": hop}])
                current = pd.concat([current, new_row], ignore_index=True)

        steps.append(current.copy())

    return steps



# ─────────────────────────────────────────────
#  DuckDB Backend  (primary — USING KEY magic)
# ─────────────────────────────────────────────
class DuckDBBackend:
    name = "DuckDB (USING KEY)"
    color = "#FFCC00"  # DuckDB yellow

    def __init__(self):
        self.con = duckdb.connect(":memory:")
        self._setup()

    def _setup(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                from_node TEXT,
                to_node   TEXT,
                cost      INTEGER
            )
        """)

    def reset(self):
        self.con.execute("DROP TABLE IF EXISTS edges")
        self._setup()

    def load_edges(self, edges: List[Tuple[str, str, int]]):
        self.con.execute("DELETE FROM edges")
        self.con.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)

    def get_edges(self) -> pd.DataFrame:
        return self.con.execute("SELECT * FROM edges ORDER BY from_node, to_node").df()

    def delete_edge(self, from_node: str, to_node: str):
        self.con.execute(
            "DELETE FROM edges WHERE (from_node=? AND to_node=?) OR (from_node=? AND to_node=?)",
            [from_node, to_node, to_node, from_node]
        )

    def delete_node(self, node: str):
        self.con.execute(
            "DELETE FROM edges WHERE from_node=? OR to_node=?",
            [node, node]
        )

    def run_routing(self) -> Tuple[pd.DataFrame, float, str]:
        sql = """
WITH RECURSIVE routing_table(from_node, to_node, best_cost, next_hop)
    USING KEY (from_node, to_node) AS (

    -- BASE CASE: Direct neighbors (T=0, each router knows its cables)
    SELECT from_node, to_node, cost AS best_cost, to_node AS next_hop
    FROM edges

    UNION

    -- RECURSIVE STEP: Bellman-Ford relaxation (each tick = one broadcast round)
    SELECT
        r.from_node,
        e.to_node,
        MIN(r.best_cost + e.cost)                    AS best_cost,
        arg_min(r.next_hop, r.best_cost + e.cost)    AS next_hop
    FROM routing_table AS r
    JOIN edges AS e ON r.to_node = e.from_node
    LEFT JOIN recurring.routing_table AS existing
        ON existing.from_node = r.from_node AND existing.to_node = e.to_node
    WHERE r.from_node <> e.to_node
      AND (existing.best_cost IS NULL OR (r.best_cost + e.cost) < existing.best_cost)
    GROUP BY r.from_node, e.to_node
)
SELECT * FROM routing_table ORDER BY from_node, to_node
"""
        t0 = time.perf_counter()
        df = self.con.execute(sql).df()
        elapsed = time.perf_counter() - t0
        return df, elapsed, sql.strip()

    def run_routing_steps(self) -> List[pd.DataFrame]:
        return _simulate_routing_steps(self.get_edges())


# ─────────────────────────────────────────────
#  SQLite Backend  (standard SQL, append-only CTE)
# ─────────────────────────────────────────────
class SQLiteBackend:
    name = "SQLite (Standard CTE)"
    color = "#4A90D9"

    def __init__(self):
        self.con = sqlite3.connect(":memory:")
        self._setup()

    def _setup(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                from_node TEXT,
                to_node   TEXT,
                cost      INTEGER
            )
        """)
        self.con.commit()

    def reset(self):
        self.con.execute("DROP TABLE IF EXISTS edges")
        self._setup()

    def load_edges(self, edges: List[Tuple[str, str, int]]):
        self.con.execute("DELETE FROM edges")
        self.con.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)
        self.con.commit()

    def get_edges(self) -> pd.DataFrame:
        return pd.read_sql("SELECT * FROM edges ORDER BY from_node, to_node", self.con)

    def delete_edge(self, from_node: str, to_node: str):
        self.con.execute(
            "DELETE FROM edges WHERE (from_node=? AND to_node=?) OR (from_node=? AND to_node=?)",
            [from_node, to_node, to_node, from_node]
        )
        self.con.commit()

    def delete_node(self, node: str):
        self.con.execute(
            "DELETE FROM edges WHERE from_node=? OR to_node=?",
            [node, node]
        )
        self.con.commit()

    def run_routing(self) -> Tuple[pd.DataFrame, float, str]:
        # Get count of nodes
        cursor = self.con.execute("SELECT COUNT(DISTINCT from_node) FROM edges")
        node_count = cursor.fetchone()[0] or 0
        if node_count >= 12:
            raise RuntimeError(
                f"SQLite standard CTE is capped at 11 nodes to prevent exponential path explosion "
                f"(your network has {node_count} nodes). Please use DuckDB or Pure Python backends for larger networks."
            )

        # Bounded Bellman-Ford via recursion depth (iter < |V|).
        # This avoids the exponential path enumeration of the visited-LIKE approach
        # while still being strictly append-only — showing the GROUP BY aggregation cost.
        sql = """
WITH RECURSIVE bellman(from_node, to_node, best_cost, next_hop, iter) AS (
    -- BASE CASE: direct neighbour links (T=0)
    SELECT from_node, to_node, cost, to_node, 0
    FROM edges

    UNION ALL

    -- RECURSIVE: relax one hop at a time, bounded to |V|-1 rounds
    SELECT b.from_node,
           e.to_node,
           b.best_cost + e.cost,
           b.next_hop,
           b.iter + 1
    FROM bellman b
    JOIN edges e ON b.to_node = e.from_node
    WHERE b.from_node <> e.to_node
      AND b.iter < (SELECT COUNT(DISTINCT from_node) FROM edges) - 1
)
-- Post-hoc aggregation: pick cheapest path per (from, to)
-- This GROUP BY is the key extra step DuckDB avoids with USING KEY
SELECT from_node,
       to_node,
       MIN(best_cost) AS best_cost,
       next_hop
FROM bellman
GROUP BY from_node, to_node
ORDER BY from_node, to_node
"""
        t0 = time.perf_counter()
        df = pd.read_sql(sql, self.con)
        elapsed = time.perf_counter() - t0
        df = df.sort_values(["from_node", "best_cost"]) \
               .drop_duplicates(subset=["from_node", "to_node"]) \
               .sort_values(["from_node", "to_node"]) \
               .reset_index(drop=True)
        return df, elapsed, sql.strip()

    def run_routing_steps(self) -> List[pd.DataFrame]:
        return _simulate_routing_steps(self.get_edges())



# ─────────────────────────────────────────────
#  Pure Python Backend  (in-memory dict)
# ─────────────────────────────────────────────
class PythonBackend:
    color = "#50C878"

    def __init__(self):
        self._edges: List[Tuple[str, str, int]] = []
        self.algo = "Bellman-Ford"

    @property
    def name(self) -> str:
        return f"Pure Python ({self.algo})"

    def reset(self):
        self._edges = []

    def load_edges(self, edges: List[Tuple[str, str, int]]):
        self._edges = list(edges)

    def get_edges(self) -> pd.DataFrame:
        return pd.DataFrame(self._edges, columns=["from_node", "to_node", "cost"])

    def delete_edge(self, from_node: str, to_node: str):
        self._edges = [
            e for e in self._edges
            if not ((e[0] == from_node and e[1] == to_node) or
                    (e[0] == to_node and e[1] == from_node))
        ]

    def delete_node(self, node: str):
        self._edges = [e for e in self._edges if e[0] != node and e[1] != node]

    def run_routing(self) -> Tuple[pd.DataFrame, float, str]:
        if self.algo == "Dijkstra":
            return self._run_dijkstra()
        elif self.algo == "Floyd-Warshall":
            return self._run_floyd_warshall()
        else:
            return self._run_bellman_ford()

    def _run_bellman_ford(self) -> Tuple[pd.DataFrame, float, str]:
        t0 = time.perf_counter()
        nodes = list({e[0] for e in self._edges} | {e[1] for e in self._edges})
        INF = float("inf")

        # dist[src][dst] = (cost, next_hop)
        dist = {n: {m: (INF, None) for m in nodes} for n in nodes}
        for n in nodes:
            dist[n][n] = (0, n)
        for (f, t, c) in self._edges:
            dist[f][t] = (c, t)

        # Bellman-Ford: N-1 rounds
        for _ in range(len(nodes) - 1):
            updated = False
            for src in nodes:
                for mid in nodes:
                    d_sm, hop_sm = dist[src][mid]
                    if d_sm == INF:
                        continue
                    for (f, t, c) in self._edges:
                        if f == mid:
                            new_cost = d_sm + c
                            if new_cost < dist[src][t][0]:
                                dist[src][t] = (new_cost, hop_sm)
                                updated = True
            if not updated:
                break

        rows = []
        for src in nodes:
            for dst in nodes:
                if src == dst:
                    continue
                cost, hop = dist[src][dst]
                if cost < INF:
                    rows.append({
                        "from_node": src, "to_node": dst,
                        "best_cost": int(cost), "next_hop": hop
                    })
        elapsed = time.perf_counter() - t0
        df = pd.DataFrame(rows).sort_values(["from_node", "to_node"]).reset_index(drop=True)
        code = (
            "# Pure Python Bellman-Ford (Distance-Vector)\n"
            "INF = float('inf')\n"
            "dist = {n: {m: INF for m in nodes} for n in nodes}\n"
            "for (f,t,c) in edges: dist[f][t] = c\n"
            "for _ in range(len(nodes)-1):\n"
            "    for s in nodes:\n"
            "        for (f,t,c) in edges:\n"
            "            if dist[s][f] + c < dist[s][t]:\n"
            "                dist[s][t] = dist[s][f] + c"
        )
        return df, elapsed, code

    def _run_dijkstra(self) -> Tuple[pd.DataFrame, float, str]:
        t0 = time.perf_counter()
        nodes = list({e[0] for e in self._edges} | {e[1] for e in self._edges})
        adj = {n: {} for n in nodes}
        for f, t, c in self._edges:
            adj[f][t] = c

        import heapq
        rows = []
        for src in nodes:
            dist = {n: float("inf") for n in nodes}
            dist[src] = 0
            prev = {n: None for n in nodes}
            pq = [(0, src)]
            
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                for v, weight in adj[u].items():
                    if dist[u] + weight < dist[v]:
                        dist[v] = dist[u] + weight
                        prev[v] = u
                        heapq.heappush(pq, (dist[v], v))
            
            for dst in nodes:
                if src == dst or dist[dst] == float("inf"):
                    continue
                curr = dst
                while prev[curr] is not None and prev[curr] != src:
                    curr = prev[curr]
                next_hop = curr
                rows.append({
                    "from_node": src, "to_node": dst,
                    "best_cost": int(dist[dst]), "next_hop": next_hop
                })
        elapsed = time.perf_counter() - t0
        df = pd.DataFrame(rows).sort_values(["from_node", "to_node"]).reset_index(drop=True)
        code = (
            "# Pure Python Dijkstra (Link-State)\n"
            "for src in nodes:\n"
            "    pq = [(0, src)]\n"
            "    dist = {n: inf for n in nodes}; dist[src] = 0\n"
            "    while pq:\n"
            "        d, u = heappop(pq)\n"
            "        for v, w in adj[u].items():\n"
            "            if dist[u] + w < dist[v]:\n"
            "                dist[v] = dist[u] + w\n"
            "                heappush(pq, (dist[v], v))"
        )
        return df, elapsed, code

    def _run_floyd_warshall(self) -> Tuple[pd.DataFrame, float, str]:
        t0 = time.perf_counter()
        nodes = list({e[0] for e in self._edges} | {e[1] for e in self._edges})
        INF = float("inf")
        dist = {n: {m: INF for m in nodes} for n in nodes}
        next_node = {n: {m: None for m in nodes} for n in nodes}
        
        for n in nodes:
            dist[n][n] = 0
        for f, t, c in self._edges:
            dist[f][t] = c
            next_node[f][t] = t
            
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]
                        
        rows = []
        for src in nodes:
            for dst in nodes:
                if src == dst or dist[src][dst] == INF:
                    continue
                rows.append({
                    "from_node": src, "to_node": dst,
                    "best_cost": int(dist[src][dst]), "next_hop": next_node[src][dst]
                })
        elapsed = time.perf_counter() - t0
        df = pd.DataFrame(rows).sort_values(["from_node", "to_node"]).reset_index(drop=True)
        code = (
            "# Pure Python Floyd-Warshall (All-Pairs Shortest Path)\n"
            "dist = {u: {v: inf for v in nodes} for u in nodes}\n"
            "for k in nodes:\n"
            "    for i in nodes:\n"
            "        for j in nodes:\n"
            "            if dist[i][k] + dist[k][j] < dist[i][j]:\n"
            "                dist[i][j] = dist[i][k] + dist[k][j]\n"
            "                next_node[i][j] = next_node[i][k]"
        )
        return df, elapsed, code

    def run_routing_steps(self) -> List[pd.DataFrame]:
        return _simulate_routing_steps(self.get_edges())


# ─────────────────────────────────────────────
#  Factory
# ─────────────────────────────────────────────
BACKENDS = {
    "DuckDB (USING KEY)": DuckDBBackend,
    "SQLite (Standard CTE)": SQLiteBackend,
    "Pure Python (Bellman-Ford)": PythonBackend,
}
