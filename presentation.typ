// ═══════════════════════════════════════════════════════════════════════
// SQL as a Programming Language:
// Distance-Vector Routing with Recursive CTEs in DuckDB
//
// Mehdi Hoseyni - Database Systems Seminar - University of Tübingen
// Summer Semester 2026
// ═══════════════════════════════════════════════════════════════════════

// ── Theme Configuration ──────────────────────────────────────────────
#let uni-red = rgb("#A51E37")
#let dark-bg = rgb("#1a1a2e")
#let accent-teal = rgb("#00897B")
#let accent-blue = rgb("#1565C0")
#let light-gray = rgb("#F5F5F5")
#let mid-gray = rgb("#E0E0E0")
#let text-dark = rgb("#212121")
#let text-muted = rgb("#757575")

#set page(
  paper: "presentation-16-9",
  margin: (x: 1.6cm, top: 1.2cm, bottom: 1.4cm),
)

#set text(
  font: "Helvetica Neue",
  size: 16pt,
  fill: text-dark,
)

// ── Helper Functions ─────────────────────────────────────────────────

#let slide-header(title) = {
  block(width: 100%)[
    #text(size: 24pt, weight: "bold", fill: text-dark)[#title]
    #v(1pt)
    #line(length: 55pt, stroke: 2pt + uni-red)
    #v(5pt)
  ]
}

#let footer-bar() = {
  place(bottom + left, dy: 0.6cm, dx: -0.2cm,
    block(width: 105%, height: 24pt, fill: rgb("#f0f0f0"))[
      #set text(size: 7.5pt, fill: text-muted)
      #pad(x: 1.6cm, y: 5pt)[
        #grid(columns: (1fr, 1fr, 1fr),
          [Mehdi Hoseyni - University of Tübingen],
          align(center)[SQL as a Programming Language],
          align(right)[#context counter(page).display("1 / 1", both: true)],
        )
      ]
    ]
  )
}

#let accent-box(body, color: accent-teal) = {
  block(
    width: 100%,
    inset: 8pt,
    radius: 3pt,
    fill: color.lighten(92%),
    stroke: (left: 3pt + color),
  )[#body]
}

#let code-block(body) = {
  block(
    width: 100%,
    inset: 7pt,
    radius: 3pt,
    fill: rgb("#f8f8f8"),
    stroke: 0.5pt + mid-gray,
  )[
    #set text(font: "Menlo", size: 8.5pt)
    #body
  ]
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 1: Title
// ═══════════════════════════════════════════════════════════════════════

#set page(margin: 0pt)
#block(width: 100%, height: 100%, fill: dark-bg)[
  #place(top, block(width: 100%, height: 4pt,
    fill: gradient.linear(uni-red, accent-teal, accent-blue)))

  #pad(x: 2.2cm, y: 1.8cm)[
    #text(size: 10pt, fill: rgb("#aaa"), tracking: 1.5pt, weight: "medium")[
      EBERHARD KARLS UNIVERSITÄT TÜBINGEN
    ]
    #v(2pt)
    #text(size: 9pt, fill: rgb("#888"))[
      Department of Computer Science - Database Systems
    ]

    #v(1.2cm)

    #text(size: 36pt, weight: "bold", fill: white)[
      SQL as a Programming Language
    ]
    #v(4pt)
    #block(width: 70%)[
      #text(size: 18pt, fill: accent-teal)[
        Implementing Distance-Vector Routing#linebreak()with Recursive CTEs in DuckDB
      ]
    ]

    #v(1cm)
    #line(length: 80pt, stroke: 2pt + uni-red)
    #v(10pt)

    #text(size: 13pt, fill: rgb("#ccc"))[Mehdi Hoseyni]
    #v(4pt)
    #text(size: 10pt, fill: rgb("#888"))[
      Seminar: SQL is a Programming Language - Summer Semester 2026
    ]
  ]
]

