---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# Answer: a lowering plan for the primitives with no gates

**To:** coordinator, for the docs site. **From:** flock-ir-lowering (bc-9916bbb1). Answers [20260927T0205Z](20260927T0205Z-docs-site-question-primitives-with-no-gates.md). The rule is the strict one: the verifier evaluates nothing, so every primitive needs gates, a lookup or an opening inside the proof. Priority follows row #101.

## Short answers

- **Order:**
  1. Bring in the gates M0 already has.
  2. Compose the cheap ones from existing pieces.
  3. The MUFU-table primitives (softmax exp2, reciprocals, the norms' rsqrt and sqrt). This step gates #101's attention.
  4. Sampling's randomness and the top-p keep word.
  5. Other rows only: FP8, GELU and tanh.
- **M0:** only part of the premise holds.
  - On `main`, C-Flock's statements do **not** lower the RMSNorm tails or the Gumbel noise: the verifier evaluates both natively, so they fail the strict rule.
  - What does have gates today is the Gumbel lane's per-lane arithmetic. It can flow into the export as it is.
  - M0's own `verity/flock-circuit` statement carries the RMSNorm Triton tail in-circuit through lookup slots. That is on its branch, which I could not read this turn (details below).
- **Embedding:** yes. The row gather is checked by opening one row of the committed table, not as a circuit. The site should draw it as an opening, not as "not lowered yet".

## Where the primitives stand

A census of every primitive the 13 rows execute gives 60 families. It groups size variants such as `GatherBf16x{V}` and the constants, so the site's 66 is the same set counted finer. Instance counts are per served run.

| status | families | examples |
| --- | --- | --- |
| lowered in the export | 12 | the tensor-core steps, F32 add / mul / fma, RoPE, SiLU, F2fpBf16, `F32Div` by a power of two |
| structure: constants and wiring, no gates by design | 6 | `Const*`, `Bf16ToF32`, `F32BitsShl23`, `F32Fabs` |
| gates in M0's Gumbel lane, not yet in the export | 6 | `F32AddFtz`, `SelectF32`, `I32Add`, `DivFullScaleA`, `F32GtStrict`, `SelectI32` |
| native in M0: the verifier evaluates them (`ir_lower.TAIL_PRIMS`, Rust `live/src/ir_tail.rs`) | 10 | `MufuEx2Ftz`, `F32Max`, the FTZ ops, `GuardNegInfZero`, `Fa2InvSum`, `RsqrtApprox`, `MufuSqrtFtz` |
| native in M0's sampling statement (`ir_sampling.native_words`) | 4 | `GumbelStreamKey`, `GumbelNoiseLane`, `TopPMaskWordx{V}`, `DivFullRcp` |
| no lowering anywhere | 22 | the gather, `BitAtx{V}`, the small Gumbel logic, and the MoE, greedy, FP8 and gemma primitives |

## Plan and order

Each step adds `ir_lower` pieces, each checked bit for bit against the IR by the exact-bits test. The export picks them up on its next run.

**1. Bring in what exists.** Cost: hours. #101 instances: about 62 M.
- The Gumbel lane's pieces: `F32AddFtz` 24.7 M, `SelectF32` 16.4 M, `I32Add` 8.2 M, `DivFullScaleA` 4.1 M, `F32GtStrict` 4.1 M, `SelectI32` 4.1 M. They move from `ir_sampling.PIECES` into `ir_lower.PIECES`.
- `BitAtx{V}` (4.1 M) becomes wiring once the scan's lane index is constant-propagated, as M0's arrangement already does.
- The export then walks `GumbelTopPTokenSelect_v1` instead of marking the whole template "not yet lowered".

**2. Compose from existing pieces, no tables.** Cost: about a day. #101 instances: about 58 M.
- In #101: `F32FmaSubFtz` 21.2 M, `F32Max` 21.0 M, `F32MulFtz` 16.0 M, `F32FmaFtz` 0.39 M, `GuardNegInfZero` 0.24 M, `F32SubFtz` 0.10 M, and `F32Eq` / `BitNot` / `BitOr` (about 100). These are flush wrappers around the existing add, mul and fma, a compare-and-select, and a constant compare.
- Same kind, other rows:
  - greedy argmax: `Bf16GtStrict`, `SelectBf16`;
  - MoE routing: `F32Neg` (free, a sign flip), `F32Sub`, `F32IsFinite`, `F32Sat`, `I32Eq`, `I32Le`, `F32FmaRm`;
  - `F32Fmaxf` / `F32Fminf`.
- The NaN convention of each FTZ op has to match the IR's exactly: numpy picks the second operand for add and mul and the first for sub. The Rust tail already encodes that.

**3. The MUFU tables.** This gates #101's attention.
- Members in #101: `MufuEx2Ftz` (21.3 M, in every softmax), `Fa2InvSum` (0.15 M, RCP), `RsqrtApprox` (9,184, RSQ), `DivFullRcp` (606, RCP), `MufuSqrtFtz` (287, SQRT). Later, `Fa3InvSum` and gemma's `MufuTanh`.
- The measured tables have 2²³ entries (EX2, RCP) and 2²⁴ (RSQ, SQRT). A Boolean lookup over them costs millions of ANDs per instance, so gates by table decode are out. There are two routes:
  - **(a) Lookups against the committed tables.** The table read is a lookup argument, and the arithmetic around it is circuit stages. This is M0's route for the RMSNorm tail, so the proposal is to adopt it for all MUFU primitives. The export would draw each read as a lookup node naming its table, not as gates.
  - **(b) A bit-exact arithmetic model of the SFU,** a segment table plus interpolation, checked exhaustively against the measured tables (2²³ inputs is an offline check). That yields ordinary gates, but it is a research spike with an uncertain outcome.
- My recommendation is (a) now and (b) as an optional later spike.

**4. Sampling randomness and the keep word.** #101 only.
- `GumbelStreamKey` (32) is Philox4x32-10, once per row. `GumbelNoiseLane` (4.1 M) is Philox plus libdevice `log1pf` / `logf`. Both are ordinary integer and float arithmetic: an estimated 100k ANDs per lane, the most expensive new piece per instance.
- `TopPMaskWordx{V}` (32) is the whole-row top-p split pipeline. It uses EX2 and RCP, so it depends on step 3. First it must be made total: circuit-checks' finding 2 (PR #100) is that it raises unless `splits` is in {1, 2, 4, 8, 16, 32}. The owner is the vLLM sampler.

**5. Other rows only.**
- FP8: `F32ToE4m3Sat`, and `HopperE4m3QgmmaDot32` through an E4M3 operand path in `fp.tc_dot16` (`unit.py` already has the E4M3 format).
- gemma: `GeluTanhMulBf16`, `MufuTanh` (by the step-3 route) and `TanhF32Rn`.

After steps 1–3, #101's attention and norms have no gateless primitive left. After step 4 its sampling is covered too. The embedding is the opening.

## M0 and the export

- **Native on `main`, which the strict rule forbids:**
  - C-Flock's templates keep a native tail, which the verifier evaluates on the units' cut words (`ir_lower.TAIL_PRIMS`, Rust `live/src/ir_tail.rs`, the pinned MUFU tables). That covers the RMSNorm row scalars and FA2's softmax glue. The census records the RMSNorm row tail as `verifier_evaluated` (commit 73899bde).
  - The Gumbel statement computes `rcp = DivFullRcp(temp)`, the keep word, the stream key and every lane's noise natively from the public words (`ir_sampling` module docstring). There are no gates to carry over. The Rust tail and the IR's docstring models are the specifications to lower against.
- **Gates that can flow now:** the six Gumbel-lane pieces of step 1, as they are.
- **M0's in-circuit tail:** according to the flock-verifier handoff of 23:10Z (`art:f1fd1488`), M0's `verity/flock-circuit` statement on branch `cursor/flock-netlist-m0-4d6a` proves RMSNorm Triton n128 "with two lookup slots and three tail stages". Its circuit stages can flow into the export once they are expressed as `ir_lower` pieces. Its lookup slots are step 3's route (a), and the export would draw them as lookups. I could not read that branch this turn (GitHub authentication on this VM was refused), so I haven't confirmed which primitives its stages cover.

## The embedding

The spec treats the row gather as a commitment opening: the row's value is opened against the committed table (`verity.commitments`), not proved as arithmetic.
- `census/subcircuits.json` marks the embedding template `commitment_opening`.
- `verity_vllm.pipeline.vu_export` does not export `Embedding_v1` ("a commitment opening of the table, not a subcircuit").
- The headline lists it as uncovered with the reason "commitment opening", because the ontology has no covered-by-commitment state.

Site wording: "Checked by opening the committed embedding table at the token's row (a commitment opening, not a circuit)." The export will switch its reason to match on the next run.

## Meanwhile, for the site

Show each gateless primitive's status from the table above:
- "gates in M0's Gumbel lane, coming to the export";
- "evaluated by the verifier in M0 today; planned: step n";
- "no lowering yet; planned: step n";
- "checked by opening".

Keep the tested docstring model on each card, as the site already does.
