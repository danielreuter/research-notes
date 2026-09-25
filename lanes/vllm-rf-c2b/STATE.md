---
id: vllm-rf-c2/state
lane: vllm-rf-c2
kind: state
agent: bc-568d82f4 (Cursor), coordinator bc-ba6cec03
updated: 2026-09-25T12:27Z
---
# c2 (Definition library, D8/D9, decision 3a): state

> **Research coordinator, 14:09Z, for the root (disk safety; the vLLM coordinator bc-ba6cec03 is disconnected):** the laptop has no room for run outputs. STOP every `research fetch` (and `fetch --all`) to the laptop. Launch runs with `research run --on <pod> --project verity --custody-r2 ...`, and inspect on the pod (`research pods ssh`) or from R2 (`research data preserved <run>`, `research data fetch <art> --path <one small file>`). Same rule as the 12:26Z URGENT banner below. Nothing else about this lane's work, pods or merges changes.

> **SUPERSEDED at 14:12Z by lane c2b** (vLLM coordinator bc-ba6cec03). This agent hung at about 12:30Z when the host disconnected. Successor: branch `lane/vllm-rf-c2b`, worktree `rf-c2b`, notes `../vllm-rf-c2b/`; it takes over your pods. If you are the old c2 agent and wake up: stop. Don't commit, push or run anything, and end your turn.

> **COORDINATOR, 12:26Z, URGENT (laptop disk at 1.5 GiB):** STOP `research fetch --all` and every other laptop-side fetch or copy of run outputs, now. Launch new runs with `research run --on ... --custody-r2`: the pod publishes the attempt and every run file to R2 itself, and the pod guard accepts that. Inspect results on the pod (ssh) or read them from R2; plain `research fetch {run}` is for status only. Keep XML and evidence in your notes under about 5 MB. Remove local copies you already fetched only once R2 has them.

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

- Step 3 equality full pass `r20260925-103740-ee23` (`evidence/step3/equality3.json`): ALL-EQUAL (2743.9 s).
  `vyv-rf-c2-cpu` terminated (~$3.33).
- Closure run `r20260925-111909-09b4` (`evidence/programs-5e21eead/`): all 12 programs-bearing rows, 16,141 distinct
  top-level spec closures identical at base and head, 0 errors. AmpereBF16TcDot16_v1 in the closures of rows 11, 23, 39,
  57, 60, 67, 68, 70, 75, 101; #73/#74 (Hopper) none. #4 is L40S by key, no stored Program -> 11 L40S rows = 10 + #4.
- GPU #101 `r20260925-105133-d03f` (`evidence/row101/`): head == base == record (run root 7adcef49…, program ccc21347…,
  manifest 90f81868…, commit_pass).

## Epoch commit `11c3e500` (pushed 12:24Z, alone at the tip; merge up to `5e21eead`)
- Epoch tests: full suite at the epoch tree `r20260925-113631-7de1` (lints 45/45; vs pre-epoch head: 15 new failures, all
  epoch pins); after the pin fixes, re-run of those files `r20260925-121653-3c15`: every outcome == pre-epoch head except
  `test_golden::test_corpus_check_passes` (protected corpus: digest changed, attribution unchanged, m1 d2b299f5 -> d72cd7ad,
  m6 14a3ac66 -> 074e6cab; integrator re-record needed). `evidence/epoch/`.
- Pins at the epoch (`r20260925-120042-34a3`): registry_version e183ae76 -> c41e555d; PROFILE_B1_EAGER_V2 2145f8ec -> 4821740e;
  rest unchanged.
- `vyv-rf-c2-g1` terminated 12:02Z (runs fetched). Remaining: gate (a) on reg, then READY.md (draft written), terminate reg.

## Epoch (step 4, details)
- Programs cite core `AmpereBF16TcDot16_v2`; integration `_v1` stays registered, `conformance="superseded by …"`.
  Call sites (targets, derived_rows, sampled_replay, examples, torch_frontend docstrings, vocab notes, tests) name `_v2`.
- Epoch closure `r20260925-113628-aac6` (`evidence/epoch/`): exactly rows 11, 23, 39, 57, 60, 67, 68, 70, 75, 101 change
  row_sha; every v1 spec now v2 (same count); #73/#74 unchanged; 0 errors.
- GPU #101 at the epoch tree `r20260925-114645-150d`: commit_pass, run root unchanged 7adcef49…, program ccc21347 ->
  dd206e6c, manifest 90f81868 -> ee65240e, descriptors cite only AmpereBF16TcDot16_v2.

## Running
- Gate (a) T0+T1 `r20260925-105303-d711` on reg (from 10:53Z; 60/158 at 12:20Z, 0 F).
- Spend ~$8.8 at 12:27Z (cpu $3.33, g1 $1.42, reg $1.76/h from 10:28Z).

## Next
1. Fetch gate (a), compare with a23b's base xml test by test; finish READY.md; terminate reg; final message.

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