#set page(margin: (x: 1.6cm, top: 1.2cm, bottom: 1.4cm))

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 2: Outline
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Outline]
#footer-bar()

#set text(size: 13pt)

#grid(columns: (1fr, 1fr), column-gutter: 24pt,
  [
    + Motivation and Research Question
    + Distance-Vector Routing Protocol
    + The Bellman-Ford Equation
    + SQL Recursive CTEs: The Challenge
    + DuckDB `USING KEY`: The Solution
    + Standard vs Keyed CTE Comparison
  ],
  [
    7. Implementation: The Algorithmic Core
    8. Convergence Results
    9. Network Failure and Re-convergence
    10. Live Demonstration
    11. Benchmark Results
    12. Key Findings and Conclusion
  ],
)

#v(10pt)

#accent-box(color: accent-blue)[
  #text(size: 11pt)[
    *Presentation duration:* ~20 minutes + discussion \
    *Demo:* Interactive Streamlit application (localhost:8501)
  ]
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 3: Motivation
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Motivation and Research Question]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 18pt,
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-teal),
    )[
      #text(weight: "bold", size: 13pt)[Research Question]
      #v(4pt)
      #set text(size: 11.5pt)
      Can SQL serve as a *first-class programming language* for complex algorithmic simulation?

      #v(4pt)
      *Approach:* Implement the Distance-Vector Routing protocol entirely within SQL using DuckDB's recursive CTEs.

      #v(4pt)
      *Goal:* Show that declarative logic with state-aware recursion achieves global optimization through local updates.
    ]
  ],
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-blue),
    )[
      #text(weight: "bold", size: 13pt)[Why It Matters]
      #v(4pt)
      #set text(size: 11.5pt)
      - *Traditional view:* SQL is only for data retrieval
      - *Our claim:* Modern SQL extensions enable full simulation of distributed systems
      - *Implication:* Database engines can function as protocol validation environments
    ]

    #v(8pt)

    #accent-box(color: uni-red)[
      #set text(size: 11pt)
      *Thesis:* Modern SQL, through `USING KEY`, can express and execute distributed routing algorithms using declarative recursion.
    ]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 4: DVR Protocol
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Distance-Vector Routing Protocol]
#footer-bar()

#grid(columns: (1.1fr, 0.9fr), column-gutter: 18pt,
  [
    #set text(size: 12pt)
    *Core Idea - "Routing by Local Knowledge":*
    #v(3pt)
    - Each router maintains a _distance vector_ of costs to all destinations
    - Routers share tables *only with immediate neighbors*
    - Each router updates its table if a cheaper path is discovered
    - Process repeats until *convergence*

    #v(6pt)

    *Algorithm Steps:*
    #v(3pt)
    #block(inset: (left: 8pt))[
      #set text(size: 11pt)
      *T=0:* Each router knows only direct neighbor costs \
      *T=1:* Share tables; apply relaxation rule \
      *T=2+:* Repeat until convergence \
      *T=k:* Fixed point - all paths optimal
    ]
  ],
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + uni-red),
    )[
      #text(weight: "bold", size: 12pt)[Key Properties]
      #v(4pt)
      #set text(size: 11pt)
      #table(
        columns: (auto, 1fr),
        stroke: none, row-gutter: 2pt,
        [*Distributed*], [No central controller],
        [*Iterative*], [Updates in rounds],
        [*Asynchronous*], [Independent timing],
        [*Convergent*], [≤ |V|-1 rounds],
      )
    ]

    #v(6pt)

    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-teal),
    )[
      #text(weight: "bold", size: 12pt)[Real-World Protocols]
      #v(3pt)
      #set text(size: 11pt)
      - *RIP* (v1, v2) - max 15 hops
      - *EIGRP* - Cisco hybrid protocol
      - *BGP* - Internet backbone routing
    ]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 5: Bellman-Ford
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[The Bellman-Ford Equation]
#footer-bar()

