---
lane: flock-glue
kind: report
created: 2026-09-25T10:11Z
status: final
---

CHECKPOINT b3a3bf2 (12:17Z) [final] FINAL (re-check after naming handoffs by file): 4096 VUs Flock b684b12 Fast (~2^-100, NOT CLEARED) e2e vs bare A100 BF16 3.26x->1.18x, H100 BF16 12.3x->1.58x, H100 FP8 6.04x->1.42x; r2 stand-in NOT GRANTED 2.18/2.87/2.59x; pods terminated 12:11Z, ~$7.4; no lane branch (notes-only lane).
CHECKPOINT b3a3bf2 (12:16Z) [final] 4096 VUs Flock b684b12 Fast (~2^-100, NOT CLEARED) e2e vs B-Ligero bare before->after: A100 BF16 3.26x->1.18x, H100 BF16 12.3x->1.58x, H100 FP8 6.04x->1.42x; kernel 1.00->1.11x, 1.24->1.41x, 1.05->1.18x; r2 stand-in (NOT GRANTED) 2.18/2.87/2.59x. GPU PoW grind + device unit witness + side-stream overlap. Pods 56nan0h04ho1u9 + oypxgunobip13f terminated 12:11Z, ~$7.4. Runs r20260925-114930-2278/-aed8 PRESERVED.
CHECKPOINT ba852261 (12:10Z) [open] H=2 witness (64 VU/CTA) bit-exact but no gain on H100 BF16 4096 (devovl 0.1673 vs H=1 0.1683, dev run); keep H=1. Final runs A100 r20260925-114930-2278, H100 r20260925-114930-aed8 preserved. Wrapping up: pods drain, report, handoff.
CHECKPOINT 78b1a62e (11:51Z) [open] final recorded runs launched: A100 r20260925-114930-2278 (ampere_bf16), H100 r20260925-114930-aed8 (hopper bf16+e4m3): before/devwit/devgpu/devovl x 1024/4096 (Flock b684b12 default ~2^-100) + flock-128-r2 cost (Fast100 x2) + nsys per-batch kernel time. Found: GPU grind cutoff 8 bits (host below) halves idle GPU gaps; side-stream witness overlap -19 ms A100, ~0 H100 at 4096 (SM contention), -25 ms H100 at 1024. Witness kernel knobs flat (~25 ms@64VU H100): per-level latency bound.
CHECKPOINT ac2a497 (11:20Z) [open] recorded runs r20260925-111311-dc17 (A100) / -250b (H100), Flock b684b12 default ~2^-100: 4096 VUs prover wall before->devgpu: A100 bf16 0.871->0.302 s (3.67x->1.27x bare), H100 bf16 1.033->0.195 (9.1x->1.72x), H100 fp8 0.485->0.114 (6.9x->1.61x). Building mode 3 (side-stream witness overlapping BLAKE3 proof). flock-128 handoff 1055Z received: r2 = 2x Fast100, will re-time.
CHECKPOINT none (11:04Z) [open] A100 4096 VUs ampere_bf16 (Flock b684b12 ~2^-100 profile): device witness + GPU PoW grind -> FFI sum 0.302 s = 1.27x bare (host grind 0.626 s); harness rebuilt BLAKE3 R1CS per call (~1 s), now cached; witness kernel 46 ms latency-bound, profiling per-segment critical path. H100 pod oypxgunobip13f up.
CHECKPOINT 5e21eead (10:53Z) [open] device unit witness bit-exact on 3 pipes (64 VUs); batched kernel 47.6 ms@64VU ampere, profiling latency now; host PoW grind identified as 0.06-0.11 s/proof host glue; handoff 20260925T1020Z acted on: every timing labelled Flock b684b12 profile (~2^-100 campaign accounting, 16-bit PoW credit, GF(2^128)). Next: A100 bench 1024/4096, H100 pod.
CHECKPOINT a19aacb (10:37Z) [open] A100 pod 56nan0h04ho1u9 up; wrote device unit-witness kernel (bit-sliced chained VUs, level-parallel) + FFI patch (GPU PoW grind, phase timers, per-circuit CSC cache); building+bit-exact check run r20260925-103733-28ee
CHECKPOINT none (10:11Z) [open] started: reading contract, flock-bench-80gb/flock-bench reports; next: plan device-side unit witness + pods

