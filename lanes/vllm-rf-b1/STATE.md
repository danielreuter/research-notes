---
id: vllm-rf-b1/state
lane: vllm-rf-b1
kind: state
updated: 2026-09-25T08:38Z
---
# b1 (evaluator kernels and replay): state

Coordinator: vLLM coordinator bc-ba6cec03. Agent bc-910bfdb6. Budget $45 of pod spend.
Worktree `~/projects/verity-wt/rf-b1`, branch `lane/vllm-rf-b1`.
a4 base: 10996616

## Done
- worktree created at 10996616.
- read: WAVE2_BRIEF, SYNTHESIS (smell 1, T1, P3, 5.1/5.2, B1, decisions), core verity.evaluation, check/replay/sampled_replay.py, program/kernels/twins.py, replay.py, f1/f3/a4 notes.

## Plan (draft)
1. `program/kernels/rows.py` (+ split): the sampled-replay row evaluators moved out of sampled_replay, one function per family, `Declined` carries today's exact "not evaluated" text.
2. Register rows (kernel "numpy") and twins (kernel "native") with core `register_kernel` against their Definitions; core `self_check` replaces twins.self_check/check_instances/gate_words and the Twin protocol. Test: every registered (kernel, Definition) pair self-checks.
3. `derived_rows.py` moves registry -> kernels (pure git mv + import lines; tell c2).
4. `check/replay/challenge.py`: today's seed forms (root, challenge, prover) + generator constructors; RNG_OWNERS; drivers (replay tiers, stoch_recompute, compiled_kernel_check, vu_query, difftest) use it. No seed derivation changes.
5. Split sampled_replay.py into sample / open / evaluate / compare / c2 driver / linkage; delete it; repoint importers (import lines only in other lanes' files).
6. Pods: gate (b) head vs base, gate (a) T0+T1 on cpu3m 512 GB, GPU #101, #67 PAIRS=1, #70 if rank path changes.

## Running
- nothing.

## Next
- finish reading difftest (properties/admission.py), compiled_kernel_check, stoch_recompute, Definitions' signatures; start step 1.

## Open questions
- difftest lives in properties/admission.py (b2v's `properties/`): will keep hunks to the rng call + import line.

## Found, not fixed
- none yet