#block(
  width: 100%, inset: 12pt, radius: 4pt,
  fill: rgb("#fafafa"), stroke: 0.5pt + mid-gray,
)[
  #align(center)[
    #text(size: 20pt, font: "New Computer Modern")[
      $d(u, v) = min_(w in "Adj"(u)) { "cost"(u, w) + d(w, v) }$
    ]
  ]
]

#v(4pt)

#grid(columns: (1fr, 1fr), column-gutter: 18pt,
  [
    #text(weight: "bold", size: 13pt)[Example Network Topology]
    #v(4pt)
    #align(center)[
      #block(inset: 10pt, radius: 4pt, fill: light-gray)[
        #set text(font: "Menlo", size: 12pt)
        ```
        A --- 3 --- B
        |             |
        23            2
        |             |
        C --- 5 --- D
        ```
      ]
    ]
    #v(3pt)
    #set text(size: 11pt)
    Direct link A→C costs 23, but the indirect path A→B→C costs only 3+2 = *5*.
  ],
  [
    #text(weight: "bold", size: 13pt)[Step-by-Step Convergence]
    #v(4pt)
    #set text(size: 10.5pt)
    #table(
      columns: (auto, 1fr),
      inset: 5pt,
      stroke: 0.5pt + mid-gray,
      fill: (_, y) => if y == 0 { rgb("#333") } else if calc.rem(y, 2) == 0 { rgb("#f8f8f8") } else { white },
      table.header(
        text(fill: white, weight: "bold")[Round],
        text(fill: white, weight: "bold")[Discovery from Router A],
      ),
      [T=0], [B=3, C=23 (direct neighbors)],
      [T=1], [C=5 via B (3+2 < 23), D=28 via C],
      [T=2], [D=10 via B (3+2+5 < 28)],
      [T=3], [No changes - *converged*],
    )
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 6: SQL Challenge
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[SQL Recursive CTEs: The Challenge]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 18pt,
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + uni-red),
    )[
      #text(weight: "bold", size: 12pt, fill: uni-red)[The Problem]
      #v(4pt)
      #set text(size: 11pt)
      Standard SQL recursive CTEs are *append-only*:
      - `UNION ALL` adds new rows each iteration
      - Cannot update or delete existing rows
      - All possible walks are enumerated
      - Final `GROUP BY ... MIN(cost)` extracts answer

      #v(4pt)
      *Result:* Exponential row growth on dense graphs. SQLite exhausts memory beyond ~12 nodes.
    ]
  ],
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-teal),
    )[
      #text(weight: "bold", size: 12pt, fill: accent-teal)[What DVR Needs]
      #v(4pt)
      #set text(size: 11pt)
      A physical router's forwarding table:
      - *In-place updates:* overwrite when better route found
      - *Bounded size:* only O(V²) entries at any time
      - *Auto-termination:* stop when no improvement
      - *Per-key pruning:* one entry per (src, dst)
    ]

    #v(6pt)

    #accent-box(color: uni-red)[
      #set text(size: 10.5pt)
      *Core mismatch:* Standard recursion builds a growing set of paths. DVR requires a fixed-size table refined iteratively.
    ]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 7: USING KEY
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[DuckDB `USING KEY`: The Solution]
#footer-bar()

#set text(size: 11.5pt)

#accent-box(color: accent-teal)[
  *`WITH RECURSIVE ... USING KEY (from_node, to_node)`* - DuckDB's extension that designates columns as a unique key. During recursion, new rows with matching keys *replace* old rows instead of appending.
]

#v(4pt)

