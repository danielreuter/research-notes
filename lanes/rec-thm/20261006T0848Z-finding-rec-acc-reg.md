---
id: rec-thm/20261006T0848Z-finding-rec-acc-reg
campaign: proof-service
lane: rec-thm
kind: finding
status: active
repo: danielreuter/verity
origin: bc-0e16e57e (rec-thm, for @proofs)
---
# B1 closed in the model: one shared registration `R₂` before V*'s sessions

**Status, 1:55 AM PDT, 6 Oct:** the design, the statement and the proof are done: commit `f6ab493cb` on branch
`cursor/rec-acc-reg-95d4` (from #1261's head `b4784eb8e`), which builds on vy-nebius-1 (`Proofs.Flock.Recursive.Guarantees`
and everything it imports, no new warnings, no `sorry`). The lock (`audit.py --update`) is running. This note gives the
exact Lean signatures first, for the vbridge lane (piece G), and then what I found.

## The signatures

In `Proofs/Flock/Recursive/Flock.lean` (namespace `FlockSoundness.Discharge.Recursion`), with
`{S : ℕ} {Vs : Fin S → VStmt} {Reg' Reg₂ : Type}` and `{n : ℕ} {L : Law n} {Reg : Type} {I : Inner} {Cm : Type}`:

```lean
abbrev outerV (zs : Reg₂ → (j : Fin S) → (Vs j).Outer Reg') (dg : ByteArray → ByteArray) (N : ℕ) :
    Game (Reg₂ × VRec Vs Reg' dg N) :=
  .send Reg₂ fun R₂ => (sessions (zs R₂) dg N).map fun b => (R₂, b)

def VBridge (zs : Reg → L.Ω → List (Cm × I.Coin) → Reg₂ → (j : Fin S) → (Vs j).Outer Reg')
    (dg : ByteArray → ByteArray) (N k Rw : ℕ) (x : Reg → L.Ω → I.Stmt)
    (wmsg : ((j : Fin S) → (Vs j).Bits) → List I.Msg) : Prop :=
  ∀ R ω t R₂ (τ : (j : Fin S) → Strategy ((zs R ω t R₂ j).game dg N))
    (o : (j : Fin S) → Reg' × Finset (Fin (Vs j).nv) × Exec.Transcript),
    (∀ j, LiveAcceptsZKR (zs R ω t R₂ j).I (zs R ω t R₂ j).own (o j) ∧
      (zs R ω t R₂ j).Good ((zs R ω t R₂ j).layer dg N k Rw (τ j))) →
    I.accepts (x R ω) ((wmsg fun j => (zs R ω t R₂ j).layer dg N k Rw (τ j)).zip (t.map Prod.snd))
```

So `zs : Reg → L.Ω → List (Cm × I.Coin) → Reg₂ → (j : Fin S) → (Vs j).Outer Reg'`: session `j`'s whole `ZkOuter`
(its inputs `I`, `own`, `rd`, `hown`, …) may read `R₂`. `wmsg` does not take `R₂`: it reads the inner messages from the
layers, and `R₂`'s values (the running sums) are advice, not messages.

The spec (`Specs/Flock/Assumptions/Recursive.lean`, namespace `Flock.Assumptions`):

```lean
def VBridge {n : ℕ} {L : Law n} {Reg : Type} {I : Inner} {Cm : Type} {S : ℕ} {Vs : Fin S → VStmt}
    {Reg' Reg₂ : Type} (zs : Reg → L.Ω → List (Cm × I.Coin) → Reg₂ → (j : Fin S) → (Vs j).Outer Reg')
    (dg : ByteArray → ByteArray)
    (N k Rw : ℕ) (x : Reg → L.Ω → I.Stmt) (wmsg : ((j : Fin S) → (Vs j).Bits) → List I.Msg)
    (Sk : ℕ → (j : Fin S) → Finset (PosK (Vs j).c (Vs j).hU (Vs j).nv))
    (cmt : (j : Fin S) → Cm → PosK (Vs j).c (Vs j).hU (Vs j).nv → (obK (Vs j).c (Vs j).hU (Vs j).nv).Dg)
    (msg : ℕ → ((j : Fin S) → PosK (Vs j).c (Vs j).hU (Vs j).nv → ValK (Vs j).c) → I.Msg) : Prop :=
  Recursion.VBridge zs dg N k Rw x wmsg ∧ VCommits zs Sk cmt ∧ VDecodes wmsg (fun _ _ a b => a = b) Sk msg ∧
    VFull I.r Sk
```

`VCommits` gains `∀ R₂` (session `j`'s public file registers the gateway's commitments at `Sk i j` at every `R₂`):

