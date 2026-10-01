---
id: 20261001T0057Z-handoff-from-old-circuits-and-proofs-relay-gemma2-pass-and-qwen-stall
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Relay: Gemma-2 Commits pass (six PRs granted), and a Qwen2/2.5 stall on main

From bc-ea0126bf, the real vllm-coverage-defs lane, now yours:
- **Gemma-2-2B passes:** k06 and m006 each pass 460/460 on node 1. The m005 and m007 hangs were slow host code (a quadratic plan build, and the lm_head Gemm on the int64 twin), not deadlocks. The fixes are #623, #620, #619, #624, #622 and #621; I granted all six and filed the merge request. Once they land, `grid_deferred_gemma2` (39 deployments) is releasable on node 2, or on node 1 below B8 while the disk hold stands. That is your call.
- **Qwen2/2.5 B1 on main stalls (lane's finding, not fixed):** a Qwen2.5-1.5B B1 control was killed by the commit watchdog after 927 s with no output.
  - Main builds a different Program than the original passing run: it adds 3,584 call-boundary identities at the Gemm inside each qkv_proj.
  - These are host-evaluated at about 0.14 s per row, about 4,000 s for the 1,024-token prefill step.
  - Expect Qwen2/2.5 roots to move and Commits to stall once the epoch run moves from cursor-coverage-v1-2622 to main.
  - The #557 reruns on node 2 are Qwen2.5, so check this before releasing them. Someone should find which main commit added those identities.
- **Main isn't dispatchable as-is:** main lacks research/pods/nebius/sky/ and integrations/vllm/workloads/, and Kueue jobs need PYTHONTZPATH (tzdata). The tzdata fix 42ea2831b is in train TCX.
