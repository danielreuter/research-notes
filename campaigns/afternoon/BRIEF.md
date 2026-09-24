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

DONE 17:56Z: main = 22741456 (pushed); render from main = campaigns/afternoon/render/1800Z-*.md (identical to 15:40Z except
the A-GKR hash text).

## Research lanes (not launched yet; base main 22741456)

Where we stand (Table 2, prover overhead x, 1800Z render): B-Ligero A100 BF16 6.0e6, H100 BF16 1.0e7, H100 E4M3 1.2e7,
4090 E4M3 2.4e6, 5090 NVFP4 4.5e6; + in-proof hash (Poseidon2) 3.5-4x those; A-GKR only A100/H100 BF16 (3.4e7, 6.2e7);
SP1 none at 2^-128. Table 3: arithmetic is 50-68% of B-Ligero prover time and 56-73% with the in-proof hash;
encoding + commitment is the next bucket (12-34%).

| lane | pods | budget | FINAL |
|---|---|---|---|
| verifier-cost | vy-live2b-verifier-ro (pitmqu0zrycw5i, CPU, running) + GPU provers one at a time | $10 | +6 h |
| arith | one GPU pod at a time, `guard = 90` in machines.toml | $10 | +6 h |

### verifier-cost: real verifier cost for every Table 2 cell (fills D3)
D3 has one real live-verifier measurement (H100 BF16: ~7 s verifier CPU per batch, ~54 cores to keep pace); the rest are
prover-side placeholders. The user's goal is "prover overhead down while communication and verifier cost stay reasonable",
so every Table 2 cell (both B-Ligero columns, and A-GKR where it has a cell) needs: verifier CPU-seconds per batch,
cores needed to keep pace with the prover, bytes each way, rounds, and live tax (t.total_live - t.total), from a live
session against a same-datacenter verifier at --target-bits 128.
1. First, before anything else: vy-live2b-verifier-ro holds 5.0 GB of 2026-09-23 live sessions in /workspace/live/sessions
   (server: `backends.direct.ligero.live serve`, /workspace/start_verifier.sh). Preserve them to R2 from the pod
   (`research data mint-credential`, then put; never copy the account keys), confirm with `research data preserved`, then
   extract what they already measure. Nothing else holds this data: do not terminate the pod before custody passes.
2. Measure the missing cells; reuse that pod as the verifier where it is in the right datacenter, else a CPU pod next to the
   prover. Register as bench-result/v1 artifacts under the frozen contract.
3. drilldown.py (not tables.py, which is frozen): D3 from the measured records; D2 prefers independently verified results
   and marks each cell's verification (today it shows SP1+TC_DOT art:0a66c35e, 4.26 s, which does not verify;
   the verified one is art:174d7b4d, 5.81 s); D1's A-GKR rows are stale (say SHA-256 / 2^-127.7 / "Table 1 says BLAKE3";
   the code is SHA-512, Table 1 now says SHA-512).
4. Small: add `included-hash-shared` to the store label vocabulary (test_label_keys_are_the_store_vocabulary fails on main).
FINAL: D3 as rendered, per-cell art ids, verifier pod terminated after custody.

### arith: hill-climb the arithmetic phase of B-Ligero
Goal: cut arithmetic-phase time (Table 3) on every target without changing security (2^-128 target and achieved) or the
relation. Start on the cheapest representative pod (4090 E4M3), then port each win to the other four targets.
Every result a bench-result/v1 under the frozen contract, independently verified (`backends/direct/ligero/reverify.py`),
so it can enter Table 2; report per step: before/after arithmetic seconds, total, overhead x, art ids. Encoding +
commitment is fair game once arithmetic stops moving. Results must be comparable with the current Table 2 cells (same
frozen instances, K, B); anything that changes the proof system goes through a red-team check before it counts.
