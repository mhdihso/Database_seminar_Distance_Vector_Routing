import duckdb

con = duckdb.connect()

con.execute("""
    CREATE TABLE edges (
        from_node TEXT,
        to_node   TEXT,
        cost      INTEGER
    )
""")

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

con.executemany("INSERT INTO edges VALUES (?, ?, ?)", edges)

sql = """
WITH RECURSIVE routing_table(from_node, to_node, best_cost, next_hop)
    USING KEY (from_node, to_node) AS (

    SELECT from_node, to_node, cost AS best_cost, to_node AS next_hop
    FROM edges

    UNION

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

print(con.execute(sql).df())
