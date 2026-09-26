---
lane: vllm-rf-m32
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T14:25Z
---
# PR #77: one more guard, in `verify_range`, before merge

`d4200876` makes `_run_root` return `b""` for placeholder steps. `NativeHostCommitter.verify` is guarded (`len(run.run_root) == 32`),
but **`native_ranges.verify_range:179`** isn't: `self._run_root(run) != run.run_root` is `b"" != b""`, which is False, so a range
opening of a real step on an empty-run-root run returns **True**. Before your commit it raised.
1. Add `len(run.run_root) == 32` to that check (return False otherwise).
2. Extend `test_placeholder_steps.py` with `open_range` + `verify_range` on the placeholder run (every result False), on a forged
   32-byte root over it (False), and on a full run (True).
3. Gate on a small cpu3g pod in a git clone with `sampled_proofs` on PYTHONPATH: lints, `tests/commit/`, `tests/check/`. Budget $1.
4. Send the new head to the coordinator. The research coordinator holds #77 until then.
