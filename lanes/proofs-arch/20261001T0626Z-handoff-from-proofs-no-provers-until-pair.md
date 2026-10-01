---
id: 20261001T0626Z-handoff-from-proofs-no-provers-until-pair
campaign: overnight
lane: proofs-arch
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Hold provers until verify-overlap's pair submits (repeat of 0606Z)

`pa-lm-1b61b02` (06:12Z) and `pa-lm-oldfold-ebcdb95` (06:24Z) went into the provers queue after
`note:20261001T0606Z-handoff-from-proofs-hold-provers-until-pair`. I tried to park the second one at 06:24Z, but the
dispatcher had already submitted it, so let it finish.

- **Submit nothing more to provers until verify-overlap's pair has submitted.** Check:
  `grep '"ev": "submit"' /workspace/jobs/dispatch/log.jsonl | grep 'proofs-verify-overlap/' | grep nvidia.com/gpu | tail -1`
  shows a submission after 06:26Z.
- After that, a CPU-only job may use a prover slot only when no BF16 or FP8/FP4 point is waiting for it, because the
  points are Daniel's overnight goal. Every prover slot can hold a GPU, so a CPU job there costs a point. I'm asking infra
  whether CPU-only work can go to a CPU queue instead; until it answers, wait.
- Node 1's window: queues hold at 5:10 AM PDT, nothing new starts after 5:15, and `/workspace` is offline 5:40–5:55.
