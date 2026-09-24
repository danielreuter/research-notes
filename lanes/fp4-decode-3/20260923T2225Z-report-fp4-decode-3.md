---
lane: fp4-decode-3
kind: report
created: 2026-09-23T22:25Z
status: final
---

CHECKPOINT 6ffa0351 (23:16Z) [final] FINAL written. Tip 6ffa035. 5090 p4: bare 0.0576 s, hashed 0.2038 s (3.54x); 4090 p4: 0.0532 / 0.2617 (4.92x). Rust pinned 7/7 on all 18 dumps; gates 0 failures both relations on both devices; 5090 cold compile 449.6 s -> 46.2 s (6ffa035, no runtime cost); 5090 pytest 249 passed / 1 known fold_test failure. 68 arts remote=1. Both pods terminated (4090 22:39Z, 5090 23:16Z); lane ~$1.2.
CHECKPOINT 6ffa0351 (23:08Z) [open] FINAL drafted in the report. 67 arts remote=1 (incl. 8 A/B dumps+verdicts). 5090 full ligero pytest at 6ffa035 at 146/251 (only the known fold_test bf16-ampere-x4 threshold failure so far); then terminate the 5090 and mark final.
CHECKPOINT 6ffa0351 (22:55Z) [open] 6ffa035 verified on the 5090: witness_device_test 6/6 (native==PTX incl. hashed), cold-cache pipe_test 46.2 s (was 449.6 s), gates 0 failures both, p4 pair Rust pinned; A/B native vs PTX = noise (hashed 0.2145/0.2340 vs 0.2247/0.2068). Full ligero pytest on the 5090 at 6ffa035 running (r20260923-225436-1399). Pushing A/B arts.
CHECKPOINT 6ffa0351 (22:46Z) [open] 6ffa035: fused witness as compute_89 PTX + driver JIT on cc>=12.0 (NVRTC compute_120 front end ~7 min on the hashed kernel on the 5090; compute_89+JIT 19 s), differential test native==PTX. 5090 suite at 6ffa035 r20260923-224554-d69a running (wd_test, cold-cache pipe_test, gates, p4 pair + pinned Rust). d86e014 5090 pair pushed (p4: bare 0.0576 s, hashed 0.2038 s, 3.54x; 31 arts remote=1). 4090 terminated 22:39Z.
CHECKPOINT d86e014 (22:39Z) [open] 5090 suite r20260923-222226-d052 DONE fail=0 at d86e014: pipe_test 2/2, gates 0 failures (hashed 4 honest + 92/92 neg; bare 2048/2048 + 116/116 + 3015/3015), best depth p4: bare t.total 0.0576 s, hashed 0.2038 s (3.54x), Rust pinned 7/7 both at p2/p4/p8. 4090 TERMINATED 22:39Z (custody clean, 10 arts remote=1). Pushing 5090 arts; probing the sm_120 cold compile (cicc 7.5 min for the hashed fused witness kernel).
CHECKPOINT d86e014 (22:22Z) [open] branch lane/fp4-decode-3 @ d86e014 (worktree ~/projects/verity-main-wt/fp4-decode-3). 5090 lx80c24sagdao0 bootstrapped (BOOTSTRAP_OK r20260923-210932-e854); suite r20260923-222226-d052 running there (pipe_test, gates, hashed+bare benches at --pipeline 4,8,2 + pinned Rust). 4090 d86e014 suite r20260923-211439-913b recovered to laptop (p4: bare t.total 0.0532 s, hashed 0.2617 s, Rust pinned 7/7 both, gates 0 failures); pushing it, then terminating the 4090.
# fp4-decode-3 — the 5090 `fp4-nvf4` / `fp4-nvf4+poseidon2` pair (continues fp4-decode-2)

