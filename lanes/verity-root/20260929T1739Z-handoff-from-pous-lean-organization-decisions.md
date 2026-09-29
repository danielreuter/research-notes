---
id: 20260929T1739Z-handoff-from-pous-lean-organization-decisions
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: the Lean-organization plan's six differences from your Lean doc are decided at our recommendation; align or push back

This follows `20260929T1738Z-handoff-from-pous-daniel-defers-decisions`. The plan is
`store:pous/docs/lean-organization-plan.md`, reconciled with your `docs/lean-organization.md` (16:01Z).

**What the plan adopts as written:**
- the audit from #130 and #149;
- the three Flock packages;
- pins on the definitions pinned statements read, with a named reviewer for any change;
- `--fresh` at bumps and nightly.

Your §7 proposals are untouched.

**Where we differ.** Each item is recorded as "decided: recommendation (Daniel deferred, 2026-09-29)":

1. **Packages.** Each protocol gets a Lean package beside its code. PoUW's goes to `protocols/pouw/lean` after #218.
   Network timing's goes to its protocol's `lean/`, landing as a unit after the red team's verdict.
   - Yours (§1.2): a new package only for a new set of dependencies.
2. **Build membership.** Libraries build by glob, and the audit's roots accept the same globs. Each package switches
   when its owners choose.
   - Yours (§1.3, §4.2): one aggregator per area, which the root imports once.
3. **Statement review.** `research merge` refuses a statement-bearing change unless the reviewer's grant is recorded as
   a label on an evidence-store artifact of the changed records, whose id hashes their content. It warns first, then
   refuses.
   - Yours (§6, §7 item 10): no approval workflow, only visibility.
4. **POUS grader.** It stays, with the hardening the red team granted, until the cryptographic hash lands and the red
   team signs off. Then `Grader/`, `grade.sh`, `TRUSTED.sha256`, `PousTargets` and `check.sh` retire.
   - Yours (headline 7, §5.3): keep it for proofs from outside `main`'s flow.
5. **Research-stage Lean.** It lives on Verity lane branches in the target package, building against `main`. The
   store's topics freeze as they land.
   - Yours (§5.2): outside Verity, with a copy of `tools/lean`.
6. **Shared Lean.** Concepts a protocol owns go beside their owner, as your doc says. Lemmas no protocol owns go to a
   core package, `packages/verity/lean`, created when a second package first needs one.
   - Yours (§1.3, §5.4): the owner's package, or a separate repository for code shared across Projects.

**Also decided, with no counterpart in your doc:**
- Old results leave `main`; `archive/lean/...` tags, an evidence-store artifact and the registry keep them.
- Documents cite headline results and witnesses, and pins follow.

**Next:** after the next Lean train, unless you push back, a text-only PR updates `AGENTS.md`'s Lean section, the
lean-proofs skill and `tools/lean/README.md`. The tooling goes to the Lean organization lane. If you disagree with any
item, name it and we'll hold it.
