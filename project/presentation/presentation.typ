// ═══════════════════════════════════════════════════════════════════════
// SQL as a Programming Language:
// Distance-Vector Routing with Recursive CTEs in DuckDB
//
// Mehdi Hosseini - Database Systems Seminar - University of Tübingen
// Summer Semester 2026
// ═══════════════════════════════════════════════════════════════════════

// ── Theme Configuration ──────────────────────────────────────────────
#let uni-red = rgb("#A51E37")
#let dark-bg = gradient.radial(rgb("#1e293b"), rgb("#0f172a"), radius: 75%)
#let light-bg = rgb("#fafbfc")
#let mid-gray = rgb("#cbd5e1")
#let border-gray = rgb("#e2e8f0")
#let card-bg = rgb("#fafafa")
#let text-dark = rgb("#0f172a")
#let text-muted = rgb("#64748b")

#set page(
  paper: "presentation-16-9",
  margin: (x: 1.6cm, top: 1.2cm, bottom: 1.4cm),
  fill: light-bg,
)

#set text(
  font: "Helvetica Neue",
  size: 16pt,
  fill: text-dark,
)

// ── Helper Functions ─────────────────────────────────────────────────

#let slide-header(title) = {
  block(width: 100%)[
    #text(size: 22pt, weight: "bold", fill: text-dark)[#title]
    #v(12pt)
    #block(width: 100%, height: 2pt)[
      #line(length: 100%, stroke: 0.5pt + mid-gray)
      #place(top + left, dy: -1pt)[
        #line(length: 45pt, stroke: 2.5pt + uni-red)
      ]
    ]
    #v(10pt)
  ]
}

#let footer-bar() = {
  place(bottom + left, dy: 0.8cm, dx: 0pt,
    block(width: 100%)[
      #line(length: 100%, stroke: 0.5pt + mid-gray)
      #v(2pt)
      #set text(size: 8pt, fill: text-muted)
      #grid(columns: (1fr, 1fr, 1fr),
        [Mehdi Hosseini | University of Tübingen],
        align(center)[Master Seminar: Database Systems],
        align(right)[#context counter(page).display("1 / 1", both: true)],
      )
    ]
  )
}

#let info-card(title: none, body, border-color: mid-gray) = {
  block(
    width: 100%,
    inset: 10pt,
    radius: 4pt,
    fill: card-bg,
    stroke: (left: 3.5pt + border-color, rest: 0.5pt + border-gray),
  )[
    #if title != none [
      #text(weight: "bold", size: 12pt, fill: text-dark)[#title]
      #v(4pt)
    ]
    #body
  ]
}

#let accent-box(body, color: uni-red) = {
  block(
    width: 100%,
    inset: 10pt,
    radius: 4pt,
    fill: color.lighten(94%),
    stroke: (left: 3.5pt + color, rest: 0.5pt + color.lighten(80%)),
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

#let code-window(title, height: auto, body) = {
  block(
    width: 100%,
    height: height,
    radius: 5pt,
    stroke: 0.5pt + rgb("#334155"),
    clip: true,
    fill: rgb("#0f172a"),
  )[
    #block(
      width: 100%,
      fill: rgb("#1e293b"),
      inset: (x: 8pt, y: 5pt),
      stroke: (bottom: 0.5pt + rgb("#334155")),
    )[
      #grid(
        columns: (1fr, auto),
        align: (left, right),
        [
          #box(circle(radius: 2.5pt, fill: rgb("#ff5f56")))
          #h(2pt)
          #box(circle(radius: 2.5pt, fill: rgb("#ffbd2e")))
          #h(2pt)
          #box(circle(radius: 2.5pt, fill: rgb("#27c93f")))
          #h(8pt)
          #text(size: 8pt, fill: rgb("#94a3b8"), font: "Menlo", weight: "bold")[#title]
        ],
        [
          #text(size: 7.5pt, fill: rgb("#64748b"), weight: "bold")[SQL]
        ]
      )
    ]
    #pad(x: 9pt, y: 7pt)[
      #set text(font: "Menlo", size: 8pt, fill: rgb("#f1f5f9"))
      #body
    ]
  ]
}

