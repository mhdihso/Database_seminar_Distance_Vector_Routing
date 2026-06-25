-- DuckDB Distance-Vector Routing Implementation
-- Run this directly in the DuckDB CLI!

-- 1. Create the Graph
CREATE TABLE edges (
    from_node TEXT,
    to_node   TEXT,
    cost      INT
);

INSERT INTO edges VALUES
    ('A', 'B', 3), ('B', 'A', 3),
    ('A', 'C', 23),('C', 'A', 23),
    ('B', 'C', 2), ('C', 'B', 2),
    ('C', 'D', 5), ('D', 'C', 5);

-- 2. Execute Distance-Vector Routing
WITH RECURSIVE routing_table(from_node, to_node, best_cost, next_hop) 
    USING KEY (from_node, to_node) AS (
    
    -- BASE CASE: Direct neighbors
    SELECT from_node, to_node, cost AS best_cost, to_node AS next_hop
    FROM edges

    UNION

    -- RECURSIVE STEP: Relax edges (Bellman-Ford)
    SELECT
        r.from_node,
        e.to_node,
        MIN(r.best_cost + e.cost) AS best_cost,
        arg_min(r.next_hop, r.best_cost + e.cost) AS next_hop
    FROM routing_table AS r
    JOIN edges AS e ON r.to_node = e.from_node
    LEFT JOIN recurring.routing_table AS existing 
        ON existing.from_node = r.from_node AND existing.to_node = e.to_node
    WHERE r.from_node <> e.to_node
      AND (existing.best_cost IS NULL OR (r.best_cost + e.cost) < existing.best_cost)
    GROUP BY r.from_node, e.to_node
)
SELECT * 
FROM routing_table 
ORDER BY from_node, to_node;


DELETE FROM edges
WHERE ( from_node = 'B' AND to_node = 'C')
OR ( from_node = 'C' AND to_node = 'B') ;