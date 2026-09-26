---
id: vllm-rf-normtap/ready
lane: vllm-rf-normtap
kind: ready
created: 2026-09-26T22:19Z
updated: 2026-09-26T22:19Z
---
# vllm-rf-normtap READY: norm-scale taps, opt-in behind NORM_TAP

Branch `cursor/vllm-rf-normtap-57d5` @ `14ea93c6`, base `baa800c6`, [PR #90](https://github.com/danielreuter/verity/pull/90) (draft).
It merges cleanly into origin/main `56c62af2` and into `cursor/no-recompute-partition-289b` `fd9f81e8`. Merge-ready handoff:
`lanes/vllm-coordinator/20260926T2219Z-handoff-from-vllm-rf-normtap.md`.

## Change
One committed f32 scale per norm Call per token row, family `norm_scales` (`<norm module>/norm_scale`):
- the fused CUDA norm through a separately built op (the pinned generic kernel plus one store);
- the Triton norm through a patched copy (the pinned kernel plus two lines);
- Gemma's `RsqrtF32_v1{N=1}` output made protocol-required.

It is off by default (`NORM_TAP=0`), and off is byte-identical.

## Results (L40S, all runs PRESERVED on R2)
| check | run | result |
|---|---|---|
| exactness (record `abcd3320…d439`) | `r20260926-204311-f524` | OK: 62/62 kernel cases (32 CUDA, 30 Triton) plus the source check |
| #101 tap off | `r20260926-204311-f524` | Build/Match/Commit PASS; Program, manifest and run root = record |
| #101 tap on | `r20260926-204311-f524` | Commit PASS; 9,471 norm-scale words = plan; new run root `9c89049c…` |
| partition checker (no-recompute, trial merge) | `r20260926-220038-b8d6` | 19/19 norm specializations OK, 0 recomputed gates, 1 committed word per row = the tapped scale; #101 norm groups 9,471/9,471 acquired, 0 violations |
| gate (b) base `baa800c6` | `r20260926-205346-78c0` | lints rc 0; 37 F / 3,908 P / 263 S / 6 xf |
| gate (b) head `14ea93c6` | `r20260926-214754-14b1` | lints rc 0; 37 F / 3,954 P / 263 S / 6 xf; jdiff rc 0 (46 new, all pass) |

Evidence: `evidence/partition/`, `evidence/gate-b/`, `evidence/pod-scripts/`.

## Found, not fixed
- The sampler (`GumbelTopPTokenSelect_v1`) recomputes a gate under the no-recompute rule, tap on or off.
- Gemma's chain has interior Calls that are not committed at the Call level.
- TP and H100 rows are not covered.
- There was no CPU stock, so gate (b) ran on the L40S pod.

## Pods, spend
`vyv-rf-normtap-g1` (`yqvagba5ef4ckg`, 1× L40S, $1.09/h) was created at 20:28Z and terminated at 22:17:54Z after every run was
preserved. Spend was about $2.00 of the $10; there was no CPU pod.
