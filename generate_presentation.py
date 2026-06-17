import os
import sys
from pathlib import Path

# Check if weasyprint is installed
try:
    from weasyprint import HTML
    print("WeasyPrint loaded successfully.")
except ImportError:
    print("Installing weasyprint...")
    os.system(f"{sys.executable} -m pip install weasyprint")
    from weasyprint import HTML

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DVR Routing Presentation</title>
    <style>
        @page {
            size: 297mm 167.0625mm;
            margin: 0;
        }

        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #2D3238;
            margin: 0;
            padding: 0;
            background-color: #F8F9FA;
            -webkit-print-color-adjust: exact;
        }

        .slide {
            width: 297mm;
            height: 167.0625mm;
            box-sizing: border-box;
            padding: 20mm 25mm;
            position: relative;
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            overflow: hidden;
        }

        /* Dark theme slides */
        .dark-slide {
            background: linear-gradient(135deg, #0a0e1a 0%, #0f1729 60%, #111828 100%);
            color: #FFFFFF;
            justify-content: center;
            align-items: flex-start;
            text-align: left;
        }

        .dark-slide::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, #00D4AA 0%, #4A90D9 50%, #FFCC00 100%);
        }

        /* Light slide with subtle background */
        .light-slide {
            background: #FAFBFC;
        }

        .light-slide::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #00D4AA 0%, #4A90D9 50%, #FFCC00 100%);
        }

        .geometric-badge {
            position: absolute;
            top: 18mm;
            right: 25mm;
            width: 40px;
            height: 40px;
            border-top: 3px solid #00D4AA;
            border-right: 3px solid #00D4AA;
        }

        /* Typography */
        h1 {
            font-size: 48px;
            margin: 0 0 12px 0;
            font-weight: 700;
            letter-spacing: -1.5px;
            color: #FFFFFF;
            border-bottom: 3px solid #00D4AA;
            padding-bottom: 12px;
            width: 70%;
        }

        h2 {
            font-size: 28px;
            color: #111111;
            margin: 0 0 18px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 700;
        }

        h2::after {
            content: "";
            display: block;
            width: 50px;
            height: 3px;
            background-color: #00D4AA;
            margin-top: 6px;
        }

        h3 {
            margin: 0 0 10px 0;
            color: #111111;
            font-size: 17px;
            font-weight: 600;
        }

        p.subtitle {
            font-size: 20px;
            color: #00D4AA;
            margin: 0 0 30px 0;
            font-weight: 400;
            letter-spacing: 0.3px;
            width: 80%;
        }

        /* Layouts */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            align-items: start;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 18px;
            align-items: start;
        }

        .grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            align-items: start;
        }

        .asymmetric-layout {
            display: grid;
            grid-template-columns: 1.3fr 0.7fr;
            gap: 30px;
        }

        .row-layout {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .row-item {
            background: #FFFFFF;
            padding: 14px 20px;
            border-radius: 4px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.04);
            border-left: 4px solid #111111;
        }

        /* Cards */
        .card {
            background: #FFFFFF;
            padding: 18px;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border-top: 3px solid #111111;
        }

        .card.accent-card { border-top-color: #00D4AA; }
        .card.gold-card { border-top-color: #FFCC00; }
        .card.blue-card { border-top-color: #4A90D9; }
        .card.red-card { border-top-color: #E74C3C; }

        /* Lists */
        ul {
            margin: 0;
            padding-left: 18px;
        }

        li {
            font-size: 14px;
            line-height: 1.55;
            color: #333333;
            margin-bottom: 8px;
        }

        li strong { color: #111111; font-weight: 600; }

        /* Code blocks */
        .code-block {
            background: #1a1f2e;
            border: 1px solid rgba(0,212,170,0.25);
            border-left: 3px solid #00D4AA;
            border-radius: 6px;
            padding: 14px 16px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 11px;
            line-height: 1.5;
            color: #c9d1d9;
            white-space: pre;
            overflow: hidden;
        }

        .code-block .keyword { color: #569CD6; font-weight: bold; }
        .code-block .comment { color: #6A9955; }
        .code-block .function { color: #DCDCAA; }
        .code-block .string { color: #CE9178; }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 8px;
        }

        th {
            background: #111111;
            color: white;
            padding: 8px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 7px 12px;
            border-bottom: 1px solid #E5E5E5;
            color: #333;
        }

        tr:nth-child(even) td {
            background: #F8F9FA;
        }

        /* Image placeholder */
        .image-placeholder {
            width: 100%;
            height: 85mm;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #f0f2f5 0%, #e8edf2 100%);
            border: 2px dashed #C0C5CC;
            border-radius: 6px;
            margin-top: 8px;
            color: #888;
            font-size: 14px;
            font-weight: 500;
            text-align: center;
        }

        .image-placeholder.small {
            height: 60mm;
        }

        /* Equation block */
        .equation {
            background: #f8f9fa;
            border: 1px solid #e0e3e6;
            border-radius: 6px;
            padding: 14px 20px;
            font-family: 'Times New Roman', serif;
            font-size: 18px;
            text-align: center;
            color: #222;
            margin: 10px 0;
        }

        /* Agenda */
        .agenda-list {
            list-style: none;
            padding: 0;
            width: 80%;
        }

        .agenda-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 7px 0;
            border-bottom: 1px solid #E5E5E5;
            font-size: 15px;
            color: #2D3238;
        }

        .agenda-name { font-weight: 600; }
        .agenda-page { color: #00D4AA; font-weight: 700; font-size: 13px; }

        /* Highlight box */
        .highlight-box {
            background: rgba(0,212,170,0.08);
            border: 1px solid rgba(0,212,170,0.25);
            border-left: 4px solid #00D4AA;
            border-radius: 4px;
            padding: 12px 16px;
            font-size: 13px;
            color: #333;
            margin-top: 10px;
        }

        .warning-box {
            background: rgba(255,204,0,0.08);
            border: 1px solid rgba(255,204,0,0.25);
            border-left: 4px solid #FFCC00;
            border-radius: 4px;
            padding: 12px 16px;
            font-size: 13px;
            color: #333;
            margin-top: 10px;
        }

        /* Page number */
        .page-number {
            position: absolute;
            bottom: 10mm;
            right: 25mm;
            font-size: 10px;
            color: #A0A5AA;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .page-number::before {
            content: counter(page);
        }

        .footer-tag {
            position: absolute;
            bottom: 10mm;
            left: 25mm;
            font-size: 10px;
            color: #A0A5AA;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }

        .footer-tag::before {
            content: "";
            display: inline-block;
            width: 7px;
            height: 7px;
            background-color: #00D4AA;
            margin-right: 7px;
        }

        /* Final slide */
        .end-box {
            background: rgba(0,212,170,0.12);
            border: 1px solid #00D4AA;
            color: #00D4AA;
            padding: 5px 14px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
            border-radius: 4px;
            margin-bottom: 20px;
            display: inline-block;
        }

        .metric-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 10px;
        }

        .metric-box {
            text-align: center;
            background: #FFFFFF;
            border-radius: 4px;
            padding: 12px 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border-top: 3px solid #00D4AA;
        }

        .metric-box .value {
            font-size: 28px;
            font-weight: 700;
            color: #00D4AA;
        }

        .metric-box .label {
            font-size: 10px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 3px;
        }

        .metric-box.gold { border-top-color: #FFCC00; }
        .metric-box.gold .value { color: #FFCC00; }
        .metric-box.blue { border-top-color: #4A90D9; }
        .metric-box.blue .value { color: #4A90D9; }
        .metric-box.red { border-top-color: #E74C3C; }
        .metric-box.red .value { color: #E74C3C; }
    </style>
</head>
<body>

    <!-- ═══════════════════ SLIDE 1: TITLE ═══════════════════ -->
    <div class="slide dark-slide">
        <h1>SQL as a Programming Language</h1>
        <p class="subtitle">Implementing Distance-Vector Routing with Recursive CTEs in DuckDB</p>
        <p style="color: #A0A5AA; font-size: 14px; margin: 0; font-weight: 500; letter-spacing: 0.5px;">
            Mehdi Hoseyni &nbsp;&bull;&nbsp; Database Systems Seminar &nbsp;&bull;&nbsp; University of Tubingen
        </p>
        <p style="color: rgba(255,255,255,0.3); font-size: 12px; margin-top: 8px; letter-spacing: 0.3px;">
            Summer Semester 2026
        </p>
    </div>

    <!-- ═══════════════════ SLIDE 2: AGENDA ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Agenda</h2>
        <div style="margin-top: 10px;">
            <ul class="agenda-list">
                <li class="agenda-item"><span class="agenda-name">01. Motivation and Research Question</span><span class="agenda-page">p. 3</span></li>
                <li class="agenda-item"><span class="agenda-name">02. Distance-Vector Routing Theory</span><span class="agenda-page">p. 4</span></li>
                <li class="agenda-item"><span class="agenda-name">03. SQL Recursive CTEs: The Challenge</span><span class="agenda-page">p. 5</span></li>
                <li class="agenda-item"><span class="agenda-name">04. DuckDB USING KEY: The Innovation</span><span class="agenda-page">p. 6</span></li>
                <li class="agenda-item"><span class="agenda-name">05. Standard CTE vs Keyed CTE</span><span class="agenda-page">p. 7</span></li>
                <li class="agenda-item"><span class="agenda-name">06. Implementation: The Complete Query</span><span class="agenda-page">p. 8</span></li>
                <li class="agenda-item"><span class="agenda-name">07. Convergence Results</span><span class="agenda-page">p. 9-10</span></li>
                <li class="agenda-item"><span class="agenda-name">08. Network Failure and Re-convergence</span><span class="agenda-page">p. 11</span></li>
                <li class="agenda-item"><span class="agenda-name">09. Live Demo: Interactive Simulator</span><span class="agenda-page">p. 12</span></li>
                <li class="agenda-item"><span class="agenda-name">10. Benchmark Results</span><span class="agenda-page">p. 13-14</span></li>
                <li class="agenda-item"><span class="agenda-name">11. Key Findings and Conclusion</span><span class="agenda-page">p. 15-16</span></li>
            </ul>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 3: MOTIVATION ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Motivation and Research Question</h2>
        <div class="grid-2" style="margin-top: 8px;">
            <div class="card accent-card">
                <h3>Research Question</h3>
                <ul>
                    <li><strong>Core Question:</strong> Can SQL serve as a first-class programming language for complex algorithmic simulation?</li>
                    <li><strong>Approach:</strong> Implement the Distance-Vector Routing protocol entirely within SQL, using DuckDB's recursive CTEs.</li>
                    <li><strong>Goal:</strong> Prove that declarative logic with state-aware recursion can achieve global optimization through local updates.</li>
                </ul>
            </div>
            <div class="card blue-card">
                <h3>Why It Matters</h3>
                <ul>
                    <li><strong>Traditional View:</strong> SQL is seen as a data retrieval language, not suitable for algorithmic modeling.</li>
                    <li><strong>Our Claim:</strong> Modern SQL extensions (recursive CTEs, USING KEY) enable full simulation of distributed systems.</li>
                    <li><strong>Implication:</strong> Database engines can function as high-level environments for protocol validation.</li>
                </ul>
            </div>
        </div>
        <div class="highlight-box">
            <strong>Thesis Statement:</strong> Modern SQL, specifically through state-aware recursive CTEs, provides a robust framework for simulating complex distributed algorithms. DuckDB's <code>USING KEY</code> syntax allows a 1:1 conceptual mapping to physical router behavior.
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 4: DVR THEORY ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Distance-Vector Routing Theory</h2>
        <div class="asymmetric-layout" style="margin-top: 5px;">
            <div>
                <div class="card accent-card" style="margin-bottom: 12px;">
                    <h3>The Protocol</h3>
                    <ul>
                        <li><strong>Distributed Algorithm:</strong> Each router maintains a distance vector of costs to all destinations.</li>
                        <li><strong>Local Knowledge Only:</strong> Routers share tables only with immediate neighbors.</li>
                        <li><strong>Iterative Convergence:</strong> Updates repeat until all routers agree on optimal paths.</li>
                        <li><strong>"Routing by Rumor":</strong> Each router trusts its neighbor's advertised distances.</li>
                    </ul>
                </div>
                <div class="equation">
                    <em>d(u, v) = min<sub>w &isin; Adj(u)</sub> { cost(u, w) + d(w, v) }</em>
                </div>
                <p style="font-size: 11px; color: #888; text-align: center; margin-top: 4px;">The Bellman-Ford relaxation equation</p>
            </div>
            <div>
                <div class="card" style="margin-bottom: 12px;">
                    <h3>Convergence Process</h3>
                    <table>
                        <tr><th>Phase</th><th>Action</th></tr>
                        <tr><td>T = 0</td><td>Each router knows direct neighbors only</td></tr>
                        <tr><td>T = 1</td><td>Share tables with neighbors, update if cheaper path found</td></tr>
                        <tr><td>T = 2</td><td>Repeat relaxation; discover indirect paths</td></tr>
                        <tr><td>T = k</td><td>Convergence: no more improvements possible</td></tr>
                    </table>
                </div>
                <div class="highlight-box" style="font-size: 12px;">
                    <strong>Guarantee:</strong> Converges in at most |V| - 1 rounds for a graph with |V| vertices (no negative cycles).
                </div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 5: SQL CTEs CHALLENGE ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>SQL Recursive CTEs: The Challenge</h2>
        <div class="grid-2" style="margin-top: 8px;">
            <div>
                <div class="card red-card">
                    <h3>Standard CTE Problem</h3>
                    <ul>
                        <li><strong>Append-Only Semantics:</strong> Standard SQL recursive CTEs can only add new rows, never update existing ones.</li>
                        <li><strong>Path Explosion:</strong> Every possible walk is enumerated, leading to exponential row growth in dense graphs.</li>
                        <li><strong>Post-Hoc Aggregation:</strong> A final <code>GROUP BY ... MIN(cost)</code> is required to extract optimal paths.</li>
                        <li><strong>Scalability Limit:</strong> Networks beyond ~12 nodes cause SQLite to exhaust disk/memory.</li>
                    </ul>
                </div>
            </div>
            <div>
                <div class="card accent-card">
                    <h3>What Routing Needs</h3>
                    <ul>
                        <li><strong>In-Place Updates:</strong> Routers overwrite their tables when a better route arrives.</li>
                        <li><strong>Bounded Working Set:</strong> Only O(V&sup2;) entries should exist at any time.</li>
                        <li><strong>Automatic Termination:</strong> Stop when no improvement is possible, not after a fixed iteration count.</li>
                        <li><strong>Key-Based Pruning:</strong> Maintain only the best cost per (source, destination) pair.</li>
                    </ul>
                </div>
                <div class="warning-box" style="font-size: 12px; margin-top: 10px;">
                    <strong>Core Mismatch:</strong> Standard SQL recursion builds a growing set of paths. DVR requires a fixed-size table that is refined iteratively. This is the fundamental tension this work resolves.
                </div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 6: USING KEY ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>DuckDB USING KEY: The Innovation</h2>
        <div class="row-layout" style="margin-top: 8px;">
            <div class="row-item" style="border-left-color: #FFCC00;">
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #333;">
                    <strong style="color: #111;">What is USING KEY?</strong> &mdash;
                    DuckDB's proprietary extension to <code>WITH RECURSIVE</code> that designates columns as a unique key. During recursion, if a new row has the same key as an existing row, it <em>replaces</em> the old row instead of appending alongside it.
                </p>
            </div>
            <div class="row-item" style="border-left-color: #00D4AA;">
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #333;">
                    <strong style="color: #111;">Why It Matters for Routing:</strong> &mdash;
                    By keying on <code>(from_node, to_node)</code>, DuckDB maintains exactly one entry per router pair. When a cheaper path is discovered, it overwrites the old entry in-place. This is exactly how a physical router's forwarding table works.
                </p>
            </div>
            <div class="row-item" style="border-left-color: #4A90D9;">
                <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #333;">
                    <strong style="color: #111;">Automatic Termination:</strong> &mdash;
                    The recursion halts when no row produces an improvement (the delta set is empty). No explicit iteration bound is needed. This mirrors the natural convergence behavior of the Bellman-Ford algorithm.
                </p>
            </div>
        </div>
        <div class="metric-strip">
            <div class="metric-box">
                <div class="value">O(V&sup2;)</div>
                <div class="label">Working Set Size</div>
            </div>
            <div class="metric-box gold">
                <div class="value">0</div>
                <div class="label">Walk Explosion Risk</div>
            </div>
            <div class="metric-box blue">
                <div class="value">Auto</div>
                <div class="label">Termination</div>
            </div>
            <div class="metric-box red">
                <div class="value">None</div>
                <div class="label">Post-Hoc Aggregation</div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 7: CTE COMPARISON ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Standard CTE vs Keyed CTE</h2>
        <div class="grid-2" style="margin-top: 5px;">
            <div>
                <p style="font-size: 12px; font-weight: 700; color: #4A90D9; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 6px 0;">SQLite: Standard CTE</p>
                <div class="code-block" style="font-size: 10px; border-left-color: #4A90D9;">
<span class="keyword">WITH RECURSIVE</span> bellman(s, t, cost, hop, iter) <span class="keyword">AS</span> (
  <span class="comment">-- Base: direct edges</span>
  <span class="keyword">SELECT</span> from_node, to_node, cost, to_node, 0
  <span class="keyword">FROM</span> edges

  <span class="keyword">UNION ALL</span>

  <span class="comment">-- Recursive: extend paths</span>
  <span class="keyword">SELECT</span> b.s, e.to_node,
         b.cost + e.cost, b.hop, b.iter + 1
  <span class="keyword">FROM</span> bellman b
  <span class="keyword">JOIN</span> edges e <span class="keyword">ON</span> b.t = e.from_node
  <span class="keyword">WHERE</span> b.s &lt;&gt; e.to_node
    <span class="keyword">AND</span> b.iter &lt; |V| - 1
)
<span class="comment">-- POST-HOC aggregation required</span>
<span class="keyword">SELECT</span> s, t, <span class="function">MIN</span>(cost), hop
<span class="keyword">FROM</span> bellman <span class="keyword">GROUP BY</span> s, t</div>
            </div>
            <div>
                <p style="font-size: 12px; font-weight: 700; color: #FFCC00; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 6px 0;">DuckDB: Keyed CTE</p>
                <div class="code-block" style="font-size: 10px; border-left-color: #FFCC00;">
<span class="keyword">WITH RECURSIVE</span> routing(s, t, cost, hop)
    <span class="keyword">USING KEY</span> (s, t) <span class="keyword">AS</span> (
  <span class="comment">-- Base: direct edges</span>
  <span class="keyword">SELECT</span> from_node, to_node, cost, to_node
  <span class="keyword">FROM</span> edges

  <span class="keyword">UNION</span>

  <span class="comment">-- Recursive: Bellman-Ford relaxation</span>
  <span class="keyword">SELECT</span> r.s, e.to_node,
         <span class="function">MIN</span>(r.cost + e.cost),
         <span class="function">arg_min</span>(r.hop, r.cost + e.cost)
  <span class="keyword">FROM</span> routing r
  <span class="keyword">JOIN</span> edges e <span class="keyword">ON</span> r.t = e.from_node
  <span class="keyword">WHERE</span> r.s &lt;&gt; e.to_node
    <span class="keyword">AND</span> r.cost + e.cost &lt; existing.cost
  <span class="keyword">GROUP BY</span> r.s, e.to_node
)
<span class="comment">-- No post-hoc aggregation needed</span>
<span class="keyword">SELECT</span> * <span class="keyword">FROM</span> routing</div>
            </div>
        </div>
        <div class="highlight-box" style="margin-top: 8px;">
            <strong>Key Difference:</strong> The standard CTE accumulates all walks (UNION ALL), requiring a final GROUP BY. DuckDB's USING KEY prunes suboptimal entries during recursion (UNION), keeping only the best cost per (s, t) pair at all times.
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 8: IMPLEMENTATION ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Implementation: The Complete Query</h2>
        <div class="asymmetric-layout" style="margin-top: 5px;">
            <div>
                <div class="code-block" style="font-size: 10.5px; line-height: 1.55;">
<span class="comment">-- Network topology definition</span>
<span class="keyword">CREATE TABLE</span> edges (
    from_node <span class="keyword">TEXT</span>,
    to_node   <span class="keyword">TEXT</span>,
    cost      <span class="keyword">INTEGER</span>
);

<span class="keyword">INSERT INTO</span> edges <span class="keyword">VALUES</span>
    (<span class="string">'A'</span>,<span class="string">'B'</span>,3), (<span class="string">'B'</span>,<span class="string">'A'</span>,3),
    (<span class="string">'A'</span>,<span class="string">'C'</span>,23),(<span class="string">'C'</span>,<span class="string">'A'</span>,23),
    (<span class="string">'B'</span>,<span class="string">'C'</span>,2), (<span class="string">'C'</span>,<span class="string">'B'</span>,2),
    (<span class="string">'C'</span>,<span class="string">'D'</span>,5), (<span class="string">'D'</span>,<span class="string">'C'</span>,5);

<span class="comment">-- Distance-Vector Routing via USING KEY</span>
<span class="keyword">WITH RECURSIVE</span> routing_table(
    from_node, to_node, best_cost, next_hop)
    <span class="keyword">USING KEY</span> (from_node, to_node) <span class="keyword">AS</span> (

    <span class="comment">-- BASE: Direct neighbors (T=0)</span>
    <span class="keyword">SELECT</span> from_node, to_node,
           cost <span class="keyword">AS</span> best_cost,
           to_node <span class="keyword">AS</span> next_hop
    <span class="keyword">FROM</span> edges

    <span class="keyword">UNION</span>

    <span class="comment">-- RECURSIVE: Bellman-Ford relaxation</span>
    <span class="keyword">SELECT</span> r.from_node, e.to_node,
      <span class="function">MIN</span>(r.best_cost + e.cost),
      <span class="function">arg_min</span>(r.next_hop,
              r.best_cost + e.cost)
    <span class="keyword">FROM</span> routing_table <span class="keyword">AS</span> r
    <span class="keyword">JOIN</span> edges <span class="keyword">AS</span> e
      <span class="keyword">ON</span> r.to_node = e.from_node
    <span class="keyword">LEFT JOIN</span> recurring.routing_table
      <span class="keyword">AS</span> existing
      <span class="keyword">ON</span> existing.from_node = r.from_node
     <span class="keyword">AND</span> existing.to_node = e.to_node
    <span class="keyword">WHERE</span> r.from_node &lt;&gt; e.to_node
      <span class="keyword">AND</span> (existing.best_cost <span class="keyword">IS NULL</span>
        <span class="keyword">OR</span> r.best_cost + e.cost
           &lt; existing.best_cost)
    <span class="keyword">GROUP BY</span> r.from_node, e.to_node
)
<span class="keyword">SELECT</span> * <span class="keyword">FROM</span> routing_table
<span class="keyword">ORDER BY</span> from_node, to_node;</div>
            </div>
            <div>
                <div class="card accent-card" style="margin-bottom: 10px;">
                    <h3>Line-by-Line Breakdown</h3>
                    <ul style="font-size: 12px;">
                        <li><strong>USING KEY (from_node, to_node):</strong> Defines stateful iteration; rows are updated, not appended.</li>
                        <li><strong>Base Case:</strong> Populates direct neighbor costs (T=0 discovery).</li>
                        <li><strong>JOIN edges:</strong> Simulates information propagation between neighbors.</li>
                        <li><strong>recurring.routing_table:</strong> References the accumulated FIB state.</li>
                        <li><strong>WHERE ... IS NULL OR &lt;:</strong> Bellman-Ford relaxation condition.</li>
                        <li><strong>MIN + arg_min:</strong> Selects the lowest-cost advertisement per round.</li>
                    </ul>
                </div>
                <div class="card" style="padding: 12px;">
                    <h3>Network Topology</h3>
                    <p style="font-size: 14px; text-align: center; color: #555; margin: 5px 0; font-family: monospace; line-height: 1.8;">
                        A &mdash;&mdash; 3 &mdash;&mdash; B<br>
                        |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br>
                        23&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2<br>
                        |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|<br>
                        C &mdash;&mdash; 5 &mdash;&mdash; D
                    </p>
                </div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 9: CONVERGENCE RESULTS ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Convergence Results: Full Network</h2>
        <div class="grid-2" style="margin-top: 5px;">
            <div>
                <div class="card accent-card">
                    <h3>Converged Routing Table (Full Network)</h3>
                    <table>
                        <tr><th>From</th><th>To</th><th>Best Cost</th><th>Next Hop</th></tr>
                        <tr><td>A</td><td>B</td><td><strong>3</strong></td><td>B</td></tr>
                        <tr><td>A</td><td>C</td><td><strong>5</strong></td><td>B</td></tr>
                        <tr><td>A</td><td>D</td><td><strong>10</strong></td><td>B</td></tr>
                        <tr><td>B</td><td>A</td><td><strong>3</strong></td><td>A</td></tr>
                        <tr><td>B</td><td>C</td><td><strong>2</strong></td><td>C</td></tr>
                        <tr><td>B</td><td>D</td><td><strong>7</strong></td><td>C</td></tr>
                        <tr><td>C</td><td>A</td><td><strong>5</strong></td><td>B</td></tr>
                        <tr><td>C</td><td>B</td><td><strong>2</strong></td><td>B</td></tr>
                        <tr><td>C</td><td>D</td><td><strong>5</strong></td><td>D</td></tr>
                        <tr><td>D</td><td>A</td><td><strong>10</strong></td><td>C</td></tr>
                        <tr><td>D</td><td>B</td><td><strong>7</strong></td><td>C</td></tr>
                        <tr><td>D</td><td>C</td><td><strong>5</strong></td><td>C</td></tr>
                    </table>
                </div>
            </div>
            <div>
                <div class="card" style="margin-bottom: 12px;">
                    <h3>Observations</h3>
                    <ul>
                        <li><strong>A to C = 5 (via B):</strong> The algorithm discovers the indirect path A-B-C (cost 3+2=5) is cheaper than the direct link A-C (cost 23).</li>
                        <li><strong>A to D = 10 (via B):</strong> Path A-B-C-D (3+2+5=10) is optimal.</li>
                        <li><strong>Convergence:</strong> Achieved in 3 rounds for this 4-node network.</li>
                    </ul>
                </div>
                <div class="image-placeholder small">
                    [INSERT SCREENSHOT]<br>
                    Streamlit Phase 2: Graph visualization<br>
                    showing green shortest path overlay
                </div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 10: DISTANCE MATRIX ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Distance Matrix and Convergence Evolution</h2>
        <div class="grid-2" style="margin-top: 5px;">
            <div>
                <div class="image-placeholder" style="height: 55mm;">
                    [INSERT SCREENSHOT]<br>
                    Streamlit Phase 2: Distance Matrix D*[s][t]<br>
                    heatmap from the "Distance Matrix" tab
                </div>
                <div class="highlight-box" style="font-size: 12px; margin-top: 8px;">
                    The distance matrix D*[i][j] shows the converged optimal cost from every source to every destination. Diagonal entries are zero.
                </div>
            </div>
            <div>
                <div class="image-placeholder" style="height: 55mm;">
                    [INSERT SCREENSHOT]<br>
                    Streamlit Phase 2: Convergence Evolution<br>
                    chart (FIB growth + updates per round)
                </div>
                <div class="highlight-box" style="font-size: 12px; margin-top: 8px;">
                    The convergence chart tracks FIB size growth and the number of updates per iteration. Convergence is achieved when updates reach zero.
                </div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 11: FAILURE & RECONVERGENCE ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Network Failure and Re-convergence</h2>
        <div class="asymmetric-layout" style="margin-top: 5px;">
            <div>
                <div class="card red-card" style="margin-bottom: 10px;">
                    <h3>Simulating Link Failure</h3>
                    <div class="code-block" style="font-size: 11px; border-left-color: #E74C3C;">
<span class="keyword">DELETE FROM</span> edges
<span class="keyword">WHERE</span> (from_node = <span class="string">'B'</span> <span class="keyword">AND</span> to_node = <span class="string">'C'</span>)
   <span class="keyword">OR</span> (from_node = <span class="string">'C'</span> <span class="keyword">AND</span> to_node = <span class="string">'B'</span>);</div>
                    <p style="font-size: 13px; color: #555; margin: 8px 0 0 0;">
                        By deleting the B-C edge and re-running the <em>same</em> recursive query, the algorithm automatically re-converges to the next-best paths.
                    </p>
                </div>
                <div class="card" style="padding: 12px;">
                    <h3>Key Re-convergence Changes</h3>
                    <table>
                        <tr><th>Route</th><th>Before</th><th>After</th><th>Delta</th></tr>
                        <tr><td>A &rarr; C</td><td>5 (via B)</td><td style="color: #E74C3C; font-weight:700;">23 (direct)</td><td style="color:#E74C3C;">+18</td></tr>
                        <tr><td>A &rarr; D</td><td>10 (via B)</td><td style="color: #E74C3C; font-weight:700;">28 (via C)</td><td style="color:#E74C3C;">+18</td></tr>
                        <tr><td>B &rarr; C</td><td>2 (direct)</td><td style="color: #E74C3C; font-weight:700;">26 (via A)</td><td style="color:#E74C3C;">+24</td></tr>
                        <tr><td>C &rarr; D</td><td>5 (direct)</td><td>5 (direct)</td><td style="color:#00D4AA;">0</td></tr>
                    </table>
                </div>
            </div>
            <div>
                <div class="image-placeholder" style="height: 95mm;">
                    [INSERT SCREENSHOT]<br>
                    Streamlit Phase 4: Side-by-side<br>
                    before/after graph comparison +<br>
                    cost impact analysis bar chart
                </div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 12: LIVE DEMO ═══════════════════ -->
    <div class="slide dark-slide" style="justify-content: flex-start; padding-top: 22mm;">
        <div class="page-number" style="color: rgba(255,255,255,0.3);"></div>
        <h2 style="color: #FFFFFF; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; font-size: 26px;">Live Demo: Interactive Simulator</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 5px;">
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 15px; height: 70mm; display: flex; justify-content: center; align-items: center; color: rgba(255,255,255,0.4); text-align: center; font-size: 13px;">
                [INSERT SCREENSHOT]<br><br>
                Phase 1: Network Setup<br>
                (topology + graph-theoretic statistics)
            </div>
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 15px; height: 70mm; display: flex; justify-content: center; align-items: center; color: rgba(255,255,255,0.4); text-align: center; font-size: 13px;">
                [INSERT SCREENSHOT]<br><br>
                Phase 2: Convergence Simulation<br>
                (routing table + path visualization)
            </div>
        </div>
        <div style="margin-top: 14px; text-align: center;">
            <span style="color: #00D4AA; font-size: 15px; font-weight: 600; letter-spacing: 0.5px;">
                http://localhost:8501 &nbsp;&mdash;&nbsp; Built with Streamlit + DuckDB + Pyvis + Plotly
            </span>
        </div>
        <div class="footer-tag" style="color: rgba(255,255,255,0.25);">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 13: BENCHMARK RESULTS ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Benchmark Results</h2>
        <div class="metric-strip" style="margin-bottom: 12px;">
            <div class="metric-box gold">
                <div class="value" style="font-size: 24px;">~10x</div>
                <div class="label">DuckDB Speedup</div>
            </div>
            <div class="metric-box">
                <div class="value" style="font-size: 24px;">3</div>
                <div class="label">Backend Engines</div>
            </div>
            <div class="metric-box blue">
                <div class="value" style="font-size: 24px;">3</div>
                <div class="label">Python Algorithms</div>
            </div>
            <div class="metric-box red">
                <div class="value" style="font-size: 24px;">45+</div>
                <div class="label">Measurements</div>
            </div>
        </div>
        <div class="grid-2">
            <div class="image-placeholder" style="height: 65mm;">
                [INSERT SCREENSHOT]<br>
                Phase 5: Execution Latency<br>
                (time vs network size with 95% CI)
            </div>
            <div class="image-placeholder" style="height: 65mm;">
                [INSERT SCREENSHOT]<br>
                Phase 5: Speedup Bar Chart<br>
                (DuckDB speedup over SQLite per size)
            </div>
        </div>
        <div class="highlight-box" style="font-size: 12px; margin-top: 8px;">
            <strong>Finding:</strong> DuckDB's USING KEY consistently outperforms SQLite's standard CTE by 5-15x across network sizes. The gap widens with graph density due to SQLite's exponential path enumeration.
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 14: COMPLEXITY ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Complexity Analysis</h2>
        <div class="grid-2" style="margin-top: 5px;">
            <div>
                <div class="image-placeholder" style="height: 55mm;">
                    [INSERT SCREENSHOT]<br>
                    Phase 5: Log-log complexity plot<br>
                    (empirical + fitted power-law curves)
                </div>
                <div class="card" style="margin-top: 10px; padding: 12px;">
                    <h3>Algorithm Comparison</h3>
                    <table style="font-size: 12px;">
                        <tr><th>Algorithm</th><th>Time</th><th>Distributed</th></tr>
                        <tr><td>Bellman-Ford</td><td>O(V&sup2; * E)</td><td>Yes</td></tr>
                        <tr><td>Dijkstra</td><td>O(V(V+E) log V)</td><td>No</td></tr>
                        <tr><td>Floyd-Warshall</td><td>O(V&sup3;)</td><td>No</td></tr>
                        <tr><td>DuckDB USING KEY</td><td>O(V * E)</td><td>N/A</td></tr>
                        <tr><td>SQLite Standard CTE</td><td>O(V * E * P)</td><td>N/A</td></tr>
                    </table>
                </div>
            </div>
            <div>
                <div class="image-placeholder" style="height: 55mm;">
                    [INSERT SCREENSHOT]<br>
                    Appendix A: Theoretical growth curves<br>
                    (log-scale complexity comparison)
                </div>
                <div class="warning-box" style="font-size: 12px; margin-top: 10px;">
                    <strong>P = path count:</strong> In SQLite's standard CTE, P denotes the number of distinct walks enumerated before the post-hoc GROUP BY. For dense graphs, P grows exponentially with |V|, making SQLite infeasible beyond ~12 nodes. DuckDB eliminates this factor entirely.
                </div>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 15: KEY FINDINGS ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Key Findings</h2>
        <div class="grid-3" style="margin-top: 8px;">
            <div class="card accent-card" style="min-height: 80mm;">
                <h3>1. SQL as a PL</h3>
                <ul style="font-size: 13px;">
                    <li>SQL can fully implement distributed routing protocols.</li>
                    <li>The declarative approach replaces hundreds of lines of imperative code with a single query.</li>
                    <li>The recursive CTE maps directly to the iterative convergence of Bellman-Ford.</li>
                </ul>
            </div>
            <div class="card gold-card" style="min-height: 80mm;">
                <h3>2. USING KEY Advantage</h3>
                <ul style="font-size: 13px;">
                    <li>DuckDB's USING KEY enables in-place row updates during recursion.</li>
                    <li>Eliminates exponential path explosion inherent in standard CTEs.</li>
                    <li>Achieves 5-15x speedup over SQLite across all tested network sizes.</li>
                </ul>
            </div>
            <div class="card blue-card" style="min-height: 80mm;">
                <h3>3. Dynamic Resilience</h3>
                <ul style="font-size: 13px;">
                    <li>Link failure simulation via simple SQL DELETE commands.</li>
                    <li>Re-running the same query automatically discovers next-best paths.</li>
                    <li>No modification to the routing query is needed for re-convergence.</li>
                </ul>
            </div>
        </div>
        <div class="highlight-box" style="margin-top: 8px;">
            <strong>Central Result:</strong> Modern SQL is no longer "just for queries." With state-aware recursion, it is a first-class language for simulating, validating, and analyzing complex distributed protocols.
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 16: FUTURE WORK ═══════════════════ -->
    <div class="slide light-slide">
        <div class="geometric-badge"></div>
        <div class="page-number"></div>
        <h2>Conclusion and Future Work</h2>
        <div class="grid-2" style="margin-top: 8px;">
            <div class="card accent-card">
                <h3>Conclusion</h3>
                <ul>
                    <li>Successfully demonstrated that <strong>DuckDB's USING KEY</strong> provides a 1:1 mapping between SQL recursion and physical router behavior.</li>
                    <li>Built a complete <strong>interactive evaluation suite</strong> with 6 phases: topology setup, convergence simulation, fault injection, re-convergence, benchmarking, and algorithmic theory.</li>
                    <li>Empirically validated that keyed CTEs maintain <strong>polynomial scaling</strong> while standard CTEs exhibit exponential degradation.</li>
                </ul>
            </div>
            <div class="card gold-card">
                <h3>Future Research Directions</h3>
                <ul>
                    <li><strong>Path-Vector Protocols (BGP):</strong> Implement BGP-like logic using SQL array types for full AS-path tracking.</li>
                    <li><strong>Link-State Simulation:</strong> Model Dijkstra/OSPF within recursive SQL for comparative benchmarking.</li>
                    <li><strong>Dynamic Traffic Modeling:</strong> Integrate real-time metrics (congestion, latency) into the edges table.</li>
                    <li><strong>Large-Scale Analysis:</strong> Test convergence on Internet-scale AS graphs to evaluate scalability limits.</li>
                </ul>
            </div>
        </div>
        <div class="footer-tag">SQL as a Programming Language</div>
    </div>

    <!-- ═══════════════════ SLIDE 17: THANK YOU ═══════════════════ -->
    <div class="slide dark-slide" style="page-break-after: avoid; justify-content: center; align-items: center; text-align: center; padding: 20mm 25mm;">
        <div class="page-number" style="color: rgba(255,255,255,0.3);"></div>

        <div class="end-box">End of Presentation</div>

        <div style="font-size: 44px; color: #FFFFFF; font-weight: 700; letter-spacing: -1px; margin: 0 0 10px 0;">
            Thank You for Your Attention
        </div>

        <div style="font-size: 20px; color: #E5E5E5; margin: 0 0 30px 0; font-weight: 400;">
            Questions and Discussion
        </div>

        <div style="display: flex; flex-direction: column; gap: 10px; align-items: center; margin-top: 5px;">
            <div style="display: flex; align-items: center; justify-content: center;">
                <span style="color: #00D4AA; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;">
                    Mehdi Hoseyni &nbsp;&bull;&nbsp; University of Tubingen
                </span>
            </div>
            <div style="display: flex; align-items: center; justify-content: center;">
                <span style="color: rgba(255,255,255,0.4); font-size: 13px;">
                    Database Systems Seminar &nbsp;&mdash;&nbsp; Summer Semester 2026
                </span>
            </div>
        </div>
    </div>

</body>
</html>
"""

output_dir = "/Users/mehdihoseyni/Desktop/2.semester/sql is a PL"
output_pdf_path = os.path.join(output_dir, "DVR_Presentation.pdf")

current_dir_path = Path(output_dir).resolve()
base_url_uri = current_dir_path.as_uri()
if not base_url_uri.endswith('/'):
    base_url_uri += '/'

print(f"Resolving assets using base URL: {base_url_uri}")
print("Generating PDF...")

HTML(string=html_content, base_url=base_url_uri).write_pdf(output_pdf_path)

print(f"\nFile successfully created: {output_pdf_path}")
print(f"Total slides: 17")
