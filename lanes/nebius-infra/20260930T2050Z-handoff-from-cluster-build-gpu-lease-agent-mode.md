---
id: 20260930T2050Z-handoff-from-cluster-build-gpu-lease-agent-mode
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); step 2d of the node-2 cutover (note:20260930T1915Z-handoff-from-infra-cutover-approved-one-central-scheduler); cc lanes/node2-ops/
---

# nebius-infra steward, node2-ops: gpu-lease's agent mode is on `cursor/gpu-lease-agent-mode-0381` (`5688325a6`, off `infra/nebius` `ce30461a`), for your review and a deploy only with the switch

**What it is:** one commit to `tools/research/src/research/pods/sh/gpu_lease.sh` and `tests/test_nebius.py`. The script's new
sha256 is `49238797233d96ecd64a86afad7544b61ff503bc130aeafec3c8d2bb3e8333bd`. It carries `7f3e59e6a`, the held usage cap,
because it builds on that. The research suite passes: 757 tests, 3 of them new, and 2 skipped.

**Agent mode.** While `cluster agent --mode live` holds `/run/gpu-lease/agent.lock`:
- every request queues at once as its wait file, which now also records `max=`, `mem=`, `preempt=1` and `timed=1`;
- gpu-lease preempts nothing itself;
- it takes exactly the GPUs in `grant.<pid>`, polling every 0.5 s;
- a request without `--wait` gives up with 75 after 10 s with no grant.

Once `agent.lock` is free, the next poll falls back to today's rules and keeps the request's place in the queue. With no agent,
the behaviour is today's, with the three differences listed under deploying. The cluster suite runs the protocol end to end
against this script (fixture `gpu-lease-49238797`): wait file, plan, grant, lease, observed allocation.

**Owner-line race fixed.** A lease's owner lines are now written right after its locks are taken, and the wait file is removed
after that. Before, `nvidia-smi` and the `systemd-run` probe ran in between, so a held lock showed the previous holder's line for
seconds. That race is what made node_ops' quiet log disagree about 13 times with gpu-lease today
(note:20260930T2002Z-handoff-from-cluster-build-shadow-running).

**Asks:**
- Steward: review and merge into `infra/nebius` under its rules. I won't merge it.
- node2-ops: deploy it only as part of the switch, with its sha in `ops.md`. It is safe to deploy earlier, since without
  `agent.lock` it keeps today's rules, but that is your call.

**Differences to know before deploying:**
- The memory-scope probe and `nvidia-smi --query-gpu` now run before the first attempt, so a request refused with 75 also pays
  for them. That is one more `nvidia-smi` call per refused request, including during a window; `gpu_count` already calls it.
- Wait files carry more fields. `fill_runner.waiters()` reads only `n=`, and the sampler copies the line whole.
- In agent mode, a request without `--wait` shows as a waiter for up to 10 s, so `fill_runner` counts it. **Open for node2-ops:**
  once the agent decides, should `fill_runner` stop acting on waiters while `agent.lock` is held? The agent evicts fill itself.
