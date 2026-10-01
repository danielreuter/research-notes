---
lane: circuits-grid-models
kind: report
created: 2026-10-01T07:07Z
status: open
---

CHECKPOINT a54b1a5 (08:11Z) [open] 1:12 AM PDT: holding for circuits' go (expected ~1:30 AM). Feeder gm-feed armed on node 1: wave 1 = gm001-120 less the 3 held Yi B8 1k rows. 36 long-Commit rows held pending node-2 staging (note 20261001T0753Z handoff). Nothing submitted.
CHECKPOINT a3db005 (07:52Z) [open] 12:54 AM PDT: acted on circuits' 0749Z no-Gemma-on-node-1 directive. Holding 36 rows likely over 30 min of Commit (all 12 gemma2-9b rows, 6 qwen3-30b-a3b-2507 B8 rows, 18 B8 1k rows of the 7-8B dense models); asked for node-2 staging of 8 checkpoints (note 20261001T0753Z handoff). Feeder armed on hold; 372 rows pre-flight resolved, 0 bad. Waiting for go.
CHECKPOINT e3f0e02 (07:37Z) [open] 12:38 AM PDT: acted on circuits' 0719Z decisions. Holding for go. Tree cursor/grid-models-8c79 @ eda63fddd is synced to node 1 and already carries replay-keep-leaves (merged coverage-v1 @ 4764da87e). Added 12 TP1 rows for the 14B models (qwen3-14b and phi4-14b, B1/B8 256/32 x 3 samplings; say if you meant 12 each). 372 items in waves: (1) cov-gm001-120, B1/B8 of the 10 models under 7B; (2) gm121-228, B1/B8 of 7B+/MoE/Gemma-9B plus the 14B TP1 rows; (3) gm229-348, small B16/B32; (4) gm349-372, TP2, held for infra. Feeder tmux gm-feed on node 1 is armed: on go, wave 1 starts within 60 s. Families counted as 11.
CHECKPOINT 31b05b7c7 (07:21Z) [open] 12:26 AM PDT: 20 models registered (branch cursor/grid-models-8c79 @ 31b05b7c7, merged coverage-v1 4764da87e), tree synced to node 1 at /workspace/research/trees/cursor-grid-models-8c79, 360 config-run items (cov-gm001..360) ready; nothing submitted; holding for circuits' go / 'builds now' (note 20261001T0707Z handoff)
CHECKPOINT 3843df1 (07:07Z) [open] 20 models staged (configs, TP1 fixtures, 480 workloads, weights.tsv); download r20261001-064838-2a41 running, ETA 12:45 AM PDT; holding every submission until circuits' go (note:20261001T0707Z-handoff-from-circuits-grid-models-builds-chain-commits)
