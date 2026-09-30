---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T08:46Z
---

# Re your 08:21Z decisions: cc 12.0 per-tensor FP8 has its own correctly ordered Definition (#516, core step #515); #502 relabelled; the GEMV is already #501

- **The red team's `fp8-per-tensor-scale-order` finding is fixed.**
  - **#516** (`cursor/vllm-sm120-fp8-scaled-mm-422d` @ `fbfc7c9d`; draft, stacked on #501, with #515 merged in) adds:
    - `fp8.ScaledMmFp8NoSwapCoordinate_v1{K,BIAS,DOT}` = `F2fpBf16(F32Mul(s_x, F32Mul(s_w, acc)))`; with a bias, `F32Fma(s_x, ·, f32(b))`;
    - `ScaledMmFp8NoSwap_v1{K,N,BIAS,DOT}`, over `DotE4m3_v2{K,DOT}`;
    - `GemmTarget.fp8_dot` / `fp8_scale_order` (blackwell_consumer: the cc 12.0 step, `no_swap`);
    - `targets.scaled_mm_fp8_spec`, which refuses by name elsewhere.
  - `ScaledMmFp8Coordinate_v1` isn't reused.
  - **The CPU test is `tests/program/test_scaled_mm_fp8_no_swap.py::test_the_red_teams_counterexamples_take_the_unswapped_word`.** The Definition takes the cc 12.0 word on every counterexample, and `ScaledMmFp8Coordinate_v1` takes the swapped one.
  - **The red team's record holds 4 counterexamples, not 5:** `fp8_order_repro.json` in `r20260930-081238-476e`, whose result says 4/4. All 4 are in the test.
  - **Results:** run `r20260930-084203-92b9`, check slot b, CUDA hidden. The new tests, `test_fp8`, the GEMM, bias and gemv tests and all lints pass. circuit-check is 3/3 with 0 failures.
  - **The bias form isn't measured yet.** It is `ScaledEpilogueBias`'s FMA from the source. The 5b run measured only the no-bias form (15,728,640/15,728,640), and the conformance says so.
- **Core step #515** (`cursor/sm120-fp8-step-prim-422d` @ `72b64c2b`; draft, stacked on #487): `verity.ml.prims.BlackwellE4m3QmmaDot32_v1`.
  - It is `tc_dot_total_e4m3` on the pinned sm_120 e4m3 model, with its kernel, its self-check, a circuit-check root and pin (9,793 AND), and flock's lowering.
  - **It touches `backends/flock/`,** so its `check` needs `lean-agreement` (`check.py --record --on POD`). #516 inherits that.
  - It stays off `verity.ml.library` (that would need a VERSION bump).
  - Run `r20260930-083533-aa80`: circuit-check 0 failures; the only test failures are the fixture-less replays base fails too.
- **#502:** the census line now reads "datasheet peak, dense, FP32 accumulate; not measured on our cards" (`b4a65e20`). No measured cuBLASLt FP8 rate is published: the PoUW RTX PRO line was withdrawn and its pod never existed.
- **"Then the GEMV":** `GemvBiasF32_v1` is **#501**, done at 07:2xZ.
  - Its T table was recovered by Kueue `port-capture` job 13 (`r20260930-063002-c5fe`).
  - Acceptance: exact on all 14 table entries (`r20260930-063644-caa1`).
  - Full quick suite clean (`r20260930-075224-1fc7`).
  - Nothing is left to run for it. Tell me if you meant something else.
- **#483:** noted. After TVF lands I'll merge main into it, resolve `targets.py` as a union with #486 and #481, rerun its tests and send the new head.
- **Nothing of mine is running.**
