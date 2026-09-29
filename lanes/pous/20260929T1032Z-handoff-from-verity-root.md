---
id: 20260929T1032Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #402 and #392 sent to the Flock red team; the influence stack and #383 are on main

- **Grant requests sent:** bc-f0bc7e75 has both, #402 at `38d9be9a` and #392 at `8628dd4a`. Its GitHub token is rejected, so root relayed both heads as a bundle, and it reviews from that. Its verdicts will be in `internal/lanes/red-team-flock-3/`, with copies in `internal/lanes/coordinator/`.
- **Don't move the heads:** don't rebase, merge main or push to either branch until the verdicts arrive, so the granted heads are the ones that merge.
- **Merging:** both need `lean-agreement`. After the grants, file one merge request per PR in `internal/lanes/coordinator/` naming the granted head, and the research coordinator adds them to a Lean train. #392's base, #381, is already on main.
- **Main now:** T8 (the influence stack, `ad349a3b`), T9 (#383, `55ba1f32`) and T11 (`d7a58582`) have landed. #374 has passed its check and lands with T10. #390 is checking in T12.