#grid(columns: (1fr, 1fr, 1fr), column-gutter: 10pt,
  block(
    width: 100%, inset: 9pt, radius: 3pt,
    fill: light-gray, stroke: (top: 3pt + accent-teal),
  )[
    #text(weight: "bold", size: 11.5pt)[In-Place Updates]
    #v(3pt)
    #set text(size: 10pt)
    Keying on `(from_node, to_node)` maintains one entry per router pair. Cheaper paths overwrite old entries.
  ],
  block(
    width: 100%, inset: 9pt, radius: 3pt,
    fill: light-gray, stroke: (top: 3pt + accent-blue),
  )[
    #text(weight: "bold", size: 11.5pt)[Bounded Memory Usage]
    #v(3pt)
    #set text(size: 10pt)
    Working set stays at O(V²) regardless of graph density. No walk explosion.
  ],
  block(
    width: 100%, inset: 9pt, radius: 3pt,
    fill: light-gray, stroke: (top: 3pt + uni-red),
  )[
    #text(weight: "bold", size: 11.5pt)[Automatic Fixpoint Detection]
    #v(3pt)
    #set text(size: 10pt)
    Recursion halts when delta set is empty. No explicit iteration bound needed.
  ],
)

#v(6pt)

#set text(size: 10.5pt)
#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  inset: 7pt,
  stroke: 0.5pt + mid-gray,
  fill: (_, y) => if y == 0 { rgb("#333") } else { white },
  table.header(
    text(fill: white, weight: "bold")[Memory Usage],
    text(fill: white, weight: "bold")[Walk Explosion],
    text(fill: white, weight: "bold")[Termination],
    text(fill: white, weight: "bold")[Post-Hoc Agg.],
  ),
  [*O(V²)*], [*None*], [*Automatic*], [*Not needed*],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 8: Side-by-side SQL
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Standard CTE vs Keyed CTE]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 12pt,
  [
    #text(size: 9pt, weight: "bold", fill: accent-blue, tracking: 1pt)[SQLITE: STANDARD CTE]
    #v(3pt)
    #code-block[
      ```sql
      WITH RECURSIVE bellman(s,t,cost,hop)
      AS (
        SELECT from_node, to_node,
               cost, to_node
        FROM edges
        UNION ALL
        SELECT b.s, e.to_node,
               b.cost + e.cost, b.hop
        FROM bellman b
        JOIN edges e ON b.t = e.from_node
        WHERE b.s <> e.to_node
      )
      -- POST-HOC aggregation required
      SELECT s, t, MIN(cost), hop
      FROM bellman GROUP BY s, t
      ```
    ]
  ],
  [
    #text(size: 9pt, weight: "bold", fill: accent-teal, tracking: 1pt)[DUCKDB: KEYED CTE]
    #v(3pt)
    #code-block[
      ```sql
      WITH RECURSIVE routing(s,t,cost,hop)
          USING KEY (s, t) AS (
        SELECT from_node, to_node,
               cost, to_node
        FROM edges
        UNION
        SELECT r.s, e.to_node,
               MIN(r.cost + e.cost),
               arg_min(r.hop,
                       r.cost + e.cost)
        FROM routing r
        JOIN edges e ON r.t = e.from_node
        WHERE r.s <> e.to_node
        GROUP BY r.s, e.to_node
      )
      SELECT * FROM routing
      ```
    ]
  ],
)

#v(4pt)

#accent-box(color: accent-teal)[
  #set text(size: 10pt)
  *Key difference:* Standard CTE uses `UNION ALL` (accumulates all walks), requiring final `GROUP BY`. DuckDB uses `UNION` + `USING KEY` (prunes in-place), keeping only the best cost per (s, t).
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 9: The Complete Query (Algorithmic Core)
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[The Algorithmic Core]
#footer-bar()

