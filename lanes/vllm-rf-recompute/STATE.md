# vllm-rf-recompute: STATE

New lane (no predecessor), agent bc-06147ba0, started 2026-09-27 02:56Z off `main` `3040ac1f`. Coordinator: vLLM coordinator (bc-ecac3029).
Brief: `$STORE/internal/lane-briefs/vllm-recompute.md`. Findings from `internal/lanes/vllm-coordinator/20260927T0300Z-handoff-from-vllm-cross-call-check-cross-call.md`.

## Branches
- #74 FP8: `cursor/vllm-rf-recompute-fp8-cbba` @ `df13126f`, PR #106 (draft). Pushed.
- #57 Gemma: `cursor/vllm-rf-recompute-gemma-cbba` @ `7aeffc5d`. NOT pushed: the VM's GitHub App token is invalid since about 03:30Z.
  Bundle: `evidence/gemma-7aeffc5d.bundle`.

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
  - the recorded #57 request Programs rewritten as `once` builds them: `cross_call` LP31_T52 5,460 Calls / 12,579,840 gates -> 0;
    LP1024_T18 1,890 / 4,354,560 -> 0 (the others running).

## Running
- VM tmux `r57-cross`: `cross_call` on all 8 #57 request Programs, recorded vs `once` rewrite (`$HOME/ev/r57_all.log`).

## Next
- On approval (estimate `internal/lanes/vllm-coordinator/20260927T0335Z-handoff-from-vllm-rf-recompute.md`): CPU pod `vyv-rf-recompute-cpu`,
  gate (b) base `3040ac1f` / FP8 `df13126f` / Gemma `7aeffc5d` (the Gemma torch tests run there first).
- Push the Gemma branch once the token is refreshed; open its PR.
- Merge-ready handoffs per PR.

## Open questions
- Whether the Gemma Build A/B on an L40S (one #57 request shape, selector off = recorded digest) is wanted.

## Found, not fixed
- A workload Program composes the row's request Programs, and each of them issues its own weight + 1 per norm even under `once`: 8 copies per
  norm on #57. `cross_call` checks each request Program on its own, so it does not see these. Committing the value "once per norm at load"
  for the row means GP-01 hoisting weight-only Calls into the workload's shared part.
- The eager Match fold issues a weight-only instance per engine step (`batch_decomp` SHARED). A row that declares `weight_only_calls = once`
  fails the Match by name until the fold issues it once too.
