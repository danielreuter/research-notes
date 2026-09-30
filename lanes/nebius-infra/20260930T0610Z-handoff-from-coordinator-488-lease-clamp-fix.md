---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: nebius-infra
kind: handoff
from: coordinator
created: 2026-09-30T06:10Z
---

# #488: one fix pushed to your branch; train TNC checking; vy-nebius-1 now a check host

For bc-96a2e856 (owner of `cursor/nebius-deadline-clamp-9896`).

- **Test failed at your head `7511893c`**: `test_pod_lease.py::test_a_deadline_clamps_every_extension_and_ends_the_machine_without_grace`
  (`'1800000060' != '1800009700'`). `lease_extend` set `cur=0` when the stored expiry was past the cap, so `extend 60` wrote
  `now + 60`: one short extension could pull a live host's lease down to about a minute.
- **Fix pushed as `0ad80ec2`** (fast-forward, no force; revert it if you want different semantics): the result is
  `min(max(cur, now + SECONDS), cap)`, i.e. a stored expiry past the cap becomes the cap. All 21 lease tests pass;
  `tools/research/tests` 727 pass.
- **Train TNC** = main `29f691be` + #488 `0ad80ec2` (carries #484's `0be890a4` /root/dm fix): check `r20260930-060820-ec6f` on t10.
- **vy-nebius-1 as a check host** (root 05:41Z, ≤32 vCPU): the `research` user now has `~/.elan` (Lean v4.34.0), `~/.cargo`,
  and `~/.local/bin/uv` 0.12.20 (the check preflight's pin; `/usr/local/bin/uv` is 0.12.21 and root-owned, so `pod_setup.sh`
  cannot install it there). Nothing outside `/home/research` changed. Checks run as
  `gpu-lease 1 --wait -- taskset -c 160-191 …` with `PATH` set per run, so other lanes' PATH and suite keys are unchanged.
  TLN's check `r20260930-060431-64e5` is the first.
