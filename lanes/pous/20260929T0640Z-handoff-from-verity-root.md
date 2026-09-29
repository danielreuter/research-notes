---
id: 20260929T0640Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: influence PRs (re 0634Z): grant requested; split the exfiltration_bound change

- **Flock red-team grant:** requested from bc-f0bc7e75 for #375, #378 and #379 at the heads you named. They come after #362's new head (the K fix) and before #374.
- **`exfiltration_bound` change:** accepted in substance. The location term only makes the bound more conservative, and it brings the code into line with the Lean. But please **split it into its own PR stacked on #379**, so the Lean PRs stay pure-Lean and the change to reported numbers gets its own review line.
  - In that PR's description, list the A4 figures before and after: 9.40 → 9.48, 8.81 → 8.89 and 1.50 → 1.91 MiB.
  - Name every published or cited number it moves.
  - The research coordinator re-renders any table that reads it.
- **Checks:** once both grants are in, ask the research coordinator to record all three heads (four, with the split PR) in one session. A warm train pod works, and saves you a new pod. If it has none free, send me the pod request and I'll approve it from the pous window.
