---
id: 20260928T1808Z-handoff-from-pouw-mvp-218-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# #218 (protocols/pouw generic protocol) is green with main merged and ready: please merge it

This follows up `20260928T1630Z-handoff-from-pous-land-protocols`. It is from the PoUW MVP owner (bc-dd22acf8).

- **PR:** https://github.com/danielreuter/verity/pull/218, base `main`, head `c726f7e4`, marked ready for review.
- **main:** `432edb3b` is merged in as `c726f7e4`. The conflicts were unions only: `AGENTS.md`, `pyproject.toml`,
  `uv.lock`, `tools/research/src/research/store/tools_registry.py` and `tools/research/tests/test_pythonpath.py`.
  `protocols/pous` and `serving_commit_cost` now sit beside `protocols/pouw` and the PoUW tools, and `uv.lock` is re-locked.
- **What #218 adds against `main`:**
  - `protocols/pouw`: the `PoUWScheme` interface, the audit lifecycle, and the schemes `ncp-v1`, `ncp-v1-shift24` and
    `pearl-fp8-v4`, with their tests and pinned vectors;
  - `benchmarks/pouw`: the harness, the native route-U kernel from #280, and the Pearl B200 calibration;
  - the PoUW store Tool declarations;
  - a `tools/research` fix: `git archive` failures now report git's stderr.

  It adds no circuits, and no `lean-audit.json` or pinned statement. The PoUW Lean stays in the research store.
- **check:** `r20260928-170604-09b7` on `c726f7e4`, PASSED: pytest (3,585 passed), circuit-check, lean-build,
  lean-unit-cut and lean-audit. lean-agreement is skipped because no bundle was sent.
- **The one earlier failure on this head** (`r20260928-163249-e7bf`) was the known race in
  `tools/research/tests/test_remote_local.py::test_exclusive_refuses_a_live_holder_and_reclaims_a_dead_one`, outside
  #218. It passes alone, and the attempt is labelled.
- **Merge:** `research merge cursor/pouw-mvp-4f91`.
  - If `main` moves first (for example with #208), `research merge` will refuse. The conflicts should be the same union
    lines. I'll merge `main` again and re-record `check` when asked.
- **Statement reviewer:** none needed. #218 changes no pinned statement or definition in the repository.
- **Stacked on #218's branch:**
  - #295, the FP8 lane's genuine-FP8 H100 scheme (bc-9914c188, told on #295);
  - #315, the PoUW vLLM option (`protocol_options/pouw.py`), a draft stacked on #311 that also carries #218 until it
    lands.
