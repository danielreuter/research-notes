---
lane: coordinator
kind: handoff
created: 2026-09-23T18:00Z
---
# red-team-leaf findings for ligerito-zk (full text: ~/.research/notes/lanes/red-team-leaf/20260923T1710Z-report-red-team-leaf.md, ## FINAL)
Your L1-L6 leak catalogue and the mask-column argument were checked and hold GIVEN:
* **F9** (missing condition): mask-column uniformity needs 2^{k_1} >> 2^{k_(l-1)} + sum|S_i| + sum(2k'_i + 1) + E. It is unstated and FAILS at
  your own §5 toy sizes; G-block cells are not free given the transcript. State the condition, make `zk.py` assert it for the chosen params
  (and `check_layout` cover every referenced cell, t_pad >= max|S_i|), and pick test sizes where it holds.
* **F10**: state that the ZK claim is interactive (live coins) only; under FS the simulator does not transfer and the q x eps rule applies.
