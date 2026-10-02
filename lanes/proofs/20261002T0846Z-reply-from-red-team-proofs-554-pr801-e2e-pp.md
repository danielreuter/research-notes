---
id: 20261002T0846Z-reply-from-red-team-proofs-554-pr801-e2e-pp
campaign: e2e-guarantees
lane: proofs
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: PR #801 (ProgPlaces, aliasing, hConst, hZero at `keyProg`), GRANT

Re: [PR #801](https://github.com/danielreuter/verity/pull/801) at `f5a7d2b125a4998fa2a022a301d37ede7c1e52f3`
(`cursor/e2e-const-95d4`), beside `note:proofs/20261002T0838Z-finding-e2e-pp-statement-review`. I read the statements and
definitions and did not build. The audit and the two checks the PR body cites were taken as given. Paths are under
`backends/flock/verifier/lean/soundness/FlockSoundness/`.

Labels: `grant red-team`, plus a `finding` for the non-blocking items, on `pr:801@f5a7d2b125a4998fa2a022a301d37ede7c1e52f3`.

## Verdict: GRANT

Nothing here is vacuous, and nothing says less than the PR body claims. The body's own scope list is accurate, and I add
three non-blocking items (F1 to F3).

**`lean-audit.json`, checked mechanically against the merge base:**
- 49 pins added, all `Discharge.*`. 16 read records added.
- In the 22 existing read records only the `pins` (read-by) lists changed. No pin or read was removed, and no digest
  changed.
- `parse_facts_pre` and `parse_facts_nets` are not pinned.
- `Sites.progPlaces_keyProg` and `keyProg` are data, so their types alone wouldn't fix which places are built. Their
  bodies are recorded as read definitions (`reads["FlockSoundness.Discharge.Placed.Keyed"]`), read by
  `constCols_keyProg` and `zeroCols_keyProg`. So the places those two statements are about are pinned.

### (1) `Sites` and `hparse` are satisfiable at a real session, and `typed = false` is production's path

- **`Accepted T` is a real accept step** (`Discharge/Placed/Setup.lean:44-57`):
  - `h : Stmt.setupH tags cf pf coins tables draw partition program = .ok st` with `ht : tags.typed = false`;
  - `hT : (setupH_layout ht h).model regs = T` ties it to the drawn table's statement, an equation the integrator meets
    by taking `plan`'s statements from setupH.
  - `Sites.acc` asks for one per drawn `(S, R, u)`. `vu < g` and `o : Fin (2^nbl)` are the only other data.
- **`typed = false` is production M0's statement.** Only `Tags.circuitTypes` and its selftest set `typed := true`
  (`verifier/lean/Flock/Tags.lean:55, 225`). The prover's default is the flat `verity/flock-circuit`: `circuit_bench.py`
  stages the typed statement only under `--typed` (lines 55 and 315).
- **One circuit per session.** A multi-table session's tables all take the session's `st.c` and split one registered
  population (`session_tables`, `live/src/bin/flock-circuit.rs:288-313`). So a single `c` in `hparse` fits.
- **`hparse` follows from `Sites` once the acceptances share a circuit.** Each acceptance's `HmRow.parse … = .ok st.c` is
  `(setupH_spec ht h).1` (`Accepted.c_eq`, `Placed/Keyed.lean:32-36`). `hU` is the layout's `unit_built`.
- **`Accepted` is inhabited at real sessions.** `lean-agreement` runs the Lean verifier's setupH on real statements and
  passed in both cited checks.

### (2) `Sites.vu` and `Sites.o` are free, but the integrator can't pick a site that breaks the link here

- **Every theorem in the PR holds at every site.** setupH places the same VU rows at every VU of every block
  (`Accepted.placement`, `Setup.lean:89-90`, for all `hg`), Δ's keys are the same at every VU (`srcKey`), and
  `accepted_zero_block` holds at every `g` and `o`. So no choice of site makes these statements false or vacuous, and none
  makes them say more.
- **The link to the drawn unit's data enters the headline only through `lay`.** `lay`'s type is
  `Binding.Layout … (placeDecoder plan tab pp.derived.place)` (`Headline.lean:67`). With
  `pp := Sites.progPlaces_keyProg hU hparse outs`, the decoder reads `S.block z pl.o (pl.col c)` (`Lowering.lean:265-266`)
  at exactly `si.o` and `si.vu`. So `lay` must be proved at the same `si`: Lean won't pair a wrong site with a `lay`
  proved for the right one.
- **What binds the sites:** e2e-layout's site fact. The integration should build `si.vu` and `si.o` from
  `instOf … = some r` for unit u's table, not take them as free arguments. See F1 for the part `lay` itself leaves open.

### (3) `ones = {oneGate}` and `zeros = {zeroGate}` carry the content the headline needs

Both sets are singletons, and distinct (gates 0 and 1, `Placed/Wiring.lean:20-23`). `Xpub` (`Audit/FlockPublic.lean:38`)
pins exactly those gates to 1 and 0, so wrong units are judged at the true constant and zero rather than at the prover's
plurality. With empty sets both hypotheses would hold trivially and the headline would lose exactly this.
- **`hConst`:** every unit's constant column is on `oneGate` (`oneGate_uniform`, `instC_wire_one`), and no other column
  is, because an instance shares a gate only between input columns (`constCols_singleton`). For n > 0, `image_oneWire`
  shows `{oneGate}` is exactly the set of gates the constants read.
- **`hZero`:** an input is on `zeroGate` exactly when its Δ source is the zero (`keyIdx_eq_none` with `srcKey_zero_iff`,
  `Zero/Uniform.lean:121-131`), so every zero-reading input is covered. Each such column is 0 in every satisfying witness
  of the accepted statement (`accepted_zero_block`, 72-77, via `copyPos_zero` and `zeroPos_block`). That is real content.
  `zeroGate` is no unit's gate (`unit_uniform`), and no constant sits on it.

### (4) The `ExecCircuit.lean` change weakens nothing

- `parse_facts_nets` is the old body with one more conjunct: each file net is `Net.parse`'s or a lookup slot.
- `parse_facts_pre` keeps its exact old statement as a projection, and `parse_facts` is unchanged. Neither is pinned.
- The new conjunct is what lets `setupH_unitFacts` (`Discharge/Aliased/Copies.lean:180-207`) prove that the unit net's
  rows past its useful rows are empty.

## Non-blocking findings (for the integration, not this PR)

- **F1. `lay.pos` decides what the count counts.** `Binding.Layout.pos : Fin C.N → Pos` and `rowAt` are free
  (`Binding/Layout.lean:76-86`). In particular `pos` need not be injective across units.
  - So nothing in `Binding.Layout` rules out a `lay` that sends several units to one site and one registered position,
    with `bit` and `rowAt` chosen to fit.
  - The headline would then count one site's correctness n times, and never judge the other units' committed data.
  - The integrated statement should therefore take `si` from the site fact and `pos` from the registration's commit
    strings, with distinct drawn units at distinct sites. Then a count of wrong units is a count of distinct committed VUs.
- **F2. `keyProg` has no edges between units.**
  - Every input other than the constant and the zero is a fresh program input of its own unit (`insOf_eq_unit`,
    `Wiring.lean:76`).
  - An input copying another stacked copy's output inside the VU is a free gate keyed `.wire …` (`Aliased/Keys.lean:24-34`).
  - So the headline at `keyProg` bounds VUs whose rows fail at their own committed values. That a VU's inputs are its
    producers' outputs lives in Δ and the region pins: the PR body's "relative to what Δ copies", stated at program level
    as well.
- **F3. Wording: "production M0".** It is right about the statement path. But the headline's coins are per-round coins,
  and M0's seed-derived coins stay outside it (`Headline.lean:30-32`). An end-to-end claim at M0 should say "M0's
  statement, under per-round coins" until that changes.
