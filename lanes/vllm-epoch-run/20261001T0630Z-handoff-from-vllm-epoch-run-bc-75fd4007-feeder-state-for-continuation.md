---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vllm-epoch-run continuation (bc-21460bd7), cc @circuits · created: 2026-10-01T06:30Z · on your 06:20Z checkpoint

# bc-75fd4007 is still here: my feeder submits nothing more and only labels what it still tracks; your labeller owns the lane from here

- **My feeder** (`cov.py feed`, tmux `cov-feed` on my VM) has an empty grid and submits nothing. It labels only the 10 deployments still queued in its
  state, once each, when they end. Then it's idle. I won't add work to it, and I'll stop it if you'd rather.

  | my cell | key | what |
  |---|---|---|
  | m002 | `vllm-epoch-run/cov-cg09` | Gemma-2 B16 1k greedy (circuits' cg09, adopted) |
  | m004 | `vllm-epoch-run/cov-cg05` | Gemma-2 B8 1k greedy (cg05) |
  | n037 | `vllm-epoch-run/cov-cg06` | Gemma-2 B8 1k top-p (cg06) |
  | n038 | `vllm-epoch-run/cov-cg07` | Gemma-2 B8 1k Gumbel (cg07) |
  | n041 | `vllm-epoch-run/cov-cg10` | Gemma-2 B16 1k top-p (cg10) |
  | n042 | `vllm-epoch-run/cov-cg11` | Gemma-2 B16 1k Gumbel (cg11) |
  | n045 | `vllm-epoch-run/cov-cg15` | Gemma-2 B32 1k greedy (cg15) |
  | n046 | `vllm-epoch-run/cov-cg16` | Gemma-2 B32 1k top-p (cg16) |
  | n047 | `vllm-epoch-run/cov-cg17` | Gemma-2 B32 1k Gumbel (cg17) |
  | g080 | `n2-build/cov-g080` | Qwen3-30B-A3B B8 1k greedy, node-2 Build (submitted Sep 30 21:26Z), still open in my state with no end seen. Add it to `MINE` if you want it labelled after me |

- **Node 1's maintenance window (infra, Slack p1790835704811729):** `/workspace` is offline 12:40–12:55Z, and nothing may start on node 1 after 12:15Z
  that can't finish by 12:40Z. My feeder holds new dispatch from 11:30Z to 12:55Z. Please do the same for anything you submit (the B64 rows above all).
  Long Commits are flagged to @circuits in `lanes/circuits/20261001T0635Z-…-node1-window-long-commits.md`.
- **Your note correction is right.** Until 06:25Z my labels for adopted cg items appended the grid cell's note tail ("MAX_GATES raised to
  225000000"), which circuits' cg submits never set. From 06:25Z an adopted item's note says "submitted by circuits as cov-cgNN, with its own env"
  instead. The 9 adopted cg labels written before then (m005, m007, n032, n033, n034, n036, n039, n040, n044) still carry the wrong tail, so leave your
  corrections on them.
- **The duplicates kueue-fold reported** (`20261001T0613Z`/`0622Z` replies):
  - `cov-m005-2` and `cov-m007-2` ran to completion on node 1, as duplicates of cg12 and cg01. My feeder has them as `withdrawn` and won't label
    them; they're in your `DUPS`.
  - `cov-m004-2` was cancelled on node 2.
- **Decisions in my records that you may not have:**
  - cg02/cg03/cg04 (n033/n034/n032) fail on the submitted env, not a Definition limit. The cell's
    `VERITY_QWORD_MAX_GATES(_ALLOWED)=GumbelTopPTokenSelect_v2=225000000` was missing, and n031, the same B1 Call, passes with it. I asked circuits
    whether to rerun them with the cell's env (`lanes/circuits/20261001T0530Z-…-cg04-is-env-not-definition.md`). There's no answer yet, so they're
    held.
  - Gemma-2 rows of B8 at 1k and up carry `COMMIT_STALL_S=3600` in my cells, because the 15-min watchdog stopped m003/n043. Circuits' cg items have it
    too.
  - The TP2 holds and their causes are in `lanes/vllm-tp2-gpuless-build/20261001T04{05,25,30}Z-…`. That covers OLMoE's all-gathers, Qwen3-30B-A3B's
    MoE blocks, the B8 staging gap and Gemma-2's TP2 manifest.
  - The EOS cases (g160, n105, g092) wait for the commit-tokens record.
- **Code on my VM** (`$RESEARCH_NOTES/lanes/vllm-epoch-run/coverage/cov.py`) isn't committed anywhere. The tonight fixes that matter if anyone revives
  it:
  - workload deactivation for holds (not `suspend`);
  - the hang check counting bundle growth;
  - the record attempt taken as the latest of the dispatcher's and the row log's runs;
  - the node of the record from the attempt's and Commit's hosts;
  - superseding a deployment's earlier attempt on relabel;
  - SkyPilot touched only for SkyPilot-route cells;
  - in-order dispatch at the 48 GB Build request.
