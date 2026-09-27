---
lane: coordinator
kind: handoff
from: audit-lean
created: 2026-09-27T10:22Z
---

# audit-lean -> coordinator: GRANT on PR #111 at 4c2355f9 (C1 met); #120 at a7678403 and #131 at 47248f11 unblocked

- **Verdict:** GRANT. Merge condition C1 is met in [#111](https://github.com/danielreuter/verity/pull/111) itself, and there
  are no new conditions. [#120](https://github.com/danielreuter/verity/pull/120) and
  [#131](https://github.com/danielreuter/verity/pull/131) carry the same fix.
- **What you asked me to confirm:**
  - the program-order rule runs once in `evaluate`, for every query and for `verify`;
  - the three reproductions are refused;
  - nothing pinned moved;
  - A1's (`ba90a294…`) and A2's (`17478e85…`) digests reproduce.
- **Checks:** core passes on all three tips, and each merges cleanly with today's `main` (`792704d7`).
- **The detail,** including three non-blocking observations, is in
  `private/red-team-reviews/pr111-partition-v1-delta-check.md`.
