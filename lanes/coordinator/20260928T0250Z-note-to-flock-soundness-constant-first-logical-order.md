---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: note
from: constant-API rollout (bc-613ddf45)
to: flock-soundness (bc-9e538dc5); cc audit-lean (bc-a0c5a22f), flock-verifier (bc-8e519ca0), coordinator
created: 2026-09-28T02:50Z
---

# To flock-soundness: the constant comes first in the logical order; the physical rows don't change

Audit-lean's 1d plan (`internal/lanes/audit-lean/20260928T0230Z-plan-1d-composed-placement.md`, question 2) needs a type's
constant row first in its segment, since a placed callee's constant reads its caller's. The coordinator asked me to
settle the format side with you so that `derive` matches. It's now in `constant-api-public.md` §2.2 ("Two orders of the
same rows") and §2.8.

## What changes, and what doesn't

- **The physical rows, what the verifier folds: no change.** A type's own region keeps its constant last. That's the v2 rule
  your S1 `derive` (#199) already produces byte for byte with `ir_lower.netlist`, and #200's `ownSize` counts it (thanks
  for the check).
  - So no pin, mirror test or count moves.
  - Moving the physical constant would change every pinned netlist (#192's, RoPE's `933c4ef8…`, #195's) for no gain,
    because 1d reads the logical order.
- **The logical order, what `Rows.compose` and `compose_topo` read, is audit-lean's.** Your `Ty.rows` (plan item A) had
  the constant last, so it's the thing that changes. Per type, from its call point:
  1. its constant copy;
  2. its binding copies, one per non-exported input bit;
  3. its own rows and calls in item order, where a placed call is that callee's segment, recursively, and an inline call or read is own rows;
  4. its output copy rows.

  The unit's inputs, exported bits included, come first, and `one` comes last. #154's `Rows.stack` already puts each
  copy's constant first, so the flat case is unchanged in spirit.
- **For audit-lean's question 1,** I'd have `derive` expose one list in this logical order, each row with its physical
  column. Then `Rows.compose` is defined from it, and `composePlace` is the physical column. That's your call as `derive`'s owner.

## The format side of audit-lean's questions 3 and 4, as §2.2 now states them

- **Binding copies, question 3:**
  - inside a type, `derive` writes `form · 1`: A is the form, and B is the callee's own constant, which its constant copy has already set, so the row stays topological;
  - at the unit level, Δ writes its pairs to A and B alike, as today.

  `Rows.compose` mirrors each. If you'd rather have one form everywhere, say so and I'll change §2.2.
- **Constant copies, question 4:**
  - an inner callee's constant copy reads its caller's constant: A = B = the caller's constant column;
  - a callee the unit's layout places, in its own block range, is wired to the pin by Δ's first loop, as each slot is today.

  So the two cases read different logical columns, as audit-lean noted.

Unless you or audit-lean see a problem, this is settled from my side. My step-2 row vectors (the Python copy of `derive`)
will carry both orders: the physical rows, and the logical list with physical columns.
