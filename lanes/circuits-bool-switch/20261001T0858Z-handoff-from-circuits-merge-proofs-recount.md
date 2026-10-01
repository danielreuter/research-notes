---
id: 20261001T0858Z-handoff-from-circuits-merge-proofs-recount
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (2:00 AM PDT): proofs' branches are published. Merge them, re-count purity, and run the 460-unit check as soon as it hits 0

- **`cursor/proofs-ir-attn-95d4`** @ `33e10236c`: `Gemm_v3{K,N,DOT}` (Gemm_v2's body on bits), `Attention_v6`, `AttentionHead_v6` and `AttnBlock_v6`
  (FA2 on bits), `Fa2InvSum_v2`, plus the E4M3, E5M2 and NVFP4/MXFP4 steps on bits.
- **`cursor/proofs-mufu-bool-95d4`** @ `3bf1b6d02`: the MUFU Boolean Definitions, bound in circuit-check with their ANDs pinned.
- Merge both into `cursor/bool-switch-8c79` along with the latest family heads (elementwise `35ca52a66`, casts `35bcb4855`, rope `e9fdc3737`,
  silu `59b134051`, norms `8e0e73ba7`, sampling `206a547a5`). Then re-run `boolean-purity` on cov-k01-10 and report the count and the
  remaining gaps in `lanes/circuits/`. Your 12:29 AM count was 36 of 54, with Attention, Gemm and the two RMSNorms as the gaps.
- At purity 0, run the 460-unit hot-swap re-verification on an existing SmolLM2-135M B1 greedy Commit's kept leaves.
- The integration PR still opens by 5:00 AM PDT with whatever is green. Keep proofs' commits as their own commits so their owners can review
  them.
