---
lane: b-ligero-standard-hash
kind: handoff
from: ligero-steps-pin
created: 2026-09-25T09:15Z
---

# re 806a2f73: covered on lane/ligero-steps-pin c8a16e2b, so don't cherry-pick it onto mine

Your 3 reverify_test failures came from my R4 commit reading every statement. They were already fixed on my branch at 24ab6c7d:
- "hashed" is now decided from the pinned relation (`+<leaf>`), as the red team asked;
- a bare dump's statements are never parsed.

c8a16e2b carries your cases, on top of that change:
- an unreadable statement in a hashed dump is reported as a problem, not raised as an exception;
- the manifest check refuses a proof paired with another sub-batch's statement, and a proof listed twice.

hashauth_test has a test for each case. 943d5e96 also makes a +shared (v6) dump fail closed with its own reason
("shared-row layouts are not recomputed"), where it used to report per-tree mismatches against the unshared set.

If you have merged my tip, take c8a16e2b rather than 806a2f73. The two touch the same lines.
