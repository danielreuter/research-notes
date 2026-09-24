---
id: r21-silicon/silicon-p0/20260922T1804Z-report-silicon-p0
campaign: r21-silicon
lane: silicon-p0
kind: report
status: closed
repo: verity-main@b243a78
---

# Report: silicon Phase 0 -- one ontology for FP8/FP4 tensor-core numerics (lane silicon-p0, 2026-09-22)

Consolidation only; no hardware touched. Everything below ran on the laptop (pure Python + z3 where the checker already used it).

## Branch

- `lane/silicon-p0` in worktree `/Users/danielreuter/projects/verity-main-wt/silicon-p0`, based on `main` = `a0f0eb9`; final
  SHA **`b243a78f74df1ad6b4a48b434a3f130901fa95d3`** (5 commits: `f8ed649` term/models/instructions/shim, `0cd8daa` tests +
  `fixtures/tc`, `ff9ed00` checker `Params` generalisation, `2868eb2` draft targets + vectors + D10-D15, `b243a78` READMEs).
- Not pushed. `main` has since moved 13 commits (to `72e8c7a`, merge of `lane/store-prov`); `git merge-tree` of `main` and
  this branch is conflict-free and the two touch disjoint files.
- Nothing under `tools/tc_probe/**` or `tools/research/**` was edited; the source repos `veritor` and `autoproof` were read only.

## Files (31 vs a0f0eb9: 16 added, 15 modified)

Added: `packages/verity/src/verity/ml/tc/{term,models,instructions}.py`; `packages/verity/tests/ml/test_{term,models,instructions}.py`;
`packages/verity/tests/verification/test_fp8_targets.py`; `backends/numerical/tests/checker/test_fp8.py`;
`fixtures/tc/{README.md,veritor-tc-fp8-2026-09-08.json,autoproof-SEMANTICS.lock.v1.json,autoproof-probe-vectors.json}`;
`fixtures/tc/vectors/fp8-{hopper-wgmma,ada-mma}-k{32,1536}.json`.

Modified: `verity/ml/tc/{silicon,__init__}.py` (shim, exports); `verity/verification/{target,programs}.py`;
`backends/numerical/python/verity_numerical/checker/{params,reference,gadgets,step,search,__init__}.py`, `checker/v2/params.py`;
`fixtures/discrepancy_log.json`; `packages/verity/tests/verification/test_discrepancy_log.py`; `backends/numerical/README.md`;
`packages/verity/tests/ml/fixtures/README.md`.

## Tests

- `uv run pytest packages/verity -q`: **370 passed** (16.8 s).
- `uv run pytest backends/numerical -q`: **564 passed, 8 skipped** (85 s; the skips are the pre-existing opt-in/z3 ones).
- Every test that existed at `a0f0eb9` passes unchanged; `silicon.py` is a re-export shim and every `silicon.*` importer in the
  repo works as before. Checker contracts, hint layout and outputs at `REAL`/`TOY`/`TINY` are byte-identical to `main`'s.

## The ontology as code

- `term.py`: `Term`, exact products `bf16_product`, `e4m3_product`, **`e5m2_product`** (1-5-2, bias 15, subnormals, inf/NaN codes
  rejected), **`e2m1_product`** (FP4: ±{0, .5, 1, 1.5, 2, 3, 4, 6}); decoders `decode_bf16/e4m3/e5m2/e2m1(word) -> (sign, exp, sig) |
  special`; `fp32_term`/`pack_fp32`. Property-tested against Python floats/Fractions on every code of every format.
- `models.py`: `Model` Protocol (`name, k, operand_bits, dtype, validated, step, product`); `GroupSum` = the old `Pipeline`
  (kept as an alias; `PIPELINES` unchanged) plus E5M2 hypotheses `ADA_E5M2_M16N8K32`, `HOPPER_E5M2_K32`; `BlockScaledAlignAdd`
  = autoproof model5 ported from `fp4-ref/src/native.rs` + `spec/src/dyadic.rs` (four exact 16-term E2M1 group dots, UE4M3/UE8M0
  scales as exact exponent shifts, five-way align-add with w1 = 42 below the largest addend and w2 = 36 riding the accumulator
  exponent, RZ, hot-group clip at 2^-19 when both scale codes of a live group are in 0x78..0x7E). Instances
  `BLACKWELL_SM120_NVF4` (pinned by autoproof), `BLACKWELL_SM120_MXF4` and `BLACKWELL_SM120_MXF4_UNDERFLOW_PLUS0` (the one
  ambiguity, D13). `MODELS` = every instance by name.
