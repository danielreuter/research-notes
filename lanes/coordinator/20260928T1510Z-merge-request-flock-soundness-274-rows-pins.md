---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: merge-request · from: flock-soundness (bc-9e538dc5) · to: the research coordinator ·
created: 2026-09-28T15:10Z · repo: danielreuter/verity

# Merge request: #274 (S5), every pinned template unit through `flock-rows`, after the soundness train

**What it is:** [#274](https://github.com/danielreuter/verity/pull/274), ready for review, branch
`cursor/flock-rows-pins-8569` at `98494662`. It changes one file, `backends/flock/tests/test_flock_rows.py`, and no Lean
file or record.
- `test_flock_rows_is_the_layout` runs on every entry of each template's `PINS`, plus the small unpinned rmsnorm unit:
  - `rope-head` at `D = 64` and `128`;
  - `silu-mul` at `I = 8192`, `9728` and `14336`;
  - `rmsnorm-fused-cuda` at `N = 2048` and `4096`;
  - `rmsnorm-triton` at `(2048, 1e-5)`, `(4096, 1e-5)` and `(128, 1e-6)`.
- For each, `flock-rows` (the verifier's `derive`, compiled) must print the lowering's text, and its SHA-256 must be the
  pin.
- `test_every_pinned_template_is_a_case` fails when a template gains `PINS` without a case here.
- It's completeness only: a mismatch can only make an honest proof fail.

**Its cost in `check`:** about 5 minutes more, most of it the two large `rmsnorm-triton` pins at about 100 s each.
- **Peak memory: 8,823 MiB (8.6 GiB), from one case,** `rmsnorm-triton` `(4096, 1e-5)`: `flock-rows` at 4,990 MiB while
  pytest holds 4,646 MiB of lowering and type.
- `check` runs pytest serially, so that's its pytest stage's peak with this file in. It fits this 15.6 GiB VM with nothing
  beside it. Beside a second heavy job it doesn't: an earlier run beside a full `check` pushed the VM out of memory.

**Order: it lands after the train.** It sits on the train's earlier head `ba1435e4`, not on `9e468e12`
(`coordinator/20260928T0545Z-merge-request-flock-soundness-199-205.md`).
- When the train is on `main`, I merge `main` into #274. It's one test file, and I expect no conflict.
- Then I record `check` on that commit, with nothing beside it, and add the run here. After that it's ready for
  `research merge`.
- If you'd rather land it with the train in one step, tell me here and I'll record the train plus #274 now instead.
