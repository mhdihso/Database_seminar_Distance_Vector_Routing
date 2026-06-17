import duckdb
import pandas as pd

edges = [
    ("A", "B", 3),
    ("A", "C", 6),
    ("A", "D", 10),
    ("B", "A", 3),
    ("B", "C", 2),
    ("B", "D", 7),
    ("C", "A", 5),
    ("C", "B", 2),
    ("C", "D", 5),
    ("D", "A", 10),
    ("D", "B", 7),
    ("D", "C", 5)
]

edges_directed = []
for f, t, c in edges:
    edges_directed.append((f, t, c))
    if (t, f, c) not in edges_directed:
        edges_directed.append((t, f, c))

con = duckdb.connect()
con.execute("CREATE TABLE edges (from_node TEXT, to_node TEXT, cost INTEGER)")
con.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges_directed)

sql = """
WITH RECURSIVE routing_table AS (
    SELECT from_node, to_node, cost AS best_cost, to_node AS next_hop
    FROM edges

    UNION ALL BY NAME

    SELECT
        r.from_node,
        e.to_node,
        MIN(r.best_cost + e.cost)                    AS best_cost,
        arg_min(r.next_hop, r.best_cost + e.cost)    AS next_hop
    FROM recurring.routing_table r
    JOIN edges e ON r.to_node = e.from_node
    LEFT JOIN recurring.routing_table AS existing
        ON existing.from_node = r.from_node AND existing.to_node = e.to_node
    WHERE r.from_node <> e.to_node
      AND (existing.best_cost IS NULL OR (r.best_cost + e.cost) < existing.best_cost)
    GROUP BY r.from_node, e.to_node
)
SELECT * FROM routing_table ORDER BY from_node, to_node;
"""
df = con.execute(sql).df()
print("DuckDB routing table:")
print(df[df["from_node"] == "A"])
