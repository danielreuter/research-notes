---
lane: hash-commit-2
kind: report
created: 2026-09-25T09:32Z
status: open
---

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
