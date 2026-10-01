---
id: 20261001T0654Z-handoff-from-proofs-pair-submitted-fill-preemptible-proofs-flock-fp
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# The pair is in: fill the free prover slots with GPU points, preemptibly

verify-overlap's pair submitted at 06:40–06:44Z (its serve and GPU jobs), so the second half of `…T0626Z` applies now.

- **Slots.** The four 16-core slots on cores 128–191 are still the limit, not GPUs. While the pair runs it holds two, so
  bf16-hill and flock-fp hold **one pod each**. Once the pair ends, two each. GPU points before 0-GPU staging.
- **GPUs.** The top-level coordinator (11:43 PM PDT) gave proofs the idle node-1 GPUs for the hill-climb until circuits' grid
  Commits resume, about 1:30 AM PDT. At 06:45Z GPUs 0 and 2 were free (circuits' `vllm-epoch-run` took 4–6 at 06:43Z).
- **Preemptible.** Yield to circuits' Commits and to compute accounting's untimed work. Kueue takes borrowed GPUs back on its
  own. Daniel, 11:33 PM PDT: **a preempted point is re-run, not reported.** Proofs beyond its floor of 2 ranks behind compute
  and memory accounting tonight.
- **`cpu-slice-shared` should stop:** infra keeps host processes and direct runs off 128–191. If a point submitted after
  06:30Z still carries the flag, write its run id to `lanes/proofs/` instead of re-running it in a loop.
- **Order:** clean re-runs of flagged points first (goal 1 needs them cleared), then new steps.
- **Node 2: nothing yet.** Its fill runner doesn't pin CPUs and has 52 CPU jobs queued, so a point there would be contended.
  I've asked the coordinator for a pinned range; I'll tell you if it's granted.
- **Window unchanged:** nothing submitted after 5:05 AM PDT that could run past 5:35.
