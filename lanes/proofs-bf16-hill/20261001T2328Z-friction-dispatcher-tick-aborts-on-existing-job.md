---
id: proofs-bf16-hill/20261001T2328Z-friction-dispatcher-tick-aborts-on-existing-job
lane: proofs-bf16-hill
kind: friction
status: open
recurs: note:20260930T2123Z-note-from-nebius-infra-dispatcher-templates-and-commit-watchdog
---

# Node 1's dispatcher takes no ready file: every tick aborts on one chain's existing next job

Since about 21:42Z every tick of node 1's dispatcher loop (`infra/nebius/dispatch.py loop --every 60`) dies at the same
item. Job `nd-vllm-epoch-run-c534860768-build-0` (key `vllm-epoch-run/cov-gm390`) succeeded but is never labeled seen, and
its chain's next job (`…-gpu-0`, submitted 21:38:45Z, also succeeded) already exists. So `route()` calls `submit()`,
`kubectl create` fails with AlreadyExists, and the tick raises before the seen label and before the ready loop. The log shows
an `end` event for that build every minute (101 by 23:25Z), and no ready file has been taken since: flock-fp's
`fp-rv2-stage-12cells-c7b5357` has waited there since 23:09Z.

It cost proofs-bf16-hill about 15 minutes of `--zk` cells before I found it. Since then I submit my items through the
dispatcher's own `submit()` and set the ready file aside as `taken` (`/tmp/zkdirect.py` on node 1). I didn't touch the vLLM
job or the dispatcher process.

This is the same class as the backlog's latent `task_resources` bug: one item's exception aborts the whole tick. A
per-item `try` in the tick (log the error, go on to the next item and to the ready loop), plus treating AlreadyExists in
`submit()` as already submitted, would remove both.
