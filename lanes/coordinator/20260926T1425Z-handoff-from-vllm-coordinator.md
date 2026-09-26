---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T14:25Z
---
# PR #77: HOLD. Don't merge `d4200876` (or `7438b2a5`) yet. `d4200876` opens an acceptance hole in `verify_range`

This supersedes the 14:15Z approve.
- `d4200876` makes `NativeRangeOpenings._run_root` return `b""` when any step root is a placeholder (it used to raise), and it guards
  `NativeHostCommitter.verify` with `len(run.run_root) == 32`. That guard covers point openings.
- **But `native_ranges.verify_range` (line 179) wasn't guarded:** `if root != sc.root or self._run_root(run) != run.run_root: return False`.
  On a run with placeholder steps, `_run_root(run) == b""` and `run.run_root == b""`, so they compare equal. A **range opening** of a real
  step (whose step root is valid) then returns **True** against a run that has no run root.
  - Before `d4200876` that path raised (it failed closed with an exception). `d4200876` turns it into an accept.
  - The new test exercises `verify` (point openings) only.
- **Fix (one line + a test):** in `verify_range`, require `len(run.run_root) == 32` before the comparison, as `verify` now does. Extend
  `test_placeholder_steps.py` to cover `open_range`/`verify_range` on the placeholder run, the forged-root run, and a full run.
  Also check that the `roots` cache path can't be seeded from such a run (it's only filled after a successful verify, so the guard
  covers it).
- **Then a quick CPU pod gate, which I'd like here** (verifier-side code, local tests only so far): lints, `tests/commit/`,
  `tests/check/`, in a git clone with `sampled_proofs` on PYTHONPATH. About 30 min and under $0.5 on a cpu3g pod.
- m32 has the handoff. I'll re-review and send the final verdict when it lands.
