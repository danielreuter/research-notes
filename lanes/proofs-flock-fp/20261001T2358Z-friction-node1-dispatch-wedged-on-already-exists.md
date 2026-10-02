---
id: proofs-flock-fp/20261001T2358Z-friction-node1-dispatch-wedged-on-already-exists
lane: proofs-flock-fp
kind: friction
status: open
severity: incident
---

# Node 1's dispatcher has failed every tick since 21:42Z on one chain's AlreadyExists

Since 21:42:13Z (2:42 PM PDT), every tick of vy-nebius-1's `dispatch.py loop` (tmux `node1-dispatch`) has failed with `kubectl create -f -: ... jobs.batch "nd-vllm-epoch-run-c534860768-gpu-0" already exists`. The tick handles finished Jobs in name order. At `nd-vllm-epoch-run-c534860768-build-0` (vllm-epoch-run/cov-gm390, succeeded 21:41Z), it submits the chain's next task, but that Job was already created at 21:38:45Z, before the build ended. The create raises, so the tick stops before it labels the build `verity.dev/seen=1`, and the next tick does the same: 131 `end` lines for that build are now in `log.jsonl`.

What it cost: the ready pass runs after the Job loop, so no node-1 `ready/` item has been submitted since. Finished Jobs whose names sort after that build are never handled either: cov-gm390 after its gpu-0 (done 21:46Z), cov-gm071's replay (21:53Z), cov-gm183's gpu task (its build finished 22:19Z), and cov-gm169's failed build (23:10Z). infra's 23:00Z and 23:30Z "GPU idle while work is waiting" alerts assume the dispatcher is refilling the queue. The same pane shows this failure on `nd-vllm-epoch-run-4615670fb1-gpu-0` at 15:58Z.

What I did instead: I moved my one ready item (fp-rv2-stage-12cells-c7b5357) out of `ready/` and submitted it with `dispatch.submit` at 23:56Z, the way bf16-hill's items have gone in since 22:58Z. I changed no Job and no dispatcher file.

The fix belongs to infra. A chain's next task that already exists should count as submitted, so one Job can't stop every tick. To clear it now, label the build-0 Job seen, since its gpu-0 has already run.

Update, 00:36Z: the last failed tick was at 00:04:50Z, and ticks have succeeded since 00:05:55Z. `dispatch.py` (last changed 20:09Z) and the loop process (started 20:10Z) are unchanged, so the Job state was changed by hand and the bug itself is still there.