#grid(columns: (1.15fr, 0.85fr), column-gutter: 12pt,
  [
    #code-block[
      ```sql
      WITH RECURSIVE routing_table(
        from_node, to_node,
        best_cost, next_hop)
        USING KEY (from_node, to_node) AS (
        -- T=0: Direct neighbor discovery
        SELECT from_node, to_node,
               cost, to_node AS next_hop
        FROM edges
        UNION
        -- Bellman-Ford relaxation
        SELECT r.from_node, e.to_node,
          MIN(r.best_cost + e.cost),
          arg_min(r.next_hop,
                  r.best_cost + e.cost)
        FROM routing_table AS r
        JOIN edges AS e
          ON r.to_node = e.from_node
        LEFT JOIN recurring.routing_table
          AS ex ON ex.from_node = r.from_node
             AND ex.to_node = e.to_node
        WHERE r.from_node <> e.to_node
          AND (ex.best_cost IS NULL
            OR r.best_cost + e.cost
               < ex.best_cost)
        GROUP BY r.from_node, e.to_node
      )
      SELECT * FROM routing_table
      ORDER BY from_node, to_node;
      ```
    ]
  ],
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + uni-red),
    )[
      #text(weight: "bold", size: 12pt)[Line-by-Line]
      #v(3pt)
      #set text(size: 10pt)
      *`USING KEY`:* Stateful row updates
      #v(2pt)
      *Base case:* Direct neighbor costs
      #v(2pt)
      *`JOIN edges`:* Neighbor propagation
      #v(2pt)
      *`recurring.*`:* Accumulated FIB
      #v(2pt)
      *`IS NULL OR <`:* Relaxation condition
      #v(2pt)
      *`MIN` + `arg_min`:* Best advertisement
    ]

    #v(6pt)

    #accent-box(color: accent-teal)[
      #set text(size: 10pt)
      This single query replaces hundreds of lines of imperative routing code.
    ]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 10: Convergence Results
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Convergence Results: Full Network]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 16pt,
  [
    #set text(size: 10pt)
    #table(
      columns: (auto, auto, auto, auto),
      inset: 4pt,
      stroke: 0.5pt + mid-gray,
      fill: (_, y) => if y == 0 { rgb("#333") } else if calc.rem(y, 2) == 0 { rgb("#f8f8f8") } else { white },
      table.header(
        text(fill: white, weight: "bold")[From],
        text(fill: white, weight: "bold")[To],
        text(fill: white, weight: "bold")[Cost],
        text(fill: white, weight: "bold")[Next Hop],
      ),
      [A], [B], [*3*], [B],
      [A], [C], [*5*], [B],
      [A], [D], [*10*], [B],
      [B], [A], [*3*], [A],
      [B], [C], [*2*], [C],
      [B], [D], [*7*], [C],
      [C], [A], [*5*], [B],
      [C], [B], [*2*], [B],
      [C], [D], [*5*], [D],
      [D], [A], [*10*], [C],
      [D], [B], [*7*], [C],
      [D], [C], [*5*], [C],
    )
  ],
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-teal),
    )[
      #text(weight: "bold", size: 12pt)[Observations]
      #v(4pt)
      #set text(size: 11pt)
      - *A → C = 5 (via B):* Indirect A-B-C (3+2) beats direct (23)
      - *A → D = 10 (via B):* Multi-hop A-B-C-D
      - *Convergence:* 3 rounds for 4 nodes
      - All router pairs converge to the expected shortest paths
    ]

    #v(6pt)

    #block(
  width: 100%,
  height: 200pt,
  inset: 0pt,
  radius: 3pt,
  stroke: 0.8pt + mid-gray,
  clip: true,
)[
  #image(
    "2.phase.png",
    width: 100%,
    height: 100%,
    fit: "contain",
  )
]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 11: Network Failure
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Network Failure and Re-convergence]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 16pt,
  [
    #block(
      width: 100%, inset: 8pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + uni-red),
    )[
      #text(weight: "bold", size: 11pt, fill: uni-red)[Simulating Link Failure]
      #v(3pt)
      #code-block[
        ```sql
        DELETE FROM edges
        WHERE (from_node='B' AND to_node='C')
           OR (from_node='C' AND to_node='B');
        ```
      ]
      #v(2pt)
      #set text(size: 10pt)
      Re-running the *same query* discovers next-best paths automatically.
    ]

    #v(4pt)

    #set text(size: 10pt)
    #table(
  columns: (auto, auto, auto, auto),
  inset: 4pt,
  stroke: 0.5pt + mid-gray,

  table.header(
    [Route], [Before], [After], [Δ]
  ),

  [A → C], [5], [*6*], [#text(fill: uni-red)[+1]],
  [B → C], [2], [*9*], [#text(fill: uni-red)[+7]],
  [C → B], [2], [*9*], [#text(fill: uni-red)[+6]],
)
  ],
  [
#block(
  width: 100%,
  height: 220pt,
  inset: 0pt,
  radius: 3pt,
  stroke: 1pt + mid-gray,
  clip: true,
)[
  #image(
    "4.phase.png",
    width: 100%,
    height: 100%,
    fit: "contain",
  )
]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 12: Live Demo
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()

