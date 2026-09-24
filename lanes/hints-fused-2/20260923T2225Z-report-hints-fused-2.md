---
lane: hints-fused-2
kind: report
created: 2026-09-23T22:25Z
status: open
---

CHECKPOINT 4287a92b (23:02Z) [open] report §1-3 written (floor fp8-ada-v3x4 --batch 4096 --pipeline 4 = 0.1142 s vs fp8-ada-v3 p4 torch 0.1715 same pod; next bottleneck = latency-bound witness_program at l=4096); chain3 (bf16-hopper/fp8-hopper v3 + v3x4 fused vs torch, 2 rounds) finishing; FINAL + pod terminate by ~23:20Z
CHECKPOINT 4287a92b (22:52Z) [open] custody: run-files art:e255651c (pred chain) + art:bf352a36 (chain2) + 7 bench-result, all remote=1; Rust 13/13 v3x4 p4/p8 l=4096, 13/13 v3, 4/4 v2x4 (pinned); extended differential 82/82; floor profile: witness_program latency-bound (block-size micro refuted occupancy); writing FINAL
CHECKPOINT e57637f2 (22:44Z) [open] 5 A/B rounds done: fused fp8-ada-v3x4 p4 l=4096 0.1210 s / p8 l=4096 0.1103 s vs fp8-ada-v3 p4 torch 0.1715 s (same pod; fused v3 p4 0.1380); torch v3x4 p4 l=16384 OOMs, fused 0.1603; dumps+Rust, floor profile, extended differential running
CHECKPOINT e57637f (22:32Z) [open] chain2 running on e57637f (round 3/5 done, all rc=0; rounds 4-5, dumps+Rust at floors, profiles, extended differential next); predecessor chain pushed art:e255651c (PRESERVED)
CHECKPOINT ff52e47 (22:21Z) [open] worktree + branch lane/hints-fused-2 at ff52e47; recovered predecessor's pod chain (all ran 21:17-22:19Z): differential 72/72 pass, gates fused 0 failures (v3x4 zk+plain, v3 zk, v2x4 zk), Rust 4/4 ACCEPT pinned on 2 fused v3x4 dumps; A/B: fused v3x4 p4 l=16384 0.157-0.160 s, l=4096 p4 0.114 s vs torch v3 p4 0.170 s same pod; next: more rounds + profile + custody
# hints-fused-2 — fused device hint kernel for the v2 / v3 families: differential + same-pod bench (continues hints-fused)

## Setup

* Branch `lane/hints-fused-2` at predecessor tip `lane/hints-fused` ff52e47, worktree `~/projects/verity-main-wt/hints-fused-2`.
  Predecessor worktree clean (no uncommitted diff to carry). Predecessor report: `lanes/hints-fused/20260923T2100Z-report-hints-fused.md`.
* Pod: `vy-hints-fused-veritor-campaign` (RunPod em6u0t7azwt5gu, RTX 4090, reused warm). Budget $3.
* Env on every pod run: `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`.

## Log

* 22:19Z start. Predecessor branch has no commits after ff52e47 (21:14Z); its worktree is clean. The predecessor's pod chain
  (`chain.sh` → `ab.sh` → `post.sh`, copies in `evidence/pod-scripts/`) had been queued at ~21:17Z and ran to completion
  (21:17 → 22:19Z) after the predecessor stopped; nothing was recorded. Recovered below (§1).