# flock-glue: Flock-CUDA end to end at 4096 VUs is 1.18x B-Ligero bare on A100 BF16, 1.58x on H100 BF16 and 1.42x on H100 FP8 (was 3.26x / 12.3x / 6.04x). Profile: Flock b684b12 `Fast`, about 2^-100, NOT CLEARED

**Flock profile label (applies to every Flock number below unless a row says otherwise).** Flock b684b12 default
`Fast` Ligerito, GF(2^128), SHA-256 Fiat–Shamir and Merkle (CUDA_HASH).
- Coordinator 1020Z accounting: about 2^-100, taking the 16-bit PoW credit.
- flock-128 TABLES accounting, no PoW credit: 2^-110.0 with live coins, 2^-50 under Fiat–Shamir.
- **Not cleared.** These numbers can't sit next to B-Ligero's 2^-128 cells without this label.

The **r2** rows use the cost stand-in for flock-128-r2: `Fast100` run twice. It would be about 2^-194.5 for the GPU pair
with live coins, but red-team-flock marks it NOT GRANTED (the reps aren't bound to one commitment, and no live-coin
challenger exists). Those rows are **not cleared** either.

Baselines: B-Ligero bare at 4096 VUs, the same as the brief: A100 BF16 0.2374 s, H100 BF16 0.1131 s, H100 FP8 0.0706 s.
There's no bare baseline at 1024 VUs, so the 1024 rows give absolute times only.

## Result

**End to end** means prover wall time for one batch, meaning one census-unit proof plus one BLAKE3 row-leaf proof. It
counts every host step inside the prover calls (FFI, grinding, uploads, syncs) and leaves out only the harness's
parse of the returned proof. Each figure is the median of 5 reps.

**Kernel** means the per-batch union of GPU kernel time from nsys (`-t cuda`), median of 3 batches after 3 warm-ups.

Every proof verified, and every negative rejected.

### 4096 VUs, Flock b684b12 `Fast` (~2^-100, not cleared)

| line | before e2e | after e2e (best) | before kernel† | after kernel (best) | witness kernel | idle GPU time per batch |
|---|---|---|---|---|---|---|
| A100 SXM4 80GB, ampere_bf16 | 0.7734 s = **3.26x** | 0.2811 s = **1.18x** (devovl) | 0.2377 s = 1.00x | 0.2647 s = 1.11x | 47 ms | ~17 ms |
| H100 80GB HBM3, hopper_bf16 | 1.3961 s = **12.3x** (ffi min 0.859 = 7.6x; earlier run 1.0326 = 9.1x) | 0.1782 s = **1.58x** (devgpu; devovl 0.1789) | 0.1406 s = 1.24x | 0.1600 s = 1.41x | 21 ms | 16–22 ms |
| H100 80GB HBM3, hopper_e4m3 | 0.4263 s = **6.04x** | 0.1005 s = **1.42x** (devovl) | 0.0743 s = 1.05x | 0.0832 s = 1.18x | 10 ms | 17–25 ms |

† Before kernel is derived as the after-devgpu kernel union minus the witness kernel. The before path's kernels are the
same proof kernels, since its witness arrives by H2D copy rather than a kernel. This agrees with the prior lanes'
1.0–1.2x (flock-bench, flock-bench-80gb).

All four variants at 4096 VUs, prover wall time and ratio to bare:

| line | before | devwit | devgpu | devovl |
|---|---|---|---|---|
| A100 BF16 | 0.7734 (3.26x) | 0.6283 (2.65x) | 0.3003 (1.26x) | 0.2811 (1.18x) |
| H100 BF16 | 1.3961 (12.3x) | 0.4775 (4.22x) | 0.1782 (1.58x) | 0.1789 (1.58x) |
| H100 FP8 | 0.4263 (6.04x) | 0.2986 (4.23x) | 0.1018 (1.44x) | 0.1005 (1.42x) |

The variants:
- **before:** host-built witness, 2.15 GB pageable H2D upload, host PoW grinding.
- **devwit:** device witness, host grinding.
- **devgpu:** device witness, plus GPU grinding for sites of at least 8 bits.
- **devovl:** devgpu, with the witness on a non-blocking side stream that overlaps the BLAKE3 proof. The unit proof
  waits on an event and then does a D2D copy.

