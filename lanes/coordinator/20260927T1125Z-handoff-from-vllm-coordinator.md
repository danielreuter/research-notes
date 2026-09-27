---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T11:25Z

# Merge request: PR #119 @ dabffea5 (serving commits in M0's format, opt-in `SERVING_ROWS`; A2 and A4 served): APPROVE

The lane's handoffs are `vllm-coordinator/20260927T0918Z-…-merge-ready.md` (A2), `…T1105Z-…-gate-b-estimate.md` (A4 and the final
head), and the copies of its e2e handoffs.

- **Merges:** `dabffea5` is a real two-parent merge (`b08eda03` + main `792704d7`), and it merges cleanly into current main `407663fb`
  (train D).
- **Opt-in:** `vllm-v1` stays the default and the record.
  - #101's manifest from the stored Build is byte-identical on main and head (`90f81868`, file `9e010897`).
  - On GPU with the scheme off, the run root `7adcef49` = the record.
  - With the scheme on, the `vllm-v1` run root stays `7adcef49` in every served run: A2 pre-canonical and canonical, A4 P4, A4 P6.
- **Headline evidence:**
  - A2: 183,680 RoPE heads, with M0's `write()` byte-identical to serving's `pub`/`inst`. The e2e lane's A2 is `complete: true` on
    both bundles.
  - A4: P4 has 12,341 non-GEMM units, and P6 is the whole layer 0 with shared GEMM rows, 6,771,765 units. Every member is
    byte-identical to M0's writer, and the served rows equal the capture.
  - Overhead: 14.6 s (A2) and 17.3 s (P6) of hook time, against a Commit stage of about 190 s.
- **Tests:**
  - my jdiff of main 407663fb against main + #119 over `tests/commit`, `tests/pipeline`, the lints (P7–P12), by-name, imports and
    dead-modules: 11 new tests pass, and **P12 now passes** (the 09:55Z hold is cleared).
  - One changed outcome, `tests/commit/test_roundtrip::test_transient_storage_is_released`, is **flaky on main too**. Run alone 6 times:
    base fails 3/6 (38,771–39,174 B against a 37,984 B bound), head fails 4/6 (39,225–39,786 B). A pre-existing flaky allocation bound,
    not a regression. See the note below.
  - The lane's pod gate (b) this morning: jdiff rc 0.
- **Spend:** serving-commit has used about $5.5 of its $40 (A2 pods, gate (b), the canonical re-serve, A4 P4/P6). All pods are
  terminated.

## For the commit-path owner (not blocking)

`test_transient_storage_is_released` bounds `tracemalloc` growth at `400*36 + 400*18 + 16*1024 = 37,984` B. It measures about 38.7–39.8 KB
on main and fails about half the time run alone on this VM. It needs a larger bound or a measurement that excludes lazy-import
allocations.
