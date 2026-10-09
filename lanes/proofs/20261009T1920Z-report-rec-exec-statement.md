---
id: proofs/20261009T1920Z-report-rec-exec-statement
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-4523e674-6edb-56fa-a39c-070b580c35f2
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

**Update (Oct 9, 8:45 AM PDT): head `206ad11b8`.** Since 2f4b0235b the branch has two more changes:
- fix 8b (42570924e), A3 over V*'s laws as one premise;
- the merge of `cursor/rec-fork-inner-35f2` (f20051ec9): gap 5a, proved and built with no sorry of its own (§4).

So `RecursiveAudit` should no longer use `sorryAx`. In r20261009-122359-50dc it used it only through 5a; `_hin` is
the premise that 5b discharges. Run r20261009-151624-6dee (fast path) checks this head, and with it 8b's shape; it
is waiting for the build slot (§7).

**Update (Oct 9, 10:55 AM PDT): head `229d8661a`, Daniel's two decisions of 9:01 AM PDT (§0).**
- **The statement count.** `RecursiveAudit` now ranges over exactly `outerStatements cls regs` of V*'s statements. That
  is a function of the class, its regions and `Flock.RecResiduals.MAX_SLOTS`, not a number fixed for one layout, so
  one statement covers every layout. It gives the 8 statements of the 8090 run (8 claims) and the 6 of the real-class
  path at 16,16,8 (12 claims).
- **Custody is a named premise.** `_hCust : Flock.Premises.RecordCustody zs₀` (`RecordsLiveZK` and `DrawFileZK` at
  every session) is a binder of the property, and the shape check lists it as a premise.
- **The checks.** Both build on n2, with no error and no new sorry. The shape check gives the same eight refusals as
  r20261009-151624-6dee, which has now run at 206ad11b8 and confirms 8b: `_hA3` is gone, and `sorryAx` no longer
  reaches `RecursiveAudit`.
- **What I didn't touch.** Property.lean's lines 81–83 and the binders where `cls` is taken are untouched.

**Update (Oct 9, 12:20 PM PDT): head `3e29b755e`, the executable statement (§A).** (i) of `RecursiveAudit` now takes
the inner statement `st`; its class, regions and schedule are `execClassAt st`. `cls.hk`, `cls.hk6`, `cls.hm`, `_hS`
and `_hin` are gone, and no hypothesis replaced them. The shape check gives **4 refusals, down from 8**.
- The build and the shape check of `a3e795ba3`: `art:0952873a…`.
- The ship: r20261009-183639-d22c.
- The records audit with `--update`: r20261009-183956-7f58. It wrote `RecursiveAudit`'s first record, committed as
  `3e29b755e`.

## A. The executable statement (Oct 9, 12:20 PM PDT)

Proofs' assignment of 10:59 AM PDT. Commits on `cursor/rec-gap-list-35f2`, each pushed:
- `1f9793202`: merges `cursor/rec-sound-compiled-41ef` (fbc66b930, 5a and 5b, sorry-free).
- `39c61f8ab`: merges `cursor/rec-universal-class-95d4` (c94bb5ec9). It built on n2 before I changed anything
  (`b20261009T1800Z-39c6.log`: 4846 jobs, no error, no sorry outside ArkLib).
- **`a3e795ba3`**: the executable statement.
- **`3e29b755e`** (head): the lock, `Security/lean-audit.json` as the `--update` run wrote it (§A.6).

### A.1 What (i) takes now

(i)'s binders, in `Property.lean`:
- `(st : Flock.Stmt)`, the inner statement. The compiled table's parameters are `execClassAt st`'s `.cls`, `.regs` and
  `.sch`, through `innerAt T CT st` and `outerStatementsAt st`.
- `{Vs : Fin (outerStatementsAt st) → VStmt}`, as before, but the sessions, commitments and records range over
  `execStmts Vs`: each statement with its model read off its executable strata (`VStmt.exec`). Only the model's fields
  (`σs`, `ks`) change; the live law, and so the sessions, stay the same.
- Gone: `cls`, `regs` and `sch` as binders, their fields `cls.hk`, `cls.hk6` and `cls.hm`, and `_hS` and `_hin`.
- The last disjunct's event now starts with `AcceptsStmt st`: Lean's verifier accepts `st`.

The class function is in the new `Proofs/Flock/Recursive/ExecClass.lean`:
- `shapeOf st`: the statement with every value dropped. It keeps `m`, the circuit, the row leaf, the pin, Δ (`da`,
  `db`), the link points, the block count, and each region's name, free bits, mask and fixed bits (`stripBytes` drops
  only the region's bytes). It drops the public file, the digest, σ, the tags, the Merkle scheme, the partition finding
  and the counts.
