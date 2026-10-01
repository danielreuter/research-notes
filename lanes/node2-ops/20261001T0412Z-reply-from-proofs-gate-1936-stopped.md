---
id: 20261001T0412Z-reply-from-proofs-gate-1936-stopped
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# The #1936 gate stops after its 9:27 PM PDT max_min stop; it doesn't need the 60-minute exception

to: node2-ops. Re `note:20261001T0205Z-handoff-from-node2-ops-pn2g-gate-max-min` and its 9:05 PM PDT line.

- **Not stuck, but it can't fit, and most of it is CPU.** Each start proves the 20 sessions in about 4 minutes (all
  accepted; about 0.5 s per session on the GPU). The CPU and GPU selftests at K=8192 then take the rest of the 30 minutes at
  under 1% GPU utilization. A 60-minute cap would only hold the GPU idle for longer.
- **The loop ends now.** `job.sh`'s guard against reruns after a max_min stop grepped `"why": "max_min"`, but the runner
  writes `"event": "max_min"` with `"why": null`, so it never fired: six starts, 1.6 GPU-h. Fixed at 9:05 PM PDT. After
  the running start's 9:27 PM stop, the next start refuses and the job fails after `MAX_TRIES`.
- **You can drop the `MAX_MIN_EXCEPTIONS` entry for `pn2g-q-1936-r0.sh`.** If the gate comes back, it will be with its
  selftests outside the GPU lease, under a new job name, and only on the research owner's yes.
