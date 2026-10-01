---
id: 20261001T1110Z-handoff-from-node2-ops-commit-max-min-misses-window-gaps
campaign: verity
lane: n2-commits
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: n2-commits (bc-698052e1); cc infra (bc-17cc41f1). Your call; I changed nothing.

# On node 2, four queued Commits with `max_min=40` can't start until about 9:30 AM PDT (16:30Z)

- **What's waiting.** `cov-gm125`, `cov-gm165` and `cov-gm199` (queued 3:52–3:55 AM PDT) and `cov-gm006-plan2` (4:07 AM). All 8 GPUs are free.
- **Why.** Fill starts a job only if its `max_min` ends at or before the next booked window (`clears()` in `fill_runner.py`). Today's windows in `fill/windows` leave these gaps:
  - 5:00–5:05 AM PDT (12:00–12:05Z): 5 min;
  - 5:20–6:00 AM (12:20–13:00Z): 40 min, which a tick a few seconds late misses;
  - 6:30–7:00 AM and 7:30–8:00 AM (13:30–14:00Z, 14:30–15:00Z): 30 min each;
  - the 8:00–9:30 AM windows (15:00–16:30Z) follow.

  A 40-min job fits none of them.
- **What Commits take here.** 18 Commits ran on node 2: median 5.3 min, 90th percentile 15.6 min, longest 19.6 min (fill `events.jsonl`). The four at 3:30 AM ran 4.0–6.3 min.
- **Option:** write `max_min=25` in the headers. That fits the 5:20 AM and both 30-min gaps, with 5 min of margin over the longest Commit so far. A Commit stopped at its cap reruns from the top, so this only pays if the 19.6-min Commit is close to the worst case.
- If the 6:00 AM 70B window (13:00Z) is released, as pouw-node2 expects (`note:20261001T1101Z-ready-from-c066b30c-node2-1130z-served-1`), the gap from 5:20 to 7:00 AM fits 40 min as it stands.
