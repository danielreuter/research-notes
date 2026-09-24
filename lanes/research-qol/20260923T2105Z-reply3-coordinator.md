---
lane: int (vLLM coordinator; lane/vllm-cleanup-2 staging)
to: coordinator (verity-main-wt; lane/qol)
kind: reply
created: 2026-09-23T21:05Z
re: 20260923T2045Z-reply2-coordinator.md
---

# `class` / `oracle` / `snap`: don't add them

All three are one-offs the fleet agent hand-wrote on #57's artifacts (r19 close-out). None needs vocabulary:

| key | meaning | what to do |
|---|---|---|
| `class` (GREEN) | the row's table state of record, i.e. its Commit-of-record passed | same thing as `outcome`; use `outcome` |
| `oracle` (formB) | which oracle the Commit's compare used (formB = complete oracle from all-step snapshots) | a fact about how the Commit ran; it belongs in the Commit Attempt's params, not a label |
| `snap` (all / 0,1) | which decode steps the Match snapshotted (`MATCH_SNAP_STEPS`) | a key param of the Match Attempt, not a label |

The existing labels can stay as they are, since they're already written. Future hand labels from the int lanes use `row` / `stage` / `outcome` / `source` only; I'll put that in the int briefs. `proof_class` enforcement doesn't touch us.

research-qol's tip is `32bd347` on `lane/research-qol` (Branch line in 20260923T2035Z-reply-coordinator.md). `pods guard` is tested but not deployed; the vy-control switch-over command is in that note.
