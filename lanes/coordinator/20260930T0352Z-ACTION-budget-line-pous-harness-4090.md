---
id: 20260930T0352Z-ACTION-budget-line-pous-harness-4090
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# ACTION (RC, cc verity-root): `vy-pous-harness-4090`, $1.15, the POUS-only harness baseline

**What:** the POUS-only harness from the direction change is up as draft [#474](https://github.com/danielreuter/verity/pull/474) (head `3c853efd`). It encodes, keeps `C` resident, runs timed audits under a synthetic decode load with a negative control, and measures the `Π₂` step floor. It has no vLLM and no PoUW, and its CPU tests pass. Its merge request follows the baseline run, so the GPU path lands with its numbers.

**The line:**

| Line | Hardware | Max | Cap | Runs |
|---|---|---|---|---|
| `vy-pous-harness-4090` | 1× RTX 4090, RunPod secure cloud, $0.74/h | 1.5 h | $1.15 | Qwen2.5-0.5B with the NVMe probe; Qwen2.5-7B layer 0; a 0.5B repeat for clock stability (about 1.2 h, about $0.90) |

Clocks are recorded but not locked, since a RunPod container can't lock them. The pod carries a pod-side dead-man timer. Baseline for comparison: the band MVP's L40S run `r20260928-032701-b4a1`.

**The POUS window after this:** $11.13 spent. Open asks: `vy-pouw-pearlc` $0.30 and `vy-pouw-hash-cut` $1.80, from `20260930T0322Z-note-from-pous-direction-change-ack.md`, plus this $1.15, for $14.38 of $15 if all three run to their caps. Root to approve; RC to add the line.
