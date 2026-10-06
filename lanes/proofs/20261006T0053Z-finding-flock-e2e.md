---
id: proofs/20261006T0053Z-finding-flock-e2e
campaign: proofs
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: bc-4d899653-f858-54e9-aaca-4cbcd1abed8d (flock-e2e, for the proofs coordinator bc-8416bc72)
---

# C-Flock's one-stage audit end to end, as one theorem: the count curve, with δ in closed form

Daniel asked this through top on Slack at 4:07 PM PDT on 5 Oct: C-Flock's whole one-stage audit guarantee as one theorem,
in the form of PoUW's `EndToEnd`. It is `Flock.SecurityProofs.EndToEnd : Flock.Guarantees.EndToEnd` on
`cursor/flock-e2e-95d4` (`bcd2b1bf9`, on `b87eeef64`). Its audit passed without the kernel replay: `audit.py --build
--no-replay --no-runs --update` on `cc76e23a9`, run `r20261006-001047-00a2` on vy-nebius-1, from 5:11 to 5:51 PM PDT.

## What it says

The prover registers `R`. The verifier draws a uniform `kd`-subset of the `n` proof units from its operating system's bytes
(`Law.execOS src (.subset kd) n`). One `--zk` session of `J = nTab I` tables proves the drawn units, and
`flock-verify verify --zk --session-tables J` reads the session's record. For every live prover,

  Pr[flock-verify accepts ∧ at least K₀ units wrong] ≤ C(n − K₀, kd)/C(n, kd) + ksAvgStrictZ + δ_link,

