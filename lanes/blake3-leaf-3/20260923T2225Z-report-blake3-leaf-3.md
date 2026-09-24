---
lane: blake3-leaf-3
kind: report
created: 2026-09-23T22:25Z
status: open
---

CHECKPOINT 820aa6fe (22:56Z) [open] FINAL section written (820aa6f): fp8+blake3 p4 5.22 s / best 4.70 s (l4096 p2), bf16+blake3 p4 10.70 s; Rust ACCEPT all 14 dumps; art ids on R2. Re-running the 86-negative gates on 820aa6f before terminating the pod.
CHECKPOINT 820aa6f (22:40Z) [open] 820aa6f level-scheduled witness interpreter (the sequential one is 126 ms/sub-batch = ~95% of +blake3 commit). Rust batch ACCEPT on all 11 dumps (pinned). p4 rows: fp8+blake3 l2048 11.81 s, bf16+blake3 l2048 25.30 s; fp8 l4096 p2 6.87 s. +shared blake3 structurally unsupported (share-logup-3 Poseidon2-only). Re-benching with the level kernel now.
CHECKPOINT 4d8668b (22:31Z) [open] controls p4 l=16384: fp8 bare 0.170 / +hash 0.421; bf16 bare 0.261 / +hash 0.805. fp8-ada+blake3 l=2048 p4 11.81 s (worse than l=4096 p2 6.89: device-bound, 2x openings). bf16+blake3 l=2048 p4 running; then same-l controls, l=4096 p2/p3, Rust batch, witness-kernel attribution.
CHECKPOINT 4d8668b (22:23Z) [open] 4d8668b = 1db0008 + cherry-pick ajtai-leaf-2 1cf9178 (pipelined hashed runner). Pod bench driver running (controls l=16384 p4, +blake3 l=2048 p4 since l=4096 p4 OOMs, l=4096 p2). Predecessor's unreported pod numbers recovered into §0b.
CHECKPOINT 4d8668b (22:25Z) [open] started; worktree ~/projects/verity-main-wt/blake3-leaf-3 on lane/blake3-leaf-3 @ 1db0008 (predecessor tip; predecessor worktree clean, nothing to carry) + cherry-pick of lane/ajtai-leaf-2 1cf9178 (HashedRelationRunner.prove_vus_many) as 4d8668b (one conflict: kept my branch's ZK note, took only the pipeline_depth line). Next: sync to pod ghpl8iy5s629sq, benches at --pipeline 4.

# Lane blake3-leaf-3 — BLAKE3 leaf benches at `--pipeline 4` vs bare and Poseidon2 (continues blake3-leaf-2 @ 1db0008)

## 0. Starting state
* Predecessor `lane/blake3-leaf-2` @ 1db0008: gates 0 failures (`fp8-ada+blake3` 25 honest + 86 negatives, `bf16-hopper+blake3`
  49 + 86, `fp8-ada-x4+blake3` 13 + 86), v2 Rust pins (fp8-ada+blake3 71f39e44…, bf16-hopper+blake3 58ef7097…, x4 1168788f…),
  fixtures on R2 art:a2e7503c / art:78121b22 / art:51b6e9e0, gate logs art:02d4da16, Rust evidence art:cb077fab. Its finding: the
  hashed runner had no pipeline (`--pipeline 4` silently ignored for +hash / +blake3); `+blake3` at l = 8192 OOMed.
* Pipelined hashed runner: cherry-picked `lane/ajtai-leaf-2` 1cf9178 (`HashedRelationRunner.prove_vus_many`) onto this branch
  as 4d8668b; one conflict in `bench_vu_rel` (ajtai's F5 `leaf_privacy_note` ZK note is not on this branch: kept mine, took
  only `pipeline_depth = int(args.pipeline)` for hashed runners).

## 0b. What the predecessor measured on the pod after its last CHECKPOINT (21:10Z), never written up (`/workspace/lane2/bench_{b,c,d,e}.out`, results in `/workspace/bench2/`)
All 4096 VUs, `--zk --mode interactive`, local coins, 3 reps, 4090 ghpl8iy5s629sq. Rows 1-4 ran on the 1db0008 tree, where the hashed
runner ignored `--pipeline` (sequential); row 5 on a pod-only merge with share-logup-2 cfdcf65 (its `prove_vus_many`).

| run | l | pipeline | sub-batches | rows/unit | t.enc+commit | t.tests | **t.total** | peak | proof/rep |
|---|---|---|---|---|---|---|---|---|---|
| `fp8-ada+blake3` | 4096 | ignored (seq.) | 49 | 35 370 | 7.05 | 3.15 | **10.68 s** | 6.7 GB | 480 MB |
| `bf16-hopper+blake3` | 4096 | ignored (seq.) | 98 | 34 843 | 13.95 | 6.30 | **21.15 s** | 6.8 GB | 950 MB |
| `fp8-ada+blake3` | 8192 | -- | -- | 35 370 | | | **OOM** (warm-up's checked sub-batch) | | |
| `bf16-hopper+blake3` | 8192 | -- | -- | 34 843 | | | **OOM** | | |
| `fp8-ada+blake3` (merged tree) | 4096 | 2 | 49 | 35 370 | 4.75 | 2.05 | **6.89 s** | 9.6 GB | 480 MB |
| `fp8-ada+blake3` / `bf16-hopper+blake3` (merged) | 4096 | 4 | | | | | **OOM** (22.2 GiB allocated, 8.75 GiB in CUDA-graph pools) | | |
| `bf16-hopper+blake3` (merged) | 4096 | 2 | | | | | **OOM** | | |

Controls on the same pod then: fp8-ada bare p4 l=16384 0.168 s, p1 0.231 s; +hash (seq.) 0.539 s; +hash pipelined (merged) 0.438 s;
bf16-hopper bare p4 0.258 s, p1 0.395 s, +hash (seq.) 1.04 s, pipelined (merged) 0.800 s. Encode/Merkle microbenchmark
(`lane2/enc_mb.py`): SIMT encode + GPU column Merkle at m = 35 370, l = 4096 = 4.3 + 6.8 ms per sub-batch (~0.55 s over 49), so
the 4.75-7 s `t.encoding_commitment` of `+blake3` is NOT the encoder/Merkle kernels (to be attributed from the per-stage timings).
**l = 16384 is infeasible for `+blake3` on a 24 GB card** (l = 8192 OOMs even sequentially; the committed codeword alone is
35 370 x 65 536 x 4 B = 9.3 GB per sub-batch in flight): the p4 runs below use the largest l that fits.

## Log
* 22:18Z read brief §0/§1.3/§2/§3, predecessor reports (blake3-leaf, blake3-leaf-2), red-team-leaf-2 (nothing BLAKE3-specific
  beyond the role NIT already fixed in 30abee8), handoff. `lane/share-logup-3` does not exist yet (no `+shared` to run).
* 22:21Z tree synced to the pod as `/workspace/src3` (4d8668b, clean). Rust sources == the tree the pod's `ligero-verify` was built
  from (diff -rq), binary reused: sha256 4f0243da… .
* 22:23Z bench driver `/workspace/lane3/bench.sh` started: controls l=16384 p4 (bare, +hash) for both relations, then `+blake3`
  l=2048 p4, same-l controls, `+blake3` l=4096 p2.
* 22:25Z controls (this tree, pipelined hashed runner): fp8-ada bare p4 **0.170 s**, +hash p4 **0.421 s** (was 0.539 s when the
  hashed runner ignored `--pipeline`); bf16-hopper bare p4 **0.261 s**, +hash p4 **0.805 s** (was 1.04 s).
* 22:27Z `fp8-ada+blake3` l=2048 p4: **11.81 s** (98 sub-batches, 983 MB proof/rep, peak 8.0 GB): WORSE than the predecessor's
  l=4096 p2 (6.89 s). Halving l doubles the sub-batches and the openings (t = 203 columns x 35 370 rows per sub-batch), and p4
  hides little because a `+blake3` sub-batch is device-bound (see §2), not launch-bound like bare.
* 22:29Z `t.encoding_commitment` attribution: with the commit graph on, the `encode` lap is the whole graph replay (fused witness
  kernel -- for `+blake3` the program-independent interpreter kernel -- + masks + SIMT encode + column Merkle); the encode + Merkle
  kernels alone are ~11 ms / sub-batch at m = 35 370, l = 4096 (predecessor's microbenchmark) of ~144 ms. Direct timing of the
  witness kernel queued (`lane3/wit.py`).
* 22:32Z `bf16-hopper+blake3` l=2048 p4: **25.30 s** (196 sub-batches; its sequential l=4096 was 21.15 s). Same-l controls (l=2048
  p4): fp8-ada bare 0.290 s, +hash 0.546 s; bf16-hopper bare 0.485 s, +hash (see table).
* 22:34Z `fp8-ada+blake3` l=4096 p2 **6.868 s** (reproduces the predecessor's 6.889 s on the merged tree); `bf16-hopper+blake3`
  l=4096 p2 **OOM** (21.2 GiB allocated, 13.8 GiB in CUDA-graph pools).
* 22:35Z **witness-kernel attribution** (`lane3/wit.py`, kernel alone, random rows, 4090): the fused witness kernel per sub-batch is
  **126.2 ms** (fp8-ada+blake3, m = 35 370, l = 2048) / **125.1 ms** (bf16-hopper+blake3) vs Poseidon2 1.15 / 0.63 ms and bare
  1.03 / 0.56 ms (l = 16384); encode + Merkle at the `+blake3` shape 1.8 + 3.4 ms. **The witness kernel is ~95 % of `+blake3`'s
  commit graph**, and it is latency-bound: the sequential interpreter runs one thread per column (l = 2048 threads = 8 blocks of
  256 on 128 SMs), each through all ~35 k ops. That is why halving l does not make a sub-batch cheaper and p4 does not help.
* 22:36Z Rust batch (pinned `ligero-verify` sha256 4f0243da…, no `--allow-any-system`): **every dump ACCEPTED, every sub-batch**:
  fp8b3 l2048 p4 98/98 (2^-128.30, 17.5 s wall at 16 jobs), fp8b3 l4096 p2 49/49 (2^-128.40, 11.6 s), bf16b3 l2048 p4 196/196
  (2^-128.58, 33.6 s), and all 8 controls; `system_pinned = true` throughout.
* 22:38Z conformance `leaf/conformance_test.py -k pipelined` (the cherry-picked test, every registered scheme incl. blake3, CPU):
  3 passed. `+blake3` l=4096 **p3 OOMs** for both relations (so on 24 GB: fp8 fits l=4096 at p <= 2, bf16 only sequentially).
* 22:39Z **820aa6f: level-scheduled interpreter** (`witness_device.py`, `LIGERO_INTERP_LEVELS`, default on; `=0` = the sequential
  interpreter): ops grouped by dependency level on the host, one launch per level over (op, column) pairs; same per-op
  arithmetic; switches on only when every row has exactly one writer and no row is read before written; test
  `test_level_interpreter_equals_sequential_interpreter` + a W-identity check on the real `+blake3` systems before any bench.
* 22:40Z level vs sequential on the real `+blake3` systems: **W identical** (fp8-ada / bf16-hopper, l = 2048 / 4096); kernel 126 ->
  17.4 ms (l = 2048), 128 -> 24.1 ms (l = 4096); `witness_device_test.py -k interpreter` 4 passed on the pod (CUDA).
* 22:41-22:48Z re-benched with the level interpreter: fp8-ada+blake3 l=4096 p2 **4.700 s** (was 6.868), l=2048 p4 **5.224 s**
  (was 11.81); bf16-hopper+blake3 l=2048 p4 **10.70 s** (was 25.30). Rust batch: 49/49, 98/98, 196/196 ACCEPT, pinned.
* 22:49Z custody started (`lane3/custody.sh`): results tree + dumps of the p4 controls and the three level-interpreter runs. The
  superseded sequential-interpreter dumps `fp8b3_l2048_p4` / `bf16b3_l2048_p4` were deleted on the pod for disk (Rust verdicts,
  manifests with every proof's sha256 and system.bin kept in the results tree); `fp8b3_l4096_p2` and the l=2048 control dumps are
  not pushed (verdicts + manifests in the results tree).
* `+shared` BLAKE3: **structurally unsupported** on share-logup-3's tip 53452a6: `SharedHashedRunner.__init__` raises for any leaf
  but Poseidon2 ("row sharing hashes with Poseidon2 only (hashchain.row_hash_system)"). Not an execution failure; nothing to run.

## 1. Results (pod vy-blake3-leaf ghpl8iy5s629sq, RTX 4090 24 GB, same pod for every row, 22:23-22:50Z)
`bench-vu --zk --mode interactive --total-vus 4096 --reps 3 --target -128 --device cuda`, local coins, median of 3 reps; `--auth
included-hash` for `+hash` (Poseidon2) and `+blake3`; `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`. Tree 4d8668b (`/workspace/src3`)
for every row except `lv_*` = 820aa6f (`/workspace/src3b`, level-scheduled witness interpreter). Rust = `ligero-verify batch
--system system.bin --dir rep1 --target-bits 128 --jobs 16`, pinned systems, no `--allow-any-system`. `proof` and `stmt` are
per pass (4096 VUs; the dump size matches), not per 3 reps.

| run | tree | l | pipeline | sub-batches | rows/unit | t.enc+commit | t.tests | **t.total** | peak | proof/pass | stmt/pass | Rust batch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp8-ada bare | 4d8668b | 16384 | 4 | 13 | 3 769 | 0.058 | 0.075 | **0.170 s** | 6.6 GB | 66 MB | 14.5 MB | 13/13 ACCEPT 2^-128.32 |
| fp8-ada +hash (Poseidon2) | 4d8668b | 16384 | 4 | 13 | 6 210 | 0.084 | 0.240 | **0.421 s** | 10.7 GB | 91 MB | 1.18 MB | 13/13 ACCEPT 2^-128.32 |
| fp8-ada bare | 4d8668b | 2048 | 4 | 98 | 3 769 | 0.054 | 0.147 | **0.291 s** | 1.2 GB | 349 MB | 13.7 MB | 98/98 ACCEPT 2^-128.30 |
| fp8-ada +hash | 4d8668b | 2048 | 4 | 98 | 6 210 | 0.111 | 0.311 | **0.546 s** | 1.4 GB | 550 MB | 1.26 MB | 98/98 ACCEPT 2^-128.30 |
| fp8-ada+blake3 (seq. interp.) | 4d8668b | 2048 | 4 | 98 | 35 370 | 6.147 | 3.346 | **11.81 s** | 8.0 GB | 2.95 GB | 2.60 MB | 98/98 ACCEPT 2^-128.30 |
| fp8-ada+blake3 (seq. interp.) | 4d8668b | 4096 | 2 | 49 | 35 370 | 4.821 | 1.857 | **6.868 s** | 8.9 GB | 1.44 GB | 2.53 MB | 49/49 ACCEPT 2^-128.40 |
| **fp8-ada+blake3 (level interp.)** | 820aa6f | 2048 | **4** | 98 | 35 370 | 1.592 | 3.202 | **5.224 s** | 8.0 GB | 2.95 GB | 2.60 MB | 98/98 ACCEPT 2^-128.30 |
| **fp8-ada+blake3 (level interp.)** | 820aa6f | 4096 | 2 | 49 | 35 370 | 1.826 | 2.737 | **4.700 s** | 8.9 GB | 1.44 GB | 2.53 MB | 49/49 ACCEPT 2^-128.40 |
| fp8-ada+blake3 | any | 4096 | 3 / 4 | | | | | **OOM** | > 23 GB | | | |
| bf16-hopper bare | 4d8668b | 16384 | 4 | 25 | 3 292 | 0.074 | 0.130 | **0.261 s** | 5.5 GB | 118 MB | 27.0 MB | 25/25 ACCEPT 2^-128.05 |
| bf16-hopper +hash (Poseidon2) | 4d8668b | 16384 | 4 | 25 | 5 637 | 0.161 | 0.480 | **0.805 s** | 9.7 GB | 164 MB | 1.17 MB | 25/25 ACCEPT 2^-128.05 |
| bf16-hopper bare | 4d8668b | 2048 | 4 | 196 | 3 292 | 0.098 | 0.269 | **0.485 s** | 1.1 GB | 625 MB | 26.5 MB | 196/196 ACCEPT 2^-128.58 |
| bf16-hopper +hash | 4d8668b | 2048 | 4 | 196 | 5 637 | 0.198 | 0.543 | **0.922 s** | 1.4 GB | 1.02 GB | 1.42 MB | 196/196 ACCEPT 2^-128.58 |
| bf16-hopper+blake3 (seq. interp.) | 4d8668b | 2048 | 4 | 196 | 34 843 | 12.590 | 10.988 | **25.30 s** | 8.4 GB | 5.87 GB | 2.76 MB | 196/196 ACCEPT 2^-128.58 |
| **bf16-hopper+blake3 (level interp.)** | 820aa6f | 2048 | **4** | 196 | 34 843 | 3.062 | 6.483 | **10.70 s** | 8.4 GB | 5.87 GB | 2.76 MB | 196/196 ACCEPT 2^-128.58 |
| bf16-hopper+blake3 | any | 4096 | 2 / 3 / 4 | | | | | **OOM** (seq. l=4096: 21.15 s, predecessor) | | | | |

Witness kernel alone (`lane3/wit.py`, `lane3/wit2.py`; random rows, W identical level vs sequential on both `+blake3` systems at both l):

| system | m | l | sequential interpreter | **level interpreter** (179 / 180 levels) | encode + Merkle | Poseidon2 fused kernel (same l) |
|---|---|---|---|---|---|---|
| fp8-ada+blake3 | 35 370 | 2048 | 125.9 ms | **17.4 ms** (7.2x) | 1.8 + 3.4 ms | 1.15 ms |
| fp8-ada+blake3 | 35 370 | 4096 | 128.5 ms | **24.1 ms** (5.3x) | | |
| bf16-hopper+blake3 | 34 843 | 2048 | 124.8 ms | **17.4 ms** | 1.8 + 3.3 ms | 0.63 ms |
| bf16-hopper+blake3 | 34 843 | 4096 | 127.4 ms | **24.1 ms** | | |

**Digest bytes.** Poseidon2 publishes 8 BabyBear elements per row digest (32 B); the BLAKE3 leaf publishes 49 (`[n_chunks + 4 role |
CV_0 | CV_1 | CV_2]` as 16-bit limbs, 196 B), two per VU (x row, W column): the statement grows by 4096 x 2 x 41 x 4 B = 1.34 MB
per pass (measured 2.53 MB vs 1.18 MB at fp8-ada). The leaf under the SHA-256 row trees is 32 B in both cases (for BLAKE3 the
keyed BLAKE3 root, recomputed by the verifier from the CVs with 1-2 native parent compressions).

**Rows/unit.** fp8-ada: bare 3 769, +hash 6 210 (1.65x), +blake3 35 370 (**9.4x bare, 5.7x Poseidon2**; 30 798 hash rows = the
half-block pairing's 2 compressions per role per column, one discarded). bf16-hopper: 3 292 / 5 637 / 34 843 (**10.6x, 6.2x**).

**Table 1 assumption line (one sentence).** `+blake3`: the operand rows are bound to the committed roots under the collision
resistance of the BLAKE3 compression function (keyed mode, a key per operand role, all 7 rounds in-circuit on the chunk chaining
values, the parent fold recomputed natively by the verifier) and of SHA-256 (the row Merkle trees); no algebraic-hash
(Poseidon2) assumption; deterministic and unsalted, so a published row digest hides the row only up to preimage search.

## Art ids (all `remote = 1`, checked with `research data sql` on the pod store at 22:54Z)
* **results tree (cite this one): art:2bb48681d21cfff3c3aeed2ae16eddbdf0fb1f1b93624345a9c171434bb896d8** (`run-files/v1`): every
  run's `result.json`, `log.txt`, dump `manifest.json` (per-proof sha256), `rust_batch.json/.err`, and `lane3/` scripts + outputs
  (bench/post/lvl/custody logs, `wit.py`/`wit2.py` + outputs, `tests_lv.out`, `table.md`, `ids.out`, source stamps of src3/src3b).
  Earlier snapshots of the same tree: art:a31226b8… (22:50Z), art:705fa712… (22:52Z).
* dumps (`ligero-proof-dump/v1`, rep1 + system.bin + manifest + rust_batch.json):
  * level interpreter (820aa6f): `lv_fp8b3_l4096_p2` art:7e846422…, `lv_fp8b3_l2048_p4` art:605badd9…, `lv_bf16b3_l2048_p4` art:e858883a…
  * sequential interpreter (4d8668b): `fp8b3_l4096_p2` art:84c2766e…
  * controls l=16384 p4: `fp8_bare_p4` art:fdb7a2a6…, `fp8_hash_p4` art:e0cdac71…, `bf16_bare_p4` art:aeb391d9…, `bf16_hash_p4` art:cd83d78b…
  * controls l=2048 p4: `fp8_bare_l2048_p4` art:ea223d3b…, `fp8_hash_l2048_p4` art:fe433280…, `bf16_bare_l2048_p4` art:d7d68b4d…,
    `bf16_hash_l2048_p4` art:e5cfb112…
  * predecessor's pod-only results cited in §0b (bench2/*/result.json + logs + manifests, lane2 scripts/outputs; no proofs):
    art:83f8f6d56f3d05548671ee51d110b766eda3cd630f9c7dfa206c08799d6b0025 (`run-files/v1`, remote = 1)
  * gates on 820aa6f: art:61a9dd2caa2ae648380f73389324054a8e85d67e336359bdd76d2ddc286929d8 (`gate-log/v1`)
  * NOT retained: `fp8b3_l2048_p4`, `bf16b3_l2048_p4` (sequential interpreter, superseded; proof files deleted on the pod for disk
    after the Rust batch accepted them; verdicts + manifests in the results tree).

## Discrepancies
(none yet)

## FINAL (22:56Z)

**Branch `lane/blake3-leaf-3` @ 820aa6f** (= 1db0008 + 4d8668b cherry-pick of ajtai-leaf-2 1cf9178 `prove_vus_many` + 820aa6f
level-scheduled witness interpreter), `git status` clean, not merged, no repo `.md`.

**t.total, 4096 VUs, local coins, RTX 4090 ghpl8iy5s629sq, same pod, Rust batch accepting every sub-batch (pinned):**

| relation | bare p4 (l=16384) | +hash Poseidon2 p4 (l=16384) | **+blake3 p4** (l=2048, the largest l that fits p4) | +blake3 best config | rows/unit (bare / +hash / +blake3) |
|---|---|---|---|---|---|
| fp8-ada | 0.170 s | 0.421 s | **5.224 s** (was 11.81 s with the sequential interpreter) | **4.700 s** at l=4096 p2 (was 6.868) | 3 769 / 6 210 / 35 370 |
| bf16-hopper | 0.261 s | 0.805 s | **10.70 s** (was 25.30 s) | l=2048 p4 (l=4096 fits only p1) | 3 292 / 5 637 / 34 843 |

vs bare / vs Poseidon2 at the best config: fp8-ada+blake3 **27.6x / 11.2x**, bf16-hopper+blake3 **41x / 13.3x**. At the same l
(2048, p4) against the same-l controls: fp8-ada 18.0x bare (0.291 s) / 9.6x +hash (0.546 s); bf16-hopper 22x (0.485 s) / 11.6x (0.922 s).

* **Rust:** `ligero-verify batch` (sha256 4f0243da…, pinned, no `--allow-any-system`) ACCEPTED all 14 dumps of this lane,
  every sub-batch: `+blake3` 98/98 (2^-128.30), 49/49 (2^-128.40), 196/196 (2^-128.58) for both interpreters; controls
  13/13, 25/25, 98/98, 196/196. `system_pinned = true` everywhere (the v2 pins of 1db0008 hold; no re-pin needed: the level
  interpreter changes how W is computed, not the system).
* **Digest bytes:** BLAKE3 publishes 49 elements (196 B) per row digest vs Poseidon2's 8 (32 B): statement 2.53 MB vs 1.18 MB per
  4096-VU pass (fp8-ada, +1.34 MB = 4096 x 2 x 41 x 4 B); the leaf under the SHA-256 row tree is 32 B for both.
* **Table 1 assumption line:** `+blake3`: operand rows bound to the committed roots under the collision resistance of the BLAKE3
  compression function (keyed, a key per operand role, all 7 rounds in-circuit on the chunk CVs, parent fold recomputed natively
  by the verifier) and of SHA-256 (row Merkle trees); no algebraic-hash assumption; deterministic, unsalted (hides a row only up
  to preimage search).
* **Finding 1 (fixed, 820aa6f):** the sequential witness interpreter was ~95 % of `+blake3`'s commit graph: 126 ms per sub-batch
  (l threads, each through ~35 k ops; latency-bound) vs ~5 ms encode + Merkle. Level-scheduled interpreter: 17.4 ms (l=2048) /
  24.1 ms (l=4096), W identical on both `+blake3` systems, `witness_device_test.py` + `leaf/blake3_test.py` 22 passed on the pod,
  conformance `-k pipelined` 3 passed, `tests/test_repository.py` 5 passed (laptop). Only systems above `INTERP_OPS` (16 384 ops:
  the BLAKE3-leaf ones) use the interpreter, so bare / Poseidon2 / Ajtai are untouched; `LIGERO_INTERP_LEVELS=0` restores the old path.
* **Finding 2 (memory):** on 24 GB, `+blake3` fits l=4096 only at p <= 2 (fp8) / p1 (bf16); l=4096 p3/p4 and l>=8192 OOM (CUDA-graph
  pools 8.8-13.8 GiB). p4 therefore forces l=2048: 2x sub-batches and 2x openings (proof 2.95 GB / 5.87 GB per pass), which is why
  fp8 p4 (5.22 s) loses to p2 at l=4096 (4.70 s). An 80 GB part runs l=16384 p4 directly.
* **Next bottleneck:** the tests (`t.arithmetic`): 2.74 s of fp8's 4.70 s = 56 ms per l=4096 sub-batch at m = 35 370, ~2.2x more
  per cell than Poseidon2's (18 ms at m = 6 210, l = 16384) -- the BLAKE3 gadget's dense XOR affine forms (~216 k linear + 246 k
  quadratic terms per block). Then the level interpreter's remaining 24 ms (179 launches) and the proof size (openings scale with
  rows: 1.44 GB per pass).
* **`+shared` BLAKE3:** structurally unsupported on share-logup-3 53452a6 (`SharedHashedRunner` refuses non-Poseidon2 leaves:
  row sharing hashes via `hashchain.row_hash_system`). Census estimate (not measured): tile64 makes BLAKE3's hash rows +6.4 % of
  bare (fp8-ada) -- the leaf would be nearly free shared; needs a BLAKE3 `row_hash_system` + the Rust pair path for it.
* **Pod:** vy-blake3-leaf ghpl8iy5s629sq (4090, $0.74/h), this lane 22:18-22:59Z ≈ **$0.50** (of $3); **TERMINATED 22:58:52Z**
  after custody (gone from `pods list`); annotated in `~/.research/machines.toml` (pod lifetime ~5.9 h ≈ $4.4 over three lanes).
* **Remaining (for a successor / integration):** (1) cherry-pick 820aa6f into integration with 1cf9178 (ajtai-leaf-2 owns
  1cf9178; 4d8668b is the same change with my branch's ZK note); (2) the tests' cost on dense-affine systems (above); (3) the
  pipelined prover's graph-pool memory at tall m (p4 at l=4096 would halve fp8's openings); (4) `+shared` with a BLAKE3 row-hash
  system.
* **Gates on the FINAL tree 820aa6f** (22:56Z, level interpreter on, `gate-vu --vus 2048 --batch 4096 --auth included-hash`,
  STRICT): `fp8-ada+blake3` **25 honest + 86 negatives, 0 failures** (32 s; predecessor's 75 s), `bf16-hopper+blake3` **49 + 86,
  0 failures** (48 s; was 108 s). Logs art:61a9dd2caa2ae648380f73389324054a8e85d67e336359bdd76d2ddc286929d8 (`gate-log/v1`, remote = 1).
