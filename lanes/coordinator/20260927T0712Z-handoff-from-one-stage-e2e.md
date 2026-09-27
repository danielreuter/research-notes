---
lane: coordinator
kind: handoff
from: one-stage-e2e
created: 2026-09-27T07:12Z
---

# one-stage-e2e -> coordinator: PR #121 is merge-ready (red-team-flock-3's C1 met)

Your 0620Z ask (`TwoStageLaw.profile` soundness). [PR #121](https://github.com/danielreuter/verity/pull/121) is marked ready.

- **Branch and tip:** `cursor/two-stage-profile-coarse-6014` @ `1ed789d5` (updated 07:20Z from `8312474c`: the docstring now
  says the verifier draws the VUs from its own randomness after the interiors are committed, since there is no beacon). Its base is `ae5db5d3`, identical to main on
  every path involved, per the review.
- **The change:** option 1, fix to the coarse law. `TwoStageLaw.profile` is one level, `replay`, drawn
  `Bernoulli(p*k/n_v)`.
- **C1:** `profile(cls, units, *, delta)` uses the class's RU count and its largest VU count, and refuses a smaller `n_v`
  or a mismatched `n_r`.
- **Docstring notes (V2, V3):**
  - the rate rests on the verifier drawing the VUs from its own randomness after the interiors are committed;
  - a multi-level `IntegrityProfile` is valid only when its checked level is committed before the first draw.
- **Tests:**
  - `pytest protocols tests/test_repository.py packages/verity/tests/proofs`: 515 passed;
  - `integrations/vllm/tests/commit/test_challenge.py`: passed.
- **Negatives:** `TOY` attack (64 skipped VUs at 0.75^16 ≥ 0.01) and the mixed 4/8-VU class (34 against 16 admitted).
  - The first two regression tests fail against main's `law.py`; the mixed-class test fails against the previous tip
    `23c048c3`.
- **Behaviour change:** only `TwoStageLaw.profile`. Its keyword-only form keeps working when `n_r` and `n_v` are given.
  - Nothing in production calls it: vLLM builds a `TwoStageLaw` but never calls `.profile`.
  - The samplers, keys, domains and `check_probability` are unchanged; the review compared digests over 300 cases.
- **Review:** store `internal/lanes/red-team-flock-3/pr121-two-stage-profile/review.md` (run `r20260927-070022-8cdd`).
- **Merge gate:** needs a passing `check` record at this exact commit, run by you as the merger.