with δ_link = Q_s/(1 − ρ)·(2t'(1 + k)/2^256 + 1/(eM) + k/(eR_w)) written out. A unit is wrong when its committed outputs
differ from its gates applied to its committed inputs, in the transcript fixed at registration (`XplurZC`), for the key
program of the circuit the verifier parses.

Named hypotheses: A3 `UniformRandomBytes`; `live-verifier` `Zk.RecordCustodyZKJ` (A6 modeled); `cr/sha-512` through
`TableCRZ` at budgets `qF`, `qS`; `ecr/sha-512` (A2) through `LinkCRZC`. The last is new at this level: without it
`linkBoundZC` is `⊤`, so the closed form needs it. Also new is `K₀ ≤ n`, which `Law.subset_miss` needs.

## What carries it

`zk_session_soundJ_custody` (`Composed/CustodyJ`) carries the bound. Inside it, `zk_headline_exec_tables` maps flock-verify's
acceptance to the compiled model, and `zk_flock_countC` gives the count curve, from `jointZC_ksBound` (on
`session_knowledge_sound_accZ`) and `zk_linkSoundC`. `Tables.execOS_subset_miss_le` covers A3, and `ksAvgZC_le_strict`
covers `cr/sha-512`. On top of that, `Audit.Law.subset_miss` gives the binomial term, and `linkBoundZC` unfolded at A2
gives δ_link. The proof is three lines. `session_knowledge_soundL` is the non-`--zk` analogue and is not on this path.

## Where it stops short of "the verdict is the program's output"

1. It is the count curve over all `n` units, not "the drawn units are correct up to ε_ks + δ_link". That form is proved
   only in the model (`Audit.audit_drawn`). The executable headline carries an event `Q : Prop` that cannot depend on
   the draw, so the drawn form needs a draw-preserving `execRefinesZK_tables`. That is a large lemma, not stated.
2. "Wrong" is relative to the committed inputs, not the program's actual inputs.
3. The units are the key program of the parsed circuit, not the IR Definition: that needs `RowsCert`, which is not
   composed here.
4. One mode only: `--zk`, untyped, public outputs, the subset law. The hidden-output (`ZkHidden`), registered-read
   (`ZkReg`) and zero-knowledge (`zk_session_composed`) theorems are not folded in.
5. The record's custody is an assumption. The hash assumptions are about this prover's finders, at budgets Lean does
   not check. Fiat–Shamir is out of scope.

## For flock-specs

The spec module imports `Proofs.Flock.Soundness.Discharge.Composed.CustodyJ`. It also uses four theorems as proof terms
inside the statement: `decodesOnZKJ_of_runsOnZCJ`, `runsZCJ_live`, `rsZJ_computes` and `drawOkZKJ_of_file`. Three policy
entries keep it out of `Specs`' build: `exempt`, `meaning` and `reads_exempt` for `Specs.Flock.Guarantees.EndToEnd`.

## Process

* The shared `/workspace` checkout changed branch under this lane at 23:17Z. My first commit landed on
  `cursor/rec-thm-95d4`, on top of a commit by one-stage-layout. I cherry-picked it to my branch and removed it from
  rec-thm's branch before rec-thm pushed. Origin's `cursor/rec-thm-95d4` (`05298f673`) is clean. From then on I worked
  only in my own worktree.
* The records fast path was refused on vy-nebius-1: its lean-slots lists no `build` pool
  (`note:proofs/20261006T0025Z-friction-records-fast-path-no-build-pool`). Instead I ran a cold audit in a clone, which
  took 40 minutes and held the node's one `audit` slot.

## Stacked steps (approved 5 Oct, after #1257)

### Step B plan: the draw-tracking lemma (6:36 PM PDT, 5 Oct)

The lemma, in a new `Composed/DrawnJ.lean`, for any event `E` on the draw:

  execRefinesZK_tables_drawn hdec τ E :
    prob (fun o => LiveAcceptsZK I o ∧ E o.2.1) (auditLive L Reg (liveOfZJ dg planZ N wr)) τ ≤
      prob (fun o => o.1 = true ∧ E o.2) (audit L Reg (batchedSessionZC A Hs planZ)) (simZJ … hdec τ)

Both audits' outcomes carry the draw, and `execRefinesZK_tables` is a sum over the law's draws of one inequality per
draw. At each draw `E` is constant, so the same proof goes through with `prob_and_const`. On top of it:
* `zk_flock_drawnC_reg`: `extraction_audit_drawn` at `analysisZCReg`, so
  Pr[accepts ∧ some drawn unit in `wrongRegZ`] ≤ `ksAvgZC` + `linkBoundZC`;
* `zk_session_soundJ_custody_drawn_reg`: the same at flock-verify's acceptance, with `ksAvgStrictZ` in place of
  `ksAvgZC`. It needs no A3, because the bound has no miss term;
* `Flock.Guarantees.EndToEndDrawn` and its proof, with δ_link in closed form under A2.

Size: about step A's. It is one refinement proof of about 40 lines, copied from `execRefinesZK_tables`, plus a few lines
for each of the other three. It is not larger than A.

### Checkpoints

* Step A (7:25 PM PDT, 5 Oct): `cursor/flock-e2e-inputs-95d4` at `cb937c063`, audit `r20261006-013404-2ff9` PASS
  (`--no-replay --no-runs`); `EndToEnd` restated in place, "wrong" = `wrongRegZ` against the public file; changed record,
  needs a statement reviewer. Gap 3 is not cheap (per-circuit `RowsCert`, constant-1 column only up to a collision); it
  stays open. Steps C (hidden outputs, registered reads) and D (zero-knowledge half) are written and type-check locally.
* Step B (9:05 PM PDT, 5 Oct): `cursor/flock-e2e-drawn-95d4` at `5aa4c94e2`, audit `r20261006-030514-32be` PASS
  (`--no-replay --no-runs`); new guarantee `EndToEndDrawn` (accepts ∧ some drawn unit wrong ≤ ε_ks + δ_link, no A3),
  needs a statement reviewer. The first run (`r20261006-022101-daf3`) failed for an unnamed guarantee; message fix on
  `cursor/lean-audit-pin-hint-ed8d`. C gained drawn-unit siblings for both modes; C's audit `r20261006-035812-e255` is running.
* Step C (10:11 PM PDT, 5 Oct): `cursor/flock-e2e-hidden-95d4` at `04d66d9eb`, audit `r20261006-035812-e255` PASS
  (`--no-replay --no-runs`); new guarantees `EndToEndHidden`, `EndToEndHiddenDrawn`, `EndToEndRegistered`,
  `EndToEndRegisteredDrawn` (gap 4, both events), need a statement reviewer. D rebased on it; D's audit is running.
