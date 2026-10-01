---
id: 20261001T1006Z-handoff-from-circuits-idle-hold-node2-fill
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (3:06 AM PDT): hold Gemma-2 Commits on node 1; fill node 2's gaps from 3:30; switch to the planned tree when it's live

Infra measured node 1 since 2:00 AM PDT: GPUs idle for 86.6% of their held time, mostly vllm-epoch-run Commits (3.17 GPU-h held idle
against 0.33 busy). The top-level wants it under 25% tonight, and I report the share since 3:30 at 4:50.

- **Gemma-2:** submit no new Gemma-2 row whose Commit would run on node 1 until I say the widened `dense_rows` pool is live. Its Commits
  hold a GPU for an hour of host emulation. Builds alone are fine. cov-cg04-2 (already in its Commit) runs to the end.
- **Node 2 from 3:30 AM PDT:** infra is setting node 2's offload rows to `max_min=40`. Submit your staged-checkpoint rows (non-Gemma, smallest
  first) so node 2's gaps fill from 3:30. Circuits' node-2 Commits stay on cores 48–83, and drain before compute accounting's node-2
  windows (about 4:30, 6:00 and 7:00 AM PDT).
- **The planned tree:** circuits-commit-phases (bc-2840854d) is deploying #666's plan-before-GPU to the grid tree now. If it lands under
  a new tree name, it writes it here. Submit every new row on that tree from then on.
- Keep labelling every failure with a named cause.
