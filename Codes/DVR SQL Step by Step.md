# Distance-Vector Routing — SQL Step by Step

The network we use in every example:

```
A ---3--- B
|         |
23        2
|         |
C ---5--- D
```

---

## Step 1 — Create the Network

```sql
CREATE TABLE edges (
    from_node TEXT,
    to_node   TEXT,
    cost      INT
);

INSERT INTO edges VALUES
    ('A', 'B', 3),
    ('B', 'A', 3),
    ('A', 'C', 23),
    ('C', 'A', 23),
    ('B', 'C', 2),
    ('C', 'B', 2),
    ('C', 'D', 5),
    ('D', 'C', 5);
```

Output — what is in the table:

| from_node | to_node | cost |
|-----------|---------|------|
| A | B | 3 |
| B | A | 3 |
| A | C | 23 |
| C | A | 23 |
| B | C | 2 |
| C | B | 2 |
| C | D | 5 |
| D | C | 5 |

---

## Step 2 — T=0 — What Each Router Knows at the Start

Each router only knows its direct neighbors. Nothing else.

```sql
SELECT from_node, to_node, cost
FROM edges
ORDER BY from_node, cost;
```

Output:

| from_node | to_node | cost |
|-----------|---------|------|
| A | B | 3 |
| A | C | 23 |
| B | A | 3 |
| B | C | 2 |
| C | B | 2 |
| C | D | 5 |
| C | A | 23 |
| D | C | 5 |

---

## Step 3 — Run the Full Algorithm (All Iterations at Once)

This is the core SQL. It keeps finding cheaper paths until nothing improves.

```sql
SOME COOL SQL CODE
```

Output — the final routing table for every router:

| from_node | to_node | best_cost |
|-----------|---------|-----------|
| A | B | 3 |
| A | C | 5 |
| A | D | 10 |
| B | A | 3 |
| B | C | 2 |
| B | D | 7 |
| C | B | 2 |
| C | A | 5 |
| C | D | 5 |
| D | C | 5 |
| D | B | 7 |
| D | A | 10 |

Notice: A to C is now 5 (via B), not 23 (direct). The algorithm found the cheaper path.

---

## Step 4 — Also Show the Next Hop

Not just the cost — also show which neighbor to use.

```sql
EVEN MORE COOL SQL CODE HERE
```

Output:

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

Reading example: A wants to reach D — best cost is 10, and it should send the packet to B first.

---

## Step 5 — Simulate a Network Failure

The link between B and C goes down. What happens to the routing tables?

```sql

DELETE FROM edges
WHERE (from_node = 'B' AND to_node = 'C')
   OR (from_node = 'C' AND to_node = 'B');
```

Now re-run the routing query from Step 4.

Output after failure:

| from_node | to_node | best_cost | next_hop |
|-----------|---------|-----------|----------|
| A | B | 3 | B |
| A | C | 26 | C |
| A | D | 31 | C |
| B | A | 3 | A |
| B | C | 26 | A |
| B | D | 31 | A |
| C | A | 23 | A |
| C | D | 5 | D |
| D | C | 5 | C |
| D | A | 28 | C |

Notice what changed:
- A to C was 5 (via B) — now it is 26 (via C directly)
- B to C was 2 (direct) — now it must go B → A → C = 26
- B and D can no longer reach each other efficiently

---

## Summary — What Each SQL Block Does

| Step   | What it does                                   |
| ------ | ---------------------------------------------- |
| Step 1 | Creates the network as a table                 |
| Step 2 | Shows T=0 — only direct neighbors known        |
| Step 3 | Runs the full algorithm, finds best costs      |
| Step 4 | Same as Step 3, but also shows next hop        |
| Step 5 | Deletes a link and re-runs to simulate failure |

---

## Links

- [[Distance-Vector Routing]] 
- [[Seminar Weekly Plan]] 
