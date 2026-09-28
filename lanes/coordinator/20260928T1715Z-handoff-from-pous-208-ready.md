---
id: 20260928T1715Z-handoff-from-pous-208-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #208 (protocols/pous generic protocol) is green on main and ready: please merge it

Follow-up to `20260928T1630Z-handoff-from-pous-land-protocols`.

- **PR:** https://github.com/danielreuter/verity/pull/208, base `main`, head `85912edd`, marked ready for review.
- **main:** `432edb3b` (train H, with #162, #183, #166 and #196) is merged in as `85912edd`, with no conflicts. Against
  `main`, #208 is its own 24 files: `protocols/pous` (the generic protocol, `schemes/`, their tests and vectors),
  `benchmarks/pous`, and `tests/test_pous_bench.py`. It adds no circuits and no Lean.
- **check:** `r20260928-161655-cfd9` on `85912edd`, PASSED: pytest, circuit-check, lean-build, lean-unit-cut and
  lean-audit; lean-agreement is skipped because no bundle was sent.
- **The one earlier failure on this head** (`r20260928-154542-00c7`) was the known race in
  `tools/research/tests/test_remote_local.py::test_exclusive_refuses_a_live_holder_and_reclaims_a_dead_one`, outside
  #208. The runner writes `done` before it releases `.exclusive.lock`, and under load the test can check between the
  two. It failed twice in eight runs today, and passes alone.
- **Merge:** `research merge cursor/pous-mvp-interface-c934`.
- **Statement reviewer:** none needed. #208 changes no pinned statement or definition.
- **Not in #208:** the vLLM `protocol_options` scaffold, now owned by the new composable-options worker. The POUS
  adapter, `pous.py`, follows on that worker's hooks interface.
