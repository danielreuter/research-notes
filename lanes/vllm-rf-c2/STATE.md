---
id: vllm-rf-c2/state
lane: vllm-rf-c2
kind: state
agent: bc-568d82f4 (Cursor), coordinator bc-ba6cec03
updated: 2026-09-25T11:21Z
---
# c2 (Definition library, D8/D9, decision 3a): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T15:30Z (8:30 AM PT; updated 11:31Z)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

a4 base: 10996616

- Worktree `~/projects/verity-wt/rf-c2`, branch `lane/vllm-rf-c2` from `10996616`.
- Budget: $25 of pod spend. Spent so far: `vyv-rf-c2-cpu` from 08:51Z at $1.28/h.

## Commits (pushed)
- `f6bf88c7` registry cites core for Bf16ToF32/F32ToBf16Rn/F2fpBf16/HopperBF16WgmmaDot16, Const family, DotBf16/
  GemmCoordinate/Gemm _v2; one-process test; allowlists P1 -4, P8 -3, P11 -1, P10 b1 cap 1285 -> 1246.
- `e0fc636f` P1 lint reads `@composite` ids too (allowlist unchanged).

## Evidence so far
- Step 1 at base (run `r20260925-091543-a01c`, `evidence/step1/equality.json`): ALL-EQUAL. Bf16ToF32 2^16,
  F32ToBf16Rn and F2fpBf16 all 2^32 words (core vs integration scalar + core numpy kernel), Hopper k16 step 7,418,816
  cases (special grid, dense specials, core sample_tc 5 M, uniform words 1 M, narrow exponent 1 M): 0 differences
  core vs integration scalar / core kernel / integration twin. 32 Gemm_v2-family program digests and 23 Const encodings
  equal. `test_derived_rows.py` + `packages/verity/tests/ml` green (separate processes).
- Quick head `e0fc636f` (run `r20260925-092504-63c3`): lints green; registry test files green incl. the new one-process test.

## Commits (step 3, pushed)
- `d838f4c4` verity.ml.scalar: 18 basic int/bit/select/compare prims; registry cites them.
- `5e21eead` verity.ml.prims: F32ToE4m3Sat_v1 + HopperE4m3QgmmaDot32_v1 (+ numpy kernel); registry cites them; P8 -2, P11 -1.
- Tests at `5e21eead` (`r20260925-102525-d29e`, `evidence/step3-tests-5e21eead/`): lints 45/45; core ml 132/132; 32 registry
  test files 678 tests, 3 fail, all 3 also fail at base (test_gen_sampling NameError, test_twins openmp, test_sampling_rows NaN
  sign on x86); equality harness crashed on a harness bug (Vocabulary.version is a property), fixed.

## Step 3 (details)
- Moved into core, same id/signature/conformance: `verity.ml.prims` F32ToE4m3Sat_v1, HopperE4m3QgmmaDot32_v1
  (cast `f32_to_e4m3_sat_word` verbatim); new `verity.ml.scalar`: F32Fabs, F32Neg, F32Fmaxf, F32Fminf, F32Sat,
  F32BitsShl23, F32IsFinite, F32Eq, Bf16GtStrict, I32Le/Eq/Add, BitAnd/Not/Or, SelectF32/Bf16/I32. Compares and
  F32Sat rewritten host-FP-free (integer order) -> equality test must cover them exhaustively / densely.
