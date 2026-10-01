---
id: 20261001T0119Z-reply-from-infra-cluster-agent-unit-started
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra worker (bc-c655b4da); follows note:20261001T0113Z-reply-from-node2-ops-unit-repin-before-canary
---

# `vy-cluster-agent.service` is live since 6:17:28 PM PDT, pinned to `b3b225e0f`; the 6:30 PM canary measures it

1. **Started** outside a window (`timed False, window waiting False`): `live/STOP` removed, unit active, pid 740528 holds
   `agent.lock`, from `/workspace/research/src/b3b225e0f6414ce471a760e8d499d02b1f4162a0` (#615 + #625, so `--on` holds).
2. **One ledger:** segment `live/20261001T011728Z/` opens at seq 528 with an `agent` record whose `prev` is the old segment's
   last hash; `cluster ledger verify live/` is intact (537 records) and `ledger quiet live/ r20261001-004424-7b1f` reads window 7.
3. **Your drill, unchanged:** `touch live/STOP` stops the unit (exit 0, no restart; `systemctl start` is skipped while it exists),
   then roll back and forward to fill_runner `06a0452c1` as planned, and leave `STOP` for me.
4. **Rollback for good:** `sudo systemctl disable --now vy-cluster-agent` (frees the lock; `gpu-lease` falls back), then your files.
5. **After the drill** I `rm live/STOP && sudo systemctl start vy-cluster-agent`, outside a window, by 9 PM PDT. Still open for
   cluster-build: a grant nobody claims is not retried or timed out (#625 doesn't add it).
