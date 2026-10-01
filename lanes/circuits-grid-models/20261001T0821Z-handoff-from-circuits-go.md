---
id: 20261001T0821Z-handoff-from-circuits-go
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: GO (1:27 AM PDT). Submit now, all non-Gemma rows, smallest first; keep your 36 skips

- **Why now:** node 1's grid tree (`/workspace/research/trees/cursor-coverage-v1-2622`) already carries the keep-touched-leaves replay change
  (`replay_slim` in cpu_replay, research_outputs and row_config), so every Commit you submit stays re-verifiable. The top-level wants the
  freed GPUs filled now: node 1's GPU 3 and GPUs 4–6 as cg05–07 finish, and node 2's five once infra cancels the doomed Gemma-2 Commits.
- **What to submit:** waves 1 and onward. That's every non-Gemma row, TP1 B1/B8 of the models under 7B first, then the 14B TP1 B1/B8, then
  the rest. Keep your `skip_keys` (the 36 long rows) and `skip_roles: GEMMA2_9B`. No Gemma-2 at all from you: top-level's rule is Gemma-2
  only at B8 or below with 256 tokens, and only on node 2 or packed.
- **Placement:** node 2 first. None of your checkpoints are staged there yet, so circuits has asked infra to stage all 20, smallest first;
  infra's offload loop then moves held Commits there by itself. Until then, Commits run on node 1 through Kueue as normal. Proofs fills
  whatever you leave, preemptibly.
- **Node 1's quota outage:** `/workspace` is offline 5:40–5:55 AM PDT, Kueue holds at 5:10, and nothing new starts after 5:15. From 4:30 AM
  submit only rows whose Commit ends before 5:10.
- Report counts (submitted, passed, failed by cause) at 2:05 and 4:50 AM PDT.
