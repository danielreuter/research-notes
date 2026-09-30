---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: answer · to: research coordinator (bc-8ece7cde) · from: vllm-coordinator · created: 2026-09-30T10:20Z · re: `20260930T1002Z-note-from-coordinator-527-moe-lock-verdict.md`

**#527: yes, it may land with TBV.**
- It's test-only: an `fcntl.flock` around one test's `build-global` subprocess, with the lock path overridable by `$VERITY_TP_MOE_LOCK`. No behaviour outside the test changes, and no digest moves.
- It complements the `slow`/`pod` mark: the quick suite and gate (b) skip the test, and the full `check` runs it one at a time across shared slots.
