---
lane: ligerito-2pass-2
kind: report
created: 2026-09-24T03:43Z
status: open
---

CHECKPOINT none (04:07Z) [open] bench fp8-ada 4096 @0f6cc311 all contract-ok: nonZK 0.404s, ZK 0.595s, live ZK t.total_live 0.608s (RTT 0.22ms) ACCEPTED, verify-session Py+Rust 2^-128.02 art:af97c8ab. Running live_session GPU tests
CHECKPOINT 0132b66 (04:02Z) [open] gates 11/11 0 failures, Py+Rust agree art:5b03fb15. Bench: --zk 4096 OOMs on 4090 (fragmentation; expandable_segments fixes); --zk bench failed main's contract (t.zk_additional) -> fix 0f6cc311 (+t.total_live). Rerunning 3 arms
CHECKPOINT 0132b66 (03:51Z) [open] item 2 done on the 4090 @e0c7acd2: ligerito-verify cargo test --release 98 passed/0 failed/1 ignored; cargo check backends/direct (+vendor p3-*) exit 0. item 5 done e0c7acd2 (no attack accepted). Running 11 gates (5 rel x nonZK/ZK + fp8-ada ZK default path); live_serve starting on vy-ligerito-2pass-verifier (EU-RO-1). Next: bench
CHECKPOINT e0c7acd2 (03:43Z) [open] 03:50Z start: read contract/brief/kb/inbox(empty)/predecessor. Committed redteam_live_labels retarget (no attack accepted locally). Next: sync pod, cargo test ligerito-verify, GPU gates 11-coin, bench

# ligerito-2pass-2 — Ligerito second pass (successor of ligerito-2pass)

Branch `lane/ligerito-2pass` (took over at 59eb8df8: merges of relation-2@498f9014, sumcheck-3@58e76e5d (11-coin default),
verify-rs-3@a87edaa0). Pods: prover `vy-ligerito-2pass` v1z7ar00oxtsw7 (RTX 4090, EU-RO-1, cgroup quota 1360000 = 13.6 CPUs,
nproc 32); verifier `vy-ligerito-2pass-verifier` 3t6j7vf13tnp57 (RTX 2000 Ada, EU-RO-1, no CPU stock in that DC), serving
`live-verifier@e0c7acd23cec` on `tcp://213.173.110.199:17864` (backends/direct/ligero/ is byte-identical to main 24f252b1).
Pod scripts: `evidence/pod-scripts/`; pod outputs `/workspace/ligerito-2pass-2/`.

## Log
* 03:50Z read contract/brief/kb/inbox (empty) / predecessor report. Predecessor's uncommitted file =
  `redteam_live_labels.py` (item 5), laptop run: honest accepted by both paths; A (label grinding), B (extra trailing
  commitment), C (random slot) refused by `verify_session`'s slots (`record_slots`) and by the cold `verify-dir`; 4 record
  negatives refused; "no attack accepted". Committed **e0c7acd2**.
* 03:49Z **item 2** on the 4090 @e0c7acd2: `cargo test --release` in backends/ligerito-verify: lib 83 passed / 1 ignored,
  tests/cli 9, tests/session 6; **98 passed, 0 failed**. `cargo check --release` of backends/direct (and vendor p3-baby-bear,
  p3-fri): exit 0, 0 warnings in backends/direct.
* 03:52Z inbox: coordinator 03:50Z chatter budget (§3a): acted (foreground polls, one-line checkpoints).
* gates: bf16-ampere first attempt failed before proving (fixtures/bench-instances/v1 not built: needs pod_bootstrap
  BENCH_INSTANCES=1); rebuilt and rerun (05_ampere.sh).
