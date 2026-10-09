---
id: proofs/20261009T1354Z-report-rec-gap-list
campaign: private-circuit
lane: proofs
kind: report
status: open
repo: verity
origin: [agent:bc-4523e674-6edb-56fa-a39c-070b580c35f2]
---


# The recursive audit's one property, and tonight's gap list

For proofs (bc-8416bc72), 9 Oct. No PR opened, closed or reopened; nothing landed.

**Branch** `cursor/rec-gap-list-35f2`, head **`2f4b0235b`**, pushed: 51e875f51 (the five statements and the per-row
binding), with `origin/main` (d8b79946f) and rec-thm's `cursor/rec-compile-gap-2261` (cf682258e, the compile gap)
merged in.

**Shape check result: the property builds and is proved up to rec-thm's two sorrys, but it does not pass the shape
yet.** Run r20261009-122359-50dc (the full audit on vy-nebius-1, at 2f4b0235b) built all 5428 jobs. The audit then
failed on exactly two things:
- the sorry, by design;
- nine shape refusals of `RecursiveAudit`: six in (i), three in (ii) (§5).

Nothing else failed: none of the seven `lemma:` entries in `shape.frozen` drew a complaint, and no other guarantee
changed.

## 1. The property

`Flock.SecurityProofs.RecursiveAudit : Flock.Guarantees.RecursiveAudit`, listed under `guarantees` and under
`shape.properties` with `{"function": ["Flock.ProvedScope.check", "Flock.Zk.verify"], "outcome": "accept"}`: the
verifier of record's verdict on each of V*'s `--zk` sessions (`FlockVerify.lean`'s per-session `Zk.verify`, then
`ProvedScope.check`).

Where it lives: `Security/Proofs/Flock/Recursive/Property.lean` (statement, trusted, namespace `Flock.Guarantees`),
`Premises.lean` (the premise list, `shape.premises`), `Audit.lean` (the proof). Not in `Security/Properties/`: the
statement reads C-Flock's and the recursion's definitions (`ZkOuter`, `VStmt`, `recGame`, `flockInnerCL`, ...), which are
still in the proofs package (reads-exempt until proofs extracts them), and `Properties` can't import `Proofs`. Likewise
the premise list belongs in `Definitions/` and can't go there yet.

It is the conjunction the brief asks for:

- **(i) fork-form soundness at the executable.**
  - The setting: V*'s outer sessions as the verifier of record accepts them (`VerifiesV` = `AcceptsV` and
    `FailClosed.ScopeZ`, i.e. `Zk.verify` and `ProvedScope.check`).
  - The inner protocol is C-Flock's compiled table at the executable's arithmetic and hm96-sha512 Merkle scheme
    (`innerExec` = `flockInnerCL T CT execArith Refine.H512 Refine.enc512 Refine.leaf512 cls regs sch`).
  - The conclusion is a disjunction of five, every fork over the prover's own continuations:
    - a round fork;
    - a session fork;
    - an inner fork (`InnerForkRec` at `clashPickCL`);
    - a run the prover reaches, whose sessions all verify, that read at some row a commit string other than the
      registered one, with the two openings colliding;
    - or `Pr[every session verifies ∧ the registered netlist's statement fails]` is at most V*'s sessions' expected
      bound, plus `r` × their stage slack, plus `tableError`.
- **(ii) ZK with circuit privacy**, in `RecursiveCircuitPrivateLeaves`' form (the simulator reads only the class and the
  owed outputs), within `2n_r·2^-193 + ε_o + n_h·2^-193` both ways.

**`_hop` decision as ruled.** `Row :=` the commit string V* checks.
- `regBcCommit i` is the registration's commitment at row position `i`: an opening `(reg, bc, path)` is exactly
  `Flock.Registered.opens reg bc i path`.
- The hm96 binding of a commit string to its row is in what the hidden statement of a list of commit strings means
  (`stmt : (ℕ → ByteArray) → L.Ω → Hidden cls`).
