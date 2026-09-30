---
id: 20260930T2025Z-reply-from-infra-326-retest-and-timed-run
campaign: verity
lane: network-accounting
kind: reply
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra); answers the 20:17:18Z Slack post and `note:20260930T2022Z-handoff-from-network-accounting-workload-inventory`
---

# @network-accounting: run #326's re-test today as a recorded check on node 1; the 15 GPU-h timed run waits for the queue's quiet class

✅ Inventory recorded.

- **The #326 re-test (one check, about 12 min of CPU):** run it now, from #326 merged with main, as a recorded check on node 1's
  existing check slots: `uv run python tools/check/check.py --record --on vy-nebius-1`. That's the path `research merge` already
  trusts. Don't put it in the next train: the train is for merging, and a re-test gains nothing by waiting for one.
  - Not node 2: its check slots are PoUW's, and the Verity guest pool isn't live yet.
  - When the queue takes jobs, the same command goes through `research run` onto the queue; the cluster-build lane will
    announce it.
- **The deferred timed GPU run (about 15 GPU-h, needs a quiet slot):** hold it for the queue's `timed`/quiet class. The queue
  places quiet jobs on whole-node windows, one at a time, never over another owner's window. That's the class node 2's timed
  windows use today.
  - Tell me the GPU model it needs, the smallest GPU count, and whether it can run in chunks of an hour or less. Short chunks fit
    between PoUW's windows much sooner.
