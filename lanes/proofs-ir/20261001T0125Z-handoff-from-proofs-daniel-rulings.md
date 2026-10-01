---
id: 20261001T0125Z-handoff-from-proofs-daniel-rulings
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Daniel's rulings on docs/boolean-ir.md (6:20 PM PDT)

1. **Conformance is not an assumption.** Daniel: "conformance is more or less out of scope; all we care about is that it
   explains the I/O of vLLM through a path of tiny subcircuits." Drop "a named assumption per instruction" from "Why this
   closes the soundness gap". Soundness rests only on SHA512CR-strict, SHA512CR-expected and A3. Matching the silicon is
   a labelled, evidence-backed claim about what the statement means, outside the security claim.
2. **Tables are already Boolean.** `ir_lower._Read` lays out MUFU reads (rsq, sqrt, rcp, ex2) as plain rows: the
   index halves are decoded one-hot, each output bit is `hi_h AND (XOR of the low minterms whose table bit is set)`, few
   ANDs, and the table's contents are XOR fan-in. M0 also has a lookup slot (`live/src/lookup.rs`). So:
   - **Decision 6 changes:** allow an n-ary XOR (and n-ary AND) as the same primitive. Binary-only would make one 2^24
     table hundreds of millions of descriptor gates. Backends may split into pairs.
   - **Decision 4 changes:** vLLM need not wait for a lookup gate. A served Program can go Boolean with each table as a
     ROM Definition generated from its pinned digest (the `_Read` construction). Lookups become an optimization of the
     big tables' linear cost (about 10^8 XOR inputs for a 2^24 table, 10^9 for the 2^27 tanh), not a blocker.
   - Fix the note's "infeasible for the MUFU tables" wording, and the migration order: tables are no longer step 5's
     prerequisite for served Programs.
3. **Amend README, the Glossary and `verity/ir/PROTOCOL.md`** in the same PRs as the code. Daniel said yes.
4. **Recommendations 1, 2, 3, 5 and 7 stand,** as Daniel read them ("looks pretty good"); 4 and 6 change as in point 2.
5. **Levers** (`docs/boolean-ir-restructure-levers.md`): no ruling yet. Plan slots to follow your slice.

Update `docs/boolean-ir.md` accordingly at your next stop. Say in your lane if the n-ary XOR clashes with anything in
step A, for instance `Q_word` v1's wide-gate rule.
