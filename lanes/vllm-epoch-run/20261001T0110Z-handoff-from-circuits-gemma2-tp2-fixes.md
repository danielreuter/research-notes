---
id: 20261001T0110Z-handoff-from-circuits-gemma2-tp2-fixes
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: merge the Gemma-2 fixes (#619–#624) and the TP2 token-budget fix pre-merge; release Gemma-2 and TP2 as breadth subsets; stay off main

1. **Merge into `cursor/coverage-v1-2622`, pre-merge:** #619, #620, #621, #622, #623, #624 (Gemma-2: k06 and m006 pass 460/460; the
   m005/m007 hangs were slow host code), and `cursor/tp2-commit-token-budget-ec1f` @ `b642a4a4b` (the TP2 crash was the engine's
   2048-token budget versus `max_model_len`; Qwen3-4B TP2 then passes 460/460, `r20261001-004454-795e`).
2. **Gemma-2 subset** (owner-approved as a new path once fixed): B1, B8 and B32 at 256/32, greedy and top-p, plus k06/m006's shapes.
   Question: *does Gemma-2's softcap / norm chain replay bit-exact on sm_120?* The rest of the 39 stay held.
3. **TP2:** with the fix, the canary is any head_dim; then the approved subset, ~10 models × B1/B8 at 256/32 plus OLMoE and Qwen3-30B-A3B.
   Question: *do collectives, rank splits and the 2-rank manifest merge replay bit-exact?* Pacer limits as usual.
4. **Don't move the run to main:** main currently adds 3,584 call-boundary identities inside each Qwen2/2.5 `qkv_proj` (host-evaluated,
   Commits stall at the watchdog), and main lacks `sky/` and `workloads/` for dispatch. coverage-defs is finding the commit.
