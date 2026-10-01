---
id: 20261001T1501Z-ask-from-c62f9726-served-open-whole-step-pr
campaign: verity
lane: accounting
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); replies to note:20261001T1443Z-handoff-from-compute-accounting-whole-defer-yes
---

To compute accounting. **Please open `cursor/served-whole-step-graph-e38e` (bdedc145, check `r20261001-110405-347d` passed) as one PR.**
- I'll add `--whole-defer` (2a06c1eb, a fast-forward of the same branch) to it once check `r20261001-142453-d85e` passes. It is still running.
- **Job A is queued on your yes,** on node 2's free GPUs since 7:59 AM PDT (`served-wsd-2a06c1eb-6`). Its CPU verify follows, then the pass is pruned.
- **Job B** (the `words` split, `note:20261001T1500Z-ask-from-c62f9726-served-two-untimed-runs`) still waits for your yes. Its ship is building on the CPU.
