---
id: 20261001T1149Z-report-from-circuits-grid-models-counts-0450
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (4:50 AM PDT counts): 79 deployments ended, 75 passed, and all 4 failures have one named cause

These are the 4:50 counts your 0821Z GO asked for. The 2:05 counts are in note:20261001T0901Z-report-from-circuits-grid-models-counts-0205.

**Submitted: 103 keys.** 74 went on `cursor-grid-models-8c79` (`b9880ac17`). 29 went on `cursor-grid-plan-gm-827a` (`05fa9d3ea`), which
every row has used since 10:36Z (note:20261001T1038Z-handoff-from-circuits-commit-phases-plan-tree). No key was resubmitted, and none
is Gemma-2.

**Ended: 79.** 75 passed and 4 failed.

- 4 of the ended rows ran their Commit and replay on vy-nebius-2, and all 4 passed. 10 ran on the plan tree, and all 10 passed.
- **The 4 failures** are cov-gm001, gm031, gm081 and gm082, all Qwen3-0.6B. Every one is SiluMul_v1's expf-overflow edge: a
  Definition gap, not a Commit fault.
  - The GPU's SiLU gives -0 for gates at or below -89, where `expf` overflows, and `SiluMulBf16_v1` gives a tiny g·e^g instead.
  - The quarantined `SiluMul_v2` equals the committed words of every mismatched row, as checked by `labeller/silu_check.py`.
  - The labeller names the cause on each failed run (`ov.note`). See note:20261001T0934Z-handoff-from-circuits-grid-models-gm001-silumul-v1-expf-overflow.
  - circuits-bool-silu's v4 is exact on bits (note:20261001T1125Z-report-from-circuits-bool-silu-silu-v4-exact).
  - Promoting `_v2` would turn these rows green on a rerun.

**Models: 17 of my 20 have an ended deployment, in 9 of my 10 families.** The families are falcon3, llama3, mistral, olmoe, phi,
qwen25, qwen3, smollm2 and yi.

- falcon3-7b and qwen3-30b-a3b-2507 haven't ended a deployment yet. Their first Commits (gm125, gm135 and gm127) wait in node 2's queue.
- gemma2-9b, the tenth family, stays held: "no Gemma-2 at all from you".

**In flight: 24.**

- 10 Commits are queued on node 2 with max_min=40. None can start before 12:00Z, because 40 min from any time after 10:50Z reaches
  the 11:30Z window.
- 3 of the 10 (gm125, gm165, gm199, queued at 10:52–10:54Z) reach `VY_N2_RECLAIM_MIN` (60) at about 11:52–11:54Z. They go back
  to node 1 just before its 12:10Z hold, 6–8 min before node 2 could start them. I'm leaving it as is, because it costs at most an hour on 3 rows.
- On node 1: 4 Commits, 8 replays and 2 Builds.
- Node 1's Commits are capped at 6 in flight, by both release.py's MAX_INFLIGHT and the GPU queue's nominal quota. That cap is
  what moves the rest to node 2.

**Commit walls on node 1** (dispatcher `wall_s`, of the GPU task):

| Model | Batch, input tokens | Commit wall |
| --- | --- | --- |
| Qwen3-14B and Phi-4 | TP1 B8, 256 | 14 min (825–868 s) |
| Phi-4 | B1, 256 | 11.5 min |
| 7–8B models | B1, 256 | 6–14 min |

None of my rows ran past 30 min of Commit.

**Next.**

- The feeder submits nothing from 11:30 to 12:55Z. At 12:55Z it resumes, smallest Build first, on the plan tree.
- 233 eligible rows remain: TP1, non-Gemma, not yet submitted. The deadline gate turns itself off at 12:55Z. From then on, the
  rows it held go in their queue order: qwen3-30b-a3b-2507 at B8 256, and the B8/B16/B32 rows at 1k tokens.
- Final numbers by 7:50 AM PDT.
