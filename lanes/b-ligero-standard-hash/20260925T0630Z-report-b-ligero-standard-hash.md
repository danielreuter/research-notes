---
lane: b-ligero-standard-hash
kind: report
created: 2026-09-25T06:30Z
status: superseded
---

CHECKPOINT none (14:05Z) [superseded] closed by coordinator 14:05Z: agent died in the 12:30-13:50Z laptop worker disconnect; branch clean and pushed; pods already gone; open verification and red-team items carried by verify-night-3 / red-team-standard-hash-2 (cloud); measurement work resumes as cloud lanes if the coordinator relaunches it
CHECKPOINT f893ba0 (13:18Z) [open] x4 instance-equiv/v1 8192 art:d9b3724d + 32768 art:b6f2e1df (PR#21 shape, equal, reproduce) -> verify-night-2. blake3-xob class granted w/ conditions (red-team 1226Z). x4 xob plateau art:ecccca50 handed off. x1 xob sweep running; FINAL by 15:00Z.
CHECKPOINT 5b28557b (13:10Z) [open] x4+blake3-xob sweep done: plateau 32768 5676 VU/s e2e 5.773s 1.89e7x ACCEPT 97/97 2^-128.07 art:ecccca50 (PROVISIONAL, not converged, 65536 OOM). x1 xob sweep r20260925-130720-ab7a running. Handoffs next, FINAL chores by 14:40Z.
CHECKPOINT 5b28557b (12:17Z) [open] blake3-xob PROVISIONAL cells (5b28557b, gated, pinned, Rust ACCEPT): x1 frozen e2e 1.974s (1.963+0.010) 5.18e7x art:b47828e4; x4 0.799s (0.790+0.009) 2.10e7x art:bb69174b; same-tree +blake3 controls 3.539/1.977s. Sent to verify-night-2, coord; x4 xob sweep running r..121605-357f.
CHECKPOINT 5b28557b (11:44Z) [open] x4 instance-equiv/v1 art:6fdeed7e registered (equal, check reproduces) -> verify-night-2; 8192 prefix-equal evidence to coordinator. blake3-xob: tests 27+16 pass, 71f39e44 kept, xob pins x1 3d6cc67b (28584 rows vs 35370) x4 f90e7b41 in 5b28557b; rust+gates r..114349-ea8d; red-team review asked.
CHECKPOINT 672b23ae (11:21Z) [open] x1 malloc sweep DONE: plateau 16384 e2e 13.821s (13.787+0.034) 1185 VU/s 9.07e7x 2^-128.40 art:c9f4a645 (32768 OOM rc-9: not converged); handed to verify-night-2. XOB (blake3-xob) tests+fixtures running r..112012-8420. 1040Z: done (lib.sh exports; merged).
CHECKPOINT fb29b130 (10:54Z) [open] x1 malloc sweep r..103611-67e0 at p4 16384 (p0-p3 1073/1128/1150/1176 VU/s). XOB wired as new scheme blake3-xob (same schema blake3-keyed/row/v2 = same frame-v3 commitment, new circuit): xadd op in all witness generators, ce86046b+tests; pod tests/pins after the sweep.
CHECKPOINT 806a2f73 (10:37Z) [open] malloc-env cells (MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12 set): x1 4096 frozen e2e 3.558s art:9b80f566; x4 4096 1.981s art:050ddede; x4 plateau 8192 2165 VU/s art:19be6afa -> verify-night-2 1037Z. x1 sweep running.
CHECKPOINT 806a2f73 (10:06Z) [open] Live same-pod verifier cell x1 4096 frozen: 5/5 sessions ACCEPT 49/49 own coins, e2e 3.596s, art:e9932b72 -> verify-night-2 (1008Z). Malloc env adopted from now (lib.sh + --env); x4 sweep re-run with it r..100526-b232.
CHECKPOINT 806a2f73 (09:58Z) [open] GPU-committer cells registered: x1 4096 frozen e2e 3.585s art:e7d59ab6; x4 4096 e2e 2.048s art:017a7069; x4 plateau 8192 2109 VU/s art:6b6d4484 -> verify-night-2 (0958Z). Live same-pod verifier run r..095340 accepting 49/49/rep.
CHECKPOINT 806a2f73 (09:20Z) [open] GPU committer smoke: device==host evidence, 4096 x1 e2e 3.64s (1125 VU/s). x4 fold probe l4096p2: e2e 2.05s @4096 (1999 VU/s, 1.78x x1; p3 OOM). x4 sweep r..091922-a390 running (custody). R2 negs on tip all caught.
CHECKPOINT 806a2f73 (09:04Z) [open] tip 806a2f73: merged ligero-steps-pin R4 + main 94b1c4d2 (GPU committer); fixed R4 test regression; cells art:5d20ad00 (4096) + art:d6328cf5 (plateau) -> verify-night-2; handoffs red-team/coordinator/steps-pin; next GPU smoke + x4 fold
CHECKPOINT f4d797b (08:50Z) [open] R4 not reproduced; merged ligero-steps-pin 06176b41 at fcf9a35b; tip check running; next handoffs + x4 fold
CHECKPOINT fcf9a35b (08:50Z) [open] R4 not reproduced on my fix (r..083926); merged ligero-steps-pin 06176b41 (their R1/R2/R4) at fcf9a35b to avoid divergence; tip check r..084934 running; next: handoffs red-team/coordinator (plateau art:d6328cf5 for verify), x4 fold probe+sweep.
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
* 08:07Z **sweep r20260925-073210-f45c DONE** (rc 0, custody-r2): 641.96 / 762.79 / 825.75 / 852.71 / **870.12** VU/s at 1024 ..
  16384; 32768 was killed (rc -9) in rep 2 -> sweep_vu stops, `sweep` {plateau: true, point 4, 16384 VUs}. Plateau: 193
  sub-batches of <= 85 VUs, e2e 18.5-19.8 s per rep, commitment ~2.2 s per rep. Pod's pinned ligero-verify (pre-fix
  e7f47a52…) on the plateau's rep 1: batch ACCEPT 193/193, union 2^-128.40, `system pinned (fp8-ada+blake3)`, python 193/193
  (producer check). Registered 08:22-08:24Z (all PRESERVED; `40-register.sh`):
  - p0 1024: result art:5dfd3ae7e4a5b6b5b52b2f2eeb9434278115a651df3c13791f94c21821097885 (tree art:07ee42d4…)
  - p1 2048: result art:7fed2ea586c24be28ee3d9c36d59fd6a59b4d09cc7024c464607a84602778fd3 (tree art:2b0677a2…)
  - p2 4096: result art:294ad179d2f58bf77c20e26f1dfa9a206c61a5f64fbf97a15dd8555f6fe33df0 (tree art:cced69d5…)
  - p3 8192: result art:642bb0d61111d328d7ef66b963f55c0884fc8b5e36dcbc4598886815be7ba95b (tree art:74992b10…)
  - **plateau 16384: result art:d6328cf5ef00648038cb35a171f212ee39a9d5f341c1f049ce4a7eb1671f874e, tree (proofs, 5.4 GB)
    art:0269046e49e47beda0cf6801812669f0628f8608236a1d5ce3d9234b6f065c77**
  - standalone cell 6238 (4096, not a sweep point): result art:5d20ad00f5e7b251987cfc58998199e7c8ee8e35fd935d9a0c9dfb5ad1853a40
    (tree art:3e64461f…)