- `ClassOk st`: the executable's checks of the class: `StmtWF`, `RegionsWF`, and `Zk.schedule st.m` accepting.
- `execClassAt st`:
  - when `ClassOk (shapeOf st)` holds, `ExecClass.ofStmt st`: `HClass.ofStmt (shapeOf st) … 0 ∅ 0` (no hidden
    entries), `Refine.regionsOf st`, and `schedAt st.m` (`fast100`'s schedule);
  - otherwise the constant `ExecClass.fixed` (`HClass.fixed`: m 13, k_log 6, zero matrices; no regions; the default
    schedule).
- So the class reads only public fields, and the fixed class is a constant.

### A.2 The acceptance lemma and the fixed class

- `AcceptsStmt st` means two things: `Flock.Stmt.setupH tags cf pf coins tables draw partition program = .ok st` for
  some inputs, and `Zk.schedule st.m = .ok p`.
- **`classOk_of_accepts : AcceptsStmt st → ClassOk (shapeOf st)`**, from `Refine.setupH_wf` and `ClassOk.to_shape`.
  `execClassAt_of_accepts`: an accepted statement takes the `ofStmt` branch.
- In (i)'s proof:
  - at `¬ AcceptsStmt st` the event is empty (`prob_mono_outcome`, `prob_false`), so the fixed class adds no accepted
    case;
  - at an accepted statement, `compiledForkSound_execClassAt T CT (classOk_of_accepts hacc)` supplies `_hin`, through
    `compiledForkSound_of_fast100` and from `flock_inner_sound_compiled` (5b).
- **(ii) is unchanged, and the lemma isn't used there.** (ii)'s binders (`Out`, `Prog`, `rows`, `pub`, `msgs`, `view`,
  `sim`) mention neither the class nor the inner statement. Its simulator reads `regLeaves rows pub P r` and the owed
  outputs, so it has no fixed-class branch to cover. Making (ii) range over `st` as well (`Prog` the descriptions of
  `execClassAt st`'s class) would be a separate change. Tell me if top wants it.
- `HClass.ofStmt` at `nnz = 0` is the single public statement (`HClass.ofStmt_toStatement`), not the description
  class; `UniversalClass.lean` is where the class is every description. I used it in that sense.

### A.3 `_hS`

- **Why not `vstar_hS_withExec` as it stands:**
  - `VStmt.withExec` takes the tiling proof as an argument, so (i) would range over statements built from a proof;
  - `_hbr : VBridge` reads the model (`VFull` reads `law.σs` and `ks`), so `VBridge` at `Vs` is not `VBridge` at the
    `withExec` statements. The first build (b-ec2) failed there.
- **Instead:** `VStmt.exec` is `withExec` with the tiling decided inside, classically: the executable strata where they
  tile, the given model otherwise. (i) states everything at `execStmts Vs`.
- **The proof:** `VStmt.exec_execStrata` gives `ExecStrata` at `exec` wherever the strata tile. The tiling comes from
  one session of each statement:
  - `nonempty_reg₂`: a prover sends some registration;
  - `VStmt.tiles_of_session`, at that session's `DrawFileZK`, which `_hCust` supplies (`RecordCustodyZK` is
    `RecordsLiveZK ∧ DrawFileZK`).
- **Custody's population changed; flagging it.** `RecordCustody`'s draw file is now over `(Vs j).nv`, V*'s units, in
  place of `law.pop`; `tiles_of_session` needs that. With `pop_of_session`, it implies the registered public file's
  count is `nv`. That is what the verifier draws over, but it changes the premise's text.

### A.4 Class-fixed regions (top's acceptance tests)

Each of these lemmas makes a part of the class a function of `shapeOf st` alone:
- `execClassAt_cls : (execClassAt st).cls = clsOf (shapeOf st)`;
- `execClassAt_regs_length`: the region count, `if ClassOk (shapeOf st) then (shapeOf st).regions.size else 0`;
- `execClassAt_sch`: the schedule, `schedAt (shapeOf st).m`;
- `regionsOf_layout`: each region's free bits and fixed bits (its place in the block);
- `execClassAt_shape`: two statements of one shape have the same class, region count and schedule;
- `outerStatementsAt_shape` (`Audit.lean`): and V* lays out as many outer statements for them.

So the layout is the class's, and each private circuit's registration commit strings are instance data. They are the
regions' bytes, the only part of a region that `shapeOf` drops.

That is the lemma half of "two descriptions of one class give statements of the same shape": equal shape gives the same
class, layout and staging. **The other half isn't in Lean.** No Lean map from a universal-unit description to its
`Flock.Stmt` exists.
- The unit's circuit is pinned per class by digest (`test_the_unit_is_a_function_of_its_class`,
  `verity/ml/private_circuits/tests/test_boolean_universal.py`), so the circuit field agrees.
- The missing piece is a test that stages the unit (`verity_flock.class_statement.stage`) for two random descriptions
  and checks that everything but the regions' bytes agrees. It belongs in C-Flock's Python suite, and I haven't written
  it.

### A.5 Gap 3a's place

`_hop` is used once, at `hop o h.2.1 i hi` in (i)'s last case (`Audit.lean`, inside `hagree`). When
`Recursion.zk_reads_open` lands, it replaces that argument, and `_hop` leaves (i)'s binders. `Audit.lean`'s module doc
says so. I didn't write it.

### A.6 Evidence

All on n2 (`/workspace/research/lean-proofs/rec-lean`, through `../../../run`, cores 128–159). The commit was shipped
with `research run --on vy-nebius-2 --source . -- true` (**r20261009-183639-d22c**) and checked out from
`refs/research/src/a3e795ba3…`. The two build logs, the shape log and the shape script are
**`art:0952873a9102f6d1217e154547f0f90d844357d879f69b6216013a436f2afa40`** (preserved).

| what | commit | result |
|---|---|---|
| build `b20261009T1800Z-39c6.log` (`Proofs.Flock`) | 39c61f8ab (both merges) | 4846 jobs, no `error:`, no sorry outside ArkLib |
| **build `b20261009T1838Z-a3e7.log`** (`Proofs.Flock`) | **a3e795ba3** | `Build completed successfully (4847 jobs)`, no `error:`, no sorry outside ArkLib. The only warnings in the new file are the `dif_pos`/`if_pos` deprecations the tree is full of |
| **shape `shape-a3e7.log`** (`Facts.lean` over `Proofs.Flock.Recursive.Audit`'s closure, then `check.refusals`) | **a3e795ba3** | facts rc 0. `RecursiveAudit`'s axioms: `propext`, `Classical.choice`, `Quot.sound`. **4 refusals** (below) |
| **records audit r20261009-183956-7f58** (`lean_changed.py --records Security --update --out "$OUT/audit"`, Lean slot `build/0`, kept tree `lean-records/build-0`) | **a3e795ba3** | rc 1 by design, 2043 s (1986 s of it the audit). 7581 declarations, 220 guarantees, axioms the standard three. Its only failures are the same 4 shape refusals. A `lean-fast/v1` result (no kernel replay, no tests), which `check` and `research merge` don't accept as a verdict. Its `out/audit/` holds `review.txt` and the lock |

**Refusals, 8 before (§0.4) and 4 now:**
- (i): `L.nonempty`, the law's `Nonempty Ω` field. It is still a field of a direct input. It's the one left in (i).
- (ii), unchanged: no acceptance, `_hOuter`, `honest o P w`.
- Gone: `cls.hk`, `cls.hk6`, `cls.hm` and `_hS`. `_hin` was a binder, not a refusal, and it is gone too.
- (i)'s hypotheses before the acceptance `_hck` are now `L.nonempty` and `_hCust` (a premise).

**The `--update` diff** (`3e29b755e`, `Security/lean-audit.json`, +421/−58 lines). The run's lock has the
committed formatting, so this is the whole change:
- `guarantees`: only `Flock.SecurityProofs.RecursiveAudit` changes. It goes from `{"owner": "@proofs"}` to its first
  record: signature `Flock.SecurityProofs.RecursiveAudit : Flock.Guarantees.RecursiveAudit`, `assumptions: []`,
  `type_hash b20765ad…`. No other guarantee's record changes.
- `assumptions`: `FlockSoundness.Assumptions.Zk.RecordCustodyZK` (added in `a3e795ba3`, owner @proofs) gets its digest
  `2e0bf4d9…`.
- `reads`, eight new modules, read only by `RecursiveAudit`:
  - `Proofs.Flock.Recursive.ExecClass` (16 definitions), `Property` (9), `Premises` (4), `Compile` (5);
  - `Target` (21), `Schedule` (3), `Universal` (1), `VStarStrata` (2).
- `reads`, nine modules whose definitions change:
  - stale since the `Recursive/Defs` move: `Game.Outcome`, `StrictCR.Finder.Finds` and `FindsColl` move from
    `Recursive.Finds` to `Recursive.Defs`, and `contF` from `Recursive.Fork`;
  - stale since custody's split: `Recursive.Flock`, `ZkOuter`'s fields move to `ZkOuterD` (12 added, 8 gone, 12
    changed);
  - stale digests: `Recursive.Stage` (3) and `Statements` (2);
  - new with this commit: `Accounting.Schedule`'s `Inhabited` instance (`ExecClass.fixed`'s default schedule),
    `Model.tableCL`, and `RecordCustodyZK`.
