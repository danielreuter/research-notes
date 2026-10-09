---
id: proofs/20261009T1900Z-report-rec-reads-open-gap3a
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-0bfaef0d-4116-5825-9925-7d4778a241ef
---


# Gap 3a: `_hop` is a lemma, `Recursion.zk_reads_open` (Oct 9, 19:00Z)

**Answer: yes, `_hop` can leave `RecursiveAudit` as a proof.** `zk_reads_open zs rt` proves it with `reads`, `row` and
`op` read off the outcome (`readsZ`, `rowZ`, `opZ`) and the registration's root `rt` an argument. The proof follows from
`checkRegistered` alone, with no probability and no new premise. It builds; Security/Proofs passes the full audit with
kernel replay; nothing new reaches `sorryAx`.

- Branch `cursor/rec-reads-open-41ef`, head db99813b6 (two commits off `cursor/rec-sound-compiled-41ef` at fbc66b930), pushed.
- Two new files under `Security/Proofs/Flock/Recursive/`, plus one import line in the `Recursive.lean` aggregator.
  `Property.lean` and `Audit.lean` are untouched.
- Build and audit run: **r20261009-181227-5fa8** on vy-cpu-1 (18:12–18:58Z). An earlier launch, r20261009-180648-d461,
  was cancelled during its cache download to relaunch at a sturdier revision of the proofs.

## The statement

`ReadsOpen.lean`, in exactly `_hop`'s form, with `reads`, `row`, `op` replaced by functions of the outcome and `rt` an
argument:

```lean
theorem zk_reads_open {S : ℕ} {Vs : Fin S → VStmt} {Reg' Reg₂ : Type} {dg : ByteArray → ByteArray} {N : ℕ}
    {Reg Ω H : Type} (zs : Reg → Ω → H → Reg₂ → (j : Fin S) → (Vs j).Outer Reg') (rt : Flock.Registered.Port) :
    ∀ o : Reg × Ω × H × (Reg₂ × VRec Vs Reg' dg N), Flock.Guarantees.VerifiesV (zs o.1 o.2.1 o.2.2.1) o.2.2.2 →
      ∀ i, readsZ zs rt o i → (Flock.Guarantees.regBcCommit i).Opens rt (rowZ zs rt o i) (opZ zs rt o i)
```

`Ω` and `H` are generic; at `Ω := L.Ω` and `H := List (Cm × (innerExec T CT cls regs sch).Coin)` this is `_hop` with
`reads := readsZ zs rt`, `row := rowZ zs rt`, `op := opZ zs rt`. The run's probe checks exactly that, as an `example`
at `RecursiveAudit`'s binders.

The definitions (`Reads.lean`), all read off the outcome:

```lean
-- a drawn instance u of statement st reads, by its ref into the table of st's circuit's port named rt.name, the
-- table row whose commit string is bc; i is the position the verifier's program reads for u's unit (rt.reads at the
-- unit st's header names), path the header's path for that table row
def StmtRead (rt : Flock.Registered.Port) (st : Flock.Stmt) (i : ℕ) (bc path : ByteArray) : Prop :=
  ∃ t idx p positions paths u, st.pub.tables = some t ∧ Flock.Registered.unitIndices st.pub = .ok idx ∧
    (List.range st.c.ports.size).find? (fun q => st.c.ports[q]!.name == rt.name) = some p ∧
    Flock.Registered.entry st.pub rt = .ok (positions, paths) ∧ u < st.pub.n ∧
    rt.reads[idx.getD u 0]? = some (some i) ∧
    bc = Flock.Registered.tableRow st.pub t p (Flock.Registered.ref t st.c.ports.size p u) ∧
    path = paths.getD (Flock.Registered.ref t st.c.ports.size p u) ByteArray.empty

-- a session j whose verifier holds rt (rt ∈ own) sets up sts from its transcript's record; one of them reads bc at i
def ReadV (zs : Reg₂ → (j : Fin S) → (Vs j).Outer Reg') (rt) (o : Reg₂ × VRec Vs Reg' dg N) (i) (bc path) : Prop :=
  ∃ (j : Fin S) (spec : Flock.SessionSpec) (sts : Array Flock.Stmt) (k : ℕ) (hk : k < sts.size),
    rt ∈ (zs o.1 j).own ∧ setupOf (zkInputs (zs o.1 j).I) (o.2 j).2.2.2.record = .ok (spec, sts) ∧
    StmtRead rt sts[k] i bc path

def readsZ zs rt o i : Prop := ∃ x : ByteArray × ByteArray, ReadV (zs o.1 o.2.1 o.2.2.1) rt o.2.2.2 i x.1 x.2
noncomputable def readZ zs rt o i := Classical.epsilon fun x => ReadV (zs o.1 o.2.1 o.2.2.1) rt o.2.2.2 i x.1 x.2
noncomputable def rowZ zs rt o i : ByteArray := (readZ zs rt o i).1
noncomputable def opZ zs rt o i : Flock.Registered.Port × ByteArray × ByteArray := (rt, rowZ zs rt o i, (readZ zs rt o i).2)
```

