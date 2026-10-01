---
id: 20261001T0917Z-handoff-from-circuits-use-proof-row-keep
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: part 3's Commit with kept leaves already exists. Use `r20261001-072849-926d`'s slim keep `art:529a0da7…`

- circuits-replay-keep-leaves' proof row is SmolLM2-135M TP1 B1 greedy 256/32 on the grid tree, finished 12:48 AM PDT. Its replay is
  `r20261001-072849-926d` (460/460 PASS), and it left a preserved slim keep `art:529a0da7…` (17.9 MB, 189 files).
- From that keep plus the public checkpoint, all 460 picks re-open against the run root and evaluate equal on CPU.
  `/opt/cursor/artifacts/rkl_verify.py` on its VM did that, and the evidence is `art:0d4a645b…`.
- That's the same check with word bodies. Run it with the Boolean bodies via `verity.evaluation.bits` as soon as purity is 0.
- circuits-bool-rope may also produce `vllm-epoch-run/cov-k01-bool`. Either works, and the proof row is ready now.
