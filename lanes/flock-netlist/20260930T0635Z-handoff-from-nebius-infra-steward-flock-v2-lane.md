---
id: 20260930T0635Z-handoff-from-nebius-infra-steward-flock-v2-lane
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> M0 (bc-ff572e70): I launched a helper lane, `flock-v2-design` (bc-37a1971b), for the lever after tiles; it feeds your backlog

**Why:** Daniel's standing instruction (06:15Z) is that when a workstream is theory-bound, the steward launches theory lanes.
`docs/gemm-hash-cost-plan.md` designs nothing after tiles and row 2. Decode overhead (M = 1–8) is plotted separately, with no
design. Node 1's GPUs were 0.4% busy from 05:16 to 06:25Z.

**What it does:** it asks you what you're on, then designs the largest remaining lever you aren't on, with no protocol or relation
change. Candidates:
- decode-shape amortization;
- device-evaluated deep units;
- unit-slot slack.

It prototypes and measures on the `provers` Kueue queue as line `flock-m0-v2`, byte-identical to the baseline.

**What it asks of you:**
- If you already cover every candidate, say so, and it stops.
- You decide what merges.

**Brief:** Project store `internal/lane-briefs/flock-m0-v2-design.md`.

**Cutover:** your 06:13Z ready-file was seen. `cutover.sh` has been running on node 1 since before 06:26Z, and it's held up by
train checks' `gpu-lease` (routed to RC). After it, run your benches through `submit.sh prover-bench`, not `gpu-lease`.
