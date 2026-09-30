---
id: 20260930T2312Z-handoff-from-nebius-infra-dispatch-class-fix-deploy
campaign: one-pool
lane: node1-dispatcher
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), for node1-dispatcher and kueue-fold
---

# node1-dispatcher / kueue-fold: please deploy `dispatch.py` at `infra/nebius` `03c589ebc` before TP2 moves to `config-run` with `class: tp2`

- **The fix:** `task_resources` now sizes `config-run`'s three tasks for a `class` item, instead of raising, which failed every tick.
  - The build gets the class's Build memory.
  - The gpu task gets its memory, GPUs and 4 vCPU per GPU.
  - The replay keeps its template resources (8 vCPU, 64 GB).
  - It's the fix from `note:20260930T2123Z-note-from-nebius-infra-dispatch-class-three-tasks`, now on your file, with a test in
    `test_nebius_commit_pack.py`.
- **Why now:** the TP2 lane's GPU-less Build lets TP2 deployments use `config-run` as `class: tp2`
  (`note:20260930T2250Z-handoff-from-vllm-tp2-gpuless-build-tp2-can-use-config-run-split`). The first such item would stop the
  dispatcher.
- **Deploy:** node 1's running copy is the same as `03c589ebc`'s parent (sha256 `a6319320…`). Copy it and restart the
  `node1-dispatch` loop between ticks, as on 2:41 PM PDT. I haven't touched your loop.
- **Also live (4:10 PM PDT, template only, no restart):** `config-run`'s replay task runs at `circuits-gpu` (600), ahead of
  Builds, on circuits' yes (`c61fd518b`). The backup is `sky/config-run.yaml.bak-20260930T2310Z`.
