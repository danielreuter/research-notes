---
id: 20260930T2135Z-handoff-from-network-accounting-326-merge-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: network-accounting subcoordinator (bc-ecea50f6-c509-5918-b17a-d2148d57728f; @network-accounting), owner of #326 since the idle network-timing agent bc-6b78649f
---

# #326 is merge-ready: head `629ec80e` contains main `e15dc1ef`, and its recorded check passed on vy-nebius-1

This supersedes the tip and check in `note:20260930T1535Z-handoff-from-network-warden-326-merge-request`. The request itself
stands; I own the PR now.

- **PR:** [#326](https://github.com/danielreuter/verity/pull/326), `protocols/network_warden: reference for the bucketed
  warden's timing channel`, branch `cursor/network-timing-reference-86f3`.
  - **Head:** `629ec80eacac36e845ccc6946e143d16ffabab92`, which contains main `e15dc1ef1` (train TCQ), as merge commits with
    no force push.
- **Recorded check: passed.** `r20260930-211439-1879`, `check.py --record --on vy-nebius-1`, on exactly this head, clean tree.
  - It started at 2:14 PM PDT and ran about 13 min, with class SUCCESS and rc 0.
  - Every step passed: preflight lock and lints, pytest (741 s), circuit-check, flock-circuit-build, lean-build, lean-unit-cut,
    lean-audit and lean-suites.
  - `lean-agreement` was skipped by name, since nothing under `backends/flock/` changed.
  - It was the first full check on node 1 since @infra restored its toolchain at 2:13 PM PDT.
- **Grants: none needed.**
  - No `lean-audit.json` changes, so no pinned statement or definition changes.
  - `CheckAxioms.lean` only regroups its `#print axioms` lines: 31 pinned, then the 3 proved but unpinned.
  - Nothing under `backends/flock/` or `integrations/vllm/` changes.
- **What changed since `c176adb1`,** after a review on main `b1c77be0` (verdict: land after fixes):
  - Calibration raises a clear error, instead of looping, when one bucket's demand exceeds the queue capacity.
  - An out-of-set clock sync is an `advice` violation in its own window only.
  - Two records for one link-window are a `duplicate` violation.
  - `SyncSet` rejects a repeated δ or ρ.
  - The docs no longer overclaim: PROTOCOL.md, the Lean README and the AGENTS.md sentence now name the 15 pins and 3 unpinned
    lemmas the tests mirror.
  - It documents that ingress links' statuses aren't audited yet.
  - Units are consistent, references outside the repo are gone, and the title no longer says "(draft)".
  - 14 commits, each with tests where behaviour changed.
- **Tests on the head:** 71 network-warden and 33 repository tests pass locally; the recorded check covers the rest.
- **Order:** it conflicts with nothing I know of; any train slot works. If main moves before the train, the train's check of the
  merged tree covers it.
- **Cleanup for the train owner:** `cursor/network-timing-lean-86f3` (`eabfdc67`) is stale, superseded by train TLS, and can be
  deleted.
