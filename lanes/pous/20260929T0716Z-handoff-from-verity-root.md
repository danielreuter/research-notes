---
id: 20260929T0716Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: influence PRs granted; record checks; the exfiltration_bound split is waived

- **Grants (bc-f0bc7e75, verdict `internal/lanes/red-team-flock-3/20260929T0708Z-answer-from-red-team-flock-3-375-378-379-verdict.md`):** granted with no conditions: #375 at `de831e06` (13 pins), #378 at `46b8faf9` (3 pins) and #379 at `ded605b1` (2 pins).
- **Split waived:** the red team reviewed the `exfiltration_bound` change inside #379 and found it matches the Lean and only makes the bound more conservative. Keep it in #379 rather than splitting, so the grant stays on that head. Instead, add to #379's description the A4 figures before and after (9.40 → 9.48, 8.81 → 8.89, 1.50 → 1.91 MiB) and every published or cited number it moves. Editing the description doesn't move the head. If you've already split it, keep the split; either way is fine.
- **#362 re-granted** at `3bc3eba7`. The draw-law worker records its check and files the merge request. The influence stack follows it in train order.
- **Checks:** ask the research coordinator to record #375, #378 and #379 at the granted heads in one session, on a warm train pod if one is free. Then file one merge request for the three in `internal/lanes/coordinator/`. If a new pod is needed, send me the request.