#let browser-window(body) = {
  block(
    width: 100%,
    radius: 5pt,
    stroke: 0.5pt + rgb("#cbd5e1"),
    clip: true,
    fill: white,
  )[
    #block(
      width: 100%,
      fill: rgb("#f1f5f9"),
      inset: (x: 8pt, y: 6pt),
      stroke: (bottom: 0.5pt + rgb("#cbd5e1")),
    )[
      #grid(
        columns: (1fr, 3fr, 1fr),
        align: (left, center, right),
        [
          #box(circle(radius: 2.5pt, fill: rgb("#ff5f56")))
          #h(2pt)
          #box(circle(radius: 2.5pt, fill: rgb("#ffbd2e")))
          #h(2pt)
          #box(circle(radius: 2.5pt, fill: rgb("#27c93f")))
        ],
        [
          #box(
            width: 85%,
            height: 12pt,
            fill: white,
            radius: 2pt,
            stroke: 0.5pt + rgb("#cbd5e1"),
            inset: (x: 5pt, y: 1pt),
          )[
            #align(left + horizon)[
              #text(size: 7pt, fill: rgb("#64748b"), font: "Menlo")[localhost:8501]
            ]
          ]
        ],
        []
      )
    ]
    #block(spacing: 0pt)[#body]
  ]
}

#let draw-node(name, x, y, radius: 14pt) = {
  place(top + left, dx: x - radius, dy: y - radius)[
    #circle(radius: radius, fill: white, stroke: 1.5pt + text-dark)[
      #align(center + horizon)[#text(fill: text-dark, weight: "bold", size: 10.5pt)[#name]]
    ]
  ]
}

#let draw-edge(x1, y1, x2, y2, label) = {
  place(top + left)[#line(start: (x1, y1), end: (x2, y2), stroke: 1.5pt + mid-gray)]
  place(top + left, dx: (x1 + x2)/2 - 7pt, dy: (y1 + y2)/2 - 7pt)[
    #box(fill: white, inset: 2pt, radius: 2pt)[
      #text(size: 9pt, weight: "bold", fill: text-dark)[#label]
    ]
  ]
}

#let outline-item(num, title) = {
  grid(
    columns: (auto, 1fr),
    column-gutter: 8pt,
    align: horizon,
    box(
      width: 18pt,
      height: 18pt,
      radius: 9pt,
      fill: uni-red,
      align(center + horizon)[#text(size: 9pt, fill: white, weight: "bold")[#num]]
    ),
    text(size: 11pt, weight: "bold", fill: text-dark)[#title]
  )
}

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 1: Title
// ═══════════════════════════════════════════════════════════════════════

#set page(margin: 0pt)
#block(width: 100%, height: 100%, fill: dark-bg)[
  #place(top, block(width: 100%, height: 4pt, fill: uni-red))

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
      #text(size: 18pt, fill: white.darken(10%))[
        Implementing Distance-Vector Routing#linebreak()with Recursive CTEs in DuckDB
      ]
    ]

    #v(1cm)
    #line(length: 80pt, stroke: 2pt + uni-red)
    #v(10pt)

    #text(size: 13pt, fill: rgb("#ccc"))[Mehdi Hosseini]
    #v(4pt)
    #text(size: 10pt, fill: rgb("#888"))[
      Master Seminar: Database Systems - Summer Semester 2026
    ]
  ]
]

#set page(margin: (x: 1.6cm, top: 1.2cm, bottom: 1.4cm))

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 2: Motivation
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Motivation]
#footer-bar()

#v(6pt)

#info-card(border-color: mid-gray)[
  #set text(size: 13pt)
  Can a declarative query language simulate a stateful, distributed network protocol?
]

#v(12pt)

