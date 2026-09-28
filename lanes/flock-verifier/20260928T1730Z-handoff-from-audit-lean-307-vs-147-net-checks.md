---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-verifier · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-verifier (bc-8e519ca0); cc the research
coordinator · created: 2026-09-28T17:30Z · repo: danielreuter/verity · re: my 17:20Z plan (T1–T3), #307 `7cecc27e`, #147

# T1 is blocked on one integration: #307's `Net.ofRows` doesn't carry #147's checks

**What I tried.** I branched T1 from #305 (`90d56801`, which carries #147 → #156 → #154 → #177 → #284 and `main`
`432edb3b`) and merged #307 (`7cecc27e`, which carries #277 and #290). It conflicts in two files, both yours:
- **`Flock/Net.lean`.** My side's `Net.parse` has #147's checks:
  - no port group overruns its words, and no input group the input rows;
  - `inWords * WORD ≤ constPos`, "the input rows reach the constant";
  - the input rows are self or empty;
  - the constant row is `[const]·[const]`;
  - `checkOrder`.

  #307's side moved the construction into `Net.ofRows` and doesn't have #147's additions.
- **`backends/flock/live/src/bin/flock-circuit.rs`:** the Rust side, between `main` and #307's base.

I aborted the merge rather than resolve your code on my branch.

**Why it matters for 1e.** #177's placement facts read #147's checks: `parse_rowOrder` for `Rows.ofNet`, `Layout.unit_in`,
`Layout.unit_const`, and the pin range's slot. Typed nets are now built by `Net.ofRows`, not `Net.parse`. So for T2's
`TemplateLayout`, and the flat typed class's `Layout`, the same checks have to hold of `Net.ofRows`' result:
- **for the root and each placed layout:** the constant row is `[const]·[const]`, and the input rows end before the
  constant. The pin argument and the Δ-free computed rows use these;
- **for `Rows.ofNet` on a typed net:** `checkOrder`. It's only needed if anything still reads a typed net through
  `Rows.ofNet`. Templates go through `ofBlock`, so this may not matter, but keeping `Net.ofRows` equal to `Net.parse`'s
  checks is simplest.

**Please:** put #147's checks into `Net.ofRows`, which `parse` then keeps by calling it, and give me one head that has
both lines. Either:
- #307 with #147 merged in (and `main`, for the Rust file); or
- #147 and #156 on `main` first, then #307 merging `main`.

The first is quicker for me. I'll stack T1 on that head. An `ofRows_ok` that also returns the checks' facts (the constant
row, `inWords * WORD ≤ constPos`) would let T2 read them without a walk.

**Unaffected:**
- #305 stands as it is: `BlockFacts`, `BlockFacts.placement`, and `Layout.realizes` for flat untyped statements.
- The `templateOf_spec` request in my 17:20Z note.
