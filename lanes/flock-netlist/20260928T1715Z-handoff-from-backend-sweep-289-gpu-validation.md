---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T1715Z-handoff-from-backend-sweep-289-gpu-validation
campaign: backend-sweep
lane: flock-netlist
kind: handoff
status: final
repo: verity
origin: backend-sweep (bc-ea1c2c4f), via the coordinator
---

# #289 on the GPU: byte identity passes; 2–4× faster at m = 34 where reuse engages

This answers `internal/lanes/coordinator/20260928T1450Z-handoff-from-flock-netlist-gemm-gpu-validation-289.md`. The numbers and tables are in `docs/backend-sweep.md`, section "GEMM diagnosis: option 1 (m = 34) and #289 (options 2 and 3)".

**Source:** #289 at `85117061`, merged with #212 so the runs carry the sweep's statement cap and bucket keys. That's the validation tree `cursor/v289-gpu-validation-866f`, at `0a24e2e4`, `0f618e90` and `a9cf899c`. The prover code is yours unchanged. The shapes are the post-S-stack digests: `e4eaddfe…` (K = 2,048), `769f25c3…` (K = 8,192), and RoPE's `9254fd7a…` (RopeOut) and `a5eb3fa1…` (RopeOutAdd).

## Run A, byte identity: passes (L40S sm_89, driver 570.124.06, B = 16, m = 25–29)

- **`r20260928-151357-ad77`:** `SELFTEST=1 SELFTEST_GPU=1 WARM=0 RUNS=1`. `selftest.all_pass` is true with `selftest.gpu` true on all four shapes: 36/36 cases per GEMM coordinate and 35/35 per RoPE shape.
- **`r20260928-165411-16f5`:** the same statements with only the two GPU cases, whose lines are now kept in the record (`selftest.gpu_cases`; #299, below). On all four shapes:
  - `gpu_paths_agree`: `proofs_equal` and `transcripts_equal` are true, `host_units [true, true]`, `rep_reused [false, true]`;
  - `gpu_proofs_match_cpu`: `proofs_equal` and `transcripts_equal` are true. `host_units` is `[true, true]` on the GEMM coordinates and `[false, false]` on RoPE.

## Run B, speed: m = 34 (B = 1,024 / 512) and default (B = 256 / 64), against `main` (`adcf38bf`)

| Cell | K = 2,048 median | K = 8,192 median | `rep_reused` |
|---|---:|---:|---|
| L40S `main` m = 34, `r20260928-163419-65fc` | 2.921 s | 7.963 s | |
| L40S #289 m = 34, `r20260928-164500-5979` | 3.055 s | **3.956 s** | **false** (both reps proved in full) |
| H100 NVL `main` default, `r20260928-162831-3201` | 2.133 s | 7.172 s | |
| H100 NVL #289 default, `r20260928-161747-16c4` | **0.484 s** | **0.441 s** | `[false, true]` |
| H100 NVL `main` m = 34, `r20260928-163943-7975` | 3.036 s | 8.276 s | |
| H100 NVL #289 m = 34, `r20260928-164803-8f25` | **1.434 s** | **2.024 s** | `[false, true]` |

Against your three expectations:
1. **`t.witness_units` ≈ 0: yes,** on every #289 rep on both GPUs. On `main` it's 1.7–2.3 s per rep at K = 8,192.
2. **Rep 1's `t.witness` and `t.encoding_commitment` ≈ 0 where `rep_reused` is true: yes,** on the H100: 0.033 s and 0. Rep 1's host time is also about 0 (0.003 s).
3. **Host time grows by the host's unit evaluation:** mixed.
   - At K = 2,048 on the L40S, host time went from 0.58 / 0.45 s to 0.77 / 1.07 s per rep, so #289 doesn't gain there: 3.06 s against 2.92 s.
   - At K = 8,192, host time fell (1.68 to 1.3 s per rep), as did `witness_s`.

**Reuse at m = 34:**
- **The L40S (46 GB) didn't have the room:** `rep_reused` stayed false on both coordinates, and rep 1 proved in full. Proof sizes are unchanged (927,729 and 927,761 bytes, as on `main`).
- **The H100 NVL (94 GB) did,** and reuse engaged.

## Two things for you

- **[#299](https://github.com/danielreuter/verity/pull/299)** (draft, stacked on #289) is 12 lines of harness. The sweep record keeps the GPU cases' NEG lines as `selftest.gpu_cases`, and `SELFTEST_CASES=a,b` runs only the named cases. Take it or drop it. Without it, the per-case fields can't be read after a run, because the harness deletes each circuit after its selftest.
- **A harness bug that isn't yours:** `70-class-sweep.sh` exported CUDA 13.3's compat `LD_LIBRARY_PATH` only when it built. So on an R570 driver, every run that reused a cached binary failed every session with "driver insufficient", at `prove_circuit.cuh:415` on `main` and `:482` on #289.
  - It's fixed on #212 (`14ff2d6a`) and in the validation tree.
  - It's why my first m = 33 / m = 34 attempts looked like a device limit.
  - Those runs are labelled `invalid=…`.
  - #289 carries the old script from `main`, so a cached-binary run of #289 on an R570 pod hits it too.
