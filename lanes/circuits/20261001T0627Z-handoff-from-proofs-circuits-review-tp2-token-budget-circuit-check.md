---
id: 20261001T0627Z-handoff-from-proofs-circuits-review-tp2-token-budget-circuit-check
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-circuits-review (bc-5abc75bd-2881-5699-b396-f5f4d2fd8b2d)
---

# proofs-circuits-review: the TP2 token-budget fix (`b642a4a4b`) touches no circuit; `circuit-check --all` passes on it, and no target reads the file it changes

- **What changed:** `cursor/tp2-commit-token-budget-ec1f` @ `b642a4a4b` (base main `e5b720899`; its head hasn't moved).
  - It changes `integrations/vllm/verity_vllm/pipeline/row_records.py`, where `tp_shape` caps the engine's `max_num_batched_tokens`.
  - It adds `tests/pipeline/test_tp_token_budget.py`.
  - That is an engine argument, not a Definition, a subcircuit template or a Boolean lowering, so AGENTS.md requires no
    circuit-check for it. I ran `--all` anyway, as ordered.
- **Where it lives now:** you folded it into `cursor/commit-gpu-phases-8c79` as `b4eea7ff2`. That commit has the same patch
  (`git patch-id --stable` is equal), so this report covers it too.
- **Result:** I ran `circuit-check --all` on this VM (CPU only).
  - **Pass:** 1145 targets, 0 new failures, 1 known, rc 0. The known failure is
    `partition/gate-recomputed ScaledMmFp8Block_v1{K=128,N=128,G=128}`.
  - **Warnings:** dead-gates/ir 145002 over 229 targets and redundant-gates/ir 21845 over 53, the same as main `4860d817a`. Also
    redundant-gates/boolean 178669 over 184; I have no count from main to compare it with.
- **Reach:** zero targets read the changed file. A cold run traced 815 targets. The other 330 went untraced because they compiled
  the fa2 numerics library. A second run on a warm cache reused the 815 and traced the 330, so every target's reads are now
  recorded. None of the 1145 reads any file under `integrations/vllm/verity_vllm/pipeline/` or `integrations/vllm/tests/pipeline/`.
- **Evidence:** both reports, their logs and the reach scan are `art:72db1abc9d6a155e607c3f35043d92eb19c8590aa9d7a641a9eaf91fbd36397d`
  (preserved).
  - It is not a `research run` Attempt. The queue refuses this tree because its `research` package predates the queue, and merging
    main in would have changed the tree under test.
