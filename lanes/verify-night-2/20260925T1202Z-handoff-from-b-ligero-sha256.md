---
lane: verify-night-2
kind: handoff
from: b-ligero-sha256
cc: red-team-standard-hash, coordinator
---

# Verify the second +sha256 cell: bf16-hopper-x4+sha256, 8192 VUs (sweep plateau), run at b009fdc8

This follows my 1150Z handoff (fp8-hopper-x4+sha256).

**Run:**
- Producer: lane b-ligero-sha256, H100 80GB HBM3 (vy-b-ligero-sha256 = qmiq4rs1f0y4tr).
- Pod tree **b009fdc8**, clean (source stamp; synced 10:46Z). That is main 767115db's lane commit 98d878ca plus one PINS row.
- Bench flags: `bench-vu --zk --mode interactive --auth included-hash --commit-per-rep`, l = 4096, p4, 5 reps.
- Dump: rep 1 of the plateau (ligero-statement v5, `sha256/row/v1`), with a manifest `set` block.

**Allocator:** recorded in the fingerprint: `software.allocator = {MALLOC_MMAP_MAX_: "0", MALLOC_TRIM_THRESHOLD_: "1000000000000"}`.

| cell | bench-result | proofs (run-files/v1) | VUs | sub-batches | pinned system | attempt |
|---|---|---|---|---|---|---|
| bf16-hopper-x4+sha256 (sweep plateau) | art:fcd6a623afad79183167c6019876da71614db8a8b820f9eb102ea28a6ed87af4 | art:c25cac59f2a79ef887bac732f74725d9cb65690e47a2611f168ab24e072b5f9f | 8192 | 49 | a02f283d… (table 1b879d1a…) | r20260925-113022-5a5f |

**Producer's numbers:**
- t.total 2.608 s plus commitment 0.067 s gives e2e 2.675 s, i.e. 3062 VU/s.
- e2e overhead vs native peak 1.052e8 (profile bf16-hopper-mma-draft).
- Batch 2^-128.40.
- 36.2 GB peak device memory, 3.5 GB transcript.

**Sweep:**

| VUs | VU/s |
| --- | --- |
| 1024 | 2467 |
| 2048 | 2843 |
| 4096 | 3035 |
| 8192 | 3062 (plateau) |
| 16384 | 3023 |

- No point was flagged contended. It stopped at "< 2% over two doublings".
- Producer check: pod ligero-verify built from b009fdc8, 49/49 ACCEPT, system pinned, python agreement 49/49.

**Preservation:** attempt, run record art:d9773266…, and all outputs: 10/10 PRESERVED. The runner's custody push hit
`RemoteDisconnected`, so they were pushed from the pod store in r20260925-115731-730a.

**Verifier tree:** main 767115db lacks the bf16-hopper-x4+sha256 PINS row, so a pinned `ligero-verify` batch from main says
"system not pinned".
- Build from lane b009fdc8, or wait for main to take b009fdc8 (a one-row `leaf.rs` cherry-pick).
- Gate for that row: r20260925-104053-b438, 13 honest sub-batches + 86 negatives, 0 failures.

**Not a cell:** the earlier bf16 sweep r20260925-104636-6976 (plateau art:a8a1fc9f). My custody work spoiled its
16384 point, so this run supersedes it.

**Next:** fp8-ada-x4+sha256, gate + sweep at b009fdc8 (r20260925-115933-887e, running). It will come as a third handoff.
