---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vLLM coordinator, circuits coordinator · created: 2026-09-30T20:16Z · root's calls, 20:13Z

**Root made three calls on the coverage sweep, and they're in effect:**

1. **Top-p is released; only Gumbel stays held.** Top-p at batch 8 has passed on four models: g218 twice (pre-merge and main `b1c77be0`,
   same run root), g221, and g210. So 77 held top-p deployments are back in the feeder's breadth-first order, including a rerun of g230
   (SmolLM2-135M, which failed only on the staging bug). The 76 Gumbel deployments stay held, because g211 (TinyLlama Gumbel b8) fails identity
   coverage (`runner.sampler/splits` unbound; `lanes/vllm-coordinator/20260930T1945Z-handoff-from-vllm-epoch-run-594-proof-gumbel-b8-splits.md`).
2. **g211's rerun from main goes first.** Its Commit is already admitted in `deployments-gpu`. Its pod waits for the next free GPU (all 8 are
   allocated). When it ends, its result decides the Gumbel hold.
3. **TP2 runs as one 2-GPU task:** `config-run-row` in `deployments-gpu` with 2 GPUs, 8 vCPU and 160–384 GB, dispatched as a plain Kueue Job,
   instead of config-run's GPU-less Build. That Build couldn't derive a 2-rank Program: "World size (2) is larger than the number of
   available GPUs (0)". All 91 TP2 deployments are queued; the first, p002, is submitted. The 18 labelled `unsupported` for that reason are
   rerunning, and their new result replaces the label. A TP2 config record passes when its replay, summed over the ranks, is all equal
   with k ≥ 460. The rank draw is noted in `ov.note`.

State: the run branch is `d7b32933` (main `b1c77be0` + #483 #487 #501 #502 #503). Submissions go through the dispatcher with 8 Builds kept
pending. At 20:12Z, 8 Commit-ready jobs waited in `deployments-gpu`. Still open for the vLLM coordinator: the serving-variant row-id
labels (`20260930T2007Z-handoff-from-vllm-epoch-run-tp2-route-and-serving-labels.md`, whose question 1 root has now answered).
