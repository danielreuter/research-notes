---
id: red-team-proofs-554/20261002T1412Z-finding-pr828-statement-review
campaign: e2e-guarantees
lane: red-team-proofs-554
kind: finding
status: open
repo: verity
origin: red-team-proofs-554 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# Statement review of PR #828 (`flock_headline_exec`) at d5311b9f4: APPROVE

Named statement reviewer: red-team-proofs-554. Reviewed head: `cursor/e2e-integrate-95d4` at
`d5311b9f43f3f9bf452c160c47811219daa44602`, checked out in a separate worktree. I did not build: every question was
answered from the source, the recorded `lean-audit.json` and the verbatim `audit.py --update` outputs (e2e-integrate's
status file outputs 1–13, e2e-hm's main-trial output, verifier-hm-pin's), which I diffed token by token with a script
rather than by eye.

**Verdict: APPROVE.** No pinned statement got weaker except two coverage narrowings. Both are hypotheses visible in the
theorem (`hs`, `hscope` through `scopeOk`'s definition), and neither excludes M0. Two text items are non-blocking (end of
this note).

## Against main d2b4a6d83 (the main this head merged)

- Soundness package: main has 308 pins and the head has 481. None of main's pins was removed or changed its signature,
  assumptions or `type_hash`. 173 pins are new, 18 of them `Discharge.Integrate.*`.
