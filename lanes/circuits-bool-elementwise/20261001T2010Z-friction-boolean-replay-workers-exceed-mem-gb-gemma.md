---
id: circuits-bool-elementwise/20261001T2010Z-friction-boolean-replay-workers-exceed-mem-gb-gemma
campaign: verity
lane: circuits-bool-elementwise
kind: friction
status: open
severity: incident
recurs: note:circuits-bool-switch/20261001T1251Z-friction-replay-workers-exceed-mem-gb
repo: danielreuter/verity
origin: circuits-bool-elementwise
---

# Gemma-2-2B's `boolean-replay` with 30 workers filled a 400 GB `research run` cgroup and died by SIGTERM with an empty stderr

`r20261001-183627-ffcb` failed at 12:40 PM PDT, after a 58-minute prewarm. The parent held the compiled Boolean versions of the
picked specs at 328 GB RSS; 90 s after it forked 30 workers, the scope was at 414 GB of 400 GiB. One OOM kill followed, then SIGTERM
(rc 143), with nothing on stderr. This missed the 11:20 deadline and cost about an hour of node time. The rerun is
`r20261001-200753-63d1` (12 workers, 1,100 GB). The fix proposed in the earlier note still applies: size `--replay-workers` from
the parent's RSS after the prewarm and the cgroup's `memory.max`, and name the OOM kill instead of exiting 143.
