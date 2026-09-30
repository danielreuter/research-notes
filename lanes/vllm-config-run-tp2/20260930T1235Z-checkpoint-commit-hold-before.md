---
id: 20260930T1235Z-checkpoint-commit-hold-before
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: report
status: checkpoint
repo: danielreuter/verity
origin: vllm-config-run-tp2
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---
Commit GPU hold, BEFORE (recorded cell cov-k01-10, SmolLM2-135M rtxpro6000 B1 i256 o32 greedy bi-eager, Kueue): stage.commit 436 s.
Dominant: warm-up instrumented 273.6 s (committer spans 1.3 s), engine build 78 s (64 s gap inside vLLM's profile run),
sampled replay 30 s; the committed runs 0.7 + 0.8 s. enforce_eager confirmed (compilation mode 0, cudagraph NONE).
Hypothesis: Kueue pods have no TRITON_CACHE_DIR (ephemeral ~/.triton), so batch-invariant Triton kernels are re-JITed per cell.
Probe (cold vs warm TRITON_CACHE_DIR, same Build dir r20260930-095004-bd5b) queued for after the quiet hour.