Kernel union for devgpu / devovl: A100 0.2849 / 0.2647, H100 BF16 0.1616 / 0.1600, H100 FP8 0.0844 / 0.0832.

### 4096 VUs, r2 cost stand-in (`Fast100` x 2, ~2^-194.5 with live coins, NOT GRANTED, not cleared)

This is two sequential proof pairs in one FS domain. The unit witness is built once on the device and used by both
reps.

| line | devovl e2e | kernel | devgpu e2e |
|---|---|---|---|
| A100 BF16 | 0.5173 s = 2.18x | 0.4835 s = 2.04x | 0.5803 s |
| H100 BF16 | 0.3247 s = 2.87x | 0.2891 s = 2.56x | 0.3500 s |
| H100 FP8 | 0.1827 s = 2.59x | 0.1496 s = 2.12x | — |

flock-128 (1128Z) measured the r2 H100 BF16 pair at 0.761 s through the host-upload path and estimated 0.51 s with one
upload. The device witness brings it to 0.325 s.

### 1024 VUs, Flock b684b12 `Fast` (absolute seconds; no bare baseline)

| line | before | devwit | devgpu | devovl | kernel devgpu / devovl | r2 devovl |
|---|---|---|---|---|---|---|
| A100 BF16 | 0.3413 | 0.3585 | 0.1173 | 0.0920 | 0.1028 / 0.0854 | 0.1696 |
| H100 BF16 | 0.3380 | 0.3501 | 0.0757 | 0.0605 | 0.0592 / 0.0477 | 0.1207 |
| H100 FP8 | 0.3375 | 0.2377 | 0.0537 | 0.0486 | 0.0377 / 0.0328 | 0.0912 |

### Checks
- The 64-VU check passes on all 3 pipes in both final runs:
  - The device unit witness (z, a, b and z_lincheck bytes) is bit-exact against the host witness.
  - Unit and BLAKE3 proofs verify.
  - Tampered proofs reject.
  - A planted NaN rejects.
- The planted-NaN runs at 4096 VUs (`devovl-nan`, under both `Fast` and r2) reject the unit proof in every run.

## What made the difference (A100 / H100 BF16 / H100 FP8, 4096 VUs)
1. **GPU PoW grinding, the largest single item: 0.33 / 0.30 / 0.20 s per batch.** Flock-CUDA ground every PoW site on
   the host with single-thread SHA-256: 0.09–0.14 s for the unit proof and 0.25–0.27 s for BLAKE3. That time had been
   counted as "host orchestration".

   I hooked `FsChallenger` grinding in `challenger.hpp` onto the existing device kernel
   `search_sha256_proof_of_work_nonce` from `pow_grind.cuh`. It returns the same minimal nonce as the host loop, so the
   proofs don't change.

   The cutoff, `FLOCK_GLUE_GRIND_MIN=8`, keeps sites under 8 bits on the host, because a GPU round trip is slower than
   the host there. A cutoff of 12 left 0.5–1.9 ms host gaps, and moving to 8 saved about 10 ms on the H100.
2. **Device unit witness: 0.15 / 0.92 / 0.13 s.** A 10–47 ms kernel replaces the 2.15 GB pageable H2D upload, which took
   0.38 s on A100 and 1.0 s on H100 BF16.

   The kernel builds the witness from the instance operands, the census netlist and the c_in chain. It runs one CTA per
   32 VUs, bit-sliced, with level-ordered gate segments. The before path also needed a 0.14–0.54 s host witness build;
   that ran once outside the timing and isn't in the before numbers.
3. **Side-stream overlap: 19 ms on A100 at 4096 VUs, 12–25 ms at 1024, about 0 on H100 at 4096.** On the H100 at 4096
   the witness CTAs compete for SMs with the BLAKE3 kernels.

   The overlap needed every `cudaDeviceSynchronize()` in `prove_ffi.cu` and `ligerito_f256.cuh` changed to
   `cudaStreamSynchronize(0)`. Otherwise each sync drains the side stream.
4. **Harness fix (not prover time).** The bench harness rebuilt the BLAKE3 `BlockR1cs` on every call, about 1 s of call
   time. It now caches the statement once, with its digest.
