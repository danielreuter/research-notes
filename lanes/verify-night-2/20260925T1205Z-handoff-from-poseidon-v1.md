---
lane: verify-night-2
kind: handoff
from: poseidon-v1
created: 2026-09-25T12:05Z
---

# verify: A100 BF16 +hash re-measured with the MALLOC vars: art:ba387d41 (n=4096, plateau of a sweep bounded by the frozen set)

This is a new result, not a relabel: the A100 row of my 0835Z/0900Z handoffs (art:af008992, which you accepted), re-measured with
MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 set (coordinator 1003Z; recorded in `meta.protocol.malloc_env`).
Tree: lane/poseidon-v1 7ffb7095 = main 3301c435 + the hash-commit `--commit-reps` harness. Pod 25b8diy5t3f3tc (A100-SXM4-80GB,
US, EPYC 7742), BENCH_INSTANCES=1 (frozen arrays matched the manifest), run r20260925-115155-e772.

| result | n (B) | run-files tree (full) | sub-batches | commit-evidence sha256 | rep-1 stmts digest |
|---|---|---|---|---|---|
| art:ba387d41cb12945914624f0cbdabb4b3a8ffc2675779e1f7f17cc6dea8840f07 (plateau) | 4096 | art:5eb0b2cc73fb55da05902920afe9d7467d330e3036312b0c890588e7935ce320 | 25 | 71b51d0bfdd7bdb5... | 25:d54de18b83eb072017ed9... |

- Config: `bf16-ampere --auth included-hash` (frozen bench-instances/v1 vu-k1536), --batch 16384 --pipeline 8, zk interactive,
  --target -128, --reps 5, --commit-reps 5, rep 1 dumped. The sweep is 1024 / 2048 / 4096, capped at the set's 4096 instances
  (meta.sweep.rule says so). Commit evidence and statements equal art:289841b1 / art:af008992 (the same frozen set); the proofs are new.
- Byte identity at n=4096 vs main's pre-b862be30 committer: IDENTICAL (16.05 s vs 0.063 s), evidence tree
  art:ab442c560592472926d1ee708d4c308c394284ee389a842c9c57529c70e83ea2.
- Producer-side Rust batch accepted 25/25. The 1024 and 2048 points are slim (art:266c210f, art:9d808b33).
