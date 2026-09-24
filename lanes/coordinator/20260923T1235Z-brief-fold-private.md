---
lane: coordinator
kind: brief
created: 2026-09-23T12:35Z
for: lane fold-private
---

# Brief — lane `fold-private`: fold the PRIVATE-operand-safe units (x4, then x8) and validate post-freeze-2 on a GPU

## 0. Where you start

* Repo `~/projects/verity` (one shared `.git`). Create a NEW worktree `~/projects/verity-main-wt/fold-private` on branch
  `lane/fold-private` from **`lane/post-freeze-2` at cc885b2** (NOT main: main 64c00bd is frozen until the coordinator
  fast-forwards it; post-freeze-2 = main + hash-relation hook + two-column tables + pipe-race fix + merkle warning +
  relmin-private v3 + relmin-lookup v2x4). You never merge into main, never touch other worktrees, never delete other
  lanes' branches or pods.
* Read, in this order: (1) `~/.research/notes/lanes/coordinator/20260923T1030Z-brief-wave2-device-lanes.md` §0–§2 for the
  tooling rules (store, `research run`, pods, pushing, `machines.toml`, notes format, D7) and §6 (coordinator appendix);
  (2) `~/.research/notes/lanes/relmin-lookup/20260923T0640Z-report-relmin-lookup.md` — the whole thing, especially the
  `_folded` construction (`relations.py`), §3 "why 10x fewer rows bought only 1.6x", §6 remaining list, §7 tooling
  gotchas; (3) `~/.research/notes/lanes/relmin-private/20260923T0752Z-report-relmin-private.md` (v3 = private-safe units,
  the zero-sum fix, the encoder caveat — NOTE the coordinator did NOT reproduce their 15x-slower encoder: dev-4090 on the
  same commits measured fp8-ada v1 l=16384 encode 0.070 s; treat it as their pod's problem but WATCH `t.encoding_commitment`
  in your own runs and ship `backends/shared` with your tree, otherwise `merkle.py` falls back to a 35x slower host Merkle
  (it now warns; `LIGERO_GPU_STRICT=1` makes it fatal — set it)).
* Notes go to `~/.research/notes/lanes/fold-private/20260923T1235Z-report-fold-private.md` (front matter like the other
  lane reports). Write a `CHECKPOINT <sha>` line at the top every ~45 min and a final `FINAL` section; the coordinator reads
  only that file and your final message.

## 1. Why this lane exists

relmin-lookup's fold (`-v2x4`: four instruction steps per column) took fp8-ada on a 4090 from 0.329 s (v2) to 0.162 s
(v2x4) per 4096 VUs, because the prover is ~95 % per-sub-batch fixed cost and the sub-batch count is
`VUs x columns/VU / l`, independent of rows. But v2/v2x4 are PUBLIC-selection relations (the verifier recomputes the public
half of the step; useless for private operands) — drill-downs only. The user's Table 2 needs private-operand-safe units:
**v1** (today's headline cells: fp8-ada 0.252 s on the 4090 at l=16384, depth 2) and **v3** (relmin-private, 2x fewer rows
than v1, operands committed). Fold THOSE.

## 2. Deliverables, in order (stop and checkpoint after each)

### D0 — GPU validation of post-freeze-2 (cc885b2) — FIRST, ~25 min, the coordinator is waiting on it

On your 4090, from an unmodified cc885b2 tree (ship the WHOLE tree incl. `backends/shared`; `LIGERO_GPU_STRICT=1`,
`LIGERO_GRAPH_STRICT=1`):

1. `run.py --relation fp8-ada gate-vu --device cuda` (bare v1), `--relation fp8-ada --auth included-hash gate-vu`,
   `--relation fp8-ada-v3 gate-vu`, `--relation fp8-ada-v2x4 gate-vu`, `--relation bf16-hopper-v3 gate-vu`
   (exact flags: see `run.py --help`; relmin-lookup §7: it is `--relation X gate-vu`, not `gate X`). Expect 0 failures.
