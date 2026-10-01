---
id: 20261001T0137Z-reply-from-71c6ab78-pearlc4-vo-rule
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: GPU 5, FP4 design (bc-71c6ab78)
---

# Re Daniel's 5:52 PM PDT Pearl-C4 ruling: #580 refuses V/O rotation or head interleave on an unrotated checkpoint (head `639128c8`)

**#580** (`cursor/pearl-c4-f1f2-3084`) **is at `639128c87`. 1,691 of its tests pass** (verity 1,351, pouw 278, benchmarks
62), and the repository suite's 32 pass too. The suites ran at 6:32 PM PDT (logs `20261001T013228-4378`). No GPU time was
used.

**The rule** (`protocols/pouw/verity_pouw/schemes/pearl_c4.py`: `check_registration`, `PearlC4.check_registration`,
`REGISTRATION_STACKS`; stated in PROTOCOL.md's Pearl-C4 section under "Registered weights"):
- A registration declares its keyed transforms in order. It passes only as one of two stacks:
  - the keyed 8-block rotation alone;
  - the rotation, then the keyed V/O rotation, then the keyed head interleave.
- An unrotated checkpoint registers only from the curated list, the fallback (Daniel, 1:36 PM PDT).
- **V/O or the interleave on an unrotated checkpoint is refused, curated or not** (Daniel, 5:52 PM PDT).

**A correction to the brief:** #580 had no registered-weights rule in code before this commit; the 8-block rotation was
adopted only in the notes. This commit writes both rules: the rotation as the registered-weights rule, and V/O plus the
interleave inside it.

**One default I took, which can be reversed:** V/O and the interleave register only together, after the rotation. V/O
alone, the interleave alone, another order, or an unknown name are refused, because the two were measured only together
(`rotb8s-nvfp4_al_voi`). If either alone should pass, it's a one-line change to `REGISTRATION_STACKS`.

**Tests** (`protocols/pouw/tests/test_pouw_pearl_c4.py`):
- `test_vo_rotation_and_head_interleave_register_inside_the_8_block_rotation_only`: the rotation, V/O and the interleave
  are accepted, curated or not. V/O plus the interleave, V/O alone and the interleave alone are each refused on an
  unrotated checkpoint, curated or not.
- `test_registered_weights_take_the_8_block_rotation_or_the_curated_list`: the rotation alone is accepted. An unrotated
  checkpoint is accepted only if curated. Half pairs, the wrong order, a repeated rotation and an unknown transform are
  refused.

**The 0055Z order:** read and in force. I own none of tonight's goal-critical jobs, so I have no READY line to write.
Nothing in #580 changes the pinned vectors or the 8,192³, decode and 16,384³ rows; this commit adds a registration check
only.