5. **Tried, no gain:**
   - Kernel knobs: thread counts 256, 512 and 1024; lanes per gate 2^3 to 2^5; fused segments. All sit within ±15%
     (24.7–28.8 ms at 64 VUs on H100), except lanes = 2^3, which is slower at 38.8 ms.
   - 64 VUs per CTA (H=2, uint64 words) is bit-exact but gives devovl 0.1673 against 0.1683 for H=1 on H100 BF16 at
     4096. That was an unrecorded dev run and within run-to-run noise; the final recorded devovl was 0.1789.

   The kernel is bound by per-level latency, about 1,600–1,900 cycles per level, with 96 units in series per VU (48 for
   FP8). Its time barely depends on the VU count.

## What's left (remaining gap to 1x)
- **Flock-CUDA's proof kernels: 1.00x / 1.24x / 1.05x bare.** This is the floor for this profile without changing
  Flock's kernels.
- **Witness kernel: +0.20x / +0.19x / +0.14x.** It's latency-bound, not bandwidth-bound. Overlap hides it only when
  there are spare SMs (A100). Cutting it would need a shallower netlist or chaining fewer units per VU.
- **About 16–17 ms of idle GPU time per batch, in about 1,500–2,000 gaps.** These are host FS round trips and launch
  gaps inside Flock-CUDA's protocol loop. Fixing them needs a device-side challenger or CUDA graphs over the rounds.
  red-team-flock's R6 notes that `zc_challenger_device.cuh` already squeezes on the device, and a live-coin version of
  it hasn't been costed.

**Not done:**
- BLAKE3 leaves from device-resident rows. Mode 0 generates its own leaf messages on the device, so no upload is
  timed, but the messages aren't the census rows.
- The glue from unit input bits to leaf message bits inside one Flock proof. It wasn't built, even as a measurement.
- A clearable profile (flock-128-r2 needs R1–R8 from red-team-flock).

## Method
- **Harness.** Rust `glue_bench` sits in Flock's `verity_unit_glue.rs` test harness (`gpu_glue_tail.rs`,
  `gen_test.py`). It calls Flock-CUDA through FFI (`prove_ffi.cu`, patched by `patch_ffi.py`), with
  `MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000` on every run.
- **Circuits.** Census unit netlists come from `export_unit.py` and `unit.py`:
  - ampere_bf16: depth 299, 7,142 gates, 96 units per VU.
  - hopper_bf16: depth 169, 96 units per VU.
  - hopper_e4m3: depth 154, 48 units per VU.

  Unit m and BLAKE3 m at 4096 VUs are 32 and 33 for BF16, and 31 and 32 for FP8.
- **Flock tree.** b684b12 with `flock-glue-b684b12-tracked.patch` applied: build.rs sm_90, r1cs_hashes.rs,
  challenger.hpp, ligerito_f256.cuh and prove_ffi.cu.
- **Scripts.** `evidence/pod-scripts/` holds `10-build.sh`, `20-check.sh`, `30-bench.sh`, `25-nsys.sh` and
  `40-final.sh` (the final-run driver), plus `unit_witness.cuh`.

## Handoffs received
- **`20260925T1020Z-handoff-from-coordinator.md`** (Flock baselines are about 2^-100; label every timing with its profile; re-time under
  flock-128): acted on. Every table is labelled, and the r2 re-time is the second 4096 table.
- **`20260925T1055Z-handoff-from-flock-128.md`** (flock-128-r2 is `Fast100` x 2 with live coins, no PoW credit): acted on through the r2
  cost stand-in, with `GLUE_PROFILE=fast100 GLUE_FLOCK_REPS=2`.
- **`20260925T1128Z-handoff-from-flock-128.md`** (r2 numbers; upload the witness once): acted on. The device witness is built once per
  batch and reused by both reps, giving 0.325 s against their 0.51 s estimate on H100 BF16.
- **`20260925T1130Z-handoff-from-red-team-flock.md`** (flock-128-r2 NOT GRANTED, R1–R8): noted. The r2 rows are labelled NOT GRANTED and
  not cleared, and the stand-in doesn't bind the reps (R1).
- **`20260925T1131Z-handoff-from-coordinator.md`** (pods idle; upload once; not cleared): acted on. Everything is labelled "not cleared",
  and the upload-once point is covered by the device witness.