* 08:19Z r20260925-081917-0039 (`50-fixcheck.sh`, tree 8dace837): ligero-verify rebuilt (sha256 e1ed499c…), cargo test
  33 + 7 + 27 passed; pytest hashauth_test + sweep_vu_test + blake3_test 20 passed. **Red team's rtsh_remap_e2e.py
  (8ace1ada), plain and --set-binding: rc 1 "not reproduced"** -- the forgery (VU 0 on x row 1 / W column 1) is refused by
  Python and Rust with "auth: a VU's x row / W column is not the one its index fixes in the committed layout"; the honest-
  mapping control stays rejected (y root mismatch); reverify FAILs the harness's dump (no `set` block: fail closed). The R2
  step of that script was wrong (it passed the manifest's base name `fp8-ada` as the pinned relation, so recomputed under
  the Poseidon2 schema -- the statement's a binding dfac8627… IS the blake3-schema binding, checked by hand) and picked a
  point whose proofs were dropped; redone as `51-r2check.sh` (r20260925-083225-a0a4).
* 08:19Z r20260925-081954-2ebd (`55-xob.sh`): **XOR-output-bits BLAKE3 prototype** (`leaf/blake3_xob.py`, 8dace837; survey
  §3.2 / §4.2 "prototype first: a CPU census"): numpy-interpreter tests 4 passed (compression == compress_np on random
  cv / msg / counter / flags, limb-only cv[0..3] and constant-counter shapes; a flipped XOR-output bit / carry / square-pair
  product breaks a constraint). **Census: 11 746 rows per 64-byte block against the pinned gadget's 15 139 on the same
  inputs (0.776x)**: 7 168 bit + 3 778 product + 800 sel rows. Per VU (fp8, 48 blocks): 563 808 hash rows vs 726 672. It
  needs a new witness op (`xadd`: bits of other ^ (lo + 2^16 hi mod 2^32)) in every generator (witness.py, the 4
  witness_device forms) and new pins -- not wired; see Decisions.
* 08:33Z r20260925-083225-a0a4 (`51-r2check.sh`, tree de2fa317, the plateau dump): **R2 honest: `commitment_problems`
  (True, []) in 49.9 s; `verify_tree` PASS 193/193 with hashed=True in 105.7 s**. Negatives on copied statements, each
  FAIL: wrong `set` digest (a/b bindings differ), a flipped root, a removed statement (16 299 / 16 384 VUs covered);
  restored control PASS. Pinned relation = the manifest's `statement_relation` (fp8-ada+blake3).
* 08:35Z red team (inbox 0835Z): R1 closed (art:9fa210e7…); **R4** (art:c7683eb2…): coverage counted statements whose proof
  is missing (Rust `batch --dir` verifies `*.proof` only). Fix 07e5cf98 + 5c7c4488: `per_rep` comes from the manifest's
  entries that have a proof; a rep whose `*.stmt` stems, `*.proof` stems and proof entries differ, a stmt entry without a
  proof, a proof paired with another stem's stmt, or an unreadable statement is a layout problem (FAIL); a hashed dump
  requires the batch's `n` = the statements counted; `hashed` is decided from the pinned relation (`+`) or any hash_auth.
  r20260925-083926-0584 (`52-r4check.sh`, 07e5cf98): **red team's rtsh_orphan_e2e.py (21393756) rc 1 "not reproduced"**:
  control PASS; orphan-stmt and stmt-entry variants FAIL (layout); honest plateau (True, []); a proof removed from a
  symlinked copy -> "rep1: 193 statements, 192 proofs, 193 manifest proof entries (not the same files: ['sub_07'])".
  r20260925-084339-014c (`53-unit.sh`, 5c7c4488): reverify_test + hashauth_test 12 passed; R4 check re-run on the tip.
* 08:45Z ligero-steps-pin (inbox 0845Z) had cherry-picked my R1 / R2 unchanged (71905f0f / 3e98dc55) and made its own R4
  (06176b41). **Merged origin/lane/ligero-steps-pin at fcf9a35b, taking its reverify.py / hashauth_test.py** (mine superseded;
  one R4 in the coordinator's merge). r20260925-084934-4816 on it: the R4 harness is not reproduced; honest (True, []);
  proof removed -> refused; verify_tree PASS 193/193. But **3 reverify_test cases FAIL** ("truncated file": 06176b41 parses
  every `.stmt`, including the test's stand-ins) -> 806a2f73 (unreadable statement = a problem of a hashed dump) ->
  r20260925-085649-8d76: 15 passed. Handoff lanes/ligero-steps-pin/20260925T0900Z (cherry-pick 806a2f73).
* 08:47Z coordinator (inbox 0847Z): merge origin/main (commit-gpu's GPU committer) before measured runs. **Merged main
  94b1c4d2 at 0ab2544f**. Conflicts: hashauth.build_row_tree -> main's batched `leaf_hashes`; run.py / relchain.py: my
  `--commit-per-rep` and commit-gpu's `--commit-reps` / `--commit-evidence` are kept as exclusive options; the first build's
  evidence is kept under per-rep too, and every per-rep recommit must reproduce its tree refs. Note on accounting:
  commit-gpu's commit.seconds includes the prover's chain states, while my per-rep commit.seconds puts them in t.witness;
  e2e is the same sum.
* 08:52Z the pod's /workspace/src was synced once from the wrong worktree (poseidon-v1: the shell's cwd had drifted),
  with no run on it. Re-synced from this worktree; every run since stamps its commit. Now `cd` explicitly before `research pods sync`.
* 09:04Z r20260925-090404-6311 (`62-r2-smoke.sh`, tree 806a2f73). **R2 on the tip**: honest (True, []), verify_tree PASS
  193/193 hashed=True. The negatives now keep the proofs in place (symlinked), so R4 holds and R2 is what is tested:
  - wrong set digest -> "the regenerated fp8-ada set of 16384 VUs has manifest digest b8722924…, the dump claims 0000…";
  - flipped root -> "tree a root differ from the instance set's";
  - statement + proof + entry removed -> "statements cover 16299 distinct VUs of [0, 16384)";
  - restored control (True, []).
  (The first try, in r20260925-084934-4816, copied statements only, so R4 masked R2; and 51 / 52 shared a scratch dir.)
  **GPU committer smoke** (frame_gpu_test + test_frame_v3: 94 passed), fp8-ada+blake3, 4096 VUs, l = 4096, p2, 2 reps,
  `--commit-per-rep`, not a Table 2 point:

  | committer | commit.seconds | t.total | e2e | VU/s |
  |---|---|---|---|---|
  | device (LIGERO_COMMIT_GPU=1) | 0.0107 s | 3.630 s | 3.640 s | 1125 |
  | host (LIGERO_COMMIT_GPU=0) | 0.058 s | 4.423 s | 4.481 s | 914 |

  The row chains in t.witness fell from ~0.8 s to 0.002 s per rep. **--commit-evidence is equal, device vs host**
  (sha256 f62b873f…; roots a = 2f9ff265…, b = 0413c926…).
  Before main, the 4096 cell was commit 0.646 s + t.total 4.31 s = 4.96 s (826 VU/s).
* 09:13Z r20260925-091311-104c (`60-fold.sh`, 806a2f73): **fp8-ada-x4+blake3 probe**, 4096 VUs, 2 reps, `--commit-per-rep`,
  GPU committer. The system is 79 184 rows per column (12 columns per VU); 341 VUs per proof at l = 4096.

  | l : p | e2e | VU/s | commit | t.total | peak GPU mem |
  |---|---|---|---|---|---|
  | **4096 : 2** | **2.049 s** | **1999** | 0.009 s | 2.040 s | 18.1 GB |
  | 2048 : 2 | 2.457 s | 1667 | | | 9.7 GB |
  | 2048 : 3 | 2.188 s | 1872 | | | 13.3 GB |
  | 4096 : 3 | CUDA OOM (tried 4.84 GiB with 21.2 GiB in use) | | | | |

  Against x1 on the same tree (1125 VU/s), x4 is **1.78× the throughput**, matching ~1.8× fewer rows per VU.
* 09:20Z red team (inbox 0920Z), run rtsh-bls-806a2f73 on its own pod, ligero-verify built from 806a2f73 (sha256
  61bc2281…), art:be211735b6d944ff9645f93a6ea82f3a3882ac0612f69b4740b87503b53e2a93: **R1 remap, R4 orphan (both variants)
  and H2 steps 64 all refused; control PASS; gadget review of leaf/blake3.py + hashchain.py: no finding**. Agrees that a
  shared / tile dump failing closed on `set.tile` is the safe direction.
* 09:19Z **x4 sweep r20260925-091922-a390** (`30-sweep.sh`, REL = fp8-ada-x4+blake3, l = 4096, p2, 5 reps, custody-r2 8h).
* 09:40Z **x4 sweep DONE** (rc 0, 1209 s): 1559.1 / 1832.5 / 2006.9 / **2108.7** / 1875.5 VU/s at 1024 .. 16384. It stopped
  on "< 2 % over two doublings" -> `sweep` {plateau: true, point 3, 8192 VUs}.
  - **Plateau 8192:** t.total 3.870 s + commit 0.0148 s = e2e 3.885 s; overhead 5.10e7× vs native peak; 128.05 bits
    (target 2^-128); peak 18.7 GB. That is 25 sub-batches of <= 341 VUs.
  - The pod's ligero-verify (e1ed499c…) on rep 1: batch ACCEPT 25/25, union 2^-128.05, system-digest 1168788f… =
    the fp8-ada-x4+blake3 pin.
  - 4096 point: t.total 2.032 s + commit 0.0088 s = e2e 2.041 s (5.36e7×, 128.33 bits).

  Registered 09:41Z (all PRESERVED; `40-register.sh` over `research pods ssh`):
  - p0 1024: result art:0320e7a78e2aa91af8a3f977012285b693fe66746a842d2f3d21f89f9bc82f66 (tree art:83240748…)
  - p1 2048: result art:e8af8d31bb9e052e71e89ad7c0260c0ce162f0822e256af6750c4edca758f167 (tree art:168856bc…)
  - p2 4096: result art:b281a6602cea7308a62ca6c747a7f6740e9118955a4b18eafaa94c9c3a478af9 (tree art:2ec81a36…)
  - **plateau 8192: result art:6b6d4484c7a3911946431ec8a7d3ef609137274157003e47654313d25be77631, tree (proofs, 1.6 GB)
    art:f35d43aa392b154f2af73bc41920ce1dc17c96b58d9ccd5a608aed9ebf7a453f**
  - p4 16384: result art:82a3e0ba7b0b2b5c4c7be9032cc812d2b37f0ca3017e3e94fdce07864d5ae2dc (tree art:d628331e…)
* 09:42Z r20260925-094242-269c (`20-cell.sh`, REL = fp8-ada+blake3, 4096 frozen, l = 4096, p2, 5 reps, custody-r2): the x1
  cell re-measured on the GPU committer, with proofs kept. **fp8-ada+blake3 4096 frozen:** t.total 3.574 s + commit
  0.011 s = e2e 3.585 s (1142 VU/s, 9.41e7×, 128.40 bits). Pod Rust batch ACCEPT 49/49, 2^-128.40, pinned 71f39e44….
  Result art:e7d59ab6a7bad2140c776f1d160efa302f46439ea1ceda9edff68d228a6df022, tree
  art:08225c8c209777cde883d544ed19b59704b2e9d3e8c60000137b5f2cdbfa1c4a.
* 09:48Z r20260925-094821-b197 (`20-cell.sh`, REL = fp8-ada-x4+blake3, 4096). **x4 4096:** t.total 2.038 s + commit 0.009 s =
  e2e 2.048 s (2000 VU/s, 5.38e7×, 128.33 bits). Rust batch ACCEPT 13/13, 2^-128.33, pinned 1168788f…. Result
  art:017a706919fd4f694ab7bfa25f63e3123a1fbd2ddd7b0bb0aff800cb447c2ae4, tree
  art:0a95eb1e36bf2003501911d5d7983eb2c39a9356635994007ac60eab78ebc240. The instances are the relation-named manifest
  c86e51a1… (counts via instance-equiv).
  Both registered 09:53Z. Handoff: lanes/verify-night-2/20260925T0958Z (the 2 cells + the x4 plateau).
* 09:53Z r20260925-095340-c456 (`63-live.sh`): the x1 frozen cell against a same-pod live verifier (niced, 127.0.0.1:7000,
  its own coins, pod ligero-verify), rep 1 dumped (coordinator 0915Z, decision 2). **DONE** (bench rc 0, 527 s): the live
  verifier ACCEPTED 49/49 in each of the 5 recorded reps (interactive: "coins are this verifier's step-0 coins";
  included-hash).
  - Timing: t.total 3.585 s, t.total_live 3.592 s, commit 0.010 s, e2e 3.596 s (1139 VU/s, 9.44e7×), 128.40 bits.
  - Network: rtt median 0.55 ms, 7.37 GB out per 5 reps, net wait 0.006 s; verify.wall 128 s / cpu 127 s per rep.
  - Rust batch on the dumped rep 1: ACCEPT 49/49 against its own (live) coins, 2^-128.40, pinned.
  Registered 10:05Z with the session records (2.9 MB: hello / session / verdict json, coins, index, serve.log; not the
  6.8 GB of session proof copies). Result art:e9932b72b71ed81a6d4a94ea62e36bc3f1db521258c9237744c5c31459ca71ee, tree
  art:6a36cde712108a60fe919043996cfdeda11e06a93e583544bd1438b09966742c. Same pod as the prover, niced: the verifier's
  process and coins are its own, not its machine.
* 10:03Z coordinator (inbox 1003Z): export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 in measured runs. Now in
  lib.sh, and passed as `--env` on the run (so job.json records it). Every cell above was measured WITHOUT it; they stand
  as they are, and re-measured cells are new results.
* 10:25Z red-team-link (inbox 1025Z, FYI): Link L is CLEARED WITH CONDITIONS C1-C4. For this lane, route (a) is also blocked
  for COMPLETE_ZK_BACKEND until Flock has ZK: it needs a two-tableau Ligero with a joint test, a third HM96 coin slot, and
  a larger t for ε_B. Not built here: the coordinator parked the binary / link routes (0752Z).
* 10:05Z r20260925-100526-b232: the x4 sweep again, **with the malloc env** (30-sweep.sh, l = 4096, p2, custody-r2).
  **DONE** 10:27Z (rc 0, 1184 s): 1636.1 / 1891.9 / 2067.8 / **2165.0** / 1943.0 VU/s at 1024 .. 16384, so the malloc env is
  +2.7 % at the plateau. The plateau is again 8192 ("< 2 % over two doublings").
  - **Plateau:** t.total 3.768 s + commit 0.0157 s = e2e 3.784 s (4.97e7×, 128.05 bits, peak 18.7 GB).
  - Rust batch ACCEPT 25/25, 2^-128.05, pinned 1168788f….
  - 4096 point: e2e 1.981 s (2068 VU/s).

  Registered 10:28Z (PRESERVED):
  - p0: art:29babef7db74c0846d2d2c3bc399bdaed177ed59e5476830c8f7a85839b26c63
  - p1: art:71968345a826a7157e5c5713a045485dea126e97b3a2e1f0f0fd6aa39e8334a9
  - p2: art:fdee8f4dcf5672fa63b697a1eb90b3898ddce995d5dc8cfec50e32ac5aa6c84d
  - **plateau: art:19be6afa2cd2239cf15f7878af8eae0a3523be86dbec8e92f3acd9d6ee3ebbd1 (tree
    art:a3d4b768d9808c55be90c98bd54fa10b5dd993faec8e2cb90a622bd912862e3a)**
  - p4: art:763754456315ceb8e5376bad26eb4a100a0cc01210b9569e1e3882b67ea8895a

  (These labels carry the lane prefix twice: 40-register.sh adds it, and I passed it too. Cosmetic.)
* 10:29Z r20260925-102900-4391 (`22-cells.sh`): the x1 + x4 4096 cells with the malloc env. DONE; both registered 10:35Z.

  | cell | t.total | commit | e2e | VU/s | overhead | bits | Rust batch (pinned) |
  |---|---|---|---|---|---|---|---|
  | **fp8-ada+blake3 4096 frozen** | 3.547 s | 0.0109 s | **3.558 s** | 1151 | 9.34e7× | 128.40 | ACCEPT 49/49 |
  | **fp8-ada-x4+blake3 4096** | 1.973 s | 0.0088 s | **1.981 s** | 2067 | 5.20e7× | 128.33 | ACCEPT 13/13 |

  - x1: result art:9b80f566838f4956ecc85df853c718ddfe07a5af8682dd69f29b3c7df75ae611, tree
    art:0c5840907e1c24fe8190d0af2b0e32763494ba413b939e0b8d8cf9195f569b4e.
  - x4: result art:050ddede1083ac67f417d2345d5b1f0a8d47314c94ee5a9988d7f1cdb8300650, tree
    art:ef264ad325e8207dae1b75b2d09b35d13cfbfe1b1c717bc40592afd69043df62.
* 10:36Z r20260925-103611-67e0: the x1 (fp8-ada+blake3) sweep with the malloc env, on the GPU committer (30-sweep.sh,
  l = 4096, p2, custody-r2). DONE 11:06Z (sweep rc 0, 1789 s). Measured points: 1073.4 / 1128.2 / 1150.3 / 1175.9 /
  **1185.5** VU/s at 1024 .. 16384.
  - **The 32768 point was killed (rc -9, host OOM).** Likely cause: MALLOC_TRIM_THRESHOLD_ = 1e12 never gives freed heap
    back, and the in-process verifier holds 386 proofs. So the sweep stopped on "a point failed", and the rule (two
    doublings < 2 %) was NOT met: 16384 is +3.06 % over 4096, though only +0.81 % over 8192. The plateau is the highest
    measured point, not a converged one.
  - **Plateau 16384:** t.total 13.787 s + commit 0.0335 s = e2e 13.821 s (9.07e7×).
  - Rust batch (pinned 71f39e44…) ACCEPT 193/193 against their own coins, 2^-128.40.
  - 4096 point: e2e 3.561 s (1150 VU/s), matching the 22-cells 4096 cell (3.558 s).

  Registered 11:17-11:19Z (PRESERVED; the points without proofs are SLIM):
  - p0: art:998f341701303ed546a94df2d8fd997d823a468dcb35a9369ee8a01a62d09ec1
  - p1: art:c3348ffe8250ae9b9b385f373a688c7a4e27a6f708d5ebcb8f0c88afef42d300
  - p2: art:69065ce3cae387f29576b96f79a24a0f82086e8441423b29118cea59dec7e8f3
  - p3: art:a149135673510096392ed08b038fb9170d3f235a2f5cb05621211cd69c25a31f
  - **plateau with rep-1 proofs: art:c9f4a645c2271c64187a2d2e8d116a5c34b0f465c9fd4ddc333d4ce7887dec1d (tree
    art:443b52fd8c9a4ace5e31d7d263a01d719eb44d67576f3168d31d0e5f067feb67)**. The SLIM copy
    art:6cdb785a4f9121b84a8d80b10abff66608899078dc5955fcfaef9f0a8326c542 has no .proof files; use the one above.
* 10:40-10:55Z XOB wired (coordinator 0915Z: after the first CLEARED cell, under a NEW scheme name). Lane tip e19bc365 /
  ce86046b / fb29b130:
  - the `xadd` program op (32 boolean rows = bits of `((lo + 2^16 hi) mod 2^32) ^ (olo + 2^16 ohi)`) in every witness
    generator: the torch program (`witness._run_program`), the register and table CUDA codegens, and the sequential and
    level-scheduled interpreter kernels (op kind 6, operands o[2..5], 32 rows written);
  - leaf scheme **`blake3-xob`** (`leaf/blake3_xob.Blake3XobLeaf`, a `Blake3Leaf` subclass): its column compression is
    `compress_xob` (204 rows per G instead of 268), and everything else is `Blake3Leaf`'s. That covers native, carry,
    leaf_bytes, keys, framing, digest layout and the GPU committer (`frame_gpu.ROW_SCHEMES`). **Same schema
    `blake3-keyed/row/v2`**: it is frame-v3's core keyed-BLAKE3 row schema, so a +blake3-xob commitment is byte-identical to a
    +blake3 one. Only the circuit, and so the system pins, differ. `Blake3Leaf.gadget` now calls `self._compress`, which
    emits the pinned finalisation rows in their old order (the 71f39e44 pin must survive; this is checked on the pod);
  - conformance: "schema / params identify the scheme" becomes "identify the LEAF". Schemes sharing a schema must share
    params, digest / carry layout and `leaf_bytes` / `native`. A statement relabelled to its twin's suffix parses, but its
    proof must not verify against the twin's system (new negative). `by_schema` returns the first registered scheme
    (blake3);
  - Rust: `leaf::BLAKE3_XOB` (the same schema, params and `blake3_leaf_bytes`) is in `SCHEMES`. No PINS row yet.
  - new tests in `blake3_xob_test.py`: xadd in all five generators against the numpy interpreter (CUDA), and the scheme's rows
    per column = pinned - (15139 - 11746).
* 11:20Z r20260925-112012-8420 (64-xob.sh, tree 672b23ae):
  - pytest `blake3_xob_test` + `witness_device_test` + `leaf_test`: **27 passed**.
  - conformance `-k blake3`: **16 passed, 2 skipped**. The skips are the Rust fixture helper: `ligero_verify_binary` looks in
    `backends/ligero-verify/target` and on PATH, and the pod's binary is `/workspace/bin`, which is on neither.
  - Fixtures, with system digests from the pod's ligero-verify:

    | fixture | sys | table | rows | hash rows |
    |---|---|---|---|---|
    | fp8-ada+blake3 (**pin 71f39e44… kept**, so the `_compress` refactor emits the same system) | 71f39e44… | bbacbe7a… | 35,370 | 30,798 |
    | **fp8-ada+blake3-xob** | 3d6cc67b… | a655b6b8… | **28,584 (-19.2 %)** | **24,012 (-22.0 %)** |
    | **fp8-ada-x4+blake3-xob** | f90e7b41… | 6ecf18da… | 65,612 | 47,822 |

  - The x1 xob fixture took 6.5 min (x1 blake3: 17 s; x4 xob: 1.5 min), single-threaded on the CPU with the GPU idle. The
    phase is not yet known; the gate / bench logs will time the compile.
  - PINS rows for both are in 5b28557b.
* 11:24-11:40Z (coordinator 1105Z / 1114Z, rule I for x4): **instance-equiv/v1 art:6fdeed7efc48da01c5c84b0e910c358bab725f01abdf2a79888d47ef25f47bc5**
  (PRESERVED; the meta is the document).
  - Derived by `instance_equiv --relation fp8-ada-x4 --vus 4096` at 672b23ae, and `--check` reproduces it. equal: x / W / y
    are d64fec05… / f7cb2046… / 27cdcef1… on both sides.
  - candidate = art:017a7069's ref (c86e51a1…).
  - The 8192 prefix, `instances(x4, 8192)[:4096]`, equals the frozen arrays (`evidence/equiv/prefix-fp8-ada-x4-8192.json`).
    The schema can't express that, so I sent it to the coordinator.
  - Script 42-equiv.sh, run over ssh. The first launch piped the script over stdin, which `research pods ssh` does not
    forward, so the file arrived empty; resent base64-encoded.
  - Tool bug: REPO = parents[4], so the tool field is `@unknown`.
  - Handoffs: verify-night-2 1142Z, coordinator 1142Z.
* 11:43Z r20260925-114349-ea8d (65-xob-pin.sh): the Rust rebuild with the xob pins, cargo test, the pinned batch of the
  11:39Z fixtures, then the gates of fp8-ada / fp8-ada-x4 under blake3-xob. The red-team class review was requested
  (red-team-standard-hash 1150Z).
  - Rust build 12 s (ligero-verify 2562ed47…); cargo test 34 + 7 + 27 passed.
  - Pinned batch ACCEPT for all three fixtures: fp8-ada+blake3, fp8-ada+blake3-xob and fp8-ada-x4+blake3-xob, each
    "system pinned".
  - **gate fp8-ada+blake3-xob: 25 honest sub-batches, 86 negatives, 0 failures (36 s).**
  - **gate fp8-ada-x4+blake3-xob: 7 honest sub-batches, 86 negatives, 0 failures (43 s).**
  - The fixtures took 17 s each here, so the 6.5 min at 11:33Z was a first-run cost.
* 11:51Z r20260925-115150-1f42 (22-cells.sh, custody-r2, malloc env, tree 5b28557b): **the blake3-xob cells, PROVISIONAL
  (the class is pending red-team review)**.

  | cell | t.total | commit | e2e | VU/s | overhead | bits | Rust batch (pinned) | peak GPU |
  |---|---|---|---|---|---|---|---|---|
  | fp8-ada+blake3-xob 4096 frozen (e66ff0f2) | 1.963 s | 0.0103 s | **1.974 s** | 2075 | 5.18e7× | 128.40 | ACCEPT 49/49 | 7.0 GB |
  | fp8-ada-x4+blake3-xob 4096 (c86e51a1) | 0.790 s | 0.0091 s | **0.799 s** | 5127 | 2.10e7× | 128.33 | ACCEPT 13/13 | 15.2 GB |

  **Against +blake3 (r..102900-4391, tree 806a2f73):**
  - x1: 3.558 s → 1.974 s (1.80×). Encoding + commitment 1.937 → 1.098 s, arithmetic 1.169 → 0.576 s.
  - x4: 1.981 s → 0.799 s (2.48×). Encoding + commitment 1.200 → 0.336 s, arithmetic 0.608 → 0.290 s. Peak GPU 18.1 → 15.2 GB.

  **This is far more than the row ratio: 0.81 at x1 and 0.83 at x4 would give about 1.2×.** Unexplained. Two confounds I can
  test: (a) the tree, since 806a2f73 predates main 767115db; (b) GPU memory pressure at p2 for the pinned x4 system. For (a),
  the same-tree control is r20260925-120625-4b74: +blake3 x1 and x4 re-measured at 5b28557b.
  - **Control DONE (12:06-12:12Z, same pod, flags and tree):**
    - fp8-ada+blake3: t.total 3.528 s + commit 0.0103 s = **e2e 3.539 s** (1158 VU/s, 9.29e7×); encoding + commitment
      2.023 s, arithmetic 1.157 s. ACCEPT 49/49, 2^-128.40.
    - fp8-ada-x4+blake3: 1.969 s + 0.0087 s = **e2e 1.977 s** (2072 VU/s, 5.19e7×); encoding + commitment 1.158 s,
      arithmetic 0.614 s. ACCEPT 13/13, 2^-128.33.
  - **So the tree is not the cause: the xob speed-up (1.79× x1, 2.47× x4) holds on one tree.** What does track it is the
    number of product rows:

    | | x1 | x4 |
    |---|---|---|
    | product rows | 15 085 → 8 043 (0.53×) | 30 821 → 16 737 (0.54×) |
    | total rows | 0.81× | 0.83× |
    | arithmetic speed-up | 2.0× | 2.1× |

    The xob design adds cheap boolean `r·r = r` quadratics and removes general products (one per XOR bit). Hypothesis, not
    shown: the prover's cost follows the general products, not m. Possibly the x4 encoding also gains from less memory
    pressure at p2 (18.1 → 15.2 GB peak).
  - Registered 12:13-12:14Z (PRESERVED):

    | cell | result | tree |
    |---|---|---|
    | xob x1 4096 frozen (PROVISIONAL) | art:b47828e4a584ff5b9e75cd171f467dc0a583115a67bb978083b4fdd61c13b32a | art:b33bc6f45d3711a933f6a1a04b599950af87d98807a97e89eb2de35ecfe38876 |
    | xob x4 4096 (PROVISIONAL) | art:bb69174bbe23bb356649fc77896b9402161c4e6c5df68e0e2a0379159c559079 | art:c32f3385afc28b8b777db07a8932b0737bdd61dd87d9754690ebe6f3450ed3cf |
    | control +blake3 x1 4096 frozen at 5b28557b | art:448029fe222f48c2339978fa9eb44db9b4e82ef48d4e979acee6c8b1d0ea04db | art:118fc65941d0bd060d6bc4cb97a021d92e973767dd8163cc1f61622cddda0cef |
    | control +blake3 x4 4096 at 5b28557b | art:49b345a825225fa624a3ddb9238657326fff22f5e29e14161f1c78bc4c1b4e43 | art:7ab931c9c87459d347785bc26f3acb1700bd4bd40a64aa513e0abb1c4e2c3d5e |
* 12:16Z r20260925-121605-357f: the x4+blake3-xob plateau sweep (30-sweep.sh, l = 4096, p2, malloc env, custody-r2).
* 13:05Z x4+blake3-xob sweep done (PROVISIONAL, 5b28557b, sys f90e7b41 / table 6ecf18da): 1024..32768 VUs ->
  4118.8 / 4737.2 / 5189.0 / 5506.4 / 5626.5 / 5676.1 VU/s; 65536 = CUDA OOM (rc 1). Plateau 32768: t.total 5.723 +
  commit 0.050 = e2e 5.773 s, 1.89e7x, Rust ACCEPT 97/97 at 2^-128.07 (pinned, python 97/97), peak GPU 19.0 GB. NOT
  converged (+0.9% over 16384, +3.1% over 8192); the ceiling is 24 GB VRAM. Registered (result / tree):
    | point | result | tree |
    |---|---|---|
    | p0 1024 (SLIM) | art:63e59ddbc1ffad1a606925d92ef65be13e2bec0a06e945c270203967827765e1 | art:b04fc1b3e82721777eced4878f0764ea87f0090f39e77e90c8d3a196c4d945cd |
    | p1 2048 (SLIM) | art:61abf20af35b46c9d70859c392acbae8cecbce37fb8ab74a89dc9080f05bc35c | art:d39724ce0e538af6014fc6ab6d789ddca995a224cfcfa366622210abd961c9ad |
    | p2 4096 (SLIM) | art:dd89a954af15e9be4c22d26e314b61de4d61257c68f20a767d2235a96acd638d | art:43df4b2be9960c33b63646627a5bdda7b4e946cbb0c11e52c8a4915dd24b1793 |
    | p3 8192 (SLIM) | art:c8a08e21205833bc2bb7a129bd2a3898384df60235ddcdb361ca3582a3e36596 | art:76a1047708b35a61153582555f2791ec31dafe4c08dd891f8b2ce1e35102d7ac |
    | p4 16384 (SLIM) | art:d3e2f8a4b40724d79a8d9ca6e6d30787779b7acd3c0b9c87378309d9ec50bc3e | art:ef970fa6dcd3e9532808aa9a39956964f57e82f71c3f128439c3bc27d008d6c5 |
    | plateau 32768 (proofs) | art:ecccca50500cecececefcd7dfb4aa97572a1e334332f1c191744489fbeccf82a | art:0785fd3dffe9bb80fcdc3cb3feae85bf32dd22c8b4b4fc06248d8f2e7e9bc5a6 |
  x4 points above 4096 use instances beyond the frozen 4096 (prefix rule, coordinator decision pending).
* 13:07Z r20260925-130720-ab7a: the x1+blake3-xob plateau sweep (same settings, MAX = 32768).
* 13:10-13:20Z: read red-team 1226Z (**blake3-xob CLASS GRANTED WITH CONDITIONS**: re-verify from ≥ 5b28557b or 06, 04 BOUND
  ≤ 2^-128, run at 5b28557b / 672b23ae; 0 free rows in both shapes; twin relabel refused both ways; H2 / R1 / R4 pass) and
  verify-night-2 1230Z (the controls are queued at main; the xob pair goes through a second verifier, main plus my diff).
  I had missed coordinator 1124Z / 1125Z (PR #21: instance-equiv/v1 can reference the synthetic stream past 4096; do only 8192).
  - The pod tree predates PR #21 and a sweep was running from it, so 43-equiv-8192.sh overlays main 2c92b9e3's
    `bench/{instance_equiv,tables,views}.py` on a copy of verity_numerical. There is no relchain / relations diff, and it
    runs at nice 19 with 8 procs. The sweep's points stayed `contended=False`.
  - **x4 8192: art:d9b3724db1d21db49cbd399642685f1a2b4aa8d21d4bab3b6c7623caaf0ca7f3.** frozen = the stream over [0, 8192]
    (35a95ed5…); candidate 5ca6851d… (art:6b6d4484's ref); equal, and `--check` reproduces it.
  - **x4 32768: art:b6f2e1dfcc3473058aad66d1aa271b4828140f3e667ef646ee176ca81a26109a.** frozen a80b38f2…; candidate
    fd076a29… (the x4 xob plateau art:ecccca50's ref); equal, and it reproduces.
  - The documents are in `evidence/equiv/`.
  - Handoffs: verify-night-2 1315Z (both documents, the x4 xob plateau), coordinator 1320Z (the same, plus the merge
    decision for blake3-xob), red-team 1320Z (the three xob cells in scope).
* kb: new `kb/ligero-hash-auth.md` (R1 / R2 / R4 rules, pinned-relation pitfall, gadget rows, x1 waste, plateau).
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
