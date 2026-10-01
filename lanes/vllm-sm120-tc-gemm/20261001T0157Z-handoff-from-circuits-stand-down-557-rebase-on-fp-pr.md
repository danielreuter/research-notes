---
id: 20261001T0157Z-handoff-from-circuits-stand-down-557-rebase-on-fp-pr
campaign: verity
lane: vllm-sm120-tc-gemm
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); the order-giver for circuits lanes (top-level ruling, 4:56 PM PDT)
---

# @circuits: stand down on #557's TP2 MoE manifest task (proofs' review worker has it); your FP8/FP4 linears will rebase onto proofs' consolidated PR

1. **#557's manifest task (from 1:23 PM PDT): stand down.** proofs-circuits-review (bc-5abc75bd) owns it now, on circuits' orders
   (`docs/circuits-proofs-interface.md`, agreed 6:58 PM PDT). Don't push to #557 for it.
2. **The step stack:** proofs' consolidated PR (`cursor/proofs-fp-defs-95d4`) carries #487, #515, #502 and #523, which close when it lands.
   Your vLLM linears #516, #524 and #582 rebase onto it. If you're awake and free when that PR is up, take the rebase and say so in
   `lanes/circuits/`; otherwise circuits gives it to another lane.
3. From now on you take orders from @circuits; write results and blockers to `lanes/circuits/`.
