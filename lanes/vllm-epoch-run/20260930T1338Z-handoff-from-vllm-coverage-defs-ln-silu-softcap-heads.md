---
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
id: 20260930T1338Z-handoff-from-vllm-coverage-defs-ln-silu-softcap-heads
campaign: overnight-sep30
lane: vllm-coverage-defs
kind: handoff
status: ready-for-review
repo: danielreuter/verity
origin: vllm-coverage-defs
---

lane: vllm-coverage-defs · to: vllm-epoch-run (cc of the coordinator handoff) · re-run from the pre-merge branches above · created: 20260930T1338Z

Three PR heads, all on origin; the push works again, so no bundle is needed. Please open the PRs. GPU evidence comes from two Kueue port-capture jobs on vy-nebius-1 (RTX PRO 6000, cc 12.0, 188 SMs, driver 580.173.02). Job 181 failed on a tree permission (the job user couldn't mkdir a C++ JIT build dir in my shipped tree); job 186 is the rerun.

## 1. Pythia LayerNorm: `cursor/pythia-layer-norm-987d` @ 4a3c60f4 (base main)
- Adds `LayerNormAtenRule` and the vocab kind `layer_norm_aten` -> `LayerNormAten_v1{N,EPS}` (quarantine.ln), the difftest adapter `quarantine/ln/layer_norm_aten_difftest.py`, and `tests/program/test_layer_norm_aten.py`.
- Exact: the `properties-admission` difftest is 60/60 bit-exact on the PRO 6000 (job 179 = run r20260930-132019-cf48, produce --n 60 --seed 7; check record sha256 e2f55bce…ca1f).
- Circuit check at N=64 and N=768, as a Definition and `--as-call`: 0 failures, 0 redundant gates. The partition applies (Q_word_v1: 584 units, max_out_bits 32).
- The dead-gates warning (539 at N=64) is the same class as the accepted RMSNormTriton_v1 (516 at N=64).
- No digest moves: the new role changes only the vocabulary/ruleset JSON in the `derive` annotation, which never enters program_digest.
- The Pythia Build still refuses next on partial rotary, erf-GELU and the biases, so no sweep cell changes yet.

## 2. SiluMul_v2: `cursor/silu-mul-v2-987d` @ 174950a8 (base main)
- `quarantine/act`: `SiluMulBf16_v2` and `SiluMul_v2{I}` fix the red-team reproducer, (gate 0x3F80, up 0x8000) -> 0x0000. They also cover NaN -> 0x7FFF, gate -inf -> NaN, gates <= -89 -> signed zero, and gate -0. v2 equals v1 exhaustively on every other gate.
- A new version only. No vocabulary binds v2 and no `_v1` record is rebound, so no digest moves and no sweep cell changes.
- Exact: difftest 60/60 bit-exact on the PRO 6000 against `torch.ops._C.silu_and_mul` (job 179, check record sha256 93328999…d79f).
- Circuit check `SiluMul_v2{I=8}` and `{I=11}`, as a Definition and `--as-call`: 0 failures, 0 redundant gates, 0 dead gates.

## 3. FA2 softcap on sm_120: `cursor/fa2-softcap-sm120-987d` @ f23660d1 (stacked on #486, base `cursor/vllm-sm120-fa2-check-inf-0ec6` @ 70a4504e; retarget to main once #486 merges)
- `registry/fa2_softcap.py` adds `AttnBlockSoftcap_v2`, `AttentionHeadSoftcap_v2` and `AttentionSoftcap_v2{T,NH,KVH,D,BN,CAP,DOT,INV,MASKED_FROM}`. This is Attention_v5 with FA2's stage A': `s = MufuTanh(F32MulFtz(dot, softmax_scale/CAP))` before the mask and row max, exp2 constant `CAP*log2e`, and Check_inf per iteration (only the rescale unguarded).
- Binding:
  - `targets.attention_spec(..., cap=)`: blackwell_consumer FA2 binds v2; the accepted target keeps `AttentionSoftcap_v1`; any other target raises UnregisteredTarget.
  - The attention rule passes CAP. The `attention_dot` kind takes an optional CAP, so the vocabulary version is unchanged (tested).
  - `FLASH_ATTENTION_LAUNCHES` adds v2.
- Exact on every head, record `fa2_softcap_capture` OK, digest 7fa28706…09d9 (job 186 = run r20260930-132723-546c):
  - 8,382 rows / 53,064 heads, 0 mismatches.
  - The 112 non-finite heads (edge rows: +-inf and NaN scores) were checked by the reference evaluator; 40 sampled finite heads show 0 twin mismatches; 0 binding mismatches.
  - Cases: every softcap case of `fa_tap_exactness.cases(2)` (including window (4095,0), which runs as plain causal) at D=128 and D=256, a wide case, and the gemma-2-2b / gemma-2-9b mixed and decode shapes.
  - All launches were tile (D,64,64,4) and deterministic; MUFU ex2/rcp matched.
- MUFU.TANH: `tanh_probe.cu`, built as compute_80 PTX (JIT), checked all 2^32 inputs against MufuTanh_v1's rules and table with 0 mismatches and 0 odd-symmetry violations. The sm_89 table holds on the PRO 6000, so there is no new tanh version.
- Circuit check `AttentionSoftcap_v2{T=40,NH=2,KVH=1,D=16,BN=16,CAP=50,...,MASKED_FROM=2|0}`, as a Definition and `--as-call`: 0 failures. The 2-dead-gate warning is identical on Attention_v5 and AttentionSoftcap_v1.
- The partition rule test passes: unit_rule has no violations, max_out_bits <= 32, and the head's units are ok.
- The suite `-m "not pod"` has 15 failures. 14 are missing LFS `.npz` fixtures (topp_split_fixture, fa2_prototype), the same set as on clean main. The 15th, test_tp_moe_members, was a SIGKILL from memory pressure under -n 4 on this 15 GB VM; it passes alone.
- **Gap for the sweep, and not new:** the Match fold (`observe/fold/patterns/attention.py:120`) refuses "softcap is not modelled" on every target, the accepted one included, and the replay rows have no softcap evaluator.
  - So a Gemma-2 sm_120 row now builds its attention, but it won't Match until the fold passes `cap` to `attention_spec` and a softcap row evaluator lands. The capture's twin, `softcap_head_states`, is ready to move into `kernels/` for that.
  - I haven't started this; say if you want it next.

## Correction to my 09:31Z finding (top-p option 1)
Option 1 (root-level pieces) needs no policy change under Q_WORD_ID. The prototype is `cursor/topp-split-calls-987d` @ 117f849c (not a PR). It is exact on CPU with a max piece of 1.03M gates. Match and replay are still to do. This is evidence for Daniel's proposal only.
