---
lane: hash-commit-2
kind: report
created: 2026-09-25T09:32Z
status: final
---

CHECKPOINT 2a92fe61 (10:22Z) [final] tip 2a92fe61 merge-ready (Poseidon2 int8 sm_90 fix); GPU committer byte-identical on A100 sm_80 + H100 sm_90 (98/98, ev c90e6d0d == 4090), committer H100 3.5ms A100 5.7ms 4090 4.9-5.2ms; 4090 A/B closed; all pods terminated; ~$3.5
CHECKPOINT 2a92fe61 (10:11Z) [open] H100 NVL sm_90 DONE: 98/98 byte-identity, fix 2a92fe61 (Poseidon2 torch int8 _int_mm M%32) -> 348 pass; bf16 GPU committer 3.5ms ev c90e6d0d == 4090 (art:c2212273); cc art:d789044f; Flock 7.51 T CLMAD/s art:31a799a7; pods 4090+H100 terminated; A100 host arm last
CHECKPOINT bcf75db7 (10:06Z) [open] PORTABILITY: byte-identity 98/98 on A100 sm_80 + H100 sm_90; bench bf16-hopper+blake3 GPU arm ev c90e6d0d stmts c9ed5a64 == 4090, Rust 49; committer H100 3.5ms (host 15.8s), A100 5.7ms. H100 neighbour fail = Poseidon2 torch int8 _int_mm (sm_90 needs M%32); fix testing r20260925-100554-2e7b
CHECKPOINT bcf75db7 (09:54Z) [open] 4090 bcf75db7 A/B closed + 15 results preserved (fp8 GPU art:91a9287e, bf16 GPU art:728e07b2, cc art:6cb3eb00); H100 NVL r20260925-094905-04b2 + A100 r20260925-095225-92f7 bootstrap->byte-identity->timing running. Laptop-disk handoff 0946Z: compliant, nothing pulled
CHECKPOINT bcf75db7 (09:45Z) [open] 4090 rerun @bcf75db7 done rc0: fp8 GPU 3.9-4.0ms/host 11.9-12.3s ev f62b873f; bf16 GPU 4.9-5.2ms/host 24.3-25.0s ev c90e6d0d; Rust ok; registering (art:91a9287e art:728e07b2 ...); A100+H100 pods up, syncing
CHECKPOINT bcf75db7 (09:32Z) [open] 09:33Z took over; in-flight run r20260925-084051-7b4e @bcf75db7 on vy-commit-gpu: fp8 x3 GPU 3.9-4.0ms vs host 11.9-12.3s ev f62b873f; bf16 r1 GPU 5.2ms vs 24.3s ev c90e6d0d rust 49; bf16 r2+commit_cost+flock left; next A100/H100 pods
# hash-commit-2: successor of hash-commit (agent died 09:25Z, infra); collect the 4090 rerun, then sm_80 / sm_90 portability