#grid(columns: (1fr, 1fr), column-gutter: 18pt,
  block(height: 80pt)[
    #info-card(title: "The Challenge", border-color: mid-gray)[
      #set text(size: 11.5pt)
      - Standard recursive CTEs are *append-only*
      - DVR needs *in-place state updates*
    ]
  ],
  block(height: 80pt)[
    #accent-box(color: uni-red)[
      #text(weight: "bold", size: 11.5pt)[The Solution]
      #v(4pt)
      #set text(size: 11.5pt)
      DuckDB's `USING KEY` enables *stateful recursion* inside SQL
    ]
  ],
)



// ═══════════════════════════════════════════════════════════════════════
// SLIDE 4: DVR Protocol
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Distance-Vector Routing Protocol]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 18pt, row-gutter: 12pt,
  info-card(title: "Core Idea", border-color: mid-gray)[
    #set text(size: 11pt)
    - Each node maintains a *cost vector*
    - Neighbors *exchange* tables periodically
    - Costs refined when cheaper path found
  ],
  info-card(title: "Key Properties", border-color: mid-gray)[
    #set text(size: 11pt)
    - *Distributed:* No central coordinator
    - *Iterative:* Round-by-round updates
    - *Convergent:* Shortest paths in $<= |V| - 1$ steps
  ],
  info-card(title: "Algorithm Steps", border-color: mid-gray)[
    #set text(size: 11pt)
    - *T=0:* Direct neighbor discovery
    - *T=1:* First exchange and relaxation
    - *T>=2:* Repeat until fixpoint
  ],
  info-card(title: "Real-World Protocols", border-color: mid-gray)[
    #set text(size: 11pt)
    - *RIP:* Classic DVR (max 15 hops)
    - *EIGRP:* Cisco hybrid protocol
    - *BGP:* Internet path-vector routing
  ]
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 5: Bellman-Ford
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[The Bellman-Ford Equation]
#footer-bar()

#info-card(border-color: mid-gray)[
  #align(center)[
    #text(size: 18pt, font: "New Computer Modern")[
      $d(u, v) = min_(w in "Adj"(u)) { "cost"(u, w) + d(w, v) }$
    ]
  ]
]

#v(4pt)

#grid(columns: (1.1fr, 0.9fr), column-gutter: 18pt,
  info-card(title: "Example Network Topology", border-color: mid-gray)[
    #v(4pt)
    #align(center)[
      #block(width: 100%, height: 120pt)[
        #draw-edge(34pt, 24pt, 184pt, 24pt, "3") // A-B
        #draw-edge(34pt, 24pt, 34pt, 94pt, "23") // A-C
        #draw-edge(184pt, 24pt, 34pt, 94pt, "2") // B-C
        #draw-edge(34pt, 94pt, 184pt, 94pt, "5") // C-D
        
        #draw-node("A", 34pt, 24pt)
        #draw-node("B", 184pt, 24pt)
        #draw-node("C", 34pt, 94pt)
        #draw-node("D", 184pt, 94pt)
      ]
    ]
    #v(4pt)
    #set text(size: 10pt)
    Direct link A→C costs 23, but indirect path A→B→C costs only 3+2 = *5*.
  ],
  info-card(title: "Step-by-Step Convergence", border-color: mid-gray)[
    #v(4pt)
    #set text(size: 10.5pt)
    #table(
      columns: (auto, 1fr),
      inset: (x: 8pt, y: 6pt),
      stroke: (x, y) => if y == 0 { (bottom: 1.5pt + text-dark) } else { (bottom: 0.5pt + border-gray) },
      fill: none,
      table.header(
        text(weight: "bold")[Round],
        text(weight: "bold")[Discovery from Router A],
      ),
      [T=0], [B=3, C=23 (direct neighbors)],
      [T=1], [C=5 via B (3+2 < 23), D=28 via C],
      [T=2], [D=10 via B (3+2+5 < 28)],
      [T=3], [No changes - *converged*],
    )
  ]
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 6: SQL Challenge
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[SQL Recursive CTEs: The Challenge]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 18pt,
  info-card(title: "Standard SQL: The Problem", border-color: mid-gray)[
    #set text(size: 11pt)
    - *Append-only:* Rows accumulate via `UNION ALL`
    - *No updates:* Cannot modify rows mid-recursion
    - *Path explosion:* All walks enumerated
    - *Memory limit:* SQLite fails beyond ~11 nodes
  ],
  info-card(title: "DVR Requirement", border-color: mid-gray)[
    #set text(size: 11pt)
    - *In-place updates:* Overwrite with better paths
    - *Bounded state:* One route per pair, $O(V^2)$
    - *Fixpoint:* Stop when no more updates
  ]
)

