---
id: 20261003T0042Z-finding-pr862-carry
campaign: proofs
lane: red-team-proofs-862
kind: finding
status: final
repo: verity
origin: pr:862@a473afcc7359e9dd0aa86cf50f06f8a26acd2e06
---
# PR #862 carry c927e9800 -> a473afcc7: GRANTED
git diff c927e9800..a473afcc7359e9dd0aa86cf50f06f8a26acd2e06 on DecodeZL/ and DecodeZL.lean: empty. All DecodeZL.* entries in soundness lean-audit.json (47 keyed occurrences, incl. the five records) byte-identical (sorted JSON) between the two heads. Diff vs main 6080aa798 is additions only (1759+, 0-), limited to DecodeZL files, the import line and lean-audit.json. Audit r20261002-235043-2004 PASS (not rebuilt). Carries note:red-team-proofs-862/20261002T2228Z-finding-pr862.
