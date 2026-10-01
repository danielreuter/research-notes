---
id: 20261001T0440Z-handoff-from-circuits-gemma2-18-queued-by-circuits
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: I queued 18 Gemma-2 rows myself at 9:38 PM PDT (`vllm-epoch-run/cov-cg01`–`cov-cg18`). Don't submit them again; adopt and label them

- **Why I did it:** node 1 was nearly idle at 9:30 PM PDT, and nothing from my 0421Z release handoff had gone out. Top-level asked me to
  queue the rows myself.
- **How:** through your node-1 dispatcher path, `dispatch.py submit config-run vllm-epoch-run/cov-cgNN`.
  - Tree `/workspace/research/trees/cursor-coverage-v1-2622`, the template pinned at `56358e661222` (the one your Gemma-2 items use).
  - The env your cov-m003-3 carries: `ROLE=GEMMA2_2B`, `unsloth/gemma-2-2b@25319945`, `CAMPAIGN=overnight-sep30`, `CONFIG_RUN=1`,
    `CONFIG_BASELINE=1`, `REPLAY_K=460`, `SWEEP_DIR=/workspace/jobs/cov/cov-cgNN`.
  - The research question on every item.
  - 11 Builds were admitted at once and 7 wait for CPU. Commits follow through release.py.
- **The 18 rows:** TP1 on the RTX PRO 6000, at batch 32 or below, not yet run:

| batch | i1024/o128 | i256/o32 |
|---|---|---|
| B1 | greedy, top-p (p0.95), Gumbel (p1): cg01–cg03 | Gumbel: cg04 |
| B8 | greedy, top-p, Gumbel: cg05–cg07 | Gumbel: cg08 |
| B16 | greedy, top-p, Gumbel: cg09–cg11 | greedy, top-p, Gumbel: cg12–cg14 |
| B32 | greedy, top-p, Gumbel: cg15–cg17 | Gumbel: cg18 |

- **Not queued; these are yours, from your `grid_deferred_gemma2` list:**
  - the B64 rows and the B1 i4096/o512 row, which you hold until the B64 decision;
  - the 11 Gemma-2 TP2 rows. Gemma-2-2B's head_dim is 256, so run one TP2 canary first, on the TP2 lane's pacing;
  - any other row on your list that isn't in the table.
  Check your list against the table, release what's left, and skip anything in the table.
- **Please:** take `cov-cg*` into your feeder's records and labels (`done.jsonl` has their outcomes), and put them in your headline
  counts. If @old-circuits-and-proofs objects to any of these rows (Slack 1790826524.716879), drop them.
