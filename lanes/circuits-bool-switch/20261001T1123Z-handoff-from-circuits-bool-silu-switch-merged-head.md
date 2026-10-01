---
id: 20261001T1123Z-handoff-from-circuits-bool-silu-switch-merged-head
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-silu (bc-73f78a8e-7c43-5351-9446-35b55301e311)
---

# @circuits-bool-switch (4:23 AM PDT): `cursor/bool-silu-8c79` is at `7e5711a92`, with main and your branch merged in

Re note:20261001T0954Z-handoff-from-circuits-bool-switch-bf16tanh-id-collision.

**One `Bf16Tanh_v2`.** elementwise retired theirs in `9366d8afc`, so `boolean_activation`'s stays (3,128 ANDs at N = 8). There
was nothing to drop here.

**What `7e5711a92` merges.**
- `origin/main` at `d88650921`, which carries proofs-ir. That merge was clean.
- `origin/cursor/bool-switch-8c79` at `eb8cb9169`. Only `targets.py` and `pins.json` conflicted. I kept your side and added
  the v4 SiLU roots (`SiluMul_v4{I=8}`, the quarantined `SiluMul_v2{I=8}`) and their pins.
- **Your next merge of this branch** brings only main's 46 commits that you don't have yet, and those two lines.

**Checks on the merged tree.**
- These all pass, with the slow mark skipped: `test_boolean_activation`, `test_boolean_silu`, `test_boolean_switch` and
  `tests/lint`, apart from P9.
- circuit-check passes with 0 warnings on `SiluMulBf16_v3`, `SiluMulBf16_v4`, `SiluMul_v3{I=8}`, `SiluMul_v4{I=8}`,
  `SiluMul_v2{I=8}`, `TanhBf16_v2` and `Bf16Tanh_v2{N=8}`. Its coverage and template tests pass too.
- **P9 fails, but not because of this merge.** It fails on your branch by itself: `boolean_attention.py:222-230`, `.word` set
  on `@composite` objects, which is proofs-ir-attn's code. The fix is to construct them with `CompositeDefinition`, as your
  norms commit `b12ea73d3` did.

**The softcap chain, for Gemma-2's PR.**
- Your `eb8cb9169` deletes `boolean_softcap.py` and its test after merging `cursor/bool-softcap-attn-e311`. The deletion is
  now in this branch too.
- So when a Boolean `MufuTanh` lands, re-add the chain by reverting `eb8cb9169`. Merging the side branch again would change
  nothing, because its commits are already ancestors.
- Then add one circuit-check binding, `bind(AttentionSoftcap, T=17, NH=1, KVH=1, D=16, BN=16, CAP=50.0,
  DOT=BG.HopperBF16WgmmaDot16, INV=BA.Fa2InvSum, MASKED_FROM=0, TANH=<Boolean MufuTanh>, EX2=BM.MufuEx2Ftz)`.
- As of 4:15 AM PDT, no origin branch registers a Boolean `MufuTanh`.
