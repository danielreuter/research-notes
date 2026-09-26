---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-26T14:40Z
---
# PR #77 new head for your final verdict: `3317d9a4` (answers 20260926T1425Z-handoff-from-vllm-coordinator.md)

PR: https://github.com/danielreuter/verity/pull/77, branch `lane/vllm-rf-bounded-finalize`, base origin/main c20bab70.

**The `verify_range` gap is closed (`3317d9a4`):**
- `native_ranges._run_root` now returns **None** over a placeholder step, which equals no run root, the empty one included.
- `verify_range` requires a 32-byte run root, like `verify`.

**Test** `test_a_run_without_a_run_root_verifies_no_range_opening`:
- Range openings of real steps (0: leaves 0-3, 2: leaves 16-20) on the placeholder run all verify False. So do the same openings against a
  forged 32-byte run root, and through the per-step `roots` cache, which stays empty.
- A full run's ranges still verify.
- It fails on d4200876 (AssertionError: a range verified).

**Other verifier paths checked:**
- `native_host.verify` and `native_ranges.verify_range` are the only verifiers that recompute the run root and compare it with the run's.
- `merkle.verify_opening` / `verify_range_opening` and `hidden_stream.verify_*` compare a folded 32-byte digest with the root they are
  given (`merkle.verify_opening` also checks the root's length), so an empty root can't match there.
- `padding_steps.py:512` is a record-side padded-map builder, not a verifier; it raises on a placeholder root, which fails closed.

**Gate** r20260926-143306-9d9f (git clone, `verity_sampled_proofs` importable, CPU-only, PRESERVED; `evidence/vr-gate-results.txt`):
- Lints at 3317d9a4: rc 0.
- tests/commit + tests/check: head 949 passed / 43 skipped / 5 xfailed, base c20bab70 945 / 43 / 5, 0 failed on either side. +4 = the
  placeholder tests.

**Pods and spend:** vyv-rf-m32-vr (an L4 whose sshd never came up) and vyv-rf-m32-vr2 (an RTX 4090 host with the GPU hidden; no CPU
stock) are both terminated, the latter at 14:38Z. About $0.25 this round. Lane total about $10.
