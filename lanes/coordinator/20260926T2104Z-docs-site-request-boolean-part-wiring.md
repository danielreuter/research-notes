---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Request from the docs site: how a Boolean subcircuit's parts connect

**To:** coordinator, for flock-ir-lowering (the Boolean-circuit export). **From:** the docs-site worker. **Written:** Sat Sep 26, 2:04 PM PT. Daniel asked for this.

## Why

The Program visualizer now steps below a Call's primitives into `internal/datasets/boolean-circuits/`. It draws every level as nodes and wires, and Daniel wants that to hold all the way down to AND, XOR and NOT gates. Two levels can't be drawn that way today:

- **A subcircuit's parts.** `subcircuits.json` gives each subcircuit's children with counts, but not which part feeds which. So the tensor-core k-step (AmpereBF16TcDot16, 26k gates) opens into its operand decodes, multiplies, group sums and rounds with no wires between them. Daniel read that as broken, and the site can't infer the wiring:
  - each child's gate list only says its inputs are its own argument bits;
  - the step itself is over `gate_limit`, so it has no list.
- **A listed subcircuit's own parts.** Lists are written only for the topmost subcircuits under the limit. So a group sum (7,122 gates) or a RoPE pair unit (17,503 gates) can only be drawn as one flat netlist. Its align, add and normalize, or RopeOut and RopeOutAdd, can't be opened on their own.

## What would fix it

Either of these works. Take whichever is cheaper to emit.

1. **A part graph for each subcircuit with children.** List its child instances (child id, instance index) and its wires: for each input bit of each instance, whether it comes from the subcircuit's own input bit i, another instance's output bit j, or a constant. Aggregated bundles are fine, like `{from, to, bits}` per pair of instances plus the subcircuit's inputs and outputs. The site folds identical instances itself, as it does for Definition bodies.
2. **A part tag on every gate.** In each gate list, record the child-instance path (within the listed subcircuit) that each gate lies under. Raise `gate_limit`, or special-case dot steps, so the tensor-core k-step gets a list. The site derives each level's wiring from gates whose tags differ, and each part's own gates from the gates carrying its tag.

Option 1 scales to the warp units (≈1 M gates), where tagged lists would be large. Ideally both land: part graphs for every subcircuit, and part tags in the lists that exist.

Row #101 first. The other 12 rows can follow in the same format. Until this lands, the site marks unwired parts as "not wired in the export" rather than drawing them as if they connected.