- `instructions.py`: `Instruction` dataclass and `INSTRUCTIONS` with exactly the 14 required ids (below).
- `target.py`: `Target.status` (`frozen` | `draft`) and `Target.instruction`; `FIRST` is `frozen` / `sm80.mma.m16n8k16.bf16`;
  `FP8_HOPPER_WGMMA` and `FP8_ADA_MMA` are `draft`; `TARGETS` by name. `programs.gemm_accumulator_fp8(k)` builds
  `GemmAccumulator<K>` (K % 32 == 0: `tc_dot32_0` then chained `tc_dot32`, no cast). The docstrings say the FP8 store epilogue
  (scale + `cvt.rn.satfinite.e4m3x2`) is a separate later relation.

## Instruction registry

| id | status | model | ptx | evidence (abridged) |
|---|---|---|---|---|
| `sm80.mma.m16n8k16.bf16` | pinned | `ampere_bf16_m16n8k16` | `mma.sync.aligned.m16n8k16.row.col.f32.bf16.bf16.f32` | Hawkeye A100; verity run r20260921-232750-56c5 (25.7M elements, 0 mismatches); golden 360 |
| `sm89.mma.m16n8k16.bf16` | pinned | `ada_bf16_m16n8k16` | same | veritor 4090 24,898,304/24,898,304; run r20260921-231618-ea24; golden 360 |
| `sm90.mma.m16n8k16.bf16` | hypothesis | `hopper_bf16_m16n8k16` | same | Hawkeye H100 groups (16,), width 26; veritor H100 evidence is **wgmma** m64n128k16 (307M words), no mma.sync measurement |
| `sm89.mma.m16n8k32.e4m3` | pinned | `ada_e4m3_m16n8k32` | `mma.sync.aligned.m16n8k32.row.col.f32.e4m3.e4m3.f32` | veritor 4090 24,898,304/24,898,304 over 194,518 tiles; Hawkeye's Hopper FP8 sim only 82.40 % (D10) |
| `sm89.mma.m16n8k32.e5m2` | hypothesis | `ada_e5m2_m16n8k32` | `...f32.e5m2.e5m2.f32` | none; e4m3 pipeline with e5m2 products |
| `sm90.wgmma.m64n8k32.e4m3` | pinned | `hopper_e4m3_wgmma_k32` | `wgmma.mma_async.sync.aligned.m64n8k32.f32.e4m3.e4m3` | veritor H100 2026-09-08: 144,543,744 words, 0 mismatches (measured shape m64n**64**k32, D15); Hawkeye zero-acc |
| `sm90.wgmma.m64n8k32.e5m2` | hypothesis | `hopper_e5m2_wgmma_k32` | `...m64n8k32.f32.e5m2.e5m2` | none; e4m3 pipeline with e5m2 products |
| `sm90.mma.m16n8k32.e4m3` | unprobed | None | `mma.sync.aligned.m16n8k32.row.col.f32.e4m3.e4m3.f32` | the Hopper legacy-path question: (16,16) or (32,)? (D14) |
| `sm120.mma.m16n8k64.e2m1.nvf4` | pinned | `blackwell_sm120_nvf4_m16n8k64` | `mma.sync.aligned.kind::mxf4nvf4.block_scale.scale_vec::4X.m16n8k64.row.col.f32.e2m1.e2m1.f32.ue4m3` | autoproof RTX 5090: 1,574,998 dots under model5; 1,601 + 1,400 vectors replayed here; zero-init acc only (D11, D12) |
| `sm120.mma.m16n8k64.e2m1.mxf4` | hypothesis | `blackwell_sm120_mxf4_m16n8k64` | None | no measurement; UE8M0 variant of the nvf4 transducer, clip off; sign-of-underflow ambiguity (D13) |
| `sm100.tcgen05.mma.e2m1.nvf4` | unprobed | None | None | B200 tcgen05, nothing measured; sm_120 model not assumed to carry over |
| `sm100.tcgen05.mma.e2m1.mxf4` | unprobed | None | None | nothing measured |
| `sm100.tcgen05.mma.bf16` | unprobed | None | None | nothing measured |
| `sm100.tcgen05.mma.e4m3` | unprobed | None | None | nothing measured |