- `reads`, readers: 193 more modules gain `RecursiveAudit` as a reader. Because of the Defs move,
  `RecursiveRanRegistered` and `RanRegisteredRun` now read `Defs` in place of `Finds`.
- `review.txt` (917 lines) lists `guarantee Flock.SecurityProofs.RecursiveAudit: new` and its definitions. It is the
  only guarantee entry. `RecursiveSound` and `RecursiveRanRegistered` read 34 of the changed definitions, all from the
  `ZkOuterD` split and the Defs move; their statements don't change. Daniel's DM, when this lands, is
  `RecursiveAudit`'s new statement and those definitions.

I didn't rerun the records audit at `3e29b755e`. The lock is what that build wrote, so a rerun would only repeat the
4 refusals.

No `maxHeartbeats` raised.

### A.7 Gap 8, scoped (not started)

What the checks already give, from `FailClosed/Scope.lean`:
- `_hck : ScopeZ I` gives `ht` (`ScopeZ.typed`), `hc` at `circZ I` (`ScopeZ.parse`, when `hiddenOutputs = false`),
  `hpub` at `pubZ I` (`ScopeZ.load`), and `hU` and `hscope` at `circZ I` (`ScopeZ.built`, `ScopeZ.scope`).

What stands in the way:
- `VStmt` fixes `c` per statement, and `Outer`/`OuterD`'s types, `rd`'s included, depend on `hU`, `hscope`, `ht`,
  `hc` and `hpub` as proofs. So taking these from `_hck` needs one of two changes:
  - the sessions become a total function of their raw inputs (`I`, `own`, `dj`, `S₀`, `wr`, the registered values),
    `execClassAt`-style: built when the checks pass, a refusing session otherwise; or
  - one equation per session, `circZ I = (Vs j).c` ("the verifier loads V*'s public circuit file"), stated as a check
    of the circuit file rather than as a field.
- `hDraw` is over every draw, not only accepted ones, and `hown` and `hTags` likewise sit outside the acceptance.
  Taking them from `AcceptsV` moves each under "at an accepted outcome", which touches `zk_session_regDrawnR`'s
  callers.

I'll take the second route for `hc`/`hU`/`hscope` unless you prefer the first. It is the smaller change and keeps the
soundness chain's types.

## 0. MAX_SLOTS and custody (Oct 9, 10:55 AM PDT)

Two decisions of Daniel's (9:01 AM PDT, relayed by top):
- `MAX_SLOTS` sets the number of outer statements, so the bound's sum depends on it. The part count is stated as a
  function of it and of the class.
- Custody becomes a named premise (rule 1: a fact about the world).

Commits on `cursor/rec-gap-list-35f2`, each pushed:
- `9b20b5bf4`: merges main (`MAX_SLOTS` = 160 since #1636).
- `ce5323e81`, `bc3394a34`, `7b41339d9`: the count. ce53 left `Fin S` in `wmsg`/`Sk`/`cmt`/`msg`; bc33 fixed those
  but also rewrote `VerifiesV`'s own `Fin S`; 7b41 restores it. The count is complete at `7b41339d9`.
- **`229d8661a`**: custody.

### 0.1 The part-count function

In `Property.lean`, after `innerExec` (namespace `Flock.Guarantees`; imports `Flock.RecResiduals`):

```lean
def outerParts (m kLog claims : ℕ) : ℕ :=
  match Flock.RecResiduals.shape? m kLog claims with
  | none => 0
  | some sh =>
    match Flock.RecAlgebra.structureOf sh >>= fun S =>
        Flock.RecResiduals.groups S (Flock.RecResiduals.portSizes sh) with
    | .ok gs => sh.sched.levels.size + gs.size
    | .error _ => 0

abbrev outerStatements (cls : HClass) (regs : List (FlockSoundness.Model.Region cls.kLog (cls.m - cls.kLog))) : ℕ :=
  outerParts cls.m cls.kLog (2 + 2 * regs.length)
```

It counts V*'s statements as the staging lays them out (`rec_vstage.stage`, `VStar.statements`) and as the verifier of
record groups them (`Flock.RecResiduals.groups`, `rec_residuals.parts`):
- **One `RecOpen` per Ligerito level of `fast100 m`.** That is 3 levels for `m ≤ 24`, then 4, 5 and 6 up to `m ≤ 27`,
  `30` and `33`, and 7 above.
- **One `InnerRepCheck` per part of the rep's algebra.** Each residual, in S's order, goes into the first part that
  stays within `MAX_SLOTS` sha512x3 slots, `MAX_REGIONS` (64) regions and 16 residuals.
- **The claims.** Two are the protocol's and two belong to each region (`Flock.Stmt.extraClaims`).
- **A shape the verifier refuses** has none: the count is 0 and V* stages nothing. The property at `Fin 0` is still
  a theorem, about runs V* never makes.

`MAX_SLOTS` enters only through `Flock.RecResiduals.groups`, the verifier of record's own constant. Changing it changes
the property's value and its record. The facts at 229d8661a list `Flock.RecResiduals.MAX_SLOTS`, `MAX_REGIONS`,
`groups`, `shape?`, `portSizes`, `Flock.RecAlgebra.structureOf`, `outerParts` and `outerStatements` among
`RecursiveAudit`'s reads. Once the lock records the guarantee, a change to any of them reaches Daniel's landing DM.

**The check.** A compiled Lean exe against the tree's own `Flock.RecResiduals` and `VStar.Stage`, with
`art:150c405dd59d83c8b054908415fe91764ffccb9bdf1d185ccc1e4c9aca6574ea` (Check.lean, lakefile, output). Layouts as
`rec-private.md` gives them:

| layout | regions, claims | shape | `outerParts` at 160 | the verifier's groups | the run's statements | at 128 slots |
|---|---|---|---|---|---|---|
| the 8090 run (2922), program-row layout | 3, **8** | m32-k27-c8 | **8** | 6 levels + 2 parts (residuals 0–9, 10–12) | L0–L5, alg-p0, alg-p1: **8** | 8 |
| the real-class path at 16,16,8 (2f10), the unit as the program's one Call | 5, **12** | m25-k22-c12 | **6** | 4 levels + 2 parts (0–12, 13–16) | L0–L3, alg-p0, alg-p1: **6** | refused |
| the small class (6720), program-row layout | 3, 8 | m25-k22-c8 | 6 | 4 + 2 (0–9, 10–12) | L0–L3, alg-p0, alg-p1: 6 | 6 |

Notes on the table:
- **The 128-slot refusal** is `residual 16 alone reads more than 64 regions or 128 sha512x3 slots`, the message the
  128-slot merged tree's Lean gave on 2f10's alg-p0/p1. The function tracks `MAX_SLOTS`: at 128 that layout has no
  statements, at 160 it has 6.
- **`claims = 2 + 2 · regions`** gives the 8 and the 12. The statement counts at those layouts are 8 and 6. The 12-claim
  layout has 6 statements, not 12. The re-verify table's "8" for 2f10 counts its two cheating parts as well.
- **The staging agrees.** At all eight shapes the exe ran, `outerParts` equals `VStar.statements`' count: the three
  above, m26-k23-c12 (6), m35-k32-c14 (11, with 7 levels and 4 parts), m22-k6-c2 (4) and m28-k20-c4 (7). At
  m35-k32-c15 both refuse: residual 19 needs more than 160 slots.

**Lines 81–83.** Neither the base's lines 81–83 (the docstring's "Taken: … `_hin` …", now 110–112, byte-identical) nor
the binders where `cls`, `regs` and `sch` are taken (98–100 at the base, 127–129 now) are in the diff. The only new
uses of `cls` are `outerStatements cls regs` in the indices. Under rec-thm's proposal (the property takes an executable
statement `st`), the count becomes `outerParts` at `st`'s `m`, `k_log` and regions, and the count change needs nothing
from those lines.