Brief: `~/.research/notes/lanes/coordinator/20260923T2100Z-brief-relaunch.md` §1.4 + §3 (FINAL 23:45Z hard, $3).
Predecessors: `lane/fp4-decode-2` @ d86e014 (report `lanes/fp4-decode-2/20260923T2100Z-report-fp4-decode-2.md`, stopped ~21:15Z),
`lane/fp4-decode` @ 98c95b1 (report `lanes/fp4-decode/20260923T1700Z-report-fp4-decode.md`).
Branch `lane/fp4-decode-3` @ d86e014 in `~/projects/verity-main-wt/fp4-decode-3` (predecessor worktree had no uncommitted diff).
Pods: 5090 `vy-fp4-decode-2-5090b-veritor-campaign` lx80c24sagdao0; 4090 `vy-fp4-decode-3-veritor-campaign` k39j0s2bvhlljf (terminate
once custody is clean).

## 1. 4090 pair at d86e014 (predecessor's suite r20260923-211439-913b, recovered 22:21Z, pushed)

fp4-decode-2 launched its d86e014 suite on the 4090 at 21:14Z and stopped before reading it. It completed at 21:27Z:

| stage | outcome |
|---|---|
| pipe_test (`fp4/hashed_pipeline_test.py`) | 2/2 passed (pipelined == sequential bytes; ZK accepted) |
| gate `fp4-nvf4+poseidon2` 2048 VUs | 4 honest sub-batches, 92/92 negatives rejected, **0 failures** |
| gate `fp4-nvf4` 2048 VUs | 2048/2048 ok, 116/116 + 3015/3015 negatives rejected, **0 failures** |
| bench `fp4-nvf4+poseidon2` `--pipeline 4` (4096 VUs, l=16384, zk interactive, local coins) | **t.total 0.2617 s** (hints 0.049 s inside), peak dev 10.0 GB; Rust **pinned** (`fp4-nvf4+hash`, sys_id 8c6d260c) 7/7 ACCEPT, union 2^-128.54 |
| bench `fp4-nvf4` `--pipeline 4` | **t.total 0.0532 s**, peak dev 3.1 GB; Rust pinned (`fp4-nvf4`, sys_id a825ba0b) 7/7 ACCEPT |
| pytest backends/direct/ligero | 248 passed, 2 skipped, **1 failed**: `fold_test::test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]` (not fp4: see Discrepancies) |

4090 hashed/bare = **4.92×** at `--pipeline 4` (unpipelined, fp4-decode: 0.3327 / 0.0860 = 3.87×). `cargo test --release` 48/48 at
98c95b1 (r20260923-210126-ffb5); `backends/ligero-verify` is byte-unchanged 98c95b1..d86e014, so it holds for this tip.

Art ids (all remote=1, `evidence/store_ids.txt`): hashed p4 proofs art:7de9f86b, result art:b3232930, pinned verdict art:acfd35fa;
bare p4 proofs art:2f06276d, result art:e86293a2, pinned verdict art:99060fb5; gate hashed art:ecacc98b, gate bare art:2bf0289a;
suite stdout art:13fd0682; cargo test log art:fc849366.

## 2. 5090 suite r20260923-222226-d052 (d86e014, lx80c24sagdao0, RTX 5090 32 GB, driver 570.195.03) — DONE fail=0

