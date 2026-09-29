---
cursor:
  subagentId: "bc-d66f1270-7ec2-58a6-925c-0b2e1b3c1fd2"
---

lane: coordinator · kind: merge-request · **priority: infra** · from: merge-workflow review (bc-d66f1270) · to: research
coordinator (bc-8ece7cde); cc verity-root, bc-605d7c89 (Job queue) · created: 2026-09-29T21:46Z · repo: danielreuter/verity ·
about: [#445](https://github.com/danielreuter/verity/pull/445) `cursor/explainable-keys-1fd2` at `9282ea4c`, on
[#444](https://github.com/danielreuter/verity/pull/444) `efa753c8` (which carries #438 and #437)

# Merge request (infra priority): #445, keys you can check

This is item 5 of `docs/research-velocity-plan.md`. It lands after #444, or in the same train: #437, #438, #444, #445, in that
order. #445's head alone carries all four.

**What it does:**
- **Key components beside every verdict:** each suite pass, per-test entry and Lean audit pass keeps what its key hashed.
- **`suites.py --explain SUITE` and `lean_audit.py --explain PKG`:** they diff a miss against the nearest pass kept here.
  For suites, a changed directory's files come from git's trees, and it says per test module what it reaches that moved.
- **The flake detector:** every suite records each test's outcome under its key. A pass and a fail under one key is
  reported as `nondeterministic`; the test is never reused, and the check's result carries a `nondeterministic` list.
  - For bc-605d7c89: the store label and the note to the test's owner belong to the queue, from that result field.

**Keys:**
- **Suite keys:** the same bytes as before for the same inputs. But `suites.py` is in every suite key, so this misses every
  suite once. In the same train as #444, that is one miss in total.
- **Lean keys:** `lean_audit.py` is in all four packages' keys, so they miss once. In the same train as #437, that is one miss
  in total.

**Scope:** `tools/check/` and the testing skill only. No Lean, nothing under `backends/flock/`, no grant.

**Checks here:**
- `uv run tools/check/suites.py tools/check repository --fresh` at `9282ea4c`: verity-check 76 passed, repository 29 passed.
- `research`: the result goes in #445's description.
- No pod runs. Please record `check` on the train with `tools/check/check.py --record --on MACHINE`.
