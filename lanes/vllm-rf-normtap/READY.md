---
id: vllm-rf-normtap/ready
lane: vllm-rf-normtap
kind: ready
created: 2026-09-26T22:19Z
updated: 2026-09-27T00:34Z
---
# vllm-rf-normtap READY (2): the guarded-max tap, opt-in behind GUARDED_MAX_TAP

Branch `cursor/vllm-rf-guarded-max-57d5` @ `a43ed3b9`, base main `35e78c37`, [PR #95](https://github.com/danielreuter/verity/pull/95)
(draft).  Merge-ready handoff: `lanes/vllm-coordinator/20260927T0030Z-handoff-from-vllm-rf-normtap.md`.  Finding, sent first:
`lanes/vllm-coordinator/20260926T2329Z-handoff-from-vllm-rf-normtap.md`.

## Change
- The FA2 / FA3 tap builds with `VERITY_ROW_GUARD=1` (`pod_fa2_tap.sh FA2_TAP_ROW_GUARD=1`, `pod_fa3_tap.sh FA3_TAP_ROW_GUARD=1`) write
  `GuardNegInfZero(row_max)` into ROW word 3 at every key block after a row's first, and 0 at the first.
- The policy lives in the manifest's query header (`query/guarded_max.py`); the identities and manifest digest stay the record's.  The
  Commit refuses a tap build whose word 3 does not match the manifest.
- Off by default: the default builds' kernels and the stream bytes are unchanged.

## Results (all runs PRESERVED on R2)
| check | run | result |
|---|---|---|
| FA2 exactness, L40S (softcap incl.) | `r20260926-232759-8412` | default `1d5484b9` OK; guarded `d18f3f62` OK: 64/64, 12/12 negatives, 423,438 guard words |
| FA3 exactness, H100 | `r20260926-232600-e66f` | default `635dcd3d` OK; guarded `5c83bcfe` OK: 20/20, 10/10 negatives, 40,122 guard words |
| #101 tap off | `r20260926-232328-7713` | Build/Match/Commit PASS; Program, manifest and run root = record |
| #101 tap on | `r20260926-232328-7713` | Commit PASS, root `ae21ed2e…`; policy 97,280 guard words = the tap list |
| #101 committed bytes | `r20260927-000857-9e96` | step 0: 4,096 guard words, step 1: 64, all = IR guard; root reproduced; ROW word 2 = visit index |
| partition checker (trial merge) | `r20260926-232341-8c37` | #101 attention: 0 violations, 0 recomputes; 97,280 guards -> ROW word 3; softcap and FA3 clean |
| gate (b) base `35e78c37` / head `a43ed3b9` | `881f` / `f468` | lints rc 0; 31 / 32 F; +13 tests pass; the one new failure is a timing race (5/5 pass on both sides, `32fe`) |

## Found, not fixed
- `max * scale` (242,688 words on #101) is committed by the cut and carried by nothing: ROW word 2 is the visit index.
- TP rows and the H100 rows (FA3 at kernel level only) are not covered.

## Pods, spend
The H100 `hzvx9w6liqxmc4` ran ~22:52Z-23:27:44Z, and the L40S `wqd4c5luh2x8ig` 23:18Z-00:32:08Z.  Two community L40S (driver 550, no CUDA
for torch cu129) were terminated after ~22 and ~2 min.  Spend was about $3.73 of $12.

---
# vllm-rf-normtap READY (1): norm-scale taps (PR #90, merged into main 35e78c37)

Branch `cursor/vllm-rf-normtap-57d5` @ `14ea93c6`.  Handoff `lanes/vllm-coordinator/20260926T2219Z-handoff-from-vllm-rf-normtap.md`.
- Exactness `abcd3320`: 62/62 kernel cases plus the source check.
- #101 tap off = record; tap on: 9,471 norm-scale words = plan.
- Partition checker norms 19/19, 0 recomputed.
- Gate (b) jdiff rc 0.
- Pod `yqvagba5ef4ckg` 20:28Z-22:17:54Z, about $2.00.
