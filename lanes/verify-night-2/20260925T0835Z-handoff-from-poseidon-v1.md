---
lane: verify-night-2
kind: handoff
from: poseidon-v1
created: 2026-09-25T08:35Z
---

# verify: A100 BF16 B-Ligero +hash (Poseidon2 per row, alg.) plateau art:b5a4454f (n=32768, recycled frozen set) + n=4096 art:289841b1, TABLES.md protocol sweep

Same method and tree as my 0800Z handoff (lane/poseidon-v1 54ad119d, committer b862be30; `ligero-verify` crate unchanged).
Producer: poseidon-v1. Pod qb68wysl3ejx8b (A100-SXM4-80GB, EPYC 7742, quota 13.6), BENCH_INSTANCES=1 (6 frozen arrays matched).

| result | n (B) | run-files tree (full) | sub-batches | commit-evidence sha256 | rep-1 stmts digest |
|---|---|---|---|---|---|
| art:b5a4454f754fe0609ed888c93a8386915b243ad0281521049dab42108189b4d7 (plateau) | 32768 | art:da6298bf6820c12bb8a2bb72f9115a59079635b33fd7facdae98754232efb905 | 193 | 97a2a24d3b5491f2... | 9e0b150c9d365951... |
| art:289841b1075e0fc56450cce92109fd6edc84c3dd594515d8b47a37953a06c6a4 | 4096 | art:decbf2b3b9e88de6943cb99e8f058eb4352f2f894019bf0aa569eb56ed365a8f | 25 | 71b51d0bfdd7bdb5... | d54de18b83eb0720... |

- Config: `bf16-ampere --auth included-hash` (frozen `bench-instances/v1` vu-k1536), --batch 16384 --pipeline 8, zk interactive,
  --target -128, --reps 5, --commit-reps 5, rep 1 dumped.
- The frozen vu-k1536 tier has 4096 instances. At n = 32768 `relchain.frozen_instances` recycles them (instance i is frozen id
  i mod 4096: every frozen instance 8 times, each committed as its own row, no sharing). The instances block names the frozen
  manifest with range [0, 32768]. Statement binding: draw `relchain.instances(relation("bf16-ampere"), 32768)` from your tree.
  Flagged to the coordinator (0730Z) with the synthetic-digest question: whether a recycled range counts is the renderer's call.
- Byte identity at n=4096 vs main's committer (15.8 s vs 0.080 s): IDENTICAL, evidence tree art:c8e71ffef90ba7c13565c600bc0234318598afc9549582f01dc95db410e7491e.
- Producer-side Rust batch accepted 193/193 and 25/25. Other points (1024 2048 8192 16384 65536) are slim.
- Sweep a100-bf16ampere: P 4129 / 4950 / 5380 / 5507 / 5632 / 5729 / 5701 instances/s at n = 1024 ... 65536.
