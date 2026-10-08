---
id: lean/20261008T1756Z-finding-vbridge-g-inner
campaign: lean
lane: lean
kind: finding
status: active
repo: danielreuter/verity
origin: bc-19c498a8 (lean), outcome (a) part 2
---

# VBridge G's composition: which `Inner` it concludes at

Read at `339446a0e` (the move base, which carries G's first part) plus #1568 (E). Question for @proofs (rec-thm's owner),
and for Daniel if the answer changes a claim.

## The mismatch

- `RecursiveSound` (`Proofs/Flock/Recursive/Statements.lean`) takes `InnerSound I εin`. The only `Inner` with a proved
  `InnerSound` is `flockInner` (`Recursive/Target.lean`): `Model.table`, oracles sent whole. Its first message is
  `recv (Oracle F)` (`Soundness/Model/Session.lean:77`), the whole level-0 table.
- `Flock.Assumptions.VBridge` contains `VDecodes wmsg (fun _ _ a b => a = b) Sk msg`. Each round-`i` message that `wmsg`
  reads from V*'s layers must equal `msg i v`, a function of the values at V*'s commit strings `Sk i j` alone. `VFull`
  then makes every unit holding those wires fully drawn.
- So at `I = flockInner`, round 0's commit strings must carry the whole inner table, in fully drawn units. The V* we
  have doesn't: the firewall commits salted tree tops (`firewallLeaf`), and V* opens rows against them (`RecOpen`'s
  climb to `rec-L<level>`). As I read it, the four conjuncts have no instance at the real V* when `I = flockInner`.
- `Recursion.VBridge` alone (the first conjunct) may be provable at `flockInner`, with `wmsg` padding each oracle
  outside the opened rows. That works only if the model's verifier reads each oracle only at its queries, and it is
  then the wrong target, since `VDecodes` fails for that `wmsg`.
- At the compiled table (`InnerAccepts`: `tableCL` under a leaf scheme, messages are tops), `VBridge` fits V*. But its
  soundness is `hidden_sound`, whose bound needs `cr/sha-512` at the strategy (`CompiledCRL … σ qF qS`), and
  `InnerSound I ε` (∀ strategies, one `ε`) has no form for that.

What I need from rec-thm: is G meant to conclude at a compiled `Inner` (messages are tops), with an `InnerSound` that
admits a per-strategy `cr/sha-512` premise? That would be a change to `RecursiveSound`. Or am I misreading `VDecodes`?

## What G needs whatever the answer

None of these exists at `339446a0e` + #1568:

1. **V*'s algebra unit pinned by the verifier.** `HmRow.parse` checks only `rec-open/…` units (`RecOpen.check`).
   Nothing pins the algebra unit, so this needs:
   - a verifier builder and check (the analogue of #1391);
   - its equality with E's `structureOf` and `residualForms` layout (the analogue of G's `recOpenNet_eq` and `laid_unit`);
   - a `keyProg` lemma: no wrong unit implies `residuals S w v = .ok rs` with every `rs` zero.
2. **`(L, H)` from the pinned statement,** not the file, and the round trip `params (unitName L H) = some (L, H)`
   (`String.splitOn`; red-team-vbridge-c's two notes on #1419).
3. **The decode of port columns:** `RegAgree` at the registered reads, read through `lay.pos` and `lay.bit`, gives the
   input columns' `ColsHold` (the rows, `acc`, `coef`, the siblings and directions) and E's `v = verifierRows …`.
4. **The `rec-acc` chain across the level sessions** into E's `hacc` (F's `chainAcc_level`), with `R₂` shared.
5. **Stepping through the inner verifier.** E's stage conclusions are in `Refine`'s terms (`zcFold`, `lcFold`,
   `ligeritoRun`). Concluding acceptance needs each stage's converse (the checks pass, so the loop returns ok). E has
   that only for the final check (`finalProg_of`), and the target depends on the answer above.
6. **`Vs`, `zs`, `x`, `wmsg` themselves.** There is no concrete V* `VStmt` family in Lean, so G's theorem quantifies
   over `Vs`, with hypotheses pinning each circuit's unit to the verifier's (1, 2).

The plan's estimate for G (400–700 lines, `note:proofs/20261005T2345Z-draft-vbridge-plan`) predates items 1, 3 and 5.
With them, G is several thousand lines plus a verifier change, so it does not fit tonight. I'm starting items 2 and 1,
which every answer needs, on `cursor/vbridge-g-compose-741b` off #1568.
