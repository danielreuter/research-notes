---
lane: b-ligero-standard-hash
kind: report
created: 2026-09-25T06:30Z
status: open
---

CHECKPOINT d69d082 (07:39Z) [open] fp8-ada+blake3 4090 l4096 p2 4096 VUs (r..6238, art:fdda2a3a run record): t.total 4.31s + commit 0.65s = e2e 4.96s, 1.30e8x, 2^-128.40, Rust batch ACCEPT pinned. Merged blake3-80gb (sweep_vu + steps-pin). Plateau sweep r..f45c at 8192 VUs.
CHECKPOINT 00ffe398 (07:26Z) [open] d5b299ff: +blake3 commit 18s->0.65s (per-row leaf_bytes fold batched; roots identical; 17 tests pass). Dev fp8-ada 4090 l4096 p2: t.total 4.49s, e2e 5.14s, 1.35e8x. Measured 5-rep cell r20260925-072604-6238 running (custody-r2). Handoff to blake3-80gb.
CHECKPOINT none (07:08Z) [open] Acted on coordinator 0650Z handoff: merged main 00ffe398 (4de530e5); names now commit.seconds/e2e.seconds per bench.views. +blake3 pins bf16-ampere/fp8-hopper (071e3ef7). Dev fp8-ada 4090: prove 4.4s, commit 18s/rep (host leaf_bytes loop?); profiling r..b881.
CHECKPOINT 00ffe398 (06:58Z) [open] 071e3ef7: +blake3 pinned on bf16-ampere (5b762054) + fp8-hopper (433bdfc3): gates 49/86/0F + 25/86/0F, fixtures pinned ACCEPT, cargo test green; fp4-nvf4+blake3 needs NVFP4 row byte schema (core-schemes). Next: fp8-ada+blake3 --commit-per-rep dev run on 4090
CHECKPOINT c21b8ccf (06:47Z) [open] started 06:30Z; 820aa6f+1cf9178 already in main (step 2 no-op); 82453d30 bench-vu --commit-per-rep (commitment bucket per rep); 4090 pod vy-b-ligero-sh bootstrapping; next: bf16-ampere/fp8-hopper +blake3 pins+gates, fp8-ada+blake3 cell dev run
# b-ligero-standard-hash: B-Ligero frame-v3 keyed-BLAKE3 full-relation Table 2 cells

Goal (launch message): the first independently verified B-Ligero BLAKE3 full-relation Table 2 cell (frame-v3, keyed-BLAKE3
row leaves, `+blake3`, 2^-128 target and achieved, frozen instances, K = 1536, B = 4096, prover on the line's SKU, commitment
time reported as its own bucket plus proving). Decision doc: Project store `docs/commitment-scheme-decision.md` §1, §3, §6.

Worktree `~/projects/verity-main-wt/b-ligero-standard-hash`, branch `lane/b-ligero-standard-hash`, base main 25f0c1de.
Pod scripts: `evidence/pod-scripts/`.

## 0. Starting state (read 06:30-06:45Z)
* **Plan step 2 is a no-op:** blake3-leaf-3's level-scheduled witness interpreter `820aa6f` and ajtai-leaf-2's pipelined hashed
  runner `1cf9178` are both ancestors of main 25f0c1de (`git merge-base --is-ancestor`).
* **`+blake3` pins on main** (`backends/ligero-verify/src/leaf.rs::PINS`): fp8-ada, bf16-hopper, fp8-ada-x4. Missing:
  bf16-ampere, fp8-hopper, fp4-nvf4. fp4-nvf4 goes through `hash_format` (`fp4/hashed.py` FP4Format), whose lane packing is
  Poseidon2-only (`Poseidon2Leaf.with_lanes`): its `+blake3` needs a byte layout for the NVFP4 row (codes + scale bytes) in the
  BLAKE3 leaf first; bf16-ampere / fp8-hopper use the same word formats as bf16-hopper / fp8-ada.
* **steps pin:** main's `verify.rs` already refuses a pinned statement whose `steps` differs from `Relation.steps`, plus the Ajtai
  `steps <= n` bound and the v5 `steps x k_ops == 1536` check (lane steps-pin, merged). Lane ligero-steps-pin is working on the
  H2 item now; per the launch message nothing counts before its handoff lands in my base.
* **Commitment timing on main:** `bench_vu_rel` commits once before the reps (`relation.hash.commit_seconds`, optionally from
  `--auth-cache`) and caches the hashed statements per run, so no timed rep pays commitment. TABLES.md requires each timed run to
  commit its own batch, with commitment reported apart from proving (Table 3).

## Log
* 06:40Z pod vy-b-ligero-sh (whwiqx4qyy75am, RTX 4090 24 GB, reference part, EPYC 7642, SECURE, $0.74/h) created, registered,
  guard 90; bootstrap r20260925-064433-58ac (RELS fp8-ada,bf16-hopper,fp8-hopper, BENCH_INSTANCES=1).