The proof is deterministic: no probability term and no new premise. When every session accepts (`AcceptsV`, the first
half of `VerifiesV`), the session's `checkRegistered` accepted the statement that reads the row. By the existing
`ZkReg.check_tables` and `ZkReg.checkPort_at`, that check opened the row's commit string against `rt` at the header's
position through the header's path, and checked that the position is the one `rt.reads` gives for the instance's unit.

## Line count

- `Reads.lean`: 116 lines (definitions, `StmtRead.opens`, `ReadV.opens`, `readZ_spec`, `opens_of_accepts`); the
  proofs are about 25 of them.
- `ReadsOpen.lean`: 25 lines (`zk_reads_open`, a one-line proof).
- `Recursive.lean`: one import and one docstring sentence.

That is 141 lines against the gap list's ~150.

## Axioms and `sorryAx`

From r20261009-181227-5fa8:

- `lake build Proofs.Flock.Recursive.ReadsOpen`: rc 0. Both new files build with no warning.
- The probe proves `_hop`'s exact type at `RecursiveAudit`'s binders (`Ω := L.Ω`, the history type
  `List (Cm × (innerExec T CT cls regs sch).Coin)`) with `reads := readsZ zs rt`, `row := rowZ zs rt`,
  `op := opZ zs rt`, by `zk_reads_open zs rt`: rc 0.
- `#print axioms`: `StmtRead.opens`, `ReadV.opens`, `opens_of_accepts`, `zk_reads_open` and
  `Flock.SecurityProofs.RecursiveAudit` each depend on `[propext, Classical.choice, Quot.sound]` only.
- Security/Proofs: **PASS**, 61959 declarations in 970 modules, axioms `propext`, `Classical.choice`, `Quot.sound`,
  with kernel replay. No declaration reaches `sorryAx`.
- Security: FAIL, with the same 229 lines as the base's run r20261009-165705-14be at fbc66b930, byte for byte. Those are
  rec-lean's 8 shape refusals and the unrecorded `RecursiveAudit` / stale guarantee reads. Nothing new.

## What rec-lean must change to use it

The lemma is in two files because `Property.lean` must read the definitions and the lemma must read the property's
`VerifiesV` and `regBcCommit`: `Reads.lean` imports only `Proofs.Flock.Recursive.Flock`, so `Property.lean` can import
it; `ReadsOpen.lean` imports `Property.lean` and `Reads.lean`, so `Audit.lean` can import it.

In `Property.lean` (line numbers at fbc66b930):

1. Add `import Proofs.Flock.Recursive.Reads`.
2. Delete the binders `reads`, `row`, `op` (lines 115–120), and trim the comment at lines 112–113 to "the registration's
   root; a private circuit's statement by its rows' commit strings".
3. Delete `_hop` (lines 130–131), and change the comment at line 129 to "at an outcome whose sessions all verify, the
   hidden statement is the read commit strings'".
4. Replace `reads o i`, `row o i`, `op o i` by `readsZ zs rt o i`, `rowZ zs rt o i`, `opZ zs rt o i` in `_hx`
   (lines 132–133) and in the fourth disjunct (line 148).
