---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-moetap (agent bc-2c25902d)
created: 2026-09-27T01:36Z
---
# Merge-ready: PR #96 router-softmax tap + TP vocabulary range (`cursor/vllm-rf-moetap-82dc` @ `c574c4a5`), GPU records ok

**Branch** `cursor/vllm-rf-moetap-82dc`, head `c574c4a5` (pushed), [PR #96](https://github.com/danielreuter/verity/pull/96) (draft).
**Base** `5b0835d4` = PR #92 `b21ce332` (contains PR #86 `fc5c5c3d`) merged with PR #90 `14ea93c6`. Merge after #86, #90, #92.
Opt-in: `ROUTER_TAP`, `VOCAB_TAP` (`CommitConfig`, default 0). Off: no command line, manifest, Program, root or verdict changes.
Pod `vyv-rf-moetap-g2` (2x L40S, reference part): runs below, all `--custody-r2`. Your 0015Z conditions, in order:

## 1. `router_tap_exactness.json` -- run `r20260927-011454-7498` (head `c574c4a5`), full (not --quick), **ok: true**, `--verify` intact (digest `e8fa0bcf5523…a68`)
L40S sm_89, torch 2.13.0+cu129, vLLM 0.28.1rc1.dev472+gd9105ea80, `VLLM_BATCH_INVARIANT=1`, engine env pins applied; tap build sha256 `ce2739c7…5b49`
(pinned `topk_softmax_kernels.cu` / `cuda_compat.h` / `cub_helpers.h` sha256-checked at build).

| config | rows | tap_ne_ir | out_ne_ir | out_eq_installed (incl. int64 ids, is_padding) | out_eq_untapped | unwritten |
|---|---|---|---|---|---|---|
| E=64 TOPK=8 plain | 1024 | 0 | 0 | true | true | 0 |
| E=64 TOPK=8 renormalize | 1024 | 0 | 0 | true | true | 0 |
| E=128 TOPK=8 plain | 1024 | 0 | 0 | true | true | 0 |
| E=128 TOPK=8 renormalize | 1024 | 0 | 0 | true | true | 0 |

Rows = 24 edge rows (ties, NaN, +-inf, +-0, subnormal, overflow/underflow) + 1000 seeded random; every row against the IR's own evaluation
(the gate `query.router_softmax.slots` names, `evaluate_call` transcript). Source check on vLLM's `fused_topk`: outputs unchanged, 0 acquired
outside a step, `moe/L<k>/router_softmax` per launch equal to the op's words, other geometry refused, op restored: ok.

Edge words (tapped = IR after the fix; "#86" = PR #86's `MoeRouterProbs` statement, CPU: `notes-asset:lanes/vllm-rf-moetap/evidence/pod-scripts/router86_compare.py`):

| config | row | max (tapped) | max (#86) | a NaN exponential (tapped / #86) | words #86 differs |
|---|---|---|---|---|---|
| E64_k8_plain | all NaN | `0x7fffffff` | `0x7fc00000` | ex[0] `0x7fffffff` / `0x7fffffff` | 1 |
| E64_k8_plain | NaN first | `0x40120000` | `0x40120000` | ex[0] `0x7fffffff` / `0x7fffffff` | 0 |
| E64_k8_plain | NaN heads thread 1 | `0x40370000` | `0x40370000` | ex[8] `0x7fffffff` / `0x7fffffff` | 0 |
| E64_k8_plain | negative NaN | `0x40070000` | `0xffc10000` | ex[63] `0x7fffffff` / `0x7fffffff` | 64 |
| E64_k8_plain | subnormal logits | `0x007d0000` | `0x00000000` | none (no NaN) | 1 |
| E128_k8_norm | all NaN | `0x7fffffff` | `0x7fc00000` | ex[0] `0x7fffffff` / `0x7fffffff` | 1 |
| E128_k8_norm | NaN first | `0x401d0000` | `0x401d0000` | ex[0] `0x7fffffff` / `0x7fffffff` | 0 |
| E128_k8_norm | NaN heads thread 1 | `0x401d0000` | `0x401d0000` | ex[8] `0x7fffffff` / `0x7fffffff` | 0 |
| E128_k8_norm | negative NaN | `0x402b0000` | `0xffc10000` | ex[127] `0x7fffffff` / `0x7fffffff` | 128 |
| E128_k8_norm | subnormal logits | `0x007c0000` | `0x00000000` | none (no NaN) | 1 |

(E=64 renormalize and E=128 plain: the same pattern; all four in `notes-asset:lanes/vllm-rf-moetap/evidence/records/router86_compare.json`.)

Where #86 differs: 5 of 24 edge rows per configuration (20 of 96): "all NaN" (max 0x7FC00000 vs the kernel's 0x7FFFFFFF), a NaN in a thread's last
column ("negative NaN": #86's `x > y ? x : y` returns the NaN, so its max and every exponential are NaN; `fmaxf` skips it -- 64 / 128 words
differ), and the three subnormal rows (#86 flushes the max to +-0; `fmaxf` keeps the subnormal). A NaN at the head of a thread's columns ("NaN
first", "NaN heads thread 1") does not differ: #86's operand order already skipped it. **Honest note:** the 0x7FFFFFFF mapping of NaN
exponentials / reciprocal changed no word on these rows -- the MUFU step already emits 0x7FFFFFFF and the registry's float ops carry that
payload -- so `fmaxf` is the substantive fix; the mapping states the GPU's NaN word explicitly (+2E+3 gates per router row, 9226 -> 9357 at E=64).
Drop it in a follow-up if you want the minimum; the GPU record would need rerunning.

## 2. Live check (same run): both served shapes, vLLM engines serving tiny random-weight models (B0's tokenizer; vLLM's own MoE layers; no full checkpoint)
- OLMoE shape (E=64 top-8, `OlmoeForCausalLM`): 2 MoE layers x 8 forwards, 16/16 launches tapped, **90 rows, rows_ne_ir 0**, tokens equal bare: true.
- Qwen3-MoE shape (E=128 top-8 renormalized, `Qwen3MoeForCausalLM`): 16/16 launches, **90 rows, rows_ne_ir 0**, tokens equal bare: true.
- Found on the way: vLLM passes `is_padding` to `topk_softmax` in a live engine (VLLM_MOE_SKIP_PADDING); the source passes it through (softmax
  unchanged; a padded launch's extra rows fail the identity check); the padding path is also checked op-level in every configuration.

## 3. TP2 vocabulary-range record -- run `r20260927-011644-9037`, **ok: true**, `--verify` intact (digest `5acdc9f2ef23…e98`)
2x L40S, `NCCL_P2P_DISABLE=1` (as tp-commit requires; without it NCCL hung). Tiny random-weight Llama (4 heads; B0's 9 heads do not shard),
vocabulary 49152 = 2 x 24576 unpadded. Per rank (starts 0 / 24576): 96 edge rows through vLLM's own `VocabParallelEmbedding.forward` with int32
and int64 ids -- ne_ir 0, kernel partial disagrees 0, outputs bit-identical to no source; live 53 rows per rank, ne_ir 0, kernel disagrees 0,
one acquisition per step (8/8), restored; tokens equal bare. The values are computed from the launch's ids (no kernel change).

## 4. Partition report -- run `r20260927-005720-ee97` (Definitions unchanged since `5a6b7a5d`), `Q_word_v1{X=16,W=32,R=no-recompute}`, PARTITION-OK

| Definition (rows) | gates | units | cut (strict, committed boundaries) | recomputed | committed interior words | tap words | max out bits |
|---|---|---|---|---|---|---|---|
| MoeRouterTopKOrdered_v1{E=64,TOPK=8} (#67 #68 #70) | 9357 | 146 (130 committed + 16 out) | ok | 0 | 130 | 130 | 32 |
| MoeRouterTopKOrderedNorm_v1{E=128,TOPK=8} (#75) | 18803 | 283 (267 + 16) | ok | 0 | 267 | 267 | 32 |
| EmbeddingShard_v1{VS=25152,H=2048,START=0/25152} (#70 ranks) | 6151 | 2051 (3 + 2048) | ok | 0 | 3 | 3 | 32 |
| EmbeddingShard_v1{VS=75968,H=2048,START=0/75968} (#75 ranks) | 6151 | 2051 (3 + 2048) | ok | 0 | 3 | 3 | 32 |

The router's committed words are, in gate order, exactly the tap's per-row layout (max, E ex, 1/sum, E p [+ 8 selected, scale]); the shard's are
`tok - START` (32 b) and the two range bits (the brief's "three 1-bit values" is one word + two bits). `ROUTER_TAP=1` / `VOCAB_TAP=1` make
`Q_word` count them as acquired (`check_calls(acquired=...)`, tests `test_word_check_sees_the_tapped_*`).

## 5. Gate (b), git clones on g2 (`gate_b2.sh`), base and head on the same pod
- base `5b0835d4` (`r20260927-005731-9c35`): lints rc 0; 38 failed / 3972 passed / 263 skipped.
- head `3146bc31` (`r20260927-011128-606f`): lints rc 0; 37 failed / 4037 passed / 264 skipped. **jdiff rc 0**: 65 new tests pass, 0 new
  failures, 0 new skips; fixed on head 1 (`test_transient_storage_is_released`, memory-dependent); the 1 skip is the listed order-dependent test.
  `notes-asset:lanes/vllm-rf-moetap/evidence/gate-b/jdiff-5b0835d4-vs-3146bc31.txt`.
- `c574c4a5` differs from `3146bc31` only in `tests/properties/router_tap_exactness_gpu.py` (records the live `ok` fields); targeted recheck in a
  git clone of `c574c4a5` (`r20260927-013459-f5f0`: lints + properties/acquire/router/vocab/norm/ordered-router/dead-modules tests): lints rc 0; tests rc 0 (about 320 passed, 9 skipped, 0 failed).
  Its tree check excludes `build` dirs: the router run compiled the IR evaluator's `program/kernels/cpp/build` into the shared source dir.

## 6. Wording
- `tests/program/test_moe_router_ordered.py` docstring (`267e5a72`): outputs equal bit for bit; the interior words are topkGating's through `MoeRouterProbs`.
- Told vllm-vu-export: `lanes/vllm-vu-export/20260927T0102Z-handoff-from-vllm-rf-moetap.md` (fine-query-plan §4b/§5 wording, suggested text).

## Behaviour changes / not changed
- Changed (opt-in only): `MoeRouterProbs` statement (fmaxf + NaN word); new families `router_softmax`, `vocab_range`; `request_manifest(taps=)`,
  `check_calls(acquired=)` accepts a function of the statics; `oracle_compare` skips the two members; `taps.py` attaches both sources in
  commit_delta and on every TP rank (the TP driver passes `taps.for_ranks(...)` through the RPC; `engine.rank_worker` gains no import).
- P10: line-neutral in capped files; four caps lowered (rank_worker x2, tp/commit main, request_manifest). No allowlist grew.
- Not changed: `MoeRouterTopK_v1` / `...Norm_v1` (record), query of record, re-baseline epoch, `GumbelTopPTokenSelect`.

## Found, not fixed
- Pod network: wheels.vllm.ai and download.pytorch.org at 0.06-0.35 MB/s per connection on these hosts (PyPI ~6 MB/s); I fetched the vLLM
  and torch cu129 wheels in 16/32 byte ranges and the nvidia pins from PyPI. The bootstrap could do ranged downloads.
- `research run` shares `/workspace/research/src/<sha>` across runs of one commit; a setup or IR-evaluating run on the same commit as gate (b)
  pollutes the tree check (`out/gen/...`, `program/kernels/cpp/build`). Run gate (b) on a commit no other run uses, first.
- Full-model live checks (OLMoE, Qwen3-30B TP2 rows #67/#68/#70/#75) not run (out of budget by design).

Pods: vyv-rf-moetap-g1 terminated 23:25Z (~$0.8); vyv-rf-moetap-g2 terminated 01:49Z (drained: 24 of 25 attempts preserved; forced over `r20260926-233458-2820`, a partition run killed at 23:37Z while still waiting, empty stdout). Spend ~$6.0 (g1 ~$0.8 + g2 2h24m x $2.18 ~$5.2) of $8. Custody: every run named above is preserved on R2 (`research pods drain`, mode head).
