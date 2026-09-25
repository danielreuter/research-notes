---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T10:37Z
---

# 3 re-measured B-Ligero +blake3 RTX 4090 cells with the malloc env (coordinator 1003Z): new results, the earlier ones stand

These follow my 0958Z / 1008Z handoffs. The tree, flags and verifier are the same (806a2f73; l = 4096, p2, 5 reps,
`--commit-per-rep`, GPU committer; reverify with R1 + R2 + R4). They add `MALLOC_MMAP_MAX_=0
MALLOC_TRIM_THRESHOLD_=1000000000000`, which is in the run's job.json env and in lib.sh. Pod: vy-b-ligero-sh.

| Line | bench-result | proofs (run_files) | VUs | sub-batches | t.total | commit | e2e | VU/s | attempt |
|---|---|---|---|---|---|---|---|---|---|
| fp8-ada+blake3 (frozen `e66ff0f2…`) | art:9b80f566838f4956ecc85df853c718ddfe07a5af8682dd69f29b3c7df75ae611 | art:0c5840907e1c24fe8190d0af2b0e32763494ba413b939e0b8d8cf9195f569b4e | 4096 | 49 | 3.547 s | 0.011 s | 3.558 s | 1151 | r20260925-102900-4391 |
| fp8-ada-x4+blake3 (`c86e51a1…`) | art:050ddede1083ac67f417d2345d5b1f0a8d47314c94ee5a9988d7f1cdb8300650 | art:ef264ad325e8207dae1b75b2d09b35d13cfbfe1b1c717bc40592afd69043df62 | 4096 | 13 | 1.973 s | 0.009 s | 1.981 s | 2067 | r20260925-102900-4391 |
| fp8-ada-x4+blake3 (sweep plateau, `sweep` block) | art:19be6afa2cd2239cf15f7878af8eae0a3523be86dbec8e92f3acd9d6ee3ebbd1 | art:a3d4b768d9808c55be90c98bd54fa10b5dd993faec8e2cb90a622bd912862e3a | 8192 | 25 | 3.768 s | 0.016 s | 3.784 s | 2165 | r20260925-100526-b232 |

- The producer's check (not a label): the pod's Rust batch gave ACCEPT on every sub-batch with system pinned. Union bounds
  were 2^-128.40 / 2^-128.33 / 2^-128.05.
- The other points of the plateau's sweep hold no proofs: p0 art:29babef7…, p1 art:71968345…, p2 art:fdee8f4d…, p4 art:76375445….
- The x1 sweep with the malloc env is running (r20260925-103611-67e0). Its plateau will follow.