Launch: coordinator 2026-09-25 ~09:30Z. Base lane/hash-commit @ bcf75db7 (already merged into main 94b1c4d2), worktree
~/projects/verity-main-wt/hash-commit, pod vy-commit-gpu (g6sehoo9nur00q). FINAL 13:30Z, budget $40 (~$3 spent before).
Inbox at startup: nothing new. Handoffs received: none. Pod scripts: evidence/pod-scripts/ (predecessor's, paths -> /workspace/hash-commit-2).

## 1. The in-flight 4090 job (r20260925-084051-7b4e, tree bcf75db7, rc 0, ended 09:35Z)
Chain: byte-identity tests (98 pass) + neighbours (326 pass, 1 skip), fp8-ada+blake3 A/B x3, bf16-hopper+blake3 A/B x2
(batch 8192, pipeline 2, reps 5, CREPS 3), commit_cost --impl gpu at 4096, Flock clmad sm_89. Every run rc 0, Rust batch accept.
| relation | arm | committer ms (r1/r2/r3) | commit.seconds | ev (commit-evidence sha) | stmts |
|---|---|---|---|---|---|
| fp8-ada+blake3 | host | 11913 / 12295 / 12132 | 12.5-12.9 s | f62b873f | 25:b09ff90f, Rust 25 |
| fp8-ada+blake3 | GPU | 3.9 / 4.0 / 4.0 | 10.3-11.6 ms | f62b873f | 25:b09ff90f, Rust 25 |
| bf16-hopper+blake3 | host | 24334 / 24992 | 25.6-29.6 s | c90e6d0d | 49:c9ed5a64, Rust 49 |
| bf16-hopper+blake3 | GPU | 5.2 / 4.9 | 12.0-13.3 ms | c90e6d0d | 49:c9ed5a64, Rust 49 |
commit_cost --impl gpu, 4096 leaves (median of 20, roots == references, openings verify): rows 1536 B frame-v3-sha256-row
commit 0.57 ms (leaf 0.17, tree 0.40; h2d 0.84 separate), blake3-row ~0.58; rows 3072 B sha256-row 0.55 (h2d 1.48);
words 6,291,456 x 2 B frame-v3 12.5 ms, vllm-v1 8.4 ms. Flock sm_89: raw CLMAD peak 0.67 TCLMAD/s.
This closes the 4090 A/B at bcf75db7. Registration: run r20260925-094434-b134 (40-register.sh / 41-register-dirs.sh), ids below.
Registered + preserved 09:44-09:46Z from the pod (run r20260925-094434-b134; bench-result / run-files; slim = no rep-1 .proof bytes, sha256 listed):
- fp8 GPU r1 art:91a9287e (full tree art:71a093c2); r2 art:83fb9ac8 (slim art:93951591); r3 art:07d36f27 (slim art:b740aade)
- fp8 host r1 art:40d3f3ca (slim art:3043520f); r2 art:2d0aa70c (slim art:55a132eb); r3 art:d263fbbb (slim art:defb7cec)
- bf16 GPU r1 art:728e07b2 (full tree art:a7800ce3); r2 art:e2cbb3aa (slim art:56ab934b)
- bf16 host r1 art:25a4c1aa (slim art:0ea28cc8); r2 art:56602c45 (slim art:e1b49908)
- commit_cost 4090: rows1536 art:6cb3eb00, rows3072 art:189b63d4, words2 art:27f58920; Flock sm_89 art:855d5a32; runs.txt + test logs art:ffc51c25
Correction to the commit_cost line above: rows 1536 B blake3-row commit 0.58 ms, vllm-v1 0.50 ms (leaf 0.22, tree 0.28); roots == reference roots.

## 2. Portability: A100 (sm_80) and H100 (sm_90)
Pods (mine, SECURE, guard 60, registered): vy-hash-commit-2-h100 053peggdba5ubj H100 NVL 94 GB (sm_90, $3.19/h, created 09:37Z;
host EPYC 9374F; the "variant (+17 %)" memory vs the reference H100 80GB HBM3), vy-hash-commit-2-a100 fertega4i5qs2a A100 80GB PCIe
(sm_80, $1.59/h, created 09:37Z). The A100's `pods create --register` died laptop-side after the pod came up; registered by hand
(`pods register --any-name`). Synced bcf75db7 (tar, 224 s / 328 s). Chain 90-port.sh via research run --custody-r2:
H100 r20260925-094905-04b2, A100 r20260925-095225-92f7 (bootstrap RELS=bf16-hopper, then arch facts, byte-identity suites,
neighbours, profile, commit_cost at 4096, bench-vu bf16-hopper+blake3 GPU arm then host arm; ev expected c90e6d0d as on the 4090).
Laptop note: background processes started from my agent shell are reaped when the call returns (two syncs and one launch
silently never ran); launch through `research run` in the foreground, and long laptop commands through the agent's own background mode.

### Results (tree bcf75db7 = main's committer; NVRTC 12.4 JIT, no arch flags; fv3_top block 896 threads on both)
Byte-identity suites (hash_gpu/tests/test_frame_v3.py, frame_gpu_test.py, tests/test_commit_cost_benchmark.py: GPU frame-v3
word / SHA-256-row / keyed-BLAKE3-row and vllm-v1 trees == core vectors, host builders, commit_cost references):
A100 sm_80 98/98 (09:54Z), H100 sm_90 98/98 (09:50Z). Neighbours (hash_gpu, hashchain, leaf_test, leaf/core_schema, verity
commitments): A100 326 passed 1 skipped; H100 1 FAILED under -x: test_hash_gpu.py::test_poseidon2_tree_matches_reference
[torch] -- Poseidon2 torch int8 MDS, `torch._int_mm` CUBLAS_STATUS_NOT_SUPPORTED at 17 rows. Not the frame-v3 / vllm-v1
committer (Poseidon2 is off Table 2), pre-existing code (f1c41260). Probe (92-int-mm-probe.py, torch 2.6.0+cu124, H100):
sm_90 cuBLASLt INT8 GEMM accepts only M % 32 == 0 (17..40, 48, 63, 65, 100, 200, 1000, 4099 fail; 32, 64, 128, 1024 ok).
FIX 2a92fe61: the int8 route pads the states to a multiple of 32 rows on cc >= 9 (no-op elsewhere). H100 after the fix
(r20260925-100554-2e7b): byte-identity + neighbours 348 passed, 1 skipped, no -x.

bench-vu bf16-hopper+blake3 (batch 8192, pipeline 2, reps 5, CREPS 3, 4096 VUs, zk interactive 2^-128, --auth included-hash;
no MALLOC_* env, before the 10:03Z handoff), one round:
| GPU | arm | committer ms | rows / trees / chain ms | commit.seconds | ev | stmts | Rust | t.total s |
|---|---|---|---|---|---|---|---|---|
| RTX 4090 sm_89 (r1/r2) | GPU | 5.2 / 4.9 | 2.3 / 2.8 / 3.9 | 0.013 | c90e6d0d | 49:c9ed5a64 | 49 accept | 6.2 |
| RTX 4090 sm_89 | host | 24334 / 24992 | | 25.6-29.6 | c90e6d0d | 49:c9ed5a64 | 49 accept | 6.2 |
| H100 NVL sm_90 | GPU | 3.5 | 0.8 / 2.7 / 2.8 | 0.0128 | c90e6d0d | 49:c9ed5a64 | 49 accept | 4.50 |
| H100 NVL sm_90 | host | 15804 | | 16.9 | c90e6d0d | 49:c9ed5a64 | 49 accept | 4.52 |
| A100 80GB PCIe sm_80 | GPU | 5.7 | 1.6 / 4.1 / 3.8 | 0.0158 | c90e6d0d | 49:c9ed5a64 | 49 accept | 6.60 |
Same commitment evidence and statement files on all three parts, host or GPU committer: byte-identical across sm_80/89/90.

commit_cost --impl gpu at 4096 (median of 20; every root == reference root, openings verify), ms, commit = leaf + tree (h2d apart):
| shape | scheme | 4090 | H100 NVL | A100 80GB |
|---|---|---|---|---|
| 4096 x 1536 B rows | frame-v3-sha256-row | 0.57 | 0.53 | 0.84 |
| 4096 x 1536 B rows | frame-v3-blake3-row | 0.58 | 0.53 | 0.85 |
| 4096 x 1536 B rows | vllm-v1 | 0.50 | 0.65 | 0.87 |
| 4096 x 3072 B rows | frame-v3-sha256-row | 0.55 | 0.59 | 0.86 |
| 4096 x 3072 B rows | frame-v3-blake3-row | (art:189b63d4) | 0.53 | 0.84 |
| 4096 x 3072 B rows | vllm-v1 | (art:189b63d4) | 0.94 | 1.26 |
| 6,291,456 x 2 B words | frame-v3 | 12.5 | 9.3 | 14.6 |
| 6,291,456 x 2 B words | vllm-v1 | 8.4 | 6.0 | 9.2 |
Profile (75-cg-prof.py, fp8 shape): H100 row_tree 0.65 ms, y word tree 0.52, pinned 6 MiB h2d 0.12; A100 row_tree 1.96 (min 1.17),
word tree 0.83, pinned h2d 0.26. The committer is launch/tree-level bound (tree ~0.4-0.6 ms regardless of leaf hash), not hash bound.

### Registered + preserved (pod-side, runs r20260925-100906-f2da H100 and r20260925-101747-4071 A100)
- H100 NVL: bf16 GPU arm art:c2212273 (full tree art:4d515578), host arm art:2091ad4d (slim art:79490945); commit_cost rows1536
  art:d789044f, rows3072 art:4a7208bc, words2 art:51c2e751; logs (runs.txt, arch, prof, tests incl. the post-fix run, bootstrap)
  art:3791e8c4; Flock sm_90 art:31a799a7.
- A100 80GB: bf16 GPU arm art:2474855e (full tree art:50f90ea2), host arm art:c51f7642 (slim art:f2b91649); commit_cost rows1536
  art:81c31b1c, rows3072 art:8a9387cf, words2 art:8a2cdb40; logs (incl. tests-all-2a92fe61: 348 passed, 1 skipped) art:45dcccbe.

## 3. Flock (survey §4.1 ask from hash-commit/0752Z; flock-bench cross-check ask hash-commit/0950Z)
Flock b684b125, CUDA 13.3.1 redist (nvcc V13.3.73) AOT, 40 CLMAD SASS lines in clmad_peak on both parts.
RTX 4090 sm_89 (driver 580.159): clmad_peak 0.67 T CLMAD/s; GF(2^128) mul schoolbook+clmad 75 G/s, binius+clmad ~50, software 17 (art:855d5a32).
H100 NVL sm_90 (driver 580.126, no cuda-compat needed): 7.51 T CLMAD/s; binius+clmad 575-607 G/s, schoolbook 363-371, karatsuba 325,
software 7-10 (art:31a799a7). Answers flock-bench's question: the ~8x H100-over-5090 clmad rate reproduces on a second H100
(NVL, 7.5 vs SXM 8.3 T/s). test_f128 exits 1 on both only for want of its vectors.bin input (a cargo dump bin never run).
kb: flock-prover.md (two measured lines), gpu-committer.md (portability section + the sm_90 _int_mm gotcha).

## Handoffs
Received:
- 20260925T0946Z-handoff-from-coordinator.md "Laptop disk at 2.6 GiB": complied (nothing fetched to the laptop, all registration pod-side).
- 20260925T1003Z-handoff-from-coordinator.md "Export MALLOC_MMAP_MAX_=0 ...": no measured run started after it; the runs above
  predate it and the peer handoffs say so.
- hash-commit/20260925T0950Z-handoff-from-flock-bench.md "5090 reference for your clmad runs": answered by the H100 Flock run (section 3).
- Predecessor's, already acted on by hash-commit (its report): hash-commit/20260925T0546Z-handoff-from-coordinator.md (Poseidon2
  PAUSE), hash-commit/20260925T0650Z-handoff-from-coordinator.md (both schemes first-class), and
  hash-commit/20260925T0752Z-handoff-from-coordinator.md (survey). Its remaining ask, Flock on an H100, is done here (section 3).
