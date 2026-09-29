---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: workstream-3 backend stress test (bc-ea1c2c4f)
created: 2026-09-27T20:45Z
---

# To the stress-test lane: no lookup slots; reads are inlined as plain gates, and your read-bearing classes can now be proved

This supersedes my 19:40Z answer's §5 plan.

**What changed (Daniel):**
- Every unit is one plain Boolean circuit, with no slot type for table reads.
- The slot branch is parked (unpushed).

**What's there instead:**
- `ir_lower.layout` lays out each `gf2` lookup read as ordinary rows of the unit. It uses the reviewed one-hot construction
  and adds no wires.
- Branch `cursor/flock-inline-reads-4d6a`, stacked on #83:
  - `9a4eeed9`: the lowering and its test;
  - `88db6ee5`: your 20:50Z finding. `unit_input_differs_from_its_message_bits` now flips unit 0 when a block holds one
    unit. Checked on a class with `vus_per_block = 1`: refused, and 31 of 31 cases pass.

**To use it:**
1. Merge the branch into your local integration.
2. Drop `class_statement`'s `"lookup" in cc.circuit.kind` refusal. `stage` then works unchanged.

I measured through your own `stage`, on `7ec44f2b` (attention-exp), `99da1701` (norm-rsqrt) and `70d35316` (`LayerPre`,
two reads), all accepted. Numbers and the scaling are in
`internal/lanes/coordinator/20260927T2045Z-answer-flock-netlist-m0-inline-reads.md`.

**What to expect per read-bearing class:**
- **Circuit and load:** 0.9 GB per ex2 or rcp read and 1.8–1.9 GB per rsq or sqrt read. Each process needs about 20 B of
  RAM per matrix entry (3.2–5.6 GB for one read) and 9–19 s to build the statement.
- **Staging (Python):** 5.5–14 GB peak and 74–234 s per class. Add swap on a 16 GB VM.
- **Selftest:** the full 31-case selftest re-parses the circuit in one process, reaching 14.5 GB on ex2. On large
  circuits, run the cases with `--only`.
- **Gemma's 27-bit tanh reads:** 1.7–2.2 G entries per read. They won't fit a 16 GB VM.

No pod was used. Your $20 cap is untouched.
