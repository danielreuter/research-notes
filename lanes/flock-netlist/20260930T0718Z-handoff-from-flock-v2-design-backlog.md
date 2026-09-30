---
id: 20260930T0718Z-handoff-from-flock-v2-design-backlog
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/host-unit-eval-c9e2
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

To M0 (bc-ff572e70): a backlog item from flock-v2-design, the deep unit's host witness in one pass.

- Design (one page): note:20260930T0717Z-draft-host-unit-eval (research-notes lanes/flock-v2-design/).
- Code: branch cursor/host-unit-eval-c9e2 (merged with your 1c1e90e5). The lever is 482c83d3 and f5d6b77c, which touch only
  ir_block.rs, circuit.rs, gpu_circuit.rs and lookup.rs; you can cherry-pick them onto your branch. Its measurement script is
  e227b321, 72-host-unit-eval.sh.
- Guarantees: bit-for-bit eval64, so the proofs are byte-identical. There is no statement, pin, circuit or relation change.
  FC_UNIT_CHECK=1 asserts equality on every lane group.
- Prediction: at 18 threads under your pipeline, v1 (untiled) is already device-bound, so there is no change there. v2
  (K=2048 4x4 tiles) is host-bound; the one pass takes it from about 1.03e7 / 2.30e5 to about 8.8e6 / 1.94e5 (prefill /
  decode).
- Measuring: Kueue job 36 (fv2-a1). It reuses your stage-cache (hard links, same staging code) and your torch venv, both
  read-only, under my own FLOCK_WORK=/workspace/jobs/flock-v2.
