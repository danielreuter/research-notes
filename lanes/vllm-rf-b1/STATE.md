---
id: vllm-rf-b1/state
lane: vllm-rf-b1
kind: state
updated: 2026-09-25T09:41Z
---
# b1 (evaluator kernels and replay): state

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

Coordinator: vLLM coordinator bc-ba6cec03. Agent bc-910bfdb6. Budget $45 of pod spend.
Worktree `~/projects/verity-wt/rf-b1`, branch `lane/vllm-rf-b1`.
a4 base: 10996616

## Done
- worktree created at 10996616.
- read: WAVE2_BRIEF, SYNTHESIS (smell 1, T1, P3, 5.1/5.2, B1, decisions), core verity.evaluation, check/replay/sampled_replay.py, program/kernels/twins.py, replay.py, f1/f3/a4 notes.
- bf3bdbec `derived_rows.py` moves `program/registry/` -> `program/kernels/` (git mv + import lines + allowlist paths). **c2: two import lines in your files changed** (`program/registry/ref_prims.py:850`, `program/registry/sampling_rows.py:34`), nothing else in `program/registry/`.

- a6613e94 (pushed) `program/kernels/rows.py` (the sampled-replay evaluator ladder as 22 per-family row kernels, registered with core `register_kernel` under kernel "rows", samplers + small check specialisations) and `program/kernels/kernel_registry.py` (instance form with decline reason, check targets, registered list: upstream candidates). `sampled_replay.evaluate` dispatches via `rows.ROWS`; `_Unresolved = Declined`. Gumbel kernel uses core `evaluate` (drops the check -> properties import, p05 entry deleted). Allowlists: p03/p05/by_name entries deleted, p08/p11 entries moved to rows.py, p10 SR 3099 -> 2614. Laptop lint scan 0 failing.

## Plan
1. done (derived_rows move).
2. done (a6613e94).
3. twins -> core kernels (kernel "twin"); core `self_check` replaces twins.self_check/check_instances/gate_words and the Twin protocol. Test: every registered (kernel, Definition) pair self-checks.
4. `check/replay/challenge.py`: today's seed forms (root, challenge, prover) + generator constructors; RNG_OWNERS; drivers (replay tiers, stoch_recompute, compiled_kernel_check, vu_query, difftest) use it. No seed derivation changes.
5. Split sampled_replay.py into sample / open / evaluate / compare / c2 driver / linkage; delete it; repoint importers (import lines only in other lanes' files).
6. Pods: gate (b) head vs base, gate (a) T0+T1 on cpu3m 512 GB, GPU #101, #67 PAIRS=1, #70 if rank path changes.

## Running
- pod `vyv-rf-b1-cpu` (RunPod cei1t48zvrcnzu, cpu3g 32 vCPU / 128 GB cgroup, $1.28/h, created 08:47Z), bootstrapped at base. Trees: /workspace/base (10996616), /workspace/head (a6613e94). Logs /workspace/b1/logs.
  - base gate (b) xdist `-n 12 --dist loadfile`, started 09:38Z (first launch at 09:06 never ran: empty gate_b.sh).
  - head touched tests (sampled_replay*, derived_rows*, twins, lints) `-n 6`, started 09:39Z.

## Next
- twins -> core kernels (step 3) while the pod runs; then read the touched-test results.

## Open questions
- difftest lives in properties/admission.py (b2v's `properties/`): will keep hunks to the rng call + evaluate call + import lines.

## Found, not fixed
- replay row evaluators differ from their Definitions on edge words (twins document the Definition's behaviour): TokenSelect_v1 with a NaN logits[0] (Definition -> 0; row kernel -> argmax of the rest); BiasAdd_v1 NaN result word (Definition 0x7FC0; row kernel 0x7FFF); Gemm_v1 / MoeExpertGemm(W)_v1 / padded MoE blocks evaluate lanes with a non-finite operand or accumulator with the vectorised twin instead of declining. Not reachable on finite committed words; kept as is (no per-VU result may move), the batch kernel declines them.
