---
lane: vllm-sm120-attention
kind: report
created: 2026-09-30T02:53Z
status: open
---

CHECKPOINT 12cea8ee (05:12Z) [open] v5 correspondence OK: fa2_target_capture 2f7cc71f (r20260930-045505-2350): Attention_v5 exact on all 122,228 heads incl. 112 non-finite, 0 binding / 0 self mismatches; PR #486 body updated (root pushed 12cea8ee). WAITING gate (b) on vy-sm120-attention-2 (last test qwen3 build-global), check after 05:20Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6. vy-nebius-1 unusable from here: research refuses provider 'ssh' (runpod only)
CHECKPOINT 12cea8ee (05:04Z) [open] WAITING on vy-sm120-attention-2: v5 correspondence r20260930-045505-2350 (60/60 launches ok, 14/60 row checks, all v5-exact so far) and gate (b) base r20260930-034927-48b4 / head r20260930-035219-a82d (last test test_the_stored_tp2_moe_builds qwen3). circuit-check Attention_v5: 0 failures (art:97c2dbcf). check after 05:20Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; GitHub push blocked (token invalid), v5 bundle in store artifacts/
CHECKPOINT 12cea8ee (04:55Z) [open] Attention_v5 (FA2 rescale-only Check_inf) on branch cursor/vllm-sm120-fa2-check-inf-0ec6 @ 12cea8ee, NOT pushed: GitHub token on this VM is invalid (gh auth: token invalid); bundle at $STORE/artifacts/vllm-sm120-attention/. v5 CPU checks pass (tests, kernel self-check, partition rule 0 violations / 0 recomputed). v5 correspondence r20260930-045505-2350 and gate (b) running on vy-sm120-attention-2
CHECKPOINT 4975dc66 (04:38Z) [open] coordinator decision fa2-inf-guard read: Attention_v4 can't be reused bit-exactly (FA2 guards max*scale in every block; v4 unguards it), handoff 20260930T0438Z-handoff-from-vllm-sm120-attention.md; starting Attention_v5 (FA2 Check_inf placement) stacked on #477; gate (b) still at 98%
CHECKPOINT 4975dc66 (04:22Z) [open] WAITING gate (b) on vy-sm120-attention-2: base r20260930-034927-48b4 and head r20260930-035219-a82d both at 98%, last test (olmoe manifest build-global) running; head lints failed P8 on arch literals in the evidence string, fixed at 4975dc66, whose lints + touched tests pass (r20260930-042000-6c90). check after 04:35Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; next: jdiff, terminate, handoff
CHECKPOINT cfcbfcef (03:52Z) [open] WAITING gate (b)+lints on vy-sm120-attention-2 (pod x8zpxecwqjekb5): base r20260930-034927-48b4 (f740c1d5) and head r20260930-035219-a82d (cfcbfcef), concurrent after the base bootstrap; r20260930-035023-a534 stopped while waiting (no tests ran). check after 04:15Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; PR #477 draft; next: jdiff, handoff
CHECKPOINT cfcbfcef (03:48Z) [open] pod estimate (revised: no CPU stock at 8 or 16 vCPU in any flavor): vy-sm120-attention-2 (RTX PRO 6000 Server Edition, SECURE on-demand, $2.09/h, --max-hours 3) for gate (b) + lints, base f740c1d5 and head cfcbfcef on the same pod: ~1.5 GPU-h, ~$3.1; lane total then ~$4.4 of $12
CHECKPOINT cfcbfcef (03:46Z) [open] pod estimate: vy-sm120-attention-cpu-1 (RunPod CPU cpu3g, 16 vCPU, --max-hours 3) for gate (b) + lints, base f740c1d5 (PR #465 tip) and head cfcbfcef on the same pod: ~1.5 h, ~$1; lane spend so far ~$1.30
CHECKPOINT b5c84fa4 (03:38Z) [open] captures done, pod vy-sm120-attention-1 terminated 03:38Z (~0.62 GPU-h, ~$1.30). FA2 on sm_120 = Attention_v2{DOT=Hopper,INV=Fa2InvSum} on all 122,228 finite heads (Attention_v3: 997 heads differ); MUFU = core tables; tile = fa2_kblock_n; FA2 taps exact 76/76 x2. Runs r20260930-033258-f611 (art:d342a748), r20260930-030755-9aab (art:592bc0ae). Next: registration commit
CHECKPOINT 08658275 (03:08Z) [open] WAITING r20260930-030444-c4b5 (FA2 capture) and r20260930-030755-9aab (FA2 tap build + fa_tap_exactness, default + guarded) on vy-sm120-attention-1, check after 03:28Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; next: read both, registration PR
CHECKPOINT 08658275 (03:06Z) [open] WAITING r20260930-030444-c4b5 on vy-sm120-attention-1 (pod 2c11k8o7d6xu7y), check after 03:28Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; next: read the FA2 capture (MUFU, tile, v2_hopper/v3_ampere/fa2_check_inf rows, engine), then the registration on cursor/vllm-sm120-attention-0ec6
CHECKPOINT 08658275 (03:01Z) [open] pod estimate: vy-sm120-attention-1 (RTX PRO 6000 Blackwell Server Edition, SECURE on-demand, 1 GPU, $2.09/h, --max-hours 3): ~1.5 GPU-h, ~$3.1 (bootstrap ~15 min, FA2 capture + MUFU + engine check ~30-45 min); lane share $12; capture script at cursor/vllm-sm120-attention-0ec6@08658275
CHECKPOINT d993873f (02:53Z) [open] source read of vLLM d9105ea8 + vllm-flash-attn 506341a: cc12 selects FLASH_ATTN/FA2, num_splits=1 under batch invariance, FA2 is 8.0+PTX so sm_120 runs a driver JIT, kBlockN arch-free; Check_inf only in masking steps. Next: capture script, then pod vy-sm120-attention-1

## Summary (FA2 on sm_120)

**Result.** vLLM `d9105ea8` on cc 12.0 (RTX PRO 6000 Blackwell, 188 SMs) selects FLASH_ATTN, FA2. `_vllm_fa2_C` ships only sm_80 SASS + compute_80 PTX, so on sm_120 the kernel is the driver's JIT of the PTX. It computes the Hopper-step chain exactly:
- **Finite heads:** `Attention_v2{BN=fa2_kblock_n(D), DOT=HopperBF16WgmmaDot16_v1, INV=Fa2InvSum_v1}` on every finite head.
- **Every head, including ±inf and NaN score rows:** `Attention_v5` (FA2's own `Check_inf` placement).
- **Ampere step:** `Attention_v3` differs on 997 finite heads, so sm_120 is not an Ampere-step target.

**Evidence (research runs, custody on R2):**
- **`fa2_target_capture` `ef4b2584`** (`r20260930-033258-f611`, `art:d342a748`; card 1, driver 595.91):
  - 19,232 rows / 122,228 heads over D 64/96/128/256, tap-exactness cases, a wide-exponent case, and 12 pinned models' head shapes;
  - kBlockM 64 / kBlockN `fa2_kblock_n(D)` on all 60 launches;
  - MUFU ex2/rcp = core's tables on all 2^32 inputs, both JIT and native;
  - engine FlashAttentionImpl FA2 on 30 layers.
- **`fa2_target_capture` `2f7cc71f`** (`r20260930-045505-2350`; card 2, driver 580.17): the same, plus the registered `Attention_v5` and its target binding, with 0 mismatches.
- **`fa_tap_exactness`** of the FA2 tap built on sm_120: default `9dee6b6f`, guarded-max `9403e9fe`, 76/76 each (`r20260930-030755-9aab`, `art:592bc0ae`).
- **circuit-check** of `Attention_v5`: 0 failures (`art:97c2dbcf`).

**PRs:**
- **#477** (`cursor/vllm-sm120-attention-0ec6` @ `4975dc66`, stacked on #465): `blackwell_consumer` FA2 registration, the `_profile` FA-version fallback, and the capture tool as a registered property record.
- **#486** (`cursor/vllm-sm120-fa2-check-inf-0ec6` @ `12cea8ee`, stacked on #477): `Attention_v5`. `v4` can't be reused, because FA2 guards `max * scale` in every block.

**Found, not fixed:**
- **FA2 guard placement on every FA2 target** (sm_89 `Attention_v3`, H100 forced-FA2 `Attention_v2`): the same placement holds, so non-finite rows differ from those chains. Reported, and not changed, per the coordinator.
- **NaN encoding:** every attention chain's row-sum FMA (core `F32FmaFtz_v1`) gives NaN `0x7FC00000`, where the GPU writes `0x7FFFFFFF`.
- **Bench template:** `backends/numerical` `ATTN_SEMANTICS` has no "FA2 on the Hopper step" entry (it would name H100 forced-FA2 and sm_120 FA2 VU sets).
- **VU export:** `vu_export` exports no `Attention_v4` / `Attention_v5` VUs.
- **Tooling:** `research pods ssh|run` refuse a `provider = "ssh"` machines.d entry (vy-nebius-1).
