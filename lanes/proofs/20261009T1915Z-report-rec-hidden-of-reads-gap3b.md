---
id: proofs/20261009T1915Z-report-rec-hidden-of-reads-gap3b
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-0bfaef0d-4116-5825-9925-7d4778a241ef
---


# Gap 3b: `_hx` can't leave `RecursiveAudit` yet (Oct 9, 19:20Z)

**Answer: no, not as a lemma about the property's current objects.** `_hx` (after 3a's substitution) is

```lean
_hx : ∀ o, VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ q : ℕ → ByteArray,
  (∀ i, readsZ zs rt o i → q i = rowZ zs rt o i) → x o.1 o.2.1 = stmt q o.2.1
```

`x`, `stmt`, `zs` and `Vs` are all free in `RecursiveAudit`, and three things are missing before `_hx` can be proved:
- two facts about how V*'s sessions are built: where their registered tables come from, and which rows they read;
- `stmt` itself, which needs the lowering of a decoded circuit to `Hidden cls`. That lowering isn't written on either
  universal branch yet.

Each fact is a premise I can't prove now, so per the brief I stopped early. **No branch pushed, no build, no run, no
new Lean.** Below: why each is needed, the named `Prop`s I'd use, and what gap 4 (or rec-lean's executable statement)
must fix so `_hx` becomes a short lemma.

## Why `_hx` needs more than acceptance

`x R ω` is fixed by the registration and the draw. `readsZ`/`rowZ` read the session statements' tables, which
`setupOf` takes from `(zs R ω t R₂ j).I.publicFile` (`Stmt.setupTables … I.publicFile … (recordDraw record)`). So
`_hx` asks that every verifying outcome at `(R, ω)` read strings whose `stmt` is the same `x R ω`. Two things can break
that, and neither is excluded by `VerifiesV`, `checkRegistered` or 3a.

1. **Coverage.** `stmt q ω` may only depend on `q` at rows the outcome reads.
   - At `S = 0` every outcome verifies (`∀ j : Fin 0`) and `readsZ` is empty. `_hx` then says
     `x R ω = stmt q ω` for every `q`, which is false for any `stmt` that reads its strings.
   - The same holds at any `zs` whose program never reads a row `stmt` depends on, or whose session never holds `rt`
     (`rt ∉ own`, 3a's note).
   - So `_hx` needs V*'s registered reads to cover every row the hidden statement reads at `ω`. That is a fact about
     V*'s program and the instance list the verifier derives (`Registered.derived`).
2. **One string per row across outcomes.** `zs` may let a session's public file vary with `t` or `R₂` (the prover's
   later messages). Then two verifying outcomes at the same `(R, ω)` can read different strings `bc ≠ bc'` at row `i`.
   - By 3a both open `rt` at `i`, so they are a SHA-512 collision (`regBcCommit_binding`).
   - No deterministic proof excludes that. `_hx` has no collision disjunct and `x` can't see the transcript, so `_hx`
     would force `stmt q ω = stmt q' ω` for `q, q'` differing at a row `stmt` reads.
   - So `_hx` holds only if `zs` fixes the registered tables' strings by `(R, ω)`. That is a construction choice in
     gap 4, not a theorem about the current `zs`.

`VBridge` needs the same choice. It says a `Good` layer (one agreeing with each session's `rd`, "the hidden circuit's
rows from its registration") is accepted on `x R ω`, and `rd` is a field of `zs R ω t R₂ j`. So `rd`'s rows must be
fixed by `R` too, or `VBridge` (G) and `_hx` talk about different private circuits.

## Why `stmt` can't be defined yet

The strings V* reads are hm96 row digests (`Flock.Registered.tableRow`: "its `b ‖ c` among the file's row digests"),
not rows. "The private circuit of the read strings" therefore needs three steps:
- **the row each digest commits to:** the registrant's opening (`rd.wv`, `rd.ws`, per session), or a choice of
  opening. It isn't a function of the string;
- **`decode`** of the rows' description bits: `UniversalClass.decode` on c94bb5ec9, total, `Desc p → Circ p`;
- **the lowering of `Circ p` to `Hidden cls`:** not on c94bb5ec9 or on `cursor/rec-universal-lower-95d4`. At
  c86ccc9e1 `UniversalLower.lean` proves `uu_unit_sound` and has lemmas about `Hidden`, but no map from a description
  or circuit to `Hidden cls`.

I didn't merge c94bb5ec9: `decode` alone doesn't give a `Hidden cls`.

## What would make `_hx` a lemma

These are named `Prop`s, unbuilt, in the form I'd state them (namespace `FlockSoundness.Discharge.Recursion`, beside
`Reads.lean`). `sr R i` is the registration's commit string at row `i`.

```lean
/-- V*'s sessions' registered tables carry the registration's strings. -/
def ReadsOfReg (zs) (rt) (sr : Reg → ℕ → ByteArray) : Prop :=
  ∀ o, VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ i, readsZ zs rt o i → rowZ zs rt o i = sr o.1 i

/-- V*'s reads cover every row the hidden statement reads. -/
def ReadsCover (zs) (rt) (stmt : (ℕ → ByteArray) → Ω → Hidden cls) : Prop :=
  ∀ o, VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ q q', (∀ i, readsZ zs rt o i → q i = q' i) →
    stmt q o.2.1 = stmt q' o.2.1
```

With `x := fun R ω => stmt (sr R) ω`, `_hx` follows from these two in about 10 lines: for `q` agreeing with the reads,
`q i = sr R i` at every read row, and `ReadsCover` gives `stmt q ω = stmt (sr R) ω`.

`ReadsCover` is close to `_hx` with `x` eliminated, so splitting only pays when gap 4 discharges each part:
- **`ReadsOfReg`:** by construction, if gap 4's `zs` takes each session's registered table (and `rd`) from `R`.
  Nearly `rfl` then: every read's string is a table string.
- **`ReadsCover`:** from V*'s program, once `stmt` is defined. The positions `rt.reads` gives at the instances' units
  must include every row the statement reads at `ω` (all rows `0 … nr−1`, or the drawn units' rows if `stmt` reads
  only those).
- **`x`:** defined, no longer free. `VBridge` is then stated at `stmt (sr R)`.

If instead the tables stay prover-chosen after `R`, `_hx` can't hold at the executable. The property would need
restructuring by rec-lean or top:
- either `x` reads the outcome;
- or `_hx` carries a collision disjunct, as the fourth disjunct does for `p`.

That is a semantics choice for top, not a proof gap.

## The bridge I sketched for 3b

3a's report sketched a bridge: at a reachable accepted outcome, `rd`'s reads at port `rt` are `readsZ` reads (about
60 lines). It isn't needed for `_hx`, which is about strings and statements, not values. It becomes useful for proving
`ReadsOfReg` and the `VBridge` side once gap 4 sources `rd` from `R`. Not written.

## Status

- Branch: none pushed. The local worktree I opened off db99813b6 (`cursor/rec-hidden-of-reads-41ef`) had no commits; I
  removed it.
- Build/audit run: none. vy-cpu-1's lease (to 20:13Z) and its warm seed dir are unused; nothing is running there.
- Line count, axioms, `sorryAx`: not applicable (no new Lean).
- rec-lean's changes: none from 3b today. When gap 4 fixes `zs`, `x` and `stmt` as above:
  - in `Property.lean`, `_hx` (lines 132–133) and the binder `x` (line 107) go;
  - `x` becomes `stmt (sr R)` in `VBridge`'s and `InnerForkRec`'s arguments (lines 141, 143);
  - in `Audit.lean`, `hx o h.1 p hagree` (line 77) becomes the lemma's application.
