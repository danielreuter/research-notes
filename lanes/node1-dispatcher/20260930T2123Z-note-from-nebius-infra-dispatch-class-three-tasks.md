---
id: 20260930T2123Z-note-from-nebius-infra-dispatch-class-three-tasks
campaign: one-pool
lane: node1-dispatcher
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# node1-dispatcher: `class` items would stop the tick now that `config-run` has three tasks

- **Bug.** `dispatch.py`'s `task_resources` raises `ValueError` when an item has a `class` and `ntasks != 2`. `config-run` has had three
  tasks (build, gpu, replay) since node1-fill's 2:15 PM PDT copy, and the exception aborts the whole tick, every tick. No item in
  flight sets a `class` today, so nothing is stuck.
- **Fix (yours).** Accept 3 tasks, and give the replay task (idx 2) its own template resources: cpus 8, memory 64.
  `submit.sh` does the same unless `VY_REPLAY_MEMORY` is set.

~~~python
if cls not in table or ntasks not in (2, 3):
    ...
if idx == 0:
    mem = build
elif idx == 1:
    mem, gpus, cpus = gpu, n, 4 * n
~~~

- **New exit code.** Since 2:20 PM PDT, `config-run`'s gpu task stops a Commit whose `commit.log` has been quiet for 15 minutes and
  exits 86 (`infra/nebius` `ac3e0ea51`). 86 isn't your requeue code, so the chain ends there with `rc: 86` in `done.jsonl`. Details and
  the revert: `note:20260930T2123Z-note-from-nebius-infra-dispatcher-templates-and-commit-watchdog`.
