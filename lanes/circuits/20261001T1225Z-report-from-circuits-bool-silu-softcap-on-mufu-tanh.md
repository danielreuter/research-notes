---
id: 20261001T1225Z-report-from-circuits-bool-silu-softcap-on-mufu-tanh
campaign: overnight
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-silu (bc-73f78a8e-7c43-5351-9446-35b55301e311)
---

# circuits-bool-silu -> @circuits (5:25 AM PDT): the softcap chain is pure Boolean on `MufuTanh_v2` and green, at `54a75c7a3`

`cursor/bool-softcap-attn-e311` is at `54a75c7a3`, ahead of 5:50. The handoff to circuits-bool-switch is
`note:circuits-bool-switch/20261001T1225Z-handoff-from-circuits-bool-silu-softcap-pr2-head`.

**What's merged** (no force-push):

- `abc153b55`, proofs-mufu's `MufuTanh_v2`;
- #672 at `443538fed`;
- #672's new head `80703ab0e` (slot d's stack), which merged cleanly.

The merge with #672 deleted `boolean_softcap.py` and its test, because the switch had removed them from PR 1. I restored them at the
switch's `2e8baf4e7`. The `pins.json` conflicts were the union of both sides; `RsqrtApprox_v2` stays at mufu's 1,134.

**The binding:**

- `TANH` = `MufuTanh_v2` and `EX2` = `MufuEx2Ftz_v2`. With those, `AttnBlockSoftcap_v3`, `AttentionHeadSoftcap_v3` and `AttentionSoftcap_v3`
  are pure Boolean.
- `boolean_softcap.py` itself is unchanged. Its `word_statics` already names `P.MufuTanh`, and the switch's `boolean_version` takes the
  word chain to these Definitions. A test pins that.

**Checks against the word views:**

- The word view is the v2 chain over `MufuTanh_v1`. The bits agree with it on special and random instances across ten targets: blocks,
  heads and GQA attention.
- The instances now reach the measured table too, not only `MufuTanh_v1`'s closed regions. A region test holds the construction to that.
- A control test confirms that a tanh which is right only on the closed regions is caught on the same instances.
- `test_boolean_softcap.py` passes, 21 tests. The heads, the attention and the control are marked `slow`.

**Pins:**

| Target | ANDs |
| --- | --- |
| `AttnBlockSoftcap_v3`, 5 keys | 216,995 |
| `AttnBlockSoftcap_v3`, 16 keys | 480,332 |
| `AttentionHeadSoftcap_v3{T=20}` | 724,703 |
| `AttentionSoftcap_v3{T=20,NH=4,KVH=2}` | 2,898,812 |

Each pin also has its XOR and NOT counts and its program digest.

**circuit-check:**

- One root in `circuit_check.targets`: one head of 17 keys (two blocks, Check_inf in both). Its four AND counts are in `pins.json`.
- 4 targets, 0 failures, at both `0079a2b22` and `54a75c7a3` (`art:0b08b82b`).
- One warning, which doesn't fail `check`: `redundant-gates/ir` on the one-key block, 29,407 values computed again. Most are in the dot
  calls over its row of one probability and fifteen zeros.

**Other checks:**

- `test_every_registered_definition_is_checked` passes, so the PR 1 coverage failure is gone.
- The vllm lints pass: `tests/lint`, including P9 and P11, and `test_no_dead_modules`.
- `test_boolean_switch.py` passes.
- proofs-mufu's quick tests pass at the merged head (31 tests).

**Not run here:** the whole `suites.py`. The TP2 MoE test still runs out of memory on this 16 GB VM, so the switch's `check` is the full run.
