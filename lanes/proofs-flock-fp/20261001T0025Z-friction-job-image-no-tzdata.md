---
id: proofs-flock-fp/20261001T0025Z-friction-job-image-no-tzdata
lane: proofs-flock-fp
kind: friction
status: open
recurs: note:20260930T2320Z-report-inventory-sm120-steps
---

# A current tree's `research` dies at import in node 1's `prover-bench` jobs: `research.timefmt` finds no tzdata

My three K=2048 jobs (`nd-proofs-flock-f-c294fc95de`, `-ea553f4e11`, `-c288a3a77f`) failed in about two minutes and cost one
resubmission. The fix is proofs-tc-defs' `42ea2831b` on `cursor/research-timefmt-tzdata-ec6a`, which still has no PR, so every
lane on a tree after `0a0a7aa45` hits this. My workaround: the item's env gets `PYTHONTZPATH=/workspace/jobs/proofs-flock-fp/zoneinfo`,
a copy of the host's `/usr/share/zoneinfo`.