2. `OMP_NUM_THREADS=8 pytest backends/direct/ligero -q` (relmin-lookup: on a 128-thread pod unthrottled torch takes 11 min).
3. One fp8-ada v1 bare bench at l=16384, `--pipeline 4`, 4096 VUs, int-ZK, 1 rep, dumps rep1, and Rust-verify the dump with the
   verifier built from your tree (`cargo build --release` in `backends/ligero-verify`; `ligero-verify batch --target-bits 128`).
   Expect t.total ~0.25 s or better (pipe-race's fix makes depth 4 ~37 % faster than depth 2) and `t.encoding_commitment`
   ~0.07 s. If encode is >0.3 s, STOP and diagnose (that is relmin-private's caveat reproducing) before anything else.

Report D0 as `CHECKPOINT cc885b2 D0 PASS|FAIL <details>` in your note. On PASS the coordinator ffs post-freeze-2 into main.

### D1 — fold v3 and v1 (x4): `_folded`-style relations with additive names

* `fp8-ada-v3x4`, `fp8-hopper-v3x4`, `bf16-hopper-v3x4`, `bf16-ampere-v3x4` and `fp8-ada-x4`, `fp8-hopper-x4`,
  `bf16-hopper-x4`, `bf16-ampere-x4` (v1 fold). Same VU claim (same operands, same final word), the three intermediate
  accumulators private. Nothing existing changes: base systems byte-identical (assert it in a test like relmin-lookup did).
* Statement widths: a folded column carries 4x the operand words. Check `serialize.py` / statement v4 widths and the Rust
  side (`relation.rs` `word_bytes`, decode: v1 = word pins per operand, so K is read off the pins — make sure the Rust
  decode accepts K = 4k for the folded names and REFUSES K = 4k for the base names, as the v2 pins do the other way round).
* Rust pins (`sys_id` / table digest, torch-free recompile, fixtures byte-identical, `cargo test --release` green),
  negatives (all existing families + a folded-boundary family: swap the word at a column boundary, claim the 3-step
  intermediate as final), differential: folded unit == 4 chained steps on 1e5 random chains per relation (CPU), then GPU
  gates for all eight. D13/D12-style entry in `backends/ligero-verify/DISCREPANCIES.md` (file is capped at 48 KB by
  `tests/test_repository.py` — if it is near the cap, write the full text in your note and a 6-line stub in the file).

### D2 — bench on the same 4090 (int-ZK, 4096 VUs, K=1536, l=16384 and l=4096, `--pipeline 4`, 3 reps, dumps rep1)

fp8-ada: v1 (control) vs v3 vs v3x4 vs v1x4; then bf16-hopper v3x4 / x4 (Python-model hardware naming as relmin-lookup did).
Every dump Rust-verified at 128 bits with your build; `research data pull` + push + snapshot `fold-private-v1`; labels
`--by fold-private --ref <run>` (relation, fold, note; NEVER `verified=` on your own results — the coordinator does that).
Report t.total, t.total per phase (`t.encoding_commitment`, tests, openings, hints), proof MB, sub-batch count, and the
whole-sub-batch number (4095 VUs) beside the contract number (4096 VUs, 1-VU tail).

### D3 — if D2 lands before 14:15Z: x8 (`_folded(rel, 8)`, one line + pins + gate) and the fused per-group hint kernel
(relmin-lookup §6.1: 0.05 s flat is now a third of the folded prover). Keep going until the deadline; each improvement is a
checkpoint. Agents give up too early: if something looks impossible, write down WHY with numbers and try the next lever.

## 3. Budget, pods, deadline

* One RTX 4090 **reference part** (`research pods create ... --require-reference-part`; 24 GiB, not the 48/49 GB variant),
  $0.74/h, <= 3.5 h => <= $2.60. Terminate it yourself when done and annotate `machines.toml`. No other pods.
* Hard deadline 15:00Z (FINAL written, pod gone, push complete, worktree left in place, `git status --short` empty, no
  conflict markers, no new `.md` in the repo except DISCREPANCIES.md edits).
* No live verifier tonight (the shared EU one is retired): bench with local coins; these are drill-down / hill-climb
  numbers, not Table 2 cells. Say so in the note.

## 4. Report format (final message to the coordinator)

CHECKPOINT sha + mergeable?; D0 verdict; rows/columns per unit table (base vs x4 vs x8); bench table (relation, l, depth,
t.total median, phases, proof MB, sub-batches, Rust verdict); artifacts (runs, results, dumps, snapshot); pod accounting;
what remains ranked; what was wrong in this brief.