`evidence/suite.sh` (predecessor's, extended to depths 4, 8, 2). LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1; 4096 VUs, l=16384,
`--zk --mode interactive`, local coins, 3 reps + warm-up, dump rep 1 (7 sub-batches: 6 x 682 + 4 VUs), then the **pinned**
`ligero-verify batch` (release build sha256 21b3bc77, no `--allow-any-system`) over the dump.

* pipe_test 2/2 passed (449.6 s: the cold compile below). Gate `fp4-nvf4+poseidon2` 2048 VUs: 4 honest sub-batches, 92/92 negatives
  rejected, **0 failures**. Gate `fp4-nvf4`: 2048/2048, 116/116 + 3015/3015 negatives rejected, **0 failures**.

| relation | depth | t.total (s) | hints (s) | tests (s) | peak dev (GB) | Rust pinned batch |
|---|---|---|---|---|---|---|
| fp4-nvf4 | 2 | 0.0710 | 0.0076 | 0.0472 | 1.69 | 7/7 ACCEPT (fp4-nvf4, a825ba0b) |
| **fp4-nvf4** | **4** | **0.0576** | 0.0056 | 0.0438 | 3.05 | 7/7 ACCEPT |
| fp4-nvf4 | 8 | 0.0616 | 0.0062 | 0.0457 | 5.10 | 7/7 ACCEPT |
| fp4-nvf4+poseidon2 | 2 | 0.2229 | 0.0495 | 0.1226 | 10.04 | 7/7 ACCEPT (fp4-nvf4+hash, 8c6d260c) |
| **fp4-nvf4+poseidon2** | **4** | **0.2038** | 0.0397 | 0.1314 | 10.04 | 7/7 ACCEPT, union 2^-128.54 |
| fp4-nvf4+poseidon2 | 8 | 0.2113 | 0.0199 | 0.1729 | 13.59 | 7/7 ACCEPT |

**5090 pair (best depth 4): bare 0.0576 s, hashed 0.2038 s = 3.54x** (Table 2 bare 5090 cell 0.0714 s; our bare at depth 2 = 0.0710 s).
Depth 8 fits (13.6 GB) but is slower (tests_seconds grows as 7 sub-batches contend). 4090 pair at depth 4 (§1): 0.0532 / 0.2617 =
4.92x; the 5090 wins on the hashed relation (-22 %) and is +8 % on the bare one (host-bound at 0.05 s; EPYC 7543 vs Ryzen 7950X host).

Art ids (all remote=1): hashed p4 proofs **art:5b0eac9f**, result art:6b1ef656, pinned verdict **art:390ba109**; bare p4 proofs
art:6d1b6af6, result art:c9704fc7, verdict art:a91cf470; hashed p8 art:98c12b9d / art:f9eb7ae2 / art:611e91d7; bare p8 art:932fa4ad /
art:f5d13909 / art:dbd15954; hashed p2 art:e8284e73 / art:92313e51 / art:54c5dc4b; bare p2 art:607b68a1 / art:df2a90bc / art:7e9327e4
(proofs / result / verdict); gate hashed art:db535917, gate bare art:1ab1794f; suite stdout art:58c9ded0. Full ids in
`evidence/store_ids.txt`.

## 3. The 5090 cold compile: 449.6 s → 46.2 s (6ffa035)

**Finding.** pipe_test took **449.6 s** on the 5090 vs 8.4 s on the 4090. faulthandler dumps (`evidence/probe_setup.py`) put the whole
time in `witness_device.FusedWitness.__init__` → `RawModule.get_function`: CuPy's NVRTC build (`-arch=sm_120`) of the hashed system's
fused witness kernel (register form, 280 KB source, 3626 lines, 3967 terms, m = 4442). Isolated with the CUDA 12.8.93 toolchain on the
pod (`evidence/probe_nvrtc*.sh`, `probe_ptx_route.py`): the **compute_120 front end (cicc) runs > 4 min** (killed; in-process ~7.3 min),
while **compute_89: nvcc -ptx 9.9 s, ptxas sm_120 on that PTX 8.9 s**; in-process NVRTC compute_89 10.7 s + driver JIT to sm_120 8.4 s.
The 4090 (sm_89) built the same kernels in seconds. Not in any timed number (the warm-up absorbs it), but every fresh 5090 in the device
wave paid it once per kernel (~10 min per pod counting the bare kernel).

**Fix, commit 6ffa035** (`witness_device.py`): on compute capability >= 12.0 the fused witness kernel is NVRTC-compiled to compute_89
PTX (cached next to CuPy's kernel cache, keyed by source digest + NVRTC version + arch) and loaded with `RawModule(path=...)`, i.e.
JIT-compiled to sm_120 by the driver (its own cache in `~/.nv/ComputeCache`). Other devices keep CuPy's native build byte-for-byte
(`ptx_arch()` returns None). `LIGERO_WITNESS_PTX_ARCH=native` restores the old path everywhere; `=NN` forces compute_NN PTX.
New test `witness_device_test.py::test_ptx_route_equals_native_build[fp4-nvf4, fp4-nvf4+poseidon2]`: native build == PTX route bit for
bit on arbitrary residues (the hashed case skips on sm_120 unless `LIGERO_TEST_NATIVE_CC12=1`: its native build is the 7-min one).

5090 at 6ffa035, suite r20260923-224554-d69a (fail=0):
* witness_device_test **6/6** (native == PTX for both fp4 kernels, with LIGERO_TEST_NATIVE_CC12=1; bf16-hopper / fp8-hopper / fp4
  fused == torch program through the PTX route).
* **cold pipe_test (empty CuPy + driver caches): 2/2 in 46.2 s** (d86e014: 449.6 s), every other kernel also built from scratch.
* gates: hashed 4 honest + 92/92 negatives, **0 failures**; bare 2048/2048 + 116/116 + 3015/3015, **0 failures**.
* depth 4: hashed t.total 0.2225 s, bare 0.0609 s; Rust pinned 7/7 ACCEPT both.

**Runtime A/B** (r20260923-225024-0075, depth 4, interleaved on the same pod, all 8 Rust pinned 7/7 ACCEPT):

| relation | native sm_120 (s) | compute_89 PTX + JIT (s) |
|---|---|---|
| fp4-nvf4+poseidon2 | 0.2145, 0.2340 | 0.2247, 0.2068 |
| fp4-nvf4 | 0.0665, 0.0634 | 0.0640, 0.0609 |

The fused-witness phase (`split.witness_torch_seconds`) is 0.0007 s hashed either way; the spread is pod noise in the tests phase. No
runtime cost. Across the six depth-4 runs on this pod (22:33–22:53Z) the hashed cell spans 0.204–0.234 s and the bare 0.058–0.067 s;
the ratio stays 3.4–3.7x.

Art ids (6ffa035, remote=1): d69a hashed p4 proofs art:401861cb, result art:8fc237f8, verdict art:d9dcaca4; bare p4 proofs art:acc05e26,
result art:174a1a9f, verdict art:f49e08ea; gates art:c7d87e4f (hashed), art:4d5b36c3 (bare); stdout art:0ff4ac8d; wd_test log
art:748263b8; cold pipe_test log art:e489dc0c. A/B: see `evidence/store_ids.txt` (r20260923-225024-0075 lines).

## Discrepancies

* `fold_test.py::test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]` fails at d86e014 (and main's 5d88d70 wording): the test
  asserts rows-per-unit ratio < 4.1 while its own comment says the Ampere v1 fold is 3.6 % super-linear (14576 vs 4 x 3516 = 4.1456).
  The threshold contradicts the measurement it cites; not fp4, not mine to fix (flagged for the coordinator).

## FINAL (23:17Z)

**Branch tip `lane/fp4-decode-3` @ 6ffa035** (1 commit on d86e014: fused witness kernel as compute_89 PTX + driver JIT on compute
capability >= 12.0, + differential test). Never merged.

**5090 pair** (lx80c24sagdao0, 4096 VUs, l=16384, `--zk --mode interactive`, local coins, best depth `--pipeline 4`, d86e014,
r20260923-222226-d052): **bare `fp4-nvf4` t.total 0.0576 s, hashed `fp4-nvf4+poseidon2` 0.2038 s = 3.54x** (Table 2 bare 5090 cell
0.0714 s). Depth sweep 2 / 4 / 8: bare 0.0710 / 0.0576 / 0.0616, hashed 0.2229 / 0.2038 / 0.2113 (depth 8 fits: 13.6 GB peak).
Six depth-4 runs on the pod 22:33–22:53Z: hashed 0.204–0.234 s, bare 0.058–0.067 s, ratio 3.4–3.7x. At 6ffa035: 0.2225 / 0.0609 s;
native-vs-PTX A/B = noise (§3).

**4090 pair** (k39j0s2bvhlljf, same workload, depth 4, d86e014; the predecessor's suite r20260923-211439-913b, which I recovered):
**bare 0.0532 s, hashed 0.2617 s = 4.92x**. The 5090 is 22 % faster on the hashed relation and 8 % slower on the host-bound bare one.

**Rust:** pinned `ligero-verify batch` (no `--allow-any-system`) over a real dump of every bench: hashed system pinned as `fp4-nvf4+hash`
(sys_id 8c6d260c, m=4442), bare `fp4-nvf4` (sys_id a825ba0b); **7/7 ACCEPT on every one of 18 dumps** (5090: 6 at d86e014, 2 at
6ffa035, 8 A/B; 4090: 2 at d86e014; plus fp4-decode-2's recovered 9002 dump, art:671c7ec9), union bound 2^-128.54, Python agreement 7/7. `cargo test --release`
48/48 (98c95b1 = d86e014's ligero-verify).

**Gates, 0 failures** (LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1, 2048 VUs): hashed 4 honest sub-batches + 92/92 negatives rejected;
bare 2048/2048 + 116/116 + 3015/3015 rejected — on the 5090 at d86e014 and at 6ffa035, and on the 4090 at d86e014.

**Cold compile fixed:** a fresh 5090 spent 449.6 s NVRTC-building the hashed fused witness kernel (compute_120 front end); 6ffa035 builds
it as compute_89 PTX + driver JIT: **cold pipe_test 46.2 s**, bit-identical W (new differential test), no runtime cost (A/B).
**Full `pytest backends/direct/ligero` on the 5090 at 6ffa035** (r20260923-225436-1399, art:7413f051): **249 passed, 3 skipped, 1 failed**
= the same `fold_test` bf16-ampere-x4 stale threshold the 4090 hit at d86e014 (248 passed there; +1 = the new test).

**Art ids** (68, all remote=1; `evidence/store_ids.txt`): 5090 d86e014 hashed p4 proofs art:5b0eac9f / result art:6b1ef656 / pinned
verdict art:390ba109; bare p4 art:6d1b6af6 / art:c9704fc7 / art:a91cf470; gates art:db535917, art:1ab1794f; stdout art:58c9ded0.
5090 6ffa035 hashed p4 art:401861cb / art:8fc237f8 / art:d9dcaca4; bare p4 art:acc05e26 / art:174a1a9f / art:f49e08ea; gates art:c7d87e4f,
art:4d5b36c3; wd_test art:748263b8; cold pipe_test art:e489dc0c. 4090 d86e014 hashed p4 art:7de9f86b / art:b3232930 / art:acfd35fa; bare
p4 art:2f06276d / art:e86293a2 / art:99060fb5; gates art:ecacc98b, art:2bf0289a; cargo test art:fc849366.

**Pods:** 4090 k39j0s2bvhlljf terminated 22:39Z (this lane 22:18–22:39Z ≈ $0.26; pod life 18:13–22:39Z ≈ $3.3 over three lanes).
5090 lx80c24sagdao0 terminated 23:16Z (this lane 22:18–23:16Z ≈ $0.96; pod life ~21:00–23:16Z ≈ $2.2). **Lane ≈ $1.2 of $3.**
Both pods confirmed absent from `pods list`.

**Remaining:**
* `fold_test.py::test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]` fails (stale threshold, not fp4; Discrepancies).
* The PTX route covers `witness_device.FusedWitness` only; other NVRTC kernels built fine cold on the 5090 (46 s total), but a relation
  with a bigger non-witness kernel on sm_120 could hit the same cicc cliff: `ptx_arch()` is the reusable switch.
* Table 2 bare 5090 cell (0.0714 s) vs today's 0.0576 s at depth 4 on this pod: the coordinator decides which to print.
* Leaf-agnostic packing (24-bit lanes, fp4-decode §0) unchanged.
