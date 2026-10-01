---
id: 20261001T0905Z-report-from-circuits-bool-silu-softcap-attention-on-bits
campaign: overnight
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-silu (bc-73f78a8e-7c43-5351-9446-35b55301e311)
---

# @circuits (2:05 AM PDT): Gemma-2's attention softcap is on bits and exact; it waits only on a Boolean `MufuTanh`, so it sits on a side branch

`cursor/bool-silu-8c79` is unchanged at `59b134051` and ready to integrate. The new work is on
`cursor/bool-softcap-attn-e311` at `ca85ccb57`: this branch, plus a merge of `origin/cursor/proofs-ir-attn-95d4`, which supplies
`MufuEx2Ftz_v2` and `Fa2InvSum_v2`.

## What is built

| Boolean Definition | Its word view |
|---|---|
| `AttnBlockSoftcap_v3{D, NVIS, FIRST, BN, CAP, DOT, CHECK, TANH, EX2}` | `AttnBlockSoftcap_v2{D, NVIS, FIRST, BN, CAP, DOT, CHECK}` |
| `AttentionHeadSoftcap_v3{T, D, BN, CAP, DOT, INV, MASKED_FROM, TANH, EX2}` | `AttentionHeadSoftcap_v2{...}` |
| `AttentionSoftcap_v3{T, NH, KVH, D, BN, CAP, DOT, INV, MASKED_FROM, TANH, EX2}` | `AttentionSoftcap_v2{...}`, the Call in Gemma-2's Program |

- **Body.** Each is `fa2_softcap`'s v2 body line for line, on bits. `DOT` and `INV` bind to the Boolean versions of the
  word's (`HopperBF16WgmmaDot16_v2`, `Fa2InvSum_v2`).
- **The MUFU statics.** `TANH` (stage A′) and `EX2` are statics. `word_statics` names their word Definitions (`MufuTanh_v1`,
  `MufuEx2Ftz_v1`), the same mechanism the norms use, so the switch binds each one to its Boolean version.
- **Exactness.** Bits equal the word at every shape I tried: a first and a later block, heads with one or two blocks and
  `MASKED_FROM` 0 and 1, `BN` = 32, and GQA with `NH` = 4, `KVH` = 2. These runs use a test-only, unregistered `TANH` that is
  exact on `MufuTanh_v1`'s closed regions (identity below 2^-8, ±1 from 8, NaN). The inputs drive every capped score into
  those regions, and two controls fail as they should: an identity `TANH`, and inputs in the table region.

## Why it's not on `cursor/bool-silu-8c79`

**No `MufuTanh` on bits exists anywhere.** I searched every recent origin branch.

**circuit-check can't pass without one.** circuit-check compares each registered Boolean Definition with its word on random
vectors. `MufuTanh_v1` evaluates the whole table region from the in-tree table. So any binding of `TANH` other than a real
Boolean `MufuTanh` fails `correspondence`. With no binding at all, the family-coverage test fails instead.

**Once proofs ships it,** merge this branch and add one circuit-check binding, and Gemma-2's attention is bits throughout.

## Asks

- **`MufuTanh_v2` for proofs-mufu.** A Boolean `MUFU.TANH` (sm_89 `tanh.approx.f32`) is the last piece of Gemma-2's attention.
- **For proofs-ir-attn.** v6 is the v3 chain on bits. Every served model on node 1 calls the v5 chain instead:
  `Attention_v5{DOT=HopperBF16WgmmaDot16_v1, INV=Fa2InvSum_v1, MASKED_FROM}`. Nobody has v5 on bits yet, and the softcap chain
  is v5 plus stage A′.

## Next

- Tests in `test_boolean_softcap.py`, the switch's binding checked in a trial merge, and units against the word's.
- 4:50 AM PDT report.

## Files

- New: `integrations/vllm/verity_vllm/program/registry/boolean_softcap.py`.
- New branch: `cursor/bool-softcap-attn-e311`.
