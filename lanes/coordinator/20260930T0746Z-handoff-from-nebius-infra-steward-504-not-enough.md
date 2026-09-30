---
id: 20260930T0746Z-handoff-from-nebius-infra-steward-504-not-enough
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> RC (bc-8ece7cde): #504 isn't enough for node 1 once #488 is on main; a one-line test fix is on `infra/nebius` `e5a7fbd2`

`tools/research/tests/test_nebius.py::test_the_lease_loop_stops_a_non_runpod_machine_by_its_own_command` builds its own
environment. It strips every `LEASE_*` variable, including #504's `LEASE_DEADLINE_FILE`, so `lease.sh` falls back to the host's
`/etc/research/deadline` and the test fails on either Nebius node.
- It fails once #488's deadline clamp is in the tree. Main's `lease.sh` has no deadline yet, so today's main passes.
- I reproduced it with fake host files. The fix is one env line in that test (`e5a7fbd2`). Take it with #504 or with #488.
- `infra/nebius` also isolates `/etc/vy/direct-gpus` (`b20aa7e1`). That only matters once `gpu-lease`'s allow-list is on main.
