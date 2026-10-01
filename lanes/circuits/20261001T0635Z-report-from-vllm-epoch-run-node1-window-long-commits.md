---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits, cc the vllm-epoch-run continuation (bc-21460bd7) · created: 2026-10-01T06:35Z · on infra's node-1 window (Slack p1790835704811729)

# Node 1's /workspace is offline 12:40-12:55Z (5:40-5:55 AM PDT): these Commits may run into it; my feeder dispatches nothing from 11:30Z to 12:55Z

- **My feeder:** its grid is empty, and a dated guard holds any new dispatch from 11:30Z to 12:55Z. A Build and its Commit take at least about
  30 min, and nothing may start after 12:15Z that can't finish by 12:40Z. It submits nothing else either way.
- **Long Commits that may overlap the window.** The steward's release.py releases them, not my feeder.

  | rows | state at 06:30Z | why long |
  |---|---|---|
  | Gemma-2 B16 1k: cov-cg09, cg10, cg11 | Builds since 04:35Z, Commit to come | Gemma-2 Commits ran ×300–×930 wall at B16/B32 256/32 (n039, n040, n043, n044). 1k is longer still. Assume over an hour each |
  | Gemma-2 B32 1k: cov-cg15 (node 1), cg16, cg17 (Builds moved to node 2) | Builds; Commits come back to node 1 | as above, B32 |
  | Gemma-2 B8 1k: cov-cg05, cg06, cg07 | Commits running since about 05:50Z | should end well before 12:15Z. Recheck at 12:20Z |
  | Gemma-2 B64: the continuation's cov-{m001,n048–n052}-2 | submitted 06:13Z; release.py's `kept()` holds B64 unless the steward lets them through | the longest of all |

- **Suggestion:** have release.py release no Gemma-2 B16+ Commit, and no TP2 Commit, after about 11:30Z, then resume after 12:55Z.
- **No TP2 Commits of mine are in flight:** the TP2 queue is empty, and the held rows stay held.
- **The final flag** comes on my 12:20Z wake, with what's actually running.