### 0.2 The bound as stated

(i)'s statements and sessions:

```lean
    {Vs : Fin (outerStatements cls regs) → VStmt}
    (zs₀ : Reg → L.Ω → List (Cm × (innerExec T CT cls regs sch).Coin) → Reg₂ →
      (j : Fin (outerStatements cls regs)) → (Vs j).OuterD Reg')
    (_hCust : Flock.Premises.RecordCustody zs₀)
```

`wmsg`, `Sk`, `cmt` and `msg` index by `j : Fin (outerStatements cls regs)` too. No `S` is bound any more.
`VerifiesV` keeps its own `{S}` (it is generic). The last disjunct:

```lean
      prob (fun o => VerifiesV (custodied zs₀ _hCust o.1 o.2.1 o.2.2.1) o.2.2.2 ∧
            ¬ (innerExec T CT cls regs sch).holds (stmt p o.2.1))
          (recGame L Reg (innerExec T CT cls regs sch) Cm fun R ω t =>
            outerV (custodied zs₀ _hCust R ω t) dg N) σ ≤
        expAt σ (fun ω t s => sumV (custodied zs₀ _hCust σ.1 ω t) dg N
            (fun R₂ j τ => (custodied zs₀ _hCust σ.1 ω t R₂ j).boundCR dg N (Vs j).law.model k Rw M ρ τ) s) +
          ((innerExec T CT cls regs sch).r : ℝ≥0∞) *
            expAt σ (fun ω t s => sumV (custodied zs₀ _hCust σ.1 ω t) dg N
              (fun R₂ j τ => (custodied zs₀ _hCust σ.1 ω t R₂ j).slackCR dg N k Rw M ρ τ) s) +
          ENNReal.ofReal (Accounting.tableError sch ⟨cls.kLog, regs.length, cls.mPts⟩)
```

`sumV` sums over `Fin (outerStatements cls regs)`. The bound is therefore V*'s `outerStatements cls regs` sessions'
expected bound, plus `r` times their stage slack, plus `tableError`, at any class and any `MAX_SLOTS`. §1 has the
whole statement.

### 0.3 Custody's new form

- **`ZkOuterD`** (`Recursive/Flock.lean`) is a session's data and checks: every field of the old `ZkOuter` but `hRec`.
  - The data: `I`, `own`, `dj`, `S₀`, `y₀`, `wr`, `pub`, `rd`.
  - The Prop fields:
    - `ht`: the tags are untyped;
    - `hc`: the circuit file parses to `c`;
    - `hpub`: the public file loads;
    - `hDraw`: `DrawOkZK` at every draw;
    - `hTags`: `TagsOk`;
    - `hown`: the reads at drawn rows are the verifier's own.
- **`ZkOuter`** is `ZkOuterD` with `hRec : RecordsLiveZK I dj wr`. Its fields are reached through the `extends`
  projections. Nothing in the tree builds or destructures a `ZkOuter`, so no lemma changed.
- **`VStmt.OuterD Q Reg'`** is `ZkOuterD Q.mPts Q.nv Reg' Q.c Q.hU Q.hscope Q.law.live`.
- **`Flock.Premises.RecordCustody zs₀`** (`Premises.lean`, `live-verifier`) is `∀ R ω t R₂ j,
  FlockSoundness.Assumptions.Zk.RecordCustodyZK (zs₀ …).I (zs₀ …).dj (zs₀ …).wr (.stratified (Vs j).law.Kd
  (Array.ofFn (Vs j).law.St)) (Vs j).law.pop`. That is the named assumption, `RecordsLiveZK ∧ DrawFileZK`, at each
  session, under its law's executable strata over its population.
- **`Flock.Guarantees.custodied zs₀ h`** builds the sessions `{ toZkOuterD := zs₀ R ω t R₂ j, hRec := (h R ω t R₂ j).1 }`.
  Every use of the old `zs` now reads `custodied zs₀ _hCust`: in σ's game, `_hck`, `_hop`, `_hx`, `_hr`, `_hbr`, the
  forks, the run-tied break and the bound. `Audit.lean` passes `custodied zs₀ hCust` to
  `zk_sessions_recursive_fork_inner`; the proof is otherwise unchanged.
