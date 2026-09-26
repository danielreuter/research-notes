---
lane: vllm-more-exports
kind: report
created: 2026-09-26T08:04Z
status: final
---

CHECKPOINT 898c32ef (14:25Z) [final] reopen: #67 export re-run not run -- no working L40S (secure stock none; 2 community L40S with broken CUDA, terminated 14:16Z/14:23Z, ~$0.3); tree cursor/vllm-67-rerun-0df4 8f2f1624 (#63+#80) and a Commit-only restore recipe (~2.7 h on a secure >=233 GB L40S) ready for a later window
CHECKPOINT 898c32ef (14:24Z) [open] 14:26Z: reopen stopped: no working L40S (secure stock none; 2 community L40S with broken CUDA, terminated); handoffs vllm-coordinator + vllm-vu-export 1424Z; no pods; FINAL next; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 8f2f1624 (14:17Z) [open] 14:22Z BUSY: vyv-more-exports-moe2 (community L40S) TERMINATED: driver 550/CUDA 12.4 can't run the cu129 stack (BOOTSTRAP_FAIL_CUDA); no L40S/L40/RTX6000Ada stock now (RunPod stock=None) for a >=240 GB replacement; polling until ~14:45Z (after that #67 can't end even by 17:45Z); asked vllm-coordinator 1417Z for a 17:45Z guard on the replacement; ~$0.5 spent; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 8f2f1624 (14:11Z) [open] 14:12Z BUSY: pod vyv-more-exports-moe2 (b83fk4drgx340u) run r20260926-141055-d540 = #67 Commit-only (+export, PR #80+#63 tree 8f2f1624) over the Build restored from art:8180df8f programs/ (VM->pod upload took 14 min); waits for bootstrap r20260926-134954-df82, then manifest ~15 min, Commit+replay ~100 min, export; check-back 14:40Z; stop at 16:45Z; ack vllm-vu-export 1344Z (#63 OK, #80); agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 8f2f1624 (13:54Z) [open] REOPENED BUSY 13:55Z: pod vyv-more-exports-moe2 (b83fk4drgx340u, 1x L40S community 251 GB $0.79/h) bootstrap r20260926-134954-df82; next: #67 Commit-only over the preserved Build (tree cursor/vllm-67-rerun-0df4 8f2f1624 = #63+#80), check-back 14:10Z; stop at $12 or 16:45Z; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (13:46Z) [open] REOPENED 13:45Z for one run: #67 re-run with PR #80 (export budget fix) + PR #63; ~$12 vLLM, stop at budget or 16:45Z guard; NOT final; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (13:24Z) [final] no captured sets: #74 Commit needs ~300 GiB (>251 GB H100; bounded/exclude finalize crashes), #67 export drew 0 VUs (vu_store budget includes >18 min population build); PR #63 (FP8 block + MoE expert coordinates) MR sent; pods terminated 12:29Z/13:20Z, ~$26.7 of $30
CHECKPOINT 898c32ef (13:24Z) [open] 13:26Z: report FINAL section written; handoffs sent (vllm-coordinator 1323Z, coordinator MR 1322Z, vllm-vu-export 1322Z); PR #63 updated; no pods; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (13:21Z) [open] 13:22Z: vyv-more-exports-moe TERMINATED 13:20Z (2 runs preserved); both pods down, ~$26.7 of $30. #67 Build/Match/Commit through sampled replay PASS (coverage 406220 missing 0, C2 16120/16120 equal, replay not-retained 0 failed 0) but its export drew 0 VUs: the export's 600 s budget counts the population build over 33 request Programs (>18 min), stopped 13:17Z; #74 no export (Commit memory, see report). No sets registered. Next: handoffs, merge request PR #63, FINAL; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (12:57Z) [open] 12:59Z BUSY: pod vyv-more-exports-moe run r20260926-082002-43e0 (#67): replay workers done 12:50Z, parent finishing the replay record, export (600 s) next; will stop after the export verifies (skip on-pod program graph; vllm-vu-export rebuilds from preserved programs/), check-back 13:10Z; ~$26.5 of $30; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (12:50Z) [open] 12:51Z BUSY: pod vyv-more-exports-moe run r20260926-082002-43e0 (#67): sampled replay, 32 workers since 12:36Z, memory flat, export (600 s) next, check-back 13:05Z; ~$26.1 of $30 (pod alone lasts to ~14:35Z); agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (12:43Z) [open] 12:43Z BUSY: pod vyv-more-exports-moe run r20260926-082002-43e0 (#67): sampled replay forked 32 workers over 38748 VUs at 12:36Z, anon plateaued at 86 GiB (+86 GiB pinned, cap 217), export (600 s) follows, check-back 12:55Z; ~$25.8 of $30; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (12:32Z) [open] 12:36Z BUSY: report updated with the #74 memory findings; pod vyv-more-exports-moe run r20260926-082002-43e0 (#67) sampled replay, export next, check-back 12:45Z; ~$25.4 of $30; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (12:32Z) [open] 12:33Z BUSY: pod vyv-more-exports-moe run r20260926-082002-43e0 (#67): sampled replay since 11:40Z (158/217 GiB non-reclaimable, no limit hits), export (600 s) next, check-back 12:45Z; asked vllm-coordinator (1232Z) to keep the pod to <=14:30Z within $30; H100 terminated 12:29Z; FP8 no-sets handoffs to flock-backend + bligero-real-k (1228Z); ~$25.3 of $30; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (12:27Z) [open] 12:30Z: vyv-more-exports-h100 TERMINATED 12:29Z (6 runs preserved; ~$15.4). #74 has no export: Match PASS only at 32 MiB snapshot cap; unbounded Commit needs ~300 GiB (197 GiB pinned staging, FA3 hidden 136 GiB, + 69 GiB C2 Programs objects) > 234 GiB cap; --bounded-staging --retain-exclude fa3_hidden_m1 (fits, 158 GiB bound) crashes in finalize: vllm_v1.fold 'leaf must be a 32-byte digest' (r20260926-115930-46a1). #67 vyv-more-exports-moe r20260926-082002-43e0 sampled replay, export next, check-back 12:45Z; ~$25 of $30; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (12:13Z) [open] 12:15Z BUSY: #67 vyv-more-exports-moe r20260926-082002-43e0 sampled replay 35 min (epoch Commit ended at 83 min, ~12:20Z), export next, check-back 12:30Z; #74 vyv-more-exports-h100 r20260926-115930-46a1 bounded-staging Commit in prep (53 GiB, no pinned staging yet), check-back 12:35Z; ~$23.5 of $30, stop ~13:20Z; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (11:59Z) [open] 12:00Z BUSY: #74 Commit restarted as r20260926-115930-46a1 on vyv-more-exports-h100 (STAGES=commit over the kept Build+Match, --bounded-staging --retain-exclude fa3_hidden_m1: the unbounded Commit r20260926-101428-71e2 held 197 GiB pinned + 27 GiB anon at the 234 GiB cap in the oracle compare, stopped before OOM); check-back 12:30Z. #67 r20260926-082002-43e0 on vyv-more-exports-moe: sampled replay, export next, check-back 12:15Z. ~$22 of $30; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (11:51Z) [open] 11:51Z BUSY: #74 vyv-more-exports-h100 r20260926-101428-71e2 Commit instrumented run done (binding 276493/276493, composition OK), oracle compare running at 233/234 GiB (197 GiB pinned host staging; Commit warns retention bound 562 GiB) -- OOM risk, watching; #67 vyv-more-exports-moe r20260926-082002-43e0 sampled replay (179/217 GiB), export next; check-back 12:05Z; ~$21 of $30; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (11:41Z) [open] 11:42Z BUSY: #67 on vyv-more-exports-moe run r20260926-082002-43e0: Commit C2 oracle compare 16120/16120 equal, coverage OK, sampled replay running (export next), 159 GiB, check-back 12:15Z; #74 on vyv-more-exports-h100 run r20260926-101428-71e2: Commit prep since 11:24Z, check-back 12:40Z; ~$20.6 of $30 (stop ~13:20Z); agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (11:32Z) [open] 11:32Z BUSY: pod vyv-more-exports-h100 (b11jkfokvzu5yi) run r20260926-101428-71e2 = #74 qwen3-4b-fp8 Match PASS 11:23Z, Commit+export running, check-back 12:40Z; pod vyv-more-exports-moe (axadsirn2n0kqq) run r20260926-082002-43e0 = #67 olmoe b32 Match PASS 10:57Z, Commit (oracle compare) running, check-back 12:20Z; ~$19.5 of $30, hard stop ~13:20Z; agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (11:24Z) [open] 11:25Z: #74 Match PASS at 32 MiB snapshot cap (verdict/global PASS, tokens equal, fold True), Commit started 11:24Z; #67 Commit pair 0 validation (137 GiB); ~$19 spent; may skip on-pod program graphs (vllm-vu-export rebuilds from preserved programs/) to hold $30. WAIT vyv-more-exports-h100 r20260926-101428-71e2 check-back 12:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 12:20Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (11:15Z) [open] 11:16Z: #74 fold done (46 min), global match since 11:07Z; #67 Commit since 10:57Z (CPU prep); ~$17 spent. WAIT vyv-more-exports-h100 r20260926-101428-71e2 check-back 11:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 12:20Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (10:58Z) [open] 10:58Z: #67 Match PASS (4279 s; verdict/global PASS, tokens equal, fold True), Commit started 10:57Z (epoch took 4962 s); #74 fold 37 min, 125 GiB; ~$16 spent. WAIT vyv-more-exports-h100 r20260926-101428-71e2 check-back 11:30Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 12:20Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (10:44Z) [open] 10:45Z: Match folds running (#74 since 10:21Z, #67 since 09:55Z, 123 GiB); ~$15 spent. WAIT vyv-more-exports-h100 r20260926-101428-71e2 check-back 11:15Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 11:15Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (10:25Z) [open] 10:25Z: #74 resumed Match capture OK at 32 MiB cap (5 min, shmem 83 GiB), fold since 10:21Z; stopped run r20260926-081920-036d PRESERVED (holds #74 programs/); #67 fold since 09:55Z (103 GiB); ~$14 spent. WAIT vyv-more-exports-h100 r20260926-101428-71e2 check-back 11:00Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 11:00Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (10:14Z) [open] 10:15Z #74 Match capture thrashed at the 234 GiB cgroup (torch pinned host cache 230 GiB in pow2 blocks; derived snapshot cap 137 MB/tensor, D87; planner said 71 GiB): stopped r20260926-081920-036d (Build kept, custody incl. programs/), resumed match,commit with MATCH_SNAP_MAX_BYTES=32MiB (cap of record) as r20260926-101428-71e2. WAIT vyv-more-exports-h100 r20260926-101428-71e2 check-back 10:45Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 10:45Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4 (#67 Match fold)
CHECKPOINT 898c32ef (10:02Z) [open] 10:02Z: #67 Build PASS 09:46Z (9516d799, workload 7b79c784, manifest db0da935), Match capture done (7 min, peak 151 GiB), fold running; #74 required manifest since 09:47Z; ~$11 spent. WAIT vyv-more-exports-h100 r20260926-081920-036d check-back 10:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 10:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (09:42Z) [open] 09:47Z: #74 derives done 6-wide 3680 s, workload compose running; #67 compose done (25 min), required manifest running; request Programs differ from the records (#74 55fd66b6 vs b725f253, #67 e9092446 vs a7be1df3) so copied into run custody (programs/, 634/426 MB) for vllm-vu-export's graphs. WAIT vyv-more-exports-h100 r20260926-081920-036d check-back 10:30Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 10:30Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (09:21Z) [open] 09:22Z: #74 Build 9/10 derives (envelope LP1024_T127 left); #67 derives done 8-wide in 2608 s, workload Program compose running since 09:06Z; ack vllm-vu-export 0830Z reply: (b), art ids only, program-graphs/ stays theirs. WAIT vyv-more-exports-h100 r20260926-081920-036d check-back 09:50Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 09:50Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (09:01Z) [open] 09:02Z Builds: #74 6/10 derives (long LP1024/365/633/817 T~120 left, 88 GiB), #67 32/34; ~$6 spent. WAIT vyv-more-exports-h100 r20260926-081920-036d check-back 09:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 09:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4
CHECKPOINT 898c32ef (08:34Z) [open] pod tests on 898c32ef: vux test set 148 pass/1 skip r20260926-082552-2706, by-name+dead-modules+vu_export 22 pass r20260926-083238-6f6f; PR #63 draft. WAIT vyv-more-exports-h100 r20260926-081920-036d check-back 09:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: #74 Build 3/9 derives; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 09:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: #67 Build
CHECKPOINT 898c32ef (08:21Z) [open] 898c32ef (FP8 block + MoE expert coordinates; lints clean in-process). WAIT vyv-more-exports-h100 r20260926-081920-036d check-back 09:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: #74 Build(6 jobs)->Match->Commit+export; WAIT vyv-more-exports-moe r20260926-082002-43e0 check-back 09:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: #67 same (auto jobs); stop at $30 ~13:20Z
CHECKPOINT e3a2d81d (08:11Z) [open] WAIT vyv-more-exports-h100 r20260926-080641-f752 check-back 08:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: bootstrap (B0,QWEN3_4B_FP8); WAIT vyv-more-exports-moe r20260926-080751-376f check-back 08:40Z agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4: bootstrap (B0,OLMOE); next: #74/#67 rows; hard stop $30 ~13:20Z (handoff 0812Z ack)
CHECKPOINT e25e3614 (08:04Z) [open] started (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4): #74 FP8 H100 + #67 OLMoE TP1; exporter drops FP8/MoE-expert GEMM VUs today (weight > max_row_words) -> adding coordinate decompositions on cursor/vllm-more-exports-0df4; #57 skipped (FAIL-class, no evaluators); pods next; handoff vllm-coordinator 0806Z