#set page(margin: 0pt)
#block(width: 100%, height: 100%, fill: dark-bg)[
  #place(top, block(width: 100%, height: 4pt,
    fill: gradient.linear(uni-red, accent-teal, accent-blue)))

  #pad(x: 2.2cm, y: 1.8cm)[
    #text(size: 10pt, fill: rgb("#888"), tracking: 1.5pt, weight: "medium")[
      INTERACTIVE DEMONSTRATION
    ]

    #v(6pt)

    #text(size: 32pt, weight: "bold", fill: white)[
      Live Demo
    ]

    #v(10pt)

#block(
  width: 100%,
  inset: 0pt,
  radius: 3pt,
  stroke: 1pt + mid-gray,
  clip: true,
)[
  #image(
    "live_demo.png",
    width: 100%,
    fit: "contain",
  )
]
  

    #v(12pt)

    #align(center)[
      #text(size: 14pt, fill: accent-teal, weight: "medium")[
        Interactive Streamlit Simulator
      ]
      #v(3pt)
      #text(size: 10pt, fill: rgb("#888"))[
        Streamlit - DuckDB - Pyvis - Plotly
      ]
    ]
  ]
]

#set page(margin: (x: 1.6cm, top: 1.2cm, bottom: 1.4cm))

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 13: Benchmark
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Benchmark Results]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 14pt,
  [
  #block(
  width: 100%,
  height: 150pt,
  inset: 0pt,
  radius: 1pt
)[
  #image(
    "execution_time.png",
    width: 100%,
    height: 100%,
    fit: "contain",
  )
]

    #v(4pt)

#block(
  width: 100%,
  height: 150pt,
  inset: 0pt,
  radius: 1pt
)[
  #image(
    "complexity_analysis.png",
    width: 100%,
    height: 100%,
    fit: "contain",
  )
]
  ],
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-teal),
    )[
      #text(weight: "bold", size: 12pt)[Key Findings]
      #v(4pt)
      #set text(size: 10.5pt)
      - DuckDB: *5-15x speedup* over SQLite
      - SQLite: *infeasible beyond ~12 nodes*
      - DuckDB: *polynomial scaling* O(V·E)
      - Python: validated reference baseline
    ]

    #v(4pt)

    #set text(size: 9.5pt)
    #table(
      columns: (1fr, auto, auto),
      inset: 4pt,
      stroke: 0.5pt + mid-gray,
      fill: (_, y) => if y == 0 { rgb("#333") } else { white },
      table.header(
        text(fill: white, weight: "bold")[Backend],
        text(fill: white, weight: "bold")[Complexity],
        text(fill: white, weight: "bold")[Max N],
      ),
      [DuckDB USING KEY], [O(V·E)], [50+],
      [SQLite Standard], [O(V·E·P)], [~11],
      [Python Bellman-Ford], [O(V²·E)], [50+],
      [Python Dijkstra], [O(V(V+E)logV)], [50+],
      [Python Floyd-Warshall], [O(V³)], [50+],
    )
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 14: Key Findings
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Key Findings]
#footer-bar()