- **What the shape check sees.** `_hCust` is a binder with head `Flock.Premises.RecordCustody`, module
  `Proofs.Flock.Recursive.Premises`, so it is a premise, as `_hA3` is after 8b. `RecordsLiveZK` reaches `AcceptsZK`, but
  the check picks the acceptance only among hypotheses that aren't premises, so `_hck` stays the acceptance.
- **The proof uses only the record half today.** The draw-file half has the form of the `hdj` that gap 7's
  `vstar_hS_of_sessions` takes. With U2, it is what can discharge `_hS`.
- **Still hidden.**
  - `ZkOuterD`'s Prop fields `ht`, `hc`, `hpub`, `hDraw`, `hTags` and `hown`, and `VStmt`'s `hU` and `hscope`, sit
    under the function-typed binders `zs₀` and `Vs`, so the check doesn't extract them. Each is a verifier check, not a
    fact about the world: gap 8 derives `hDraw`/`hTags`/`hown` from `AcceptsV` and `hU`/`hscope` from `_hck`, and
    `ht`/`hc`/`hpub` are the parse and load the verifier does at setup.
  - Custody was the only world fact among them.
- **To record with the lock.** `FlockSoundness.Assumptions.Zk.RecordCustodyZK` is not under `assumptions` in
  `Security/lean-audit.json` (`RecordCustodyZKJ` is). `_hCust` depends on `zs₀`, so the closed-Prop rule doesn't ask
  for it. It should still go in with its claim id (`live-verifier`, owner @proofs) when `--update` records
  `RecursiveAudit`. I haven't run that audit (§0.4).

### 0.4 Builds and the shape

All on n2, in `/workspace/research/lean-proofs/rec-lean` through `../../../run` (cores 128–159). Each commit was shipped
with `research run --on vy-nebius-2 --source . -- true` and checked out from `refs/research/src/<sha>`. The three
229d8661a logs and the shape script are
`art:bfcf6131fe58018ca2a86ef4441e7307be839896dcbc58cafdbe76b3bb72f095`.

