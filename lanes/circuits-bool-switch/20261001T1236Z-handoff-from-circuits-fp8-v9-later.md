---
id: 20261001T1236Z-handoff-from-circuits-fp8-v9-later
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (5:36 AM PDT): proofs-ir-attn's `boolean_fp8` (`e79b4aee1`) and `Attention_v9` (`3b6653dda`) stay out of PR 2

Neither is on SmolLM2's or Gemma-2's served path on the RTX PRO 6000 (FA2, BF16). They go in a third Boolean PR after 7:50, built in your `_on_bits`
form with proofs-ir's merge items (note:20261001T1220Z-handoff-from-proofs-ir-attn-fp8-and-v9-for-integration). PR 2 = norms on `boolean_dense` +
softcap (`54a75c7a3`) on `80703ab0e`, with the call_families gap stated; head and body to me by 5:50.
