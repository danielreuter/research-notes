---
id: 20261001T0145Z-handoff-from-proofs-lean-standards
campaign: verity
lane: proofs-lean-restate
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Lean's standards for the restatement, read against `d6c8b0e37`: §12 applies, the footprint needs four fixes, and these are working theorems

to: proofs-lean-restate (bc-3b607340), the writer; red-team-flock-3 (bc-f0bc7e75), the reviewer of record. The same note
is in both lanes. These are lean's (bc-19c498a8) answers, relayed by the top-level at 6:44 PM PDT. Lean sets the
standards for Lean in Verity. Nothing is pinned without Daniel's yes.

1. **`docs/lean-infrastructure.md` §12 applies.** On top of `note:20261001T0131Z-handoff-from-proofs-acceptance-criterion`
   (every `--update` entry traces to one of the seven changes or to L1's removal; one PR; no new pins needed), the
   reviewer checks three things by hand:
   - Every Prop hypothesis of each headline maps to a claim id, an open obligation or a numeric condition. The wrappers
     `LinkCR`, `TableCR` and `finder.CR` are traced to `SHA512CRExpected` or `SHA512CRStrict`.
   - Every removed or renamed pin is listed with its replacement or its reason. A rename counts as one retirement plus
     one new pin.
   - **Teeth:** each CR assumption holds for an injective hash and fails for a constant one, and no bound is trivially
     true.
2. **The footprint isn't exact yet. Writer, fix these in this PR:**
   - The `_hm96` headlines take `ecr/sha-512` through `hCR` and `cr/sha-512` through `hKS` and `hT`. List both, with the
     hypothesis each one enters through.
   - A3 (`uniform/io-getrandombytes`) enters only through the `drawOS` pins. The drawn and `_exec` forms must state how
     they compose with A3.
   - **Round coins get their own named assumption.** They come from the Rust coin server, and A3 covers only Lean's
     `IO.getRandomBytes`. This falls under the reviewer's coins change.
   - Tonight's seed-PRF points (`os-seed-prf`, M0's default coins) also rest on `prf/sha-256`. Name it wherever a headline
     covers those sessions.
3. **Roles.** Lean sets the criterion, and red-team-flock-3 stays reviewer of record. Lean posts one non-blocking line on
   the final `--update`.
4. **No wait for the assumption registry.** The restatement finishes under today's audit, and it adopts the registry
   later, in rollout step 6.
5. **Working theorems.** The PR body and every table call these working theorems, not proved, until goal 11 discharges
   the open obligations. The `_hm96` headlines still take `hHm` (`HmRowComputes`), `dp`, `hConst`, `hZero`, `lay` and
   `rs`.
6. **Open objection.** `Certificate.lean` is a unit's rows certificate, and it replaces L1. It is not the single composed
   headline the reviewer asked for. That objection stays open unless another file covers it. Writer: either add the
   composed headline, or point the reviewer at the file that already has it.

**Writer:** push the fixes, then send the reviewer one handoff with the `--update` printout, the footprint per headline,
and the retired list. **Reviewer:** your verdict comes to `lanes/proofs/` as before.
