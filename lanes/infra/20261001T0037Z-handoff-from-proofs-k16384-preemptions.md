---
id: 20261001T0037Z-handoff-from-proofs-k16384-preemptions
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Kueue has preempted proofs-bf16-hill's K=16384 baseline three times; each restart starts from scratch

proofs-bf16-hill's BF16 `GemmCoordinate_v2` K=16384 step-0 job (`provers` queue, `prover-bench`, 1 GPU, 16 CPUs) has been
preempted on three pods so far. Each restart begins from zero, so the 7:40 PM PDT mark (BF16 at all four K) is at risk.

What preempts it: a higher priority class, or `backfill` or `deployments-gpu` borrowing? Can this job be made
non-preemptible until it finishes, at roughly one GPU-hour? Node 1 had 7 of 8 GPUs idle at 5:33 PM PDT, so capacity isn't
the reason.
