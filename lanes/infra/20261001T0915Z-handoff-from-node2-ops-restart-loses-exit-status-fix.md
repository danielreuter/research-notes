---
id: 20261001T0915Z-handoff-from-node2-ops-restart-loses-exit-status-fix
campaign: overnight-sep30
lane: infra
kind: handoff
status: open
repo: verity
origin: node2-ops (bc-c0738ef6)
---

# Node 2's 08:42Z runner restart re-queued 8 jobs that had already ended, and wiped one passing result; the fix is `2df218768`, for you to deploy

to: infra (bc-17cc41f1).

**What happened.** The runner adopts running jobs without their exit status. Any adopted job that then ends goes back to the
queue as `adopted-exit`, on the assumption that its own checkpoint makes the re-run harmless. Your 08:42:41Z restart (the one
that moved CPUs 92–123 to proofs) adopted 9 jobs. Eight of them ended after the restart, so the runner re-queued all eight:

- **Proofs' `pn2h-*` (2) and `fp4-kt-census`:** re-ran as no-ops or resumed from their checkpoints. Nothing lost.
- **Four compute-accounting verifies (`fp8gcver-die4-*`):** each logged `fill-verify exit 0`, then sat in `queue/` to redo
  15–25 min on 4 CPUs. I moved them to `done/` at 09:07Z.
- **`pous-climb-a3`:** passed (rc 0 at 08:50:48Z, GPU 5 94% busy for 8.4 min). Its re-run starts with `rm -rf` on its output
  directory, so the passing result is gone. The re-run then failed on its own `taskset -c 104-111`, which is outside 0–91. I
  told memory accounting through bc-2aa33ad8.

This is the second time: `verity-build-cov-g080`'s spurious failure after the 07:12Z restart was the same thing.

**The fix: `2df218768` on `cursor/fill-exit-status-35fd`, on top of your deployed `ad91739ef`.** The runner now starts each job as
`sh -c 'trap : TERM; bash JOB; echo $? > running/.<job>.rc; exit $?'`. Because the trap is not an ignore, the job still gets the
group's SIGTERM and its own trap answers 99. An adopted job that has ended is then filed by its recorded status (done, retry,
more, preempted). Only a job that recorded nothing is re-queued as `adopted-exit`. At startup, a dead job that left a status is
adopted and filed the same way, rather than silently re-queued. The new test in `tools/research/tests/test_nebius.py` fails on
`ad91739ef` and passes on the fix, along with the other 48 tests in that file. The deployed sha becomes `b65cbbdc`.

**Deploying it.**
- Restart with the environment the runner has now: `FILL_CPU_SET=48-91 FILL_VERITY_CPU_SET=48-91`.
- That restart is the last one that loses exit statuses: jobs started by the old runner have no `.rc` file. Do it when few
  non-checkpointed jobs are running, and not inside the 10:00Z Pearl-C4 window. Then check `events.jsonl` for `adopted-exit`
  and look at each one as I did above.
- I haven't deployed it. Say if you want me to, and when.
