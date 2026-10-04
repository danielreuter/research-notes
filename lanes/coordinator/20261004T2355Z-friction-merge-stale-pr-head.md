---
id: coordinator/20261004T2355Z-friction-merge-stale-pr-head
lane: coordinator
kind: friction
status: open
---

# `research merge` doesn't refuse a train tip whose PR head the PR has since moved past, or one a red-team finding supersedes

At 23:47Z on 4 Oct, the train tips 595fa006f, 6315ea54f and 582aa41f7 carried #1126 at 83c25a27b. The PR had since moved to 8216f316c, red-team-1126's fix for two false cache hits (note:proofs/20261004T2253Z-finding-red-team-1126). The pin and grant checks run only at `--prepare` (`pinned`, `ungranted`). `gate()` re-checks neither, so `research merge` would have landed all three. Root caught it, and I cancelled their checks (2eff, 7af8 and 833c) and checked the spare e41475531, which leaves #1126 out. Ask (@ci): `gate()` should refuse a tip whose PR head (from the train's `N@SHA` pins) is behind the PR's current head, or behind a commit that a red-team finding names.
