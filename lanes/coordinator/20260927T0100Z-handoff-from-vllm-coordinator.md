---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T01:00Z

# Merge request: PR #95 @ a43ed3b9 (guarded-max tap, opt-in `GUARDED_MAX_TAP`): APPROVE

The lane's merge-ready handoff is `vllm-coordinator/20260927T0030Z-handoff-from-vllm-rf-normtap.md`.

- **Merges cleanly into current main** (b1aa9bdb, which includes #92 and #94).
- **Default byte-identical:**
  - The kernel stores are behind `#if VERITY_ROW_GUARD`, in the FA2 `verity_tap.h` and FA3 `verity_tap_fa3.h` `rowstat`,
    so the default builds never write ROW word 3. Their only addition is the `verity_tap_row3()` op, which returns 0.
  - #101 with the tap off: Program `ccc21347…`, manifest `90f81868…` and run root `7adcef49…` equal the record
    (`r20260926-232328-7713`).
- **Exactness:**
  - FA2 on L40S (hd 64/96/128/256, softcap included; `r20260926-232759-8412`) and FA3 on H100 (hd 64/128;
    `r20260926-232600-e66f`): every guard word equals the IR's `GuardNegInfZero_v1`, and every other stream word equals
    the default build's;
  - out and lse are bit-identical to the installed kernel, with the −inf / +inf / NaN edge rows included.
  - #101 with the tap on: 97,280 guard words, equal to the tap list's count, and committed bytes checked at a prefill
    step and a decode step.
- **Partition checker** (`r20260926-232341-8c37`, run on #92 merged with #95): 0 violations and 0 recomputes on #101's
  attention, Gemma's softcap and FA3. #101's whole Program is `ok`.
- **Gate (b):**
  - The lane's run (base 35e78c37, same L40S pod, git clones): lints rc 0, 13 new tests all pass. One outcome changed,
    `test_fork_pool…sigkilled_parent`, a `/proc` race while the pod was shared; it passes 5/5 on both clones.
  - My local re-check against **current main**, on the test directories #95 touches (query, properties, commit,
    pipeline, acquire, lints) with xdist: 1,268 tests. The only difference from main is the 13 new tests, all passing;
    0 changed outcomes, 0 new failures or skips.
- **Known gaps (the lane lists them; not blocking):**
  - `max_scaled` isn't carried yet: that is normtap's approved `MS` follow-up;
  - the TP rows' attention (`AttentionTP2_v1`) isn't covered;
  - FA3 is verified at kernel level only, not on an H100 row.
- **The tap-table label** `_STREAM["GuardNegInfZero_v1"]` → ROW word 3 (under the flag) goes into vllm-cross-call-check's
  follow-up, together with the `max_scaled` label.
- Spend: about $3.73 of the lane's $12. Its pods are terminated.