## Plan and state

Goal 7 of the overnight plan: captured verification-unit input sets beyond #101 and #4. The priorities are an H100 FP8 row, then Gemma-2-2B, then one MoE row. The recipe is vllm-vu-export's (`vux_row.sh` / `vux_redraw.sh`, `register_export.py`), copied into `evidence/`; its files are untouched. The budget is $30 of the vLLM budget, a hard stop, which lands about 13:20Z at $5.67/h (handoff `20260926T0812Z-handoff-from-vllm-coordinator.md`: pods registered, WAIT checkpoints kept).

- **#74 qwen3-4b-fp8 H100:** pod `vyv-more-exports-h100` (`b11jkfokvzu5yi`, H100 80GB SXM, 251 GB cgroup, $3.49/h, AP-IN-1). Bootstrap `r20260926-080641-f752`, row `r20260926-081920-036d` (BUILD_JOBS=6, limits `{"per_family_override": {"Gemm_v2": 24}, "max_seconds": 1200}`).
- **#67 olmoe b32 TP1:** pod `vyv-more-exports-moe` (`axadsirn2n0kqq`, 2x L40S, run on GPU 0, 233 GB cgroup, $2.18/h, EUR-IS-2). No 1x L40S with 200 GB or more was in stock. Bootstrap `r20260926-080751-376f`, row `r20260926-082002-43e0` (BUILD_JOBS=auto, max_seconds 1200).
- **Planner (PAIRS=1), build / match / commit:** #74 41 / 71 / 170 GiB; #67 15 / 127 / 187 GiB; #57 32 / 126 / 224 GiB.
- **#57 Gemma is skipped.** It's FAIL-class (Match has no fold, Commit local_replay FAIL). Its distinct templates have no registered row evaluator: GeluTanhMul_v1, AttentionSoftcap_v1, NarrowF32ToBf16_v1 and Bf16MulScalar_v1. Its RMSNorm is interior structure with no identity. So the exporter can't capture what Gemma was chosen for; only Bf16MulScalarTensor_v1 would be new.

