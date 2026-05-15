# SQL as a Programming Language: Distance-Vector Routing

This project demonstrates the power of modern SQL as a declarative programming language by implementing the **Distance-Vector Routing (DVR)** protocol entirely within **DuckDB** using stateful Recursive Common Table Expressions (CTEs).

## Objective
The target of this study is to prove that SQL is not just for data retrieval, but a robust environment for simulating complex distributed algorithms. By leveraging DuckDB's `USING KEY` extension, we map the **Bellman-Ford equation** 1:1 onto relational logic, allowing for autonomous network convergence and resilience against link failures.

## Project Structure

### Research & Documentation
- **[Distance_Vector_Routing_Report.tex](Distance_Vector_Routing_Report.tex)**: A professional, 2-column LaTeX research paper documenting the theory, implementation, and results of this study.
- **[Overview.md](Overview.md)**: High-level introduction to DVR and Bellman-Ford logic.
- **[duckdb_implementation/](duckdb_implementation/)**:
    - `01 DuckDB and Recursive CTEs.md`: Technical deep-dive into DuckDB's state-aware recursion.
    - `02 Distance-Vector Routing in DuckDB.md`: Detailed analysis of the SQL implementation and convergence results.

### Implementation
- **[duckdb_implementation/03 Full SQL Script.sql](duckdb_implementation/03%20Full%20SQL%20Script.sql)**: The complete, runnable DuckDB script including schema setup, DVR simulation, and link failure testing.
- **[Codes/DVR SQL Step by Step.md](Codes/DVR%20SQL%20Step%20by%20Step.md)**: A practical walkthrough for executing the simulation.

## How to Run

1. **Install DuckDB**: Download the CLI from [duckdb.org](https://duckdb.org/).
2. **Run the Simulation**:
   ```bash
   duckdb -c ".read 'duckdb_implementation/03 Full SQL Script.sql'"
   ```
3. **Simulate Failure**: The script includes a `DELETE` command to remove the B-C link. Re-run the routing query to observe the network re-converge to the next best paths.

## Key Results
The implementation successfully finds the shortest paths in a 4-node topology. When a link fails, the declarative query automatically adapts:
- **Router A** transitions from a cost-5 path (via B) to a cost-23 path (direct to C).
- Convergence is achieved autonomously without external procedural logic.

## Future Work
- **BGP Simulation**: Implementing Path-Vector routing using SQL array types.
- **OSPF Simulation**: Modeling Link-State protocols via recursive graph traversals.
- **Dynamic Congestion**: Adaptive routing based on variable link costs.

---
*Created for the Database Systems Seminar, University of Tübingen.*
