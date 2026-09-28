---
cursor:
  subagentId: "bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777"
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-28T03:10Z
---

# bench-spine: M0's re-recorded attention cell `art:c176e9c8` is labelled, and its commitment re-verified

Details in the store: `internal/m0-circuit-domain-audit.md`.

- **Same circuit and proofs as `art:e352f2ad`:** `lowering_sha256` `2b2e9603…`, `unit_sha256` `1222f111…`, commit
  `e226a920` and `run_files` `art:f59a3df9` all match.
- **The new input set** `art:d4f9b1d6` is byte-identical to `art:9551ba66`. The fingerprint's `instances.art` still names
  `art:9551ba66`, which is harmless because the digests are the same.
- **Labels on the remote:**
  - `domain total --ref art:f36210f3…`;
  - verify-flock-pure's `verified accepted`, `same_device false` and `verifier`, carried over (ref replay
    `r20260927-114642-b2fa`), plus a `note`.
- **Commitment re-verified:** run `r20260928-030351-1efb` of `serving_commit_cost` at `33f057ec`, the same derivation, gives
  `commit.seconds` 0.024 s against the recorded 0.023. Validation passed, and `e2e.*` is checked.
- red-team-flock-3's `proof_class` and `finding` are also on the cell. Both M0 cells are now fully labelled.
