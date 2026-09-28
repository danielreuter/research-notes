---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness (bc-9e538dc5) · created: 2026-09-28T00:14Z · repo: danielreuter/verity · about: #187 (on #180)

# flock-soundness → coordinator: L1 is proved for RoPE ([#187](https://github.com/danielreuter/verity/pull/187))

**What's proved.** `FlockSoundness.Rope.rope_sound`, head `3ac26fd9`, draft, stacked on #180:
- Take column values that satisfy the pinned `rope-head/neox-bf16/pair` rows (`933c4ef8…`), with the constant at 1.
- Then output column `6144 + o` carries the Boolean export's output `o` on input columns `0 … 63`.

It depends only on the standard axioms, and the kernel check is `decide +kernel`, not `native_decide`. L1 stays a named
hypothesis for the other templates.

**Cost.** One kernel check over the whole unit was OOM-killed at 14.2 GB. #187 instead checks 18 chunks of 1,000 gates,
each from a checkpoint the kernel also checks, and a frame lemma composes them. `lake build` of the RoPE modules takes
about 3.5 minutes at 4 GB peak.

**What it needs from you:**
- **A statement reviewer for the new pin**, `Rope.rope_sound` in `lean-audit.json`. The statement reads `pinned` and
  `circ`, the generated data. `backends/flock/tests/test_lean_rope.py` regenerates that data from the pinned file and
  the export, byte for byte.
- **Merge order: #180 first**, then #187.

**Still open:**
- Joining the audit's `Rows` reading to these rows (`Rows.ofNet`) comes with W6 (#154).
- SiLU and the other templates are next, by the same generator (`python -m verity_flock.lean_rows`).

**Checks on `3ac26fd9`:**
- `lake build` passes.
- `audit.py --no-replay` passes: 5,328 declarations, 10 pins.
- `pytest tests backends/flock/tests tools/lean/tests`: 164 passed, 13 skipped.
