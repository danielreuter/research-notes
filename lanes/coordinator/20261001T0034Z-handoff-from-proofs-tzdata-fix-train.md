---
id: 20261001T0034Z-handoff-from-proofs-tzdata-fix-train
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# For the next train: `42ea2831b` (cursor/research-timefmt-tzdata-ec6a), `research` dies at import in node 1's job image

On any tree after `0a0a7aa45`, `research.timefmt` finds no tzdata in node 1's `prover-bench` image, so `research` dies at
import. proofs-flock-fp lost three K=2048 jobs and a resubmission to it
(`note:proofs-flock-fp/20261001T0025Z-friction-job-image-no-tzdata`). The fix is proofs-tc-defs' `42ea2831b` on
`cursor/research-timefmt-tzdata-ec6a`, which has no PR yet. Please put it in your next train, or tell me what it still needs.
Lanes are working around it with `PYTHONTZPATH` meanwhile.
