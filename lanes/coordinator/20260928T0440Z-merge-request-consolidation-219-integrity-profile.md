---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc one-stage audit (bc-c520c11b), audit-lean (bc-a0c5a22f)
created: 2026-09-28T04:40Z
---

# Merge request: PR #219, the integrity profile as one object (Daniel's decision, 04:07Z)

- **PR:** [#219](https://github.com/danielreuter/verity/pull/219), branch `cursor/integrity-profile-object-ac68`, head **`39c9ebb8f04466d6c1667ce573d9e7eb37ca3203`**, into `main`. Ready, CPU only, $0.
- **Contents:**
  - one `IntegrityProfile` for subset, Bernoulli and stratified laws, with `bound()`, `stratum_bounds()` and the generic `harm_bound`;
  - `verity_one_stage.audit.profile()` returns it for every law;
  - the new `verity_one_stage.consumers` holds `exfiltration_bound` and `compute_bound`;
  - the protocol docs split the profile from its consumers.
- **Nothing recorded moves:**
  - the audit record's bytes are held to `main`'s computation by a test;
  - every bound and reading is byte-identical against `main` in a comparison script;
  - no digest, vector, Lean file or `lean-audit.json` changes, so no statement reviewer is needed.
- **Tests:** core `proofs/` with `protocols/one_stage/tests/`: 562 passed. `protocols/`: 49. Boundaries, repository and flock's `test_audit_profile.py`: 23.
- **Overlaps:** trial merges are clean with #211 and #168. #132 conflicts only where it already conflicts with `main`.
- **Epoch:** moves no digest.

**For the one-stage lane (bc-c520c11b):** folding the record's three profile fields into one changes recorded bytes, so it needs an audit-record format bump from v0 to v1. That's your call, and it's left out of this PR. The survey and details are in `20260928T0423Z-note-to-one-stage-and-audit-lean-from-consolidation-integrity-profile.md`.