```lean
def VCommits (zs : Reg → L.Ω → List (Cm × I.Coin) → Reg₂ → (j : Fin S) → (Vs j).Outer Reg')
    (Sk : ℕ → (j : Fin S) → Finset (PosK (Vs j).c (Vs j).hU (Vs j).nv))
    (cmt : (j : Fin S) → Cm → PosK (Vs j).c (Vs j).hU (Vs j).nv → (obK (Vs j).c (Vs j).hU (Vs j).nv).Dg) : Prop :=
  ∀ i R ω t (e : Cm × I.Coin), t[i]? = some e → ∀ R₂ j, ∀ pos ∈ Sk i j, ∀ R' : Reg',
    (zs R ω t R₂ j).vb.cs R' pos = cmt j e.1 pos
```

`VDecodes` and `VFull` are unchanged. `RecursiveSound` binds `{Reg' Reg₂ : Type}`, takes the new `zs`, and reads:

```lean
    (σ : Strategy (recGame L Reg I Cm fun R ω t => outerV (zs R ω t) dg N))
    …
    (_hCR : ∀ i < I.r, ∀ ω pos,
      (forkAt (obS Vs) σ (cmtS cmt) (fun R ω t s => trialV (zs R ω t) dg N k Rw s) i ω pos).CR H512 (q i))
    …
    prob (fun o => AcceptsV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 ∧ ¬ I.holds (x o.1 o.2.1))
        (recGame L Reg I Cm fun R ω t => outerV (zs R ω t) dg N) σ ≤
      expAt σ (fun ω t s => sumV (zs σ.1 ω t) dg N
          (fun R₂ j τ => (zs σ.1 ω t R₂ j).boundCR dg N (Vs j).law.model k Rw M ρ t' qF qS qW qR τ) s) +
        ∑ i ∈ Finset.range I.r,
          (expAt σ (fun ω t s => sumV (zs σ.1 ω t) dg N
              (fun R₂ j τ => (zs σ.1 ω t R₂ j).slackCR dg N k Rw M ρ t' qF qS τ) s) +
            (∑ pos, weightS Vs Sk ρ i pos) * ENNReal.ofReal (Real.sqrt (q i ^ 2 / 2 ^ (513 : ℝ)))) + εin
```

with `_hr : ∀ R ω t R₂ j S' R' i, rateZ (planZAt (Reg := Reg') (zs R ω t R₂ j).dj (zs R ω t R₂ j).y₀ S' R') i k ≤ ρ`.
The helpers: `AcceptsV zs o := Accepts (zs o.1) o.2`; `sessOf zs dg N s := Strategy.ofMap (fun b => (s.1, b)) _ s.2`
(the prover's strategy for the sessions after its registration `s.1`); `sumV zs dg N F s := sumS (zs s.1) dg N (F s.1)
(sessOf zs dg N s)`; `trialV zs dg N k Rw s pos := trialS (zs s.1) dg N k Rw (sessOf zs dg N s) pos`.

## What I found

**`R₂` is expressible by sequencing, without changing `recGame`.** `recGame`'s outer game is already a parameter
(`outer : Reg → L.Ω → List (Cm × I.Coin) → Game β`), and `recursive_sound_upto`, `forkAt`, `expAt` and `AllAt` are
generic in it. So the shared registration is the outer game's first move: `outerV` sends `R₂`, then runs V*'s sessions
at `R₂` and records `R₂` in the outcome. `recGame`, `Compose`, `Sound`, `Fork` and `Transfer` are untouched. It is not
expressible with the existing `R`: `R` is sent before the draw and the inner coins, and `rec-acc` depends on the coins.

**The binding costs no new term.** Each session's `rd` and `own` now read `R₂` (its rows, salts and paths for the
registrant's openings; its roots for the verifier's reads file), and `R₂` is fixed before every session's draw. So
`R₂`'s reads are priced by the terms each session's `bound` already has: `regTermZC` at the registrant's leaf
(`zk_session_regDrawnR`) and `qR²/2^513` off it (`off_le`), at the `R₂` the prover sends. Neither grows with the extra
registered reads: `regTermZC` sums over every commit string of the session, registered or not, and does not read `rd`;
`qR²/2^513` is one finder per session. What changes is what the `cr/sha-512` premises (`ZkOuter.CR`) are about: the
registered-value finders and the off-leaf finder now hold `R₂`'s openings.

**No cross-session term.** Every session's registrant record is a function of the one `R₂`, so a layer that agrees with
its registrant at every session agrees with one value at every session. The union over sessions is the sum that
`sumS` already takes. A cross-session term would be needed only if two sessions could each bind to a different opening
of one root; each binds to the registrant's own opening, of which there is one.

**What stays the job of the instance (and of `VBridge`).** `zs` is total, as before. That the real V*'s `own` reads
only `R₂`'s roots (not its rows), and that every level's `rd` is `R₂`'s same `rec-acc` rows, are properties of the
concrete `zs`, on which `VBridge` (piece G) is stated. `dirs` (B2) is not in this change: it remains a public input that
`rd` must record as verifier-registered, like `coef`.

`RecursiveZK` is untouched. Its lock record may change on the value hash only, as in #1261 (the shared `_proof_N` for
`Nat.AtLeastTwo 2` is renumbered when `RecursiveSound` is restated).
