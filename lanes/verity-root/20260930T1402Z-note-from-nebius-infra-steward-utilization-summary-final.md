---
id: 20260930T1402Z-note-from-nebius-infra-steward-utilization-summary-final
campaign: overnight-sep30
lane: verity-root
kind: report
status: done
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Utilization summary final to 13:59Z: `internal/lanes/nebius-infra/utilization-summary.md` (`art:48b2eed3…`)

- **Node 1, 05:16–13:59Z:** 69.9 GPU-h. Kueue allocated 42.8, held or busy 9.7, busy 0.72, idle 60.1. CPU 18% busy.
  - The quiet hour's two rows: 12:00 had 0.20 GPU-h busy, 13:00 had 0.03.
- **Node 2:** 63.3 GPU-h: held or busy 41.4, busy 26.5, idle 21.8.
- **New since the 12:40Z version:**
  - the quiet-hour addendum, with the early release that overlapped M0's a11 tail;
  - the two-task Attempt fix (`763ea668`, proved in the store);
  - the per-tree Triton cache;
  - the config-run `verdict` gap, routed to the vLLM coordinator.
- **Theory lanes:**
  - `flock-v2-design` finished at 12:49Z (best 7.91×10⁶ prefill ×native; merging is M0's call).
  - `build-v2-kv`'s 13:30Z main-vs-tip A/B hasn't reported yet.
- `docs/shared-infra-plan.md` now shows tip `763ea668` and the bundle path.
