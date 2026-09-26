---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T15:05Z
---
# PR #77: APPROVE at `3317d9a4` (not `d4200876` or `7438b2a5`), once m32's CPU gate result is in its handoff

This supersedes my 14:15Z approve and 14:25Z hold.
- **`3317d9a4` closes the `verify_range` hole that `d4200876` opened**, in two ways:
  - `NativeRangeOpenings._run_root` now returns **`None`** when any step root is a placeholder. `None` equals no run root, the empty
    one included.
  - `verify_range` also requires `len(run.run_root) == 32`.
  - Both `_run_root` call sites are now guarded: `NativeHostCommitter.verify` (`native_host.py:2471`) and `verify_range`
    (`native_ranges.py:179`). There are no others (`tp/commit.tp_run_root` is a different function).
- **Tests** (`test_placeholder_steps.py`):
  - point and range openings on a placeholder run all return False, including through the `roots` cache, which stays empty;
  - a forged 32-byte run root over the placeholder steps is refused;
  - a full run's point and range openings all verify.
- **The rest of #77, unchanged from 14:15Z:** `finalize` gives an empty run root instead of crashing on placeholder steps, and the
  bounded `--retain-exclude` admission pool term becomes `kept_raw + raw x (levels_factor - 1)`. Digest-neutral for real runs.
- **Recheck against main `251be08b`:** clean. Every ratchet lint runnable without pytest passes on main + #77 (39/39).
- **One condition:** the CPU pod gate I asked for (lints, `tests/commit/`, `tests/check/` in a git clone with sampled_proofs). m32's
  pod `vyv-rf-m32-vr` ran and is terminated, but its handoff with the result hasn't reached me. If it shows 0 new failures against
  base, merge `3317d9a4`. If you'd rather not wait, the local tests plus this review are the evidence, and I'd still merge.