* 06:50Z 82453d30 `bench-vu --commit-per-rep` (below).
* 06:49-06:53Z r20260925-064848-b593 (`10-pins-gates.sh`, tree 25f0c1de): `+blake3` fixtures + gates.
  **bf16-ampere+blake3**: m = 35 067 rows/unit, sys_id 5b762054…, table f67ab817…; gate `--vus 2048 --batch 4096 --zk
  interactive` **49 honest sub-batches, 86 negatives, 0 failures**. **fp8-hopper+blake3**: m = 34 997, sys_id 433bdfc3…,
  table a27af32f…; gate **25 honest, 86 negatives, 0 failures**. Rust `system-digest` == Python sys_id for both.
* 06:55Z 071e3ef7 the two PINS rows; r20260925-065539-17cf (`15-rust.sh`): ligero-verify rebuilt at 071e3ef7 (sha256
  e7f47a52…), `cargo test --release` 32 + 7 + 27 passed; both fixtures **pinned batch ACCEPT** (`system pinned
  (bf16-ampere+blake3)` / `(fp8-hopper+blake3)`, 2^-128.05). fp4-nvf4+blake3 not attempted: see §0 (needs the NVFP4 row's byte
  serialization under the keyed-BLAKE3 leaf schema, which core-schemes defines).
* 06:57Z dev cell fp8-ada+blake3 l=4096 p2 2 reps with `--commit-per-rep` (r20260925-065733-eade, tree 071e3ef7 + 82453d30;
  harness validation, not a result): m = 35 370, 49 sub-batches, t = 203. Rep 1: prover 3.32 s + hints 1.10 s (t.total 4.42 s,
  row chains 0.82 s + statements 0.16 s inside it); **commitment 18.0 s** (warm-up 18.03 s); e2e 22.4 s (rep 2: 22.36 s).
  The committer dominates. (A second launch r20260925-070258-88d6 exited GPU NOT IDLE: `--source .` had launched eade
  although I killed it locally; now `research pods sync` + `--cwd /workspace/src`.)
* 06:50Z inbox: coordinator handoff "Core schemes landed (PR #15, main 00ffe398)". Merged origin/main at 4de530e5: the
  core `blake3-keyed/row/v2` schema is the leaf's (core_schema_test cross-checks it); no local stand-in existed. Order kept:
  frame-v3 first, vllm-v1 after (its SHA-256 leaves need the SHA-256 gadget = survey gate). ad4c3440 renames my measurements to
  the `commit.*` / `e2e.*` names `bench.views` reads.
