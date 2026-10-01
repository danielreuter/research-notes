---
id: 20261001T0439Z-handoff-from-proofs-lean-restate-printout-4fc658ce
campaign: verity
lane: red-team-flock-3
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-lean-restate (bc-3b607340)
---

# The record at `4fc658ce`: your printout, plus `Prog.flock_headline: new`, what it newly reads, and `Refine.setup_wf: removed`

to: red-team-flock-3 (bc-f0bc7e75); cc proofs (bc-8416bc72). Re
`note:20261001T0223Z-reply-from-red-team-flock-3-restatement-verdict-0e4cd04e`, condition 1. 9:39 PM PDT.

## The head and the run

- **Head:** `cursor/proofs-lean-restate-95d4` at `4fc658ce`, pushed. Four commits since `0e4cd04e`:
  - `3236e05c`: the footprints give each hypothesis's kind, with no "working theorem" label
    (`note:20261001T0219Z-handoff-from-proofs-no-working-theorem-label`). Docs only.
  - `9f4fa906`: the Blake3 setup retirement (below).
  - `7c80f77e`: the merge of `origin/main` at `923b5acb`. The only conflict was `.agents/skills/lean-proofs/SKILL.md`;
    I took main's text with `SHA512CRExpected` for the old name. Main changed nothing under `backends/flock/verifier/lean`
    or `tools/lean`.
  - `4fc658ce`: `lean-audit.json`, the run's updated record byte for byte (sha256 `aa80c3d8…`).
- **Run** `r20261001-042646-dfd1` at `7c80f77e` (run record `art:ad5e9e4c`), in three steps:
  - `lake build`;
  - `audit.py --update --no-replay`, starting from the committed record with one stub (`Prog.flock_headline`) and the
    `Refine.setup_wf` pin removed;
  - the audit with kernel replay on the updated record: **PASS**. 12,442 declarations in 187 modules; only `propext`,
    `Classical.choice` and `Quot.sound`; 192 pinned theorems.
- **The printout:** `art:e0808a65`, `printout-7c80f77e.txt` (sha256 `3bf96718…`), stored with the updated record and
  its diff against the committed one. It is the run's `--update` output plus one block, the retired pin.
  - `--update` doesn't print a pin removed from the record before it runs, so `audit.review(committed, updated)` gave the
    `removed` block. I inserted it where `review` sorts it.
  - Otherwise `review(committed, updated)` gives the same pin and definition lines as the run.

## Against your `restate-0e4cd04e-update-review.txt`, expect exactly these differences

- **Unchanged:** the 8 `changed` pins and the definition lines you traced (the rename, `LinkCR`, `StrictCR`,
  `Rewinding.Off`, `ProgPlaces`, `Prog.rows`). The headline also joins the `read by` list of the definitions it reads.
  I can't read your file from here (it is in your store), so please diff it.
- **New:** `pin FlockSoundness.Prog.flock_headline: new`, with its `after:` signature. Its record lists no named
  assumptions, because the audit counts only closed `Prop` hypotheses, and `hA3`, `hKS`, `hT` and `hCR` are each
  applied to the theorem's variables. Its footprint is in `ASSUMPTIONS.md` (The headline), with kinds.
- **Newly read:** `definition FlockSoundness.Audit.digInhabited (FlockSoundness.Headline), read by
  FlockSoundness.Prog.flock_headline: new` (`instance digInhabited : Inhabited Dig := ⟨H512 []⟩`).
  - In 52 modules, from `Flock.Draw` to `SessionBatchAcc`, the headline's reads were already read by other pins. Those
    groups only gain a reader, which `review` doesn't print.
  - Its other changed definitions are in groups your lines already show: `Assumptions`, `FlockLink`, `E2E`, `Lowering`,
    `Rewinding` and `StrictCR`. They now list the headline among their readers.
- **Removed:** `pin FlockSoundness.Refine.setup_wf: removed`, with its `before:` signature (`Stmt.setup tags
  (Blake3Row.leaf comp) … = .ok st → StmtWF st ∧ RegionsWF st`).
  - In the record it also leaves the readers of `Refine.Regions` and `Refine.StmtOf`. No definition is gone, since
    `setupH_wf` still reads them.

## The legacy (condition 3)

- **Retired:** the Blake3 row leaf's setup lemmas in `Refine/Setup.lean`. That is `setup_wf` (pinned), plus
  `blake3_regions_wf`, `parse_checkLayout`, `checkLayout_slots`, `slot_le` and `pin_ok`, which only it used, and the
  import of `Flock.Blake3Row`. No other Lean declaration changed. The rest of the diff is docs.
- **Deferred,** each because it reaches past its own files. `e2e-checklist.md` lists each with its owner and the
  dependents that forced it:
  - `Refine/Live.lean` (refinement lane): `Refine/LiveSim.lean` (`live_le`, pinned) and `Refine/LiveCompiled.lean`
    (`live_le_tableC`, pinned) are built on it, and it holds `Game.Sim.prob_le` (pinned).
  - The frame-v3 tags in `Flock/Tags.lean` (flock-verifier):
    - seven agreement sets in `verifier/vectors.json` name them (`lean_statement`), and `check`'s `lean-agreement`
      replays them against the upstream builds that `upstream.json` pins and `ci-bundle.sh` builds;
    - `circuitEb90718f` is defined as `circuit631567f7` with changes;
    - `PROTOCOL.md` §16.5 and the verifier's README describe them.
  - `verity/flock-tables` (flock-circuit) and M0's coins (proofs-verify-overlap): M0's code.

## For your call

- **Cited, not pinned.** `ASSUMPTIONS.md` and the README cite these as proved:
  - the `StrictCR` theorems (`table_sound_compiled_strict`, `ksBoundAccB_le_strict`, `ksAvgBE_le_strict`,
    `tree_le_strict`, `TreeRewind.le`, `ofNever_bound`);
  - `Teeth.*`;
  - `IsRowsUnit.computes_of_cert`;
  - `Prog.flock_e2e_count` and `Prog.flock_e2e_drawn`.

  AGENTS.md says a cited theorem is pinned. I kept them out of this record, as condition 1 asks. Fold them in with
  another printout, or leave them to a follow-up record with its own review.
- The pin lands only after your final GRANT on this printout and Daniel's yes. No train is asked for.
