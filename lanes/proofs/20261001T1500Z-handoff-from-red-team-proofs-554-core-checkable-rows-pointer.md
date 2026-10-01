---
id: 20261001T1500Z-handoff-from-red-team-proofs-554-core-checkable-rows-pointer
campaign: overnight
lane: proofs
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# Pointer: the design review for core-checkable packed rows is in flock-fp's lane

to: proofs. The step 1 design review is
`note:proofs-flock-fp/20261001T1459Z-handoff-from-red-team-proofs-554-core-checkable-rows-requirements`. Its main
conditions:
- **The prefix.** It binds the format (element format, scale format and group, byte order), the role (1 for x rows, 2 for W
  columns) and the code width, k and scale count. It is one 128-byte block with no padding. `sha512/row/v1` at width 8
  doesn't name E4M3.
- **The rows** are the tensor's own bytes in core's order (NVFP4 is `nvfp4_row_bytes`), with no zero padding to whole
  blocks.
- **The coincidence test.** It enumerates the new, default and packed frames, and must find no shared digest across
  formats, roles or k, nor between the new frame and an old one.
- **Core lands first.** The schemas go into `verity.commitments.rowleaf` and `frame_v3/PROTOCOL.md` §6 with vectors.
  `frame-v3-sha512` must admit them, and the hiding leaf's schema string must name the inner schema.
- **Both verifiers** (Rust and Lean) derive each prefix, midstate and padding from the per-port (schema, role, k) and
  check the length. Partial last blocks (MXF4 K=2048 is 8.5 blocks) are either pinned by the verifier or refused. Pinned
  Lean records that change need a statement reviewer, and the change needs lean-agreement.
- **The claim** stops at "a row opened from the root checks with core alone". It may not claim a weights-root binding,
  because Flock's inner digest is private behind hm96 and no weights root uses this schema.

For you: the new SHA-512 MXFP4 and FP8 schemas, and admitting element rows into `frame-v3-sha512`, are new core
protocol. I recommend mirroring §4a and landing it in core first. Whether it needs Daniel is your call.
