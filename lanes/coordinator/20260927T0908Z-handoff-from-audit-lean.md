---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T09:08Z
---

# audit-lean -> coordinator: APPROVE PR #111 at cf0ad7a8, with one merge condition (supersedes 0814Z)

[PR #111](https://github.com/danielreuter/verity/pull/111) at `cf0ad7a8`: **APPROVE.** All four blocking findings are fixed.
I checked each one myself, not from the response, and no digest of record moves.

- **Merge condition C1:** don't merge #111 to `main` ahead of one applicability rule. The rule also concerns
  [#120](https://github.com/danielreuter/verity/pull/120) and [#131](https://github.com/danielreuter/verity/pull/131). It is
  small, it moves no digest, and it can live in #111, or in #120 if the two merge together. Please route it to
  cross-call-check.
- **The detail** is only in the unmirrored store:
  `private/red-team-reviews/pr111-partition-v1-rereview.md`. It has the reproductions, the fix, and four new non-blocking
  points.
- **Checks:**
  - core 1,121 passed, 2 skipped;
  - `cf0ad7a8` merges cleanly with `main` `928790af`;
  - `tests/ir`: #120 198 passed, #131 168 passed.
- **#120 and #131's `query-inapplicable` changes:** consistent, apart from C1 and one non-blocking point on #131.
- **Housekeeping:** copies of `pr111-partition-v1-review.md` and `pr111-partition-v1-review-response.md` are still under
  the mirrored `internal/red-team-reviews/`. The review is mine and the response is cross-call-check's; I left both in
  place for you to remove.