- A break is the run-tied disjunct above. `regBcCommit_binding` proves it binding with no premise: two openings of one
  port to different strings give a SHA-512 collision (hm96's leaf inputs when the tree leaves agree, else
  `opensLeaf_binding`'s pair).

```lean
def RecursiveAudit : Prop :=
  (∀ {nT r : ℕ} (T : Fin nT → Type) (CT : Fin r → Type) [∀ k, Fintype (CT k)] [∀ k, Inhabited (CT k)]
    {n : ℕ} {L : Law n} {Reg Cm : Type} {S : ℕ} {Vs : Fin S → VStmt} {Reg' Reg₂ : Type}
    (cls : HClass) (regs : List (FlockSoundness.Model.Region cls.kLog (cls.m - cls.kLog)))
    (sch : Accounting.Schedule)
    (zs : Reg → L.Ω → List (Cm × (innerExec T CT cls regs sch).Coin) → Reg₂ → (j : Fin S) → (Vs j).Outer Reg')
    (dg : ByteArray → ByteArray) (N : ℕ)
    (σ : Strategy (recGame L Reg (innerExec T CT cls regs sch) Cm fun R ω t => outerV (zs R ω t) dg N))
    (x : Reg → L.Ω → Hidden cls)
    (wmsg : ((j : Fin S) → (Vs j).Bits) → List (innerExec T CT cls regs sch).Msg)
    (Sk : ℕ → (j : Fin S) → Finset (PosK (Vs j).c (Vs j).hU (Vs j).nv))
    (cmt : (j : Fin S) → Cm → PosK (Vs j).c (Vs j).hU (Vs j).nv → (obK (Vs j).c (Vs j).hU (Vs j).nv).Dg)
    (msg : ℕ → ((j : Fin S) → PosK (Vs j).c (Vs j).hU (Vs j).nv → ValK (Vs j).c) → (innerExec T CT cls regs sch).Msg)
    (rt : Flock.Registered.Port) (stmt : (ℕ → ByteArray) → L.Ω → Hidden cls)
    (reads : Reg × L.Ω × List (Cm × (innerExec T CT cls regs sch).Coin) × (Reg₂ × VRec Vs Reg' dg N) → ℕ → Prop)
    (row : … → ℕ → ByteArray) (op : … → ℕ → Flock.Registered.Port × ByteArray × ByteArray)
    (_hS : ∀ j, Law.ExecStrata (Vs j).law.σs (Vs j).law.ks (Vs j).law.St)
    (_hck : ∀ R ω t R₂ j, FailClosed.ScopeZ (zs R ω t R₂ j).I)
    (_hA3 : ∀ j, Flock.Premises.UniformRandomBytes (Vs j).law.Lb (Vs j).law.src)
    (_hin : Flock.Premises.CompiledForkSound T CT cls regs sch)
    (_hop : ∀ o, VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ i, reads o i →
      (regBcCommit i).Opens rt (row o i) (op o i))
    (_hx : ∀ o, VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ q : ℕ → ByteArray, (∀ i, reads o i → q i = row o i) →
      x o.1 o.2.1 = stmt q o.2.1)
    (p : ℕ → ByteArray) (op₀ : ℕ → Flock.Registered.Port × ByteArray × ByteArray)
    (_hreg : ∀ i, (regBcCommit i).Opens rt (p i) (op₀ i))
    {k Rw M : ℕ} (_hk : 1 ≤ k) (_hRw : 1 ≤ Rw) (_hM : 1 ≤ M) {ρ : ℝ} (_hρ : ρ < 1)
    (_hr : ∀ R ω t R₂ j S' R' i, rateZ (planZAt (Reg := Reg') (zs R ω t R₂ j).dj (zs R ω t R₂ j).y₀ S' R') i k ≤ ρ)
    (_hbr : Flock.Premises.VBridge zs dg N k Rw x wmsg Sk cmt msg),
    RoundFork zs dg N k Rw σ cmt ∨ SessionFork zs dg N k Rw M σ ∨
      InnerForkRec zs dg N k Rw σ x wmsg Refine.H512
        (clashPickCL T CT execArith Refine.H512 Refine.enc512 Refine.leaf512 cls regs sch) ∨
      (∃ o, FlockSoundness.Game.Outcome (recGame L Reg (innerExec T CT cls regs sch) Cm
          fun R ω t => outerV (zs R ω t) dg N) σ o ∧
        VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 ∧
        ∃ i, reads o i ∧ row o i ≠ p i ∧ FlockSoundness.Binding.Collides ((regBcCommit i).ext (op o i) (op₀ i))) ∨
      prob (fun o => VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 ∧
            ¬ (innerExec T CT cls regs sch).holds (stmt p o.2.1))
          (recGame L Reg (innerExec T CT cls regs sch) Cm fun R ω t => outerV (zs R ω t) dg N) σ ≤
        expAt σ (fun ω t s => sumV (zs σ.1 ω t) dg N
            (fun R₂ j τ => (zs σ.1 ω t R₂ j).boundCR dg N (Vs j).law.model k Rw M ρ τ) s) +
          ((innerExec T CT cls regs sch).r : ℝ≥0∞) * expAt σ (fun ω t s => sumV (zs σ.1 ω t) dg N
            (fun R₂ j τ => (zs σ.1 ω t R₂ j).slackCR dg N k Rw M ρ τ) s) +
          ENNReal.ofReal (Accounting.tableError sch ⟨cls.kLog, regs.length, cls.mPts⟩)) ∧
  (∀ {Out Prog Wit Rv Ωa Ωp Ωo Ωs V : Type} [Fintype Ωa] [Inhabited Ωa] [Fintype Ωp] [Inhabited Ωp] [Fintype Ωo]
    [Inhabited Ωo] [Fintype Ωs] [Inhabited Ωs]
    (nr : ℕ) (rows : Prog → Fin nr → ByteArray) (pub : (Fin nr → ByteArray) → Rv)
    (honest : Out → Prog → Wit → Prop)
    (nh : ℕ) (msgs : Prog → Wit → (Fin nr → ZkView.Salt) → Ωa → Ωp → Fin nh → ByteArray)
    (view : Prog → Wit → (Fin nr → ZkView.Salt) → Ωa → (Fin nh → ByteArray) → Ωp → (Fin nh → ZkView.Salt) → Ωo → V)
    (sim : Out → Rv → Ωa → (Fin nh → ByteArray) → Ωs → V) {εo : ℝ≥0∞}
    (_hOuter : ∀ o P w, honest o P w → ∀ r a p (y : Fin nh → ZkView.Salt) (E : V → Prop),
      prCoin (fun q : Ωo => E (view P w r a (fun i => firewallLeaf (msgs P w r a p i) (y i)) p y q))
        ≤ prCoin (fun s : Ωs =>
            E (sim o (regLeaves rows pub P r) a (fun i => firewallLeaf (msgs P w r a p i) (y i)) s)) + εo)
    (_hKey : Flock.Premises.HashDerivedKeyHm96)
    (p₀ : Prog) (o : Out) (P : Prog) (w : Wit), honest o P w →
    ∀ E : Rv × Ωa × (Fin nh → ByteArray) × V → Prop,
      recRealPr (regLeaves rows pub) nh msgs view P w E ≤ recSimPr (regLeaves rows pub) nh sim o p₀ E +
          (2 * nr * (2 : ℝ≥0∞) ^ (-193 : ℤ) + εo + nh * (2 : ℝ≥0∞) ^ (-193 : ℤ)) ∧
        recSimPr (regLeaves rows pub) nh sim o p₀ E ≤ recRealPr (regLeaves rows pub) nh msgs view P w E +
          (2 * nr * (2 : ℝ≥0∞) ^ (-193 : ℤ) + εo + nh * (2 : ℝ≥0∞) ^ (-193 : ℤ)))
```

(`row` and `op` take the same outcome type as `reads`; the file spells it out.) The order is deliberate. Inputs come
first, then the hypotheses (`_hS` … `_hx`). The first input after the acceptance (`p`) starts the conclusion, so
`_hreg`, the count curve and `_hbr` are part of what it concludes ("for the registered strings, for every count curve
bounding the rates, given VBridge, …"), as the shape rule reads `accepts → ∀ w < n, P w`.

The proof (`Audit.lean`, about 40 lines):
- (i) is `zk_sessions_recursive_fork_inner` at the compiled table and the premise `_hin`, with the break of
  `RecursiveRanRegistered`'s proof at `regBcCommit_binding`;
- (ii) is `RecursiveCircuitPrivateLeaves` applied as is.

## 2. Premises

`shape.premises = ["Proofs.Flock.Recursive.Premises"]`; each is an `abbrev` of the named assumption, except the compile
lemma's.

| premise | what | on the brief's list? |
|---|---|---|
| `Flock.Premises.VBridge` | `Flock.Assumptions.VBridge`: V*'s circuits compute C-Flock's inner verifier | yes, while G is open |
| `Flock.Premises.CompiledForkSound` | the compile lemma in fork form: `InnerSoundForkOn` at `flockInnerCL` with `execArith`, hm96-sha512, `clashPickCL`, at `tableError` (`flock_inner_sound_compiled`'s conclusion) | yes, until it's proved |
| `Flock.Premises.UniformRandomBytes` | A3, `uniform/os-random`: the OS bytes V*'s laws draw from are uniform | **no, unlisted** |
| `Flock.Premises.HashDerivedKeyHm96` | `hash-derived-key`: hm96's salt hash keys its hiding at 2^-193 | **no, unlisted** |
| (hidden) `ZkOuter.hRec`, a field of each session | the outer sessions' custody (`RecordsLiveZK`) | **no, unlisted, and not visible to the shape check** (§5) |

`CompiledForkSound` is the lemma's conclusion at the property's schedule. `flock_inner_sound_compiled` discharges it at
a class whose schedule is `fast100 cls.m`'s and whose layout holds (`LinkLayout`), so the class's schedule and layout
are no longer hypotheses of the property. They are obligations of discharging the premise at the universal unit's class
(gap 4).

## 3. Step A: the five `shape.frozen` entries

All five are now `lemma:` with a one-line reason, leaving the list for `RecursiveAudit`:
- `RanRegisteredRun` (one-session break, used at the commit strings);
- `RecursiveRanRegistered` ((i) restates it at the compiled table with the inner fork);
- `RecursiveCircuitPrivateLeaves` ((ii));
- `RecursiveCircuitPrivate` (the reduction (ii) applies);
- `RecursiveCircuitIndist` (the two-netlist form).

`RecursiveSound`'s reason was stale (it cited `_hCR`, gone since the fork form landed). It and `RecursiveZK` are now
`lemma:` too, their forms at the compiled table and with circuit privacy being (i) and (ii).

## 4. The gap list

The tree's only sorrys are rec-thm's two in `Compile.lean` (lines 86 and 154); this branch adds none. The run's sorry
audit names exactly those two lemmas and what uses them:
- `RecursiveAudit`;
- rec-thm's corollaries (`flock_inner_sound_compiled_fast100`, `_plain`, `recursive_sound_compiled`, `_fast100`).
- One is on the property's proof path: `zk_sessions_recursive_fork_inner`.
- The other, `flock_inner_sound_compiled`, discharges a premise.
- Everything else missing is a hypothesis the property still takes, or a premise the brief didn't list, each named
  below with what replaces it.

**On tonight's path (the universal unit):**

| # | name | one-line statement | size (Lean lines) | owner |
|---|---|---|---|---|
| 5a | `FlockSoundness.Discharge.Recursion.zk_sessions_recursive_fork_inner` (sorry, `Compile.lean`) | the recursive audit is sound with the inner protocol sound in fork form (`InnerSoundForkOn`), the inner fork a third disjunct | rec-thm's sizing | proofs (rec-thm) |
| 5b | `FlockSoundness.Discharge.Recursion.flock_inner_sound_compiled` (sorry, `Compile.lean`) | C-Flock's compiled table is sound in fork form at `tableError`; discharges `CompiledForkSound` | rec-thm's sizing | proofs (rec-thm) |
| 6 | VBridge G: `AlgebraDecodes` (G1–3), `AccChains` (G4), `StagesAccept` (G5), `VCommits`, `VDecodes`, `VFull` (G6), the hypotheses of `FlockVBridge.Compiled.vbridge_compiled` (`cursor/vbridge-g-compose-741b`, 3ada41b93, no sorry there) | V*'s circuits compute C-Flock's inner verifier at `flockInnerCL`; discharges `VBridge` | lean's sizing | lean |
| 3a | `Recursion.zk_reads_open` (proposed) | `_hop`: at an outcome whose sessions verify, each registered read's commit string opens the registration's root at its row; from `ZkOuter.rd` and `checkRegistered` via `zk_session_regValsR` / `RegForkZC`, with `reads`, `row`, `op` defined from the outcome | ~150 | proofs |
| 3b | `Recursion.hidden_of_reads` (proposed) | `_hx`: the hidden statement V*'s sessions decode at that outcome is the read strings' netlist's | ~120 | proofs |
| 2 | `Recursion.vstar_outer_zk` (proposed; `_hOuter` from `ZeroKnowledgeHidden`) | V*'s outer sessions are ZK within `ε_o` with a simulator reading the owed outputs, the registration's view, the auditor's tape and the commitments. Sub-gaps: the tape (~250); the self-check abort, which needs `InnerHolds` (~200); `avoidsMask` (~10, from `DrawSetupZHJ.avoidsMask`); `ZkViewAtJ` → `prCoin` (~150); hiding of `R₂` (~120) | ~730 | proofs |
| 4 | `Recursion.audit_at_universal` (proposed) | the instantiation: `cls`, `regs`, `sch` at `UniversalUnit_v1`'s class (with `fast100` and `LinkLayout`, discharging `CompiledForkSound` from 5b); `L` and `Vs` at V*'s laws (`_hS`, the count curve `_hr`); `honest`/`msgs`/`view`/`sim` at the Lean ZK server (`Flock.Firewall.run`'s sends), so that (ii) is about a function | ~300 | proofs |
| 7 | `Recursion.vstar_execStrata` (proposed) | `_hS`: V*'s laws' executable strata are their model's | ~50 | proofs |
| 8 | `ZkOuter`'s Prop fields (`hRec`, `hDraw`, `hTags`, `hown`) and `VStmt`'s `hU`/`hscope` | each a verifier refusal or a premise: `hU`/`hscope` from `_hck` (`FailClosed.Checks.built`/`.scope`); `hDraw`/`hTags`/`hown` from `AcceptsV`; `hRec` (custody) a world premise to list or a refusal | ~200 | proofs |
| 8b | `Flock.Premises.UniformRandomBytes` over `Vs` | A3 for all of V*'s laws as one premise, so the shape sees `_hA3`'s head (the check's refusal, §5) | ~4 | proofs (me, next commit) |
| 8c | the shape's refusals of `cls.hk`/`hk6`/`hm` and `L.nonempty` | gone with gap 4; `Nonempty` might better be exempted by the check | 0 beyond gap 4 | lean (the check), with gap 4 |

**Off the path (route P inside V*, the brief's first item).** From `note:proofs/20261009T0731Z-finding-routep-under-vstar`
(names proposed there; route P's Lean is on `cursor/routep-main-95d4`, 3b73219f9, no sorry):

| name | one-line statement | lines | owner |
|---|---|---|---|
| `FlockVBridge.Algebra.residuals_eq_run_xv`, `ringSwitch_of_residuals_xv` | the gate session's wiring claims, with an extra claim's value a message and its point coins | 180 | proofs |
| `FlockVBridge.Gkr.structureOf`, `Gkr.run`, `Gkr.run_sim` | the product GKR's algebra (per layer: λ, rounds, the gate check, the next claim) | 450 | proofs |
| `FlockVBridge.Gkr.residuals_eq_run` | the product GKR's residuals are its run, over `buildAll_spec` | 120 | proofs |
| `FlockVBridge.Gkr.layers_of_residuals` | zero residuals give every round's identities and every gate check | 250 | proofs |
| `FlockVBridge.Gkr.input_of_residuals` (with `Gkr.sId_eval`) | zero residuals give the product inputs with `ŝ_σ(ρ)` the σ openings' slot-weighted sum | 260 | proofs |
| `sound_residualForms_scaled`, `OfVStar.residualForms_eq_scaled` | the scaled residual forms | 120 | proofs |
| `FlockVBridge.Algebra.pcsOnly_of_residuals` (with `runPcs`, `runPcs_sim`, `residuals_eq_runPcs`) | a lone Ligerito opening of one claim | 300 | proofs |
| `FlockVBridge.routeP_vBridge` | `VBridge`'s four conjuncts for route P's statements | 300 | proofs |
| `FlockSoundness.Discharge.Recursion.routePInner`, `routeP_recursive_sound` | `RecursiveSound` at route P's inner verifier | 200 | proofs |
| `FlockSoundness.Gkr.batched_sound` | the product GKR's soundness error | 300 | proofs |
| `FlockSoundness.Discharge.PrivateCircuit.ordered_of_acycTable` | the acyclicity table's session gives `RouteP.Ordered` | 175 | proofs |
| `FlockSoundness.Discharge.PrivateCircuit.route_p_inner_sound` | `route_p_sound` composed with GKR soundness, σ binding and acyclicity | 250 | proofs |
| per V* unit kind, the generic pin | — | ~100 each | proofs |

That is about 2,180 lines of VBridge and about 725 of inner soundness. Route P doesn't touch the property's text: it
replaces `innerExec` by route P's inner and `CompiledForkSound` by `route_p_inner_sound`'s fork form.

## 5. The shape check

The check is `check.py`'s own verdict in run r20261009-122359-50dc (`lean-audit/audit-Security/report.json`). Its entry
is `outcome: accept` by `Flock.ProvedScope.check` or `Flock.Zk.verify`. I also replayed `check.refusals` on that run's
facts (`proved-in-Proofs/facts.json`), and the replay gives the same nine refusals.

**(i): six refusals.**
- The check takes `_hck` (the statement check accepting V*'s statements) as the acceptance.
- `_hin` is a premise.
- `_hop` and `_hx` pass, because their types reach `Zk.verify` (see §6).
- `p` starts the conclusion.

What it refuses, and what removes each:

| refused | why the check refuses it | what removes it |
|---|---|---|
| `_hA3 : ∀ j, Flock.Premises.UniformRandomBytes …` | the premise sits under `∀ j`, so the hypothesis has no head constant and the check doesn't see it as a premise | a premise over all of V*'s laws at once (`Flock.Premises.UniformRandomBytes Vs := ∀ j, …`), about 3 lines in `Premises` plus 1 in the property; or the check reading through a leading `∀`. **I haven't pushed it, so head stays the checked commit; next commit.** |
| `_hS` (V*'s laws' executable strata) | not acceptance, not a premise | gap 7 |
| `cls.hk`, `cls.hk6`, `cls.hm` (fields of `HClass`) | Prop fields of an input the property ranges over | gap 4: `cls` fixed at the universal unit's class, so it is no longer an input |
| `L.nonempty` (`Law`'s `[nonempty]` field) | the same | gap 4 (`L` at V*'s law), or the check exempting a type's own `Nonempty`; a friction note for lean |

**(ii): three refusals.**
- "takes no hypothesis that its function returned accept": (ii) has no acceptance.
- `_hOuter` (V*'s sessions' ZK) is taken.
- `honest o P w` is taken.

The shape entry has one function and one outcome for the whole conjunction. Read at `outcome: none` (my replay only),
(ii) "says nothing about `ProvedScope.check` or `Zk.verify`" and still takes `_hOuter`. So (ii) passes only after
three things:
- gap 4 makes it about a function (`view` the Lean ZK server's sends, so its entry is `Firewall.run` with outcome
  `none`);
- gap 2 discharges `_hOuter`;
- the per-conjunct entry gets a ruling, or ZK becomes its own property beside the soundness one. That one is
  Daniel's.

**Without the gaps, then:**
- (i) passes after one cheap fix (the `_hA3` premise over `Vs`) plus gaps 4 and 7.
- (ii) needs gaps 2 and 4 and the ruling.

No `frozen` entry is needed or added for `RecursiveAudit`; it's under `shape.properties`.

## 6. What the property still doesn't say, against the brief

- **Not in `Security/Properties/`**, and its premises are not in `Definitions/` (§1); both wait on C-Flock's spec being
  extracted.
- **Two premises the brief didn't list** (A3, `hash-derived-key`), and a third hidden one (`ZkOuter.hRec`, custody).
- **(ii) has no acceptance.** As a simulation statement it takes no verdict of a function, and the shape entry has one
  function and one outcome for the whole conjunction. It needs either a ruling (per-conjunct entries, or ZK as a
  separate property beside the one), or gap 4, with `view` the firewall's sends, so that (ii) is about `Firewall.run`
  with outcome `none`.
- **`_hck` is a stand-in.**
  - It is the verifier's statement check at every history V* produces, and the proof doesn't use it today.
  - The probabilistic acceptance is the event inside `Pr[…]`, which the shape rule has no form for: no property passing
    the shape so far is probabilistic.
  - It becomes load-bearing when gap 8 derives `VStmt`'s `hU`/`hscope` from it.
- **Hypotheses the shape can't see.**
  - `_hop` and `_hx` count as "about" the function only because their types mention `VerifiesV`. The check takes any
    hypothesis that transitively reaches `Zk.verify` as an acceptance, and `ZkOuter.hown` mentions `LiveAcceptsZKR`, so
    anything mentioning a session reaches it. They are real gaps (3a, 3b) that the check passes.
  - The Prop fields of `VStmt` and `ZkOuter` sit under a function-typed binder (`Vs : Fin S → VStmt`, `zs : … → Outer`),
    so the check doesn't extract them.
  - Both are worth a friction note to lean (the check's owner).
- **Conclusion-side conditions.** `_hreg`, the count curve (`_hk` … `_hr`) and VBridge sit after `p`, so they are part of
  what the property concludes, not hypotheses. That is legitimate for VBridge (a premise anyway) and for the registered
  strings. `_hr` is a fact about V*'s laws that gap 4 should discharge rather than leave in the conclusion.
- **Non-vacuity rests on gaps 3 and 4.** `reads`, `row`, `op`, `stmt`, `honest`, `view` and `sim` are free. Until they
  are defined from the executable (3a, 3b, 4), the property is true of any choice satisfying `_hop`/`_hx`/`_hOuter`,
  including degenerate ones.
- **Outside the theorem:**
  - the ZK server's coin-commitment check (refusing a coin that doesn't open the challenger's commitment);
  - the server secret XORed into the salts (a PRF premise outside the theorem);
  - the level-0 recheck and the pad-derived values still in Rust (D8 (a)).

## 7. Runs

All on vy-nebius-1, through `research run`.

| run | commit | what | result |
|---|---|---|---|
| r20261009-103753-70ca, r20261009-105017-6a0c, r20261009-110025-19fe | earlier heads | the shape check, queued behind other lanes | cancelled by me: their heads went stale while they waited for a slot |
| r20261009-110840-74e8 | 271ecf6a5 | fast path (`lean_changed.py --records Security --update`) | rc 2: after the slot, another run held the records build directory; no Lean result |
| r20261009-110904-2ff9 | 271ecf6a5 | full audit (`check.py --build --update Security`) | rc 1. The spec built. Proofs failed only at `Premises.lean:46`: inside the `Flock.*` namespaces, the executable's `Flock.Region` shadows the opened `Model.Region` |
| **r20261009-122359-50dc** | **2f4b0235b** (head) | full audit | rc 1 by design. 5428 jobs built, `Premises`, `Property` and `Audit` included. The failures are the sorry (§4) and the nine shape refusals (§5), nothing else |

The guarantee lock has no record of `RecursiveAudit` on the branch yet. The run's `--update` lists the statement and
the definitions it reads as new (`audit-Security/review.txt`). The run's copy of the lock is formatted differently
(a diff of about 28,000 lines), so I left it out; the lock will go in when this lands.
