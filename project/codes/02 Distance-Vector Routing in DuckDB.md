# Implementing Distance-Vector Routing in DuckDB

Using DuckDB's `USING KEY` syntax, we can write a clean, efficient implementation of Distance-Vector Routing. 

Below is the complete SQL query and a step-by-step justification of how it mirrors the actual networking protocol.

## The Network Graph Setup

```sql
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
```

## The Routing Query

```sql
WITH RECURSIVE routing_table(from_node, to_node, best_cost, next_hop) 
    USING KEY (from_node, to_node) AS (
    
    -- 1. BASE CASE: Initial router state at T=0
    SELECT from_node, to_node, cost AS best_cost, to_node AS next_hop
    FROM edges

    UNION

    -- 2. RECURSIVE STEP: Bellman-Ford equation
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
      -- Critical check: Only propagate if it's strictly better!
      AND (existing.best_cost IS NULL OR (r.best_cost + e.cost) < existing.best_cost)
    GROUP BY r.from_node, e.to_node
)
SELECT * FROM routing_table ORDER BY from_node, to_node;
```

---

## 0 to 100: Explaining Every Line

### 1. The Key Definition
`USING KEY (from_node, to_node)`
* **Justification:** A router's routing table only holds one "best" entry for any given destination. We enforce this constraint directly in the CTE. `from_node` represents the router holding the table, and `to_node` is the destination.

### 2. The Base Case
```sql
SELECT from_node, to_node, cost AS best_cost, to_node AS next_hop FROM edges
```
* **Justification:** At $T=0$, routers only know about the neighbors they are directly plugged into. The cost is the cable's direct cost, and the `next_hop` to reach the neighbor is simply the neighbor itself.

### 3. The `UNION`
* **Justification:** We use standard `UNION` (instead of `UNION ALL`) which combines our base case with our recursive iterations.

### 4. Simulating Network Broadcasts
```sql
FROM routing_table AS r
JOIN edges AS e ON r.to_node = e.from_node
```
* **Justification:** In DuckDB, `routing_table` refers to the rows that were *added or updated in the immediately preceding iteration*. By joining it with `edges`, we simulate the router (`e.to_node`) receiving the updated vector information from its neighbor (`r.to_node`).

### 5. Checking the Current State
```sql
LEFT JOIN recurring.routing_table AS existing 
    ON existing.from_node = r.from_node AND existing.to_node = e.to_node
```
* **Justification:** `recurring.routing_table` represents the entire routing table constructed up to this point. We left join to peek at what our current best known cost is for this destination.

### 6. The Bellman-Ford Condition
```sql
WHERE r.from_node <> e.to_node
  AND (existing.best_cost IS NULL OR (r.best_cost + e.cost) < existing.best_cost)
```
* **Justification:** The core logic of the algorithm. We prevent routing to ourselves (`r.from_node <> e.to_node`). Then, we evaluate: Is this destination entirely new (`existing.best_cost IS NULL`), or is the proposed cost cheaper than our current cost (`< existing.best_cost`)? If neither is true, the query yields nothing, perfectly simulating a router ignoring suboptimal route advertisements.

### 7. Resolving Simultaneous Updates
```sql
SELECT MIN(r.best_cost + e.cost) AS best_cost,
       arg_min(r.next_hop, r.best_cost + e.cost) AS next_hop
...
GROUP BY r.from_node, e.to_node
```
* **Justification:** If a router receives multiple advertisements for the same destination in the exact same tick, it must pick the absolute best one. Standard `ORDER BY` is forbidden in recursive queries, so we use `GROUP BY` combined with the `arg_min()` aggregate function. `arg_min` picks the `next_hop` that corresponds to the minimum cost found.

### Summary
When no more rows satisfy the condition `(r.best_cost + e.cost) < existing.best_cost`, the recursive step produces 0 rows. The network has converged, and the query completes instantly. No manual cycle detection is needed, no post-query aggregation is needed!

---

## Convergence Results

### 1. Initial State (Full Network)
The routing table shows the globally optimal paths. For example, A reaches C via B for a total cost of 5.

| from_node | to_node | best_cost | next_hop |
|-----------|---------|-----------|----------|
| A | B | 3 | B |
| A | C | 5 | B |
| A | D | 10 | B |
| B | A | 3 | A |
| B | C | 2 | C |
| B | D | 7 | C |
| C | A | 5 | B |
| C | B | 2 | B |
| C | D | 5 | D |
| D | A | 10 | C |
| D | B | 7 | C |
| D | C | 5 | C |

### 2. Post-Failure State (B-C Link Removed)
After removing the link between B and C, the algorithm re-converges. Notice that A now takes the direct (but expensive) path to C (cost 23).

| from_node | to_node | best_cost | next_hop |
|-----------|---------|-----------|----------|
| A | B | 3 | B |
| A | C | 23 | C |
| A | D | 28 | C |
| B | A | 3 | A |
| B | C | 26 | A |
| B | D | 31 | A |
| C | A | 23 | A |
| C | B | 26 | A |
| C | D | 5 | D |
| D | A | 28 | C |
| D | B | 31 | C |
| D | C | 5 | C |

*See the full walkthrough in [[Distance_Vector_Routing_Report.tex]]*
