# vllm-rf-normtap: STATE

Agent bc-12c2f2d9 (cloud).  Norm-scale taps (PR #90) and the guarded max (PR #95) are merged (main 84801045).  The MS class (PR #102) is
merge-ready.  Next: FA3 `Check_inf` per iteration in the IR (handoff `internal/lanes/vllm-rf-normtap/20260927T0200Z-handoff-from-vllm-coordinator.md`),
CPU first; an estimate before any H100 (root approves).

## FA3 Check_inf per iteration (follow-up to #102): STARTING (CPU)
- The fix: a new FA3 block Definition with a per-iteration `CHECK` static (true on the first block and on the causal-masked iterations,
  false on the unmasked ones) that mirrors `max_get_scale` / `fwd_step` for both the max it uses and the rescale; the head derives each
  block's class from the launch geometry (the kernel's `n_block_min_causal_local_mask`).  Opt-in construction selector, default the
  current `AttnBlock_v2` chain; with it off no digest moves.  The re-baseline switch is root's.
- Acceptance: CPU tests; partition checker 0 recomputes, units <= 32 bits; FA3 exactness: every MS word and output = the new IR,
  edge rows included (H100 ~30 min, ~$2, after root approves the estimate).

## MS class (branch cursor/vllm-rf-ms-plane-57d5, from main 84801045): DONE, merge-ready (PR #102, draft)
- Head `40ec2e13` (67516cfa kernels + builds, 06485b76 host + property + tests, 40ec2e13 the X-03 policy record with the flag off).
- Handoffs: finding 20260927T0152Z (FA3 IR Check_inf), merge-ready 20260927T0228Z.  READY.md (3).
- Coordinator handoffs for this task: 0015Z (superseded by 0030Z), 0020Z (GO, $10, guard 04:15Z), 0030Z (the MS design), 0135Z (terminate the
  H100 after FA3 exactness), 0200Z (FA3 record accepted on ms_mismatch_neg_inf_max; the follow-up).
- Results: FA2 955c OK (547,438 MS words = IR); FA3 34ba default OK, guarded ok:false from 40 MS words with row_max -inf only; #101 0f64 off =
  record (root 7adcef49, manifest 90f81868 = base main's), on root fa38d70b, 242,688 max_scaled words, committed MS = IR; partition 2c04
  0 violations / 0 recomputes, checker = policy = strict word check; gate (b) 1737 / 9dbf jdiff rc 0.
- Pods: vyv-rf-normtap-h2 rl550thlwam3ui (H100, $3.49/h) 01:26Z-01:46:13Z; vyv-rf-normtap-g5 kt6i7m2zu3jy61 (L40S secure, $1.09/h)
  01:26Z-02:25:59Z.  Both terminated, every run preserved.  Spend about $2.27 of $10.

## Guarded-max tap (branch cursor/vllm-rf-guarded-max-57d5, from main 35e78c37): MERGED (PR #95, main 84801045)
- Head `a43ed3b9` (5425de64 kernels + builds, ef734866 host side + property, efb2bd4a property rule fix, a43ed3b9 the Commit's dump fix).
- Handoffs: finding 20260926T2329Z (max * scale not carried), merge-ready 20260927T0030Z.  READY.md updated.
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
- vyv-rf-normtap-g4 wqd4c5luh2x8ig (L40S secure, driver 580.126, $1.09/h) 23:18Z-00:32:08Z.  Terminated after every run was preserved.
- Spend about $3.73 of $12 (H100 $2.07, community L40S $0.31, L40S $1.35).

## Running
- Nothing.  All runs PRESERVED (incl. r20260926-225442-c5cb, the community pod's setup, preserved by the pod before it was terminated).

## Results
- FA3 (H100, r20260926-232600-e66f, efb2bd4a): default record 635dcd3d OK (20 cases, 10 negatives); guarded record 5c83bcfe OK: 20/20 cases,
  10/10 negatives, 40,122 guard words = GuardNegInfZero(row_max), first blocks 0, IR sample agrees, every other stream word = default's.
- FA2 (L40S, r20260926-232759-8412, efb2bd4a): default 1d5484b9 OK (64 cases, 12 negatives); guarded d18f3f62 OK: 64/64, 12/12, 423,438 guard
  words (28 softcap cases, 8 edge cases with 2,808 guard words).
- #101 (r20260926-232328-7713): off: Build/Match/Commit PASS, Program ccc21347, manifest 90f81868, root 7adcef49 = record.  On: Commit PASS,
  root ae21ed2e, manifest identities = record, header guarded_max.words 97,280; manifest_verify OK with the policy on both sides.
- #101 committed bytes (r20260927-000857-9e96, --tensor-digests + VERITY_DUMP_STEP 0 / 1): root ae21ed2e reproduced twice; L0 step 0 4,096 guard
  words, step 1 64, 0 mismatches, first blocks 0, IR sample agrees; ROW word 2 = the visit index.
- Partition checker (r20260926-232341-8c37, trial merge a3d4ec46 / tree 678f436c): #101 attention 4,592 Calls, 287 specializations, 0 violations,
  0 recomputes; GuardNegInfZero 97,280 -> ROW word 3 (= policy), F32MulFtz 242,688 not carried; softcap / FA3 Definitions and head cuts clean;
  #101 whole Program ok (0 violations); merged-tree tests 165 passed, lints rc 0.
- Gate (b): base 35e78c37 (881f) 31 F / 3,913 P / 286 S; head a43ed3b9 (f468) 32 F / 3,925 P / 286 S; jdiff: +13 pass, 1 new failure
  test_fork_pool (ProcessLookupError race in the test's /proc read), 5/5 pass on base and head in r20260927-002905-32fe.

## Found, not fixed
- **max * scale is not in the stream** (confirmed: 242,688 committed words on #101, checker 8c37; ROW word 2 = visit index in the committed
  bytes, 9e96).  The no-recompute cut commits `max_scaled = F32MulFtz(m_use, scale)` in every block with more than one visible key; the
  plan's §3 and the no-recompute branch's `committed_today` map it to "ROW step".  Reported (20260926T2329Z); the coordinator decides.
- The sampler (GumbelTopPTokenSelect_v1) recompute and Gemma's chain Calls (from the norm-scale lane) still stand.

---
## Norm-scale taps (PR #90, merged 35e78c37): FINAL 22:22Z; handoff 20260926T2219Z; exactness abcd3320; #101 off = record, on 9,471
words; partition checker norms 19/19, 0 recomputed; gate (b) jdiff rc 0; pod yqvagba5ef4ckg terminated 22:17:54Z, ~$2.00.
