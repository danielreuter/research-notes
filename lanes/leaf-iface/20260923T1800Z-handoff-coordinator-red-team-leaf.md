---
lane: coordinator
kind: handoff
created: 2026-09-23T18:00Z
---
# red-team-leaf findings for leaf-iface (full text: ~/.research/notes/lanes/red-team-leaf/20260923T1710Z-report-red-team-leaf.md, ## FINAL)
* **F5**: `ZK_HASHED_NOTE` (relchain.py) hard-codes Poseidon2 and "hiding only up to preimage search" for EVERY leaf. Make it come from the
  LeafScheme (e.g. a `privacy_note` attribute: Poseidon2/BLAKE3 = "deterministic, unsalted: hides only up to preimage search on a row";
  Ajtai = "linear, unsalted: binding-only, leaks equality and linear relations between rows"). Fingerprint and Table 2 footnote read it.
* Cross-scheme framing checked OK (SHA-256 leaf framing separates schemes); keep the scheme name in the leaf domain tag.
