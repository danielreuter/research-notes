---
id: 20261001T1628Z-handoff-from-proofs-hold-core-rows-pending-daniel
campaign: proofs-hillclimb
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Hold the core-rows branch: Daniel is choosing the row schema's design

to: proofs-flock-fp. This applies to `cursor/proofs-flock-fp-core-rows-83e6` @ `074a7a95c`, and it applies now, before your
next commit there.

**Stop adding to it.** Don't extend the per-format schemas (`b0a3a64d0`) into the Rust or Lean verifiers, and don't stage the
CPU table on them. What's built stays as it is: keep it pushed, open no PR, run no GPU job.

**Why.** Daniel is deciding between your three per-format schemas and one format-free schema that I proposed at his
request:
- a row is the bits of its words, each word low bit first, which is the tensor's own bytes;
- it's hashed under a one-block prefix of tag and bit length, with SHA-512's padding as constants from that length;
- there's no format or role in the prefix, no whole-block rule, and no shape refused.

The reason it's on the table is that soundness on main is parametric in the row encoding (`Binding/Rows.lean`,
`HmRows.enc` with `enc_inj : Function.Injective enc`) and has no block structure.

I'll write again with Daniel's ruling. If it's the format-free schema, most of `074a7a95c`'s stager wiring carries over,
and `b0a3a64d0` gets replaced by a smaller core commit.
