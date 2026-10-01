---
id: 20261001T0445Z-draft-from-proofs-lean-restate-pr-body-4fc658ce
campaign: verity
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: proofs-lean-restate (bc-3b607340)
---

# Draft PR body for `cursor/proofs-lean-restate-95d4` at `4fc658ce` (base `main`, draft)

to: proofs (bc-8416bc72). I can't open the PR from this VM: `gh` is read-only here and there is no PR tool. Open it as a
draft with base `main`, title and body below, or have the environment do it. The branch is pushed. Everything under the
rule is the body.

**Title:** Flock soundness: SHA-512's two collision-resistance forms, the end-to-end theorems on the statement's rows,
and the headline `Prog.flock_headline`

---

Restates C-Flock's soundness theorems over Daniel's decisions:
- the two collision-resistance forms are `SHA512CRStrict` (`cr/sha-512`) and `SHA512CRExpected` (`ecr/sha-512`);
- L1 is dropped, and the lowering is generic;
- the headline bounds wrong units of the pinned rows circuit.

Draft: the pin lands only after the statement reviewer's final GRANT on the printout and Daniel's yes.

## What changes

- **Assumptions.** `SHA512ExpectedTimeCR` becomes `SHA512CRExpected`, and `SHA512CRStrict` is new.
  - Each is stated per finder and per prover.
  - `Teeth.lean` proves both hold for an injective hash and fail for a constant one.
  - A6, `uniform/flock-coin-server` (the coin server's round coins), is registered in `verity.claims`, with a test. This
    touches core.
- **Strict terms.** The compiled, knowledge and `δ_tree` terms are stated under `SHA512CRStrict` (`StrictCR.lean`).
  - The `_hm96` bounds add `δ_tree`, through the serving roots' rewinding `tr`.
  - `TreeRewind.ofNever` builds `tr` from `hExec` at `δ_tree = 0`.
  - The budgets `qF, qT ≥ 2t′ + 2v` and `qS ≥ t′ + v` are stated as numeric conditions Lean doesn't check.
- **L1 dropped.** The end-to-end theorems are on the circuit of the statement's rows (`Prog.circuit`, `ProgPlaces`).
  - What a correct unit computes is its certificate's: `RowsCert` and `IsRowsUnit.computes_of_cert`.
- **The headline.** `Prog.flock_headline` (`Headline.lean`) is the count curve on the rows' circuit, with:
  - SHA-512 as the session's hash and the rows';
  - the live draw `Law.execOS`, composed with A3.
- **Legacy.**
  - Retired: the Blake3 row leaf's setup lemmas in `Refine/Setup.lean`, that is `Refine.setup_wf` and its pin, and
    `blake3_regions_wf`, `parse_checkLayout`, `checkLayout_slots`, `slot_le` and `pin_ok`.
  - Deferred, each with its owner and the dependents that forced it, in `assumptions/e2e-checklist.md`:
    - `Refine/Live.lean`: `LiveSim.lean` (`live_le`, pinned) and `LiveCompiled.lean` (`live_le_tableC`, pinned) are
      built on it.
    - The frame-v3 tags in `Flock/Tags.lean`:
      - seven agreement sets in `vectors.json` name them, and `lean-agreement` replays them against the builds
        `upstream.json` pins;
      - `circuitEb90718f` is defined from `circuit631567f7`;
      - `PROTOCOL.md` §16.5 describes them.
    - `verity/flock-tables` in Rust, Python and the README (flock-circuit), and M0's seed coins
      (proofs-verify-overlap).
  - The headline isn't cited until these are retired.

## Footprints

Each theorem is proved under the assumptions listed, every hypothesis with its kind. A6 (`uniform/flock-coin-server`,
platform: the coin server's OS randomness) is in every footprint. It is not a hypothesis: the model embodies it, since
the session's game (model) draws each round's coins uniform after the prover's message, against any prover strategy.
It covers per-round OS coins only, so M0's seed-derived coins are outside every statement here.

**`Prog.flock_headline`.** Bound: `miss(K) + ksAvgStrict + δ_link + δ_tree`.

| Hypothesis | Kind |
|---|---|
| `hKS`, `hT`: `SHA512CRStrict` (`cr/sha-512`), at budgets `qF`, `qS`, `qT` | hardness |
| `hCR`: `SHA512CRExpected` (`ecr/sha-512`) | hardness |
| `hA3`: A3 (`uniform/io-getrandombytes`) | platform |
| A6, through the model | platform |
| the session's game | model |
| `pp.placed` (W6), `pp.aliased` (`Layout.Aliased`) | intended to prove |
| `hHm` (`HmRowComputes`) | intended to prove |
| `lay`, `rs` (the layout's facts) | intended to prove |
| `tr` (the serving roots' rewinding) | intended to prove |
| `hConst`, `hZero` | intended to prove |
| `hks`, `hS`, `hk`, `hRw`, `hM`, `hρ`, `hr`, `ht` | numeric condition |
| `qF, qT ≥ 2t′ + 2v`, `qS ≥ t′ + v` | numeric condition (unchecked by Lean) |

**`Binding.flock_e2e_count_hm96`.** Bound: `miss_L(K) + ksAvgStrict + δ_link + δ_tree`, at any law `L`.
- hardness: `hKS`, `hT` (`cr/sha-512`, of the session's hash `H`), `hCR` (`ecr/sha-512`);
- platform: A6 only, through the model; no A3, since it holds at every law;
- model: the session's game;
- intended to prove: `dp` (the derived column placements), `hHm`, `lay`, `rs`, `tr`, `hConst`, `hZero`;
- numeric conditions: `hk`, `hRw`, `hM`, `hρ`, `hr`, `ht`, and the budgets.

**`Binding.flock_e2e_drawn_hm96`.** Bound: `ksAvgStrict + δ_link + δ_tree`, at any law, so it holds at the live draw.
Footprint: as `flock_e2e_count_hm96`.

**`Binding.flock_e2e_count_exec_hm96`.** Bound: `Law.stratified`'s `miss(K) + ksAvgStrict + δ_link + δ_tree` at
`Law.execStratified`. Its outcomes are uniform byte tapes, so there is no A3. Footprint: as `flock_e2e_count_hm96`, plus
the numeric conditions `hks` and `hS`.

**`Binding.flock_e2e_drawn_exec_hm96`.** Bound: `ksAvgStrict + δ_link + δ_tree` at `Law.execStratified`, with no A3.
Footprint: as `flock_e2e_count_hm96`.

## The record

- `lean-audit.json`:
  - `pin FlockSoundness.Prog.flock_headline: new`;
  - `pin FlockSoundness.Refine.setup_wf: removed`;
  - eight changed pins: the four `Partition.flock_e2e_*` by the L1 drop, and the four `Binding.flock_e2e_*_hm96` by
    L1 and the strict terms;
  - the definitions they read (the rename, `LinkCR`, `StrictCR`, `Rewinding.Off`, `ProgPlaces`, `Prog.rows`,
    `digInhabited`).
- **Statement reviewer:** red-team-flock-3 (bc-f0bc7e75). The printout is `art:e0808a65`, from run
  `r20261001-042646-dfd1` (`art:ad5e9e4c`), sent as
  `note:20261001T0439Z-handoff-from-proofs-lean-restate-printout-4fc658ce`. The final GRANT is pending, and so is
  Daniel's yes.
- **Audit at `7c80f77e`, with the record `4fc658ce` commits:** PASS with kernel replay. 12,442 declarations in 187
  modules; only `propext`, `Classical.choice` and `Quot.sound`; 192 pinned theorems; no `sorry`, `axiom` or
  `native_decide`.
- **Cited but not pinned:** the `StrictCR` theorems, `Teeth.*`, `computes_of_cert`, and `Prog.flock_e2e_count` and
  `_drawn`. Left to a follow-up record unless the reviewer folds them in.

## Checks

- Lean: the soundness package builds on the pod (`EXIT 0`), and the audit passes (above).
- `packages/verity/tests/claims` (5 passed) and `tests/test_lean_packages.py` (6 passed) pass on the branch.
- No circuit changed, so there is no `circuit-check` report.
- `check` is not recorded yet. The change touches `backends/flock/`, so it needs `lean-agreement`:
  `uv run python tools/check/check.py --record --on POD`.
