---
id: red-team-proofs-1261/20261006T1000Z-finding-pr1330-review
campaign: flock
lane: red-team-proofs-1261
kind: finding
status: final
repo: verity
origin: pr:1330@8fb946c2d9e659ed14581bb02f40f1bada6a94d3
---

# Red team, PR #1330 (B1's fix: one shared registration `R₂` before V*'s sessions): GRANT

Reviewed 3:00 AM PDT, 6 Oct, by red-team-proofs-1261 for the proofs coordinator. The review is of head
`8fb946c2d9e659ed14581bb02f40f1bada6a94d3` of `cursor/rec-acc-reg-95d4`, base #1261 at
`b4784eb8e0167d59e96b738058209edd8ca2567a` (still that branch's head), read in a separate worktree (`/tmp/rt1330`).
File references are relative to `verity/Security/Proofs/Flock/Recursive/` unless they start with `verity/`. It closes B1
of note:red-team-proofs-1261/20261006T0810Z-finding-pr1261-review; the design is
note:rec-thm/20261006T0848Z-finding-rec-acc-reg.

**Verdict: GRANT.** B1 is closed in the model, the "no new term" argument holds, the new hypotheses are satisfiable
and don't make `RecursiveSound` vacuous, the lock is the audit's byte for byte with only `RecursiveSound`'s reads
changed, and `RecursiveZK` needs no restatement. No blocking finding. Four non-blocking notes follow, N1 being the one
piece G must act on.

## What I ran

No Lean of my own. The change is eight declarations, each a wrapper (`outerV` is `.send Reg₂` then `sessions`;
`prob_outerV` is `prob_map`; `outerV_le` and `outerV_stage_le` are `sessions_le` and `sessions_stage_le` at `s.1`), plus
`∀ R₂` added to `Recursion.VBridge`, `VCommits` and `_hr`. I read the diff `b4784eb8e..8fb946c2d`, the definitions the
statement reads at the head (`ZkOuter`, `Good`, `RegAgree`, `bound`, `CR`, `off_le`, `Registered.Reads`,
`regTermZC`, `RegCRZC`, `regOpenZ`, `OwnReads`, `Finder.CR`, `SHA512CRStrict`), and the author's audit run
`r20261006-084941-c067` (record art:857db6da9ff1a1f2706a7290d356a1b95ba91fb4c8d3488345fa27c2541fb496, fetched with
`research data fetch`: `review.txt`, both `report.json`, both `build.log`, the lock, `stdout.log`). The kernel replay
is still `check`'s.

## Check 1: B1 is closed in the model. Yes

`zs : Reg → L.Ω → List (Cm × I.Coin) → Reg₂ → (j : Fin S) → (Vs j).Outer Reg'`, and `outerV` (`Flock.lean:400`) sends
one `R₂` before `sessions (zs R₂)`, so every session's `own`, `rd` and `hown` are fields of `zs R ω t R₂ j` at the same
`R₂`. `rd.port` is per commit string (`Registered/Defs.lean:56`) and `own` is an array of ports, so one session can hold
the hidden circuit's rows, `R₂`'s `rec-acc` rows (a level's `p` and `p + 1`, the algebra's first and last), each level's
`rec-rows-L<level>`, and the verifier's own values, side by side. `Good` (`Flock.lean:167`) asks `RegAgree` at every unit
of every session: each wire at a registered read carries `rd.wv`'s bit. When every session's `rd` records `R₂`'s rows,
`Good` at every session makes every level and the algebra read the same chain, which ties the sums. That the concrete
`zs` records them is piece G's (check 3).

## Check 2: the "no new term" argument. It holds; no gap in the model

- `regTermZC` (`ZkReg/RegLink.lean:73`) is `(Σ_c π_c)/(1 − ρ)·(qW²/2^513 + k/(eR_w))` over every commit string
  `c : vb.Pos`, and takes `vb`, `L`, `k`, `Rw`, `ρ`, `qW`, not `wo` or `rd`. More registered reads add no summand. Its
  finders (`regFinderZC`) are one trial per commit string, as before.
- The off-leaf term is one finder per session, `StrictCR.oneRun` of that session outputting one pair (`Reads.pick` at
  `offAt`), at `qR²/2^513`.
- **No cross-session union.** The reference opening each session binds to is `rd`'s, a function of `R₂` that the finder
  holds, not another session's run. If two sessions read different values at one `R₂` row, at least one of them
  disagrees with `rd` there. That session then has a bad unit: `regWrongZ` at the registrant's leaf, or `offUnits` off
  it. Its own `bound` prices that unit, and `sumS` sums the sessions (`prob_seqC_exists_le`). A two-session finder would
  be needed only if the reference were another session's opening. It isn't.
- **The fork finders.** `R₂` doesn't enter round `i`'s binding. `forkAt` rewinds after round `i`'s gateway commitment,
  at its coin, and each branch sends its own `R₂`. `VCommits` fixes the registered digest at `Sk i j` to `cmt j e.1` at every `R₂`, so
  the two openings that collide are of the same commitment whatever the branches' `R₂`.

N2 is a budget note, not a term.

## Check 3: `VBridge` over every `R₂` is satisfiable, and nothing makes `RecursiveSound` vacuous. Yes

**Not vacuous.** At `Reg₂ := Unit` and `zs` constant in `R₂`, each changed hypothesis is #1261's. `_hr`'s `∀ R₂`,
`Recursion.VBridge`'s `∀ R₂` and `VCommits`'s `∀ R₂` range over one point, and `trialV` is `trialS` at `sessOf`. So the
hypotheses are jointly satisfiable wherever #1261's were (check 4 of the #1261 review). No hypothesis was added; three
gained a quantifier over a type the instance chooses.

**What piece G must prove for V\* as staged**, at every `R ω t R₂`:

1. **`R₂` opens the roots `own` holds (N1).** `Reads.committed` requires the registrant's opening to open `port p` at
   `readAt p` at every registered read.
2. **`own` holds only `R₂`'s roots, not its rows.** The session's inputs, `dj`, `y₀` and public file don't read `R₂`'s
   private parts. Then `VCommits` and `_hr` hold at every `R₂` as they did, and the model's acceptance event is the real
   verifier's.
3. **Every session's `rd` records the same chain.** Every level's `rd` records `R₂`'s `rec-acc` rows at that level's
   `p` and `p + 1`, and its `rec-rows-L<level>`. The algebra's `rd` records a rep's first and last rows. `coef` and `dirs` are
   recorded as verifier-registered (B2, on `cursor/vstar-register-coef-95d4`, at `96142e0b` on origin).
4. **`hown`.** Each `rd` lines up with the verifier's reads file at every `R₂`.
5. **The bridge, for every chain `R₂`, since `R₂` is the prover's.** Suppose every session accepts and is `Good`. Then
   every level's step is correct on `R₂`'s rows (positions `0 .. N - 1` of one chain) and the algebra's checks on a
   rep's first and last rows hold, so the chain telescopes to the inner verifier's sum and the inner verifier accepts
   on `x R ω`.

Each is a fact about V\*'s circuits and the concrete `zs`. None is false for a V\* that registers `rec-acc` this way.

## Check 4: the lock. Yes, as the body says

- `sha256(verity/Security/lean-audit.json)` at `8fb946c2d` is `d7910c233b9aceb5…`. That equals the run's
  `out/audit-verity_Security/lean-audit.json`. The run's source is `f6ab493cb`, and `f6ab493cb..8fb946c2d` touches only
  the lock.
- Against `b4784eb8e`, 4 of 541 `reads` modules changed (`Proofs.Flock.Recursive.Flock` and `.Stage`, and
  `Specs.Flock.Assumptions.Recursive` and `Specs.Flock.Guarantees.Recursive`). In them, 4 definitions changed
  (`Flock.Assumptions.VBridge`, `Flock.Guarantees.RecursiveSound`, `Recursion.VBridge`, `Recursion.VCommits`) and 5 are
  new (`AcceptsV`, `outerV`, `sessOf`, `sumV`, `trialV`). The hashes match the body's.
- `review.txt` lists exactly those nine, each "read by Flock.SecurityProofs.RecursiveSound", and none read by
  `RecursiveZK`.
- Unchanged: `Flock.Guarantees.RecursiveZK` at `68bb5616`, both `guarantees` records (type hashes `0643eccd` and
  `444c0683`), every module's guarantees list, and every other top-level key. `Specs.Flock.Guarantees.Recursive`'s
  module digest moved, and both guarantees read that module, but only because `RecursiveSound` is defined there.
- Run `r20261006-084941-c067` (`research inspect`) ran on vy-nebius-1 for 2628 s at tree `f6ab493cb`.
  - `verity/Security`: PASS. 6873 declarations in 217 modules, axioms `propext`, `Classical.choice` and `Quot.sound`.
  - `verity/Security/Proofs`: 891 modules and 58046 declarations (455 + 13513 + 287 + 287 + 43504), the same three
    axioms, `escapes: []`. Its build log has 0 errors, and the five changed modules built with no warning. The lane's only
    warnings are #1261's `if_pos` and `if_neg` deprecations in `ZkReg/Off.lean`.
  - The run's rc=1 is the Proofs package's one failure: the `Proofs.Warden.DifftestMain` `generate` refusal under the
    `--cwd clone` shim, as in #1261. It isn't this branch's.
- The diff adds no `instance`, `attribute`, `axiom`, `sorry`, `opaque` or `implemented_by`.

## Check 5: `RecursiveZK` needn't be restated. The body's reason holds

`RecursiveZK` quantifies over an abstract `view : Ωa → (Fin nh → ByteArray) → Ωp → (Fin nh → Salt) → Ωo → V` and `sim`,
with simulability within `εo` as its premise. It never mentions `zs`, `sessions` or `outerV`, at #1261 or here. `R₂`'s
root is a function of the inner proof (`p`), the auditor's coins (`a`) and the outer salts (`Ωo`), so a `view` that
includes it is an instance. N3 is what that premise now has to cover.

## Non-blocking notes

- **N1 (for piece G): `R₂`'s roots must be derived from its rows, or `Reg₂` restricted to consistent registrations.**
  `Reads.committed` asks the registrant's opening to open the root `own` holds. Suppose `Reg₂` carries the root as a
  free field. Then at an `R₂` whose root its rows don't open, `rd` has to leave the `rec-acc` reads out. `Good` then
  doesn't tie them, and `VBridge` is false at that `R₂`, which is B1's forged-sum attack again. Take
  `Reg₂ := rows × salts`, with the root computed (or a subtype). The body says "`R₂` in the model is the prover's whole
  registration (rows, salts and paths)" but not that the root is computed from it. That would be one line in Limits or
  in the note to piece G.
- **N2: honest budgets count `R₂`'s hashing.** The bound's form is unchanged, and Lean checks no budget
  (`Finder.CR`'s docstring). The fork finder of round `i` (`q i`) builds `R₂`'s tree in each branch. The off-leaf finder
  (`qR`) checks leaves across the registered reads, now including `R₂`'s, to find an off-leaf one. The honest real
  prover already did that work in #1261's world, inside its sessions, so an honest `q i` there already counted it. Nothing
  is missing; whoever states the budgets counts it.
- **N3: `RecursiveZK`'s `εo` now covers `R₂`.** Its explicit `nh · 2^-193` is the gateway's `nh` commitments only.
  `R₂`'s root reveals hm96 leaves of the running sums, which depend on the inner witness. Their hiding (fresh salts in
  `Ωo`, `hash-derived-key` per leaf) belongs inside `εo` for whoever discharges the premise. Alternatively, `R₂`'s
  values could be among the `msgs`.
- **N4 (inherited): `R₂` carries the registrant's opening, as `R` and `R'` do.** The theorem covers provers whose
  registration is a full opening, and its finders hold that opening as advice. This is the same convention as #1261's,
  and isn't new here.

## Label

`grant=red-team` on `pr:1330@8fb946c2d9e659ed14581bb02f40f1bada6a94d3`, by red-team-proofs-1261, ref this note, written
2026-10-06T10:02:01Z. `research data labels … --key grant --remote` shows it "on both", local and remote.
