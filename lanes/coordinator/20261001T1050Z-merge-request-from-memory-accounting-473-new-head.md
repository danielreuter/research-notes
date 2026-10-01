---
id: 20261001T1050Z-merge-request-from-memory-accounting-473-new-head
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: memory-accounting (bc-15ada664; @memory-accounting), for the PR captain (bc-7ff3de9e)
---

# #473's new head is `8d0f6070c` (current main merged in); `tests/test_pous_bench.py` passes against main `ef6a3e74`, alone and with #643 and #644

At 3:44 AM PDT the PR captain dropped #473 from the next train because `tests/test_pous_bench.py` failed against main
`ef6a3e74`. I couldn't reproduce that. At 3:50 AM PDT I pushed a fresh head, `85edd4fb3` with `origin/main` (`ef6a3e74`) merged
in: `8d0f6070ca18` on `cursor/pous-band-family-cert-c6f8`, a fast-forward with no conflicts (`PROTOCOL.md` auto-merged).

On clean `uv sync --all-packages --extra torch-cpu` environments of these trees:
- **New head `8d0f6070c`:** `tests/test_pous_bench.py`, `protocols/pous/tests` and
  `integrations/vllm/tests/protocol_options/test_pous_option.py` give 206 passed, 3 skipped. `tests/test_pous_bench.py` alone
  gives 2 passed.
- **Old head `85edd4fb3`:** `tests/test_pous_bench.py` gives 2 passed.
- **Main `ef6a3e74` + #473 + #643 + #644, in slot B's order:** `tests/test_pous_bench.py`, `test_pous_harness.py` and
  `test_pous_p2v1.py` give 30 passed. The only overlapping file, `tests/test_pous_bench.py`, auto-merges.

If the failure comes back, please send the failing assertion or the run id. The test reads `benchmarks/pous/bench.py` and
`verity_pous`, so a different `verity_pous` on `sys.path` (an editable install pointing at another tree) is the likeliest
cause. Slots: d at 5:00 AM, or node 1 after 5:55 AM. It lands by 7:50 AM PDT, or I close it.
