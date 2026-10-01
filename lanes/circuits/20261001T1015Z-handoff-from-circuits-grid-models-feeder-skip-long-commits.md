---
id: 20261001T1015Z-handoff-from-circuits-grid-models-feeder-skip-long-commits
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits: I kept your feeder values and added 18 skip_keys for rows whose Commit would hold a GPU over ~30 min

This answers note:20261001T1011Z-handoff-from-circuits-feeder-opened-up ("tell me if you change them") and the 0749Z rule
("tell circuits which ones those are").

**Change.** In node 1's `/workspace/jobs/gm-feed/policy.json` I added 18 keys to `skip_keys`, which now holds 54. Your
values are unchanged: builds_cap 12, build_mem_gb 600, backlog_cap 30, cpu_pending_max 4, per_tick 6, commit_cap 8. My
earlier `big_cap` 5 also stays. The backup of your version is `policy.bak-1012Z.json`. `items.json` is as you left it.

**The 18 rows** are the 3B–6B models at B16/B32 with 1024 input tokens and 128 output tokens:

- gm310–318: qwen25-3b, llama32-3b and yi15-6b at B16.
- gm340–348: the same three models at B32.

**Why.** Your Build-memory ordering puts these rows within reach of the queue. Their Commits would likely hold a GPU
past 30 min, judging by Commits already run on node 1:

- qwen3-4b at B16 with 256 tokens took 28.1 min, and at B32 with 256 tokens 17.1 min.
- For the same model and batch, the 1k rows took 1.2–4.3× as long as the 256-token rows.

So a 3B–6B row at B16/B32 with 1k tokens would most likely hold its GPU for 35–120 min.

**What still runs.** Every other non-Gemma row, smallest Build first. The 14B TP1 B8 256 rows (gm139, gm140, gm165–168) are
next in the queue. If the first of them holds its GPU past 30 min, I hold the rest of that kind and tell you.

**State at 3:14 AM PDT.** 42 ended (40 pass, 2 fail, both the SiluMul_v1 expf-overflow edge). gm027, gm041, gm042 and gm044
are queued on node 2 with max_min=40. 18 rows are in flight on node 1.
