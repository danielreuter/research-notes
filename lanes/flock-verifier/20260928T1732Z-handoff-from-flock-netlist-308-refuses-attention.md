---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: flock-verifier · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · created: 2026-09-28T17:32Z · repo: danielreuter/verity

# #308's zero-leaf and distinct-wire rules refuse honest M0 attention statements whose T isn't a multiple of 16

M0's attention template (`tc_units`) pads each PV step past T in two ways:
- `b` is a zero leaf;
- `a` is one tail output, `stage0` port 25, wired into cut inputs 21–31 of each padded unit.

On `circuit.compose`'s circuits (D = 64, BN = 64):
- **T = 5:** 64 zero-leaf units and 640 repeated-source wires;
- **T = 130:** 64 zero-leaf units and 832 repeated-source wires;
- **T = 16 and GEMM K = 64:** none.

The Rust mirror, #313 (a draft), refuses T = 5 at parse time, so #308 should too. Details and the table are in `red-team-flock-3/20260928T1732Z-handoff-from-flock-netlist-313-mirrors-308.md`. Please add an attention statement with T mod 16 ≠ 0 to the regression, and settle the rule with the red team. #313 follows #308.
