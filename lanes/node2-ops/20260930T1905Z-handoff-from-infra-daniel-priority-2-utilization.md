---
id: 20260930T1905Z-handoff-from-infra-daniel-priority-2-utilization
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: take the 18–19Z hour, then Daniel's priority 2 (a standing GPU backlog, CPU fill, and an hourly useful-versus-filler report)

Start by confirming you own the node (owner file), then adopt `/workspace/pouw/infra/lane/`. Read the hand-back note in full,
including the fill runner's missing supervisor loop.

None of the items below changes the node. They use only the existing fill queue and `gpu-lease`.

1. **The 18:00–19:00Z hour is yours:** the old lane's partial figure is 77%.
   - Write the hour's busy % in ops.md, plus a one-line handoff to `lanes/pous/`.
   - Commit a cap on `gpu-lease`'s usage report (`busy_s` and `sampled_s` no more than `held_s`) on `infra/nebius`. Don't
     deploy it; list it in ops.md under "held for the next approved deploy".
2. **An hourly report for node 2**, in `utilization-report.json` and ops.md. Report GPU busy %, CPU busy % (not counting the
   reserved check CPUs), and the useful share against the filler share. Filler must carry a label in the fill header. The
   proposed target is ≥95% GPU busy, with ≥90% of it useful.
3. **A standing GPU backlog, in priority order,** agreed with the RTX PRO coordinator bc-2aa33ad8, so no GPU waits on a lane's
   turn.
   - Reach bc-2aa33ad8 through `lanes/pous/`, asking the pouw coordinator to relay.
   - When the queue runs dry, name the missing work and its owner, every hour.
   - Run filler only when nothing useful is queued. It must be labeled, and never ε_R or seed padding.
4. **CPU fill outside timed windows:** verifies, tests, Lean, censuses and captures, as `gpus=0` fill jobs that freeze in
   windows. Not through the held Verity CPU pool.
5. **Record node 2's GPU-to-NUMA layout, once and read-only:** run `nvidia-smi topo -m` and `lscpu | rg NUMA` outside a timed
   window. Write the map in ops.md and in a handoff to `lanes/infra/`.
6. **The cutover plan's step 1 asks for node2-ops's agreement**
   (`lanes/infra/20260930T1858Z-handoff-from-pous-one-cluster-to-infra-cutover-plan.md`). Answer yes or no in `lanes/infra/`,
   with each condition on one line.
