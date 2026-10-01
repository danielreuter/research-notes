---
id: 20261001T1025Z-handoff-from-circuits-tracer-costs
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (3:25 AM PDT), not urgent: three tracer costs circuits-bool-sampling hit in `verity.ml.boolean.trace`

circuits-bool-sampling (bc-dab39801) found these while tracing the Gumbel lanes and left them for you, since the tracer is your code.
Details: note:20261001T0945Z-report-from-circuits-bool-sampling-gumbel-select.

- Python's garbage collector dominates trace time.
- `trace.emit` ignores its `colls` argument.
- Philox traces take about 4 GB of memory.

Take them after the floor (your 7:50 list or later). None blocks the Boolean PRs.
