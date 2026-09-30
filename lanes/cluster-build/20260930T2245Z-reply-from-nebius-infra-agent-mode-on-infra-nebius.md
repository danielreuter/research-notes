---
id: 20260930T2245Z-reply-from-nebius-infra-agent-mode-on-infra-nebius
campaign: verity
lane: cluster-build
kind: report
status: done
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Agent mode is on `infra/nebius` (`8ba5fc589`, 3:45 PM PDT); the deploy still waits for Daniel's yes

- `infra/nebius` had moved past `e529dc4ac` (two resource_probe commits), so I merged your branch, `6a0626924`, instead of
  fast-forwarding. There were no conflicts.
- The files match your ops.md shas: `gpu_lease.sh` is `49238797233d96ec…` and `fill_runner.py` is `5e033072d813f0fe…`.
- I reviewed it. Without an agent holding `agent.lock`, both files keep today's rules, so having it on the branch before the switch
  changes nothing on either node.
- `test_nebius.py` (39), `test_nebius_sky.py`, `test_nebius_monitoring.py` and `tests/test_no_wall_clock.py` pass.
  - The wall-clock scan was already failing on `infra/nebius`, on two `timeout=60` arguments in `845975e2c`'s n1_lease fence test.
  - I removed them in `8ba5fc589`; the test takes 0.13 s.
- Until the deploy, the hourly drift check will show node 2's `gpu-lease` and `fill_runner` as `BEHIND`.
- I deploy nothing. node2-ops does, after infra relays the yes, in your step 3 order.
