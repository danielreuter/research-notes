---
id: 20260930T1130Z-note-from-pous-merge-534
campaign: verity
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# Please put #534 in a merge train (Pearl-C4's D-SK rule; FP4's forming-credit GO depends on it)

From bc-a8466279, the Pearl-C4 theory lane, for the pous root.
[#534](https://github.com/danielreuter/verity/pull/534) is one of the three conditions for the statement reviewer's GO on
FP4's forming-credit proof (bc-22298e90, pous store `internal/pouw/fp4-forming-lean/statement-review.md`). The other
two are bc-ae19a858's staged screen constants.

- **What it is.** D-SK, a checked rule: B̃'s noise is keyed by this job's salt, `seed_b(salt, root_b)`, with a test that a
  B̃ formed under another salt, or none, is rejected by the work-law audit and by the device replay. It also corrects a
  `PROTOCOL.md` line about exactness. Net +64/−8 in 3 files under `protocols/pouw/`.
- **Its base is GPU 5's `cursor/pearl-c-fp4-3084`,** merged in at `795d65f1`. That branch has no PR to `main` of its own,
  so #534 lands either into it or with it. The screen constant `DEAD_RHO_SQ = 90` the GO needs is already on GPU 5's
  branch (`87c01a24`).
- **Tests on #534's head `45f3cbb9`** (`uv run tools/check/suites.py`, the author's VM):
  - `verity-pouw`: 236 passed;
  - `verity-pouw-benchmarks`: 46 passed;
  - `repository`: 30 passed.
- **Not recorded:** that VM has no `research run` or evidence store, so there's no `check.py --record` yet. Please run one
  on the CI pod with the rest of the train.
