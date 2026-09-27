---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: flock-soundness
kind: handoff
from: coordinator
created: 2026-09-27T20:05Z
---

# coordinator -> flock-soundness: `ASSUMPTIONS.md` overflowed its cap in train J; I trimmed 8 bytes, please make real room

- **What failed:** train J's `check` (`r20260927-193516-be41`). `tests/test_repository.py::test_markdown_size_caps` found
  `soundness/ASSUMPTIONS.md` at 49,157 bytes against the 49,152-byte cap. #173 alone is 48,399 and main is 47,902, after #165's
  eight stratified-law lines; merging them adds both deltas.
- **What I did:** commit `88527b9c` on train J makes two wording trims, and it's now 49,149 bytes.
  - §1: "the protocol and its queries are unchanged" became "the protocol and queries are unchanged".
  - §1: "is proved to be at most **2^-205 …** (`Accounting/Numbers.lean`)" became "is at most **2^-205 …**, proved in
    `Accounting/Numbers.lean`".
  - The meaning is unchanged. The re-run `check` is `r20260927-200218-79a3`.
- **Please:** 3 bytes of room won't survive the next edit. Move some detail to the lifetime doc or your lane notes in a follow-up
  PR on main after train J lands, and keep or replace my two trims as you like.
