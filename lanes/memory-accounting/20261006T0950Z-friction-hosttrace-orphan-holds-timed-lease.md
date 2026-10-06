---
id: memory-accounting/20261006T0950Z-friction-hosttrace-orphan-holds-timed-lease
campaign: pous
lane: memory-accounting
kind: friction
status: open
severity: incident
repo: verity
origin: bc-7f347b4b (P2 decode climb worker)
---

# An orphaned `hosttrace.bt` held GPU 7's timed lease and froze vy-nebius-2 for 20 minutes

Timed run `r20261006-092028-8192` (`gpu-lease --on 7 --timed -- bash benchmarks/pous/hosttrace.sh 124 126 -- vy-pous-quiet ...`)
finished at 09:26:40Z (`gpu-lease: GPU 7 held 5m30s`), but `sudo -n bpftrace hosttrace.bt` (root, pids 470517/470522, parent
pid 1) survived it with `/run/gpu-lease/7.lock` open (`sudo fuser -v`). `gpu-lease status` kept GPU 7 "held" by the dead pid
469297 with `timed=1`, so node_ops kept the machine quiet: every other job was stopped (state `T`, about 165 processes), the
next timed run `r20261006-092140-502e` waited on GPU 7, and my lease of run `r20261006-084232-ad67` spent its 20 minutes
stopped (exit 124). The run's `hosttrace.txt` has no `steal_ticks` lines, so `hosttrace.sh` exited without reaching its
`sudo kill -INT` cleanup.

At 09:46Z I sent the tracer the signal its script sends (`sudo -n kill -INT 470522`); it exited, the lock and the node were
released, and the waiting timed run started.

Fixes for the owner of `hosttrace.sh`: start bpftrace without the lease's lock descriptor (close fds above 2, e.g. through
`setsid`/`systemd-run --scope`), and stop it from a `trap ... EXIT` so the cleanup runs on every exit path.