* 07:08Z r20260925-070830-b881 (`12-prof.sh`): cProfile of one fp8-ada+blake3 commit-per-rep bench. The commitment is the
  **per-row `leaf_bytes`** in `hashauth.build_row_tree`: every row's chunk CVs folded to its BLAKE3 root on single-lane numpy
  (32 939 calls, 80 s cumulative = ~21 s per commit + the Python verifier's per-VU calls); `native()` ~1.5 s per tree.
* 07:14Z d5b299ff `leaf_bytes_many` (lockstep fold, byte-identical, row-by-row fallback on a malformed frame); build_row_tree
  uses it. r20260925-072321-d0e6: blake3_test + core_schema_test **17 passed**; 1-rep bench: **commit 0.650 s** (was 18.0 s),
  roots a=2f9ff265… b=0413c926… identical to eade, Python verifier ACCEPT; t.total 4.489 s, e2e 5.139 s, 1.349e8x native
  peak. (The full leaf/auth suite r20260925-071530-178a was stopped after 7 min: too slow for what it covers.)
* 07:26Z measured cell r20260925-072604-6238: fp8-ada+blake3 l=4096 p2 5 reps, `--commit-per-rep`, custody-r2 8h, Rust batch.
* 07:27Z handoff to blake3-80gb (d5b299ff + `--commit-per-rep`; H100 lines are theirs).
* 07:30Z **r20260925-072604-6238 DONE** (tree d5b299ff, custody PRESERVED, run record art:fdda2a3a…, 171 files 1.46 GB):
  fp8-ada+blake3, frozen `bench-instances-fp8-ada/v1` (manifest e66ff0f2…) [0, 4096), l=4096 p2 (49 sub-batches of <= 85
  VUs), 5 reps, uncontended. **t.total 4.312 s** (witness 0.949, enc+commit 1.933, arith 1.216, ser 0.200), **commit.seconds
  0.646 s** (cold 0.636), **e2e 4.958 s = 826.1 VU/s, 1.301e8x** native (proving alone 1.132e8x), soundness 2^-128.40.
  Pod's pinned ligero-verify (sha256 e7f47a52…): sys_id 71f39e44…, `system pinned (fp8-ada+blake3)`, batch ACCEPT 49/49,
  union 2^-128.40, python agreement 49/49 (producer check, not a label). Not a sweep point (no `sweep`/`protocol` block).
* 07:09Z inbox (read 07:28Z): blake3-80gb handoff -- views need `sweep` {plateau} + `protocol` blocks; their sweep_vu
  (8c50b497); split: H100 + A100 theirs, 4090 mine. Merged lane/blake3-80gb (fca28d54: + ligero-steps-pin 236020a6 via it,
  so the pin is in my base); dc2cae87 sweep_vu ranks by `e2e.vu_per_second`. Reply 07:31Z.
* 07:32Z sweep r20260925-073210-f45c (tree dc2cae87, custody-r2): fp8-ada+blake3 l=4096 p2 5 reps `--commit-per-rep`, from
  1024: 641.96 / 762.79 / 825.75 / 852.71 VU/s at 1024 / 2048 / 4096 / 8192; 16384 reps e2e 18.5-19.8 s (~867 VU/s, < 2 %
  over 8192), so the rule needs 32768. Each point's in-bench Python verifier is ~97 s/rep: ~10 min per point at 16384.
* 07:35Z inbox: red-team-standard-hash (lanes/coordinator/20260925T0735Z-handoff-from-red-team-standard-hash.md, evidence
  art:2b51c5fd…, harness rtsh_remap_e2e.py on lane/red-team-standard-hash 8ace1ada): **R1 BREAK** -- the (vu, x, W) triple
  of a v5 hashed statement was prover-chosen; neither verifier derived x_index / w_index from vu_index, so a committer serving
  VU v a wrong y (another VU's true output) got it accepted on that VU's (x, W). **R2 BLOCKING** -- reverify recomputed no
  commitment. My `+blake3` cells are pulled from Table 2 until both land and the red team re-runs the harness.
* 07:53Z fixes pushed. 3af90e71 (R1): `auth::layout_error` (Rust, in `check_hashed`) and `hashauth.layout_error` (Python, in
  `verify_hash_auth`): counts a = b = y -> x = W = vu; a.count x b.count = y.count -> x = vu // nw, W = vu % nw
  (relchain.tile_indices); anything else refused. The honest prover (`auth_for`) is already canonical: existing dumps stay
  valid. de2fa317 (R2): reverify recomputes the a/b/y bindings (hashauth.binding_digest of dataset, tier, the regenerated
  set's manifest digest, [0, total), K, tree, schema) and roots (core frame-v3 over keyed-BLAKE3 digests of the raw rows,
  not the prover's leaf code) and requires every statement's trees to equal them and each rep's vu_index to cover [0, total)
  exactly once; a hashed dump with no `set` block, a tile, or a digest mismatch FAILs (fail closed). Pod check
  `50-fixcheck.sh` (cargo test, pytest, the red team's harness, R2 honest + 3 negatives) waits for the sweep: a run syncs
  /workspace/src, which later sweep points would import.
* Seen: lane/hash-commit 86d7edb7 / fe9c7172 has a CUDA committer for frame-v3 keyed-BLAKE3 row trees (commit-gpu) with its
  own `--commit-reps` harness; not merged (overlaps hashauth / relchain); my committer is 0.65 s of 4.96 s.

## 1. `--commit-per-rep` (82453d30, names aligned with main's `bench.views` in ad4c3440)
Every rep (the warm-up included) drops the committed state and runs `commit_vus` with no tree cache, then rebuilds the hashed
statements, then proves (pipelined, p >= 2, CUDA, unshared `included-hash` only). Measured, the hash-commit lane's convention
that `bench.views` (main fb2f0420 / 6fdd261b) reads:
* `commit.seconds`: median over the timed reps of the x / W / y trees and their row digests (frame-v3 over keyed-BLAKE3 row
  leaves) = the Table 3 serving-overhead bucket; excludes the prover's row chains. `commit.cold_seconds` = the warm-up rep's,
  `commit.reps` = how many;
* `commit.row_chain_seconds`: the prover's precomputed in-circuit chain states of every committed row -> in `t.witness`
  (hints_host), so inside `t.total`;
* `commit.statement_seconds`: rebuilding the hashed statements from the new digests -> in `t.serialization`, inside `t.total`;
* `e2e.seconds = commit.seconds + t.total` (`t.total` from `phases.median_rep`, unchanged; the Table 2 P divides e2e),
  `e2e.vu_per_second`, `e2e.overhead_vs_native_peak`. `fp.commitment` records the rule. `bench.views` recomputes
  end_to_end = t.total + commit.seconds itself, so the table does not depend on my e2e names.
bench-result/v1's contract is unchanged: the new names sit outside its reserved prefixes. `R._committed_digests` now keeps the
base (instance-word) marshal cached and drops only the hashed statements.

## Discrepancies
(none yet)

## FINAL
(pending)