- **`20260925T1146Z-handoff-from-coordinator.md`** (`--custody-r2` always; no `fetch --all` or big fetches to the laptop): acted on. The
  final runs used `--custody-r2`, results were inspected on the pod, and nothing big was fetched.
- **`20260925T1202Z-handoff-from-coordinator.md`** (`--custody-r2` caveat: check `data preserved`): acted on. All four recorded bench
  runs show PRESERVED, and no repush was needed.
- **`20260925T1210Z-handoff-from-coordinator.md`** (STOP: laptop disk; write FINAL now): acted on. Both pods were terminated at about
  5:11 AM PT, and this report and FINAL were written without fetching anything.

## Runs and artifacts (all PRESERVED on R2)
| run | pod | what | run_record |
|---|---|---|---|
| r20260925-114930-2278 | A100 56nan0h04ho1u9 | final: check, 4 variants x 1024/4096, r2, nsys | art:863fbebf9c14c0ba1b87c7ea1f4cbfe335f2f8758facb746c0d1bd465edbd1af |
| r20260925-114930-aed8 | H100 oypxgunobip13f | final: check, BF16 and FP8, 4 variants x 1024/4096, r2, nsys | art:406987995a6bc7a879063f6a2fcbe0c21357f16d654bbc7bd973ea6bd141a573 |
| r20260925-111311-dc17 | A100 | first bench (before/devwit/devgpu) | art:3a68ff63ed2330adc0e772382e7128976824b0fe87564f31fad44e67f418752e |
| r20260925-111311-250b | H100 | first bench | art:9402a68e36c442d967a3ece0058135fc3e22116938c33f4e618b266572ed73a2 |

The final runs' telemetry resources: A100 art:aa2f74bd4fbb586ac12664bba864c8375805c962b08af12c7cdeb2f1f35ef7ed and H100
art:2c293e0aa424fd12a183cade4bdde2ab4bedaf42677eb680e8e16cf145a870ae.

The H=2 test and the kernel-knob sweeps were unrecorded dev runs on the pods, so they're cited as dev evidence only.

## Pods and spend
- **A100 SXM4 80GB `vy-flock-glue-a100`** (56nan0h04ho1u9, $1.59/h): up from about 3:18 to 5:11 AM PT. About $3.0.
- **H100 80GB HBM3 `vy-flock-glue-h100`** (oypxgunobip13f, $3.49/h): up from about 3:55 to 5:11 AM PT. About $4.4.
- **Total: about $7.4 of the $25 budget.** Both pods are terminated.

## FINAL

~~~text
tip: none (no repo worktree; notes and pods only; Flock patch and harness in lanes/flock-glue/evidence/)        merge-with: none
known-failures: all Flock timings are profile-labelled and NOT CLEARED (b684b12 Fast ~2^-100 with PoW credit, 2^-50 under FS; r2 NOT GRANTED per red-team-flock); BLAKE3 leaves from device-resident rows and the unit-to-leaf bit glue not built; H100 BF16 before e2e is noisy (1.03-1.40 s across runs); H=2 and knob sweeps are unrecorded dev runs; no lane/flock-glue branch exists because the lane made no repo commits (code is the patch plus scripts in evidence/), so --require-pushed reports it missing    pod: A100 56nan0h04ho1u9 terminated 12:11Z, H100 oypxgunobip13f terminated 12:11Z; ~$7.4
artifacts: art:863fbebf9c14c0ba1b87c7ea1f4cbfe335f2f8758facb746c0d1bd465edbd1af art:406987995a6bc7a879063f6a2fcbe0c21357f16d654bbc7bd973ea6bd141a573 art:3a68ff63ed2330adc0e772382e7128976824b0fe87564f31fad44e67f418752e art:9402a68e36c442d967a3ece0058135fc3e22116938c33f4e618b266572ed73a2
~~~

At 4096 VUs, under Flock b684b12 `Fast` (about 2^-100, not cleared), end-to-end prover time against B-Ligero bare is:
- A100 BF16: 3.26x before, 1.18x after.
- H100 BF16: 12.3x before, 1.58x after.
- H100 FP8: 6.04x before, 1.42x after.

Kernel-only, before and after: 1.00x to 1.11x, 1.24x to 1.41x, and 1.05x to 1.18x. The after figure includes the
device witness kernel.

The r2 cost stand-in comes to 2.18x, 2.87x and 2.59x.
