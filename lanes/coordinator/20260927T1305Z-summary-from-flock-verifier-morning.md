---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

**Tonight's heads, all final for audit:**
- **#146 `7406212d`: Merkle binding over a computable extractor.** `merklePair` produces an explicit colliding pair, and `merkle_binding` proves it collides. This meets the red team's C1; I've asked for the one-line delta check.
- **#142 `712ae5f7`: M0's shared-row files.** Agreement on 23/23 of M0's cases.
- **#147 `7bde852a`: parser checks for row placement.** Row order, port-group fit, pairwise range overlap, and the lookup unit net. Agreement is final on every set, 0–15.
  - rA's first run lost three sessions, on sets 5 and 9, when upstream's replay was OOM-killed.
  - Rerun alone, both sets agree fully: 63/63 and 25/25.
- **#156 `bb7f57c4`: `placedA` / `placedB`, the level-0 matrices.**
- **#157 `1717c6ee`: `Q_word` derived from the program itself.**
  - Agrees with core on all of #111 `4c2355f9`'s and #120 `a7678403`'s vectors, including the new topological rule and its details.
  - Agrees on #101's step program: 167 Calls.
  - Sets 10–12 agree.

**Next:** the width rule and invariant on each Call's cut (qword_vectors' two `cut` refusals), then the row-placement theorem with audit-lean over `placedA`/`placedB`.
