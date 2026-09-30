---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T09:35Z
---

# Root's 08:47Z tasks: #516's bias form is measured; NVFP4 Definition exact on the PRO 6000 (#524, core #523); one open item, the step's totality

- **#516's bias form, measured.**
  - Kueue `port-capture` job 110 (template `infra/nebius` b4541ee1 ≥ 73998c0e), run `r20260930-090150-a42a`: `bf16(fma(s_x, s_w·acc, b))` is exact on 786,432 of 786,432 coordinates.
  - The alternatives miss 8, 9 and 13 of the 17 discriminating coordinates.
  - The Definition itself through the IR reference: 576 of 576.
  - #516 is now at `58c44852`, green (run `r20260930-090540-b627`), and its body is updated.
- **NVFP4 on cc 12.0, #524** (draft, on #516, with core #523 merged in):
  - The Definitions are `Nvfp4QuantBlock_v1` / `Nvfp4ActQuant_v1{K}` (`cvt_fp16_to_fp4`) and `DotNvfp4` / `ScaledMmNvfp4Coordinate` / `ScaledMmNvfp4_v1{K,N,DOT}` (`bf16(alpha·acc)`), with `QuantLinearNvfp4_v1` as the whole linear.
  - The Commit's layouts are `sf_offset` and `unpack_codes`.
  - The binding is `GemmTarget.fp4_dot` with `nvfp4_quant_spec` / `nvfp4_gemm_spec`, on blackwell_consumer only. It cites `art:3bc1b2c4`.
  - **Acceptance:** capture job 111 (`r20260930-091510-b35b`), CPU check `r20260930-091735-c29b`. **Quantizer: 131,072 of 131,072 blocks exact**, NaN, inf, zero, −0, tiny, huge and rounding ties included. **GEMM: 295,936 of 295,936 coordinates exact**; the Definition itself 640 of 640.
  - **The pin's PRO 6000 evidence** is pouw's `r20260930-064142-07f5` and `-064149-a24f` (16.9M words each on two GPUs, 0 mismatches), so no second sweep was needed. The run ids are copied to `lanes/pous/`.
- **Core #523** (on #515) adds `BlackwellNvf4OmmaDot64_v1`, `F32ToE2m1Sat_v1` and `E4m3ToF32_v1`.
  - The capture fixed the E2M1 NaN rule: code 7, sign dropped.
- **The open item: circuit-check needs the step total.**
  - It fails `ScaledMmNvfp4_v1`, `QuantLinearNvfp4_v1` and the step with "reference-not-total": the model raises on scale bytes outside UE4M3 and on non-finite accumulators.
  - **The accumulator rule is measured,** including on the PRO 6000 via pouw's specials tiles: NaN gives `0x7FFFFFFF`, inf returns itself.
  - **Invalid scale bytes** (bit 7, `0x7F`; `0x7F` is reachable from an all-NaN activation block) were never probed. Kueue job 119 measures them now, with a single-instruction library built on the host (`r20260930-092019-5d78`). I'll encode what it finds and rerun circuit-check.
- **Other:** every direct run of mine is in a check slot with CUDA hidden. No pods.
