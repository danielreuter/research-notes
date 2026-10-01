---
id: 20261001T1027Z-handoff-from-circuits-grid-models-unskip-ack-deadline-gate
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits: I keep your unskip, and the feeder now holds only rows whose Commit can't end by 5:10 AM PDT

This answers your 3:16 AM PDT addendum to note:20261001T1011Z-handoff-from-circuits-feeder-opened-up. That addendum crossed with my
note:20261001T1015Z-handoff-from-circuits-grid-models-feeder-skip-long-commits, whose 18 skips you have now undone.

**Your question.** None of the 42 rows was held for a reason other than length, so I put none of them back. Your `skip_keys`
(the 12 Gemma-9B rows), big_cap 8 and every other value stay as you set them.

**What I added.** Your rule that "rows that can't finish their Commit by 5:10 AM PDT wait until after 5:55" had no
enforcement in the feeder. Its 11:30–12:55Z guard stopped only new submissions. So `gm_feed.py` on node 1 now has a deadline
gate:

- `policy.json` has two new keys: `"deadline": "12:10"` and `"deadline_until": "12:55"`.
- Before 12:55Z, the feeder skips a row if now plus its estimate passes 12:10Z. It moves on to the next row rather than
  stopping, so shorter rows further down still fill the GPUs.
- The estimate is 10 min of queue, plus the slowest Build and slowest Commit node 1 has logged for the same model, TP, batch and
  input length, times 1.1. Any lane's rows count. A base model's rows stand in for its variants: qwen3-30b-a3b for -2507,
  mistral-7b for -instruct, olmoe-1b-7b for -0125-instruct. A class nobody has run uses a conservative table.
- Each submit line in `feed.log` shows the row's estimate, and the tick line counts the rows held by the gate.
- The code is in `lanes/circuits-grid-models/feeder/gm_feed.py`. The backups on node 1 are `gm_feed.bak-1024Z.py` and
  `policy.bak-1024Z.json`. To turn the gate off, delete the two keys.

**What waits until 12:55Z** at the estimates as of 3:23 AM PDT:

| Rows | Estimate | Why |
| --- | --- | --- |
| gm137, gm161, gm162 (qwen3-30b-a3b-2507, B8, 256 tokens) | 123 min | On node 1 the base model's rows had a 49 min Build and a 54 min Commit. |
| gm169–175, gm177–190 (7–8B and MoE, B8, 1k tokens) | 107–258 min | |
| gm147, gm225, gm226 (the MoE at B1, 1k tokens) | 228 min | |
| gm289–348 (every B16 and B32 row at 1k tokens) | 170–225 min | |

Everything else, including the 7–8B and OLMoE rows at B1/B8 with 256 tokens and the small models' B16/B32 rows with 256
tokens, keeps going until each row's latest start (between 10:32 and 11:49Z).

**One risk for you to decide, which I haven't acted on.** `n2_commit.sh offload` moves any Commit that Kueue has held for 2 min
to node 2, under `max_min=40`. With big_cap 8 and release.py's MAX_BIG 4, B8+ Commits will wait on release.py. On node 1 the
qwen3-30b-a3b B8 Commits took 22–54 min. If one of them moves to node 2 and passes 40 min, it will likely be stopped twice
there and then come back to node 1. The gate keeps those rows out until 12:55Z, so this only matters after that.

**The restart.** The old feeder's tmux session ran the command directly, so it ended when I stopped it. It was down from
10:23:12 to 10:24:43Z. The session `gm-feed` now runs a shell with the feeder inside it.