5. In the docstring, lines 77–79 ("`reads o i` says a session read row `i`, `row o i` is the commit string it read there
   and `op o i` its opening of `rt`") become a description of `readsZ`/`rowZ`/`opZ`, and line 81–82's "every read
   string opening `rt` at an accepted outcome (`_hop`)" leaves the list of what is taken.

In `Audit.lean`:

1. Add `import Proofs.Flock.Recursive.ReadsOpen`.
2. Line 59–60: drop `reads row op` and `hop` from the `intro`.
3. Lines 68–69 and 73: `reads o i`, `row o i`, `op o i` become `readsZ zs rt o i`, `rowZ zs rt o i`, `opZ zs rt o i`.
4. Line 76: `(hop o h.1 i hi)` becomes `(zk_reads_open zs rt o h.1 i hi)`.
5. Line 22 of the docstring: `_hop` leaves the list of what the property still takes.

`RecursiveAudit`'s lock record changes (one hypothesis fewer, three definitions read), so `audit.py --update` and the DM
to Daniel follow, as for any change to a guarantee's statement.

## Notes for rec-lean and for gap 3b

- **The root.** `rt` is an argument: per top's acceptance test, `rt.root` is the instance's registered commitment, and
  the rest of `rt` (`name`, `value`, `leaves`, `words`, `wordBits`, `domain`, `reads`) is the region the class fixes.
- **Non-vacuity needs `rt ∈ own`.** `readsZ` only counts reads at sessions whose verifier holds `rt` (`rt ∈ (zs …).own`),
  because only those does `checkRegistered` check against `rt`. At a session whose `--registered` file lacks the
  instance's port, `readsZ` is empty, and `_hx` must then hold with no reads. So the executable statement should build
  V*'s sessions' `own` from the instance's registration, so that `rt` is among them.
- **Positions.** `i` is the position the verifier's own program reads (`rt.reads` at the instance's unit), not the
  header's claim; acceptance makes the two equal.
- **One string per row.** `rowZ` picks one read per row (`Classical.epsilon`). Two reads of row `i` with different
  strings both open `rt` at `i`, so `regBcCommit_binding` makes them a SHA-512 collision; 3b can use that for uniqueness.
- **Why not through `zk_session_regValsR` / `RegForkZC` / `ZkOuter.rd`.** `_hop` is about the public commit strings, and
  acceptance alone gives it. `zk_session_regValsR` and `RegForkZC` bound the values the proof commits at the registered
  reads (a layer agreeing with the registrant's), which is what `_hx` (3b) needs, not `_hop`. `ZkOuter.rd`'s reads are
  free data of the session (its `isRead` may be empty), and `hown` only holds at reachable outcomes
  `(R', Lv.draw ω, wr …)`, while `_hop` ranges over every outcome. So reads defined from `rd` would neither be fixed by
  the outcome nor prove `_hop` at every `o`. `readsZ` reads what the verifier actually checks.
- **A bridge 3b may want, not written.** At a reachable accepted outcome, each of `rd`'s reads with port `rt` is a
  `readsZ` read, at `rd.readAt` with the population's row digest as its string: the same steps as
  `ZkReg.checked_of_accepts`, about 60 lines.

## Gap 4(d), the count curve `_hr`: V*'s plans are not fixed anywhere

`_hr` can't yet be stated as a numeric fact.

- `rateZ (planZAt dj y₀ S' R') 0 k` is `2 ^ logLen₀ / (e · k)`, where `logLen₀` is level 0 of the one `--zk` table's
  schedule, `tableAtZK dj y₀ S'`. That is the schedule `verify --zk` sets up from the session's `Inputs` (V*'s circuit
  and public files, tags, partition, program) at the draw JSON `dj S'`, or `y₀`'s refused table.
- Those are fields of `zs R ω t R₂ j : ZkOuter …`, and `zs` is a free argument of `RecursiveAudit`; `Vs` (V*'s circuits
  and laws) is free too.
- None of the gap-4 branches fixes them. `cursor/rec-universal-class-95d4` (c94bb5ec9),
  `cursor/rec-universal-lower-95d4` (12bf1e4c2) and `cursor/rec-gaps-4-7-2261` (99d7a5b27) fix the inner class
  (`cls`, `regs`, `sch`) and V*'s strata (`_hS`), and keep `_hr` verbatim.
- `_hr` becomes numeric once V*'s statements are fixed: each session's `Inputs` and `dj` as V*'s registered files. Then
  it needs a bound `logLen₀ ≤ L_j` on each V* circuit's level-0 schedule at every draw, and `k ≥ 2^L / (e·ρ)`.
