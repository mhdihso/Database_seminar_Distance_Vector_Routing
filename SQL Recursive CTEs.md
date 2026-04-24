# SQL Recursive CTEs

A CTE (Common Table Expression) is a temporary table you define inside a query.
A Recursive CTE is one that refers to itself — it keeps running until there is nothing new to add.

---

## The Basic Structure

```sql
WITH RECURSIVE cte_name AS (

    -- Part 1: Base case (the starting point)
    SELECT ...

    UNION ALL

    -- Part 2: Recursive step (refers to cte_name itself)
    SELECT ...
    FROM cte_name
    WHERE ...  -- stopping condition

)
SELECT * FROM cte_name;
```

Two parts, always:
- **Base case** — runs once, gives the starting rows
- **Recursive step** — uses the previous result to produce new rows
- Stops when the recursive step produces zero new rows

---

## Example 1 — Count from 1 to 5

The simplest possible recursive CTE.

```sql
WITH RECURSIVE counter AS (

    -- Base case: start at 1
    SELECT 1 AS n

    UNION ALL

    -- Recursive step: add 1 each time
    SELECT n + 1
    FROM counter
    WHERE n < 5  -- stop when we reach 5

)
SELECT * FROM counter;
```

Output:

| n |
|---|
| 1 |
| 2 |
| 3 |
| 4 |
| 5 |

What happened step by step:

| Iteration | Produces |
|-----------|----------|
| Base case | 1 |
| Step 1 | 2 |
| Step 2 | 3 |
| Step 3 | 4 |
| Step 4 | 5 |
| Step 5 | nothing (5 < 5 is false) — stops |

---

## Example 2 — Walk Through a Simple Path

Network: A → B → C → D

```sql
CREATE TABLE path (
    from_node TEXT,
    to_node   TEXT
);

INSERT INTO path VALUES
    ('A', 'B'),
    ('B', 'C'),
    ('C', 'D');
```

Now find all nodes reachable from A:

```sql
WITH RECURSIVE reachable AS (

    -- Base case: start at A
    SELECT to_node
    FROM path
    WHERE from_node = 'A'

    UNION ALL

    -- Recursive step: where can we go from the current node?
    SELECT p.to_node
    FROM path p
    JOIN reachable r ON p.from_node = r.to_node

)
SELECT * FROM reachable;
```

Output:

| to_node |
|---------|
| B |
| C |
| D |

What happened:

| Iteration | Current node | Finds |
|-----------|-------------|-------|
| Base case | A | B |
| Step 1 | B | C |
| Step 2 | C | D |
| Step 3 | D | nothing — stops |

---

## Example 3 — Walk Through a Graph and Track the Cost

Now we add costs on each link.

```sql
CREATE TABLE edges (
    from_node TEXT,
    to_node   TEXT,
    cost      INT
);

INSERT INTO edges VALUES
    ('A', 'B', 3),
    ('B', 'C', 2),
    ('C', 'D', 5);
```

Find the total cost to reach each node from A:

```sql
WITH RECURSIVE travel AS (

    -- Base case: direct neighbors of A
    SELECT from_node,
           to_node,
           cost AS total_cost
    FROM edges
    WHERE from_node = 'A'

    UNION ALL

    -- Recursive step: extend the path
    SELECT t.from_node,
           e.to_node,
           t.total_cost + e.cost
    FROM travel t
    JOIN edges e ON t.to_node = e.from_node

)
SELECT * FROM travel;
```

Output:

| from_node | to_node | total_cost |
|-----------|---------|------------|
| A | B | 3 |
| A | C | 5 |
| A | D | 10 |

What happened:

| Iteration | Extends | Total cost |
|-----------|---------|------------|
| Base case | A to B | 3 |
| Step 1 | A to C via B | 3 + 2 = 5 |
| Step 2 | A to D via B,C | 5 + 5 = 10 |
| Step 3 | nothing left — stops | — |

---

## Example 4 — What Happens Without a Stopping Condition

If you forget the WHERE clause, the query runs forever.

```sql
-- DANGEROUS — do not run this
WITH RECURSIVE infinite AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM infinite  -- no WHERE — never stops
)
SELECT * FROM infinite;
```

PostgreSQL will eventually crash or run out of memory.

Always make sure your recursive step will eventually produce zero new rows.

---

## How to Avoid Infinite Loops in Graph Queries

When a graph has cycles (A → B → A), the recursive CTE can loop forever.

The fix is to track which nodes you have already visited.

```sql
WITH RECURSIVE travel AS (

    SELECT from_node,
           to_node,
           cost,
           ARRAY[from_node] AS visited   -- track the path so far
    FROM edges
    WHERE from_node = 'A'

    UNION ALL

    SELECT t.from_node,
           e.to_node,
           t.cost + e.cost,
           t.visited || e.to_node        -- add current node to visited list
    FROM travel t
    JOIN edges e ON t.to_node = e.from_node
    WHERE NOT e.to_node = ANY(t.visited) -- do not visit a node twice

)
SELECT from_node, to_node, cost
FROM travel;
```

The `visited` array keeps a record of every node in the current path. If a node is already in that list, we skip it.

---

## UNION vs UNION ALL

| | Meaning |
|--|---------|
| `UNION` | Remove duplicate rows |
| `UNION ALL` | Keep all rows, including duplicates |

In recursive CTEs you almost always use `UNION ALL` because removing duplicates at each step is expensive and usually not needed. You handle duplicates at the end with `MIN()` or `DISTINCT`.

---

## Common Mistakes

| Mistake | What goes wrong |
|---------|----------------|
| No stopping condition | Query runs forever |
| Using `UNION` instead of `UNION ALL` | PostgreSQL may not allow it in recursive CTEs |
| Not tracking visited nodes in a graph with cycles | Infinite loop |
| Selecting too many columns in the base case | Recursive step must have exactly the same columns |

---

## The Pattern for Distance-Vector Routing

This is how everything above connects to your seminar topic:

```sql
WITH RECURSIVE routing AS (

    -- Base case: each router knows its direct neighbors
    SELECT from_node, to_node, cost, to_node AS next_hop
    FROM edges

    UNION ALL

    -- Recursive step: extend paths one hop further
    SELECT r.from_node,
           e.to_node,
           r.cost + e.cost,
           r.next_hop
    FROM routing r
    JOIN edges e ON r.to_node = e.from_node
    WHERE r.from_node <> e.to_node  -- do not go back to origin

)
SELECT from_node, to_node, MIN(cost) AS best_cost
FROM routing
GROUP BY from_node, to_node
ORDER BY from_node, best_cost;
```

Each recursive step = one iteration of the Distance-Vector algorithm.
The query stops = the algorithm converged.

---

## Summary

| Concept | One sentence |
|---------|-------------|
| CTE | A temporary named table inside a query |
| Recursive CTE | A CTE that refers to itself to build results step by step |
| Base case | The starting rows — runs only once |
| Recursive step | Uses the previous result to produce new rows |
| Stopping condition | The WHERE clause that eventually makes the step return zero rows |
| UNION ALL | Combines base case and recursive step |

---

## Links

- [[Distance-Vector Routing]] — the algorithm these CTEs implement
- [[DVR SQL Step by Step]] — full working code with outputs
- [[Seminar Weekly Plan]] — your schedule
