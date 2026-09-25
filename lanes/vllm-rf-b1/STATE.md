---
id: vllm-rf-b1/state
lane: vllm-rf-b1
kind: state
updated: 2026-09-25T09:20Z
---
# b1 (evaluator kernels and replay): state

Coordinator: vLLM coordinator bc-ba6cec03. Agent bc-910bfdb6. Budget $45 of pod spend.
Worktree `~/projects/verity-wt/rf-b1`, branch `lane/vllm-rf-b1`.
a4 base: 10996616

## Done
- worktree created at 10996616.
- read: WAVE2_BRIEF, SYNTHESIS (smell 1, T1, P3, 5.1/5.2, B1, decisions), core verity.evaluation, check/replay/sampled_replay.py, program/kernels/twins.py, replay.py, f1/f3/a4 notes.
- bf3bdbec `derived_rows.py` moves `program/registry/` -> `program/kernels/` (git mv + import lines + allowlist paths). **c2: two import lines in your files changed** (`program/registry/ref_prims.py:850`, `program/registry/sampling_rows.py:34`), nothing else in `program/registry/`.

## Plan
1. done (derived_rows move).
2. `program/kernels/rows.py`: the sampled-replay row evaluators moved out of sampled_replay, one function per family, `Declined` carries today's exact "not evaluated" text; registered with core `register_kernel` (kernel "numpy") against the family Definitions.
3. twins -> core kernels (kernel "twin"); core `self_check` replaces twins.self_check/check_instances/gate_words and the Twin protocol. Test: every registered (kernel, Definition) pair self-checks.
4. `check/replay/challenge.py`: today's seed forms (root, challenge, prover) + generator constructors; RNG_OWNERS; drivers (replay tiers, stoch_recompute, compiled_kernel_check, vu_query, difftest) use it. No seed derivation changes.
5. Split sampled_replay.py into sample / open / evaluate / compare / c2 driver / linkage; delete it; repoint importers (import lines only in other lanes' files).
6. Pods: gate (b) head vs base, gate (a) T0+T1 on cpu3m 512 GB, GPU #101, #67 PAIRS=1, #70 if rank path changes.

## Running
- pod `vyv-rf-b1-cpu` (RunPod cei1t48zvrcnzu, cpu3g 32 vCPU, $1.28/h, created 08:47Z): shipping base 10996616 (`git archive`) to /workspace/base, then pod_bootstrap.sh. First sync attempt failed (tarred the worktree mid-move).

## Next
- rows.py (step 2), then base gate (b) on the pod while coding.

## Open questions
- difftest lives in properties/admission.py (b2v's `properties/`): will keep hunks to the rng call + evaluate call + import lines.

## Found, not fixed
- replay row evaluators differ from their Definitions on edge words (twins document the Definition's behaviour): TokenSelect_v1 with a NaN logits[0] (Definition -> 0; row kernel -> argmax of the rest); BiasAdd_v1 NaN result word (Definition 0x7FC0; row kernel 0x7FFF); Gemm_v1 / MoeExpertGemm(W)_v1 / padded MoE blocks evaluate lanes with a non-finite operand or accumulator with the vectorised twin instead of declining. Not reachable on finite committed words; kept as is (no per-VU result may move), the batch kernel declines them.
