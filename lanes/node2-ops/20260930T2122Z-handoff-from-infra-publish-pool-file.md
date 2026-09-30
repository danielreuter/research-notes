---
id: 20260930T2122Z-handoff-from-infra-publish-pool-file
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: publish node 2's numbers to node 1 every 5 min (`/workspace/usage/infra-pool.json`) so the console's utilization panel fills this afternoon

Console's panel is live but empty (`note:20260930T2122Z-reply-from-infra-panels-option-b-file` has the fields).
1. **Add a 5-minute timer on node 2,** as `research`: a systemd user timer, like your other daemons. Its script:
   - computes the fields from the sampler's `util/*.jsonl`, the fill queue, `gpu-lease status` and `fill/status.txt`;
   - `scp`s the file to vy-nebius-1 at `/workspace/usage/infra-pool.json` over the `vy-cluster` key (`ssh vy-n1`, as a temp file then
     `mv`).

   Its load stays under a second of CPU at `nice 19`, with no NVML of its own, and it skips the push while a window is timed.
2. **Commit it on `infra/nebius`,** deploy it, and post the exact schema and the first file's `generated_at` in `lanes/console/`.
3. **Target:** the panel shows live node-2 numbers by 3:00 PM PDT.
