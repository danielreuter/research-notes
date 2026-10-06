---
id: network-accounting/20261006T0625Z-friction-node1-gpu-jobs-share-cpus
campaign: network-accounting
lane: network-accounting
kind: friction
status: open
repo: danielreuter/verity
origin: network-accounting live online-sync sweep (agent bc-7f347b4b)
---

# On node 1, every queued GPU job's CPU set is the same 96–127, so a latency-bound cell shares its cores with other lanes' CPU work

`research run --queue --gpus 1 --cpus 16 --on vy-nebius-1` gives each job the affinity 96–127, whatever `--cpus` says. On
6 Oct my sweep's two cells (one GPU each) split it into two 16-CPU halves under a flock in the job, as 4 Oct's runs had.
Other lanes' jobs ran on the same cores at the same time (a `verity_flock` CPU stage at 100% and a custody triage), with the
node's load average near 414 on 160 CPUs.

The warden's proxy has a 25 ms slack per release (verity#1146): a request not written upstream by its release tick plus
25 ms fails its window closed. On the shared cores, ticks stalled for tens to hundreds of ms and whole bursts went out late:
- r20261006-031529-0590, r20261006-031802-13b9 and r20261006-040542-d15e accepted 20–26 of 70 link-windows, almost all
  rejections `delivery-refused`.
- The same envelope cell at `--nice -20` (r20261006-042805-434a) accepted 67 of 70.

It got worse through the day: at 09:00Z other lanes' Lean builds and Python jobs filled 96–127 (load average 218), and
by 11:26Z the load average was 265. The same envelope cell accepted 6 of 16 link-windows at 08:55Z, and the Qwen3-8B
envelope 24 of 70 at 09:50Z (note:network-accounting/20261006T1201Z-report-live-online-sync-sweep).

About 2 GPU-hours went to cells whose acceptance measured the co-tenants rather than the warden. What I did instead: run
every later cell at `--nice -20`, and read a cell's acceptance together with its proxy's tick lateness and late forwards.

The better abstraction: a queue job that asks for `--cpus N` gets N cores of its own (an `AllowedCPUs` slice in its scope),
or a flag for latency-bound jobs that keeps CPU-phase work off their cores.
