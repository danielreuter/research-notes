---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (question, blocks RunPod cells) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T06:20Z · re: `lanes/vllm-epoch-run/20260930T0522Z-GO-from-vllm-coordinator-config-sweep-v0.md`

**RunPod has no uk-south2, or any UK data center.**
- uk-south2 is Nebius's region, and it appears only in `pods/nebius/`. RunPod's data-center list (its API, 06:15Z) has nothing in the UK. Its European ones are EU-RO-1, EU-SE-1/2, EUR-IS-1..5, EUR-NO-1/2, EU-CZ-1, EU-DK-1, EU-FR-1 and EU-NL-1.
- `overnight-objectives.md` lists "launching outside uk-south2" as waiting for Daniel, so I won't pick a region myself.
- **Which do you want for the `vyv-cov-` pods?**
  - **(a)** SECURE on-demand in any data center, as the epoch pods were.
  - **(b)** SECURE, restricted to the European data centers (`--data-center` per offer).
  - **(c)** No RunPod: every cell runs on vy-nebius-1. That means only RTX PRO 6000 Commits, and only after #465 and #476 land. The L40S, A100 and H100 cells would then be recorded as not run.
- **Until you answer I launch no RunPod pod,** even once the line shows (it was still absent at 06:08Z). Meanwhile I'm preparing cells and recording unsupported ones from their refusal messages, which needs no pod.

**How I plan to measure extraction slowdown (correct me if you meant otherwise).**
- **Source:** each cell's Commit runs one uninstrumented control arm beside its instrumented run, on the same pod, so every slowdown has a same-GPU baseline.
- **Labels on the cell's attempt:**
  - the slowdown: `ov.slowdown.prefill` and `ov.slowdown.decode` (instrumented ÷ control);
  - the baseline's source: `ov.slowdown.source`, set to `control-arm`;
  - the line: `ov.line build-v1` with `ov.attempt 0`, the reading I take from "the baseline is attempt 0 of line build-v1".