#grid(columns: (1fr, 1fr, 1fr), column-gutter: 10pt,
  block(
    width: 100%, inset: 10pt, radius: 3pt,
    fill: light-gray, stroke: (top: 3pt + accent-teal),
  )[
    #text(weight: "bold", size: 12pt, fill: accent-teal)[1. SQL as an Algorithmic Language]
    #v(4pt)
    #set text(size: 10.5pt)
    SQL can fully implement distributed routing protocols. A single recursive query replaces hundreds of lines of imperative code.
  ],
  block(
    width: 100%, inset: 10pt, radius: 3pt,
    fill: light-gray, stroke: (top: 3pt + accent-blue),
  )[
    #text(weight: "bold", size: 12pt, fill: accent-blue)[2. State-Aware Recursion]
    #v(4pt)
    #set text(size: 10.5pt)
    Eliminates exponential path explosion. Working set bounded at O(V²). Achieves 5-15x speedup over SQLite.
  ],
  block(
    width: 100%, inset: 10pt, radius: 3pt,
    fill: light-gray, stroke: (top: 3pt + uni-red),
  )[
    #text(weight: "bold", size: 12pt, fill: uni-red)[3. Automatic Re-Convergence]
    #v(4pt)
    #set text(size: 10.5pt)
    Link failure via SQL `DELETE`; re-running the same query discovers next-best paths. No code changes needed.
  ],
)

#v(8pt)

#accent-box(color: accent-teal)[
  #set text(size: 11.5pt)
  *Central result:* Modern SQL is no longer "just for queries." With state-aware recursion, it is a first-class language for simulating and analyzing complex distributed protocols.
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 15: Conclusion & Future Work
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Conclusion and Future Work]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 16pt,
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-teal),
    )[
      #text(weight: "bold", size: 12pt)[Conclusion]
      #v(4pt)
      #set text(size: 11pt)
      - DuckDB's `USING KEY` provides a *1:1 mapping* between SQL recursion and router behavior
      - Built a complete *interactive evaluation suite* with 6 phases
      - Keyed CTEs maintain *polynomial scaling*; standard CTEs degrade exponentially
      - Declarative approach: *more concise* and *verifiably correct*
    ]
  ],
  [
    #block(
      width: 100%, inset: 10pt, radius: 3pt,
      fill: light-gray, stroke: (top: 3pt + accent-blue),
    )[
      #text(weight: "bold", size: 12pt)[Future Research]
      #v(4pt)
      #set text(size: 11pt)
      - *Path-Vector (BGP):* SQL array types for AS-path tracking
      - *Link-State (OSPF):* Dijkstra via recursive SQL
      - *Dynamic Traffic:* Real-time metrics in edges table
      - *Large-Scale:* Internet AS-graph convergence
    ]
  ],
)

#v(6pt)

#block(
  width: 100%, inset: 10pt, radius: 3pt,
  fill: rgb("#fafafa"), stroke: 0.5pt + mid-gray,
)[
  #set text(size: 10pt)
  *References:* \
  #set text(size: 9.5pt, fill: text-muted)
  [1] R. Bellman, "On a Routing Problem," _Q. Appl. Math._, 1958. \
  [2] DuckDB Documentation, "Recursive CTEs with USING KEY," 2026. \
  [3] A. S. Tanenbaum, _Computer Networks_, 6th ed., Pearson, 2021.
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 16: Thank You
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()

#set page(margin: 0pt)
#block(width: 100%, height: 100%, fill: dark-bg)[
  #place(top, block(width: 100%, height: 4pt,
    fill: gradient.linear(uni-red, accent-teal, accent-blue)))

  #align(center + horizon)[
    #pad(x: 2cm)[
      #text(size: 10pt, fill: rgb("#888"), tracking: 2pt, weight: "medium")[
        END OF PRESENTATION
      ]

      #v(12pt)

      #text(size: 38pt, weight: "bold", fill: white)[
        Thank You
      ]

      #v(6pt)

      #text(size: 17pt, fill: rgb("#ccc"))[
        Questions and Discussion
      ]

      #v(16pt)

      #line(length: 60pt, stroke: 1.5pt + uni-red)

      #v(12pt)

      #text(size: 12pt, fill: accent-teal)[Mehdi Hoseyni]
      #v(3pt)
      #text(size: 10pt, fill: rgb("#888"))[
        Database Systems Seminar - University of Tübingen - Summer 2026
      ]
    ]
  ]
]

