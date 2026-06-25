# Seminar Weekly Plan — Distance-Vector Routing in SQL

---

## Overview

| Phase         | Dates                   | Deadline |
| ------------- | ----------------------- | -------- |
| Training      | Apr 17 → Apr 24         | Apr 24   |
| Programming   | Apr 24 → May 29         | May 29   |
| Slides        | May 29 → Jun 19         | Jun 19   |
| Presentations | Jun 26 / Jul 3 / Jul 10 | —        |
| Paper         | Late Jun → Aug 21       | Aug 21   |
| Review        | Aug 21 → Sep 4          | Sep 4    |
| Final Paper   | Sep 4 → Sep 18          | Sep 18   |

---

## Week 1 — Training Period
**April 17 → April 24**

- [ ] Install PostgreSQL and confirm it runs
- [ ] Draw a small network by hand (4–5 nodes)
- [ ] Run the algorithm manually on paper, step by step
- [ ] Re-read the Wikipedia article carefully
- [ ] Write in your own words: what happens at each iteration?


**Deadline: April 24**

---

## Week 2 — First SQL Version
**April 24 → May 1**

- [ ] Create an `edges` table with your hand-drawn network
- [ ] Write a `WITH RECURSIVE` query that computes costs
- [ ] Do not worry about next-hop yet
- [ ] Test: does the SQL output match your hand calculation?

---

## Week 3 — Add Next-Hop Tracking
**May 1 → May 8**

- [ ] Extend your query to also record which neighbor gives the best path
- [ ] Test again with the same hand-drawn example
- [ ] If stuck, ask your supervisor for a hint

> This is the hardest week. Give it extra time and do not skip it.

---

## Week 4 — Show Every Iteration
**May 8 → May 15**

- [ ] Output T=0, T=1, T=2... separately so convergence is visible
- [ ] Try a bigger network (6–7 nodes)
- [ ] Fix any bugs that appear with the larger network

---

## Week 5 — Simulate Network Failure
**May 15 → May 22**

- [ ] After convergence, delete one edge from the table
- [ ] Re-run the algorithm and show how routing tables change
- [ ] Try cutting different edges and observe the results

> This is your main new contribution. Spend good time here.

---

## Week 6 — Polish the Code
**May 22 → May 29**

- [ ] Clean up your SQL code
- [ ] Make sure the demo output is readable and clear
- [ ] Write short notes: what was hard? what surprised you?
- [ ] No new features after this week

**Deadline: May 29 — programming done**

---

## Week 7 — Build Slide Structure
**May 29 → June 5**

- [ ] Write the slide outline: problem → algorithm → SQL → demo → findings
- [ ] Fill in the first half: problem description and algorithm explanation
- [ ] One idea per slide — keep it simple

---

## Week 8 — Finish Slides
**June 5 → June 12**

- [ ] Add implementation slides: show your core SQL query
- [ ] Add the network failure demo slides
- [ ] Practice saying your talk out loud

> Contact your supervisor this week to book a review appointment before June 19.

---

## Week 9 — Slide Review and Fixes
**June 12 → June 19**

- [ ] Meet supervisor and go through slides together
- [ ] Apply all suggested changes
- [ ] Do a full 25-minute practice run

**Deadline: June 19 — slides done**

---

## Presentations
**June 26 / July 3 / July 10**

- [ ] Have code editor open and ready for Q&A
- [ ] Prepare a small demo network (4 nodes)
- [ ] Prepare a bigger demo network (6–7 nodes)
- [ ] Network failure demo is the highlight moment

---

## Paper Writing
**Late June → August 21**

| Week | What to write |
|------|--------------|
| Week 1 | Introduction and problem description |
| Week 2 | Background: algorithm explanation |
| Week 3 | SQL implementation |
| Week 4 | Results and network failure experiment |
| Week 5 | Polish, TikZ figures, abstract |
| Week 6–8 | Buffer for fixes and final review |

- [ ] Use SIGCONF two-column LaTeX template
- [ ] Minimum 4 pages, maximum 6 pages
- [ ] Use TikZ for network diagrams
- [ ] Write in English

**Deadline: August 21**

---

## Review Round
**August 21 → September 4**

- [ ] Write review of another participant's paper

**Deadline: September 4**

---

## Final Paper
**September 4 → September 18**

- [ ] Read the review you received
- [ ] Incorporate feedback into the paper
- [ ] Submit final version

**Deadline: September 18**

---

## Important Notes

- The three most critical weeks are **Week 3** (next-hop), **Week 5** (network failure), and **Week 9** (slide review)
- Book your supervisor slide review meeting no later than **June 12**
- Slides must be discussed with supervisor **1–2 weeks before** your presentation date
- Paper must use LaTeX — start the template early, do not wait until the last weeks

---

## Links

- [[Distance-Vector Routing]] — algorithm notes
- [[SQL Recursive CTEs]] — technical reference
- [[Bellman-Ford Algorithm]] — math background
