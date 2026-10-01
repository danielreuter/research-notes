---
id: 20261001T0110Z-handoff-from-proofs-levers-section
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Link the levers section from docs/boolean-ir.md, and check it against your design

Daniel is deciding your seven decisions now, together with the restructure study's levers. You were mid-run, so I wrote
that section myself:
`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/boolean-ir-restructure-levers.md`. It covers step-sized
slots, cross-block wiring, lookups and weight binding: how each fits the Boolean IR, with a recommendation for each.

At your next stop:
1. Add one line to `docs/boolean-ir.md` under the decisions linking that file, or fold it in as a short section, your
   choice.
2. Tell me in your lane if anything in it contradicts your design. In particular, check the claim that slots need the
   lowering to lay each Call out whole, rather than sharing identical ANDs across Calls as your decision 7 notes.
3. Plan the slice so slots can follow it directly on `GemmCoordinate_v3`, since that is the recommended first lever.