#v(10pt)

#info-card(border-color: mid-gray)[
  #set text(size: 11pt)
  *Mismatch:* CTEs grow history; DVR needs fixed-size iterative refinement.
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 7: USING KEY
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[DuckDB `USING KEY`: The Solution]
#footer-bar()

#accent-box(color: uni-red)[
  #set text(size: 11.5pt)
  *`USING KEY (from_node, to_node)`*: Matching keys *replace* old rows instead of appending.
]

#v(8pt)

#grid(columns: (1fr, 1fr, 1fr), column-gutter: 12pt,
  info-card(title: "In-Place Updates", border-color: mid-gray)[
    #set text(size: 10pt)
    One entry per router pair. Cheaper paths overwrite.
  ],
  info-card(title: "Bounded Memory", border-color: mid-gray)[
    #set text(size: 10pt)
    Working set stays at $O(V^2)$. No walk explosion.
  ],
  info-card(title: "Auto Fixpoint", border-color: mid-gray)[
    #set text(size: 10pt)
    Halts when delta set is empty.
  ],
)

#v(10pt)

#align(center)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr),
    inset: (x: 10pt, y: 8pt),
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + text-dark) } else { (bottom: 0.5pt + border-gray) },
    fill: none,
    table.header(
      text(weight: "bold")[Memory Usage],
      text(weight: "bold")[Walk Explosion],
      text(weight: "bold")[Termination],
      text(weight: "bold")[Post-Hoc Agg.],
    ),
    [*O(V²)*], [*None*], [*Automatic*], [*Not needed*],
  )
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 8: Standard CTE vs Keyed CTE
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Standard CTE vs Keyed CTE]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 12pt,
  [
    #align(center)[
      #text(size: 11pt, weight: "bold", fill: text-dark)[SQLite: Standard (Append-Only)]
    ]
    #v(3pt)
    #code-window("sqlite_standard.sql", height: 230pt)[
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
    #align(center)[
      #text(size: 11pt, weight: "bold", fill: uni-red)[DuckDB: Keyed (USING KEY)]
    ]
    #v(3pt)
    #code-window("duckdb_keyed.sql", height: 230pt)[
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

#v(6pt)

#accent-box(color: uni-red)[
  #set text(size: 10pt)
  *Key Difference:* Standard CTEs accumulate all walks (post-hoc `GROUP BY`). `USING KEY` prunes *during* recursion.
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 9: The Algorithmic Core
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[The Algorithmic Core]
#footer-bar()

#grid(columns: (1.15fr, 0.85fr), column-gutter: 12pt,
  [
    #code-window("duckdb_dvr_simulation.sql")[
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
    #accent-box(color: uni-red)[
      #text(weight: "bold", size: 12pt)[Line-by-Line Review]
      #v(4pt)
      #set text(size: 10pt)
      - *`USING KEY`:* Stateful row updates.
      - *Base case:* Direct neighbor costs.
      - *`JOIN edges`:* Neighbor propagation.
      - *`recurring.*`:* Bounded state access.
      - *`IS NULL OR <`:* Relaxation condition.
      - *`MIN` + `arg_min`:* Select cheapest hop.
    ]

    #v(6pt)

    #info-card(border-color: mid-gray)[
      #set text(size: 10pt)
      One query replaces hundreds of lines of imperative code.
    ]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 10: Convergence Results
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Convergence Results: Full Network]
#footer-bar()

