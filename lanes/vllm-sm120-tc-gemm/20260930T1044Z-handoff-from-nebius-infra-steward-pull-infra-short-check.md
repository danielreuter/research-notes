---
id: 20260930T1044Z-handoff-from-nebius-infra-steward-pull-infra-short-check
campaign: overnight-sep30
lane: vllm-sm120-tc-gemm
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> vllm-sm120-tc-gemm (bc-049fc756): `infra/nebius` is at `9540e031`; run your NVFP4 circuit-check with `check_slot.sh --short` now instead of waiting on `check-b`

1. `git fetch origin infra/nebius && git merge origin/infra/nebius` into your working branch. `submit.sh` refuses stale templates, and
   `9540e031` has the shared-tree bootstrap cache: a repeat capture skips the bootstrap lock.
2. Cancel the circuit-check queued on `check-b` (`r20260930-100544-7226`, if it's still waiting). It holds nothing, so cancelling
   loses nothing.
3. Relaunch it on a short slot, which never waits on a train:

~~~sh
research run --on vy-nebius-1 --project verity --source . --env CUDA_VISIBLE_DEVICES= -- \
  bash tools/research/src/research/pods/nebius/check_slot.sh --short <your circuit-check command>
~~~

`--short` runs at `nice 10` on the check CPUs 8–95 under `check-s1` or `check-s2`. Keep it to minutes; train-length runs stay on
`check-a`, `check-b` or `check-c`.
