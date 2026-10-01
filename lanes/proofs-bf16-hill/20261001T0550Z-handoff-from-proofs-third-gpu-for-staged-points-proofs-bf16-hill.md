---
id: 20261001T0550Z-handoff-from-proofs-third-gpu-for-staged-points-proofs-bf16-hill
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs), on the top-level's 10:45 PM PDT order
---

# Node 1 has 6 idle GPUs: run staged points side by side, up to all three `provers` slices

to: proofs-flock-fp (bc-15199603) and proofs-bf16-hill (bc-89f3138c); the same note is in both lanes.

At 10:45 PM PDT only 2 of node 1's 8 GPUs were busy, because circuits' Gemma-2 Commits are waiting on slow CPU Builds. Until
those Commits arrive:

1. **Don't wait for one point to end before submitting the next.** Whenever a point's statements are already staged (a
   `STAGE_ONLY=1` job ended rc 0 on that tree), submit it now, beside your other running points.
2. **The cap is `provers`' three 16-core slices (cores 128-175) and 3 GPUs (2 floor + 1 borrowed), shared by both lanes.**
   Count the 0-GPU staging jobs too: each takes a slice. A fourth `provers` pod would share a slice and get
   `cpu-slice-shared`, so don't go past three; check `kubectl get clusterqueue provers` (cpu total 48 means full).
3. **Timed points may use the borrowed GPU now** (this replaces "untimed only" in `…T0216Z-…-provers-floor-and-slices`).
   Kueue takes it back when circuits' Commits arrive. A preempted point is re-run, never reported.
4. **Unchanged:** staging and every CPU-only step stay in `gpus: 0` jobs, `CPUS=16`, one point per job, each with its
   question. No new kind of job without the research owner's yes.
