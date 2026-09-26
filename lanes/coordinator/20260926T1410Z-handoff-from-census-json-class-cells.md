---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
---

# census-json: class-pin attention cells are credited per listed key count. Merge request (PR #79), time-critical

**To:** research coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628).

## Merge request
- **PR:** [PR #79](https://github.com/danielreuter/verity/pull/79), `cursor/attention-class-cells-574a` into `main`, on top of `c20bab70`.
- **Tests:** `backends/numerical` passes (981). CPU only.
- **Byte identity:** without class cells, the tables, raw JSON, markdown and parity are byte-identical.

## What it does
- **Shape read** (`ir_bench` on flock-ir-lowering, 4eb3b991):
  - fingerprint `key_counts` `{T: heads}`;
  - fingerprint `key_class` `{T: [lo, hi], pin}`;
  - result `per_key_count` `{T: {heads, e2e_s, ...}}`.
- **What is credited:** each T listed in `key_counts` that is inside the class and has a positive `heads` and `e2e_s` in `per_key_count`.
  - It is credited at P = heads / e2e_s, with native N per T.
  - Every other listed T shows up as `not_credited` with a reason.
  - An unlisted T is never credited.
  - A cell with nothing creditable is rejected X.
- **Table 2:** each class gets its own row, with N work-weighted over the cell's credited T.
- **Headline:** it takes the fastest single-T or class cell per T. The † footnote stays, and its ruling now cites both grants (20260926T1115Z and 20260926T1340Z, CP7).

## Please check
- **The shape:** neither `20260926T1340Z-handoff-from-red-team-flock-3.md` nor `lanes/red-team-flock-3/evidence/` had synced to my VM, so I could not read CP7 or the evidence scripts.
  - If the class results put `per_key_count` somewhere other than the result document (or the fingerprint), or key it differently, tell me and I'll adapt.
  - The same applies if CP7 asks for something the headline must show.
- **After merge:** render once class cells land from about 14:15Z. The class rows should read `· T = 1–128` (and so on) on the L40S line, and #101's attention line should list the credited T.
