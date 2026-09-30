---
lane: vllm-sm120-attention
kind: report
created: 2026-09-30T02:53Z
status: final
---

CHECKPOINT 70a4504e (08:36Z) [final] FINAL: #477 and #486 merge-ready (FA2 on sm_120: Attention_v2 on finite heads; Attention_v5 exact on every head); NVFP4 on sm_120 = match (art:3bc1b2c4); pods vy-sm120-attention-1/-2 terminated (03:38Z, 07:01Z), ~$8.00 RunPod + ~15 GPU-min Kueue
CHECKPOINT 70a4504e (08:13Z) [open] NVFP4 capture: job 56 ran but every load failed (vLLM sampler warmup JIT-builds FlashInfer top_k and ninja is not on PATH) and the probe path was one level short; fixed (VLLM_USE_FLASHINFER_SAMPLER=0 as the integration's env, venv bin on PATH, parents[4]); resubmitted as job 81 nvfp4-capture-attn-3. check after 08:30Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6
CHECKPOINT 70a4504e (07:56Z) [open] NVFP4 capture: job 35 FAILED_SETUP (pod_bootstrap can't write the research-owned synced tree as uid 1000); resubmitted as job 56 nvfp4-capture-attn-2 with a setup-only override (untracked port-capture-attn.yaml); handoff 20260930T0756Z. check after 08:12Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6
CHECKPOINT 70a4504e (07:38Z) [open] NVFP4 capture: Kueue job 35 pod vanished in SETTING_UP after ~5.5 min (pod not found -> SkyPilot 'preempted', RECOVERING, recovery 1); re-checking at 07:48Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6
CHECKPOINT 70a4504e (07:14Z) [open] NVFP4 kernel capture (06:17Z task): Kueue port-capture job 35 nvfp4-capture-attn PENDING on vy-nebius-1 (circuits); prefetched nvidia/Qwen3-8B-FP4@ccd10a89 + RedHatAI/Qwen3-8B-NVFP4@e391349c into /workspace/hf (r20260930-071006-e96d). submit.sh syncs untracked files (research pods sync = git ls-files --cached --others --exclude-standard), so nothing was committed; script lanes/vllm-sm120-attention/tools/nvfp4_kernel_capture_gpu.py. Pinned vLLM: VLLM_BATCH_INVARIANT forces CutlassNvFp4LinearKernel. check after 07:35Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6
CHECKPOINT 70a4504e (07:04Z) [open] pod vy-sm120-attention-2 (x8zpxecwqjekb5) TERMINATED 07:01Z after #486's gate (b) and custody (8/8 attempts preserved); no RunPod pods of this lane remain; lane spend ~$8.00 (pod 1 ~$1.30, pod 2 ~$6.70). #486 MERGE-READY handoff 20260930T0702Z; #477 MERGE-READY 20260930T0547Z. Next: the NVFP4 kernel capture (06:17Z note) as a Kueue port-capture job on vy-nebius-1
CHECKPOINT 70a4504e (06:31Z) [open] WAITING #486 gate (b) on vy-sm120-attention-2: base486 r20260930-051932-96ce / head486 r20260930-051942-008f in the last test (qwen3 build-global, 31 min of ~55), check after 06:58Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; next: jdiff, terminate, #486 handoff, FINAL
CHECKPOINT 70a4504e (05:48Z) [open] #477 MERGE-READY: gate (b) jdiff art:a175e2b2, 0 unexpected (the one new failure, P8, fixed at 4975dc66); PR body updated; handoff 20260930T0547Z-handoff-from-vllm-sm120-attention-477-merge-ready.md. WAITING #486 gate (b) base486 r20260930-051932-96ce / head486 r20260930-051942-008f (MoE build-global tests), check after 06:30Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6
CHECKPOINT 70a4504e (05:24Z) [open] WAITING on vy-sm120-attention-2: #477 gate (b) base r20260930-034927-48b4 / head r20260930-035219-a82d (last test qwen3 build-global); #486 gate (b) base486 r20260930-051932-96ce (4975dc66) / head486 r20260930-051942-008f (12cea8ee). #486 head lints failed P10 (derived_rows 949 > 944), fixed at 70a4504e (pushed), whose lints + touched tests pass (r20260930-052148-661b). check after 05:45Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6
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

## FINAL

~~~text
tip: cursor/vllm-sm120-fa2-check-inf-0ec6 @ 70a4504e (base cursor/vllm-sm120-attention-0ec6 @ 4975dc66, on cursor/vllm-sm120-target-422d @ f740c1d5)   merge-with: #465 -> #477 -> #486
known-failures: gate (b) base's 37 failed / 16 errors, none new on either head    pod: vy-sm120-attention-1 terminated 03:38Z, vy-sm120-attention-2 terminated 07:01Z; ~$8.00 RunPod (+ ~15 GPU-min on vy-nebius-1 Kueue)
artifacts: art:d342a748 art:7bc06ae3 art:592bc0ae art:97c2dbcf art:a175e2b2 art:a5c0e8e5 art:00ff2fa3 art:0006ccaf art:0f9bf31a art:7f6c0964 art:1b03bd9b art:5b51253d art:3bc1b2c4
~~~

**PRs:**
- **#477** (merge-ready, handoff `20260930T0547Z`): FA2 on sm_120 binds the Hopper-step `Attention_v2`; the `_profile` fallback; the capture tool.
- **#486** (merge-ready, handoff `20260930T0702Z`): FA2's per-iteration `Check_inf` as `Attention_v5`. It's exact on every head, non-finite rows included, with the partition invariants and circuit-check passing.

**Stretch, NVFP4 on sm_120:** match (finding `20260930T0835Z-finding-nvfp4-kernel-sm120.md`, `art:3bc1b2c4`; copy in `lanes/pous/20260930T0835Z-handoff-from-vllm-sm120-attention.md`). vLLM's `CutlassNvFp4LinearKernel` runs `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`, the pinned `sm120.mma.m16n8k64.e2m1.nvf4`.

**Handoffs received, all acted on:**
- `20260930T0240Z-note-from-vllm-coordinator-budget-line-live`
- `20260930T0253Z-note-from-vllm-coordinator-sweep-target`
- `20260930T0314Z-note-from-vllm-coordinator-465-fa2-items`
- `20260930T0359Z-decision-from-vllm-coordinator-fa2-inf-guard`
- `20260930T0547Z-note-from-vllm-coordinator-vy-nebius-1-ready`
- `20260930T0605Z-note-from-vllm-coordinator-kueue-on-vy-nebius-1`
- `20260930T0617Z-note-from-vllm-coordinator-nvfp4-capture-reassigned`
- `20260930T0626Z-note-from-vllm-coordinator-terminate-pod-after-486-gate`

**Handoffs sent (lanes/vllm-coordinator):**
- `0438Z`: `v4` can't be reused.
- `0547Z`: #477 merge-ready.
- `0702Z`: #486 merge-ready.
- `0756Z`: `port-capture` setup failure.
- `0835Z`: NVFP4 verdict and the custody gap.

**Found, not fixed:**
- The attention chains' `_v1` FMA NaN is `0x7FC00000`, where the GPU writes `0x7FFFFFFF`.
- `vu_export` has no `Attention_v4` / `v5`.
- `ATTN_SEMANTICS` has no FA2-on-Hopper-step entry.
- `port-capture`'s setup can't write a synced tree, and its in-container attempts aren't published to the store.
- `research data label` has no `custody` key, though notes sync suggests one.
