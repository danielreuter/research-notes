---
id: vllm-rf-c2b/ready
lane: vllm-rf-c2b
kind: ready
agent: bc-b15365e1 (Cursor), coordinator bc-ba6cec03; drafted by c2 (bc-568d82f4) at 12:30Z
created: 2026-09-25T14:25Z
---
# c2b (Definition library, SYNTHESIS D8/D9, §6 C2, decision 3a): READY

c2b succeeds c2 (hung at the 12:30Z host disconnect) from its pushed head `11c3e500`. c2b's work: gate (a) finished and
compared, its run preserved on R2, the reg pod terminated, the rebase onto main. Evidence paths `evidence/...` below are
c2's (`~/.research/notes/lanes/vllm-rf-c2/evidence/`) except `evidence/gate_a-5e21eead/`, which is c2b's.

## Branch, head, base, what to merge
- Branch **`lane/vllm-rf-c2b`** (pushed). **Base: main `33e4d8d1`** (the a4 merge), rebased from a4 `10996616` with
  `git rebase --onto origin/main 10996616`. c2's commits map to: `f6bf88c7` -> `56a32533`, `e0fc636f` -> `dfd3e8ec`,
  `d838f4c4` -> `d5219087`, `5e21eead` -> `4d053f01`, `11c3e500` -> `dedf5313`.
- The rebase changes nothing that was tested: `integrations/vllm` and `packages` are byte-identical to `5e21eead` and
  `11c3e500`, and the lane diff has the same `git patch-id --stable` (full `8699d19d…`, pre-epoch `6d2cced7…`). Main's
  other changes since `10996616` are outside both trees, so the gates below were not re-run at the rebased ids.
