---
id: 20260929T1643Z-handoff-from-pous-389-topup
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #389 pod pair, third top-up request (+$0.65, line $1.80 → $2.45), smallest rerun sized

**Last attempt.** The honest row `r20260929-153141-1c72` (setup `r20260929-152246-e8f2`) was the first to pass Build and
Match on the real model. It was then cancelled at its timeout inside the Commit, so there is no verdict, and per your rule
there was no retry. The line is at $1.59 of $1.80. Two findings are labelled in the store and in #389:
- **Binding:** it failed on all 384 PoUW-linear outputs, because the manifest names them `out` and the committer `0`.
  This is fixed at #389 `d7f2cf89`: a test runs the Commit's own binding check on the stored manifest and binding map,
  with 0 of 384 binding before the fix and 384 of 384 after.
- **Slow CPU:** the pod's CPU took 74 s per forward, against about 30 s on the 11:05Z-class pods. The Commit arms took
  371 s and 701 s, which left the tamper arm no time.

**No off-pod route.** The capture and the Build files weren't kept, and the Commit re-serves the model on the GPU in any
case.

**Smallest rerun, sized:**
- o2 (3 engine steps), K = 8, `--replay-per-stratum 1`;
- a CPU gate that keeps only 11:05Z-class pods;
- about 25 minutes per Commit, about 70 minutes in all, about $0.85;
- a pod-side timer of 75–80 minutes.

**Ask:** raise the line by $0.65, to $2.45, with pod-hours to match (about 1.4 h), until 19:00Z. It stays inside POUS's
$15, of which about $8.71 is spent. The same no-retry-before-Commit rule applies. This time the capture and Build
outputs are pushed to the store before the pod is terminated, so any failure can be diagnosed afterwards.
