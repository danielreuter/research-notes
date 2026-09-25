---
lane: b-ligero-standard-hash
kind: report
created: 2026-09-25T06:30Z
status: open
---

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

## 1. `--commit-per-rep` (82453d30)
Every rep (the warm-up included) drops the committed state and runs `commit_vus` with no tree cache, then rebuilds the hashed
statements, then proves (pipelined, p >= 2, CUDA, unshared `included-hash` only). Measured per rep:
* `commitment.seconds`: the x / W / y trees and their row digests (frame-v3 over keyed-BLAKE3 row leaves) = the Table 3
  serving-overhead bucket; excludes the prover's row chains;
* `commitment.row_chain_seconds`: the prover's precomputed in-circuit chain states of every committed row -> in `t.witness`
  (hints_host), so inside `t.total`;
* `commitment.statement_seconds`: rebuilding the hashed statements from the new digests -> in `t.serialization`, inside `t.total`;
* `end_to_end.seconds = commitment.seconds + t.total` (the Table 2 P divides this), `end_to_end.vu_per_second`,
  `end_to_end.overhead_vs_native_peak`; the reported rep is the median END-TO-END rep. `fp.commitment` records the rule.
bench-result/v1's contract is unchanged: the new names sit outside its reserved prefixes. `R._committed_digests` now keeps the
base (instance-word) marshal cached and drops only the hashed statements.

## Discrepancies
(none yet)

## FINAL
(pending)
