

Link-State Routing is the main alternative to Distance-Vector Routing.
Instead of sharing routing tables with neighbors only, every router shares information with the entire network.
Each router then builds a complete map of the network and calculates the best paths itself.

---

## What it Does in One Sentence

Every router floods the network with information about its own links.
Every router collects all of this information.
Every router independently runs Dijkstra on the full map to find all shortest paths.

---

## The Core Difference from Distance-Vector

| | Distance-Vector | Link-State |
|-|----------------|------------|
| What each router knows | Only what neighbors tell it | The full network map |
| What is shared | Routing tables | Only own link costs |
| Who calculates paths | Distributed — each router trusts neighbors | Each router calculates independently |
| Algorithm used | Bellman-Ford | Dijkstra |
| Nickname | Routing by rumour | Routing by map |
| Convergence speed | Slow | Fast |
| Memory needed | Low | High — must store full map |

---

## Key Terms

| Term | What it means |
|------|--------------|
| Link-State Advertisement (LSA) | A message a router sends describing its own direct links and their costs |
| Flooding | Sending an LSA to every router in the entire network |
| Link-State Database (LSDB) | The full collection of all LSAs — the complete network map |
| SPF (Shortest Path First) | Another name for the algorithm — Dijkstra finds the shortest path first |
| OSPF | Open Shortest Path First — the most widely used link-state protocol |

---

## How Link-State Routing Works Step by Step

1. Each router discovers its direct neighbors and measures the cost to each
2. Each router creates an LSA describing its own links
3. Each router floods its LSA to every other router in the network
4. Every router collects all LSAs and builds the same complete map (LSDB)
5. Every router runs Dijkstra on that map independently
6. Each router installs the resulting shortest paths into its routing table

---

## A Simple Example

Network:

```
A ---3--- B
|         |
23        2
|         |
C ---5--- D
```

### Step 1 — Each router sends its LSA

| Router | LSA content |
|--------|-------------|
| A | I have links: B=3, C=23 |
| B | I have links: A=3, C=2 |
| C | I have links: A=23, B=2, D=5 |
| D | I have links: C=5 |

### Step 2 — Every router now has all four LSAs

Every router builds the same complete map:

```
A --3-- B
A --23- C
B --2-- C
C --5-- D
```

### Step 3 — Every router runs Dijkstra independently

Router A runs Dijkstra from itself:

| Step | Visited | dist(A) | dist(B) | dist(C) | dist(D) |
|------|---------|---------|---------|---------|---------|
| Start | — | 0 | inf | inf | inf |
| Visit A | A | 0 | 3 | 23 | inf |
| Visit B | A, B | 0 | 3 | 5 | inf |
| Visit C | A, B, C | 0 | 3 | 5 | 10 |
| Visit D | A, B, C, D | 0 | 3 | 5 | 10 |

Final result for A:

| Destination | Cost | Via |
|-------------|------|-----|
| B | 3 | B |
| C | 5 | B |
| D | 10 | B |

Same result as Distance-Vector — but calculated differently and faster.

---

## Dijkstra — The Algorithm Link-State Uses

Dijkstra always picks the cheapest unvisited node next.
It is greedy — it never goes back and changes a decision.

```
1. Set dist(source) = 0, all others = infinity
2. Mark all nodes as unvisited

3. Repeat until all nodes are visited:
       Pick the unvisited node with the smallest known distance — call it u
       For each neighbor v of u:
           new_cost = dist(u) + cost(u, v)
           if new_cost < dist(v):
               dist(v) = new_cost
       Mark u as visited
```

Key difference from Bellman-Ford:
- Bellman-Ford relaxes all edges repeatedly
- Dijkstra picks the best unvisited node each time — much faster

---

## Flooding — How LSAs Reach Every Router

When router A creates an LSA, it sends it to all its neighbors.
Each neighbor forwards it to all their neighbors.
And so on — until every router in the network has received it.

To avoid sending the same LSA forever, each LSA has a sequence number.
If a router receives an LSA it already has — it drops it.

```
A sends LSA to B and C
B forwards to C (C already has it — drops it)
C forwards to D
D has received all LSAs — done
```

---

## OSPF — The Main Link-State Protocol

OSPF (Open Shortest Path First) is the most widely used link-state protocol.
It is used in large company networks and internet service provider networks.

| Property | Value |
|----------|-------|
| Cost metric | Bandwidth (faster link = lower cost) |
| Updates | Only when something changes (not periodic like RIP) |
| Network size | Very large networks |
| Convergence | Fast |
| Standardized | 1998 |

OSPF divides large networks into areas to reduce the amount of flooding needed.

---

## Link-State vs Distance-Vector — When to Use Which

| Situation | Better choice |
|-----------|--------------|
| Small simple network | Distance-Vector (RIP) — simpler to set up |
| Large network | Link-State (OSPF) — faster convergence |
| Limited router memory | Distance-Vector — does not store full map |
| Need fast recovery from failures | Link-State — detects changes immediately |
| Teaching and learning | Distance-Vector — easier to understand |

---

## Why Link-State Does Not Have Count-to-Infinity

In Distance-Vector, routers trust what neighbors say — and neighbors can be wrong.
In Link-State, every router has the full map and calculates paths itself.
There is no chain of trust that can go wrong.

If a link goes down:
- The router connected to that link immediately sends a new LSA
- The new LSA floods the network
- Every router updates its map and re-runs Dijkstra
- Convergence is fast and correct

---

## Why This Matters for Your Seminar

Your seminar topic is Distance-Vector Routing — not Link-State.
But understanding Link-State helps you explain why Distance-Vector is interesting and where it fits.

In your presentation you can say:

- Distance-Vector is simpler — each router only needs local information
- This makes it a natural fit for SQL recursive CTEs
- Link-State requires a full map — harder to model in SQL
- Your implementation shows what Bellman-Ford does step by step — which Dijkstra hides

---

## Summary

| Question | Answer |
|----------|--------|
| What does each router share? | Only its own direct link costs (LSA) |
| What does each router know? | The full network map |
| What algorithm does it use? | Dijkstra |
| What is flooding? | Sending an LSA to every router in the network |
| What is OSPF? | The most widely used link-state protocol |
| Why is it faster than DVR? | No rumour chain — every router calculates independently |
| Why does it not have count-to-infinity? | Every router has the full picture — no wrong assumptions |

---

## Links

- [[Distance-Vector Routing]] 
- [[Bellman-Ford Algorithm]] 
- [[Routing Information Protocol (RIP)]] 
- [[DVR SQL Step by Step]] 
- [[Seminar Weekly Plan]] 
