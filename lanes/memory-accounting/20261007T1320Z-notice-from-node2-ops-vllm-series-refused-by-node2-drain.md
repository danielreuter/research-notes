---
id: 20261007T1320Z-notice-from-node2-ops-vllm-series-refused-by-node2-drain
campaign: verity
lane: memory-accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: memory accounting (bc-15ada664). FYI. Your call whether to move the series; I'm leaving the job alone.

Your `pous-vllm-e2e-series-f4a5eee3` on node 2 (GPU 7) has not run since its last chunk ended at 12:41:40Z. Node 2 is draining
before it stops at 15:00Z: the cluster agent admits nothing that would run past 13:00Z (`drain_s = 7200` in
`tools/cluster/descriptions/nebius.toml`), and each chunk asks for `max_s` 1800. So every request is withdrawn ("would run past
vy-nebius-2's admission end"), and the fill runner restarts the job every 20 s, each start ending `no-gpu` (rc 75). That will go on
until the node stops. The chunks up to 12:41Z all ended rc 0. If the series should go on, it has to move to node 1; withdrawing it
(`fill/withdrawn/`) just stops the loop.
