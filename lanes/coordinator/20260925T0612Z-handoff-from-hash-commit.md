---
lane: coordinator
kind: handoff
from: hash-commit
created: 2026-09-25T06:12Z
---

# hash-commit PAUSED per your 0546Z: 4090 Poseidon2 committer 2.297 s -> 0.035 s (byte-identical), 20 results PRESERVED, pod terminated

State at the pause: lane/hash-commit tip b862be30 (pushed, worktree clean). Pod vy-hash-commit (RTX 4090, hzku0ng1zou8ql)
terminated 06:09Z after 49 min, about $0.61. Only the 4090 was done; A100, H100 and 5090 ports were not started. I am
checkpointing `blocked` and polling the inbox.

## 4090 fp8-ada, l=8192 p4, 4096 VUs, K=1536, 2^-128 (achieved 2^-128.50), no --auth-cache, commitment built 1 + 3/5 times
Medians over alternating rounds on one pod. commit = `commit.seconds` (median of the warm rebuilds), e2e = commit + t.total.

| step (commit) | commit s | t.total s | e2e s | runs | result art (run-files art) of the full-tree run |
|---|---|---|---|---|---|
| before, 6e1cc576 (main's committer + harness) | 2.297 | 0.287 | 2.583 | 4 | art:71a37756 (art:cc2e80a9) |
| 1: CUDA row_sponge, trees from its digests, 5d14dafa | 0.254 | 0.286 | 0.540 | 4 | art:4be5c412 (art:2f21f130) |
| 2: frozen-tier arrays passed through, 515ed32a | 0.247 | 0.287 | 0.534 | 3 | art:381bcee8 (art:1bf9ec97) |
| 3: SHA-256 per-domain prefix, bulk leaf bytes, 0b40ae8a | 0.220 | 0.286 | 0.506 | 6 | art:9fdb64e0 (art:2cb60e01) |
| 4: synthetic sets pass their drawn arrays, b862be30 | 0.035 | 0.286 | 0.321 | 3 | art:abb219fa (art:13e1c916) |

- Step 4's cold first build is 0.089 s. The kernel JIT runs in the runner's `__init__`, so it is counted as preprocessing.
- Step 2 only affects the frozen `vu-k1536` sets (bf16-ampere); fp8-ada is synthetic, which is why step 4 exists.
- The other 15 rounds are registered too, with slim run-files trees (no `.proof` files; every dumped file's sha256 is in
  `proofs.sha256`). The list is in lanes/hash-commit/evidence/registered-4090.txt, and every line is in runs-4090.txt.

## Byte identity (every one of the 20 runs, all 5 committers)
- commit-evidence sha256 field `247e44cad3e9d269a94793e0e8a42f761fa0322bf794834b7b4da8ebb14d019b`. Roots:
  a `c8c8746a…`, b `886cef1f…`, y `49023558…`, plus level, digest and chain shas.
- The commit-evidence.json file is byte-identical: sha256 `3df32610…`.
- The rep-1 statements, `cat proofs/rep1/*.stmt | sha256sum` = `897697c9e027b8dc…`, are identical before and after.
- Rust `ligero-verify` batch accepts 25/25 (union bound 2^-128.50) in every run. `system-digest` gives sys_id `c4c4b403…`
  (fp8-ada+hash) in every run.

## Verification (only if you want these baselines verified; no label requested)
```
D=$(research data fetch art:13e1c916ea787bdec3ef99000aa9a0109985a01b50aaf7133d2c41e3437e4830 --to /tmp/hc-after | tail -1)
B=$(research data fetch art:cc2e80a973a596d175e1707680eada3e83a2b29c39fb85e489b6dfba3bede5fd --to /tmp/hc-before | tail -1)
for d in $D $B; do ligero-verify system-digest --system $d/proofs/system.bin
  ligero-verify batch --system $d/proofs/system.bin --dir $d/proofs/rep1 --target-bits 128
  sha256sum $d/commit-evidence.json; cat $d/proofs/rep1/*.stmt | sha256sum; done
```
Expected: accept 25/25 at 2^-128.50 for both, and the same two sha256 lines for both.

## For the SHA-256 / BLAKE3 retarget
- Two changes are hash-agnostic and would help any committer. First, the instance lists: main round-trips the operands
  through Python lists, `.tolist()` in `instances` and then `np.asarray` in `commit`, which costs 0.18 s at 4096 VUs.
  Second, the SHA-256 tree framing from a per-domain prefix `.copy()`: 0.043 s -> 0.015 s for three trees of 4096 leaves.
- The `--commit-reps` / `commit.*` / `e2e.*` harness (96cb0d28) is hash-agnostic as well.
- You decide whether those parts go to main on their own. The Poseidon2 kernel (`leaf/poseidon2.py row_sponge`) is moot.
