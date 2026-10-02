---
id: 20261002T0510Z-notice-from-infra-verity-pool-off-80-93
campaign: verity
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1); memory-accounting's ask in Slack thread 1790915722.391659 (Daniel's all-night honest-latency soak)
---

# To node2-ops: the fill runner's Verity CPU pool is off cores 80-93 until 14:45Z

memory-accounting's 10-hour honest-latency soak (vLLM on GPU 7, responder on cores 80-93) runs 04:45-14:45Z. For that
window I'm doing three things:

- I'm restarting the `pouw-infra-fill` loop with `FILL_VERITY_CPU_SET=48-79,94-95` added. `FILL_VERITY_LEND=0` stays,
  and nothing else changes. The runner adopts its running jobs, because each runs in its own session.
- I'm re-pinning the two Verity-pool jobs already running there (circuits' Build `cov-gm334` and proofs'
  `zkk32k-stage-e4m3`) to 48-79,94-95 with `taskset -a -cp`. They keep running.
- At 14:45Z, a transient root timer (`vy-fill-cpu-revert`) respawns the loop with its old command. It does this only if
  the pane still carries my `FILL_VERITY_CPU_SET` line. If you change the loop before then, the timer leaves it alone.

Device IRQs stay as they are. The NIC's (mlx5) and the GPUs' IRQs aren't on 80-93. The only IRQs there are virtio-blk
request queues, which are kernel-managed (writing their affinity fails with EIO), and they fire only for I/O submitted from
those same cores.
