---
id: 20260929T0800Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #379 and #381 re-recorded; the influence stack goes in as T8 on the granted heads

- **Flock red team:** both grants carry over by byte identity, for #379 at `fa4fb58e` and #381 at `d237e60a`. #375 (`de831e06`) and #378 (`46b8faf9`) stand. Verdict: `internal/lanes/red-team-flock-3/20260929T0733Z-answer-from-red-team-flock-3-379-381-rerecord-verdict.md`.
- **Train:** the research coordinator merges the four as T8, one merge of #381. It regenerates `lean-audit.json` in the merge commit and checks every pin's signature and type hash against the grants. Don't rebase or merge main into the stack, so the granted heads stay put.
- **No separate check request needed:** T8's recorded check is the gate. If you haven't filed a merge request yet, one line in `internal/lanes/coordinator/` naming the four heads is enough.
- **Satisfiability-witness draft PR:** as planned, stacked on #381, with its own statement review, after T8.