- Flagged, not moved: F32Add/Mul/Div + FTZ family (host NaN word, MXCSR), F32Fma* (NaN 0x7FC00000 vs PTX canonical),
  MUFU (b1's kernels + package tables), ref vocabulary (pinned unit), F32Max (kernel), app-specific, DotBf16_v1 family,
  DotE4m3{K}, collectives, AmpereBF16TcDot16 (v1 vs core v2: epoch).
- `ref_vocab_digest` changes at steps 2 and 3 (code-identity pin; record before/after).

## Gates at the pre-epoch head `5e21eead` (so far)
- Gate (b) `r20260925-104202-1d10` (vyv-rf-c2-reg, head and base concurrently): base 51 F / 3647 P / 286 S / 11 E; head 51 F /
  3648 P / 287 S / 11 E. jdiff: 0 new failures, 0 new skips / skip reasons, 0 renamed; +2 new tests (the one-process test, both
  orders); 1 outcome change = a1's known order-dependent allocator test. `evidence/gate_b-5e21eead/`.
- Stored Programs, #101 (the only row whose store tree carries its descriptors): 3 descriptors, stored digest == artifact.json,
  decode + re-encode through base and head reproduce it; all 727 registered composites re-specialize through either library to
  the stored v1 encoding (`r20260925-111122-91e4`). Other rows' store trees have instances only (spec ids): closure run
  `r20260925-111909-09b4` re-specializes every top-level spec id through base and head and scans for AmpereBF16TcDot16_v1.

## Running
- `vyv-rf-c2-cpu` (RunPod `v34wij1rkanus8`, cpu3g 32 vCPU / 128 GB, EPYC 7702P, guard 90, from 08:51Z, $1.28/h):
  `r20260925-103740-ee23` step-3 equality at `5e21eead`. Quick pass ALL-EQUAL (encodings, evaluators, dot); full pass
  submitted 10:38Z, running.
- `vyv-rf-c2-reg` (RunPod `ht2p5tooi75gev`, cpu3m 32 vCPU / 256 GB cgroup, EPYC 7713P, 200 GB, $1.76/h, from 10:32Z; no 64 vCPU
  cpu3m/cpu5m in any DC, gate (a) pod is 256 GB not 512 GB): prefetch of every fixture row's artifacts into the pod-local
  store done (26 artifacts, 0 failures; read-only key deleted 10:46:22Z). Gate (b) head vs base `r20260925-104202-1d10`
  (~97% at 10:56Z); gate (a) T0+T1 `r20260925-105303-d711` (started 10:53Z, ~2 h).
- `vyv-rf-c2-g1` (RunPod `xqv97uozks8cw1`, L40S, $1.09/h, from ~10:45Z): #101 Build head then base `r20260925-105133-d03f`
  (bootstrap done 10:53Z).
- Next on `vyv-rf-c2-reg`: #73/#74 stored-Program re-encode (head + base) and the AmpereBF16TcDot16_v1 scan of the
  L40S rows' stored Programs (for the epoch list).

## Next
1. Step 3 equality run (`tools/equality3.py`) + lints + core ml tests + registry tests on `vyv-rf-c2-cpu`.
2. Gates at the pre-epoch head: lints, gate (b) head vs base, gate (a) T0+T1 (cpu3m 512 GB), GPU Build #101 (L40S),
   Hopper: CPU re-encode of #73/#74 stored Programs.
3. Epoch commit (AmpereBF16TcDot16 v1 -> v2) at the tip, separate.

## Open questions
(none)

## Found, not fixed
- Two collisions beyond the allowlisted four block a one-process import of `verity.ml` + the integration registry:
  `Const<w>[0x..]_v1` (b1.py's own `const()` vs core's; core makes `ZERO32` at import) and `DotBf16_v2`,
  `GemmCoordinate_v2`, `Gemm_v2` (b1.py vs `verity.ml.gemm`). P1's lint only scans `primitive`/`PrimitiveDefinition`/
  `CompositeDefinition` calls, not the `@composite` decorator, so the second set is not in its allowlist. Fixed in
  `f6bf88c7` / `e0fc636f`.
- `F32Add_v1`, `F32Mul_v1`, `F32Div_v1` and `F32AddFtz/SubFtz/MulFtz_v1` evaluate through host numpy float32
  arithmetic, so the NaN word they return is the host's: `inf + -inf` is `0x7fc00000` on arm64 (laptop numpy 2.5.3);
  x86 expected `0xffc00000` (to confirm on the pod). They also inherit the process's MXCSR FTZ/DAZ state. Basic
  Definitions that belong in core, but moving them as they are would put a host-dependent function in core; not moved.