- Head `dedf5313` = the **re-baseline epoch commit** (decision 4), alone at the tip.
- **Merge up to `4d053f01` (the commit before the epoch; c2's `5e21eead`).** Those four commits move no Program digest,
  manifest digest, commitment root, leaf id or regression verdict (evidence below). Nothing in them depends on the epoch commit.
- Take `dedf5313` only with the re-baseline epoch. It moves the digests of every Program that binds the Ampere k16 step
  (list below). It also leaves one protected test red until the integrator re-records the golden corpus (see "Epoch").

## What changed
| commit (c2 id; c2b id in the mapping above) | change |
|---|---|
| `f6bf88c7` | Registry cites core `verity.ml` for the Definitions it duplicated: `Bf16ToF32_v1`, `F32ToBf16Rn_v1`, `F2fpBf16_v1`, `HopperBF16WgmmaDot16_v1`, the `Const<w>[0x..]_v1` family (`const`/`ZERO32`), `DotBf16_v2`/`GemmCoordinate_v2`/`Gemm_v2`. New one-process test (`tests/program/test_registry_one_process.py`, both import orders). Allowlists: P1 -4, P8 -3, P11 -1; b1.py P10 cap 1285 -> 1246. |
| `e0fc636f` | P1 definition-id lint also reads `@composite(...)` ids (the GEMM `_v2` collision was invisible to it). Allowlist unchanged. |
| `d838f4c4` | New `verity.ml.scalar`: 18 basic primitives move to core under the same ids, signatures and conformance: F32Fabs, F32Neg, F32Fmaxf, F32Fminf, F32Sat, F32BitsShl23, F32IsFinite, F32Eq, Bf16GtStrict, I32Le/Eq/Add, BitAnd/Not/Or, SelectF32/Bf16/I32. Comparisons, max/min and sat are rewritten as integer order on the encoding (no host FP state). The integration re-exports them under the old names. |
| `5e21eead` | `verity.ml.prims`: `F32ToE4m3Sat_v1` (word function moved verbatim to `verity.ml.tc.cast.f32_to_e4m3_sat_word`) and `HopperE4m3QgmmaDot32_v1` (+ numpy kernel) move to core; the registry cites them. Allowlists: P8 -2, P11 -1. |
| `11c3e500` | **Epoch.** Programs cite core `AmpereBF16TcDot16_v2`; the integration's `AmpereBF16TcDot16_v1` stays registered with `conformance="superseded by AmpereBF16TcDot16_v2 …"` (the `RMSNormFusedCuda_v1` precedent) so that recorded Programs decode, and its pre-R17 evidence is marked superseded on non-finite outcomes. Call sites and pinned test digests updated. |

Primitive encodings are id + params + ret, so moving a Definition under the same id is digest-neutral; every move was
checked for equal evaluators before it landed (below).

Outside c2's files (minimal hunks, no reformatting): the lint allowlists (entries deleted only) and P1's lint;
`check/replay/sampled_replay.py` (b1's: 4 lines, epoch only, `_v2` names; line count unchanged at its P10 cap);
`tests/query/test_query_fixtures.py` (2 callee strings, epoch only); `program/frontend/{examples,torch_frontend,rules/vocab}.py`
(epoch only: `ops["AmpereBF16TcDot16_v2"]` and docstrings/notes); the registry and conformance tests.

## Inventory: what stays in the integration, and why
Application-specific, stays (no flag): the model composites (Serve*, Attention*, AttnBlock*, RMSNorm*, RoPE*, SiluMul,
Embedding, TokenSelect, BiasAdd, ResidualAdd, MoE*, Lifted/L* padding and liveness primitives, SplitsForSMS, LiveCount,
sampling (GumbelStreamKey, GumbelNoiseLane, TopPMaskWord)), and the vLLM/aten kernel semantics SiluMulBf16, RopeOut,
RopeOutAdd, GeluTanhMulBf16, GeluErfBf16 (quarantine).

Flagged: borderline, or silicon semantics left in the integration (one line each):
- `F32Add/F32Mul/F32Div_v1`, `F32AddFtz/SubFtz/MulFtz_v1`: silicon (FADD/FMUL/div.rn), but evaluated through host numpy
  float32, so the NaN word and MXCSR FTZ/DAZ are the host's (x86 `inf + -inf` = `0xffc00000`, arm64 `0x7fc00000`).
  Moving them would put a host-dependent function in core; they need an integer-exact rewrite first (as d838f4c4 did for the compares).
- `F32Fma/F32FmaFtz/F32FmaSubFtz_v1`, `F32FmaRm_v1` (moe.py): host-independent (exact rational), but NaN -> `0x7FC00000`
  is a documented, not measured, choice (PTX's canonical NaN is `0x7FFFFFFF`). Moving them would fix an unmeasured NaN rule in core.
- `F32Max_v1`, `GuardNegInfZero_v1`: FA2 `MaxOp` / `Check_inf` with the fast-math ftz: kernel semantics, not the IEEE
  op (core's `F32Fmaxf` is the libm `fmaxf`); stays with the FA2 model.
- `Bf16Add/Bf16AddF2fp/Bf16MulF32/Bf16MulBf16_v1`: aten / vLLM `_f16Vec` element-wise semantics (compute in f32, one
  rounding, framework NaN word), built on the host-numpy F32 add/mul above; stays until those are host-free.
- MUFU family (`MufuEx2Ftz`, `MufuRcpFtz`, `MufuSqrtFtz`, `MufuTanh`, `RsqrtApprox`, `DivFullRcp`, `DivFullScaleA`,
  `Fa2InvSum`, `Fa3InvSum`): silicon (SFU), but evaluated through b1's `program/kernels` models and the integration's sm_89
  measured tables (package data). Moving them needs b1's kernels and the tables in core first.
- `REFERENCE_CPU_F32` members (`ref_prims.py`: F32Sub, F32Sqrt, F32MaxRef, F32GtStrict, F32ExpRn, F32ErfRn, F32TanhRn,
  GatherF32x{V}, I64ToI32, DotRef{K}): the torch-CPU reference model's arithmetic, a pinned vocabulary unit
  (`ref_vocab_digest`), not a silicon op. Stays with the vocabulary.
- `TanhF32Rn_v1` (dense.py): a quarantined stand-in for libdevice `tanhf` (float64 tanh, one RN32), not a measured
  function. Stays in quarantine until measured.
- `GatherBf16x{V}`, `BitAtx{W}`: basic (an element/bit select), but built per width at run time (prims.py / sampling.py).
  Moving them needs a core factory like `const()`; candidate, not moved.
- `DotBf16_v1/GemmCoordinate_v1/Gemm_v1` (b1.py, K-only, the step named in the body): after the epoch each is the
  same function as core's `_v2{K, DOT=AmpereBF16TcDot16_v2}` but a different id. Replacing them would move every B1
  digest a second time, and core deliberately did not carry the `_v1` forms. Kept; candidate for a later epoch.
- `DotE4m3_v1{K}` (fp8.py): the same pattern as `DotBf16_v2` over core's `HopperE4m3QgmmaDot32_v1`, but it carries
  the CUTLASS FastAccum / `scale-d = 0` conventions of the vLLM scaled-mm kernel. Borderline; kept with fp8.py's scaled-mm composites.
- Collectives (b1_tp2.py): NCCL / tensor-parallel semantics, application-specific.
- **Same id, different body in core:** only `AmpereBF16TcDot16` (integration `_v1` vs core `_v2`). Not guessed: resolved by
  the epoch commit (below). No other integration id collides with a core id (the one-process test loads both).
- `_BoundPrims._over` (hopper.py) is keyed by the bare name `AmpereBF16TcDot16`, so it maps v1 and v2 alike to
  `HopperBF16WgmmaDot16_v1`: the Hopper rows cite no Ampere step at either side of the epoch.

## Gate evidence
Pods: `vyv-rf-c2-cpu` (cpu3g 32 vCPU / 128 GB), `vyv-rf-c2-reg` (cpu3m 32 vCPU / 256 GB cgroup, EPYC 7713P),
`vyv-rf-c2-g1` (L40S). Evidence under `~/.research/notes/lanes/vllm-rf-c2/evidence/`.

Pre-epoch head `5e21eead` (c2b `4d053f01`) vs base `10996616`:
- **Lints** (`python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q`):
  45/45 (`r20260925-102525-d29e`, `evidence/step3-tests-5e21eead/lints.xml`).
- **Gate (b)** (`OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile`, head and base
  concurrently on `vyv-rf-c2-reg`, `r20260925-104202-1d10`, `evidence/gate_b-5e21eead/gate_b-{base,head}.xml.gz`, `jdiff.txt`):
  base 51 F / 3647 P / 286 S / 11 E / 6 xF; head 51 F / 3648 P / 287 S / 11 E / 6 xF. baseline-jdiff: 0 new failures, 0 new
  skips or skip reasons, 0 renamed or deleted; +2 new tests (the one-process test, both orders); 1 outcome change, the
  listed-unstable weakref allocator test.
- **Gate (a)** (`VERITY_REGRESSION=1 VERITY_REGRESSION_TIERS=T0,T1 python -m pytest integrations/vllm/tests/regression -m regression`,
  `r20260925-105303-d711` at `5e21eead` on `vyv-rf-c2-reg`, local store prefetched, read-only key deleted 10:46:22Z;
  10:53:05Z-14:06:48Z, 11,618 s, rc 0): **73 passed, 85 skipped, 33 deselected**. Compared on the pod with `baseline-jdiff.py`
  (`evidence/gate_a-5e21eead/`: `gate_a-t0t1-5e21eead-c2reg.xml.gz`, `jdiff-a4.txt`, `jdiff-a23b.txt`):
  - vs a4's head `10996616` (`vllm-rf-a4/evidence/gate_a/gate_a-t0t1-head-10996616-reg.xml.gz`): identical. 158 tests,
    0 outcome changes, 0 ids on one side only, 0 new skip reasons.
  - vs a23b's base (`gate_a-t0t1-base-72884c8a-samepod.xml.gz`): 158/158 same outcome, 0 failures either side. The only flags
    are the two skip rewordings a4 reported (`manifest_digest` on TP rows #70/#75, "merged by tp_stage.sh", from main's `5cc0506e`).
  - **The pod was 256 GB, not 512 GB**: no 64 vCPU / 512 GB cpu3m or cpu5m was available in any DC. The shared cgroup
    peaked at 156.6 GB (`memory.current` sampled max; `memory.peak` 156.64 GB), so 256 GB was enough.
  - Custody: the run predates `--custody-r2`. From the pod, with a minted 1 h delete-free key (deleted 14:14Z): the attempt
    (events + resources telemetry) and a separate `run-record/v1` of all 16 run files (gate_a.xml, gate_a.log, stdout, job,
    status, ...) `art:6b5ef88ed51fc0eae5adb659e422b80e10d3c1f0916fe36c7f7171c6a0722622`, both PRESERVED on s3://verity-dev
    (sha256 readback; checked again from the laptop). The attempt itself does not name that run record (attempts are immutable).
- **Evaluator equality** (before each move, both sides imported in separate processes):
  - Step 1, `r20260925-091543-a01c` (`evidence/step1/equality.json`): Bf16ToF32 over 2^16 words, F32ToBf16Rn and
    F2fpBf16 over 2^32 (integration scalar vs core scalar vs core numpy kernel). Hopper k16 step on 7,418,816 cases
    (special grid, dense specials, core `sample_tc` 5 M, uniform words 1 M, narrow exponent 1 M). 0 differences. 32
    Gemm_v2-family Program digests and 23 Const encodings equal.
  - Step 3, `r20260925-103740-ee23` (`evidence/step3/equality3.json`, 2743.9 s): ALL-EQUAL. F32Sat, F32Fabs, F32Neg,
    F32BitsShl23, F32IsFinite and Bf16GtStrict exhaustive (2^32 cases each). F32ToE4m3Sat 8.3 M cases. Fmaxf, Fminf,
    Eq, I32Le/Eq/Add 100.7 M each; the selects 4.2 M; the bit ops exhaustive. HopperE4m3QgmmaDot32 1.82 M cases vs
    integration scalar, core kernel and the twin. Encodings of all 20 moved primitives equal, 36 Program digests equal,
    and the E4M3 word function body is byte-equal.
- **Program digests on a CPU pod** (§6 C2):
  - #101 stored Program, the only store tree that carries its descriptors (`r20260925-111122-91e4`,
    `evidence/programs-5e21eead/descriptors/`): stored digest == artifact.json; decode + re-encode through base and
    head reproduce it; all 727 registered composites re-specialize to the stored v1 encoding.
  - All 12 programs-bearing rows (`r20260925-111909-09b4`, `evidence/programs-5e21eead/closure-{base,head}.json.gz`):
    each stored top-level spec id is re-specialized through base and head and its definition closure hashed. 16,141
    distinct closures, identical at base and head, 0 errors. This covers the Hopper rows #73/#74.
- **Spot row on a GPU pod**: #101 (llama32-1b bf16 L40S) Build/match/commit at head and at base, `r20260925-105133-d03f`
  (`evidence/row101/`): head == base == regression record. Run root `7adcef49…`, program `ccc21347…`, manifest
  `90f81868…`, commit_pass.
- **Core tests**: `packages/verity/tests/ml` 132/132 at `5e21eead`. The 32 registry test files: 678 tests, 3 failing,
  and all 3 fail at base too (`evidence/step3-tests-5e21eead/`).

## Epoch commit `11c3e500` (c2b `dedf5313`)
- **Rows whose Program digest changes: the 11 L40S rows.** The scan of the stored Programs' closures
  (`r20260925-111909-09b4`) finds `AmpereBF16TcDot16_v1` in rows **11, 23, 39, 57, 60, 67, 68, 70, 75, 101**. #4 is
  L40S by its row key but has no stored Program. The Hopper rows #73/#74 cite no Ampere step and do not change.
- Epoch closure (`r20260925-113628-aac6`, `evidence/epoch/closure-epoch.json.gz`): the same stored spec ids
  re-specialized at the epoch tree. Exactly those 10 rows change their closure hash; every spec that cited v1 now cites
  v2, with the same counts (e.g. row 11: 4612/4619 specs); #73/#74 unchanged; 0 errors.
- #101 on the L40S at the epoch tree (`r20260925-114645-150d`, `evidence/epoch/r101_epoch_summary.json`): commit_pass
  and **run root unchanged** (`7adcef49…`: the committed values are the same). Program `ccc21347…` -> `dd206e6c15be3f77163cc1452bfbca1fdc7545bff095703cd6c8a00f69d0f96a`,
  manifest `90f81868…` -> `ee65240e662ee5206effcf22d8b24a30120ac372f0cf58e75621d3b8476dc625`, and the build descriptors cite
  only `AmpereBF16TcDot16_v2`. The other nine rows' new digests come from re-recording them at the epoch (GPU); not run here.
- Pinned digests updated in tests (old -> new):
  - `Serve_v1{C=B0,LP=32,STEPS=7}` v1 codec: `2d483c89…` -> `e7be3165…` (test_nan_conversion);
  - `Serve_v1{C=B0,LP=32,STEPS=15}`: `d4f4b1f1…` -> `dc895366…` (test_derive; its docstring names the certificate of
    record's digest). The INT-PAD-2 B0 certificate is under v1 and needs re-issuing at the epoch;
  - `Gemm_v1{K=32,N=4}` v0 codec: `708fd264…` -> `082b51d0…` (test_codec). `docs/data/frontend` acceptance still shows `708fd264…`;
  - MoE Stage 2 block: `43bb1ede072b2031` added to the accepted pins (test_moe_pad_route_a3);
  - the query fixtures' PV k-step callee `BF16TcDot16_v1` -> `_v2` (test_query_fixtures).
- **Protected, not edited**: `verity_vllm/properties/golden/corpus.json` (gate G6: "integrator only … never a silent
  edit"). `tests/properties/test_golden.py::test_corpus_check_passes` fails at the epoch. Both entries report "digest
  changed", with attribution_sha and instance counts unchanged (`evidence/epoch/golden-epoch.json`). `smollm2-135m-m1`
  moves `d2b299f5…` -> `d72cd7ad71fbf73854c8fc9af5d8fa51fa71ec4a65bcad396fbcc5834fb0e8e1` and `qwen2.5-1.5b-m6` moves
  `14a3ac66…` -> `074e6caba4f1e1884fa336c1bf8798f845b3f6e06224462d7aa313f5488dd89c`. Integrator:
  `python -m verity_vllm.properties.golden --record smollm2-135m-m1 --log data/logs/m1.jsonl.gz --profile vllm_d9105ea80_sm89_eager --decision <epoch>`
  (and `qwen2.5-1.5b-m6`, `data/logs/m6/log.jsonl.gz`, `vllm_d9105ea80_sm89_eager_qwen15`).
- Epoch tests at the epoch tree (`r20260925-113631-7de1` full suite; `r20260925-121653-3c15` re-run of the changed
  files; `evidence/epoch/`). Lints 45/45. The full run, against the pre-epoch head's gate (b) xml (baseline-jdiff), had
  15 new failures, all epoch-moved pins: the four digests above, the 10 query-fixture PV tests, and golden. After the
  pin updates, the re-run of those six files matches the pre-epoch head on every test except `test_golden` (above).
  The one other failure in the re-run (`test_derive::test_s3_untied_lm_head_loses_sharing_and_is_refused_by_family`)
  also fails at the pre-epoch head and at base. The committed tree is the one tested (last edit 12:10Z, sync 12:15Z).
- Left as they are: the data/evidence JSON under `integrations/vllm/data/` and `docs/data/` (records under v1);
  `conformance.NAN_CANONICALISATION.program_digests_unchanged` (historical); `packages/verity/tests/ir/test_query_ast.py`
  (c4ir's file, where the v1 string is only a query pattern); the frontend `Ops` bare-name default `_v1` (see Found, not fixed).

## Code-identity pins (recorded; they may change)
| pin | base `10996616` | `5e21eead` | epoch |
|---|---|---|---|
| `registry_version()` | `beb5d5f73aff6abd…` | `e183ae76b405d45a…` | `c41e555dc71ffcbd…` |
| `ref_vocab_digest()` | `63c73b5ecfaac756…` | `afb8df0652817b63…` | `afb8df0652817b63…` |
| `REFERENCE_CPU_F32` | `f955cb18bda06826` | `a05926da8eaeb697` | `a05926da8eaeb697` |
| `PROFILE_B1_EAGER_V2` | `2145f8ecc2118059` | `2145f8ecc2118059` | `4821740e43cc8a01` |
| `PROFILE_B1_EAGER`, `_V3`, `PROFILE_DENSE2_EAGER_V1` | `a2dcd5c2ed3919bb`, `b1a14d881eeda3e0`, `810f5908c0a5dd85` | same | same |

Full values: `evidence/step3/equality3.json` (`encodings.pins`) and `evidence/epoch/pins-{head,epoch}.json`.

## Found, not fixed
- Host-dependent F32 NaN: `F32Add/Mul/Div` and the FTZ family return the host's NaN word and inherit MXCSR FTZ/DAZ
  (x86_64 numpy 2.3.5: `F32Add(inf,-inf)` = `F32Mul(inf,0)` = `F32Div(0,0)` = `0xffc00000`, `F32Add(1,sNaN)` = `0x7fc00001`;
  arm64 laptop: `0x7fc00000`).
- `registry_version()` hashes the integration's registry sources only, not core's `verity.ml`. A change to a core
  Definition's evaluator does not move it.
- `check/replay/sampled_replay.py:184` names `fp8.py` as the home of the E4M3 cast (b1's file; it's core's now).
- The frontend `Ops.__getitem__` resolves a bare name to `f"{name}_v1"`, so `ops.AmpereBF16TcDot16` gives the superseded
  v1. The epoch's call sites use `ops["AmpereBF16TcDot16_v2"]`; the default is unchanged.
- The store's records trees omit `descriptor.json.gz` for 11 of the 12 programs-bearing rows (only #101 has them).
  The spec-id closure check stands in for them.
- `tests/program/test_gen_sampling.py` fails at base too (NameError); so do `test_twins` (openmp) and `test_sampling_rows`
  (NaN sign on x86).
- Gate (a) ran on a 256 GB pod, not 512 GB; T1 (with `replay_partition`) passed, and the pod cgroup peaked at 156.6 GB.
- Runs launched before `--custody-r2` have a local attempt with no run record, so `research data custody RUN --publish`
  finds the attempt "already" published and then fails its verify. Without a laptop fetch the only route is a separate
  run-record artifact that the attempt doesn't name (what c2b did, `tools/custody_gate_a.py` in c2b's notes).
- Lints were not re-run at the rebased ids: their inputs (`integrations/vllm`, `packages`, root config) are byte-identical
  to the tested `5e21eead` / `11c3e500`.

## Pods and cost
- `vyv-rf-c2-cpu` 08:51Z–~11:27Z, $1.28/h (~$3.33); `vyv-rf-c2-g1` 10:44Z–12:02Z, $1.09/h (~$1.42);
  `vyv-rf-c2-reg` 10:28Z–14:15Z, $1.76/h (~$6.66; terminated by `research pods drain`, 1/1 preserved). Total **~$11.4** of
  the $25 cap. All terminated; c2b created no pods.
