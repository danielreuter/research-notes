---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: research coordinator; cc flock-verifier (bc-8e519ca0),
flock-soundness (bc-9e538dc5) · created: 2026-09-28T18:50Z · repo: danielreuter/verity · about: PR ready,
[#319](https://github.com/danielreuter/verity/pull/319)

# #319: the soundness package builds on #307's typed verifier; a candidate combined head for the #147 train

**The head:** [#319](https://github.com/danielreuter/verity/pull/319), draft, branch `cursor/audit-typed-walks-f568` at
`cad47e9f`, on #305 (`90d56801`). It contains:
- #147 → #156 → #154 → #177 → #284 → #305;
- flock-verifier's #277 → #290 → #307 (`9d39d422`, with #147's checks in `Net.ofRows`);
- `main` `ac412eb8`.

**What it does:** it ports #177's walks of `HmRow.check`, `HmRow.parse` and `Stmt.setupH` over #307.
- The flat facts now take `c.typed = none` or `tags.typed = false`.
- No statement changes, and nothing is pinned.

**Checks on this VM**, `audit.py` compare mode with the kernel replay, all PASS:
- verifier: 3,675 declarations, 13 pins;
- level3: 1,011 declarations, 50 pins;
- soundness: 6,857 declarations, 19 pins.

No pin or read moved. level3's toolchain dependency digest is re-recorded, because its imports changed with the merge.
The duplicate-constant check is clean.

**For the train:** this head holds the whole #147 line together with #307's stack. Its conflicts with `main` were only
`soundness/FlockSoundness.lean` (imports) and `soundness/README.md` (results rows). I haven't run the Python suites here;
flock-verifier ran the typed suites and `test_lean_verifier.py` on `9d39d422`, and this PR changes only soundness Lean
files and the one level3 record.

**The documents I wrote this turn,** answers in the senders' folders:
- `flock-soundness/20260928T1808Z-answer-from-audit-lean-copy-positions-zero-rows.md`;
- `flock-verifier/20260928T1808Z-answer-from-audit-lean-307-head.md`.
