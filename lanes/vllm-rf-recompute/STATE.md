# vllm-rf-recompute: STATE

New lane (no predecessor), agent bc-06147ba0, started 2026-09-27 02:56Z off `main` `3040ac1f`. Coordinator: vLLM coordinator (bc-ecac3029).
Brief: `$STORE/internal/lane-briefs/vllm-recompute.md`. Findings from `internal/lanes/vllm-coordinator/20260927T0300Z-handoff-from-vllm-cross-call-check-cross-call.md`.

## Branches
- #74 FP8: `cursor/vllm-rf-recompute-fp8-cbba` @ `df13126f`, PR #106 (draft). Pushed.
- #57 Gemma: `cursor/vllm-rf-recompute-gemma-cbba` @ `39e3b24c`, PR #109 (draft). `51692785` and `39e3b24c` fix two test spellings
  (the construction is unchanged since `7aeffc5d`).

## Done (CPU, lane VM; scripts in `$HOME/ev/` on the VM)
- FP8: `ScaledMmFp8BlockSharedScale_v1` + `SHARED_SCALE` (opt-in). Checks:
  - the same circuit as `ScaledMmFp8Block_v1` once the copies are merged;
  - bit-equal on 96 edge vectors;
  - #74 row `Q_word_v1` with #98's member check: recorded 4 violations / 113,639,803,200 recomputed gates, selector on 0 / 0; committed
    interior words +894,801,600 (6,160 per token per layer);
  - `cross_call` 0 on both constructions (LP73_T1);
  - the 229 Definitions of #74's and #57's Programs encode byte-identically on main and the branch.
- Gemma: `TargetProfile.weight_only_calls` (None = `per-forward` = the record; `once`) and `AddScalarRule` issuing a weight-only add once per
  weight leaves. Checks:
  - default `TargetProfile` digest unchanged (`86c255b3…` on both);
  - lints pass;
  - the 8 recorded #57 request Programs rewritten as `once` builds them: `cross_call` 44,520 duplicate Calls / 102,574,080 gates -> 0
    (`evidence/cross_r57_recorded_vs_once.jsonl`); committed `+ 1` output words 104,509,440 -> 1,935,360.

## Running
- Pod `vyv-rf-recompute-cpu` (RunPod `qlirspls2cbwyr`, cpu3g 16 vCPU, since 03:50Z, about $0.64/h). Gate (b):
  - base `r20260927-035144-299a`: done;
  - FP8 `r20260927-035231-167a`: done, jdiff rc 0;
  - Gemma `7aeffc5d` `r20260927-035257-150f`: superseded;
  - `r20260927-043810-c5cf`: stopped (TERM to its process group);
  - Gemma `39e3b24c` `r20260927-044046-03f9`: queued, check-back 05:10Z.
- FP8 merge-ready handoff sent: `internal/lanes/vllm-coordinator/20260927T0445Z-handoff-from-vllm-rf-recompute-fp8.md`.

## Next
- Gemma gate (b) jdiff, fetch, `data preserved`, terminate the pod, Gemma handoff, READY.md, FINAL.
- Merge-ready handoffs per PR, after gate (b).

## Open questions
- None. The L40S Build A/B is deferred to the re-baseline (coordinator, 03:49Z).

## Found, not fixed
- A workload Program composes the row's request Programs, and each of them issues its own weight + 1 per norm even under `once`: 8 copies per
  norm on #57. `cross_call` checks each request Program on its own, so it does not see these. Committing the value "once per norm at load"
  for the row means GP-01 hoisting weight-only Calls into the workload's shared part.
- The eager Match fold issues a weight-only instance per engine step (`batch_decomp` SHARED). A row that declares `weight_only_calls = once`
  fails the Match by name until the fold issues it once too.
