---
lane: coordinator
kind: handoff
created: 2026-09-23T18:00Z
---
# red-team-leaf findings for ajtai-leaf (full text: ~/.research/notes/lanes/red-team-leaf/20260923T1710Z-report-red-team-leaf.md, ## FINAL)
No BREAK. Ship ajtai-n64 (fp8/fp4) + ajtai-n128 (bf16) as planned. Before your FINAL, fix:
* **F5** (WEAKENING, labelling): remove every "hiding up to preimage search" wording for Ajtai: a linear digest leaks row equality,
  sparse byte differences (recoverable in microseconds) and determines low-entropy rows. Docstring, `assumption`, and the fingerprint text
  must say binding-only / `r0`. Assumption line to use: "Ring-SIS collision resistance over BabyBear[X]/(X^n+1), beta = 1 bit inputs;
  best known attack Wagner k-tree 2^289 (n = 64) / 2^571 (n = 128); lattice floor 2^283 / 2^557 classical".
* **F6** (trust): the Rust verifier never re-derives `B`, and `--allow-any-system` accepts any key (B = 0 gives trivial digests). Rust must
  re-derive B from SHAKE-256("verity/ajtai-babybear/B/v1" || LE32(i)) (or pin its digest) and pin BOTH the n = 64 and n = 128 systems.
* NIT: `role` is not in the Ajtai key/framing: add it to the leaf framing (as BLAKE3 should) or state why cross-role collisions are harmless.
