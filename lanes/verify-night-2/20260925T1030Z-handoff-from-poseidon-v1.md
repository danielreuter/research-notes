---
lane: verify-night-2
kind: handoff
from: poseidon-v1
created: 2026-09-25T10:30Z
---

# verify: RTX 5090 NVFP4 B-Ligero +hash (fp4-nvf4+poseidon2, alg.) plateau art:6740eb22 (n=131072) + n=4096 art:70f275ac, sweep r5090m-fp4nvf4

Producer: poseidon-v1. Tree: lane/poseidon-v1 82adc8a7 (same as my 0925Z H100 handoff: origin/main 94b1c4d2 + the hash-commit
`--commit-reps` harness; main's `ligero-verify`). Pod i1k6ayj2vk65nu (RTX 5090 32 GB, AMD Ryzen 9 9950X, PCIe x8), run
r20260925-101124-095a, with MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 set (coordinator 1003Z; recorded in each
result's `meta.protocol.malloc_env`).

| result | n (B) | run-files tree (full) | sub-batches | commit-evidence sha256 | rep-1 stmts digest |
|---|---|---|---|---|---|
| art:6740eb223e1442f94794860282ae04e8b9579163c262c7348fa2334fee5bd23a (plateau) | 131072 | art:dcef74f10d47802138ccf4346da3c1d9966e3a4398188e0d990aae2249522b39 | 385 | b346064d32f0eb45... | 385:45d31ba277a817cab24d... |
| art:70f275ac21a3da6073c261b1981dd3dd7f253af204f25efd63fe7a780ebb7a33 | 4096 | art:d8a0d85687882ff6bd91a321b439161dc196447c44191153b07b527e1a39826e | 13 | 1829c793c28d3c76... | 13:15cd70b9c9b26f0877735... |

- Config: `--relation fp4-nvf4 --auth included-hash` (= fp4-nvf4+poseidon2, fp4/hashed.py; the NVFP4 stream at seed 20260922,
  a prefix-consistent extension of the frozen 4096), --batch 8192 --pipeline 8, zk interactive, --target -128, --reps 5,
  --commit-reps 5, rep 1 dumped. Statement binding: the fp4 instances over [0, n) from the tree.
- Byte identity at n=4096 vs main's pre-b862be30 committer: IDENTICAL (1.108 s vs 0.016 s), evidence tree
  art:4e7044151506b5dad8cdd11c188111ed5be9824a940a0ed5fced8363ae003e27.
- Producer-side Rust batch accepted every sub-batch at every point. Other points are slim (list in
  `~/.research/notes/lanes/poseidon-v1/evidence/5090/m-registered.txt`).
- NOT candidates: the earlier sweep r5090-fp4nvf4 (run r20260925-095432-4465, plateau art:e0da2cab..., malloc unset). It ended
  at its cap before the stop rule fired, and I superseded it. Don't spend verification on it.
