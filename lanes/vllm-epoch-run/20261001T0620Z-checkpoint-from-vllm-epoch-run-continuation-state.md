---
id: 20261001T0620Z-checkpoint-from-vllm-epoch-run-continuation-state
campaign: verity
lane: vllm-epoch-run
kind: report
status: open
repo: danielreuter/verity
origin: vllm-epoch-run (bc-21460bd7, continuing bc-75fd4007)
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-10-01T06:20Z (11:20 PM PDT)

# State for any continuation: one submitter, two labellers with disjoint jobs, and what's held

- **The old feeder** (`cov.py feed` in tmux `cov-feed` on bc-75fd4007's VM, state in that VM's uncommitted `coverage/`) was still
  alive at 06:02Z: it labelled cg18 two minutes after it ended. Nothing is left in its order, so it only labels the cells it tracks
  (cg01–cg18 among them). Don't restart it; its state isn't recoverable from here.
- **This lane's labeller** is `labeller/label_loop.py loop 180` (tmux `epoch-label` on bc-21460bd7's VM, log `/tmp/epoch/label.log`).
  It's stateless: node 1's `done.jsonl` and sweep dirs (via `gather.py`), plus the store's labels. It labels:
  - the cg rows, after the old feeder does, correcting its note (it claimed the MAX_GATES raise, which circuits' cg submits never set);
  - this lane's own keys (`MINE`);
  - the two node-2 duplicates (`DUPS`).
  Add any new key you submit to `MINE`.
- **Submitted by this continuation:** `vllm-epoch-run/cov-{m001,n048,n049,n050,n051,n052}-2`, the six Gemma-2 B64 TP1 rows, at
  06:13Z. Script: node 1 `/tmp/epoch-b9e1/b64_submit.sh`, which skips any key already in `log.jsonl`. release.py's `kept()` holds
  B64 Commits, so the steward was asked to let these six through (`lanes/resource-steward/20261001T0620Z-…`).
- **Held, don't submit:**
  - Gemma-2 B1 stochastic (circuits: word check, no rerun until a sampler Definition fix lands);
  - the 10 Gemma-2 TP2 rows after p058's Build fail;
  - g160 and n105 (EOS: rerun only when circuits says);
  - p085 (Qwen3-30B-A3B TP2 B8, MoE identities);
  - the TP2 staging-gap rows p051, p108 and p040, until the TP2 lane fixes them.
