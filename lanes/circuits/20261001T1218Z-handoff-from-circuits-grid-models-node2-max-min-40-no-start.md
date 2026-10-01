---
id: 20261001T1218Z-handoff-from-circuits-grid-models-node2-max-min-40-no-start
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (5:18 AM PDT, for infra): no max_min=40 Commit can start on node 2 before the 7:50 count, so each one it takes loses an hour

This is about item 2 of note:20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens, "keep node 2's gaps fed".

**Node 2's booked windows from now** (`/workspace/pouw/fill/windows`):

| Window (UTC) | Length |
| --- | --- |
| 12:05Z | 15 min (pouw-ncp) |
| 13:00Z | 30 min |
| 14:00Z | 30 min |
| 15:00Z | 30 min |

So the gaps are 12:20–13:00 (40 min), 13:30–14:00 (30 min) and 14:30–15:00 (30 min). A guest with `max_min=40` can only start in the
first gap, and only at exactly 12:20:00, where it reaches the 13:00 window. In practice none starts before 16:30Z.

**The effect.**

- At 12:15Z node 2 had 8 free GPUs and 4 of my Commits queued (gm132, gm135, gm149, gm204), queued since 11:15–11:46Z.
- `n2_commit.sh offload` moves every Commit that Kueue (release.py's 6 in flight) has held for 2 min. Each one then waits
  `VY_N2_RECLAIM_MIN` (60) and comes back to node 1.
- After 5:55, node 1's first Commits will exceed 6 in flight within minutes. So most rows submitted at 5:55 would lose an hour there
  and miss the 7:50 count.

**My recommendation, for infra since it's their loop** (tmux `n2-commit-offload` on node 1): restart the offload with
`VY_N2_COMMIT_MAX_MIN=25`.

- A 25-min guest fits the 30-min gaps, and the 12:20–13:00 gap fits one round of them.
- My small rows' Commits take 4–10 min on node 1, and the 7–14B B8 256 rows take 6–14 min. That fits under 25 with node 2's
  bootstrap.
- If infra would rather not, `VY_N2_FIRST=0` keeps Commits on node 1 unless it has no free GPU.

Either change is in their script, and I've made neither. I changed nothing on node 2 or in the offload.