## Found and fixed: the exporter dropped FP8 and MoE-expert GEMM VUs

On main `e3a2d81d`, `vu_store._evaluation` samples weight rows only for `Gemm_v1` / `Gemm_v2`. Every other evaluation whose registered-weight operand exceeds `max_row_words` (4M words) returns None, and the unit is counted `not_stored_operand_too_large`. That hits every `ScaledMmFp8Block_v1` VU (weight N×K e4m3, for example 19456×2560) and every `MoeExpertGemm_v1` / `W_v1` VU (the whole [E, N, K] slab). So #74 would have exported no FP8 GEMM, and #67 no expert GEMM.

The fix is branch `cursor/vllm-more-exports-0df4` @ `898c32ef`, [PR #63](https://github.com/danielreuter/verity/pull/63):
- **New decompositions** (each re-evaluated like the existing ones):
  - `ScaledMmFp8Block_v1` → `ScaledMmFp8BlockCoordinate<K,G>`. Ports: x e4m3[K], sx f32[K/G], w e4m3[K], sw f32[K/G] (the weight row's block scales), y bf16[1].
  - `MoeExpertGemm_v1` → `GemmCoordinate<K>` over the routed expert's rows.
  - `MoeExpertGemmW_v1` → `RoutedGemmCoordinate<K>` (x, w, g, y).
- **Store:** `WEIGHT_ROWS_OF` gives the weight operand's [N, K] rows, and the store keeps a row sample of them. The checkpoint fallback reads the weight's own word type; it had been hard-coded to u16.
- **Checks:** `fp8_block_coordinate` equals `scaled_mm_fp8_block_row` on all 256 coordinates of a 384×256 block GEMM. The new tests pass in-process. The by-name, P10 and argument-free lint ratchets are clean.
- **Pod test run:** `r20260926-082552-2706`. The row runs' background tests failed to collect: my script started them after `cd integrations/vllm`, a PYTHONPATH mistake. It's fixed in `vme_row.sh`.

**The FP8 statement mismatch matters to the FP8 lanes.** The served FP8 GEMM is block-scaled. Per 128-tile, `temp` = 4 wgmma e4m3 k32 steps from +0, then `acc = FFMA(temp, sx·sw, acc)`, then bf16. So no served FP8 coordinate is an unscaled K-long chain, which is what `gemm-coordinate/k<K>/sm90-wgmma-e4m3` states. The exact captured sets are `ScaledMmFp8BlockCoordinate`. `evidence/derive_fp8_chain_sets.py` writes the spine-format `input-set/v1` sets over the same captured x/w bytes, with y from the chain relation (source "captured inputs, model y"). It was tested on a synthetic block set, and `input_sets.verify` passes.

## #74 (qwen3-4b-fp8, H100): Build and Match pass, but the Commit doesn't fit a 251 GB pod, so there's no export

- **Build PASS**, 6-wide in 3680 s. The request Program is `55fd66b6…`, not the record's `b725f253…`; workload `09bec925…`, manifest `550c6995…`. The request Programs are preserved in `r20260926-081920-036d` under `programs/` (634 MB).
- **Match with the derived snapshot cap thrashed.** The cap was 137,943,040 B per tensor (D87: 3545 rows × GU 19456 × 2 B). The capture's torch pinned-host cache reached 230 GiB in power-of-two blocks (297×256 MB, 931×64 MB, 1830×32 MB, …). The GPU sat at 0% under ~145M page scans at the 234 GiB cgroup, against a planner estimate of 71 GiB. I stopped the run: `r20260926-081920-036d`.
- **Match PASS at the 32 MiB cap of record** (`MATCH_SNAP_MAX_BYTES=33554432`), resumed over the kept Build as `r20260926-101428-71e2`: capture 5 min at 83 GiB, fold 46 min, verdict/global PASS, tokens equal, fold True, wall 4097 s.
- **The unbounded Commit** (same run) got through the instrumented run: binding 276493/276493, composition OK, coverage 262162 missing 0. By the oracle compare it held 197 GiB of pinned staging plus 27 GiB anon at the cap.
  - The Commit's own sizing: host retention bound 562,202 MiB. The stream of record is 152,257 MiB, of which the hidden stream is 139,410 MiB; step 0 alone is 142,471 MiB.
  - The C2 Programs forecast is 7,853,122 instance rows → 70,439 MiB of Python objects. That's about 300 GiB in total, so I stopped it before an OOM.
- **Bounded staging crashes.** `EXTRA_COMMIT_ARGS="--bounded-staging --retain-exclude fa3_hidden_m1"` (STAGES=commit, `r20260926-115930-46a1`): its planner says ADMIT, with a host bound of 162,049 MiB (hidden 146,380 MiB excluded). It crashed in `native_host.finalize` → `scheme.run_root` → `vllm_v1.fold`: `InvalidArtifact: leaf must be a 32-byte digest`. That's a bug in the flag path; I didn't touch commitment code.
- **Needed for #74:** an H100 host with at least 320 GB RAM (unbounded Commit, 32 MiB Match cap), or the bounded/exclude finalize fixed. Pod `vyv-more-exports-h100` was terminated at 12:29Z with all 6 runs preserved, about $15.4. The FP8 lanes were told: `lanes/flock-backend/` and `lanes/bligero-real-k/` `20260926T1228Z-handoff-from-vllm-more-exports.md`.

## #67 (olmoe b32 TP1): the Commit passes through the replay, but the export drew 0 VUs

- **Build PASS:** 8-wide derives in 2608 s, then a 25 min workload compose. Digest `9516d799…` (request `e9092446…`, not the record's `a7be1df3…`), workload `7b79c784…`, manifest `db0da935…`.
- **Match PASS** (4279 s): verdict and global PASS, tokens equal, fold True. The capture took 7 min and peaked at 151 GiB.
- **Commit** (from 10:57Z):
  - Coverage 406220 with 0 missing (the epoch's #67 had 20,928 missing).
  - C2 oracle compare 16120/16120 equal.
  - The sampled replay forked 32 workers over 38,748 VUs at 12:36Z. It ended "not retained 0, failed 0" at about 12:58Z. Memory peaked at 86 GiB anon plus 86 GiB pinned of 217 GiB, with no OOM.
- **Export: 0 VUs.** `export_vus` started at 12:58:01 and had stored no value and no `export.json` by 13:16.
  - The cause: `vu_store.export_vus` takes `t0` at its top, and `_run_draw` measures `max_seconds` from it. The `ProgramIndex` + `population` build over 33 request Programs took more than 18 minutes, so the budget expired before the first draw.
  - I had lowered this run's budget from 1200 s to 600 s at 12:21Z to hold the $30. The default is also 600 s, so a default-on export of any large row would do the same.
  - Handed to vllm-vu-export, `lanes/vllm-vu-export/20260926T1322Z-handoff-from-vllm-more-exports.md`.
- **Stopped at 13:17Z** for the budget and the 13:30Z deadline. The Commit's evidence (`commit.log`, `row.log`, `stages.txt`, timeline, summaries) was copied into the run's `evidence/` first. The request Programs are in its `programs/` (426 MB, 33 dirs). Run preserved; pod `vyv-more-exports-moe` terminated at 13:20Z.

## Handoffs

- **Received:** `20260926T0812Z-handoff-from-vllm-coordinator.md`: register pods, WAIT checkpoints, $30 hard stop. Done; see the checkpoints.
- **Received:** `20260926T0830Z-handoff-from-vllm-vu-export.md`: option (b), art ids only, and `program-graphs/` stays theirs. I didn't touch `program-graphs/`, and no exports exist to hand over.
- **Received:** two messages relayed by my launcher, the coordinator's asks to register pods and checkpoint at each wait. My checkpoints had reached research-notes but not the store mirror the vLLM coordinator reads. From 11:32Z each checkpoint also copies this report to `$STORE/internal/lanes/vllm-more-exports/`.
- **Sent:**
  - `vllm-coordinator/` 0806Z (pods and plan), 1232Z (H100 down, deadline ask), 1323Z (final status).
  - `vllm-vu-export/` 0830Z (additions, program-graphs question), 1322Z (the budget finding and the programs locations).
  - `flock-backend/` and `bligero-real-k/` 1228Z (no captured FP8 sets, why, and the format when they exist).
  - `coordinator/` 1322Z (merge request for PR #63).

## FINAL

~~~text
tip: cursor/vllm-more-exports-0df4 @ 898c32ef (base main@e3a2d81d)        merge-with: none (PR #63; merges cleanly with main e77d40c9)
known-failures: none    pod: vyv-more-exports-h100 terminated 12:29Z, vyv-more-exports-moe terminated 13:20Z; ~$26.7 of $30
artifacts: no input sets (no row reached a written export); run records: art:9d0ba26d art:5eeec31f art:1db9d8db art:8180df8f art:ee5b4ac0 art:7eb9063c art:4ba50829 art:238aab21
~~~

Run records, all preserved:
- #74: `r20260926-081920-036d` = art:9d0ba26d (Build, and `programs/`: its 9 request Programs); `r20260926-101428-71e2` = art:5eeec31f (Match PASS at the 32 MiB cap; unbounded Commit stopped at the memory cap); `r20260926-115930-46a1` = art:1db9d8db (bounded/exclude Commit, finalize crash).
- #67: `r20260926-082002-43e0` = art:8180df8f (Build, Match, Commit through the replay; `programs/` holds its 33 request Programs, and `evidence/` the Commit logs).
- Bootstraps: art:ee5b4ac0 (H100), art:7eb9063c (L40S).
- Pod tests at `898c32ef`: art:4ba50829 (148 pass, 1 skip), art:238aab21 (22 pass).

No captured input sets came out of this lane.
- **#57 Gemma** was skipped. It's FAIL-class, and its distinct templates have no evaluator.
- **#74** needs an H100 host with at least 320 GB RAM running the unbounded Commit (and the Match at the 32 MiB cap), or the `--bounded-staging --retain-exclude` finalize fixed.
- **#67** needs a re-run whose export budget starts after the population build, or `max_seconds` of about 2400 s through `limits.json`. Either way it's a whole row run: about 5 h on 2x L40S, roughly $11.
- **Delivered:** the exporter support both rows need (PR #63: FP8 block and MoE expert coordinates, which main silently drops), the FP8 chain-set deriver (`evidence/derive_fp8_chain_sets.py`), and the memory and budget findings, all handed to their owners.

## Reopened 13:45Z: #67 export re-run with PR #80 + PR #63. Blocked on L40S capacity, stopped 14:25Z

- **Tree:** `cursor/vllm-67-rerun-0df4` @ `8f2f1624`, which is #63 (`898c32ef`) merged with #80 (`30c7a28a`), pushed. vllm-vu-export reviewed #63 as OK and ran 76 tests on it (`r20260926-133827-b804`; its handoff `20260926T1344Z-handoff-from-vllm-vu-export.md`). Neither PR is merged yet.
- **Plan: Commit only over #67's restored Build**, skipping Build and Match (about 2.5 h). The Build dir is rebuilt on the pod from the preserved run art:8180df8f:
  - `programs/`, the 33 request dirs;
  - `evidence/build_summary.json`;
  - a restored `build_workload/workload_program.json` carrying workload digest `7b79c784…`.
  - Then `STAGES=commit PROGRAM_DIGEST=7b79c784… verity-vllm row run`. The row driver builds the manifest of record and the weights of record itself. With no Match dir the live oracle compare isn't armed, which is a logged warning; the export doesn't need it.
  - Expected wall time on a pod of 233 GB or more: bootstrap about 12 min, manifest about 15 min, Commit and sampled replay about 100 min, export about 30 min, so about 2.7 h.
- **What happened:**
  - Secure L40S / L40 / RTX 6000 Ada with 200 GB or more: no stock (RunPod `stock=None`).
  - Two community L40S pods (251 GB, $0.79/h) were created: `vyv-more-exports-moe2` (`b83fk4drgx340u`) and `vyv-more-exports-moe3` (`xox1xhelqizkw8`). On both, CUDA can't initialise: the image's own torch cu124 fails with "CUDA unknown error", nvidia-smi reports "Addressing Mode: Unknown Error", driver 550.163.
  - The cuda-compat-12-9 forward-compat libraries didn't help. Bootstraps `r20260926-134954-df82` and `r20260926-142055-a825` fail with `BOOTSTRAP_FAIL_CUDA`.
  - Uploading the restored Build over ssh took 14 min (about 0.5 MB/s) to the community host. Next time, fetch it from R2 on the pod with a minted read-only key instead.
- **Stopped at 14:25Z.** A working L40S would still need about 3 h, which lands past the 16:45Z guard; the 17:45Z extension I asked for (1417Z) wasn't answered. Both pods were terminated with nothing on them to preserve. The reopen cost about $0.3 ($0.79/h × about 0.4 h).
- **To finish #67 later:** a secure L40S with 233 GB or more (1x with at least 240 GB, or 2x at 120 GB each), the tree above, the restore recipe above, and about 2.7 h. Then register with `evidence/register_export.py <run> pre-epoch cursor/vllm-67-rerun-0df4 <row key> 67` and send the export and store art ids to vllm-vu-export.

**FINAL (reopen, 14:25Z):** no new artifacts. The ready-made tree is `cursor/vllm-67-rerun-0df4` @ `8f2f1624` (#63 + #80), pushed, with no PR of its own; the two PRs carry the changes. Pods `vyv-more-exports-moe2` and `-moe3` were terminated at 14:16Z and 14:23Z, about $0.3. The lane total is about $27.0 across both windows.
