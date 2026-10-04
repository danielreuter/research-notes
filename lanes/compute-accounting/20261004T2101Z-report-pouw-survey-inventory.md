---
id: 20261004T2101Z-report-pouw-survey-inventory
campaign: pouw
lane: compute-accounting
kind: report
status: final
repo: danielreuter/verity
origin: hidden-zk (bc-f9071e48-09a6-5b2d-ad82-156dce9fb5fc), relayed by compute-accounting from its agent store
---

# PoUW survey inventory for the repo-principles draft

Lane hidden-zk, 2026-10-04T19:28Z, read-only, from `origin/main` 06edf032c (worktree `/tmp/wt-survey`). Line counts
are `wc -l`. Sizes for context: `benchmarks/pouw` is about 43.8k non-test lines plus 7.5k lines of tests,
`verity_pouw` is 10.1k, and `protocols/pouw/lean` is 68.6k.

## 1. Kernels

| Kernel (path, lines) | Op | Build | Bit-exact reference, test | GPU | Live claim |
|---|---|---|---|---|---|
| `benchmarks/pouw/kernels/pouw_gemm.cu` 268, `__init__.py` 51 | NCP u8×s8 route-U GEMM and its s8 control (16-deep checkpoints); Pearl's e4m3 GEMM on `ada` | torch `cpp_extension.load` at import, sm_89 | `gemm_bench` gates against `verity_pouw` `ncp-v1.checked()` and `pearl-fp8-v4`; `test_native_route_u`, `test_route_u_shift` | RTX 4090 sm_89 | README only: r20260928-120218-f7d7, SASS r20260928-120439-c053 |
| `pearl_c/`: `pearl_c.cu` 716, `hash.cuh` 366, `hash_sm120.cuh` 321, `hash_h2.cuh` 205, `h1_standin.cu` 199, `hash_host.cpp` 70 | Pearl-C G4 FP8 GEMM with the BF16 peel, forming, noise lines, tickets, BLAKE3 -h1/-h2 trees | nvcc 12.9.1 ahead of time, sm_90a cubin (hash also sm_120a); SASS gate and FTZ gate (`ftz_pins.json`); `ship.sh` pins the tree as one commit; `run.py` is ctypes on libcuda | `fixture.py` from `verity_pouw.schemes.pearl_c` (h100-v0/v1/-h1/-h2), `verity.commitments`, `verity.ml.kernels`; `twin.py`; `test_pearl_c_{kernel,h2,hash_host,bench,h1_tune,ftz_gate}` | H100 SXM sm_90a | pinned γ `pearlCGammaH100Rev1_{8192,16384}`; no live claim. The chain `hash_h2`→`hash_sm120`→`hash.cuh` (892 lines) is included by the live sm120 kernel |
| `pearl_c_sm120/`: `pearl_c_sm120.cu` 827, `mainloop_sm120.cuh` 363, `h2_rows_stats.cuh` 43 | Pearl-C v1 on `mma.sync` (E4M3 m16n8k32, BF16 peel), -h2 hashing | nvcc ≥ 12.8 (default cuda-13.0) ahead of time, sm_120a, `-O3 -fmad=false -cubin`; `sass_gate.py` (QMMA/HMMA, no local memory); `fixture.py` | `fixture.py` from `verity_pouw.schemes.pearl_c` + `pearl_kw` + `pearl_c_device`; `verify.py` through `verity_pouw.audit.Verifier`; `benchmarks/pouw/tests/test_pearl_c_sm120.py` (929), `protocols/pouw/tests/test_pouw_pearl_c_sm120.py` | RTX PRO 6000 sm_120 | **Live**: #1116 window r20261004-150005-0c35 (`pearl-c-sm120-v1-h2`, ACCEPT, 54.25%, γ `pearlCGammaSm120v1LoopCast8p72Rev1Cap1000_8192`); served table #1001 through vLLM |
| `pearl_c4/pearl_c4.cu` 871 | Pearl-C4 NVFP4/MXFP4 block-scaled GEMM, chain, TurboSHAKE hashing | CUDA 12.9 nvcc ahead of time, sm_120a, against `pouw_hash.cuh` fetched at pinned `HASH_COMMIT` 71086532 (sha256 checked); `sass.py`; `dev.py` (ctypes) | `fixture.py` from `verity_pouw.schemes.pearl_c4` + `verity.commitments.turboshake`; `twin.py` on `verity.ml.kernels.block_scaled_batch`; `test_pearl_c4_{f1_fast,real,twin}`, `test_pouw_pearl_c4` | sm_120 | Pearl-C4 runs (`pearl-c-nvfp4-v0`, 32 pinned `gammaFp4*_sm120*` plus 15 `pearlCGammaFp4*`); #1034 (hidden_zk) uses its scheme, not this kernel |
| `pouw_hash/`: `pouw_hash.cuh` 672, `vectors.cuh` 351, `pouw_hash_bench.cu` 853, `pouw_hash_check.cu` 132 | BLAKE3, Keccak/TurboSHAKE128, SHA-256 on device | CUDA 12.9.1 nvcc ahead of time; `sass.py` | `check.py` against `verity.commitments.{turboshake,blake3}` and `pearl_c`; `test_pouw_hash` | sm_120 | indirect: included by the sm120 kernel (#1116) and by `pearl_c4` |
| `nvfp4_sm120/`: `nvf4_plain.cu` 195, `nvf4_bench.cu` 163, `mainloop_nvf4.cuh` 435, `fp8_bench.cu` 143 | plain NVFP4/FP8 GEMMs; an NVFP4 mainloop bench | nvcc commands run by hand from the file headers, sm_120a; `nvf4_plain.cu` is compiled into `libpouw_harness.so` | gates against its own numpy decode, no `verity` import; no test | sm_120 | `nvf4_plain` is a harness baseline (indirect); the benches are not cited |
| `harness/native/`: `harness.cu` 626, `cutlass_{2x,3x,registry}.cu` 468, `lt.cu` 315; `harness/ieee_pin.cu` 357 | fill/derive/chain kernels; cuBLASLt and CUTLASS baselines (the timed denominator); IEEE pin probes | `native/build.sh` ahead of time, sm_120a, CUTLASS v4.8.0 pinned, output **keyed by source hash + nvcc version + cuBLAS headers**, per-object cache; `jobs/toolkit.sh` pins nvcc 12.9.86 | numpy twins `fill.py`, `derive.py` (preflight on every run), `ieee_pin.py`; `test_harness` (1,458), `test_ieee_pin`, `test_sass_gate` | sm_120 | **Live**: #1116's baselines (`bench.py`, `verify.py`) |
| `integrations/vllm/verity_vllm/protocol_options/pouw_cuda/`: `ncp2.cuh` 580, `ncp2_fast.cuh` 426, `ncp2_fused.cu` 406, `ncp2_kernels.cu` 368, `ncp2_host.cpp` 192, `ncp2_rates.cu` 26 | NCP v2 prover in vLLM: GEMM plus SHA-256/SHA-512/SHAKE256/TurboSHAKE transcript | `pouw_device._build`: nvcc on first use, arch `$VERITY_POUW_CUDA_ARCH` (default 89), cached in `~/.cache/verity/pouw_cuda` under a sha256 key | `verity_pouw` NCP (vLLM tests; `benchmarks/pouw/ncp2_gpu_bench.py` + test) | sm_89 | vLLM NCP option (a product); no table |
| `pouw_pearl_c_triton.py` 58, `pouw_pearl_c_screen.py` 85 (`screen_into`) | Pearl-C scatter and liveness screen in vLLM | Triton JIT (Triton's own cache keyed by source and arch) | screen's torch ops; the band's rows go to `verity_pouw` `pearl_c.live_row` | sm_120 | served table #1001 |

- **B200:** only `pearl_b200_setup.sh` (nvcc 13.3) and `pearl_calibration.py`, which calibrate Pearl's upstream kernel. No kernel of ours ran on B200, and none ran on sm_80.
- **Compile on first use** fits where it is already done: vLLM `pouw_cuda`, `harness/native/build.sh`, Triton, and `cpp_extension` (`pouw_gemm`). These are three separate implementations of the same hash-keyed cache, which one registry could replace.
- **It doesn't fit as stated** for `pearl_c`, `pearl_c_sm120`, `pearl_c4` and `pouw_hash`. Each claim is about one exact cubin: built ahead of time off the GPU box with a pinned toolkit, refused unless the SASS/FTZ gate passes, fixture built beside it, then manifest and GPU identity checked on the pod.
  - The fix: the cache key must include the pinned toolkit, the cache fill must run the gate, and the claim must record the cubin's hash.
  - A timed run must never compile on the leased GPU. `harness/native/build.sh` already enforces this: an existing build is reused.
- **Torch beyond a container:**
  - `pouw_pearl_c_screen.screen` decides record rows outside a 2⁻¹⁰ band in torch FP32. This is the prover's records, and rows inside the band are decided exactly.
  - Benches only: `vllm_bench`, `gemm_bench` and `e2e_audit` draw noise from torch and run Pearl's quantization and peel as torch ops (the README says so). `pearl_c/vendor.py` and `tools/native_peak` use `torch._scaled_mm` for baselines and peaks.
  - No torch in `verity_pouw` or in any verifier path (`pearl_c_vllm/verify_run.py`, `harness/verify.py`, #1116's audit).

## 2. Duplication

- **Python hashing: none in the references.** `verity_pouw` uses `verity.commitments` (`blake3`, `keyed`, `turboshake128`, `MerkleTree`) and stdlib `hashlib`.
  - Unique to PoUW: `bls12_381.py` 391 (min-sig BLS verify, RFC 9380 hash-to-G1) and `beacon.py` 111 (drand). This is generic crypto with no twin in the repo; it could move to core (commitments or randomness).
- **Hashing in gates:** `verity_pouw/circuit/hashes.py` 252 + `words.py` 298 (SHA-512 compression and Keccak-f/TurboSHAKE as IR Definitions) against `backends/flock/python/verity_flock/sha512_circuit.py` 212 (SHA-512 in Flock's circuit model). The same compression is written twice, in two models.
- **Hashing in CUDA** (PoUW has about 2.5k lines of device hashing):

  | Hash | PoUW copies | Copies elsewhere |
  |---|---|---|
  | BLAKE3 | `pearl_c/hash*.cuh` 892; `pouw_hash.cuh` 672 | — |
  | Keccak/SHAKE/TurboSHAKE | `pouw_hash.cuh`; vLLM `ncp2.cuh` 580 + `ncp2_fast.cuh` 426 | `benchmarks/pous/band_gpu/pous_native.cu` 1,825 |
  | SHA-512 | `ncp2.cuh` | `backends/flock/cuda/sha512.cuh` 349 |
  | SHA-256 | `ncp2.cuh`, `pouw_hash.cuh` | vLLM `commit/committer/native_leafhash.cu` 194 |

- **FP semantics:**
  - `schemes/pearl_kw.py` lines 108–222, about 115 lines: f32/bf16/e4m3 casts and bf16 mul, div, fma, max and min. Twin: `verity.ml.tc.cast` 130 (`bf16_to_f32_word`, `f32_to_bf16_rn_word`, `f32_to_e4m3_sat_word`, `e4m3_to_f32_word`) and `verity.ml.fp32` 342 (BF16 element-wise).
  - `pearl_kw.py` device matmul, lines about 245–390, about 145 lines (`_Term`, Pearl's GFloat, `replay`, `device_dot`). Twin: `verity.ml.tc.models` 903 / `total_fp8` 164.
  - `pearl_c4.py` casts, lines 196–262, about 65 lines (`e2m1`, `ue4m3`, `ue8m0_up`). Twin: `verity.ml.tc.cast.f32_to_e2m1_sat_word` and `verity.ml.boolean.fp4` 232. `pearl_c4` already imports `BLACKWELL_SM120_NVF4` from the models.
  - `harness/fill.py` 114 + `derive.py` 219: numpy E4M3/E2M1/UE4M3/UE8M0 rounding and the MX/NVFP4 scale rules. Twin: `verity.ml.kernels` / `tc.cast`.
  - `pearl_c4/f1_fast.py` 213 is a numpy fast verifier for `pearl_c4.tile_debit`, kept in benchmarks instead of next to its reference.
  - Lean: `Pouw/Protocol/Fp8Atom/Fp32.lean` 58 (a rational RN model) + `E4M3.lean` 52 + `Atom.lean` 207, against core's `Verity/Protocol/Fp32.lean` 212 (bit level) + `TC/Spec.lean` 185 + `TC/Relation.lean` 416. That is two FP32 models and two step models.
- **Sampling: no duplication.** `audit.py`, `pearl_c_work.py`, `ncp.py`, `circuit/plan.py` and `circuit/anchors.py` use `verity.randomness` (`derive`, `frame`).
  - Pearl's noise lines (`pearl_kw.sample_line`, a BLAKE3-keyed XOF) are Pearl's spec, not a sampler.
  - `anchors.py:363` takes `secrets.token_bytes` as a source. Benchmarks use numpy/random for inputs only.
- **Harness and pod scripts:**
  - Seven ctypes-on-libcuda loaders, each with its own module/launch/NVML-UUID code, about 4.4k lines in all: `harness/arm.py` 321 + `native.py` 426, `pearl_c/run.py` 631, `pearl_c/h1_bench.py` 853, `pearl_c_sm120/run.py` 934, `pearl_c4/dev.py` 432 + `pearl_c4_arm.py` 415, `nvfp4_sm120/nvf4_bench.py` 774.
  - Six SASS/FTZ gates: `harness/sass_gate.py` 1,437 (the general one, with `sass_pins.json` 509), plus `pearl_c_sm120/sass_gate.py` 89, `pearl_c4/sass.py` 93, `pouw_hash/sass.py` 100, `check_route_u_sass.py` 33, `pearl_c/ftz_gate.py` 208.
  - `tools/native_peak/measure.py` 773 (dense-GEMM peak via torch) overlaps the harness's cuBLASLt/CUTLASS baselines.
  - Little overlap with `benchmarks/one_stage` (1,013) or `backends/numerical/bench` (14.4k). `harness/ledger.py` 621 writes the store kind `kernel-attempt/v1`, which `tools/research` registers; it is not a duplicate.

## 3. Sprawl

**The `SCHEMES` entries:**

| Name | Status | Cited by |
|---|---|---|
| `ncp-v1` | stays | the vLLM NCP option (`protocol_options/pouw.py`), circuit `ncp-v2`, Lean NCP (42 pins) |
| `ncp-v1-shift24` | stays | the vLLM option, `circuit/__init__`, PROTOCOL |
| `pearl-fp8-v4` | stays (cheap) | Pearl compatibility. `PearlKW` in `pearl_kw.py` 726 is the base of every Pearl-C. Cited by the 4090 benches, PROTOCOL and vLLM tests. Its benches are deletable |
| `pearl-c-h100-v0` | deletable | README, PROTOCOL, `pearl_c.cu` comments. No pin, no live claim |
| `pearl-c-h100-v1`, `-v1-h1`, `-v1-h2` | deletable after a ruling on the pins | pinned γ `pearlCGammaH100Rev1_*`, 45 pins with "h100" in the name. No table, product or open PR |
| `pearl-c-sm120-v1` | **live** | #1116, #1001, #1014, the `pc8` circuit, Lean |
| `pearl-c-nvfp4-v0` | stays | Pearl-C4: the `pc4` circuit, #1034, FP4 γ pins |

**Scheme modules not in `SCHEMES`:**
- Stay:
  - `pearl_c4_c_L` 158, imported by `pearl_c4`.
  - `pearl_c4_replay` 342, imported by `pearl_c4_arm.py`.
  - `pearl_c_debit` 172, imported by `pearl_c_work`.
  - `pearl_c_work` 532: the served draw, `verify_run.py`, `served_debit.py`, vLLM's `pouw_pearl_c_device`, #1014.
  - `pearl_c_device` 115, imported by `pearl_c` and circuits `pc8` / `rowk`.
- `pearl_c_u` 211: used by H100's `pearl_c/twin.py` and the sm120 tests; its γ `UOnly` appears only in `test_ledger`. It goes with H100 unless the sm120 tests need it (unchecked).

**Open PRs touching PoUW** (26 open): #1118 #1116 #1108 #1104 #1099 #1093 #1085 #1084 #1082 #1079 #1077 #1060 #1059 #1052 #1036 #1034 #1031 #1020 #1014 #1001 #997 #983 #967 #884 #864 (and #1088, Lean only).
- Under `benchmarks/pouw` they touch:
  - `exhaustion/`: #1001, #1082, #1116.
  - `harness/`: #1052, #1059, #1060, #1079, #1085, #1118.
  - `hidden_zk/`: #1034.
  - `pearl_c/`: #1052, #1060 (probably stale diffs; check before deleting).
  - `pearl_c_vllm/`: #1001, #1014, #1052, #1060, #1082.
- In the schemes, only `pearl_c_work` (#1014).
- None touches `kernels/`, `nvfp4_sm120/`, `pouw_hash/` or `pearl_c4/`.

**One-off scripts** (who uses each):

| Script | Lines | Used by |
|---|---|---|
| `vllm_bench.py` | 449 | `pearl_c_vllm` imports its `PROMPTS` / `find_model`; move those (about 30 lines) before deleting |
| `ncp2_gpu_bench.py` | 413 | its own test (326); it benches the vLLM NCP kernels |
| `gemm_bench.py` | 214 | `ncp2_gpu_bench` imports `timed` |
| `e2e_audit.py` | 157 | — |
| `gamma.py` | 149 | `test_gamma` |
| `route_u_bench.py` | 147 | — |
| `pearl_calibration.py` | 138 | — |
| `pearl_b200_setup.sh` | 36 | — |
| `check_route_u_sass.py` | 33 | nothing |
| `tool.py` | 68 | infrastructure; keep |
| `run_result.py` | 28 | infrastructure, used by the `pearl_c_vllm` scripts; keep |

**Estimate:**
- Deletable from `benchmarks/pouw`, about 10.1k lines:
  - The H100 lane: `pearl_c/` minus `hash*.cuh`, about 6.0k (including `bench.json` 918), plus about 1.3k of tests.
  - The NCP/4090/B200 one-offs and `kernels/`: 1.6k, plus 0.16k of tests. `kernels/pouw_gemm.cu`'s SASS is route U's
    evidence (r20260928-120439-c053), so it goes only with that run kept.
  - The `nvfp4_sm120` benches minus `nvf4_plain.cu` and `mainloop_nvf4.cuh`, which `nvf4_plain.cu` includes: 1.3k.
  - Maybe `ncp2_gpu_bench` with its test: 0.7k.
- Must stay, about 33k: `harness` 13.8k (4.6k of it JSON), `pearl_c_sm120` 3.3k, `pearl_c4` 3.3k, `pouw_hash` 2.5k, `pearl_c_vllm` 2.4k, `pearl_c/hash*.cuh` 0.9k, `nvf4_plain.cu` with `mainloop_nvf4.cuh` 0.6k (#1116's second denominator, `verity_fp8_256x128_ew`), `exhaustion` (#1116), about 6k of tests.
- `verity_pouw`: about 9.8k of 10.1k stays; the H100 code and `pearl_c_u` are 0.2–0.4k.
- **γ pins:** 197 of the 793 pins are γ.
  - 109 are named somewhere outside Lean, 104 of them by `harness/price_twins.json` (a table of priced variants).
  - A live claim cites 1 (#1116); PROTOCOL.md names 2.
  - Pruning pins changes recorded guarantees, so it needs Daniel's ruling.

## 4. Lean (`protocols/pouw/lean/Pouw`)

| Layer | Files | Lines | Declarations |
|---|---|---|---|
| Protocol | 76 | 19,727 | 1,089 defs; 14 theorems, all `rfl` instance equalities |
| Assumptions | 52 | 5,034 | 394 defs; 0 theorems (22 assumption modules in the audit) |
| Guarantees | 5 | 394 | 26 defs (Barrier, Dimension, Game, NCP; **no PearlC**) |
| SecurityProofs | 135 | 43,662 | 3,260 theorems, 483 defs |

- **Protocol by directory:** PearlC 10,677, Fp8Atom 6,208, NCP 703, TileBound 427, Barrier 309, Dimension 285, Game 258, Basic 103, Witness 90.
- **SecurityProofs by directory:** PearlC 25,673, Dimension 6,012, Fp8Atom 5,235, NCP 2,680, TileBound 1,376, Barrier 605.
- Outside the layers: `PouwBulk.lean` 65 (exempt from the audit as a conformance test), `Pouw.lean` 4, `scripts/` 1,076.

**What sits in the wrong layer:**
- **Data in the trusted layer:** 12,060 of Protocol's 19,727 lines are generated test vectors in 12 files:
  - `H1TVectors` 2,892, `Fp4Vectors` 2,063, `Sm120Vectors` 1,903, `EncVectors` 1,770, `Fp8Atom/Vectors/Add` 1,133, `PeelExactVectors` 743, `C00` 525, `Ada` 382, among others.
  - Generators: `lean/scripts/fp8atom_vectors.py`, `h1t_vectors.py`, `tests/ncp_lean.py`. These are catalog candidates; without them the spec is about 7.7k lines.
- **Statements in Protocol:** `Fp8Atom/H1TLemmas.lean`, `Pinned.lean` and `H1TPinned.lean` (about 400 lines, about 41 `def … : Prop`) are statements of lemmas whose proofs sit in SecurityProofs, so they belong in Guarantees.
- **The cited statements live in the proof layer:** all 793 pins are theorems declared in SecurityProofs with their statements inline, not `def G : Prop` in Guarantees.
  - Example: the cited γ is `SecurityProofs/PearlC/DeviceCapRev1Gamma.lean:180`.
  - PoUW is only partly on core's four-name layout. Moving the pins to Guarantees is a `--moved` exercise over 793 names.
  - Pins by namespace: `Pouw.PearlC` 402, `Dimension` 154, `TileBound` 63, `NCP` 42, `Fp8Atom` 41, `Sanity` 31, others 60.
- **One import exception:** `Pouw.Protocol.PearlC.Defs` imports Batteries and Fp8Atom pieces, the only exception to the Protocol import rule.

## 5. What a move breaks or slows

- **Paths hard-coded in run scripts:**
  - `pearl_c_vllm/window.sh` sets `PYTHONPATH=…/protocols/pouw:…/integrations/vllm:…/benchmarks/pouw`, passes `--kernel benchmarks/pouw/pearl_c_sm120`, and runs `cmp` between the ship's `run.py` and the run tree's.
  - `harness/jobs/env.sh` and `harness.yaml` / `harness-timed.yaml` (sky jobs) use `benchmarks/pouw/harness/$CMD` and `PYTHONPATH=…/protocols/pouw`.
  - Every `build.sh` (`pearl_c`, `pearl_c_sm120`, `pearl_c4`, `pouw_hash`) and `pearl_c/h1_ship.sh` / `ship.sh` take paths relative to the repo root.
  - `tool.py` has 13 path references; `price_twins.json` has 9.
  - `pearl_c_sm120.cu` includes `../pearl_c/hash_h2.cuh` and `../pouw_hash/pouw_hash.cuh`, so the kernels can't move separately.
  - `pearl_c4/build.sh` runs `git show 71086532:benchmarks/pouw/pouw_hash/pouw_hash.cuh`, reading the path as it was at that old commit, so a move doesn't break it. It does break if the commit becomes unreachable: when it is missing locally, the script fetches it from branch `cursor/pouw-hash-sm120-9569`.
- **Product coupled to a bench directory:** vLLM's `pouw_pearl_c_device` (setting `kernel`, the run tree's `benchmarks/pouw/pearl_c_sm120`) imports that directory's `run.py` / `fixture.py`. `pearl_c_vllm` imports `vllm_bench` from `benchmarks/pouw`.
- **Shipped trees and old results:** every timed claim was run from a ship tree pinned as one commit (`exhaustion/ship.sh`, `pearl_c/ship.sh`). Re-verifying with old code works if those commits stay reachable; nothing in a ship tree reads the current layout.
- **`research run --cwd source`:** jobs invoke `benchmarks/pouw/...` and `protocols/pouw/...` by path. These include the kernel ledger (store kind `kernel-attempt/v1`, whose description in `tools/research/.../kinds.py` names `benchmarks/pouw/harness/ledger.py`) and #1116's window. `tools/research/tests/test_pythonpath.py` lists `protocols/pouw`, and the root `pyproject.toml` lists it as a workspace member and in testpaths.
- **Fixtures:**
  - `fixtures/artifacts.json` has 1 PoUW entry out of 120: `integrations/vllm/tests/query/fixtures/pouw_row_binding.json.gz`.
  - PoUW's test inputs read core's `fixtures/tc/vectors/fp8-hopper-wgmma-{k1536,k32}.json` and `packages/verity/tests/ml/fixtures/golden/ada_e4m3_m16n8k32.json` (`protocols/pouw/pyproject.toml` `inputs`). Moving core's fixtures breaks PoUW's suite.
  - The SASS gate's test fixtures are `benchmarks/pouw/tests/fixtures/sass_gate/*.cu`.
- **Vectors:** `protocols/pouw/tests/vectors` is 700K, 12 files (`ncp.json`, `ncp_lean.json`, `pearl_kw.json`, `pearl_c.json`, `pearl_c_u.json`, `pearl_c4.json`, `pouw_regions.json`, `pouw_rows.json`, `identifier_v1.json`, `quicknet.json`, `pearl_c_skip_vectors{,_k8192}.txt.gz`).
  - Generators write them by relative path: `tests/*_vectors.py` → `tests/vectors/*.json`; `ncp_lean.py` → `lean/Pouw/Protocol/NCP/*.lean`; `lean/scripts/*` → `Pouw/Protocol/Fp8Atom/*.lean`.
  - `test_lean_package.py` and `test_cap_lean.py` read `lean/Pouw/...` paths.
- **Lean:** module renames re-key all 793 pins (a `--moved` file) and `tools/check/lean-deps.json` (`protocols/pouw/lean`). They also invalidate pod Lake caches, a full Mathlib rebuild per pod.
- **SASS pins:** `harness/sass_pins.json` is keyed by toolkit and subroutine signature, not by path, so it survives a move. Cubin manifests (`MANIFEST.sha256`) are relative to the ship tree.
- **What slows me:** any move that lands while #1034 (hidden_zk, which runs `benchmarks/pouw/hidden_zk` on node 1 with paths in its launch scripts), #1104 or #1099 are open forces a rebase of their path-bearing scripts and re-runs of path-keyed `check` suites. No result would be lost: the art ids and ship commits stand.
