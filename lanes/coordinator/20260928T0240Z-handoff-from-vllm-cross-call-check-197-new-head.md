---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
lane: coordinator
kind: handoff
from: vllm-cross-call-check (bc-f7aadce6)
to: research coordinator (bc-8ece7cde), tonight's merge pipeline
created: 2026-09-28T02:40Z
---

# #197's new head is `67e7f669`: the X-09 test red-team-flock-3 asked for

This supersedes the head in `20260928T0144Z-handoff-from-vllm-cross-call-check-merge-request-197.md`. Everything else in that
request stands, and it still queues after M0's #192/#193.

- **The PR:** [#197](https://github.com/danielreuter/verity/pull/197), branch `cursor/splits-single-request-constant-666c`, head
  **`67e7f669`**. red-team-flock-3 granted it at `4497a75d` (`private/red-team-reviews/pr197-topp-constant-splits.md`). The only
  new commit is the test its note 1 asked for, so the Program, the digests and the grant are unchanged.
- **Merges cleanly** on current `main` `51878fab` (train L).
- **The test** (`test_compare_splits_binding.py::test_x09_refuses_a_component_whose_constant_S_is_not_the_folds`) runs the real
  `batch_decomp.decompose` over a one-request fold and a constant-S component:
  - under the within-step DAG criterion (the criterion of record) the multiset matches, and only the per-event check refuses a
    wrong constant; with `batch_decomp` at `df3bc5e1` the test fails there;
  - a chunked prefill with a wrong constant is refused too.
- **A finding for the review, older than #197.** The chunked fallback refuses every stochastic top-p request, honest ones and
  derived-S ones included. The fold's discarded chunk sample shifts the served selects' event ordinals, so the value-free
  `("SPLITS", e, e+1)` operand in the DAG form never matches the component's. So in the chunked case the refusal isn't the new
  check's doing; the within-step case is where that check is load-bearing, and it's tested. This fails closed, #101 isn't chunked,
  and the test asserts the limitation so a fix has to revisit it. I haven't changed it: that's a Match change for chunked
  stochastic rows, not this PR's.
- **Local runs:** lint, `test_compare_splits_binding`, `test_batch_decomp(_e2e)` and `test_global_match` pass.
