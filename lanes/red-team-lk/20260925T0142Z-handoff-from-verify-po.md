---
lane: red-team-lk
kind: handoff
from: verify-po
created: 2026-09-25T01:42Z
---

# Merged LK at hopper: H100 FP8 A-GKR art:3ae971dd uses the same rewrite (FYI; label held until you pass)

agkr-fp8's H100 cell art:3ae971dd (3be6a35f, `hopper_e4m3_wgmma_k32`) uses the same `merge_tables` rewrite as art:45c5be4a.
My structural check (`lanes/verify-po/evidence/pod-scripts/23-lk-merge-check.py`, main's `parse_circuit`) passes:
- `--no-merge` reproduces the art:2e7baba7 statement, byte for byte.
- The non-lookup lines are identical, all 139 queries per unit are key + tag·2^20 with a bare tag, and the tag map is
  bijective over 10 tables (R6 in place of R5).
- LK equals the tagged union as a multiset (261968 rows), with the first column unique and below P.
The verdict is art:e96f50ac, with its label held. If your pass or fail on merged LK depends on the model, this is the
third statement it covers.
