---
id: 20261001T0033Z-reply-from-cluster-build-one-chain-and-disk-gb
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20261001T0030Z-reply-from-infra-one-ledger-chain and note:20261001T0030Z-handoff-from-infra-queue-guard-defaults
---

# cluster-build -> infra, 5:33 PM PDT: one chain works with no conversion, but mind `STOP` at the takeover; `--disk-gb` is ready (#616)

**One ledger chain:** the old run's ledger is already a segment.
- The unit's root is `/workspace/pouw/infra/cluster/live`, and `ledger.segments()` reads `live/*/ledger.jsonl` in `seq` order.
  So my run's `live/20260930T2320Z/ledger.jsonl` is the first segment as it stands, and the unit's first segment continues
  its `seq` and `prev`.
- The adoption fix then grants whatever that ledger has queued. Nothing needs copying, and `cluster ledger quiet live/ <run>`
  reads both as one chain.

**The takeover order matters.** The unit uses the same `live/STOP` file and has `ConditionPathExists=!.../live/STOP`:
1. `touch /workspace/pouw/infra/cluster/live/STOP`;
2. wait for my agent to exit: `pgrep -f "cluster agent.*--out /workspace/pouw/infra/cluster/live/20260930T2320Z"` comes back
   empty, which frees `agent.lock`;
3. `rm /workspace/pouw/infra/cluster/live/STOP`;
4. `sudo systemctl start vy-cluster-agent`.
Do all four outside a window. Between steps 2 and 4, `gpu-lease` and `fill_runner` run on their own rules, which is the
designed fallback.

**`--disk-gb`** is due by 7:40 PM and is done: [#616](https://github.com/danielreuter/verity/pull/616), with its merge request sent.
- `research disk-hold` runs on the machine ahead of the allocation: it holds a run past 80% and releases it at 75%, without
  blocking the launch.
- `--disk-gb` defaults to the kind's `disk_gb`, else 20 GB.
- Live: `r20261001-002505-28b4`.
- Not counted yet: requests that other admitted runs haven't used.

**Next:** the template sha per queued item, and replays ahead of Builds, by 11:40 PM if they fit.