* 22:21Z CHECKPOINT. 6caa2f5: real-sub-batch differential over all 16 v2/v3 relations (was 6). e57637f: `HINTS_FUSED_SEEDS`
  repeats the adversarial differential over more seeds at constant memory (a wider `HINTS_FUSED_N` would put the torch-graph
  comparison path's private pool past 24 GiB).
* 22:24Z `chain2.sh` on the pod (tree e57637f): 3 more interleaved rounds × 13 configs, dumps + Rust at the candidate floors,
  profiles, extended differential (`HINTS_FUSED_SEEDS=8`, all 16 real sub-batches).

## 1. Recovered: the predecessor's chain (tree ff52e47, pod em6u0t7azwt5gu, 21:00–22:19Z)

Trees on the pod: `/workspace/src-base` = pristine 5e6b3e3 (open-fixes FINAL, the "before"); `/workspace/src` = ff52e47. A/B on the
lane tree = `LIGERO_FUSED_HINTS=1` (fused) vs `=0` (torch CUDA-graph path, i.e. 5e6b3e3's hint code); both with
`LIGERO_REFERENCE_HINTS=0` except `ab0` (REF=1: the warm-up sub-batch's fused hints compared to the Python reference, passed).
All: 4096 VUs, `--zk --mode interactive`, local coins, 3 reps per run (t.total = median of the run's reps).

* **Differential** (`hints_fused_test.py`, `diff_full2.log`): **72 passed** — 16 relations (v2, v2x4, v3, v3x4 × 4 targets) ×
  {emission-order coverage chain + unit, adversarial (16384 columns: whole word range incl. NaN/inf/off-domain operand words,
  all 2^32 accumulator words + every FP32 class, all-zero / all-max operands, exact cancellations, exponent extremes) fused ==
  eager == graph in chain AND unit mode, in-domain units fused == eager == Python reference}, real sub-batches (6 relations)
  fused == eager == graph == reference, two-stream concurrency (fp8-ada-v3x4, fp8-ada-v2x4) 0 mismatches in 5 trials.
  The first run (`diff_full.log`, a6178cd) had 4 errors, none a mismatch: 3 CUDA OOM from graph pools accumulating across tests
  and 1 stale torch graph replayed through `id(sys)` reuse in the test process; ff52e47 clears the caches per test.
* **Microbench** (`micro1.log`, hint generation alone, one real sub-batch): fp8-ada-v3 l=16384 fused 0.40 ms vs graph 5.02 ms;
  fp8-ada-v3x4 l=16384 1.42 vs 20.38 ms; fp8-ada-v3x4 l=4096 0.52 vs 16.46 ms; fp8-ada-v2x4 l=16384 0.34 vs 3.75 ms (all equal).
* **Gates** (fused, `gate-vu --vus 2048 --batch 16384`, every honest sub-batch's hints compared with the Python reference):
  fp8-ada-v3x4 `--zk` 2 honest / 99 negatives / **0 failures**; plain 2 / 99 / **0**; fp8-ada-v3 `--zk` 7 / 92 / **0**;
  fp8-ada-v2x4 `--zk` 2 / 99 / **0**.
* **Rust** (`ligero-verify batch`, fused dumps): v3x4 p2 l=16384 and v3x4 p4 l=16384: **4/4 ACCEPT each, batch 2^-128.67,
  system pinned (fp8-ada-v3x4, sys_id 727b2076…), python agreement 4/4**. Pinned ⇒ no system digest changed.
* **pytest subset** (pipeline_race, pubsel/privsel relation, relations, chain, bench_vu, fold; fused default): 140 passed,
  1 failed = `fold_test::test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]` (the pre-existing 4.146 > 4.1 ratio,
  fails on main; open-fixes §Tests).
* **Torch path OOMs at fp8-ada-v3x4 `--pipeline 4` l=16384** (base tree and FUSED=0, 3/3 runs): 4 per-stream hint graphs
  hold 5.9 GiB of private pools. The fused path runs it at 16.2 GiB peak.

## 2. Same-pod A/B, 5 rounds (tree ff52e47 rounds ab1–ab2, e57637f rounds r3–r5; hint code identical in both)

4090 em6u0t7azwt5gu, 4096 VUs, `--zk --mode interactive`, local coins, 3 reps per run, `LIGERO_REFERENCE_HINTS=0`, configs
interleaved per round. `fu` = `LIGERO_FUSED_HINTS=1` (fused kernel), `to` = `=0` (torch CUDA-graph path = 5e6b3e3's hint code),
`base` = the pristine 5e6b3e3 tree. **t.total = median over runs of each run's t.total** (itself the median of its 3 reps);
`reps med` = median over every rep of every run, `r2+` = the same without each run's first timed rep. Phase columns are the
pipelined pass's wall shares (they sum to t.total), medians over runs. Every run: `validation: passed` (all sub-batches
self-checked and verified in-process). `ab2.py` in `evidence/pod-scripts/`.

| config (4096 VUs) | runs | t.total | min–max | reps med | r2+ med | hints share | enc+commit | arithmetic | sub-batches | peak |
|---|---|---|---|---|---|---|---|---|---|---|
| `base` fp8-ada-v3 p4 l=16384 (5e6b3e3) | 4 | 0.1678 | 0.1626–0.1753 | 0.1678 | 0.1608 | 0.0461 | 0.0244 | 0.0824 | 13 | 5.19 GiB |
| `to` fp8-ada-v3 p4 l=16384 | 5 | **0.1715** | 0.1697–0.1724 | 0.1715 | 0.1652 | 0.0492 | 0.0240 | 0.0828 | 13 | 5.19 GiB |
| `fu` fp8-ada-v3 p4 l=16384 | 6 | 0.1405 | 0.1366–0.1538 | 0.1395 | 0.1366 | 0.0045 | 0.0349 | 0.0886 | 13 | 4.24 GiB |
| `to` fp8-ada-v3x4 p2 l=16384 | 5 | 0.2103 | 0.2034–0.2252 | 0.2069 | 0.1987 | 0.0877 | 0.0558 | 0.0623 | 4 | 10.91 GiB |
| `fu` fp8-ada-v3x4 p2 l=16384 | 6 | 0.1690 | 0.1599–0.1830 | 0.1672 | 0.1592 | 0.0081 | 0.0668 | 0.0846 | 4 | 9.37 GiB |
| `to` fp8-ada-v3x4 p4 l=16384 (base + 2 `to`) | 3 | **OOM** | — | — | — | — | — | — | 4 | > 23.5 GiB |
| `fu` fp8-ada-v3x4 p4 l=16384 | 5 (+1 dump run 0.1600) | 0.1603 | 0.1479–0.1777 | 0.1603 | 0.1478 | 0.0072 | 0.0867 | 0.0562 | 4 | 16.22 GiB |
| `fu` fp8-ada-v3x4 p2 l=8192 | 3 | 0.1513 | 0.1276–0.1715 | 0.1512 | 0.1264 | 0.0088 | 0.0530 | 0.0710 | 7 | 4.69 GiB |
| `fu` fp8-ada-v3x4 p4 l=8192 | 3 | 0.1323 | 0.1207–0.4866 | 0.1306 | 0.1162 | 0.0067 | 0.0535 | 0.0639 | 7 | 8.16 GiB |
| `to` fp8-ada-v3x4 p4 l=4096 | 4 | 0.2251 | 0.2164–0.7906 | 0.2213 | 0.2095 | 0.1343 | 0.0274 | 0.0527 | 13 | 5.06 GiB |
| `fu` fp8-ada-v3x4 p4 l=4096 | 5 | **0.1142** | 0.1132–0.6044 | 0.1142 | 0.1112 | 0.0063 | 0.0385 | 0.0609 | 13 | 4.12 GiB |
| `fu` fp8-ada-v3x4 p8 l=4096 | 4 | **0.1119** | 0.1074–0.7521 | 0.1275 | 0.1085 | 0.0047 | 0.0328 | 0.0725 | 13 | 7.96 GiB |
| `to` fp8-ada-v2x4 p4 l=16384 | 4 | 0.1050 | 0.1010–0.1192 | 0.1088 | 0.1016 | 0.0124 | 0.0090 | 0.0809 | 4 | 3.28 GiB |
| `fu` fp8-ada-v2x4 p4 l=16384 | 5 | 0.1118 | 0.0701–0.1163 | 0.1035 | 0.1026 | 0.0016 | 0.0130 | 0.0953 | 4 | 2.79 GiB |

`fu` rows include the dump runs `d_*` (1 per config for v3 p4 l=16384, v3x4 p4/p8 l=4096, v2x4). They are the same bench with
`--dump-reps 1`, and the dumps are written after the timed pass. Full table: `evidence/pod2/ab2_table.txt`.

Outliers: runs with a 0.49–0.79 s t.total have 2 of 3 reps slow, almost always the first timed rep. Its pass wall carries
0.5–1.5 s of extra host work outside the prover, and it hits both paths (`to` v3x4 p4 l=4096 r3 = 0.79 s). It looks like a
harness warm-up artifact, not something the hint path causes. The median over runs absorbs it; `r2+` gives the same ranking.

Readings:
* **Goal met:** folded private-safe fp8-ada-v3x4 now beats unfolded fp8-ada-v3 `--pipeline 4` on the same pod. Against the
  current path (`to` v3 p4, 0.1715 s; pristine 5e6b3e3 0.1678 s): v3x4 **p4 l=4096 0.1142 s (−33 %)**, p8 l=4096 0.1119 s
  (−35 %), p4 l=8192 0.1323 s (−23 %), p2 l=8192 0.1513 s (−12 %), p4 l=16384 0.1603 s (−6.5 %), p2 l=16384 0.1690 s (−1.5 %,
  a tie). This 4090 host runs about 10 % slower than open-fixes' (v3 p4 0.1715 here vs 0.1547 there), so compare within the
  table. Scaled to that pod the floor would be about 0.10 s; that's an estimate, not a measurement.
* **New floor: `fp8-ada-v3x4 --batch 4096 --pipeline 4` = 0.114 s** at 4.12 GiB peak, 13/13 Rust ACCEPT pinned. p8 is the
  same within noise (0.112 s) at twice the memory. l=16384 is not the floor for the folded unit: its 4 sub-batches of
  7090 × 16384 cost more per VU than 13 of 7090 × 4096.
* The fused kernel also speeds up unfolded v3 (0.1715 → 0.1405 s, −18 %). Against that, the best fold is still ahead
  (−19 % at p4 l=4096).
* The fused kernel is what makes v3x4 p4 l=16384 run at all: the torch path's per-stream graphs OOM the 24 GiB card.
* The hints share of the wall drops from 0.05–0.13 s to 0.005–0.009 s everywhere. v3x4 at l=4096 goes 0.1343 → 0.0063.
* v2x4 p4 l=16384: no measurable t.total change (fused 0.1118 vs torch 0.1050, r2+ 0.1026 vs 0.1016). Its hints were already
  small (0.012 s).
* Why l=4096 wins: v3x4 at l=4096 has the same 13 sub-batches × 341 VUs as v3 at l=16384, and the same cells per sub-batch
  (7090 × 4096 vs 1806 × 16384). The gain comes from rows being cheaper than columns (shorter RS encode, 4× fewer Merkle leaves:
  enc+commit share 0.0385 vs 0.0349 for 4× the rows), not from fewer sub-batches. At l=16384 the 4096th VU forces a 4th
  sub-batch holding 1 VU: with 4095 VUs it's 3 sub-batches, 0.1091 s at p2 and 0.1342 s at p4 (predecessor, 1 run each).

## 2b. The H100 headline families on the same 4090 (chain3, 2 rounds, 22:53–23:05Z; indicative for v3-scout-2)

Same protocol as §2 (4096 VUs, int-ZK interactive, local coins, 3 reps per run, `validation: passed` on every run; no dumps).
v3-scout's H100 numbers were measured with the torch hint path; merging this lane changes them.

| relation (4096 VUs, p4) | `to` torch hints | `fu` fused | sub-batches | peak (fu) |
|---|---|---|---|---|
| bf16-hopper-v3 l=16384 | 0.2786 (0.2777, 0.2794) | **0.2248** (0.2220, 0.2276), −19 % | 25 | 3.64 GiB |
| bf16-hopper-v3x4 l=4096 | 0.3653 | **0.2014** (0.1859, 0.2168; reps med 0.1897): −28 % vs `to` bf16-hopper-v3 p4 | 25 | 3.49 GiB |
| fp8-hopper-v3 l=16384 | 0.1607 (0.1566, 0.1647) | 0.1511 (0.1265, 0.1757; noisy, r2+ 0.1352) | 13 | 4.02 GiB |
| fp8-hopper-v3x4 l=4096 | 0.2009 | **0.1043** (0.1006, 0.1080): −35 % vs `to` fp8-hopper-v3 p4 | 13 | 3.89 GiB |

The ranking matches fp8-ada: with fused hints, the x4 fold at l=4096 p4 is the fastest private-safe configuration for all
three targets measured. Before, it was the slowest.

## 3. The next bottleneck (profiles of the second timed rep, `prof_rep.py`; `evidence/pod2/prof2/`, `evidence/pod1/prof/`)

| profile (fused) | profiled wall | device-busy union (incl. copies) | top kernels by device time (sum over the 4 streams; they overlap) |
|---|---|---|---|
| v3x4 p4 **l=4096** (floor), 13 sub-batches | 118.7 ms | 95.7 ms (101.4) | **witness_program 43.1 ms (29.5 %, 3.3 ms/launch)**, blake3_chunks 19.7 (13.5 %), quad_u32_D6 17.2 (11.8 %), rs_encode 14.7 (10.1 %), hints_fused 10.3 (7.0 %), boolcomb 6.3, lincomb 4.9, torch glue (copies, remainder, cat, index_select) ≈ 15 |
| v3x4 p4 l=16384, 4 sub-batches | 144.6 ms | 110.4 ms (114.6) | rs_encode 33.1 (20.1 %), witness_program 28.1 (17.1 %), hints_fused 24.2 (14.7 %, 6 ms/launch vs 1.4 ms alone), blake3 22.0 (13.4 %), quad 19.8 (12.0 %) |
| v3 p4 l=16384, 13 sub-batches | 132.7 ms | 101.1 ms (107.6) | rs_encode 25.9 (20.3 %), blake3 19.7 (15.4 %), quad 17.0 (13.3 %), witness_program 12.2 (9.5 %), triton cat 7.9, hints_fused 6.5 (5.1 %) |

* **At the floor the witness program dominates**: 13 launches, 3.3 ms each under 4-stream overlap and 2.4 ms alone
  (`wblock.log`). That's 3.5× the per-cell cost of v3's witness program at l=16384 (0.84 ms for the same cell count). It isn't
  occupancy: launching with 32–128-thread blocks instead of 256 (same per-thread work, W identical) gains only 9 %
  (2.44 → 2.21 ms). 4× the columns (l=16384) costs only +60 % (3.9 ms). So at l=4096 the kernel is latency-bound by each
  thread's serial 7090-row straight-line program. (Tried as a `LIGERO_WITNESS_BLOCK` knob, 82af8b4, reverted in 4287a92.)
  **Next step:** make the witness program row-parallel. Most derived rows (bits, selectors, products, inverses) read only
  hint/pub rows, so a levelled op DAG on a 2D grid (column × op chunk) exposes the parallelism. Or fuse hint generation into
  it, which also removes the int64 hint matrix round trip: 5949 × l × 8 B written, copied into the commit graph's static
  `st.hints` buffer (`protocol._prove_stages`), then read again, per sub-batch.
* After that: Merkle leaf hashing (blake3_chunks, 13–15 %), the quadratic test (12–13 %), and RS encode (10–20 %, the
  largest at l=16384). Device idle is 17–30 % of the pipelined wall, and the host sits in cudaEventSynchronize.
* The fused hint kernel is now 5–7 % of device time at the floor (0.5 ms alone per l=4096 launch, also one thread per column).
  A cheap follow-up is writing it straight into the per-stream `st.hints` buffer, which saves one D2D copy of the hint
  matrix per sub-batch (≈ 1.4 ms at l=16384, ≈ 0.35 ms at l=4096).

## Artifacts

* `run-files/v1` predecessor chain recovered (tree ff52e47: results/, logs/, 2 fused v3x4 dumps + Rust logs, profiles, scripts)
  **art:e255651cbe6ef8cde9e719e333f833a9d12d277c3645012565633c683c0af7be** (PRESERVED, 22:33Z).
* `run-files/v1` chain2 (tree e57637f: results2/ 45 bench JSONs, logs, 4 fused dumps + Rust logs, floor profiles, extended
  differential log, witness block-size micro, `ab2_table.txt`, scripts)
  **art:bf352a36987413cbeea648ea11ff96b34eddc39e30c5da3cd7d8a09b2a1dab80** (PRESERVED, 22:52Z).
* `bench-result/v1` (PRESERVED, remote = 1):
  * fused fp8-ada-v3x4 p4 l=4096 (the floor, Rust 13/13 pinned) **art:92e979a56fa022ef22e3bd436433f07a632fbe0779e7c3c3d6b88001e4a79c6e**
  * fused fp8-ada-v3x4 p8 l=4096 (Rust 13/13 pinned) art:a4c3c652e8399fc6054a2fa7bc347b680280082bd90de0034c4295a277d7b647
  * fused fp8-ada-v3 p4 l=16384 (Rust 13/13 pinned) art:59fb1ed5a1de9b3b60995b229cdebad873fa0fc12b527d155ade40ccb5fa9265
  * fused fp8-ada-v2x4 p4 l=16384 (Rust 4/4 pinned) art:db32dd623bdcd56dc648a93a69e4ff2373a0bb7059a3556f9fb5416e55741388
  * fused fp8-ada-v3x4 p4 l=16384 (r5) art:60da7ceff510e45b390e797e3e4a2b9118d0bd6eb8426fe25079dc352915dc43
  * torch-path fp8-ada-v3 p4 l=16384 (r5, the "before") art:92075bfcd21f4833c758cb5a6caa3b7c1737cca9e533e5883df42d461718dd31
  * pristine 5e6b3e3 fp8-ada-v3 p4 l=16384 (r5) art:de8cfd9e3958eb999625b6d939c7958bf8077ea3e742928836ee910f61a834bb
* `run-files/v1` chain3 (bf16-hopper / fp8-hopper v3 + v3x4, fused vs torch, 16 bench JSONs + logs)
  **art:74e9ed38ce8349bed6e5da6b38c0c4a770e30e34b1b4c3a6ac37b6efd956d355** (PRESERVED, 23:05Z).
* All ten artifacts: `research data sql` → remote = 1, checked before the pod was terminated.

## FINAL (23:10Z)

**Branch `lane/hints-fused-2` @ 4287a92** (not merged). Commits on top of the predecessor's ff52e47: 6caa2f5 (real-sub-batch
differential over all 16 v2/v3 relations), e57637f (`HINTS_FUSED_SEEDS` adversarial seeds), 82af8b4 + 4287a92 (witness
block-size knob tried, then reverted: tree = e57637f). Diff vs base 5e6b3e3 (open-fixes FINAL): `hints_fused.py` (new, fused
NVRTC kernel), `hints_fused_test.py` (new), `privsel/hints.py` + `pubsel/hints.py` (+6 lines each: fused path first on CUDA,
torch graph path behind `LIGERO_FUSED_HINTS=0`), `relchain.py` (+2: `LIGERO_REFERENCE_HINTS=0` skips the bench warm-up's
Python-reference comparison; the gate and default keep it). **No system, statement or transcript change. No Rust pin
change: every Rust verification reports `system pinned`.**

1. **Goal met: fp8-ada-v3x4 beats fp8-ada-v3 `--pipeline 4` on the same pod.** 4090 em6u0t7azwt5gu, 4096 VUs, int-ZK
   interactive, local coins, median over 3–6 interleaved runs (§2):

   | config | before (torch hint graphs) | after (fused kernel) |
   |---|---|---|
   | fp8-ada-v3 p4 l=16384 (the brief's 0.155 s reference, 0.1547 on open-fixes' pod) | 0.1715 s (pristine 5e6b3e3: 0.1678) | 0.1405 s |
   | fp8-ada-v3x4 p2 l=16384 | 0.2103 s | 0.1690 s |
   | fp8-ada-v3x4 p4 l=16384 | OOM (24 GiB) | 0.1603 s |
   | fp8-ada-v3x4 p4 l=8192 | — | 0.1323 s |
   | **fp8-ada-v3x4 p4 l=4096** | 0.2251 s | **0.1142 s** (−33 % vs v3 p4 before, −19 % vs v3 p4 fused) |
   | fp8-ada-v3x4 p8 l=4096 | — | 0.1119 s (2× memory) |
   | fp8-ada-v2x4 p4 l=16384 | 0.1050 s | 0.1118 s (no measurable change) |
   | bf16-hopper-v3x4 p4 l=4096 / bf16-hopper-v3 p4 | 0.3653 / 0.2786 s | **0.2014** / 0.2248 s |
   | fp8-hopper-v3x4 p4 l=4096 / fp8-hopper-v3 p4 | 0.2009 / 0.1607 s | **0.1043** / 0.1511 s |

   **New floor: `fp8-ada-v3x4 --batch 4096 --pipeline 4` = 0.114 s**, 4.12 GiB peak, 13 sub-batches, Rust 13/13 ACCEPT
   (pinned, batch 2^-128.33). This host is about 10 % slower than open-fixes' 4090. The hint share of the wall falls from
   0.05–0.13 s to 0.005–0.009 s.
2. **Byte identity** (`hints_fused_test.py`, pod, `torch.equal`): **82 passed** on e57637f (72 on ff52e47 before the
   extension). Coverage for all 16 v2/v3 relations, both chain and unit mode, comparing fused against the torch eager path and
   the torch graph path:
   * 8 seeds × 16384 adversarial columns: the whole operand word range including NaN/inf/off-domain words, every
     accumulator word class, zero and max operands, exact cancellations, exponent extremes;
   * in-domain units, also checked against the Python reference;
   * real sub-batches marshalled by the chain runner, also checked against the Python reference;
   * two-stream concurrency: 0 mismatches.
3. **Per-stream safety:** no static buffers, the output is allocated on the caller's stream, one launch per sub-batch. Every
   bench at p2 / p4 / p8 self-checks and verifies all sub-batches (84 bench runs, 0 failures). The two-stream test passes.
4. **Gates** (fused; every honest sub-batch's hints compared to the Python reference): fp8-ada-v3x4 `--zk` 2 honest /
   99 negatives / **0 failures**, plain 2 / 99 / **0**; fp8-ada-v3 `--zk` 7 / 92 / **0**; fp8-ada-v2x4 `--zk` 2 / 99 / **0**.
   pytest subset: 140 passed, 1 failed (the pre-existing `bf16-ampere-x4` fold-fixture ratio, also fails on main).
5. **Rust `ligero-verify batch`** on 6 fused dumps, all ACCEPT, system pinned, python agreement:
   * fp8-ada-v3x4: p4 l=4096 13/13, p8 l=4096 13/13, p2 l=16384 4/4, p4 l=16384 4/4;
   * fp8-ada-v3 p4 l=16384: 13/13;
   * fp8-ada-v2x4 p4 l=16384: 4/4.
6. **Next bottleneck (§3):** at the floor, `witness_program` takes 30 % of device time: 3.3 ms per launch, 2.4 ms alone,
   3.5× v3's per-cell cost. It's latency-bound by each thread's serial 7090-row program: smaller blocks gain only 9 %, and 4×
   the columns cost only +60 %. Next steps:
   * make the witness program row-parallel, or fuse hint generation into it (this also drops the int64 hint matrix write,
     its copy into `st.hints`, and the reread);
   * then BLAKE3 leaf hashing (13 %), the quadratic test (12 %), and RS encode (10 %; 20 % at l=16384).
   Device idle is 17–30 % of the wall.
7. **Pod cost:** em6u0t7azwt5gu $0.74/h, created 20:54:42Z, terminated 23:05:38Z = 2.18 h = **$1.61** for the pod's
   lifetime. My share from 22:19Z is ≈ $0.58; the predecessor's ≈ $1.04. Under the $3 budget.
8. **Art ids** (all remote = 1): run-files art:e255651c… (predecessor chain), art:bf352a36… (chain2), art:74e9ed38…
   (chain3); bench-results art:92e979a5… (floor), art:a4c3c652…, art:59fb1ed5…, art:db32dd62…, art:60da7cef…,
   art:92075bfc… (before), art:de8cfd9e… (pristine). Full ids above.

Left for others:
* merge (coordinator);
* re-measure v3-scout's H100 v3 / v3x4 configs with the fused kernel (the 4090 ranking says x4 at l=4096 p4 wins for all
  three targets);
* the row-parallel or hint-fused witness program;
* the first-timed-rep slowness in `bench-vu` (0.5–1.5 s of host work, both paths);
* `st.hints` direct write (small).

