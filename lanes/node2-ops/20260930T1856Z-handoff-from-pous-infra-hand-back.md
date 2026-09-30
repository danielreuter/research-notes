---
id: 20260930T1856Z-handoff-from-pous-infra-hand-back
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: pous infra (bc-efe47341), for node2-ops (bc-c0738ef6)
---

# pous infra -> node2-ops: node 2 hand-back

Handed back under `note:20260930T1850Z-handoff-from-infra-stop-old-node2-ops-lane`. Steps 1–3 are done. The owner file (step 4)
is written right after this note, and then pous infra takes no further action on node 2.

**1. Timers:** all five are unsubscribed (hourly, alerts, the two Oct 7 final backups, #494). `list_subscriptions` returns empty.
Last relayed alert: `2026-09-30T18:30:59Z` (GPU 3's `gpu3-fp8-v2hot-cancel-gpu.sh`).

**2. Scripts:** they are in `/workspace/pouw/infra/lane/` on node 2. There are no keys, tokens or credential files; the only
match for `token|secret` is the README's own sentence saying so. `README.md` there says which copy is deployed.

**3. Uncommitted and held:**

| File | Live on node 2 | Repo | Lane copy |
|---|---|---|---|
| `bin/gpu-lease` | `0d172cf3…` | = `infra/nebius` `13f402b2`, `pods/sh/gpu_lease.sh` | - |
| `bin/fill_runner.py` | `7444de9f…` | = `13f402b2`, `pods/nebius/fill_runner.py` | `86f3d1d5…`: live plus the held Verity CPU pool |
| `bin/node_ops.py` | `cb706e88…` | **not in the repo** | `7b8ebe56…`: live plus the held OOM-guard preference for `fill-verity-*` |
| `bin/gpu_util_sampler.py` | `1f15688e…` | **not in the repo** | same |
| `bin/backup.sh`, `backup_unit.sh` | `b6b58bc0…` (`backup.sh`) | **not in the repo** | same |

- **The held Verity edits** (the interim terms in `note:20260930T1629Z-reply-from-pous-infra-to-nebius-infra-steward-spare-cpu`)
  stay undeployed until Daniel says yes and a path is chosen; the one-cluster design may replace them.
- **The runner has no supervisor loop:** it runs bare in tmux `pouw-infra-fill`. Restart it with
  `bin/restart_fill_after_window.sh`, which waits out any timed window. A bare SIGTERM stops fill for good.

**4. 18:00–19:00Z:** my 19:03Z tick won't run, so node2-ops owes the full hour. Partial figure for 18:00–18:55Z: **77% busy**
(timed 0.60, kernels 5.14, of 7.44 GPU-h; leased-idle 1.11, free-idle 0.59).

**5. Open promises:**
- The pous root wants the busy % for 18:00–19:00Z, the first full hour after the waiters fix (`13f402b2`, live 17:58:46Z).
  Before the fix the hours were 32–72%; since it, 87% at 18:00–18:10Z and 77% at 18:00–18:55Z.
- **A small fix for `gpu-lease`'s usage report:** each reading counts a full 10 s cadence, so `busy_s` or `sampled_s` can exceed
  `held_s` by up to one cadence. Cap them at `held_s`.
- **Relayed alerts, still with their owners:** GPU 3's `gpu3-fp8-v2hot-cancel-gpu.sh` (18:30Z, rc 1, no error text), and GPU 5's
  `-verify` retry (17:42Z).
- **One-cluster:** phase 1a (the usage report) is shipped. Phase 1b's read-only shadow runs have pous infra's yes, with
  conditions (`note:20260930T1727Z-reply-from-pous-infra-to-pous-one-cluster-phase-1`).
- **The pous root's rulings to keep:**
  - no ε_R or seed padding (15:27Z);
  - GPU 3's `gpu3-fp8/out` flags are never backed up, and kept until v2-hot is rated;
  - disk use is raised only past 60% (`node_ops.py` alerts at 60%);
  - GPU 1 has no hold (the `keep-free` file was removed at 14:19Z; add it back only for a quiet-die gate).
- **Daniel's 18:50Z utilization request:** I had started nothing. The pous root's 18:53Z message replaced it before any work, so
  there is no backlog queued, no CPU fill added and no per-node hourly report yet.

**6. Broker:** `source=broker` since 17:41Z; `token.json` still said `source = broker` at 18:56Z.
