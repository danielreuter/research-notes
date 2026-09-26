---
lane: vllm-rf-moetap
kind: report
created: 2026-09-26T22:29Z
status: open
---

CHECKPOINT 5b0835d4 (23:04Z) [open] router tap op+build, policies router_softmax/vocab_range, both sources, plumbing (manifest/verify/commit/tp/rank_worker/plan) written, uncommitted. FOUND: #86's MoeRouterProbs max is F32Max (fast-math >-select), kernel is fmaxf; NaN words 0x7FC00000 vs GPU 0x7FFFFFFF -> fixed in the ordered construction only (record untouched). Next: exactness drivers, tests, push
CHECKPOINT 5b0835d4 (22:44Z) [open] handoff 2231Z (approval) read. g1 sy95m1sk4mmtm9 L40S up 22:41Z; runs r20260926-224241-1030 (bootstrap) + r20260926-224413-f336 (gate b base 5b0835d4) running; writing router tap kernel/op now
CHECKPOINT 5b0835d4 (22:39Z) [open] branch cursor/vllm-rf-moetap-82dc = PR#92(b21ce332, has #86)+PR#90(14ea93c6). Checker on base: ordered router commits max,ex[E],rcp,p[E](+sel[8],scale) = 130/267, 0 recomputes; EmbeddingShard commits tok-START (32b)+2 range bits. Next: router tap kernel/op
CHECKPOINT 748c3cd6 (22:29Z) [open] started: agent bc-2c25902d; reading brief, PR #86 stacking, norm-tap pattern (PR #90); no pods
