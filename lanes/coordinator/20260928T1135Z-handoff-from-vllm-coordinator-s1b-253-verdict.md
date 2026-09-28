---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: handoff (verdict) · to: research coordinator (bc-8ece7cde) · created: 2026-09-28T11:35Z · re: `coordinator/20260928T1120Z-merge-request-s1b-253.md`

# S1b #253 at `1f37f506`: approved, merge behind the S-stack; #57 is deferred

**Stacking:** #253 sits on the S-stack head `2965a01a`.
- It touches 14 files, one of them in core: `verity/evaluation/batch.py`, where the width check reads `width_set()`, a faster path with the same refusals.
- The P10 allowlist only shrinks: `commit.py` goes from 2,936 to 2,927 lines, and `binding_record` from 210 to 201.

**Tests I ran on this VM** (CPU torch 2.14):
- `packages/verity/tests/evaluation`, all of `tests/acquire` (including the 25 torch tests in `test_call_boundary_source`, `test_scale_products_source` and `test_plan`), the vLLM lints P01–P12 and `test_no_by_name_rules`: 202 passed, 0 failed.
- `tests/commit` and `tests/check`: pass, rc 0.

**One behaviour change I checked:** `commit/binding.split_name` now splits on the **last** `/`.
- It matters only for committed names with two or more slashes outside `fa2.m1/`, `fa3.m1/` and `moe/`, which have their own branch.
- Every acquire source's names are in those families, or have at most one slash.
- So for wave-1 rows it changes no identity, and records made at the GO SHA stay valid after #253 lands.

**Rows:**
- **#74:** runs in wave 2 once #253 is on main. It adds about 22 min of plan and 3.4 min of host time per Commit, and must run eager.
- **#57:** deferred to the follow-up epoch with its old record kept. Host evaluation is about 16.4 h per Commit, against my 90-minute stop.
- **#39:** needs #244 (`GemmBias_v1`), which is on neither main `64f94732` nor the S-stack `2965a01a`. If #244 isn't on main by #39's latest start, #39 is deferred too.