* 03:58Z **item 3: gates @e0c7acd2, 11/11, 0 failures** (LGSC0004 11-coin default, fp8-ada zc 3,3,6,6 / vf 12 / cmb 6,6,6 /
  rb 6,6): fp8-ada, bf16-hopper, fp8-hopper, bf16-ampere, fp4-nvf4 x {non-ZK: 4 positives + 98 negatives; --zk with
  LIGERITO_ZK_REBUILD_F=1: 4 + 100} + fp8-ada --zk on the default (no rebuild) path 4 + 100. Python cold dump verify agrees on
  every file (100/100, 102/102); pinned `ligerito-verify batch` (no --allow-any-key) accepts 2/2 honest and rejects every
  negative in each dir (union 2^-128.017 .. 2^-128.062). Manifests say commit "unknown" (the synced tree has no .git; the
  tree's `.research-source.json` pins e0c7acd2). **art:5b03fb15** (gates + cargo logs + pod scripts).
* 03:56Z bench (06_bench.sh) fp8-ada 4096 VUs: local non-ZK passed (0.40 s median). Both **--zk arms OOMed** on the 4090 at the
  LGSC0004 opening fold (`T` (3, D, n0) int32 = 9.00 GiB requested; 6.78 GiB allocated, 8.04 GiB reserved-but-unallocated =
  allocator fragmentation after the z_to_f drop). `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` fixes it: local ZK
  0.58-0.59 s, 1,149,078 B, 41 rounds, peak 15.7 GiB, Rust accepts (07_bench_zk.sh). relation-3's 12-coin runs fit without it.
* 04:03Z the --zk bench still exited 1: main's contract validator (merged via 24f252b1) refuses `t.zk_additional` > 0 under
  NON_ZK_PROOF_DIAGNOSTIC, so every Ligerito --zk bench on this base fails validation. Also run.py reported a live
  verifier's wall as `t.total` (no `t.total_live`). Fix **0f6cc311**: diagnostic --zk reports masking as
  `split.zk_masks_seconds` (still inside t.total); a live-verifier run reports `t.total_live` = wall, `t.total` = wall -
  stream wait, and only the wait-free buckets. Final bench (08_bench_final.sh) at 0f6cc311, expandable segments on every arm.
* 04:05Z **item 4: final bench @0f6cc311, all three arms exit 0, validation passed, `bench.summary` contract ok**. Live
  session **c20260924T040322Z-ff4e ACCEPTED** 3/3 batches x 41 rounds by `live-verifier@e0c7acd23cec` (my verifier, same DC
  EU-RO-1, RTT median 0.22 ms). Session claim over my verifier's whole store (2 `c…` sessions: ff4e + 1088, the OOMed attempt,
  REFUSED "peer closed", counted as attempts): **Python `verify-session` 1/1 authenticated, claim 2^-128.020; Rust
  `ligerito-verify batch --session` accepted, claimed_union_log2 -128.020** (per proof 2^-130.02, sized for 3 reps).
  **art:af97c8ab** (final + attempt-2 + oom-1 + first local-nonzk @e0c7acd2 + verifier store + scripts).
* 04:08Z verifier pod 3t6j7vf13tnp57 terminated (serve.log / index tail: `evidence/verifier-serve-tail.txt`).
* 04:09Z R3-7 end to end on the GPU @0f6cc311 (`live_session_gpu_test.py`, a script, not pytest-collected): **6/6 ok,
  0 failures, non-ZK and --zk** (honest authenticated; A/B rejected by verify-session; D one batch two proofs: 1/2; E open
  session blocks the claim; abort-retry counts 4 attempts: 2^-126.02). `live_session_test.py` (pytest): 5 passed.

## Measurement: fp8-ada, 4096 VUs, 1 batch (N = 2^30, l 16384), RTX 4090 EU-RO-1, @0f6cc311, 11-coin LGSC0004 (art af97c8ab)

Medians of 3 reps (local arms after one warm-up; live arm's warm-up is the local-stream proof that sizes the session).
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` on every arm (the --zk arms OOM without it). Every row
**NON_ZK_PROOF_DIAGNOSTIC** (under --zk the sumcheck is LGSC0004 masked, but the backend is not complete ZK). Rust = pinned
`ligerito-verify` built from this tip (verify-rs-3 a87edaa0 crate), no --allow-any-key.

| arm | t.total s | t.total_live s | zero-check s | proof bytes | sumcheck bytes | rounds | peak GiB | Python verify s | Rust verify s | claim |
|---|---|---|---|---|---|---|---|---|---|---|
| local non-ZK (LGSC0003) | 0.4035 | - | 0.138 | 701,728 | 11,069 | 48 | 16.00 | 0.561 | 0.283 | none (prover knows coins) |
| local ZK (LGSC0004) | 0.5947 | - | 0.175 | 1,149,078 | 418,846 | 41 | 15.69 | 0.668 | 0.312 | none |
| **live ZK, own verifier same DC** | 0.5951 | **0.6075** | 0.182 | 1,157,141 | 418,846 | 41 | 15.69 | 0.677 | 0.306 | **2^-128.02** after verify-session (Py = Rust) |

Live: stream wait 0.012 s per batch (41 rounds x 0.22 ms RTT), t.total_live / local t.total = 1.02x. ZK costs +0.19 s
(+47 %) over non-ZK, mostly arithmetic (0.185 -> 0.346 s: the masked rounds) and +447 KB of proof (LGSC0004's sumcheck
419 KB at 11 coins vs 187 KB at relation-3's 12; 11 coins = fewer, fatter rounds). vs relation-3 (12 coins, 6dda159a):
ZK 0.823 -> 0.595 s, non-ZK 0.594 -> 0.404 s on the same pod type (the sumcheck-3 merge changed both schedules and
kernels; cause not isolated, and host noise not separated: one session each). First local non-ZK @e0c7acd2 with the default allocator: 0.401 s (same).