Full evidence strings are in `instructions.py`; `tests/ml/test_instructions.py` checks the exact id set, model/dtype/k
consistency, that `pinned` entries have a recorded mnemonic and evidence and a model not marked HYPOTHESIS, that `unprobed`
entries have no model, and that the recorded mnemonics are the source repos' (the four sm_100 ids have `ptx=None`, `shape=None`).

## Autoproof cross-check

- `BlockScaledAlignAdd` replays **1,601 / 1,601** recorded nvfp4 sample vectors (`probe3_1783788526.json`: ascending-K chains
  from a zero accumulator, K in {64, 128, 256}, suites scan/random/extreme-span/cancellation/curated) bit-exactly, and
  **1,400 / 1,400** unscaled kind::f8f6f4 E2M1 m16n8k32 dots (`probe2_1783788240.json`) through the same machinery as a
  scale-less two-group GroupSum. The refuted single-window W = 26 model disagrees on the recorded vectors as autoproof says.
- The full 1,574,998 dots exist only as per-suite counts in autoproof's result files (the raw words were not kept), so the
  agreement count verity can *replay* is 3,001; the pin count it *cites* is autoproof's.
- Corrections to the brief: autoproof's pin is dated **2026-07-11** (lockfile `ADOPTED at oracle-v3`), not 2026-09; the
  lockfile's 1,574,998/1,574,998 is model5 (clip on) while the checked-in JSON scores clip-less model2 at 1,574,997 (the one
  mismatch is the clip's evidence). Both recorded in `validated`, the evidence strings and D12.

## `Params` generalisation (backends/numerical checker)

- `Params` now carries two formats: operand (`sig`, `exp`, `op_nan_rule` ∈ {ieee, e4m3}) and accumulator (`acc_sig`, `acc_exp`
  defaulting to `exp`), and admits `width < acc_sig` (`lossy`, `acc_drop = acc_sig - width`; Hopper/Ada E4M3: 14 < 24).
  `Params.from_model(GroupSum)` derives them; at `AMPERE_BF16_M16N8K16` it is `REAL`. New small instance `TOY_LOSSY`.
- One new **gadget**, `RescaleState` (`M = 2^drop·P + r`, `r < 2^drop`, `P < 2^W`), before `AlignState` on lossy paths --
  the truncation `GroupSum.step` performs on the incoming FP32 significand. `Normalise` produces a W-bit magnitude and scales
  back up exactly (`norm_up`). `Bf16Decode` (alias `OperandDecode`) admits the E4M3 NaN rule (0x7F/0xFF NaN, 0x7E = 448
  finite) via one extra range check; accumulator gadgets read `acc_*`.
- **No new family** in `verification/families.py`: the cast-free `veritor.tensor-core.<pipeline>@2` sets already describe
  `tc_dot32`/`tc_dot32_0`; the rescale is a gadget of the checker's decomposition of that step, not a new gate.
- `z3_group_step` and the `v2` arithmetisation stay BF16-only and raise (`Reject`/`ValueError`) on lossy or two-exponent
  configurations instead of answering wrongly.
- `tests/checker/test_fp8.py`: reference evaluator and gadget relation equal `model.step` on 2,000 random finite cases each for
  `HOPPER_E4M3_K32` and `ADA_E4M3_M16N8K32` (zero accumulators, cancellation, subnormals, 448), D10's zero-product truncation,
  E4M3 NaN rejection, rescale-hint mutations rejected, E5M2 hypotheses through the same `Params`, exhaustive `TOY_LOSSY` slice.

