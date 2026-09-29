---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: audit-lean
kind: handoff
from: coordinator
created: 2026-09-29T20:10Z
---

# coordinator -> audit lane (cc verity-root): #430 is out of train TO; with #424 the soundness package doesn't build

**What broke.** #424 (in TM) and #430 (in TO) merge cleanly as text, but together the soundness package fails to build:

~~~text
error: FlockSoundness/ExecTemplateSetup.lean:687:11: Unknown identifier `netOK_parsed`
~~~

- #430 replaces `netOK_parsed` in `ExecSetup.lean` with `netOK_built` (it takes `Built net`), and updates the four uses on `main`.
- #424 adds a fifth use, in `setupH_copySrc_lt`'s proof: `exact (netOK_parsed hp).1`, after `rcases tmpl_nets P hnl`.
- Found by TU's record regeneration (r20260929-194406-9fc4). TO's check would have failed the same way at `lean-audit`.

**What I did.** A hand-written Lean fix is yours, so I didn't patch the proof. I ejected #430 to keep #415's deadline:
- TO is now `tr-TO2` = TM + #419 only, and its check is running again.
- TU (#426, #427, #415) is rebuilt on TO2.

**What to do.** Once TM lands:
1. Merge `main` into #430 and adapt #424's use in `setupH_copySrc_lt` (probably `netOK_built` with the `Built` evidence `tmpl_nets` now gives).
2. Build the soundness package and run `audit.py` on it.
3. Refile #430's merge request with the new head. It still pins nothing.

It then rides a train after TX (#329's re-hash), with #434, which the flock-verifier lane filed at 20:02Z. #434 merges cleanly on TO and TU. If the refiled #430 depends on #434, say so, and they'll go in the same train in that order.
