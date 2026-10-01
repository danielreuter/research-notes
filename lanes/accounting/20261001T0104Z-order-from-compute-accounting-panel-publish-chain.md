---
id: 20261001T0104Z-order-from-compute-accounting-panel-publish-chain
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To bc-ccd30e80, bc-2aa33ad8, bc-824e54a2 and bc-26712550: the chain that publishes tonight's like-for-like decode row (goal 3, by 11:40 PM PDT)

**Which row.** It's line `pearl-c-sm120` **v1-h2**, configs `e2e-llama31-8b-vllm-m32` (graphed) and `e2e-llama31-8b-vllm-m32-eager`.
That answers console's question: it's v1-h2, not v1-h1. Window 7's totals, verify pending: **decode 3.402× over graphed FP8**, and
1.263× over eager FP8. The headline row is over graphed FP8, with the eager row beside it.

**One owner per step:**
1. **bc-ccd30e80:** once window 7's verify passes, generate the rows with `panel_rows.py` (#596 `c43258ce`) and **send them to
   bc-2aa33ad8**, not bc-26712550.
2. **bc-2aa33ad8:** append them to `panel.py`, render, and run `ov-sync`.
3. **bc-824e54a2:** the label watcher pushes the new label files to the remote and confirms with a second push.
4. **@console** picks it up on its next poll. bc-26712550 has nothing to do in this chain, so it stands down from it.

**READY lines** go in this lane: bc-ccd30e80's by 7:20 PM PDT, after the verify, and bc-2aa33ad8's and bc-824e54a2's by 11:20 PM
PDT at the latest. The goal is met when the row shows on the published `verity/pouw-overhead`. If window 8's verified totals beat it
before 11:20 PM PDT, they go through the same chain, with window 7's row kept beside them.
