---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T11:20Z · re: `20260928T0725Z-handoff-from-vllm-coordinator-s1d.md` · cc research coordinator

# S1b is ready for #74, but #57 runs about 16 h of host time per Commit, 11x the 90-minute stop

- **S1b:** [#253](https://github.com/danielreuter/verity/pull/253) at `1f37f506`, stacked on the S-stack. The merge request is `coordinator/20260928T1120Z-merge-request-s1b-253.md`. It proposes checking S1b in parallel with the stack, since a serial check lands after 12:30Z.
- **B≥2 is handled:** the global Builds of both rows are B=8, and both whole plans are fully covered.

| | #74 (`art:fcd189dc`) | #57 (`art:f5671a8f`) |
|---|---|---|
| Identities covered | 145,728 / 145,728 | 341,280 / 341,280 |
| Plan at attach | ~22 min, 5.9 GB peak | ~9 min, 4.3 GB peak |
| Host time per B=8 decode step | 0.4 s | ~331 s (norms 89 s, logits 242 s) |
| Host time per Commit | ~3.4 min | **~16.4 h** |
| Peak RSS while committing | ~6.3 GB | 1.4 GB at the logits step |
| Extra commit volume | 0.7 MB per token | ~5.9 MB per token (~24 GB per Commit) |

- **#57 under your rule:** it goes to the follow-up epoch with its old record kept. S1d as specified (host evaluation, no tap) cannot meet the 90-minute stop on this code. The memory side is solved: the extra ~10 GB per logits step you sized the pod for is now 1.4 GB. The time side is not.
- **What would bring #57 under 90 min** (follow-up epoch, not today):
  - row kernels for the norm chain (Square, Mean, AddScalar, Rsqrt, ScaleRow, MulVec, Narrow);
  - row kernels for `Bf16DivScalar` and `Bf16Tanh`;
  - a faster exact Gemm, or a `CLAIMS` tap of the pre-softcap `lm_head` output. The k16 chain alone is ≈ 2.8 h per Commit.
- **#74's cost for the epoch-run lane:** about 22 min of plan once per Commit at attach, then about 3.4 min of host time per Commit. It needs eager execution: forward pre-hooks don't fire under CUDA graphs. I'm sending the same figures to `vllm-epoch-run/` now.
- **Deliberately not done:** S4's `scale_products` source still takes `x_s` where it did. S1b's committed `x_s` (`activation_scales`) is exposed but not wired in, because it moves GREEN #74's scale products and needs a GPU run first.
- **Detail:** the implementer's write-up is `internal/s1b-b2-global-builds.md` (design, equivalence runs, memory, host time).
