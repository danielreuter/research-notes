---
lane: vllm-57-fix
kind: report
created: 2026-09-24T07:50Z
status: final
---

CHECKPOINT f16703a2 (13:11Z) [final] Lane complete. #57 PASS at f16703a2 (verdict art:bad7b21c) + #67 PASS at f16703a2 (r20260924-102613-0196, verdict art:51826b81), both preserved; vyv-sw-67b drained. Integrator: take f16703a2
CHECKPOINT f16703a2 (12:08Z) [open] CHECKPOINT 67-pass AT-RISK 12:10Z revised: each #67 Commit pair ~41 min (replay serial prep ~28 min, no cross-pair reuse). Verdict ~12:52Z, preserved + drained ~13:00Z. Clean so far
CHECKPOINT f16703a2 (11:53Z) [open] CHECKPOINT 67-pass AT-RISK 11:55Z: #67 Commit pairs 1-2 re-run the ~25 min sampled replay (cache key differs in binding_map_sha256). Clean so far; verdict ~12:35Z, preserved + drained ~12:45Z
CHECKPOINT f16703a2 (11:40Z) [open] #57 Commit PASS on merged tree f16703a2 (r20260924-103124-47d5, verdict art:bad7b21c preserved). #67 Commit r20260924-102613-0196 pair 0 clean (replay 38,748/38,748), verdict ETA ~12:05Z
CHECKPOINT f16703a2 (10:27Z) [open] 67-pass AT-RISK: staging 2c8aa2b3 broke v2 Commit (stale verity_capture imports from relayout); fixed f16703a2 (pushed, integrator handoff). #67 Commit r20260924-102613-0196 @f16703a2 ETA ~12:05Z
CHECKPOINT 2c5e038b (10:00Z) [open] #57 Commit also PASS on retire-v1 trial merge 25170f24 (verdict art:6b939117, preserved); integrator note updated. #67 Commit r20260924-085702-d2e3 pair 0 in sampled replay, ETA ~10:45Z
CHECKPOINT 2c5e038b (08:59Z) [open] #67 Match PASS art:f95c7d60; #67 Commit r20260924-085702-d2e3 @2c5e038b running (ETA ~10:40Z). #57 Commit on retire-v1 trial merge 25170f24 r20260924-085749-2570 running (ETA ~09:50Z)
CHECKPOINT 2c5e038b (08:56Z) [open] 57-pass MET 08:49Z: #57 Commit PASS @2c5e038b r20260924-075409-3621 verdict art:b99af6c6 (preserved+labelled). 57-ready MET 08:58Z (integrator note; asks #57 rerun on merged tree vs retire-v1). #67 Match running
CHECKPOINT 2c5e038b (08:38Z) [open] #57 @2c5e038b pairs 0,1 clean (oracle 159,840 equal, replay 5,883/5,883, linkage 432/432); pair 2 -> verdict ~08:45Z. #67: population reconciles at tip (0 identities_without_rows, was 20,928); Match running
CHECKPOINT 2c5e038b (08:12Z) [open] #57 rerun @2c5e038b: C2 oracle compare 159,840/159,840 equal, 0 mismatch (was 432); local_replay+verdict pending. Trial onto retire-v1 9d80e302 clean, tests 237 pass/0 fail. #67 Match running
CHECKPOINT 2c5e038b (08:01Z) [open] #57 Commit r20260924-075409-3621 @2c5e038b running (ETA ~09:00Z); #67 Build PASS art:5b7e5bcf, Match r20260924-075730-80bd running; 2c5e tests green (3 watchdog fails = ninja not on PATH); laptop disk at guardian floor, handed to coordinator
CHECKPOINT 2c5e038b (07:50Z) [open] successor took over 07:50Z; 2c5e038b on origin+sw57, #57 rerun at it not yet launched; #67 Build r20260924-063717-5860 PASS 07:42Z; next: launch #57 Commit at 2c5e038b + #67 Match

## Final (13:11Z)
- **Cause (#57):** two v2 gaps.
  1. The sweep's replay addressed Program rows by the v1 rule. Staging `38122d1f` already fixes that; it's also what #67's 20,928 `identities_without_rows` were.
  2. A `v2-query` manifest carries no producer annotations. So form (B) couldn't pick among a fused norm's two narrowings, and Commit hooked `model`'s forward return instead of the embed scale its body hands to `model.layers.0` (432 `model/out` mismatches).
- **Fixes:**
  - `4f6f6d1d`: form (B) derives producer facts from the Programs of record by dataflow.
  - `8b606f16`: row_pod takes all snapshot steps when form (B) needs them.
  - `2c5e038b`: values a module body hands down are marked promoted and observed at their first consumer's input.
  - `f16703a2`: staging `2c8aa2b3` (merged with the relayout) kept 5 stale function-local imports and crashed every v2 Commit. This commit repoints them and adds `tests/test_imports_resolve.py`.
- **#57:** Commit PASS at `2c5e038b` (verdict `art:b99af6c6`), on the retire-v1 trial merge (`art:6b939117`), and on the merged tree `f16703a2` (`r20260924-103124-47d5`, `art:bad7b21c`). All 3/3 runs, every check PASS.
- **#67:** Commit PASS at `f16703a2` (`r20260924-102613-0196`, `art:51826b81`), 3/3 runs, replay 38,748/38,748 ×3. The earlier run at `2c5e038b` failed on MoeSum replay (fixed by retire-v1 `6813fe06`). 67-pass was met at 13:10Z, 40 min late, with AT-RISK posted ahead of the deadline.
- **Pods:** vyv-sw-67b drained and terminated. vyv-sw-57 is still up, idle, and hosts the integrator.
- **Open for the integrator:**
  - Take `f16703a2`.
  - On FA2-tap rows, the replay-cache key misses every pair because the binding map carries cumulative `fa2_tap_bounded` counters. It's fail-safe and costs about 55 min per OLMoE Commit.
