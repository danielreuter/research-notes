---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-attention
created: 2026-09-30T05:47Z
---

# MERGE-READY #477: FA2 on sm_120 binds the Hopper-step Attention_v2; gate (b) 0 unexpected failures

- **Branch and head.** `cursor/vllm-sm120-attention-0ec6` @ `4975dc66`. It's stacked on #465 (`cursor/vllm-sm120-target-422d` @ `f740c1d5`), which merges first. #486 stacks on this PR.
- **What it does.**
  - `blackwell_consumer` accepts FA2 only, and binds `Attention_v2{BN=fa2_kblock_n(D), DOT=HopperBF16WgmmaDot16_v1, INV=Fa2InvSum_v1}`.
  - `query/required.py::_profile`'s fallback uses `effective_flash_attn_version`, so cc 12.0 requires the FA2 hidden stream.
  - It adds `tests/properties/fa2_target_capture_gpu.py` and the `fa2_target_capture` property schema.
- **What doesn't change.** sm_89 and sm_90 bindings, Program digests, manifests and the vocabulary version. No Definition is added or restated.
- **Hardware evidence** (RTX PRO 6000, cc 12.0, 188 SMs):
  - `fa2_target_capture` `ef4b2584` (`r20260930-033258-f611`, `art:d342a748`): 122,228 heads, `Attention_v2` exact on every finite head, `Attention_v3` differs on 997; MUFU tables, tiles and engine FA2 selection match.
  - `fa_tap_exactness` `9dee6b6f` / `9403e9fe`, 76/76 each (`r20260930-030755-9aab`, `art:592bc0ae`).
- **Gate (b)**, same pod `vy-sm120-attention-2`:
  - Commands: `gate-tools/gate_b2.sh`, base with `BOOTSTRAP=1`, head concurrently after the base bootstrap.
  - Base `f740c1d5` `r20260930-034927-48b4` (`art:00ff2fa3`): 37 failed / 4401 passed / 16 errors.
  - Head `cfcbfcef` `r20260930-035219-a82d` (`art:0006ccaf`): 38 / 4407 / 16.
  - jdiff `art:a175e2b2`: the one new failure is the P8 lint (arch literals in the evidence string), fixed at `4975dc66`. `4975dc66`'s lints and touched tests pass (`r20260930-042000-6c90`, `art:0f9bf31a`). The 7 new tests pass; the one removed test is the renamed sm_120 test; `test_twins::test_check_writes_the_evidence_schema` goes xfail -> pass (environmental, known).
- **Found, not fixed.**
  - The FA2 guard placement holds on every FA2 target; #486 models it for sm_120, and sm_89/sm_90 are unchanged by decision.
  - The attention chains' `_v1` FMA NaN is `0x7FC00000` where the GPU writes `0x7FFFFFFF` (row sums on NaN rows only).
  - `ATTN_SEMANTICS` has no FA2-on-Hopper-step entry.
