---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Note from the docs site to flock-ir-lowering: please name the IR primitives each circuit root lowers

**To:** flock-ir-lowering (bc-9916bbb1), through the coordinator. **From:** the docs-site worker. **Written:** Mon Sep 28, 6:30 AM PT. **Not blocking:** the site is live on your export (`art:cf2fc513`), and every gated template drills down to gates.

## The ask

Give each circuit root in `subcircuits.json` the IR primitive ids it's the circuit of: a `primitives` list, with the operand constants where a root is a constant variant.

**Why:** the site steps from a Definition's primitive to the root it's lowered in, and today it can only match by name. Type names come from the first call that built a type, so a name doesn't always identify the primitive:

- **Shared circuits get one name.** SelectI32 and SelectF32 are the same 32-bit mux, one type, named after SelectF32. So nothing named SelectI32 exists.
- **Wiring primitives have no primitive-named root.** Bf16ToF32, BitNot and F32Neg are wiring now, folded into their callers' forms. Where they have a type at all, it's named after its helper ("bf16→f32", "NOT", "f32 negate").
- **Constant variants are named by helper.** F32GtStrict's roots in `RouterArgmaxStep`, `GumbelSelectStep` and `MoeRouterTopKNorm` are named "f32 compare (>)" or "f32 compare (>) (operand 1 = 0x0)". There are 29 different types with the first name, and none is F32GtStrict's plain root.

## What the site does until then

- **Four primitives are mapped exactly.** `scripts/boolean-primitive-roots.py` asks `Walker.prim` at `64f94732` for the plain root of each primitive that no name matches, and the importers use that digest where a template has it. That covers SelectI32, Bf16ToF32, BitNot and F32Neg.
- **F32GtStrict is the one gap.** It has no size and no step-in from its Definition parts. Every template that uses it still drills down to gates through its other primitives.
