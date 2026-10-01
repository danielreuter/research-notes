---
id: 20261001T0843Z-report-from-circuits-bool-silu-tanh-green-attn-softcap-blocked
campaign: overnight
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-silu (bc-73f78a8e-7c43-5351-9446-35b55301e311)
---

# @circuits: Gemma-2's tanh is on bits (`Bf16Tanh_v2`, 391 ANDs per element). GeLU and the scalar rows were already elementwise's, so I retired mine. The attention softcap needs `MufuTanh_v2` and proofs' v6 block (1:43 AM PDT)

Branch `cursor/bool-silu-8c79` at `59b134051`, pushed. It merges `cursor/bool-trace-emit-f91f`, so it already uses `trace.emit`.

## Converted

Each row below is a hot swap for the word row in the served Program. The id is the one in node 1's Gemma-2 descriptors
(`cov-cg04`).

| Boolean Definition | Word Definition it replaces | And / Xor / Not |
|---|---|---|
| `TanhBf16_v2` (element) | `TanhBf16_v1` (the word element, new) | 391 / 1,628 / 31 |
| `Bf16Tanh_v2{N}` | `Bf16Tanh_v1{N=256000}`, the final-logit softcap's tanh | 391 N (N = 8: 3,128 / 13,024 / 248) |

- **Exactness.** Exact on all 65,536 words: the element against `TanhBf16_v1`, and the row of one against the served `Bf16Tanh_v1{N=1}`.
- **The table's band.** The closed forms hold off a band of exponent fields (e 122..129), and the band's first and last
  exponent pairs are each needed.
- **Partition.** Under `Q_word_v1`, the row has the word row's units, one per element.
- **circuit-check.** Green with `--fail-on-warnings` (SiLU too), and the counts are pinned.
- **Tests.** `test_boolean_activation.py` has 9 tests, each under 5 s. With them, the vLLM `program` and `query` quick tiers pass
  (fixtures fetched), as do the vLLM lint and the circuit-check suite.
- **MUFU.** None: the word calls `TanhF32Rn_v1`, the libdevice `tanhf` stand-in.

## Duplicates retired: GeLU and the softcap's divide and multiply belong to elementwise

elementwise's `boolean_dense` registers the same ids as I had, so one of the two had to go. It added them at 12:17 AM PDT (GeLU)
and 12:54 AM PDT (the scalar rows), on `cursor/bool-elementwise-8c79`.

| Id | elementwise | mine |
|---|---|---|
| `GeluTanhMulBf16_v2` | 1,347 ANDs | 1,353 ANDs |
| `GeluTanhMul_v2{I}` | same | same |
| `Bf16DivScalar_v2` | 865 ANDs per element at C = 30 | identical |
| `Bf16MulScalar_v2` | 629 ANDs per element at C = 30 | identical |

I removed mine, with their roots and pins, in `59b134051`. I also checked their GeLU against `GeluTanhMulBf16_v1`. It
matches on every gate word at 12 up words (786,432 pairs) and on 200,000 random pairs.

## For circuits-bool-switch: one import error breaks elementwise in the merged tree

I trial-merged the switch (`df22df4aa`), then elementwise (`a38c5b2ee`), then this branch.

**The error.** `verity/ml/boolean/elementwise.py` on elementwise's branch still imports `trace._body`, which `trace.emit`
replaced. In the merged tree, `verity.ml.boolean.elementwise`, `boolean_dense` and `boolean_norms` all fail to import, so the
switch reports every one of their rows as a gap.

**With the fix.** Renaming that import to `emit`, the registry loads with no errors and the switch maps all four of
Gemma-2's rows:
- `GeluTanhMul_v1{I=9216}`, `Bf16DivScalar_v1{N=256000,C=30.0}` and `Bf16MulScalar_v1{N=256000,C=30.0}` map to
  `boolean_dense`.
- `Bf16Tanh_v1{N=256000}` maps to `boolean_activation`.

My tests and the SiLU tests pass in that tree.

**Expected conflicts.** `targets.py` (`_boolean_roots`) and `pins.json` conflict between every pair of family branches. The
union of both sides resolves them.

## Attention-logit softcap: blocked on proofs

**Where it is.** The softcap is not a separate Definition. It is stage A′ inside
`AttentionSoftcap_v2{T, NH=8, KVH=4, D=256, BN=64, CAP=50.0, DOT=HopperBF16WgmmaDot16_v1, INV=Fa2InvSum_v1, MASKED_FROM}`:
`MufuTanh_v1(F32MulFtz(s, softmax_scale / 50))`. The multiply by the cap is folded into the exp2 constant.

**What it needs.**
- `F32MulFtz_v3` is already Boolean.
- `MufuTanh_v1` is the measured sm_89 `tanh.approx` table over [2^-8, 8), about 89M words with no closed form. proofs-mufu's
  list has no `MufuTanh_v2`.
- The rest of the block is `AttnBlock_v5`'s body, which proofs-ir-attn is putting on bits as `AttnBlock` / `AttentionHead` /
  `Attention` v6.

**My plan.** As soon as v6 is on origin, I write `AttnBlockSoftcap_v3` / `AttentionHeadSoftcap_v3` / `AttentionSoftcap_v3`
as v6's body plus A′. `TANH` and `EX2` become statics through `word_statics` (`MufuTanh_v1`, `MufuEx2Ftz_v1`), so the switch
binds proofs' Boolean MUFUs, or names the gap until they exist.

**Why not now.** Writing it before v6 would duplicate proofs' FA2 body on bits. Without a Boolean `MUFU.TANH`, the block
couldn't be evaluated on bits anyway.

**Alternative for the switch's owner.** The switch could lift registered word composites by replay, as it already lifts
derived functions. Once the leaves exist, `AttentionSoftcap_v2` would need no hand-written Boolean version at all.

**Asks.**
- Route a `MufuTanh_v2` request to proofs-mufu. Gemma-2's attention can't be pure without it.
- Tell me if you want the softcap block built now regardless.

## Other models: SiLU is the only activation

I read one row per model from node 1's descriptors: Llama-3.2-1B, Qwen2.5 0.5B / 1.5B / 7B, Qwen3-4B / 30B-A3B, Phi-3-mini,
OLMoE-1B-7B, Mistral-7B, SmolLM2 and TinyLlama. The only activation is `SiluMul_v1` / `SiluMulBf16_v1`, which is done
(`SiluMul_v3`). `NvExpf_v1`, in the MoE models, is the router's softmax, not an activation.

## Files

- New: `integrations/vllm/verity_vllm/program/registry/boolean_activation.py`.
- New: `integrations/vllm/tests/program/test_boolean_activation.py`.
- Changed: `boolean_silu.py` now uses `boolean_activation.band` (same circuit, same digests).
- Changed: `circuit_check` `targets.py` and `pins.json`.
