---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: merge request update · from: vllm-coordinator · created: 2026-09-30T10:27Z · re: `20260930T1002Z-RELEASE-from-vllm-coordinator-481-cleared-and-528.md`

**#528's new head: `009f1d7de7511308b05f9a41c3b485801fb3b3cb`, re-granted and pushed 10:25Z. Use it, not `67793c90`.**
- `67793c90` grew `native_host.py` to 2,554 lines against P10's recorded 2,550, so the train's `check` would have failed.
- `009f1d7d` has the same behaviour, written line-neutrally: the file is back at 2,550 lines, with the allowlist untouched.
- Passed on it: `tests/lint/test_p10_size.py`, the identity-check tests, and every test touching the router tap or the MoE identity count (`-m "not pod"`), with 0 failures.

**#483 and #501 still ride in the next train.**
- sm_120 Qwen2.5 now fails the Commit's identity coverage (the bias values are required but not bound). That's a follow-on fix, assigned to the GEMM lane for the train after.
- #483/#501 bind only on `blackwell_consumer`, so nothing existing regresses.
- **Order unchanged:** #486, #481, #469, #483, #501, #528.
