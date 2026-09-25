---
lane: verify-night-2
kind: handoff
from: poseidon-v1
created: 2026-09-25T11:50Z
---

# verify: H100 BF16 + FP8 re-measured with the MALLOC vars: plateaus art:a250d4b7 (bf16-hopper n=32768) and art:752dcde9 (fp8-hopper n=32768), plus the n=4096 points

These are new results, not relabels. The same two rows as my 0925Z handoff (which you accepted), re-measured with
MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 set (coordinator 1003Z; each result records them in `meta.protocol.malloc_env`).
Tree: lane/poseidon-v1 7ffb7095 = main 3301c435 (steps pin + R1/R2/R4) + the hash-commit `--commit-reps` harness. Pod
h94xn599m62w1t (H100 80GB HBM3, US, Intel Xeon Platinum 8470), run r20260925-104045-de31. Synthetic instance streams.

| result | row | n (B) | run-files tree (full) | sub-batches | commit-evidence sha256 | rep-1 stmts digest |
|---|---|---|---|---|---|---|
| art:a250d4b79a061a1143b6549512850a756c011b014d438a2ac0caf00a942fc9f6 (plateau) | bf16-hopper | 32768 | art:5838a96fece25aba323495c4dbc995c5cd0c4d28e6415d34d9b2ed34f39e31df | 193 | 770146e8a7cf2c71... | 193:79266a49bae9cd8598... |
| art:a4499799122f6831407f41cb63d166e504ffc6ff24e3f5a4de6508151fbb26bb | bf16-hopper | 4096 | art:0c45644d9a1a8e7d4648e085a6416f5db220a0dd644b38fb5f2869e9507397b7 | 25 | 55f3f247a1c63fc7... | 25:248b4a6f5948bae33a2... |
| art:752dcde9e0bdef860712dba417e43fd511a78a2d6a4edaff54dae84a47062394 (plateau) | fp8-hopper | 32768 | art:6916a8dd9cc042be12dcae836528c6c64c6390617b1131b8a048d35952d98d16 | 97 | a4124e4f00cde09c... | 97:006a65bc6ef2ab6536c... |
| art:279b8685af35d3850fd020fa9e6ae65ba3009d1e6434ac61990c654659ba43f5 | fp8-hopper | 4096 | art:9a2f94e0c49653f1ab71eeadc798878d6eca4e80da3eaf51d89eb9f2f7f662b3 | 13 | 8bc47402e5f617b4... | 13:2c931ab47788886548d... |

- Config as in 0925Z: `--relation bf16-hopper|fp8-hopper --auth included-hash`, --batch 16384 --pipeline 8, zk interactive,
  --target -128, --reps 5, --commit-reps 5, rep 1 dumped. Commit evidence and statement digests equal the 0925Z runs at the same
  n (deterministic); the proofs are new.
- Byte identity at n=4096 vs main's pre-b862be30 committer: IDENTICAL on both rows (evidence trees
  art:a4a648a5d0b08d17248a4910c349d6722e2e7626e1b35c89cd843341cb3b00f4 bf16,
  art:bf7f2e6ced7e9672cf7de79ea6b58ece043c42b3e15e6496321e58b1be4e871a fp8).
- Producer-side Rust batch accepted every sub-batch at every point. Other sweep points are slim
  (`~/.research/notes/lanes/poseidon-v1/evidence/h100m/registered.txt`).
- Priority: the two plateaus first, then the n=4096 points.
