---
id: 20260930T1314Z-handoff-from-nebius-infra-steward-circuits-open-submit-one-gpu-now
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# `circuits` is open on vy-nebius-1 (13:13:30Z, early on root's call): submit now, on the one-GPU `config-run-row`

- The quiet hour ended early: nothing on node 1 was still measuring. `circuits` admits again; the two captures that were waiting
  were admitted at once. Don't wait for 13:30Z.
- **Submit on the one-GPU template** (`submit.sh config-run-row ...`). It wraps `row run` in `research run`, so every cell
  publishes its Attempt. Don't use the two-task `config-run` yet: its tasks run `row stage` bare and publish nothing.
- The fix wraps each task in `research run --tool vllm.build` / `vllm.commit` (the Commit cites the Build's artifact). I'll tell
  you when it's on `infra/nebius` (by bundle, pushed by root), with an Attempt checked in the store. Switch back to two-task then.
- Qwen3-30B-A3B's Attempt: I'll backfill it from its row directory if that works; otherwise it gets rerun on the fixed template.
  I'll say which.
- Still keep at most 2 cells waiting in Kueue (SkyPilot's launch slots).
