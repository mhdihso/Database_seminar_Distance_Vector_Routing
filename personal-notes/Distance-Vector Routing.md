
## Overview

Distance-Vector Routing is a distributed algorithm used in networks to determine the shortest path between nodes. Each node (router) maintains a table (distance vector) that stores the best-known distance to every other node and the next hop to reach them.

The algorithm is based on the **Bellman-Ford principle**, but operates in a decentralized manner where nodes exchange information only with their immediate neighbors.

---

## Core Idea

Each node:
- Knows the cost to its direct neighbors
- Maintains a table of distances to all other nodes
- Periodically shares this table with neighbors
- Updates its own table based on received information

---

## Data Structure

Each node maintains a routing table:

| Destination | Cost | Next Hop |
|------------|------|----------|
| A          | 0    | -        |
| B          | 1    | B        |
| C          | 3    | B        |

---

## Algorithm Steps

### Initialization

For each node `x`:
- `distance[x][x] = 0`
- `distance[x][neighbor] = cost(x, neighbor)`
- All others = ∞

---

### Iterative Update Rule

When node `x` receives a distance vector from neighbor `v`, it updates: 
    `D(x, y) = min(D(x, y), cost(x, v) + D(v, y))`


Where:
- `D(x, y)` = distance from x to y
- `cost(x, v)` = cost to neighbor v
- `D(v, y)` = neighbor’s distance to y

---

### Convergence

The algorithm repeats updates until:
- No routing table changes occur
- All nodes have consistent shortest paths

---

## Example

Network: *A --1-- B --1-- C*


Initial:
- A knows B = 1
- B knows A = 1, C = 1
- C knows B = 1

After updates:
- A learns C = 2 via B
- C learns A = 2 via B

---

## Key Properties

- Distributed
- Iterative
- Asynchronous
- Based on local knowledge

---

## Problems

### 1. Count to Infinity

When a node goes down:
- Incorrect updates propagate
- Distance values gradually increase to infinity

Example:
	`A is down`  
	`B thinks C knows path`  
	`C thinks B knows path`  
	`→ loop`

---

### 2. Slow Convergence

- Updates propagate slowly across network
- Especially problematic in large networks

---

### 3. Routing Loops

- Nodes may form cyclic paths temporarily

---

## Classical Solutions

### Split Horizon

Do not send route info back to the node it came from.

---

### Poison Reverse

Send back route with infinite cost to prevent reuse.

---

### Hold-Down Timers

Delay accepting new updates after a failure.

---

### Maximum Hop Count

Limit path length (e.g., RIP uses 15)

---

## Variants of Distance-Vector Routing

### 1. RIP (Routing Information Protocol)

- Basic distance-vector protocol
- Uses hop count as metric
- Periodic updates every 30 seconds
- Max hop = 15

---

### 2. RIPv2

- Adds subnet masks and authentication
- More flexible than RIPv1

---

### 3. EIGRP (Enhanced Interior Gateway Routing Protocol)

- Hybrid approach (distance-vector + link-state ideas)
- Faster convergence
- Uses Diffusing Update Algorithm (DUAL)
- Considers multiple metrics (bandwidth, delay)

---

### 4. BGP (Border Gateway Protocol)

- Used on the Internet
- Path-vector protocol (extension of distance-vector)
- Uses policies instead of pure distance
- Highly scalable

---

### 5. Babel

- Modern distance-vector protocol
- Loop-free
- Designed for dynamic networks

---

## SQL Implementation Concept

Distance-vector can be simulated using SQL:

### Representation
`edges(from_node, to_node, cost)`



---

### Recursive Computation

- Use recursive queries (CTE)
- Generate paths iteratively
- Aggregate with MIN(cost)

---

### Goal:
	shortest_paths(from, to, cost, next_hop)

---

## Advanced Ideas and Extensions

### 1. Weighted Multi-Metric Routing

Instead of simple cost:
- latency
- bandwidth
- reliability

---

## Advanced Ideas and Extensions

### 1. Weighted Multi-Metric Routing

Instead of simple cost:
- latency
- bandwidth
- reliability
*cost = w1 * latency + w2 * loss + w3 * bandwidth*

---

### 2. Probabilistic Routing

- Use probabilities instead of fixed paths
- Useful in uncertain or dynamic networks

---

### 3. Learning-Based Routing

- Apply Machine Learning to predict better paths
- Use historical traffic patterns

---

### 4. Braille/Compressed Representations

- Encode routing tables in compact symbolic form
- Useful for storage and visualization

---

### 5. Real-Time Adaptive Systems

- Combine streaming data with routing updates
- Dynamic reconfiguration

---

### 6. Distributed Simulation in Databases

- Simulate network protocols using SQL recursion
- Useful for analysis and education

---

### 7. Fault Detection Systems

- Detect anomalies in routing tables
- Identify unstable nodes or links

---

## Future Research Directions

- Integration with AI-driven networks
- Hybrid routing models (DV + ML)
- Queryable network intelligence (SQL + routing)
- Explainable routing decisions
- Low-resource routing for edge devices

---

## Conclusion

Distance-Vector Routing is a foundational algorithm in networking that demonstrates how simple local interactions can lead to global optimization. While it has limitations, its concepts remain highly relevant and serve as the basis for many modern routing systems and research directions.