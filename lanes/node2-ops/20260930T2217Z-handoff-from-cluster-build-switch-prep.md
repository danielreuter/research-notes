---
id: 20260930T2217Z-handoff-from-cluster-build-switch-prep
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); follows note:20260930T2213Z-handoff-from-infra-switch-timing-window-plan (HOLD pending Daniel's OK)
---

# cluster-build -> node2-ops and nebius-infra: the node-2 switch, ready to deploy (on hold until infra relays Daniel's yes)

**1. `infra/nebius`** (nebius-infra, please). It can fast-forward to `e529dc4ac` on `cursor/gpu-lease-agent-mode-0381`, which
merges today's `infra/nebius` with agent mode (`5688325a6`) and the `fill_runner` agent.lock change (`cc8e54b6a`). The one
conflict was two imports in `test_nebius.py`, and `test_nebius.py` passes (39). The files to deploy, for `ops.md`:
- `tools/research/src/research/pods/sh/gpu_lease.sh`: sha256 `49238797233d96ec…`, unchanged from the one held for deploy;
- `tools/research/src/research/pods/nebius/fill_runner.py`: sha256 `5e033072d813f0fe…`, which includes infra/nebius's changes
  since `ce30461a`.

**2. The agent (the brain):** from `main` once train TQS lands (expected `ce30e9b6`, about 3:52 PM PDT). That cut includes both
before-live fixes and the partial-window rule. Launched the way the shadow was:

~~~text
research run --on vy-nebius-2 --project verity --source <verity at TQS's merge> --cwd source --timeout 17h --stage cluster-agent -- \
  env PYTHONPATH=tools/cluster/src python3 -m cluster agent tools/cluster/descriptions/nebius.toml --mode live \
  --out /workspace/pouw/infra/cluster/live/<run> --hours 16 --stop-file /workspace/pouw/infra/cluster/live/STOP
~~~

**3. Order, outside a window, with 15 minutes' notice** to bc-2aa33ad8 (through compute-accounting) and to this lane:
1. deploy `gpu_lease.sh` and `fill_runner.py` together (node2-ops; I never restart the fill runner);
2. start the live agent. It takes `/run/gpu-lease/agent.lock`, and from then on requests queue to it;
3. `touch /workspace/pouw/infra/cluster/shadow/STOP` to end the shadow (it takes no lock, so this only stops a duplicate
   reader).

**4. Stop and rollback:**
- `touch /workspace/pouw/infra/cluster/live/STOP` (or any exit, or `--hours` running out) frees the lock. `gpu-lease` and
  `fill_runner` then fall back to today's rules on their next poll.
- A full rollback also restores `gpu-lease` `58e2474c` and the previous `fill_runner` from ops.md.
- The rollback drill in the first hour is node2-ops'.
- The canary: the first timed window after the switch (the 5:00 PM attempt 67 if the switch is at 4:15 PM) must land inside
  0.13–0.15%. Otherwise stop the agent.
