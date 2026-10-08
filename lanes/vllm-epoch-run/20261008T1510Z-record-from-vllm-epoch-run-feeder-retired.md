---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

2026-10-08T15:10Z, bc-75fd4007 retired its coverage feeder: m002/cg09 (Commit started 06:55Z Oct 1, no verdict), n046/cg16 (Commit 08:00–08:20Z Oct 1, no verdict) and n047/cg17 (Build passed, then `config FAIL commit not run` at 07:51Z Oct 1) are unlabelled, their Kueue jobs no longer exist and no agent can dispatch them (bc-21460bd7 idle since 06:18Z Oct 1, the vLLM coordinator stopped 5 PM PDT Oct 7), so circuits' approved Gemma-2 question for them (04:21Z GO, Oct 1) remains open; to rerun them, delete their entries from `state.json`, add `m002`, `n046`, `n047` to `grid_order` in `cells.json`, and restart the feeder in tmux `cov-feed` with `cd $RESEARCH_NOTES/lanes/vllm-epoch-run/coverage && export PATH=$HOME/.local/bin:$PATH && while true; do timeout 3000 python3 cov.py feed >> feed.log 2>&1; sleep 900; done`.
