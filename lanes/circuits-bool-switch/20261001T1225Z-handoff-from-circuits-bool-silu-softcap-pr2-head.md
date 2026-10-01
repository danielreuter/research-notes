---
id: 20261001T1225Z-handoff-from-circuits-bool-silu-softcap-pr2-head
campaign: overnight
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-silu (bc-73f78a8e-7c43-5351-9446-35b55301e311)
---

# For PR 2 (Gemma-2): the softcap chain on `MufuTanh_v2` is pure Boolean and green, at `54a75c7a3` on `cursor/bool-softcap-attn-e311`

From circuits-bool-silu, 5:25 AM PDT. Take `54a75c7a3` into the second Boolean PR.

**Merged, with no force-push:**

- proofs-mufu's `abc153b55` (`MufuTanh_v2`, 1,049 ANDs);
- #672 at `443538fed`;
- #672's new head `80703ab0e` (your 5:12 AM merge of slot d's stack). It merged cleanly, so `54a75c7a3` sits on PR 1 as it is now.

**Against `80703ab0e`, seven files change.** Three are proofs-mufu's: `mufu.py`, `mufu_tanh_quadratic.json` and `test_boolean_mufu.py`. Four are mine:

- `integrations/vllm/verity_vllm/program/registry/boolean_softcap.py` is back, unchanged from your `2e8baf4e7`. Its `word_statics` already
  names `P.MufuTanh`, so your lookup binds `TANH` to `MufuTanh_v2` with no code change. A test pins that.
- `integrations/vllm/tests/program/test_boolean_softcap.py` binds `TANH = MufuTanh_v2` (see the tests below).
- `tools/circuit_check/src/circuit_check/targets.py` gets one root in `_boolean_roots()`, which reaches the head and both of its blocks:

  ~~~python
  bind(BSC.AttentionSoftcap, T=17, NH=1, KVH=1, D=16, BN=16, CAP=50.0, DOT=BG.HopperBF16WgmmaDot16, INV=BAT.Fa2InvSum,
       MASKED_FROM=0, TANH=BM.MufuTanh, EX2=BM.MufuEx2Ftz)
  ~~~

  It also adds two imports there: `boolean_softcap as BSC` and `verity.ml.boolean.attention as BAT`.
- `tools/circuit_check/src/circuit_check/pins.json` gets four AND pins:
  - `AttentionSoftcap_v3{T=17,...}`: 670,766
  - `AttentionHeadSoftcap_v3{T=17,...}`: 670,766
  - `AttnBlockSoftcap_v3{NVIS=1,FIRST=True,...}`: 145,671
  - `AttnBlockSoftcap_v3{NVIS=16,FIRST=False,...}`: 480,332

  The full ids end in `TANH=MufuTanh_v2,EX2=MufuEx2Ftz_v2`.

**What passes at `54a75c7a3`:**

- **circuit-check** on the four ids: 0 failures. The one warning is `redundant-gates/ir` on the one-key block: 29,407 values computed again,
  27,295 of them in the `HopperBF16WgmmaDot16_v2` calls over its row of one probability and fifteen zeros. It doesn't fail `check`. I got the same result at `0079a2b22`
  (on `443538fed`). The reports are in `art:0b08b82b`.
- **`test_every_registered_definition_is_checked`** passes, so the coverage failure that took softcap out of PR 1 is fixed.
- **The vllm lints** pass: `tests/lint` (P9, P11 and the rest) and `test_no_dead_modules`.
- **`test_boolean_switch.py`** passes.
- **`test_boolean_softcap.py`** passes, 21 tests:
  - Every target is Boolean (`is_boolean`) and agrees with its word view, the v2 chain over `MufuTanh_v1` and `MufuEx2Ftz_v1`. That covers ten
    targets: blocks at each mask shape, Check_inf placement and BN 32, the Ampere step, heads with one or two blocks and a partial last block
    at either MASKED_FROM, and GQA with two KV heads. Each key row gets its own scale, so the capped scores reach all three of
    `MufuTanh_v1`'s regions: the identity, the measured table and ±1. From the second third of instances on, special words are planted in
    every operand.
  - A region test checks that the instances do reach all three regions.
  - A control test checks that a tanh which is right only on the closed regions is caught on the same instances.
  - Counts and digests are pinned for four targets, for example `AttentionSoftcap_v3{T=20,NH=4,KVH=2,...}` at 2,898,812 ANDs.
  - `boolean_version` takes the word chain to these Definitions.

I'm not pushing anything else to this branch unless you ask.
