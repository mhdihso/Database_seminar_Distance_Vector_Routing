# Distance-Vector Routing

> A method that routers use to find the cheapest or shortest path to send data across a network.

---

## The Core Idea

- Every router only knows about its **direct neighbors**
- Routers share what they know with their neighbors
- Each router updates its table based on wha t it hears
- This repeats until everyone agrees — this is called **convergence**

> "Routing by rumour" — because each router trusts what its neighbor says, without verifying it independently.

---

## Key Terms

| Term | What it means |
|------|--------------|
| **Router** | A node or computer in the network |
| **Hop** | One step from one router to another |
| **Cost / Distance** | How expensive a path is (number of hops, speed, latency, etc.) |
| **Routing Table** | A table each router keeps: "to reach X, go via Y, cost = Z" |
| **Distance Vector (DV)** | The list of distances a router knows and shares with neighbors |
| **Next Hop** | Which neighbor to go through to reach a destination |
| **Convergence** | When all routers agree and stop updating their tables |

---

## How the Algorithm Works

### Step by step

1. **T=0 (Start):** Each router only knows the cost to its direct neighbors
2. **Share:** Every router sends its table to all its neighbors
3. **Update:** Each router checks: "Is there a cheaper path via what my neighbor told me?"
   - Formula: `new_cost = cost_to_neighbor + neighbor's_cost_to_destination`
   - If `new_cost < current_cost` — update the table
4. **Repeat** steps 2 and 3 until nothing changes anymore

### The math behind it (Bellman-Ford equation)

```
dist(u, v) = min over all neighbors w of:  cost(u, w) + dist(w, v)
```

In plain language: the cheapest way from u to v is through whichever neighbor w gives the lowest total cost.

---

## A Concrete Example[[DVR SQL Step by Step]]

Network: 4 routers — A, B, C, D

```
A ---3--- B
|         |
23        2
|         |
C ---5--- D
```

### T=0 — each router only knows its direct neighbors

| Router | Knows |
|--------|-------|
| A | B=3, C=23 |
| B | A=3, C=2 |
| C | A=23, B=2, D=5 |
| D | C=5 |

### T=1 — after first exchange

- A hears from B: "I can reach C for cost 2" — A updates: A to C via B = 3+2 = **5** (cheaper than 23)
- A hears from C: "I can reach D for cost 5" — A to D via C = 23+5 = **28**

### T=2 — after second exchange

- A hears from B: "I can reach D for cost 7" — A to D via B = 3+7 = **10** (cheaper than 28)

### T=3 — convergence

No router finds a cheaper path. The algorithm stops.

Final best paths from A:

| Destination | Cost | Via |
|-------------|------|-----|
| B | 3 | direct |
| C | 5 | B |
| D | 10 | B |

---

## The Count-to-Infinity Problem

### What is it?

When a link goes down, routers can get confused and keep increasing a cost forever (1, 2, 3, 4... toward infinity) before realizing the destination is unreachable.

### Why does it happen?

Router B does not know that the path C claims to have actually goes through B itself. So B keeps believing C has a valid route, and the cost inflates endlessly.

### Solutions

| Solution | How it helps |
|----------|-------------|
| **Split Horizon** | Do not advertise a route back to the router you learned it from |
| **Poison Reverse** | Advertise a route back with cost = infinity to explicitly block it |
| **Hold-down timer** | Ignore updates for a short time after a route goes down |
| **Maximum hop count** | RIP uses 15 as maximum — anything beyond is considered unreachable |

---

## Real-World Protocols That Use This

| Protocol | Notes |
|----------|-------|
| **RIP (v1, v2)** | Oldest. Max 15 hops. Shares tables every 30 seconds |
| **IGRP / EIGRP** | Cisco protocols. EIGRP is a hybrid and loop-free |
| **BGP** | Used across the entire Internet between ISPs |
| **Babel** | Modern loop-free distance-vector protocol |

---

## Why This Matters

- The algorithm is **iterative** — perfect for `WITH RECURSIVE` in SQL
- Each round of the algorithm = one recursive step in the query
- The routing table = a SQL table updated each iteration
- Convergence = when the recursive query produces no new rows

### Core SQL idea (sketch only)

```sql
WITH RECURSIVE routing AS (
    -- Base case: direct neighbors
    SELECT from_node, to_node, cost, to_node AS next_hop
    FROM edges

    UNION ALL

    -- Recursive step: can we reach further via a neighbor?
    SELECT r.from_node, e.to_node, r.cost + e.cost, r.next_hop
    FROM routing r
    JOIN edges e ON r.to_node = e.from_node
    WHERE r.cost + e.cost < current_known_cost
)
SELECT * FROM routing;
```

---

## Related Concepts to Look Up

- [[Bellman-Ford Algorithm]]
- [[Routing Information Protocol (RIP)]]
- [[Link-State Routing]]
- [[SQL Recursive CTEs]]

---

## Sources

- Wikipedia: Distance-vector routing protocol
- Seminar topic description, University of Tubingen, Database Systems
