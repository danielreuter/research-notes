---
id: 20261001T0730Z-handoff-from-proofs-bf16-hill-kcompactd1-on-prover-slots
campaign: overnight
lane: infra
kind: handoff
status: open
repo: verity
origin: proofs-bf16-hill
---

to: infra; cc proofs.

# Node 1's NUMA node 1 is out of memory: kcompactd1 burns a core on the provers slots

**Finding.** `r20261001-071235-2b1a` (BF16 K=16384, submitted 07:06Z, slot 128–143) is flagged `cpu-slice-shared`, with 0.97
foreign cores on its slice. The source is a kernel thread, not a job: `kcompactd1` (PID 1191, allowed on 96–191) uses
1.02 cores without pause. At 07:25Z it was on CPU 131, inside that slot. It wanders over NUMA node 1's CPUs, which include all
four provers slots, so any timed point can draw it.

**Cause.** NUMA node 1 (CPUs 96–191) has 19 GB free of about 880 GB. Node 0 has 458 GB free. Node 1's free pages are all
order 0 or 1, so the kernel is compacting all the time (`compact_stall` 4.29M, `compact_fail` 3.88M). Every provers job
allocates on node 1, and those allocations also stall in direct compaction. That may be part of why clean step-0 points vary
about ±12% between runs on the same binary and slot. On node 1: anonymous memory 380 GB, Shmem 228 GB, inactive page cache
198 GB. The largest holders, all on node-1 CPUs (96–127 now, plus 176–191 for pods started before the restart), are circuits'
`verity_vllm.pipeline.cli commit --case GEMMA2_2B` processes (PIDs 567492, 569456, 570578, 4155231 and 93134, together about
320 GB), two `global-program` processes (65 GB together) and the vLLM workers.

**Fixes (root):**
- Take the thread off the slots now: `taskset -p -c 96-127 1191`. kcompactd has no affinity lock.
- Make it run less: `sysctl vm.compaction_proactiveness=0` (now 20). Freeing node 1's inactive page cache
  (`echo 1 > /proc/sys/vm/drop_caches`) gives the zone high-order blocks back.
- Structural: every non-provers dispatch task now starts on 96–127, which is node 1, so circuits' memory and the provers
  share one NUMA node while node 0 sits half empty. Starting the dispatch range on node 0's CPUs (or `numactl --preferred=0`
  for memory-heavy tasks) would separate them.

I'm not re-running 2b1a in a loop. If kcompactd1 lands on one of my points again, I'll add that run id here.
