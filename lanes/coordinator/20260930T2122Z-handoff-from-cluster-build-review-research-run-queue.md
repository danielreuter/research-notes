---
id: 20260930T2122Z-handoff-from-cluster-build-review-research-run-queue
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); infra's T3 target (note:20260930T2110Z-handoff-from-infra-t3-tonight)
---

# cluster-build -> research coordinator: a short review of `research run --queue` (tools/research), by 7 PM PDT if you can

Branch `cursor/queue-submit-path-0381`, commit a05caf25f, stacked on #586. The tools/research part is small:
- `cli.py`: `run --queue` with declared resources (`--gpus --gpu-model --cpus --mem-gb --max-min --class --preemptible --quiet
  [--on NODE]`). It calls `cluster submit` from the `--source` tree by subprocess (research imports no cluster), then goes
  through the unchanged `_run_remote` on the placed machine.
- `remote.py`: the request carries `wrap`, and `_launch_request` puts it in front of the runner's argv. The allocation
  (gpu-lease or a systemd scope) is held until the runner exits, so custody finishes before release. `knows_queue` refuses
  a `--source` tool package that predates this.
- Tests: `test_cli.py` (`-k queue`) and `test_remote_local.py::test_a_queued_run_…`. The research suite passes (720).
- Live on vy-nebius-2, both `done rc=0` with records preserved: a CPU scope run (r20260930-211910-7b9b) and a 1-GPU guest
  run through gpu-lease (r20260930-211957-1028).

Two things I'd like your call on:
1. **Naming.** `research queue` is already the merge queue. Is `--queue` fine, or do you prefer `--on cluster`? Either is a
   one-line change.
2. **Phases are coming next.** Daniel's rule is that the GPU is booked only for the GPU phase. That adds `--phase KIND:NAME`,
   which runs each phase under its own wrapper inside the runner, so custody then runs outside any allocation. Same files;
   I'll send a follow-up.
