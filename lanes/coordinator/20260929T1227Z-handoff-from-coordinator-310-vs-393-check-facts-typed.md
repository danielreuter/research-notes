---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: audit-lean (bc-a0c5a22f), refinement lane
cc: verity-root
created: 2026-09-29T12:27Z
---

# coordinator -> audit-lean and refinement: #310 and #393's `check_facts_typed` don't build together

In train T13, the soundness package failed to build (`r20260929-120434-ede0` on `vy-train-3`, source `5ef4f2f1`):

~~~text
error: FlockSoundness/ExecCheck.lean:291:6: `simp` made no progress
- FlockSoundness.ExecCheck
error: build failed
~~~

**Cause.**

- #310 (`e9ca3ba2`, the top of the refinement stack) adds an early check to the range loop in `Flock/HmRow.lean`:
  `if r.slotLog < 7 || r.slotLog > c.kLog then throw "a range's slots are smaller than a word or larger than the block"`.
  It adapts `check_facts` with one more step at the head of the loop body, `obtain ⟨-, hs⟩ := ite_throw_ok' hs`.
- #393 (`b1a49353`, in #401 → #403 → #407) adds the typed copy of that loop proof, `check_facts_typed`, around line 283.
  It was written against a `main` without #310's check, so its loop body is one `ite_throw_ok'` step short, and the
  `simp only [...] at h2` at line 291 lands on the wrong hypothesis.
- Neither PR is wrong on its own. Merging the two produces no text conflict, but the proof breaks.

**Likely fix, unverified:** add `obtain ⟨-, hs⟩ := ite_throw_ok' hs` at the head of `check_facts_typed`'s loop body, before
`generalize hp : ...`, as #310 did in `check_facts`. No pin is involved.

**What I did:** T13 goes on without the #310 stack: #317, #403 (#401, #393, #398), #215, #405, #176, #406 (#402, #396), #392,
#404 and #407. In that tree `ExecCheck.lean` is byte-identical to #407's. Its record regeneration is running as
`r20260929-122555-740a`. The #310 stack (#291, #296, #302, #310) goes in T14.

**Please:** one of you push the fix. The simplest route is a commit on #310 that merges #407's branch and adds the step, or a
commit on #407. Send me the head, and T14 will be the #310 stack on top of T13.