#set page(margin: (x: 1.6cm, top: 1.2cm, bottom: 1.4cm))

// ═══════════════════════════════════════════════════════════════════════
// BACKUP SLIDES
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#set page(margin: 0pt)
#block(width: 100%, height: 100%, fill: rgb("#f0f0f0"))[
  #align(center + horizon)[
    #text(size: 26pt, weight: "bold", fill: text-muted)[Backup Slides]
    #v(3pt)
    #text(size: 12pt, fill: text-muted)[Additional material for discussion]
  ]
]

#set page(margin: (x: 1.6cm, top: 1.2cm, bottom: 1.4cm))

// BACKUP: Complexity Table
#pagebreak()
#slide-header[Complexity Comparison (Backup)]
#footer-bar()

#set text(size: 10pt)
#table(
  columns: (1.5fr, 1fr, auto, auto, auto),
  inset: 5pt,
  stroke: 0.5pt + mid-gray,
  fill: (_, y) => if y == 0 { rgb("#333") } else if calc.rem(y, 2) == 0 { rgb("#f8f8f8") } else { white },
  table.header(
    text(fill: white, weight: "bold")[Algorithm],
    text(fill: white, weight: "bold")[Time],
    text(fill: white, weight: "bold")[Space],
    text(fill: white, weight: "bold")[Distributed],
    text(fill: white, weight: "bold")[Neg. Weights],
  ),
  [Bellman-Ford], [O(V²·E)], [O(V²)], [Yes], [Yes],
  [Dijkstra (heap)], [O(V(V+E)log V)], [O(V²)], [No], [No],
  [Floyd-Warshall], [O(V³)], [O(V²)], [No], [Yes],
  [DuckDB USING KEY], [O(V·E)], [O(V²)], [N/A], [No],
  [SQLite Standard CTE], [O(V·E·P)], [O(V²·P)], [N/A], [No],
)

#v(6pt)

#accent-box(color: uni-red)[
  #set text(size: 10pt)
  *P = walk count:* In SQLite, P denotes distinct walks enumerated before the final GROUP BY. For dense graphs, P grows exponentially with |V|.
]

// BACKUP: CTE Semantic Comparison
#pagebreak()
#slide-header[CTE Semantic Comparison (Backup)]
#footer-bar()

#set text(size: 10pt)
#table(
  columns: (1fr, 1fr, 1fr),
  inset: 5pt,
  stroke: 0.5pt + mid-gray,
  fill: (_, y) => if y == 0 { rgb("#333") } else if calc.rem(y, 2) == 0 { rgb("#f8f8f8") } else { white },
  table.header(
    text(fill: white, weight: "bold")[Aspect],
    text(fill: white, weight: "bold")[Standard CTE (SQLite)],
    text(fill: white, weight: "bold")[Keyed CTE (DuckDB)],
  ),
  [*Recursion model*], [Append-only (UNION ALL)], [In-place update (UNION + KEY)],
  [*Working set*], [Grows each iteration], [Bounded at O(V²)],
  [*Row pruning*], [None during recursion], [Auto per-key minimum],
  [*Aggregation*], [Post-hoc GROUP BY], [Built into recursion],
  [*Termination*], [Explicit iteration bound], [Automatic (empty delta)],
  [*Memory*], [O(V²·P), P = walks], [O(V²)],
  [*Walk explosion*], [High (exponential)], [None (pruned by design)],
)
