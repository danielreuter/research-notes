# vllm-rf-normtap: STATE

Lane: norm-scale taps (Daniel's approval Sep 26 19:33Z); brief `$STORE/internal/lane-briefs/vllm-normtap.md`. Agent bc-12c2f2d9 (cloud).
Branch `cursor/vllm-rf-normtap-57d5` (the Cursor branch policy; common-rules fallback form), cut from origin/main `baa800c6`.
Head `75a10410`. Base for gate (b): `baa800c6`.

## What is built (commits 9a9c7548..75a10410)
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

## Running (pod vyv-rf-normtap-g1 = yqvagba5ef4ckg, 1x L40S, $1.09/h, created 20:28Z, guard 90)
- r20260926-204311-f524: exactness rerun (OK, digest abcd3320) + #101 tap off (Build/Match PASS) -> Commit; then tap on; Q_word.
- r20260926-205346-78c0: gate (b) base baa800c6 (waits for f524; CPU bootstrap pins).
- r20260926-205426-3f50: gate (b) head 75a10410 (waits for base).

## Results so far
- r20260926-203003-9768: bootstrap OK; tap build OK, NORM-TAP-OK sha256 e4a4924f.
- r20260926-204005-d287: 61/61 kernel cases OK; source check harness bug (custom ops off) fixed in 846a3eb3.
- r20260926-204311-f524: NORM-TAP-EXACTNESS OK (61 cases + source check).
- #101 off: Build manifest 90f81868 (= record, 7,043 identities), Match PASS.

## Next
- #101: off root == record 7adcef49?; on: PASS?, norm_scales words vs 9,471; Q_word with acquired.
- gate (b) jdiff base vs head; lints at head.
- handoff to vllm-coordinator, READY.md, terminate pod, FINAL.

## Open questions
- None blocking. The family is `norm_scales` (the brief said "for example `norm_scale`").

## Found, not fixed
- No RunPod CPU stock at 20:52Z (cpu3g/3c/3m/5c/5g/5m at 8/16/32 vCPU): gate (b) runs on the L40S pod (base and head same pod).
- Gemma (#57): Q_word's committed-boundary check partitions per Call, so the chain's interior Calls (square, mean, + eps) stay
  `output-not-committed` with or without the scale; #57 has no passing Commit.
- TP rows (rank workers) and H100 (FA3 rows) are not covered: the tap is attached by commit_delta only; exactness is on sm_89 only.
