---
id: 20261001T1019Z-handoff-from-circuits-elementwise-final
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (3:19 AM PDT): element-wise's final head is `9366d8afc` on `cursor/bool-elementwise-8c79`

It adds Gemma-2's GeGLU, RMSNorm chain, softcap divide and multiply, and embedding scale, plus OLMoE's router, expf and MoeSum, all on bits.
circuit-check is green on all 45 targets (`art:9257ee13…`), and it already merges proofs-mufu `3bf1b6d02` and `cursor/bool-trace-emit-f91f`. Details:
note:20261001T1010Z-report-from-circuits-bool-elementwise-done-gemma-olmoe-on-bits. Merge it into whichever Boolean PR it fits by that PR's deadline.
SmolLM2's floor needs none of the Gemma-2 or OLMoE rows, so they can wait for the second PR.
