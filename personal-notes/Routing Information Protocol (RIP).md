

RIP is the oldest and simplest distance-vector routing protocol.
It is the real-world implementation of the Distance-Vector algorithm.

---

## What is RIP in One Sentence

Every 30 seconds, each router tells its neighbors its full routing table.
Neighbors update their own tables if they find a cheaper path.
This repeats until everyone agrees.

---

## Key Numbers to Remember

| Property | Value |
|----------|-------|
| Maximum hops allowed | 15 |
| Cost of unreachable destination | 16 (means infinity) |
| How often tables are shared | Every 30 seconds |
| Standardized | 1988 |
| Cost metric | Number of hops only |

---

## Why Maximum 15 Hops?

RIP uses hop count as its only cost metric.
If a destination is more than 15 hops away, RIP considers it unreachable and assigns cost 16.

This was a design decision to prevent the count-to-infinity problem from running forever.
The downside: RIP cannot work in large networks where destinations are more than 15 hops away.

---

## How RIP Works Step by Step

1. Each router starts knowing only its direct neighbors (cost = 1 per hop)
2. Every 30 seconds, each router broadcasts its full routing table to all neighbors
3. Each neighbor checks: is there a cheaper path in what I just received?
   - New cost = 1 (hop to neighbor) + neighbor's cost to destination
   - If new cost is cheaper, update the table
4. Repeat until no router updates anything — convergence reached

---

## RIP vs the General Distance-Vector Algorithm

| | General DVR | RIP |
|-|------------|-----|
| Cost metric | Any (latency, bandwidth...) | Hops only |
| Update trigger | When something changes | Every 30 seconds, always |
| Max distance | No limit | 15 hops |
| Infinity value | Depends | 16 |
| Network size | Any | Small networks only |

---

## A Simple RIP Example

Network:

```
A ---1hop--- B ---1hop--- C ---1hop--- D
```

### T=0 — each router knows only direct neighbors

| Router | Knows |
|--------|-------|
| A | B = 1 hop |
| B | A = 1 hop, C = 1 hop |
| C | B = 1 hop, D = 1 hop |
| D | C = 1 hop |

### T=1 — after first broadcast

| Router | Now also knows |
|--------|----------------|
| A | C = 2 hops (via B) |
| B | D = 2 hops (via C) |
| C | A = 2 hops (via B) |
| D | B = 2 hops (via C) |

### T=2 — after second broadcast

| Router | Now also knows |
|--------|----------------|
| A | D = 3 hops (via B) |
| D | A = 3 hops (via C) |

### T=3 — convergence

No new paths found. Algorithm stops.

Final routing table for A:

| Destination | Hops | Via |
|-------------|------|-----|
| B | 1 | B |
| C | 2 | B |
| D | 3 | B |

---

## The Count-to-Infinity Problem in RIP

### What happens when a link breaks

```
A ---1--- B ---1--- C
```

Suppose the link A-B breaks.

- B knows A is unreachable (its direct link is down)
- But C still thinks A is reachable via B at cost 2
- C tells B: "I can reach A at cost 2"
- B thinks: "C can reach A at 2, so I can reach A at 3" — wrong
- B tells C: "I can reach A at 3"
- C updates to 4
- This goes on until the cost hits 16 (infinity)

This process is slow and wastes time. RIP has workarounds for this.

---

## RIP's Solutions to Count-to-Infinity

### Split Horizon

Do not advertise a route back to the router you learned it from.

```
B learned about A from... A itself.
So B will NOT tell A about A.
```

This prevents the most basic loops.

### Poison Reverse

A stronger version of Split Horizon.
Instead of saying nothing, actively advertise the route back with cost = 16 (unreachable).

```
B learned about A from A.
B tells A: "my cost to A via you = 16 (unreachable)"
```

This makes it explicit and faster to detect broken routes.

### Hold-Down Timer

After a route goes down, ignore any updates about that route for a fixed time period.
This gives the network time to stabilize before accepting new (possibly wrong) information.

Downside: convergence becomes slower.

### Maximum Hop Count

As mentioned: cost 16 = infinity.
Even if count-to-infinity happens, it stops at 16 instead of running forever.

---

## RIP Versions

| Version | Notes |
|---------|-------|
| RIPv1 (1988) | Original. Broadcasts to all. No subnet mask support |
| RIPv2 (1998) | Sends subnet mask with updates. Uses multicast instead of broadcast |
| RIPng | Extension of RIPv2 with support for IPv6 (modern internet addresses) |

---

## Where RIP is Used

- Small local area networks (LANs)
- Simple internal networks where the destination is always within 15 hops
- Teaching and learning — RIP is the simplest protocol to understand

RIP is NOT used for:
- The global internet (BGP is used there)
- Large company networks (OSPF is used there)
- Any network where destinations are more than 15 hops away

---

## RIP vs Other Protocols

| Protocol | Type | Used for | Cost metric |
|----------|------|----------|-------------|
| RIP | Distance-vector | Small LANs | Hops |
| OSPF | Link-state | Large networks | Bandwidth |
| BGP | Distance-vector (hybrid) | Internet between ISPs | Many factors |
| EIGRP | Hybrid | Cisco networks | Bandwidth + delay |

---

## Why RIP Matters for Your Seminar

RIP is the direct real-world version of what you are implementing in SQL.

Your SQL implementation:
- Uses cost instead of hops (more general than RIP)
- Runs the same Bellman-Ford logic RIP uses
- Converges the same way RIP converges
- The network failure simulation you will build mirrors what happens in RIP when a link goes down

Understanding RIP helps you explain *why* your SQL solution matters and where it fits in the real world.

---

## Summary

| Question | Answer |
|----------|--------|
| What is RIP? | The oldest distance-vector routing protocol |
| What does it use as cost? | Number of hops only |
| How often does it update? | Every 30 seconds |
| What is its limit? | 15 hops maximum |
| What is 16? | Infinity — means unreachable |
| What problem does it have? | Count-to-infinity |
| How does it fix that? | Split horizon, poison reverse, hold-down timer, max hop count |
| Where is it used? | Small local networks |

---

## Links

- [[Distance-Vector Routing]] — the algorithm RIP is based on
- [[Bellman-Ford Algorithm]] — the math behind RIP
- [[DVR SQL Step by Step]] — your SQL implementation
- [[Seminar Weekly Plan]] — your schedule
