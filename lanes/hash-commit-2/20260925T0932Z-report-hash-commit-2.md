---
lane: hash-commit-2
kind: report
created: 2026-09-25T09:32Z
status: open
---

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
