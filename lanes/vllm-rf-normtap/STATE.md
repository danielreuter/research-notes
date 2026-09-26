# vllm-rf-normtap: STATE

Lane reopened 22:39Z for the guarded-max tap (handoff `internal/lanes/vllm-rf-normtap/20260926T2245Z-handoff-from-vllm-coordinator.md`;
estimate approved 22:29Z, cap $12, vyv- guard deadline 02:30Z). Agent bc-12c2f2d9 (cloud). The norm-scale taps (PR #90) are merged
(main 35e78c37); their record is below the line.

## Guarded-max tap (branch cursor/vllm-rf-guarded-max-57d5, from main 35e78c37)
- Head `efb2bd4a` (5425de64 kernels + builds, ef734866 host side + property, efb2bd4a property rule fix).
- Kernel: FA2 `verity_tap.h` / FA3 `verity_tap_fa3.h` `rowstat`: under `VERITY_ROW_GUARD=1`, ROW word 3 = `row_max != -inf ? row_max : 0`
  at step > 0 (every key block after the row's first in the kernel's visit order), 0 at step 0.  Default builds never write word 3.
  `verity_tap_row3()` op (0 / 1).  `pod_fa2_tap.sh FA2_TAP_ROW_GUARD=1` -> `build/matReqG/verity_fa2_matReqG.so`;
  `pod_fa3_tap.sh FA3_TAP_ROW_GUARD=1` -> `build/fa3_matReqG/verity_fa3_matReqG.so`.
- Host: `query/guarded_max.py` (attention_words = NH x (ceil(T/BN) - 1) per attention Call; the policy is a query-header statement,
  identities and manifest digest stay the record's), `manifest build --guarded-max`, manifest-verify compares the policy,
  `hidden_source.require_row3` via `make_hidden_source(manifest=...)` (commit.py passes the required manifest), CommitConfig
  `GUARDED_MAX_TAP` (default 0), RunEnv `hidden_so_fa2_guarded` / `hidden_so_fa3_guarded`, row_stages moves aside a manifest whose policy
  differs from the flag.
- Property: `fa_tap_exactness` (e): guarded build vs the default build's record (`--baseline`): masked stream digest, `check_row3`
  (IR GuardNegInfZero_v1 of the entry's row_max at blocks after the first, 0 at the first; twin on all, IR reference on a sample incl.
  specials), ROW word 3 in the closedness mask; edge cases with -inf / +inf / NaN rows (FA2 softcap too).

## Pods
- vyv-rf-normtap-h1 hzvx9w6liqxmc4 (H100 80GB HBM3, $3.49/h) ~22:52Z-23:27:44Z: setup 54e0, FA3 exactness db4a (rule bug) and e66f (OK). Terminated.
- vyv-rf-normtap-g2 gbyqr7veo5qdlw and -g3 mx5580q5a2j5xe (L40S community, $0.79/h): driver 550.163 (CUDA 12.4), torch cu129 sees no CUDA.
  Terminated after ~21 and ~2 min.
- vyv-rf-normtap-g4 wqd4c5luh2x8ig (L40S secure, driver 580.126, $1.09/h) since 23:19Z, guard 90.

## Running (L40S g4)
- r20260926-232004-ee99: bootstrap + FA2 default/guarded builds + FA2 exactness at ef734866 (its single-block guarded cases hit the rule bug).
- r20260926-232328-7713: #101 tap off (Build/Match/Commit = record?) and on (Commit, VERITY_DUMP_STEP=0 L0 ROW word 3 check). After ee99.
- r20260926-232341-8c37: partition checker on a LOCAL trial merge a3d4ec46 (tree 678f436c) of no-recompute 194ac3f9 + ef734866. After 7713.
- r20260926-232633-881f: gate (b) base 35e78c37 (gate_b3.sh XDIST_ONLY=1 NO_GPU=1). After ee99.
- r20260926-232759-8412: FA2 exactness rerun at efb2bd4a. After 7713.
- Next: gate (b) head at the final commit (same pod, same switches), jdiff; handoff; READY; PR; FINAL.

## Results
- FA3 (H100, r20260926-232600-e66f, efb2bd4a): default record 635dcd3d OK (20 cases, 10 negatives); guarded record 5c83bcfe OK: 20/20 cases,
  10/10 negatives, 40,122 guard words = GuardNegInfZero(row_max), first blocks 0, IR sample agrees, every other stream word = default's.

## Found, not fixed
- **max * scale is not in the stream.** The no-recompute cut commits `max_scaled = F32MulFtz(m_use, scale)` in every block (read by all the
  block's exp2 units), and the plan's §3 and the no-recompute branch's `committed_today` map it to "ROW step", but ROW word 2 is the kernel's
  visit index (`dst[2] = __int_as_float(vt_step)`).  So even with the guarded max the attention cut has one uncommitted value per
  (head, block, row).  To confirm with the checker (8c37) and report to the coordinator.
- The sampler (GumbelTopPTokenSelect_v1) recompute and Gemma's chain Calls (from the norm-scale lane) still stand.

---
## Norm-scale taps (PR #90, merged 35e78c37): FINAL 22:22Z; handoff 20260926T2219Z; exactness abcd3320; #101 off = record, on 9,471
words; partition checker norms 19/19, 0 recomputed; gate (b) jdiff rc 0; pod yqvagba5ef4ckg terminated 22:17:54Z, ~$2.00.
