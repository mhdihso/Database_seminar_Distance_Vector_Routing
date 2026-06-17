import pandas as pd

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

# Simulate 1_Stage_1_Network_Setup.py undirected logic
edges_directed = []
for f, t, c in edges:
    edges_directed.append((f, t, c))
    if (t, f, c) not in edges_directed:
        edges_directed.append((t, f, c))

edges_df = pd.DataFrame(edges_directed, columns=["from_node", "to_node", "cost"])

def _simulate_routing_steps(edges_df: pd.DataFrame):
    current = edges_df.rename(columns={"cost": "best_cost"}).copy()
    current["next_hop"] = current["to_node"]
    current = current[["from_node", "to_node", "best_cost", "next_hop"]]

    steps = [current.copy()]
    nodes = set(edges_df["from_node"]) | set(edges_df["to_node"])
    max_iter = len(nodes)

    for i in range(max_iter):
        updated = False
        new_rows = []
        for _, r in current.iterrows():
            neighbors = edges_df[edges_df["from_node"] == r["to_node"]]
            for _, e in neighbors.iterrows():
                if r["from_node"] == e["to_node"]:
                    continue
                new_cost = r["best_cost"] + e["cost"]
                existing = current[
                    (current["from_node"] == r["from_node"]) &
                    (current["to_node"] == e["to_node"])
                ]
                if existing.empty or new_cost < existing.iloc[0]["best_cost"]:
                    new_rows.append({
                        "from_node": r["from_node"],
                        "to_node": e["to_node"],
                        "best_cost": new_cost,
                        "next_hop": r["next_hop"],
                    })
                    updated = True

        if not updated:
            print(f"Converged at round {i}")
            break

        for row in new_rows:
            mask = (
                (current["from_node"] == row["from_node"]) &
                (current["to_node"] == row["to_node"])
            )
            if mask.any():
                current.loc[mask, "best_cost"] = row["best_cost"]
                current.loc[mask, "next_hop"] = row["next_hop"]
            else:
                current = pd.concat([current, pd.DataFrame([row])], ignore_index=True)

        steps.append(current.copy())

    return steps

steps = _simulate_routing_steps(edges_df)
final = steps[-1]
print("Final routes from A:")
print(final[final["from_node"] == "A"].sort_values("to_node"))