## Draft targets and vectors

- `FP8_HOPPER_WGMMA` (`sm90.wgmma.m64n8k32.e4m3`, family `veritor.tensor-core.hopper_e4m3_wgmma_k32@2`, digest `6d90478b…`) and
  `FP8_ADA_MMA` (`sm89.mma.m16n8k32.e4m3`, `…ada_e4m3_m16n8k32@2`, digest `2bcdad67…`), both `status="draft"`: program
  `GemmAccumulator<K>`, finite E4M3 operands / finite FP32 accumulators, bare-dot epilogue (FP32 word public). No guest is
  bound to these families and no `typed-obligation/v0` lowering exists yet.
- Vectors `fixtures/tc/vectors/fp8-{hopper-wgmma,ada-mma}-k{32,1536}.json` (schema `verity/tc-reference-vector/v0`): model
  replays from a recorded seed + recipe (10 % zeros, 15 % subnormals, 5 % ±448, rest uniform finite), every step's FP32 word,
  regenerable byte-for-byte by the test. On shared operands the two drafts differ in 36 of 48 K = 1536 steps -- different
  functions, same adder. They are *not* hardware captures; the instruction pins are their evidence.

## Discrepancy log (D10-D15; schema unchanged, `profile` may now be any `TARGETS` name or an `INSTRUCTIONS` id)

- **D10** resolved: Hawkeye's Hopper FP8 sim vs Ada (82.40 %, 2,252,909 mismatches of 12.8M); Ada is (16,16)/14/-139; the
  14-bit truncation of a pass-through accumulator applies even through all-zero products (`0x3F800001 -> 0x3F800000`).
- **D11** resolved: autoproof's single-window W = 26 refuted (142,270 lockfile / 143,076 JSON mismatches of 1,574,998).
- **D12** resolved: what the autoproof pin covers (model5 vs model2 counts, 2026-07-11 date, zero-init accumulators only).
- **D13** open (owner tc-probe-fp8): sign of a computed zero when a nonzero sum lies below the FP32 subnormal grid (mxf4 only) --
  two named hypotheses.
- **D14** open (tc-probe-fp8): Hopper legacy path `sm90.mma.m16n8k32.e4m3` -- (16,16) or (32,)?
- **D15** open (tc-probe-fp8 / coordinator): the id `sm90.wgmma.m64n8k32.e4m3` names n8 while the H100 evidence is m64n64k32;
  the FP8 floor (-139) is Hawkeye's constant, bounded only to [-152, -126] by the H100 fit and unobservable on Ada.

## Open questions for the probe lane (what the hardware must confirm first)

1. **Hopper legacy path** (D14): one `mma.sync.m16n8k32.e4m3` on an H100 with the separating tile (products 0, 1 = ±256·256,
   product 16 = 1·1, rest zero, acc 0): `0x00000000` → one group of 32, `0x3F800000` → two of 16. Same for `sm90.mma.m16n8k16.bf16`.
2. **E5M2** on sm_89 and sm_90: are groups/width/floor those of the E4M3 pipeline (the registered hypotheses)?
3. **wgmma n8 vs n64** (D15a): probe `m64n8k32` directly or have the coordinator declare the id's shape nominal.
4. **FP8 floor** (D15b): subnormal FP32 accumulators with all-zero products; if unobservable in the finite domain, say so in
   the target and admit any floor ≤ -126.
5. **mxf4 on sm_120** (D13): the kind::mxf4 mnemonic, the hot clip's absence, and the sign of the underflowed zero
   (`0x80000000` vs `0x00000000`).
6. **Arbitrary accumulators on sm_120 nvf4** (D12): autoproof only chained from +0; the w2 = 36 window's dependence on the
   accumulator exponent is extrapolated for accumulators the chain never produced.
7. **sm_100 tcgen05** (all four ids): nothing measured; the sm_120 model is not assumed to carry over.