Sent: coordinator/20260925T1024Z-handoff-from-hash-commit-2.md (merge-ready 2a92fe61),
b-ligero-sha256/20260925T1022Z-handoff-from-hash-commit-2.md, blake3-80gb/20260925T1022Z-handoff-from-hash-commit-2.md.

## Pods and cost
vy-commit-gpu g6sehoo9nur00q (4090, 06:50Z-10:09Z, $0.74/h: ~$2.46 total, ~$0.48 of it mine), vy-hash-commit-2-h100
053peggdba5ubj (09:37Z-10:11Z, $3.19/h: ~$1.81), vy-hash-commit-2-a100 fertega4i5qs2a (09:37Z-10:21Z, $1.59/h: ~$1.17).
Lane total including hash-commit ~$6.5 of $40.

## FINAL
~~~text
tip: lane/hash-commit @ 2a92fe61 (base lane/hash-commit@bcf75db7)        merge-with: lane/hash-commit@2a92fe61 (1 commit on main 3301c435, merges clean)
known-failures: none    pod: vy-commit-gpu terminated 10:09Z, vy-hash-commit-2-h100 10:11Z, vy-hash-commit-2-a100 10:21Z; ~$3.5 this lane (~$6.5 with hash-commit)
artifacts: art:91a9287e art:728e07b2 art:c2212273 art:2091ad4d art:2474855e art:c51f7642 art:6cb3eb00 art:d789044f art:81c31b1c art:855d5a32 art:31a799a7
~~~
The GPU committer (frame-v3 word / SHA-256-row / keyed-BLAKE3-row, vllm-v1) is byte-identical and fast on sm_80, sm_89 and sm_90
without code changes: 3.5 ms (H100 NVL) / 4.9-5.2 ms (4090) / 5.7 ms (A100) per 4,096 bf16 instances, evidence c90e6d0d and statements
identical across all three and against the host committer. The only portability defect was in the Poseidon2 torch int8 MDS
(off Table 2), fixed in 2a92fe61. The 4090 A/B at bcf75db7 is closed (fp8 3.9-4.0 ms vs 11.9-12.3 s host).
