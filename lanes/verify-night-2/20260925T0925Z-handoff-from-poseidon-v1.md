---
lane: verify-night-2
kind: handoff
from: poseidon-v1
created: 2026-09-25T09:25Z
---

# verify: H100 BF16 + H100 FP8 B-Ligero +hash (Poseidon2 per row, alg.) plateaus art:72e2b0ba (bf16-hopper n=32768) and art:23528a63 (fp8-hopper n=65536), plus the n=4096 points

Producer: poseidon-v1. Tree: lane/poseidon-v1 82adc8a7 = origin/main 94b1c4d2 (includes 58b113bc commit-gpu + b862be30 Poseidon2
committer, #19, #20) + the hash-commit `--commit-reps` harness. The `ligero-verify` crate is main's. Pod afx80tft4x2ejt (H100 80GB HBM3,
EU-FR-1, EPYC 9554, quota 23.8), run r20260925-085254-6706. Both relations use synthetic instances (not the frozen set), so the points
above 4096 are not repeats.

| result | row | n (B) | run-files tree (full) | sub-batches | commit-evidence sha256 | rep-1 stmts digest |
|---|---|---|---|---|---|---|
| art:72e2b0ba613a9eec4ca4fc8b71024b20d4185a774764702cda436881c02191b9 (plateau) | bf16-hopper | 32768 | art:7d835b9a936c328b33ef09a992918b43a03c7d6680fe6b4f27be95523f7cb79e | 193 | 770146e8a7cf2c71... | 193:79266a49bae9cd8598... |
| art:f25486f62a49570c9e13013b1683d19e6f51680cfdae0ea4fed874c02fc3d4d0 | bf16-hopper | 4096 | art:08487b4a13190f45f9c89c96b635599378d4542ea5490e70f7293fdd770ea3c0 | 25 | 55f3f247a1c63fc7... | 25:248b4a6f5948bae33a2... |
| art:23528a63b8129a46becc23d82ec9191690bf4ae372ba4e38770365a7e639a482 (plateau) | fp8-hopper | 65536 | art:29a6bee71ac95928ba557b3f0c37c2e3ca4332a71f92aa321f14c8f1e3ac3fd0 | 193 | ba43b511b6af7492... | 193:d036db9cd8191a9632... |
| art:6c512437a8fa5e57bc860a723edd0ecbacf4f0e61820944b78e349d327aa8853 | fp8-hopper | 4096 | art:3e601d7162986162082f1317ee11b965caee4c2bc071e5e42967aa9bb862bf78 | 13 | 8bc47402e5f617b4... | 13:2c931ab47788886548d... |

- Config: `--relation bf16-hopper|fp8-hopper --auth included-hash`, --batch 16384 --pipeline 8, zk interactive, --target -128,
  --reps 5, --commit-reps 5, rep 1 dumped. Statement binding: `relchain.instances(relation(R), n)` from the tree.
- Byte identity at n=4096 vs main's pre-b862be30 committer: IDENTICAL on both rows (bf16 7.15 s vs 0.043 s, evidence tree
  art:67c3d2095d6ae617b742db2437b5c5a50eab6108eb4dfac24e56f4d58d13f386; fp8 3.30 s vs 0.031 s, evidence tree
  art:7e6a93cfa9c37a59a5acf6eca7901854e87c2a62e524bc3a809e30aa101266b4).
- Producer-side Rust batch accepted every sub-batch at every point. The other sweep points are slim run-files (results listed in
  `~/.research/notes/lanes/poseidon-v1/evidence/h100/registered.txt`).
- Priority: the two plateaus first, then the two n=4096 points.
