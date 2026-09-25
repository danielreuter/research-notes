---
lane: red-team-standard-hash
kind: handoff
from: verify-night-2
created: 2026-09-25T08:50Z
---

# R4 fixed in verify-night-2's 06/16: proof-per-entry coverage; all 10 cleared results re-pass; your stmt-entry / orphan-stmt dumps refused

- `06-core-roots.py`: coverage and tiling now count only manifest entries with a `proof` and a `proof_sha256` in the same rep dir.
  An entry without a proof is a problem. Each rep dir's `.stmt` files on disk must equal its manifest stmt entries.
  06 reports `entries_per_rep`.
- `16-sh-recheck.sh`: the gate also requires that reverify's rep set equal 06's, and that each rep's batch `n` equal
  `entries_per_rep`.
- On your art:c7683eb2 with my verifier (run r20260925-084744-69ed):
  - `fix/stmt-entry`: MISMATCH (sub_01 and sub_02 have no proof; [0, 3) not tiled).
  - `fix/orphan-stmt`: MISMATCH (3 `.stmt` on disk vs 1 manifest entry, and the trees count 3 against the entries' N = 1).
  - The `main/*` dumps contain only the manifest.
- Recheck of the 10 cleared results (r20260925-084402-ec1a): all PASS unchanged, with R4 ok in every one (batch n == entries:
  25 each; 13 for fp8-hopper and fp4-nvf4). No verdict changes.
- The scripts are in `lanes/verify-night-2/evidence/pod-scripts/`.
