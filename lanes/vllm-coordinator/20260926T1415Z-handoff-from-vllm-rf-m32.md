---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-26T14:15Z
---
# PR #77 follow-up done: a placeholder run can never pass. Branch head `d4200876` (MERGE-READY, replaces 7438b2a5)

PR: https://github.com/danielreuter/verity/pull/77 (not yet merged; the commit is added to its branch `lane/vllm-rf-bounded-finalize`).

- **Found while writing the test:** `native_host.verify` on an empty-run-root Commit did not return False. It crashed with
  `InvalidArtifact` in `native_ranges._run_root` (the recompute folds the placeholder step root). If only `_run_root` were made total,
  `b"" == b""` would have passed, so both parts are needed.
- **Fix (`d4200876`):**
  - `verify` requires a 32-byte run root.
  - `_run_root` returns `b""` over a placeholder step instead of raising.
  - Line-neutral in native_host.py (2572), digest-neutral.
- **Test** `test_a_run_without_a_run_root_verifies_no_opening`:
  - Every opening of the placeholder run verifies False, and a forged 32-byte run root over it is also rejected.
  - A normal run's openings still verify.
  - Without the fix it raised InvalidArtifact.
- **Run locally (CPU, the VM):**
  - The 3 placeholder tests pass.
  - The 13 existing `tests/commit/test_native_host_security.py` tests still pass (run through a stub, since pytest isn't installed on the VM).
  - No pod was used. The earlier pod gates cover 7438b2a5 (r20260926-133406-4d7c, r20260926-140124-74e1).
- **Spend:** $0 this task. Lane total about $9.7.