#grid(columns: (1fr, 1.1fr), column-gutter: 14pt,
  info-card(title: "Converged Forwarding Table", border-color: mid-gray)[
    #set text(size: 9pt)
    #table(
      columns: (1fr, 1fr, 1fr, 1.2fr),
      inset: (x: 6pt, y: 3.5pt),
      stroke: (x, y) => if y == 0 { (bottom: 1.5pt + text-dark) } else { (bottom: 0.5pt + border-gray) },
      fill: none,
      table.header(
        text(weight: "bold")[From],
        text(weight: "bold")[To],
        text(weight: "bold")[Cost],
        text(weight: "bold")[Next Hop],
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
    #info-card(title: "Observations", border-color: mid-gray)[
      #set text(size: 10pt)
      - *A→C = 5 (via B):* Indirect beats direct (23).
      - *A→D = 10 (via B):* Multi-hop path.
      - *Convergence:* 3 rounds for 4 nodes.
    ]

    #v(4pt)

    #browser-window[
      #image(
        "2.phase.png",
        width: 100%,
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

#grid(columns: (1.1fr, 0.9fr), column-gutter: 16pt,
  [
    #info-card(title: "Simulating Link Failure", border-color: mid-gray)[
      #v(2pt)
      #code-window("simulate_failure.sql")[
        ```sql
        DELETE FROM edges
        WHERE (from_node='B' AND to_node='C')
           OR (from_node='C' AND to_node='B');
        ```
      ]
      #v(4pt)
      #set text(size: 10pt)
      Re-run query to discover next-best paths.
    ]

    #v(6pt)

    #info-card(title: "Routing Table Shift", border-color: mid-gray)[
      #set text(size: 9.5pt)
      #table(
        columns: (1.2fr, 1fr, 1fr, 1fr),
        inset: (x: 8pt, y: 5pt),
        stroke: (x, y) => if y == 0 { (bottom: 1.5pt + text-dark) } else { (bottom: 0.5pt + border-gray) },
        fill: none,
        table.header(
          text(weight: "bold")[Route],
          text(weight: "bold")[Before],
          text(weight: "bold")[After],
          text(weight: "bold")[Δ],
        ),
        [A → C], [5], [*6*], [#text(fill: uni-red)[+1]],
        [B → C], [2], [*9*], [#text(fill: uni-red)[+7]],
        [C → B], [2], [*9*], [#text(fill: uni-red)[+7]],
      )
    ]
  ],
  [
    #v(10pt)
    #browser-window[
      #image(
        "4.phase.png",
        width: 100%,
        fit: "contain",
      )
    ]
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════════
// SLIDE 12: Live Demo
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()

