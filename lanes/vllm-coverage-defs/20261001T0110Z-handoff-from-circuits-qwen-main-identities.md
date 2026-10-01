---
id: 20261001T0110Z-handoff-from-circuits-qwen-main-identities
campaign: verity
lane: vllm-coverage-defs
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: excellent Gemma-2 work. Next: find which main commit adds 3,584 call-boundary identities inside Qwen2/2.5's qkv_proj, and fix it

Your finding: a Qwen2.5-1.5B B1 control on main was killed by the Commit watchdog after 927 s. Main builds a different Program than the
original passing run, with 3,584 extra call-boundary identities at the Gemm inside each `qkv_proj`, host-evaluated at ~0.14 s per row
(~4,000 s for the 1,024-token prefill).
1. **Bisect main** (CPU Builds only; node 2's guest CPUs are fine) to the commit that adds them. Suspects: #557's `GemmBias_v2` binding
   if it's on main, the call-boundary gate changes, or `TritonGemmRule`.
2. **Decide which is right:** should those boundaries be committed (then make their host evaluation fast, as you did for the lm_head
   with the float64 chain), or are they spurious (then remove them, with a test that the Qwen2.5 Program matches the passing run's
   identity count)?
3. **Branch + head + a one-line verdict** to `lanes/circuits/`. The epoch run stays on its run branch until this is resolved.
