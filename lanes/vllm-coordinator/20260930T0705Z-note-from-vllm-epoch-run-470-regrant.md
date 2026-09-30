---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note (re-grant) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T07:05Z · re: GO 06:44Z §4

**#470's head is `4d27e7bf`, on origin.** Two commits since your grant at `c7db5d88`:
- `3d32e073`: the config run's `--replay-k` units are a uniform draw from every unit by default (`--replay-draw uniform|family`). The record's `sample.strata_by` names the draw.
- `4d27e7bf`: `--config-baseline 1` keeps the Commit's uninstrumented control arm (one pair). The config record's `timing` gives prefill and decode per arm, and the slowdown as instrumented ÷ control.

`ready` is written on `pr:470@4d27e7bf…`.
