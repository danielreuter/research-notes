---
id: 20260930T2209Z-handoff-from-console-progress-questions
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: console (bc-ddee017b), for Daniel, who is reading `verity/prover-overhead-{prefill,decode}` on the new console
---

# Proofs: three questions from Daniel about the M0 prover-overhead charts

Daniel asked "why are we proving such big tiles?" and how the data cuts. Short answers please, in `lanes/console/`:

1. **Coverage.** For a shape like 256x16384x2048, is the overhead the time to prove *every* output coordinate (all 256 × 16,384,
   in 4×4 tiles packed into m = 35 statements), or one statement's time scaled up by the statement count? Is Llama-3.2-1B's
   number the sum over its 16 layers plus lm_head?
2. **Why these shapes and this statement size.** Are 256x16384x2048 and 256x2048x8192 Llama-3.2-1B's MLP gate/up and down
   GEMMs (M = 256 tokens, decode M = 1)? Why m = 35 statements rather than smaller ones (fixed per-statement cost amortized?),
   and why 4×4 tiles?
3. **Overview vs Progress.** The Overview table (Sep 25 render: C-Flock 1.6e7–6.0e7×, datacenter chips, K = 1,536, N ÷ P) and M0's
   4.8e6× (RTX PRO 6000, torch bf16 linear baseline) measure different things. Is there a single number that should replace
   C-Flock's cells, or should they stay separate?

Also: is M0's line still moving (#22 was waiting on Kueue at 20:51Z), and which vCPU basis (18, 24 or 48 per GPU) do v3's
numbers use now?
