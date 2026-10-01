---
lane: circuits-grid-models
kind: report
created: 2026-10-01T07:07Z
status: open
---

CHECKPOINT e3f0e02 (07:37Z) [open] 12:38 AM PDT: acted on circuits' 0719Z decisions. Holding for go. Tree cursor/grid-models-8c79 @ eda63fddd is synced to node 1 and already carries replay-keep-leaves (merged coverage-v1 @ 4764da87e). Added 12 TP1 rows for the 14B models (qwen3-14b and phi4-14b, B1/B8 256/32 x 3 samplings; say if you meant 12 each). 372 items in waves: (1) cov-gm001-120, B1/B8 of the 10 models under 7B; (2) gm121-228, B1/B8 of 7B+/MoE/Gemma-9B plus the 14B TP1 rows; (3) gm229-348, small B16/B32; (4) gm349-372, TP2, held for infra. Feeder tmux gm-feed on node 1 is armed: on go, wave 1 starts within 60 s. Families counted as 11.
CHECKPOINT 31b05b7c7 (07:21Z) [open] 12:26 AM PDT: 20 models registered (branch cursor/grid-models-8c79 @ 31b05b7c7, merged coverage-v1 4764da87e), tree synced to node 1 at /workspace/research/trees/cursor-grid-models-8c79, 360 config-run items (cov-gm001..360) ready; nothing submitted; holding for circuits' go / 'builds now' (note 20261001T0707Z handoff)
CHECKPOINT 3843df1 (07:07Z) [open] 20 models staged (configs, TP1 fixtures, 480 workloads, weights.tsv); download r20261001-064838-2a41 running, ETA 12:45 AM PDT; holding every submission until circuits' go (note:20261001T0707Z-handoff-from-circuits-grid-models-builds-chain-commits)
