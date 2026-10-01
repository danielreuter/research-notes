---
id: 20261001T1407Z-handoff-from-circuits-grid-models-deadline-gate-idles-gpus
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (7:07 AM PDT): the 7:50 deadline gate now holds 200 rows while node 1 GPUs idle. Drop it?

- **Where things stand.**
  - Since the Hold lifted at 13:30Z, short Commits (2 to 5 min) have used up every row that can end by 7:50.
  - At 14:02Z the gate held 209 of the 209 rows left, and 3 of node 1's 8 GPUs had nothing loaded.
  - My 1149Z note promised the gate would keep the GPUs full. That is no longer true.
- **Changed at 14:05Z, within your "keep the gate":** a row now goes until 14:50Z if its Commit can end by 14:45Z, not 14:35Z.
  - Its replay of 2 to 4 min then ends before the 7:50 check.
  - That released 3 rows (B1 1k, about 34 min). The 600 GB Build cap holds the rest.
  - The other rows go after 14:50Z.
- **The cost of holding them.** Every row still held crosses 7:50 whatever happens. Its Build takes 35 to 60 min, so its Commit
  would reach a GPU only after the rows that count. Holding them gains nothing for the count, and node 1's Commit GPUs sit idle from
  about 14:40Z until 15:30Z or later.
- **My recommendation:** drop the gate now, so the held rows' Builds start and their Commits arrive around 14:45–15:10Z. The rows
  that count keep the front of the queue, because the item order is sorted by estimate. I'll do it on your word. Otherwise the gate
  stays until 14:50Z.
- **Rollback either way:** node 1's `/workspace/jobs/gm-feed/policy.json` `deadlines` (backups `policy.bak-1404Z.json`, `-1410Z.json`).
