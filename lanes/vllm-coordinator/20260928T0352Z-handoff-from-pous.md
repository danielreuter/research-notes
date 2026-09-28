---
id: 20260928T0352Z-handoff-from-pous-to-vllm-coordinator
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS: generic protocol interface and vLLM option (question)

Daniel wants the POUS band d = 12 result frozen as an MVP. He wants it to be the first implementation of a fully generic Python POUS protocol with interfaces, in the spirit of `protocols/sampled_proofs`. A vLLM integration would enable POUS as an option, and each scheme (band, dense, P3) would implement only a few methods: encode, decode, respond.

Questions:

1. **Structure.** How do you want this structured so it matches how sampled proofs is organised?
   - Is `protocols/pous` (verity_pous, PR #166) the right home for the abstract interfaces, with the schemes as implementations?
   - Is there an existing interface pattern in Verity we should copy? For example, how backends are judged in `verity.proofs`.
2. **vLLM** (for the vLLM coordinator). Where should the POUS option live in `integrations/vllm/`?
   - Its job: decode weights from the encoded store on every forward pass, run the timed audit responder in process, and do nothing when disabled.
   - Existing work: demo PR #172 and kernels PR #188.
   - Per your 20260927T1505Z note, we won't touch `integrations/vllm/` until you've OK'd a plan.

The owner is bc-13eada34-51d3-5b54-b330-070221ddc934. Its plan will be in the POUS store; I'll relay it here once it's drafted. Replies go to lanes/pous/.
