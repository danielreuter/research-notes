---
cursor:
  subagentId: "bc-6b78649f-a717-5744-b3d4-04b44e9386f3"
id: 20260930T1535Z-handoff-from-network-warden-326-merge-request
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: network-warden (bc-6b78649f, for pous)
---

# network-warden -> RC: merge request for #326 (`protocols/network_warden`), now that #461 has landed

- **PR:** [#326](https://github.com/danielreuter/verity/pull/326), branch `cursor/network-timing-reference-86f3`, head
  **`c176adb101abbe1d563737c1b106c73bafcb0865`**. It's ready for review, out of draft.
- **Base:** it has `main` `2c4101bf` (train TLS) merged in, as merge commits with no force push, and it merges cleanly onto
  it.
- **Recorded check: passed.** `r20260930-151146-adaf` is `check.py --record --on vy-nebius-2` on exactly this head, in a
  node-2 check slot (724 s). Every step passed: preflight, pytest, circuit-check, flock-circuit-build, the Lean build,
  unit-cut, the Lean audit and the Lean suites. The attempt is on the remote: tool `check` v1, `source.commit` =
  the head, clean tree.
- **Grants: none needed.**
  - It pins nothing: no `lean-audit.json` differs from `main`.
  - It touches nothing under `backends/flock/`, so `lean-agreement` was skipped by name.
  - It touches nothing under `integrations/vllm/`.
- **What it changes** (21 files):
  - the new distribution `protocols/network_warden`: the warden's grid, the schedule and clock-sync advice, the exact
    audit on records committed by hash, the capacity counts, calibration, and 66 tests;
  - its workspace registration: `pyproject.toml`, `uv.lock`, `tools/research/tests/test_pythonpath.py`;
  - one sentence in AGENTS.md's protocols map;
  - in `protocols/network_warden/lean/`, docs only: the README and `CheckAxioms.lean` now say 31 pins, not 34, per #461's
    red-team follow-up (`occ_fill`, `leftPacked_occ_fill` and `leftPacked_fifoGrid` are proved but not pinned).
- **Tests on the head:**
  - `uv run tools/check/suites.py network_warden`: 66 passed;
  - protocol boundaries, repository, pythonpath and Lean-package tests: 108 passed.
- **One stale branch:** `cursor/network-timing-lean-86f3` has three commits past #461's merged head (`eabfdc67`): my
  own main merge, rehash and pin. TLS superseded them. They're unused, and the branch can be deleted.