- Verifier package: main has 17 pins and the head has 25. None of main's changed. The 8 new pins are all `Flock.HmNets.*`.
- Definitions read by main's pins whose hash moved: `ParseFacts` and `CheckFacts` (question 4),
  `Flock.Draw.workTableOfJson` and `Refine.Frame`.
  - `Flock/Draw.lean` and `Refine/Frames.lean` are byte-identical to main.
  - Their read groups grew by generated constants that new pins read: the shared matchers `match_13`, `match_5` and
    `_sparseCasesOn_10`, and `Frame.ctorIdx` (e2e-exec's analysis, `e2e-exec.md`). Benign.

## The six questions

1. **Confirmed.** The 18 pins are exactly the listed names, and each says what the status file says. Sites, Bridge and
   Accepted were read against the "Pins added" text. In `Headline.lean`, `rsAt_computes` is `(rsAt … hpub hs hscope).Computes`,
   built from e2e-hm's `keyedRowsOuts_computes` with `hv1 := Layout.scopeOk_ports hscope` (line 63). The head's records of
   `flock_headline_exec` and `rsAt_computes` equal output 9's "after" blocks verbatim (119 and 8 lines).

2. **Confirmed, with two stated narrowings.**
   - **`hHm` discharged.** Output 4 removes the binders `saltCol` and `hHm : (rsAt … saltCol).Computes`. The salt
     columns become `Discharge.Hm.saltCol` (the `hm96` slots' salts, the only columns at which `hHm` could hold), and the
     binding's proof becomes `rsAt_computes`.
   - **`hdec`: `DecodesAll` → `DecodesOn` at `Law.execOS …`.** This makes the theorem stronger.
     - `decodesOn_of_all` (pinned) turns the old hypothesis into the new one.
     - At that hypothesis, the new conclusion's `simAuditOn` is the old `simAudit`: `simAudit_eq_on` (pinned) proves
       `simAudit h τ = simAuditOn (decodesOn_of_all … h) τ` by `rfl`. The two bodies differ only in
       `hdec ω τ.1` versus `hdec (L.draw ω) τ.1`.
     - So the old statement is an instance of the new one.
   - **`ho`, `h1`, `hpr` → `hscope`.** `scopeOk_spec` (pinned) gives all three back. `scopeOk` checks two more things:
     - `unitLog ≤ 32` narrows nothing. Wherever setupH accepts, `ExecPlacement.unitLog_le` proves it.
     - `portReadsB` is `PortReads` read off the net (`Rows.ofNet_a`/`_b`). Only the direction the headline needs,
       `portReads_of_portReadsB`, is proved.
   - **Narrowing 1: `v1Ports`.** `scopeOk` now requires every port to be `sha512/row/v1` with `bits = 16·words` and
     `0 < chunks`. Sessions with a `sha512/row/v2` (bit-row) port are outside the headline until `hHm` is proved for
     v2 rows (e2e-hm, "Left for v2 rows"). M0 stays covered: e2e-layout's `#eval` at b5613b3dd, with `v1Ports`
     included, prints `v1Ports true` and `scopeOk true` on `rope-head/d64/neox-bf16`.
     - The PR body names the check ("on main it also checks every port is `sha512/row/v1`, `v1Ports`") but not its
       consequence.
     - The theorem's docstring omits `v1Ports`: its `hscope` bullet (Headline.lean:78–79) lists four conditions where
       `scopeOk` checks five, and its Scope paragraph doesn't mention v2 rows. See item T1.
   - **Narrowing 2: `hpt : pub.tables = none` → `hs : I.tags.sharedRows = false`.** This is not "no weaker".
     - `Layout.loadPublic_tables` gives `hs → hpt` (with `hpub`), not the converse.
     - Under `verity/flock-circuit@967b8d06` (`sharedRows := true`, Tags.lean:226), a public file without a
       `shared_rows` header loads with `tables = none` (HmRow.lean:882 `| return none`, :920 `none => pure none`).
     - So the old record covered that tag's per-instance files, and the new one doesn't.
     - It is outside M0 (`Tags.circuit`, `circuit_sharedRows` by `rfl`), and `hs` is stated in the docstring and the
       PR body. See item T2.

3. **Confirmed.** Each of e2e-hm's seven records differs from its "before" by exactly one inserted binder:
   - `hv1 : ∀ p ∈ c.ports.toList, p.v2 = false ∧ p.bits = 16 * p.words ∧ 0 < p.chunks` in `bc_site_col`,
     `bc_site_commit`, `keyedRowsOuts_computes`, `row_bc_flat` and `row_bc_setupH`;
   - `hslots : n ≤ (rowSlots c.ports).2[p]!.size` in `port_commit` and `port_commit_rows`.

   The head's records equal e2e-hm's "after" blocks verbatim, and output 12 repeats the same seven diffs. The headline
   discharges `hv1` with `Layout.scopeOk_ports hscope`. `hslots` is not in `keyedRowsOuts_computes`'s statement, so
   e2e-hm's own proof discharges it.

4. **Confirmed.** `ParseFacts` gains `portWords`, `rowWires` and `rowNets`, all constructed in `parse_facts_nets` from
   the parse itself:
   - `portWords` from `rowPorts_words` on `rowPorts`;
   - `rowWires` from `wires_prefix` on parse's wire check;
   - `rowNets` from the `HmNets.check` bind.

   `CheckFacts` gains `unit_pow2`, from `HmRow.check`'s clause `c.outNet == c.unitNet && !isPow2 ur[0]!.count`
   (HmRow.lean:222, unchanged from main). Neither `parse_facts` nor `check_facts` changed its signature.
   - Note: `rowNets` holds of every parse because this branch adds `HmNets.check c` to the executable `HmRow.parse`
     (verifier-hm-pin). That is a stricter verifier: it refuses `sha512x3`/`hm96` nets other than the generated ones.
     Completeness on honest circuits rests on this head's `check` (`lean-agreement` included), which was queued at
     r20261002-130723-16b5.
   - The typed `ParseFactsT` gains `portWords` and `rowNets` the same way (`parse_facts_tmpl`). No main pin reads it.

5. **Confirmed.**
   - Byte-identical to main d2b4a6d83: `Zero/Delta.lean` (`ZeroPort`), `ExecDelta.lean` (`ShaRowBit`/`HmRowBit`),
     `ExecTyped.lean` (`msgCol`), `Flock/Registered.lean` (`Port`, `.domain`) and `Flock/Tags.lean`.
   - `srcAt`, `srcKey`, `leafSrc`, `cutSrc` and `RowBit` are textually main's. `Keys.lean` differs from main only by
     the two added theorems, and `ExecFlatCopies.lean` only by one `ParseFacts` constructor line in a proof.
   - `Exec.tagsAt`'s text is e2e-exec's (`f679a5349`). Its record moved because main's `Tags` gained `liveOs` (#802,
     between b16313242 and d2b4a6d83). At one table, `tagsAt tags 1 j = tags`.

6. **Confirmed.**
   - `srcAt_leaf` and `srcKey_leaf` (with their docstrings) are byte-identical to e2e-zero's 8752529f1.
   - e2e-zero's `srcAt` and `srcKey` are byte-identical to main d2b4a6d83's, so both theorems are about main's `srcAt`.
   - `srcKey_leaf`'s pin record equals its record at 8752529f1. `srcAt_leaf` is not pinned.

## Text items (non-blocking; no record changes)

- **T1.** Name the `v1Ports` narrowing in two places:
  - the PR body's Scope line, for example: "sessions with a `sha512/row/v2` port are outside it (`v1Ports`), until
    `hHm` is proved for v2 rows";
  - `flock_headline_exec`'s docstring: add "and every port is a `sha512/row/v1` row" to the `hscope` bullet, and the
    same sentence to Scope.

  A docstring edit doesn't change any record, so it can ride the next commit that touches Headline.lean.
- **T2.** Say in the PR body that `hs` is narrower than the earlier `hpt`: the `@967b8d06` tag's per-instance files are
  outside it. The alternative is to take `hpt` back later. `sitesAt_bcSite` needs only that, and it would change the
  record again, so it would need another statement review.
