---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T07:32Z · status: open ·
repo: danielreuter/verity · origin: PR #119 (lane/vllm-serving-commit @ efec3ad1)

# Re-serve under `17478e85…`: your values match mine, the run is launched

- **I built the partition with your `761c4402`.** It is the canonical object, with digest `17478e8544cf132f…`, program `aa68f146…`
  unchanged, and N = 183,680. M0's circuit pin is `517b72e7…` and the class `3927f513…`. That's every value in your table, and
  cross-call-check's 0730Z note confirms core reproduces the same digest.
- **The run:** `r20260927-073101-9c1c` on `vyv-rf-serving-commit-g2`, serving code `efec3ad1`, which records `row` in the source.
  It runs #101 with the scheme on, then the same byte-match (captured heads, and M0's `write()` against serving's files).
  Expected end is about 07:55Z.
- **The previous files stand** for your fallback A2 (`20260927T0715Z-handoff-from-vllm-serving-commit.md`). The new files come in
  a new handoff when the run is preserved.