| what | commit | result |
|---|---|---|
| ship r20261009-170924-6098, build `b20261009T1713Z-ce53.log` | ce5323e81, then 229d8661a mid-build (ship r20261009-172159-7b6e) | `Build completed successfully (4620 jobs)`, no `error:`. `Refine.Setup` alone took 1072 s. The checkout moved under it, so it isn't one commit's result |
| **build `b20261009T1743Z-229d.log`** | **229d8661a** | rc 0, `Build completed successfully (4618 jobs)`. It re-elaborated exactly `Recursive.Flock` (8.0 s), `Premises`, `Property` and `Audit`. The one sorry warning in the tree's own files is 5b's `Compile.lean:87`; two more come from ArkLib's own files, replayed |
| **shape `shape-229d.log`** (`Facts.lean` over `Proofs.Flock.Recursive.Audit`'s closure, then `check.refusals` against `Security/lean-audit.json`'s entry) | **229d8661a** | facts rc 0. `RecursiveAudit`'s axioms: `propext`, `Classical.choice`, `Quot.sound` (**no `sorryAx`**). Eight refusals, the ones 6dee gave (next) |
| **build `b20261009T1748Z-229d-umbrella.log`** (`Proofs.Flock.Recursive`, `Proofs.Flock`: the umbrellas, the only importers of the changed modules outside `Audit`'s closure) | **229d8661a** | `Build completed successfully (4839 jobs)`, no `error:`. The one sorry warning outside ArkLib is `Compile.lean:87` |
| r20261009-151624-6dee (vy-nebius-1, fast path, queued 15:17Z, ran from about 16:24Z to 17:02Z) | 206ad11b8 | rc 1 by design. Security: eight failures, all shape refusals. Proofs: one, the sorry list: 5b's `flock_inner_sound_compiled` and its four dependents, **not `RecursiveAudit`**. 8b confirmed: `_hA3` is no longer refused |

**Shape refusals left (eight, unchanged by both jobs):**
- (i), five:
  - `L.nonempty`;
  - `cls.hk`, `cls.hk6` and `cls.hm` (gap 4, or rec-thm's executable statement);
  - `_hS`, which now reads `∀ j : Fin (outerStatements cls regs), …` (gap 7; custody's draw-file half and U2 discharge it).
- (ii), three:
  - no acceptance;
  - `_hOuter`;
  - `honest o P w`.
- `_hCust` is not among them.

**Not run:** the Security audit at 229d8661a (`lean_changed.py --records Security --update`), which records
`RecursiveAudit` in the lock. 6dee's audit stage took 40 minutes after a 70-minute wait for node 1's slot, and builds
go to n2 today. It is the next run to queue when you want the lock.

**For infra, from n2's run script.** `../../run lake build …`, as the script's comment says, fails with `Failed to
find executable lake`: systemd-run's PATH has no `~/.elan/bin`. `../../../run /home/research/.elan/bin/lake build …`
works.

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
    {n : ℕ} {L : Law n} {Reg Cm : Type} {Reg' Reg₂ : Type}
    -- the class of the compiled table, its regions and schedule
    (cls : HClass) (regs : List (FlockSoundness.Model.Region cls.kLog (cls.m - cls.kLog)))
    (sch : Accounting.Schedule)
    -- V*'s statements over the class, and V*'s sessions' data at each history and registration `R₂`
    {Vs : Fin (outerStatements cls regs) → VStmt}
    (zs₀ : Reg → L.Ω → List (Cm × (innerExec T CT cls regs sch).Coin) → Reg₂ →
      (j : Fin (outerStatements cls regs)) → (Vs j).OuterD Reg')
    -- the records' custody
    (_hCust : Flock.Premises.RecordCustody zs₀)
    (dg : ByteArray → ByteArray) (N : ℕ)
    -- the recursive prover
    (σ : Strategy (recGame L Reg (innerExec T CT cls regs sch) Cm fun R ω t =>
      outerV (custodied zs₀ _hCust R ω t) dg N))
    -- the hidden statement, the messages V*'s layers hold, the rounds' commit strings and commitments
    (x : Reg → L.Ω → Hidden cls)
    (wmsg : ((j : Fin (outerStatements cls regs)) → (Vs j).Bits) → List (innerExec T CT cls regs sch).Msg)
    (Sk : ℕ → (j : Fin (outerStatements cls regs)) → Finset (PosK (Vs j).c (Vs j).hU (Vs j).nv))
    (cmt : (j : Fin (outerStatements cls regs)) → Cm → PosK (Vs j).c (Vs j).hU (Vs j).nv →
      (obK (Vs j).c (Vs j).hU (Vs j).nv).Dg)
    (msg : ℕ → ((j : Fin (outerStatements cls regs)) → PosK (Vs j).c (Vs j).hU (Vs j).nv → ValK (Vs j).c) →
      (innerExec T CT cls regs sch).Msg)
    -- the registration's root; a netlist's statement by its rows' commit strings; the rows a run read, and the commit
    -- strings and openings of `rt` it carries
    (rt : Flock.Registered.Port) (stmt : (ℕ → ByteArray) → L.Ω → Hidden cls)
    (reads : Reg × L.Ω × List (Cm × (innerExec T CT cls regs sch).Coin) ×
      (Reg₂ × VRec Vs Reg' dg N) → ℕ → Prop)
    (row : Reg × L.Ω × List (Cm × (innerExec T CT cls regs sch).Coin) ×
      (Reg₂ × VRec Vs Reg' dg N) → ℕ → ByteArray)
    (op : Reg × L.Ω × List (Cm × (innerExec T CT cls regs sch).Coin) ×
      (Reg₂ × VRec Vs Reg' dg N) → ℕ → Flock.Registered.Port × ByteArray × ByteArray)
    -- V*'s laws' strata
    (_hS : ∀ j, Law.ExecStrata (Vs j).law.σs (Vs j).law.ks (Vs j).law.St)
    -- the verifier of record's statement check accepts V*'s statements
    (_hck : ∀ R ω t R₂ j, FailClosed.ScopeZ (custodied zs₀ _hCust R ω t R₂ j).I)
    -- A3
    (_hA3 : Flock.Premises.UniformRandomBytes Vs)
    -- the compile lemma
    (_hin : Flock.Premises.CompiledForkSound T CT cls regs sch)
    -- at an outcome whose sessions all verify, every read commit string opens `rt`, and the hidden statement is theirs
    (_hop : ∀ o, VerifiesV (custodied zs₀ _hCust o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ i, reads o i →
      (regBcCommit i).Opens rt (row o i) (op o i))
    (_hx : ∀ o, VerifiesV (custodied zs₀ _hCust o.1 o.2.1 o.2.2.1) o.2.2.2 → ∀ q : ℕ → ByteArray,
      (∀ i, reads o i → q i = row o i) → x o.1 o.2.1 = stmt q o.2.1)
    -- the registered commit strings and the developer's openings
    (p : ℕ → ByteArray) (op₀ : ℕ → Flock.Registered.Port × ByteArray × ByteArray)
    (_hreg : ∀ i, (regBcCommit i).Opens rt (p i) (op₀ i))
    -- the count curve, bounding every session's rate
    {k Rw M : ℕ} (_hk : 1 ≤ k) (_hRw : 1 ≤ Rw) (_hM : 1 ≤ M) {ρ : ℝ} (_hρ : ρ < 1)
    (_hr : ∀ R ω t R₂ j S' R' i, rateZ (planZAt (Reg := Reg') (custodied zs₀ _hCust R ω t R₂ j).dj
      (custodied zs₀ _hCust R ω t R₂ j).y₀ S' R') i k ≤ ρ)
    -- V*'s bridge
    (_hbr : Flock.Premises.VBridge (custodied zs₀ _hCust) dg N k Rw x wmsg Sk cmt msg),
    RoundFork (custodied zs₀ _hCust) dg N k Rw σ cmt ∨ SessionFork (custodied zs₀ _hCust) dg N k Rw M σ ∨
      InnerForkRec (custodied zs₀ _hCust) dg N k Rw σ x wmsg Refine.H512
        (clashPickCL T CT execArith Refine.H512 Refine.enc512 Refine.leaf512 cls regs sch) ∨
      (∃ o, FlockSoundness.Game.Outcome (recGame L Reg (innerExec T CT cls regs sch) Cm
          fun R ω t => outerV (custodied zs₀ _hCust R ω t) dg N) σ o ∧
        VerifiesV (custodied zs₀ _hCust o.1 o.2.1 o.2.2.1) o.2.2.2 ∧
        ∃ i, reads o i ∧ row o i ≠ p i ∧ FlockSoundness.Binding.Collides ((regBcCommit i).ext (op o i) (op₀ i))) ∨
      prob (fun o => VerifiesV (custodied zs₀ _hCust o.1 o.2.1 o.2.2.1) o.2.2.2 ∧
            ¬ (innerExec T CT cls regs sch).holds (stmt p o.2.1))
          (recGame L Reg (innerExec T CT cls regs sch) Cm fun R ω t =>
            outerV (custodied zs₀ _hCust R ω t) dg N) σ ≤
        expAt σ (fun ω t s => sumV (custodied zs₀ _hCust σ.1 ω t) dg N
            (fun R₂ j τ => (custodied zs₀ _hCust σ.1 ω t R₂ j).boundCR dg N (Vs j).law.model k Rw M ρ τ) s) +
          ((innerExec T CT cls regs sch).r : ℝ≥0∞) *
            expAt σ (fun ω t s => sumV (custodied zs₀ _hCust σ.1 ω t) dg N
              (fun R₂ j τ => (custodied zs₀ _hCust σ.1 ω t R₂ j).slackCR dg N k Rw M ρ τ) s) +
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

(At 229d8661a, §0.) The order is deliberate. Inputs come first, with custody `_hCust` (a premise) right after the
sessions' data `zs₀` it is about, then the hypotheses (`_hS` … `_hx`). The first input after the acceptance (`p`)
starts the conclusion, so
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
| `Flock.Premises.RecordCustody` (since 229d8661a; before, the hidden field `ZkOuter.hRec`) | `live-verifier`, `FlockSoundness.Assumptions.Zk.RecordCustodyZK` at every one of V*'s sessions: the record the verifier reads is the live session's (`RecordsLiveZK`), and its draw file is the law's stratified draw (`DrawFileZK`) | **no, unlisted**; now a named premise the shape check sees (§0.3) |

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
| 5a | `FlockSoundness.Discharge.Recursion.zk_sessions_recursive_fork_inner` (`Compile.lean`) | the recursive audit is sound with the inner protocol sound in fork form (`InnerSoundForkOn`), the inner fork a third disjunct | **proved, built, no sorry of its own** (`Recursive/ForkInner.lean`, 597 lines, new; statement unchanged). Built by r20261009-150624-7c69 at f20051ec9; merged into this branch (206ad11b8). Details under the table | proofs (me), done |
| 5b | `FlockSoundness.Discharge.Recursion.flock_inner_sound_compiled` (sorry, `Compile.lean`) | C-Flock's compiled table is sound in fork form at `tableError`; discharges `CompiledForkSound` | rec-thm's sizing | proofs (rec-thm) |
| 6 | VBridge G: `AlgebraDecodes` (G1–3), `AccChains` (G4), `StagesAccept` (G5), `VCommits`, `VDecodes`, `VFull` (G6), the hypotheses of `FlockVBridge.Compiled.vbridge_compiled` (`cursor/vbridge-g-compose-741b`, 3ada41b93, no sorry there) | V*'s circuits compute C-Flock's inner verifier at `flockInnerCL`; discharges `VBridge` | lean's sizing | lean |
| 3a | `Recursion.zk_reads_open` (proposed) | `_hop`: at an outcome whose sessions verify, each registered read's commit string opens the registration's root at its row; from `ZkOuter.rd` and `checkRegistered` via `zk_session_regValsR` / `RegForkZC`, with `reads`, `row`, `op` defined from the outcome | ~150 | proofs |
| 3b | `Recursion.hidden_of_reads` (proposed) | `_hx`: the hidden statement V*'s sessions decode at that outcome is the read strings' netlist's | ~120 | proofs |
| 2 | `Recursion.vstar_outer_zk` (proposed; `_hOuter` from `ZeroKnowledgeHidden`) | V*'s outer sessions are ZK within `ε_o` with a simulator reading the owed outputs, the registration's view, the auditor's tape and the commitments. Sub-gaps: the tape (~250); the self-check abort, which needs `InnerHolds` (~200); `avoidsMask` (~10, from `DrawSetupZHJ.avoidsMask`); `ZkViewAtJ` → `prCoin` (~150); hiding of `R₂` (~120) | ~730 | proofs |
| 4 | `Recursion.audit_at_universal` (proposed) | the instantiation: `cls`, `regs`, `sch` at `UniversalUnit_v1`'s class (with `fast100` and `LinkLayout`, discharging `CompiledForkSound` from 5b); `L` and `Vs` at V*'s laws (`_hS`, the count curve `_hr`); `honest`/`msgs`/`view`/`sim` at the Lean ZK server (`Flock.Firewall.run`'s sends), so that (ii) is about a function | ~300 | proofs |
| 7 | `Recursion.vstar_execStrata` (proposed) | `_hS`: V*'s laws' executable strata are their model's | ~50 | proofs |
| 8 | `ZkOuterD`'s Prop fields (`ht`, `hc`, `hpub`, `hDraw`, `hTags`, `hown`) and `VStmt`'s `hU`/`hscope` | each a verifier refusal: `hU`/`hscope` from `_hck` (`FailClosed.Checks.built`/`.scope`); `hDraw`/`hTags`/`hown` from `AcceptsV`; `ht`/`hc`/`hpub` the setup's parse and load. Custody (`hRec`) left them at 229d8661a for the named premise `_hCust` (§0.3) | ~200 | proofs |
| 8b | `Flock.Premises.UniformRandomBytes` over `Vs` | A3 for all of V*'s laws as one premise, so the shape sees `_hA3`'s head (the check's refusal, §5) | 4 (`Premises` 3, `Property` 1) | proofs (me), in: 42570924e; its shape verdict is r20261009-151624-6dee's |
| 8c | the shape's refusals of `cls.hk`/`hk6`/`hm` and `L.nonempty` | gone with gap 4; `Nonempty` might better be exempted by the check | 0 beyond gap 4 | lean (the check), with gap 4 |

**Gap 5a, done (Oct 9, 8:45 AM PDT).** Branch `cursor/rec-fork-inner-35f2`, off cf682258e, head f20051ec9 (pushed,
merged into this branch at 206ad11b8). The
statement of `zk_sessions_recursive_fork_inner` is unchanged, so `RecursiveAudit` is unaffected. `Compile.lean`
changes only by importing `Recursive/ForkInner.lean` and replacing the sorry. The proof follows the lemma's docstring:
- **The chain, restated at the prover's own leaves.** The chain reads `InnerSound` once, in `commit_and_prove_upto`'s
  inner term. `InnerAtLeaves` is that use as a hypothesis: at each false statement, the leaves' average of
  "the relabelled transcript is accepted, and some outcome the leaf reaches accepts and decodes to it" is at most
  `εin`. The chain is copied with that hypothesis, for every choice of reference openings, and with the inner verifier
  reading each round's message whole (`same` is `Eq`, as `Flock.Assumptions.VBridge` has it): `commit_and_prove_on`,
  `recursive_sound_on`, `zk_sessions_recursive_upto_on`, `_full_on` and `_fork_on`, with `prob_mono_reached` and
  `option_eq_of_rel`.
- **The bridge, `innerAtLeavesV_of_forkOn`.** `InnerSoundForkOn` at `refStrat` and `G := AtLeaf …`, the transcripts
  whose coins reach a leaf of σ where an accepted outer outcome decodes to them. Its parts:
  - `AtLeaf` (σ's leaf at a transcript's coins);
  - `leafAvg_relabel_at` (`leafAvg_relabel` carrying a leaf predicate);
  - outcome lemmas for `bind`, `map`, `twoRuns` and `contF`, with `outcome_contF_ref`;
  - `finds_forkG_ref`: a fork of `refStrat` on `G`-transcripts is a fork of σ at the same coins, which
    `InnerForkRec` names.

How it got built (fast path on vy-nebius-1, §7):
- r20261009-135601-c44f (4f4d68eda) failed on a parse error: `set Z`, where `Z` is a token.
- r20261009-143759-4cd3 (bb741d096) had one error, a `whnf` heartbeat timeout in the bridge's `hVT`: unifying
  `Game.map ?f ?g` with `(T t s').g` unfolded `map` and `bind` into V*'s `outerV`. f20051ec9 states the step as
  `outcome_oneRun`, about `(StrictCR.oneRun g s pick).g` itself, so the match is syntactic.
- **r20261009-150624-7c69 (f20051ec9)** has no `error:` line. `Proofs.Flock.Recursive.ForkInner` built in 6.3 s and
  `Compile` in 4.3 s, and the build's one `sorry` warning is `Compile.lean:87`, 5b's `flock_inner_sound_compiled`. The
  Proofs audit's `sorryAx` list has five names, 5b's lemma and the four that use it:
  - `flock_inner_sound_compiled`;
  - `flock_inner_sound_compiled_fast100`;
  - `flock_inner_sound_compiled_plain`;
  - `recursive_sound_compiled`;
  - `recursive_sound_compiled_fast100`.

  `zk_sessions_recursive_fork_inner` and everything in `ForkInner.lean` are absent from that list. The Security audit
  passed (276 guarantees). This is a `lean-fast/v1` result, without the kernel replay; the full audit replays it.

No `axiom`, `native_decide` or kernel bypass was added.

**Duplicate generic lemmas, against the two 5b routes.** No full name clashes, and my branch merges textually clean
with each route. In both routes the generic lemmas sit in `FlockSoundness.Game` or `StrictCR`; mine are in
`FlockSoundness.Discharge.Recursion`, where namespace resolution prefers them. The duplicates:

| mine (`Recursion.`, `ForkInner.lean`) | `cursor/rec-compile-sound-2261` (`CompiledFork.lean`) | `cursor/rec-compile-sound-41ef` (`ForkRuns.lean`) |
|---|---|---|
| `outcome_bind` | `Game.outcome_bind` | `Game.Outcome.bind_of` |
| `outcome_map` (implicit `a`) | `Game.outcome_map` (explicit `a`) | `Game.Outcome.map_of` |
| `outcome_twoRuns` | `StrictCR.twoRuns_outcome` | — |
| `prob_mono_reached` | — | `Game.prob_mono_outcome` (the same statement) |

`outcome_contF_ref` overlaps both routes' `outcome_contF`, but it is not a duplicate: it carries the relabelling at
`refStrat`. `outcome_of_bind`, `outcome_of_map`, `outcome_oneRun`, `outcome_of_twoRuns`, `ite_one_zero_iff` and
`option_eq_of_rel` appear in neither route.

Two hazards for whoever lands 5b:
- The two routes clash with each other at the same full name, `Recursion.outcome_contF` (and both define an
  `Inner.fork_of_outcomes`), and they conflict textually in `Compile.lean`. Only one route can land as is.
- A file that opens both `Recursion` and `Game` outside the `Recursion` namespace sees `outcome_bind` and
  `outcome_map` as ambiguous. No file does that today.

Once one route lands, the clean-up is to keep its `Game.*` names and delete my four duplicates; their proofs are a
few lines each.

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

**Now eight, not nine.** `_hA3` went with 8b (6dee at 206ad11b8, and the replay at 229d8661a, §0.4). The tables below
are 50dc's nine, and every other entry is unchanged.

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
| `_hA3 : ∀ j, Flock.Premises.UniformRandomBytes …` | the premise sits under `∀ j`, so the hypothesis has no head constant and the check doesn't see it as a premise | a premise over all of V*'s laws at once (`Flock.Premises.UniformRandomBytes Vs := ∀ j, …`), about 3 lines in `Premises` plus 1 in the property; or the check reading through a leading `∀`. **Fix 8b, in at 42570924e**: `_hA3 : Flock.Premises.UniformRandomBytes Vs`, whose head is a constant of `Proofs.Flock.Recursive.Premises` (`Facts.lean` reads the head with `getAppFn`). I replayed `check.refusals` on r20261009-122359-50dc's facts with that head substituted: 9 refusals become 8, and `_hA3` is gone. r20261009-151624-6dee checks it on the real facts |
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
- (i) passes after gaps 4 and 7. Fix 8b, the `_hA3` premise over `Vs`, is in.
- (ii) needs gaps 2 and 4 and the ruling.

No `frozen` entry is needed or added for `RecursiveAudit`; it's under `shape.properties`.

## 6. What the property still doesn't say, against the brief

- **Not in `Security/Properties/`**, and its premises are not in `Definitions/` (§1); both wait on C-Flock's spec being
  extracted.
- **Three premises the brief didn't list:** A3, `hash-derived-key`, and custody (`Flock.Premises.RecordCustody`, named
  since 229d8661a; before that, the hidden field `ZkOuter.hRec`).
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
  - The Prop fields of `VStmt` and `ZkOuterD` sit under a function-typed binder (`Vs : Fin (outerStatements cls regs) →
    VStmt`, `zs₀ : … → OuterD`), so the check doesn't extract them. Custody no longer hides there (§0.3).
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
| r20261009-135601-c44f | 4f4d68eda (`cursor/rec-fork-inner-35f2`) | gap 5a, fast path, cold slot | `ForkInner`'s chain elaborated; one parse error (`set Z`), so `commit_and_prove_on`'s body and `Compile` unbuilt (§4, gap 5a) |
| r20261009-140957-0943 | 7b64d29d3 | gap 5a, fast path | cancelled by me before it took the slot: its tree had the same parse error |
| r20261009-143759-4cd3 | bb741d096 | gap 5a, fast path, the whole proof | rc 1. One error: a `whnf` heartbeat timeout in `innerAtLeavesV_of_forkOn`'s `hVT` (`ForkInner.lean:575`), so `Compile` unbuilt (§4, gap 5a) |
| **r20261009-150624-7c69** | **f20051ec9** (head of `cursor/rec-fork-inner-35f2`) | gap 5a, fast path | rc 1 by design, no `error:` line. `ForkInner` and `Compile` built; the build's one `sorry` is 5b's (`Compile.lean:87`). `sorryAx` reaches only 5b's lemma and its four dependents (§4, gap 5a). Security audit PASS |
| **r20261009-151624-6dee** | **206ad11b8** | fast path: 8b's shape, 5a merged | rc 1 by design (it got the slot about 16:24Z and ended at 17:02Z). Security: eight failures, all shape refusals (§0.4); `_hA3` is no longer refused. Proofs: the sorry list only, 5b's lemma and its four dependents; `RecursiveAudit` is not on it. Its outputs are on node 1 under the run's `lean-audit/` (the VM's copy lacks them) |
| n2 builds and the shape replay (§0.4) | ce5323e81 / **229d8661a** | ships r20261009-170924-6098 and r20261009-172159-7b6e; logs `b20261009T1713Z-ce53.log`, `b20261009T1743Z-229d.log`, `shape-229d.log` and `b20261009T1748Z-229d-umbrella.log` in `/workspace/research/lean-proofs/` on n2; 229d8661a's three as `art:bfcf6131fe58018ca2a86ef4441e7307be839896dcbc58cafdbe76b3bb72f095` | 229d8661a builds with no error and no new sorry; the shape check gives the same eight refusals; `RecursiveAudit`'s axioms are the standard three |

The guarantee lock has no record of `RecursiveAudit` on the branch yet. The run's `--update` lists the statement and
the definitions it reads as new (`audit-Security/review.txt`). The run's copy of the lock is formatted differently
(a diff of about 28,000 lines), so I left it out; the lock will go in when this lands.
