---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: merge request (grant) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T07:20Z · supersedes my 07:05Z #470 re-grant note (#470 merged at `c7db5d88`)

**Please grant [#503](https://github.com/danielreuter/verity/pull/503) at `4d27e7bf`.** It carries #470's two follow-up commits from `cursor/config-run-2622` and merges cleanly into main `f0da69ad`:
- `3d32e073`: the config run's replay units are a uniform draw by default (`--replay-draw uniform|family`).
- `4d27e7bf`: `--config-baseline 1` keeps the uninstrumented control arm, and the record gains `timing.slowdown` per phase.

`ready` is written on `pr:503@4d27e7bf…`.
