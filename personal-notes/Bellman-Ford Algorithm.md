

Bellman-Ford is the algorithm that finds the shortest path from one node to all other nodes in a network.
It is the mathematical core behind Distance-Vector Routing and RIP.

---

## What it Does in One Sentence

Start from a source node.
Relax every edge repeatedly.
After enough rounds, you have the cheapest path to every node.

---

## What "Relax an Edge" Means

Relaxing an edge (u, v) means asking one question:

```
Is the path  source → ... → u → v  cheaper than what I currently know?
```

If yes — update. If no — do nothing.

```
dist(v) = min( dist(v),  dist(u) + cost(u, v) )
```

That one line is the entire algorithm.

---

## Key Properties

| Property | Value |
|----------|-------|
| What it finds | Shortest path from one source to all others |
| Works with negative costs? | Yes |
| Works with negative cycles? | No — it detects them but cannot solve them |
| How many rounds does it need? | At most N-1 rounds (N = number of nodes) |
| Time complexity | O(N * E) — N nodes, E edges |

---

## Why N-1 Rounds?

In the worst case, the shortest path visits every node once.
A path through N nodes has N-1 edges.
So after N-1 rounds of relaxation, every shortest path is guaranteed to be found.

If anything still changes after N-1 rounds — there is a negative cycle in the network.

---

## Step by Step — A Simple Example

Network:

```
A ---4--- B
|         |
2         1
|         |
C ---3--- D
```

Edges:
- A to B: cost 4
- A to C: cost 2
- B to D: cost 1
- C to D: cost 3

Goal: find the shortest path from A to every other node.

---

### Setup — Starting Distances

Set the source (A) to cost 0.
Set everything else to infinity (unknown).

| Node | Distance from A |
|------|----------------|
| A | 0 |
| B | infinity |
| C | infinity |
| D | infinity |

---

### Round 1 — Relax Every Edge Once

Check every edge and update if cheaper:

- Edge A→B: dist(B) = min(infinity, 0 + 4) = **4**
- Edge A→C: dist(C) = min(infinity, 0 + 2) = **2**
- Edge B→D: dist(D) = min(infinity, 4 + 1) = **5**
- Edge C→D: dist(D) = min(5, 2 + 3) = **5** (same, no change)

| Node | Distance from A |
|------|----------------|
| A | 0 |
| B | 4 |
| C | 2 |
| D | 5 |

---

### Round 2 — Relax Every Edge Again

- Edge A→B: dist(B) = min(4, 0 + 4) = 4 (no change)
- Edge A→C: dist(C) = min(2, 0 + 2) = 2 (no change)
- Edge B→D: dist(D) = min(5, 4 + 1) = 5 (no change)
- Edge C→D: dist(D) = min(5, 2 + 3) = 5 (no change)

Nothing changed. The algorithm can stop early.

---

### Round 3 — Would also produce no changes (N-1 = 3 rounds maximum here)

Final result:

| Node | Shortest distance from A | Path |
|------|--------------------------|------|
| A | 0 | — |
| B | 4 | A → B |
| C | 2 | A → C |
| D | 5 | A → C → D or A → B → D (same cost) |

---

## The Full Algorithm Written Out

```
1. Set dist(source) = 0
2. Set dist(every other node) = infinity

3. Repeat N-1 times:
       For every edge (u, v) with cost w:
           if dist(u) + w < dist(v):
               dist(v) = dist(u) + w

4. (Optional) Check one more time:
       If anything still changes — there is a negative cycle
```

---

## In SQL

```sql
-- Setup: source node is 'A', all others start as infinity
CREATE TABLE distances AS
SELECT 'A' AS node, 0 AS dist
UNION ALL
SELECT 'B', 999999
UNION ALL
SELECT 'C', 999999
UNION ALL
SELECT 'D', 999999;

-- One round of relaxation
UPDATE distances d
SET dist = e.new_dist
FROM (
    SELECT e.to_node,
           MIN(d.dist + e.cost) AS new_dist
    FROM edges e
    JOIN distances d ON e.from_node = d.node
    GROUP BY e.to_node
) e
WHERE d.node = e.to_node
  AND e.new_dist < d.dist;

-- Repeat this UPDATE N-1 times
-- In practice, use WITH RECURSIVE instead (see DVR SQL Step by Step)
```

---

## Bellman-Ford vs Dijkstra

Both find shortest paths. They work differently.

| | Bellman-Ford | Dijkstra |
|-|-------------|----------|
| Negative costs allowed | Yes | No |
| Speed | Slower — O(N * E) | Faster — O(E log N) |
| How it works | Relaxes all edges repeatedly | Always picks the closest unvisited node next |
| Used in | Distance-Vector Routing, RIP | GPS navigation, Google Maps |
| Simple to implement in SQL | Yes — fits naturally into recursive CTEs | Harder — needs a priority queue |

For your seminar: Bellman-Ford is the right choice because it maps directly to `WITH RECURSIVE`.

---

## The Negative Cycle Problem

A negative cycle is a loop where the total cost keeps going down forever.

Example:
```
A ---(-1)--- B ---(-1)--- C ---(-1)--- A
```

Going around this loop: A → B → C → A costs -3.
Going around again: -6.
Going around again: -9.
There is no shortest path — it goes to negative infinity.

Bellman-Ford detects this: if distances still change after N-1 rounds, a negative cycle exists.
In routing networks, negative costs do not occur, so this is rarely a real problem.

---

## Why Bellman-Ford Works for Distance-Vector Routing

In Distance-Vector Routing, each router does not know the full network.
It only knows what its neighbors tell it.

Bellman-Ford fits perfectly because:
- It does not need to see the whole network at once
- Each round = one exchange of routing tables between neighbors
- It naturally converges after enough rounds

The key equation used by every router at every step:

```
dist(me, destination) = min over all neighbors n of:
    cost(me, n) + dist(n, destination)
```

This is the Bellman-Ford relaxation step, applied from each router's local perspective.

---

## Summary

| Question | Answer |
|----------|--------|
| What does Bellman-Ford find? | Shortest path from one source to all nodes |
| What is relaxation? | Checking if a path through u makes the path to v cheaper |
| How many rounds are needed? | At most N-1 |
| What if it still changes after N-1 rounds? | There is a negative cycle |
| Why is it used in routing? | Each router only needs local information — fits perfectly |
| Why is it good for SQL? | Maps directly to WITH RECURSIVE |

---

## Links

- [[Distance-Vector Routing]] 
- [[Routing Information Protocol (RIP)]] 
- [[SQL Recursive CTEs]] 
- [[DVR SQL Step by Step]] 
- [[Seminar Weekly Plan]] 
