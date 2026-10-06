---
id: circuits/20261006T0655Z-report-strong-reason-unit-output-width
campaign: proof-service
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: "@circuits lead (bc-b8aaadaa), X1 of note:verity-root/20261006T0550Z-report-proof-service-implementation; the rule in note:verity-root/20261006T0545Z-draft-daniel-one-recursive-architecture-v2"
---

# Unit output width: "at most 16 bits", or 16 bits with one 32-bit value

**Verdict: this is not a strong reason in the rules' sense.** There is no soundness or zero-knowledge hole and no
contradiction with a proved theorem. The literal rule's measured cost is modest. I report it because v2's default width
rule is not the plan's literal one. It has one exception, and choosing between the two is a choice of semantics.

**A correction to my 06:15Z first cut.** I wrote there that strict 16 "forces each output element's unit to recompute
the whole reduction" and "multiplies each norm unit's proving cost by d". That is wrong. A cheaper construction exists:
split each crossing 32-bit value into two 16-bit halves, each computed by its own unit. That costs one extra copy of the
producing unit, not d copies. See the measurements in "Measured".

## What the plan says

From note:verity-root/20261006T0545Z-draft-daniel-one-recursive-architecture-v2:

> The committed computation is divided into the fewest steps whose outputs are each at most 16 bits. … The proof shows
> each private partition satisfies its public predicates, such as "every proof unit's outputs are at most 16 bits".

## What is in the code today

The query of record is `Q_word{X: 16, W: 32}` (v1). Its width rule is `cut.fits`: a unit's committed outputs total at
most X = 16 bits, or they are exactly one value of at most W = 32 bits. The exception is the reason it is not 16.

## Measured

Method: `Q_word{16, 32}`'s cut of each Definition, from `cut.evaluate_definition` on main 68e614869. I list the units
that fail the literal rule (`cut.fits` at X = W = 16). "Split cost" is the extra computing gates if each failing unit is
duplicated into a high-half unit and a low-half unit, as a share of the Definition's computing gates. The checks are
run in `verity.primitives.circuits.partition_v2.check` with width (16, 16).

| Definition | Computing gates | Units | Fail at 16 | Failing outputs | Readers per failing unit | Split cost |
|---|---|---|---|---|---|---|
| `RMSNormTriton_v1{N=2048}` | 9,485 | 2,049 | 1: the FP32 scale | (32 bits, 1 value) | 2,048 | +3,341 gates (+35%), +1 unit |
| `AttentionHead_v3{T=21, D=64, BN=128}` | 446 | 129 | 44: FP32 row statistics | (32, 1) each | 2 to 64 | +169 gates (+38%), +44 units |
| `Attention_v3{T=21, NH=4, KVH=2, D=64}` | 4 heads | 516 | 176 | (32, 1) each | | +38% |
| `TokenSelect_v1{V=8}` | 21 | 1 | 1: the I32 token | (32, 1) | | +21 gates (+100%), +1 unit |
| `Gemm_v1`, `SiluMul_v1`, `RoPE_v1` | | | none | | | 0 |

Every failing unit is exactly one 32-bit value. Every unit the literal rule refuses here is admitted by the single-value
exception.

## Why the literal rule needs new circuits

- **A unit that outputs a 32-bit value fails at 16 in any cut.** Its output is that value. The only alternative is to
  put all of the value's readers in its own unit: RMSNorm's scale is read by all 2,048 element units, so that one unit's
  outputs become 2,048 × 16 bits.
- **The value must therefore become two 16-bit values.** One unit computes the high half and another the low half, and
  each reader combines them. The split has to be a computing gate (a shift or a mask), not wiring: `cut` treats wiring
  as structure, which each reader copies, so a wiring slice would leave the 32-bit value committed.
- **Each half's unit needs the whole computation of the value.** The circuit must hold it twice, since a gate is in
  exactly one unit. Two consequences:
  - new versions of every Definition in which an FP32 or I32 value crosses units: the norms, attention's statistics,
    softmax and the sampler;
  - the recompute rule moves from v1's `refuse` to `Q_word` v2's `report`, since the two copies compute one value.
- **Sound and hiding.** Each half is checked as its own unit. A faulty unit corrupts at most 16 bits, which is the
  plan's leakage weighting. Under the exception the weighting is at most 32 bits per faulty unit.
- **The measured cost is small at model scale.** About +35–38% on the norm and the attention statistics, which are a
  small share of a layer's gates next to its GEMMs, plus one extra unit per crossing value.

## What I built

- `verity/partition/v2` takes the width rule as a public parameter of the statement: `predicates(width=(X, W))`.
- The plan's literal rule is `predicates(width=(16, 16))`. It refuses today's Definitions at exactly the units in the
  table. The test `test_outputs_of_at_most_16_bits_refuse_every_unit_returning_a_32_bit_value` pins the refusal on v1's
  pinned program.
- The default is (16, 32), the query of record. `from_v1` maps a v1 object to it, so query mode and today's circuits
  register unchanged.
- Nothing in the format or the checker changes when the rule changes: only the statement's `width`.

## For Daniel

Choose one:

- **(16, 32), no circuit change.** Leakage is at most 32 bits per faulty unit on the norm, attention-statistics and
  sampler units, and 16 elsewhere.
- **(16, 16), the plan's rule.** It needs split versions of those Definitions (circuit-check on each), the `report`
  recompute rule, and about +35–38% gates on those Definitions.

My recommendation is (16, 32) now, and (16, 16) once the split Definitions exist, if the per-unit weighting matters for
the profile. The checker already supports both.
