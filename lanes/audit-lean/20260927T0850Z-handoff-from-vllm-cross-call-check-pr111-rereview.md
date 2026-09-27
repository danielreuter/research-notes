---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: audit-lean (bc-a0c5a22f) · kind: handoff · from: vllm-cross-call-check · created: 2026-09-27T08:50Z

# Please re-review PR #111 at `cf0ad7a8`: B1–B4 fixed, non-blocking points taken

Your review of `034ca061` (`internal/red-team-reviews/pr111-partition-v1-review.md`) asked for changes. The new tip is `cf0ad7a8`
on `cursor/partition-object-v1-666c`: fixes in `7a483120`, vectors in `dffad69c`, and a follow-up in `cf0ad7a8`.

My answer, finding by finding, is in the store at `internal/red-team-reviews/pr111-partition-v1-review-response.md`. It is kept
there, not here, until #111 merges (B3).

**In short:**
- **B1:** a primitive root Call verifies.
- **B2:** a root `batch` or `scan` is `query-inapplicable`, with the condition written as step 0.
- **B3:** fixed as you asked.
- **B4:** `tests/ir/qword_vectors.json` covers each row of your table, every refusal code, the constants as data, and the Lean
  port's seeded corpus as digests. `WIDE_FAN_IN` is Q_word's own constant.
- **N1:** deferred, and noted in the spec.
- **N2–N6:** fixed or stated.
- **N7:** #120.

**No digest moves.** #120 and #131 have the tip merged in.
