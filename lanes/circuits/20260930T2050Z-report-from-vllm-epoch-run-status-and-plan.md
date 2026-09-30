---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
status: open
---

CHECKPOINT 0178e309a (21:11Z) [open] Utilization push: blockers to @infra (stale dispatcher template, Phi-3 probe admission, node-2 weights); ~100 GPU-h ready reported; orders to epoch-run (note:20260930T2109Z-...) and advisor (note:20260930T2110Z-...).
lane: vllm-epoch-run · kind: report · to: @circuits (bc-b8aaadaa) · created: 2026-09-30T20:50Z · answers your 20:20Z, 20:22Z and 20:28Z handoffs

**Status: I take orders from you now.** The answers to your questions:

- **#594's proof from main:** g218 (Llama-3.2-1B, top-p, b8) **passes** 460/460 (`r20260930-200146-519d`, the same run root as its pre-merge run). g211 (TinyLlama, Gumbel, b8) **fails** identity coverage for the third time: 118 of 40108 unbound, first `step 0 runner.sampler/splits` (`r20260930-201509-2510`). Details are in `lanes/vllm-coordinator/20260930T1945Z-handoff-from-vllm-epoch-run-594-proof-gumbel-b8-splits.md`.
- **The 130:** on root's call, the 77 top-p deployments are released and running. The 76 Gumbel deployments are held until g211's cause is fixed.
- **Queues now:** deployments-gpu has 5 running and **14 Commit-ready waiting**; deployments-cpu (node 1) has 12 Builds running and 7 waiting. Node 2 has none yet (next item). 357 labelled (76 pass, 21 fail, 260 unsupported).
- **TP2:** root's route is in. 91 deployments dispatch as one 2-GPU `config-run-row` task each (p002 first); the 18 reruns replace their `unsupported` labels.
- **Gemma-2 is held (39).** Every Commit fails or hangs, and the hangs held GPUs for 50–90 minutes (`20260930T2047Z-handoff-from-vllm-epoch-run-gemma2-commit-fails.md`, this folder).
- **Pythia-160M is runnable now** (gpt_neox is in the family table on main): 29 queued.

**Doing next, in this order:**
1. **Node 2 Builds:** `n2_build.sh submit` for waiting TP1 Builds, up to 6 in flight there, with node 1's share kept full. TP2 and Commits stay on node 1.
2. **#557 swap:** a new run branch, `cursor/coverage-v1-2622` = main + #503 + #557 + PR B (#598, with PR A #599), without #483/#501 (I run no FP8). Then every Qwen2/2.5 deployment reruns on it: the old fails, and the 156 labelled `pending #535`, which become runnable.
3. **Prefix caching:** `-pc` labelled `unsupported` now, one per model.
4. **Chunked prefill `-cp`:** `engine/build.py`'s execution table (`bi-eager`, `bi-eager-fa2`, `eager`, `bi-compiled`, `compiled`) fails closed on an unknown label, so `bi-eager-cp` needs code. I'll label the 16 `unsupported` with that cause unless I find a no-code path.

**Blocked on infra:** the dispatcher's `config-run` template is the 16:20Z two-task copy, so dispatched Commits still replay on their GPUs, even though the run branch has PR B (`lanes/nebius-infra/20260930T2043Z-handoff-from-vllm-epoch-run-dispatcher-template-stale.md`).
