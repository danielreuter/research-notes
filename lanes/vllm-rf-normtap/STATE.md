# vllm-rf-normtap: STATE

Lane: norm-scale taps (Daniel's approval Sep 26 19:33Z); brief `$STORE/internal/lane-briefs/vllm-normtap.md`. Agent bc-12c2f2d9 (cloud).
Branch `cursor/vllm-rf-normtap-57d5` (the Cursor branch policy; common-rules fallback form), cut from origin/main `baa800c6`; PR #90 (draft).
Head `14ea93c6`. Base for gate (b): `baa800c6`. origin/main is now `56c62af2` (2 commits, no file in common).

## What is built (commits 9a9c7548..14ea93c6)
- `query/norm_scales.py`: family `norm_scales` (not `norm_scale`: that name is by-name vocabulary in `FAMILIES`), member
  `norm_scale`, one f32 per norm Call row. Kernel norms (RMSNormTriton_v1, RMSNormFusedCuda_v2): one identity per (step, module).
  Gemma's ATen chain: RsqrtF32_v1{N=1} outputs protocol-required. `request_manifest(norm_scales=POLICY)`; off = byte-identical.
- CUDA tap: `acquire/norm_tap_src/build_ext.py` (verity-vllm norm-tap-build) cuts the pinned generic kernel (sha-pinned) and adds
  a `Tap` template parameter; `norm_tap.cu` launches it as the installed op does under batch invariance. `ops/pod_norm_tap.sh`.
- Triton tap: `acquire/norm_tap_src/rms_norm_tap.py` = pinned `_rms_norm_kernel` + 2 lines.
- Source: `acquire/sources/norm_scale_source.py` (engine.hooks patches, module-scoped). Flag: `CommitConfig.norm_tap` (NORM_TAP,
  default 0) -> manifest --norm-scales, commit_delta --norm-tap-so, manifest-verify --norm-scales.
- Q_word: `check_calls(acquired=TAP_WORDS)`; plan route `norm_tap`; replay mechanism entry; form (B) no-oracle by member.
- Property: `properties/norm_tap_exactness.py` + GPU driver `tests/properties/norm_tap_exactness_gpu.py`.
- 14ea93c6: `tests/census_roots.txt` declares `pod_norm_tap.sh` and `verity_vllm.properties.norm_tap_exactness` (gate (b) at 75a10410
  failed `test_no_new_dead_modules` on the property module, as fa_tap_exactness would without its roots entry).

## Running
- Nothing. Pod vyv-rf-normtap-g1 (yqvagba5ef4ckg, 1x L40S, $1.09/h) created 20:28Z, terminated 22:17:54Z after all 7 runs were
  PRESERVED. Spend about $2.00 (1.83 h); no CPU pod.

## Results
- r20260926-203003-9768: bootstrap OK; tap build OK, NORM-TAP-OK sha256 e4a4924f.
- r20260926-204311-f524: NORM-TAP-EXACTNESS OK, record digest abcd33208a41...d439: 62 kernel cases (32 CUDA, 30 Triton) + source check.
  Every case: output == installed kernel, 0 unwritten rows, 0 scales != twin, 0 != IR model; CUDA == untapped build; Triton == vLLM's
  launch, PTX arithmetic equal (73 ops; 57 without weight) + exactly 1 extra global store.
- #101 tap off (Build/Match/Commit PASS): Program ccc213475e7c...00c6b, manifest 90f81868...eaac, run root 7adcef49...1dec5 = record.
- #101 tap on (Commit PASS): manifest cfc7e16b...f572, 8,099 identities (+1,056 norm_scales), 9,471 words (fused 9,184 + Triton 287)
  = plan's 9,471; run root 9c89049c...3b26 (never the record). Q_word_v1{16,32} strict: 9,471 acquired by a tap, passes.
- Gate (b) base baa800c6 (r...78c0): 37 failed / 3,908 passed / 263 skipped. Head 75a10410 (r...3f50): 38 / 3,952 / 264; jdiff: 46 new
  tests all pass; 1 new failure (test_no_new_dead_modules, fixed in 14ea93c6); the 1 new skip is the listed order-dependent test.
- Gate (b) head 14ea93c6 (r20260926-214754-14b1): lints rc 0; 37 F / 3,954 P / 263 S / 6 xf; jdiff vs base rc 0 (46 new tests
  pass, 0 outcome changes, 0 new failures, 0 new skips). `evidence/gate-b/`.
- Partition checker (r20260926-220038-b8d6; the 20:48Z rule), on a LOCAL trial merge `23067146` (never pushed) of
  cursor/no-recompute-partition-289b fd9f81e8 + 14ea93c6, Q_word_v1{X=16,W=32,R=no-recompute}: 19/19 norm specializations OK
  (cut OK, width OK, 0 recomputed gates, 1 committed interior word per row = the tapped scale). #101 under the policy: norm groups
  9,471 Calls, 38,214,911 units, 9,471 committed interior words, all acquired, 0 violations; whole #101: 46,558 Calls, 273,995,039
  units, 64,169,215 committed interior words, one violation outside the norms (GumbelTopPTokenSelect_v1 gate-recomputed, 32 Calls,
  same with the policy off). Merged-tree tests 177 passed, lints rc 0. `evidence/partition/`.
- Custody: all 7 runs (9768, d287, f524, 78c0, 3f50, 14b1, b8d6) PRESERVED on R2.

## Next
- Done: merge-ready handoff `lanes/vllm-coordinator/20260926T2219Z-handoff-from-vllm-rf-normtap.md`, READY.md, PR #90 updated, FINAL.

## Open questions
- None blocking. The family is `norm_scales` (the brief said "for example `norm_scale`").

## Found, not fixed
- No RunPod CPU stock at 20:52Z (cpu3g/3c/3m/5c/5g/5m at 8/16/32 vCPU): gate (b) runs on the L40S pod (base and head same pod).
- Gemma (#57): Q_word's committed-boundary check partitions per Call, so the chain's interior Calls (square, mean, + eps) stay
  `output-not-committed` with or without the scale; #57 has no passing Commit.
- TP rows (rank workers) and H100 (FA3 rows) are not covered: the tap is attached by commit_delta only; exactness is on sm_89 only.
- The partition checker (no-recompute rule) lives on cursor/no-recompute-partition-289b, not main; its `word.py` and this branch's
  merge without conflict (this branch touches only `check_calls` / `check_query`).
- Under the no-recompute rule the sampler `GumbelTopPTokenSelect_v1{V=128256}` recomputes a gate: a strict `--word-check 16/32` on #101
  fails on it once that branch merges, tap on or off.
