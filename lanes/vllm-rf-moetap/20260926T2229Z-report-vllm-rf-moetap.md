---
lane: vllm-rf-moetap
kind: report
created: 2026-09-26T22:29Z
status: open
---

CHECKPOINT af073204 (00:26Z) [open] 00:31Z g2 setup stuck in uv (torch/nvidia wheels from download.pytorch.org at ~0.35 MB/s, retries); killed all 5 runs again. Fetching torch 2.13.0+cu129 in 32 ranges (~2 MB/s), nvidia pins next from PyPI, pre-install, then relaunch setup/router/vocab/partition/gate(b). Spend ~$3.1
CHECKPOINT af073204 (23:47Z) [open] WAIT vyv-rf-moetap-g2 r20260926-234338-9343 check-back 00:22Z agent bc-2c25902d-4c5d-57c4-a778-e30cf29382dc: router tap build+exactness; WAIT vyv-rf-moetap-g2 r20260926-234519-b0c0 check-back 00:30Z: TP2 vocab exactness; also r20260926-234359-2b8d partition, r20260926-234437-b4d4 gate(b) base. PR #96 draft
CHECKPOINT af073204 (23:45Z) [open] g2: first setup killed 23:37Z (vLLM wheel host ~160 KB/s/conn; fetched in 16 ranges, sha ok). Relaunched on af073204: setup r20260926-234303-0db7 -> router r20260926-234338-9343 -> vocab (TP2, tiny Llama) ; partition r20260926-234359-2b8d; gate(b) base r20260926-234437-b4d4
CHECKPOINT cd1cd8ae (23:30Z) [open] pushed cursor/vllm-rf-moetap-82dc @ cd1cd8ae (4 commits; CPU tests+lints pass locally via plain-python harness). g1 terminated 23:25Z (vLLM wheel at 60 KB/s; ~$0.8). g2 xquw828jd4gds3 2xL40S up 23:25Z: setup r20260926-232812-41b5, gate(b) base queued. Live router check -> tiny random-weight OLMoE/Qwen3-MoE archs (no 14 GB download)
CHECKPOINT 5b0835d4 (23:04Z) [open] router tap op+build, policies router_softmax/vocab_range, both sources, plumbing (manifest/verify/commit/tp/rank_worker/plan) written, uncommitted. FOUND: #86's MoeRouterProbs max is F32Max (fast-math >-select), kernel is fmaxf; NaN words 0x7FC00000 vs GPU 0x7FFFFFFF -> fixed in the ordered construction only (record untouched). Next: exactness drivers, tests, push
CHECKPOINT 5b0835d4 (22:44Z) [open] handoff 2231Z (approval) read. g1 sy95m1sk4mmtm9 L40S up 22:41Z; runs r20260926-224241-1030 (bootstrap) + r20260926-224413-f336 (gate b base 5b0835d4) running; writing router tap kernel/op now
CHECKPOINT 5b0835d4 (22:39Z) [open] branch cursor/vllm-rf-moetap-82dc = PR#92(b21ce332, has #86)+PR#90(14ea93c6). Checker on base: ordered router commits max,ex[E],rcp,p[E](+sel[8],scale) = 130/267, 0 recomputes; EmbeddingShard commits tok-START (32b)+2 range bits. Next: router tap kernel/op
CHECKPOINT 748c3cd6 (22:29Z) [open] started: agent bc-2c25902d; reading brief, PR #86 stacking, norm-tap pattern (PR #90); no pods
