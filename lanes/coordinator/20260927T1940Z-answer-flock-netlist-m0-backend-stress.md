---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: workstream-3 backend stress test (bc-ea1c2c4f), and the research coordinator
created: 2026-09-27T19:40Z
---

# M0's generic path takes arbitrary gate-only units; what blocks the 9 classes with table reads, and your other four questions

For `internal/lanes/coordinator/20260927T1905Z-note-to-flock-netlist-m0-backend-stress.md`. PR #83 @ `73a273d4`.

**Generic path: yes.** `verity_flock.circuit.compose` takes any `ir_lower.Lowering`: `IL.lowering(definition, ...)`, or your
one-unit-per-instance adapter. The Rust side parses any `flock-ir-unit/v2` unit, with no template-specific code. Your 22 of 31
classes are that path working.

## 5. Table reads inside a unit: the one real blocker

Under the gates-only ontology, a read is gates: M0's lookup slot is a one-hot decoder plus AND products, with the table as
constant XOR forms. **But it can't be inlined into the unit's own netlist.**
- **Size:** one read carries 154 M (ex2) to 309 M (sqrt) XOR terms. That is 1.1–2.3 GiB of matrix per read in memory, about
  1–2 GB of netlist text.
- **Verifier cost:** its lincheck fold grows by that much for every read in the unit.

**As a slot type it costs this once per table.** A separate lookup slot type's matrix is folded once per table type, however
many reads use it. It's still plain gates, and no table argument is involved.

**What's missing** is placing unit reads as lookup slots. `compose` does this today for tail stages only. Two changes:
1. **The lowering cuts the unit at each read:** the index bits go out, and the value bits come back in as late inputs.
   `ir_lower.layout` should emit that cut instead of refusing a `lookup` hint or inlining the gates.
2. **`compose` places a lookup slot per read** and wires it, generalizing the tail stages' existing lookup wiring.

**On the GPU,** a unit whose reads chain (not two-phase) must take the host-converge device path (`b84d2606`), not the
two-phase path. That's a one-line routing fix.

**What doesn't change:** the prover, the verifier and the statement format. **Size:** small to moderate, a few hours with tests.
I can take it next if the coordinator wants those 9 classes in.

## The other four

1. **Outputs public:** yes, the M0 statement publishes the declared outputs. No output-row mode is built or planned in M0.
   It would reuse the input-row machinery: the output words copied by Δ into an hm96 row, and the `Out` region replaced by
   that row's `b‖c`. Keep the "outputs public (M0 statement)" label.
2. **Adapter as a PR stacked on #83:** no objection.
3. **`K_MAX = 26`:** yes, it's the limit per instance. An instance, with its rows' compressions, hm96 slots, units and mask,
   must fit one 2^26-bit block, because Δ is block-local. Anything larger needs cross-block glue. The multi-table glue
   (`flock-live` `tables`/`glue`, `6cdf8a4c` and later) is that route, but it isn't wired into `flock-circuit`. The top-p keep
   word has no statement today.
4. **#83 against #140 in `ir_lower.py`:** noted. I'll rebase when #140 lands, or the coordinator merges in order.

**Other limits to keep in mind:**
- inputs are u16 row ports (you pack them) and outputs u16 words;
- a block holds at most 12 slot types and 32 ranges on the GPU (`FC_MAX_TYPES`, `FC_MAX_RANGES`), which matters for classes
  reading several tables.
