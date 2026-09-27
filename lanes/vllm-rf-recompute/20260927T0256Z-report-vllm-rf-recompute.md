---
lane: vllm-rf-recompute
kind: report
created: 2026-09-27T02:56Z
status: open
---

CHECKPOINT 7aeffc5d (03:51Z) [open] approved 03:49Z (CPU pod cap $2.50; L40S deferred). pod vyv-rf-recompute-cpu = RunPod qlirspls2cbwyr (cpu3g 16 vCPU/64 GB, 80 GB, EU-RO-1, ~$0.64/h) created 03:50Z, guard 90; next: gate (b) base 3040ac1f (bootstrap) -> FP8 df13126f -> Gemma 7aeffc5d
CHECKPOINT 7aeffc5d (03:48Z) [open] WAIT approval of pod estimate (internal/lanes/vllm-coordinator/20260927T0335Z-handoff-from-vllm-rf-recompute.md), check-back 04:15Z agent bc-06147ba0-d1ae-5ddc-84d6-00cb2d93cbba; PRs #106 (FP8, df13126f) and #109 (Gemma, 7aeffc5d) drafts; token OK again; next: CPU pod gate (b) base/FP8/Gemma
CHECKPOINT 7aeffc5d (03:47Z) [open] Gemma pushed 7aeffc5d (token back 03:44Z). #57 all 8 request Programs cross_call: recorded 44,520 dup AddScalarBf16 Calls / 102,574,080 gates -> once-rewrite 0 (evidence/cross_r57_recorded_vs_once.jsonl); #74 word A/B evidence/word_row74.jsonl; awaiting pod approval
CHECKPOINT 7aeffc5d (03:33Z) [open] estimate sent (ls ok): internal/lanes/vllm-coordinator/20260927T0335Z-handoff-from-vllm-rf-recompute.md (CPU pod gate (b) 3 sides ~2.5h cap $2.50; optional L40S #57 Build A/B cap $1.50); GitHub token refresh asked; no pod until approved
CHECKPOINT 7aeffc5d (03:31Z) [open] Gemma #57 committed 7aeffc5d on cursor/vllm-rf-recompute-gemma-cbba; push FAILED (GitHub App token on the VM invalid: fetch+gh 401), bundle lanes/vllm-rf-recompute/evidence/gemma-7aeffc5d.bundle; asking once for a token refresh. #57 LP31_T52 cross_call: recorded 5,460 Calls / 12,579,840 gates -> once-rewrite 0; all 8 running
CHECKPOINT df13126f (03:24Z) [open] FP8 PR #106 (draft) cursor/vllm-rf-recompute-fp8-cbba @ df13126f; def-digest A/B main vs branch: 229 Definitions of #74/#57 Programs identical. Now Gemma #57: TargetProfile selector + norm-chain rule emits the weight-only + 1 once per norm; fold = re-baseline switch point
CHECKPOINT df13126f (03:17Z) [open] FP8 #74: cursor/vllm-rf-recompute-fp8-cbba @ df13126f pushed (ScaledMmFp8BlockSharedScale_v1 + SHARED_SCALE, tests). VM checks: same circuit, bit-equal 96 edge vectors, row #74 Q_word A/B recorded 4 viol / 113.6 G recomputed -> selector on 0 / 0, +894.8 M committed words; cross_call 0 both. next: digest A/B, Gemma #57
CHECKPOINT 3040ac1f (03:04Z) [open] plan: FP8 #74 = new ScaledMmFp8BlockSharedScale_v1 (products once per (weight block,kb) in a tile node, committed; same signature), Gemma #57 = Build emits AddScalarBf16 once per norm weight (selector), both default-off; checker reproduces #74 on VM (508 gates at K=N=256); branches cursor/vllm-rf-recompute-{fp8,gemma}-cbba off main 3040ac1f
CHECKPOINT fa662029 (02:56Z) [open] started 02:57Z agent bc-06147ba0-d1ae-5ddc-84d6-00cb2d93cbba; reading cross-call-check handoff + #98 tree; CPU only, no pods
