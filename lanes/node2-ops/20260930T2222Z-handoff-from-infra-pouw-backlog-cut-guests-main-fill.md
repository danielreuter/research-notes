---
id: 20260930T2222Z-handoff-from-infra-pouw-backlog-cut-guests-main-fill
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: PoUW cut its overnight backlog to about 8–10 GPU-h, so circuits' approved Commits (as guests) become node 2's main fill, once circuits says yes

compute-accounting, 3:16 PM PDT: tonight's PoUW backlog is now about 8–10 GPU-h plus the timed windows. Those are GPU 7's 70B FP4
coverage (about 5 GPU-h), the per-die divisor baselines (1–2 GPU-h), and the 5 proposed windows plus the canary; the window plan is
unchanged. hsplit's remainder, the per-die form repeats and the hash bench are dropped.
- **Main fill:** circuits' 1-GPU Commits for the small staged models, plus the 8 #557 Qwen2.5 reruns, as `gpus=1 project=verity` guests
  through n2-commits' `n2_commit.sh`. They run only after the `cov-g217` cross-node check passes and circuits posts its overnight yes
  and question (asked on Slack at 3:20 PM PDT).
- **Also approved:** proofs' `pn2g-1936` stage job and its 3 chunks.
- **Nothing else overnight.** If a GPU is idle, report it with its cause. T2 on node 2 now depends on guests, so report guest GPU-h
  separately in the hourly line.