#set page(margin: 0pt)
#block(width: 100%, height: 100%, fill: dark-bg)[
  #place(top, block(width: 100%, height: 4pt, fill: uni-red))

  #pad(x: 2.2cm, y: 1.4cm)[
    #text(size: 10pt, fill: rgb("#888"), tracking: 1.5pt, weight: "medium")[
      INTERACTIVE DEMONSTRATION
    ]

    #v(4pt)

    #text(size: 32pt, weight: "bold", fill: white)[
      Live Demo
    ]

    #v(8pt)

    #browser-window[
      #image(
        "live_demo.png",
        width: 100%,
        fit: "contain",
      )
    ]

    #v(8pt)

    #align(center)[
      #text(size: 13pt, fill: white, weight: "medium")[
        Interactive Streamlit Simulator
      ]
      #v(2pt)
      #text(size: 9pt, fill: rgb("#aaa"))[
        Streamlit #h(4pt) · #h(4pt) DuckDB #h(4pt) · #h(4pt) Pyvis #h(4pt) · #h(4pt) Plotly
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
    #align(center)[
      #image("execution_time.png", width: 100%, fit: "contain")
      #v(6pt)
      #image("complexity_analysis.png", width: 100%, fit: "contain")
    ]
  ],
  [
    #info-card(title: "Key Findings", border-color: mid-gray)[
      #set text(size: 10.5pt)
      - *DuckDB:* 5-15x faster than SQLite
      - *SQLite:* Fails beyond ~11 nodes
      - *DuckDB:* Polynomial $O(V dot E)$
      - *Python:* Baseline comparison
    ]

    #v(6pt)

    #set text(size: 9pt)
    #table(
      columns: (1.2fr, 1fr, 1fr),
      inset: (x: 6pt, y: 5.5pt),
      stroke: (x, y) => if y == 0 { (bottom: 1.5pt + text-dark) } else { (bottom: 0.5pt + border-gray) },
      fill: none,
      table.header(
        text(weight: "bold")[Backend],
        text(weight: "bold")[Complexity],
        text(weight: "bold")[Max N],
      ),
      [*DuckDB USING KEY*], [O(V·E)], [50+],
      [SQLite Standard], [O(V·E·P)], [~11],
      [Python Bellman-Ford], [O(V²·E)], [50+],
      [Python Dijkstra], [O(V(V+E)logV)], [50+],
      [Python Floyd-Warshall], [O(V³)], [50+],
    )
  ],
)

// ═══════════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════════
// SLIDE 14: Key Findings
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Key Findings]
#footer-bar()

#grid(columns: (1fr, 1fr, 1fr), column-gutter: 10pt,
  info-card(title: "1. SQL as Algorithm", border-color: mid-gray)[
    #set text(size: 10pt)
    One recursive query replaces hundreds of lines of imperative code.
  ],
  info-card(title: "2. State-Aware Recursion", border-color: mid-gray)[
    #set text(size: 10pt)
    No path explosion. $O(V^2)$ working set. 5-15x faster than SQLite.
  ],
  info-card(title: "3. Auto Re-Convergence", border-color: mid-gray)[
    #set text(size: 10pt)
    `DELETE` a link, re-run query. No code changes needed.
  ],
)

#v(10pt)

#accent-box(color: uni-red)[
  #set text(size: 11pt)
  *Central Result:* With `USING KEY`, SQL becomes a first-class language for simulating distributed protocols.
]

// ═══════════════════════════════════════════════════════════════════════
// SLIDE 15: Conclusion & Future Work
// ═══════════════════════════════════════════════════════════════════════

#pagebreak()
#slide-header[Conclusion and Future Work]
#footer-bar()

#grid(columns: (1fr, 1fr), column-gutter: 16pt,
  info-card(title: "Conclusion", border-color: mid-gray)[
    #set text(size: 10.5pt)
    - *1:1 mapping* between SQL recursion and router behavior
    - Interactive evaluation suite with 6 phases
    - Keyed CTEs: *polynomial*; standard CTEs: *exponential*
    - More concise and verifiably correct
  ],
  info-card(title: "Future Research", border-color: mid-gray)[
    #set text(size: 10.5pt)
    - *BGP:* Path-vector via SQL arrays
    - *OSPF:* Dijkstra in recursive SQL
    - *Dynamic Traffic:* Real-time edge metrics
    - *Large-Scale:* Internet AS-graph tests
  ],
)

#v(8pt)

#info-card(border-color: mid-gray)[
  #set text(size: 9.5pt)
  *References:* \
  #set text(size: 9pt, fill: text-muted)
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
  #place(top, block(width: 100%, height: 4pt, fill: uni-red))

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

      #text(size: 12pt, fill: white)[Mehdi Hosseini]
      #v(3pt)
      #text(size: 10pt, fill: rgb("#888"))[
        Database Systems Seminar - University of Tübingen - Summer 2026
      ]
    ]
  ]
]


