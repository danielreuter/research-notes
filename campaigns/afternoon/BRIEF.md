---
campaign: afternoon
created: 2026-09-24T16:55Z
---
# Afternoon 2026-09-24: land the overnight work on main, then verifier cost + arithmetic hill-climb

User decisions (16:50Z):
- Every proof variant at the same security: 2^-128 target and achieved (the frozen contract already gates this). SP1 stays
  out of Table 2 until an SP1 run meets it; 100-bit SP1 results are drill-down only.
- Table 1's A-GKR assumptions line: correct the Merkle hash to what the code uses (SHA-512, not BLAKE3).
- Next research: verifier cost for every Table 2 cell (fills D3) and a hill-climb of the arithmetic phase (50-73% of
  prover time on every row). Lanes launch on main after the merge lands.

| lane | base | worktree | pod | budget | FINAL |
|---|---|---|---|---|---|
| merge-postwave | lane/post-wave 1b3c7be6 | ~/projects/verity-main-wt/post-wave (full) | one pod for cargo check / tests | $3 | 18:15Z |

## merge-postwave

Merge into lane/post-wave, in this order, one merge commit each (never rebase, never touch main or its worktree):
1. main e7d4a978 (steward rules, 4 commits)
2. lane/fill-consumer 444084d3 (1)
3. lane/agkr-table 5b3a4646 (7)
4. lane/sp1-table 2da1e77e (16; already contains lane/sp1-formats 2b0cc33a, confirm it is a no-op after)
5. lane/sp1-tcdot 97b5b60a (31)
lane/fill-dc and lane/verify-night are at 1b3c7be6 (nothing to merge).

Then one commit: Table 1 A-GKR `assumptions` in backends/numerical/python/verity_numerical/bench/tables.py names the hash
the A-GKR code actually commits with (read the gkr crate; expected SHA-512 Merkle). Nothing else in the frozen text changes.

Validation (all must pass before FINAL):
- `git status` clean, `rg -n '^(<<<<<<<|>>>>>>>|=======)$'` finds nothing tracked.
- On ONE pod through `research run --on` (LANE-CONTRACT §3a): `cargo check --release` of every Rust crate the merges touched
  (ligero-verify, the gkr crate, the SP1 host/guest crates: the sp1-* lanes' bootstrap scripts say what they need), and
  the Python suites of backends/numerical and tools/research. Terminate the pod at FINAL.
- Render on the laptop from the merged tree:
  `PYTHONPATH=<wt>/backends/numerical/python:<wt>/tools/research/src:<wt> ~/projects/verity-main-wt/main/.venv/bin/python -m verity_numerical.bench.tables --root ~/.research/store --format md`
  (and `bench.drilldown`), diff against campaigns/morning-tables/render/1540Z-tables.md / -drilldowns.md. The only
  allowed Table 1-3 change is the A-GKR hash text; explain any other difference line by line (a changed number is a stop:
  report it, do not "fix" the renderer).
FINAL: tip sha, per-check pass/fail, the diff, anything that surprised you. The coordinator fast-forwards main.
