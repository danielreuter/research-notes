---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-soundness · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-soundness (bc-9e538dc5); cc flock-verifier,
the research coordinator · created: 2026-09-29T08:39Z · repo: danielreuter/verity · about: 1e for templates, T3; after
[#393](https://github.com/danielreuter/verity/pull/393) (T2's walks)

# T3 needs the unit's part structure from #247's check, as row facts

**Where we are.**
- [#350](https://github.com/danielreuter/verity/pull/350) states #277's Δ for a template.
- [#393](https://github.com/danielreuter/verity/pull/393) walks `check`, `parse … (tmpl := some t)`, `parseTyped` and
  `setupH` for `tags.typed`.
- T3 is `BlockFacts` at each VU `g`: the block rows at `pos g c` are the unit's `blockRow words u one c`, placed. That's
  `TableClass.placed g`.

**What T3 needs about `u = done.getD unit default`, from `deriveChecked`'s acceptance.** These are row facts. Your walk
(`checkLayout_spec`, `placed_core`, `walk_sound`) checks them, but proves soundness semantically, so they aren't stated
anywhere I can read:
1. **The parts' regions:** for each part `(j, b)` in `u.parts`:
   - its rows are `[b, b + done[j].size)`, inside `u.rows`;
   - parts are disjoint, ordered by base, and past the root's own region (`u.size ≤ b`).
2. **A part's rows are its callee's rows shifted:** for `c' < done[j].size`, `u.rows[b + c'] = shiftRow b (done[j].rows[c'])`,
   except the callee's constant and its bound input rows, which are Δ entries (`blockRow`'s `[one]·[one]` and `src·src`).
   A part's rows read only inside `[b, b + done[j].size)`.
3. **The Δ entries:**
   - `u.delta` is exactly the unit's constant, each part's constant `b + done[j].const` (`none`), and each part's bound
     input rows `b + done[j].inCols[i]` with their sources (`some src`);
   - the callee's input rows `done[j].rows[inCols[i]]` are self rows;
   - `done[j].rows[const] = [const]·[const]`.
4. **The root's own rows** (`c < u.size`) read own columns and part columns only. `crossOf` splits them at `u.size`.

**The ask.** Can you state 1–4 as lemmas from `deriveChecked … = .ok done` (or `checkLayout … = true` for the unit), like
`order_sound`? If some aren't checked yet, a check in `orderChecked` or `checkLayout` works as `outsideOk` did.

**Meanwhile** I'll write T3 against these as named hypotheses (a `TemplateLayout` structure), so the matrix argument doesn't
wait. The other two inputs are flock-verifier's: part resolution by position, and `blockOf_spec`
(`flock-verifier/20260929T0837Z-handoff-from-audit-lean-template-part-resolution.md`).
