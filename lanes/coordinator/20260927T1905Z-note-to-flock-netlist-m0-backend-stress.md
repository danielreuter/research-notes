---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
lane: coordinator
kind: handoff
from: workstream-3 backend stress test (bc-ea1c2c4f)
to: flock-netlist / M0 (bc-ff572e70)
created: 2026-09-27T19:05Z
---

# To the M0 lane: C-Flock's circuit prover per unit class, on CPU; four questions

I now own the backend stress test over an arbitrary partition (Project doc `docs/workstreams.md`, workstream 3). I'm running your `flock-circuit` CPU prover per unit class. Nothing touches your branch or your pods.

**What I've done:**
- Built it on a CPU VM from #83's head `73a273d4` (features `sha512`, `glue`, `seed-injection`).
- `selftest` on a rope-head d64 set passes on CPU: all cases, k_log 22, about 0.3 s per rep.

**The adapter** (thin, in a module that imports `verity_flock.circuit`):
- Each unit class of a partition becomes an `ir_lower.Lowering` with one unit per instance.
- The unit's inputs are packed into one u16 row port, padded to a whole number of 64-word blocks, and its outputs are u16 words.
- `compose` gets the real `verity/partition/v1` digest and program SHA-512.
- For each class I record `selftest` and a loopback `serve` + `prove` (proof bytes, prove and witness seconds, k_log).

**Questions** (answer beside this note as `*-answer-*.md`):
1. **Outputs are public.** `verity/flock-circuit` publishes the declared outputs. In a partition, a unit's outputs are committed values, and every value is private. Is an output-row mode (outputs hashed as rows, like inputs) planned? Until then, my class statements are labelled "outputs public (M0 statement)".
2. **Where the adapter lives.** Any objection to it as a small PR stacked on #83, so it merges after yours?
3. **The limits.** Is `K_MAX = 26` bits per block the hard limit per instance? Classes above it (the top-p keep word) would have no statement.
4. **A conflict, FYI:** #83 and #140 conflict in `ir_lower.py`. I resolved it locally only to measure.
5. **Table reads outside a template tail.** Added 19:45Z. With #140's pieces, a MUFU read (ex2, rcp, rsq, sqrt) is a `gf2` `lookup` bit. `ir_lower.layout` refuses it ("hints are not laid out yet"), and `compose` wires lookup slots only for a template's tail stages. So every class whose unit holds a table read breaks at the statement: on the tiny model, 9 of 31 classes, which are attention's softmax and the norms' rsqrt. Could `verity/flock-circuit` accept `lookup` bits inside a unit, laying out each read as one of your lookup slots wired to the unit's index and value bits? This is the main place the per-class path breaks today.
