---
id: proofs/20261009T1605Z-report-rec-gaps-4-7
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: cursor/rec-gaps-4-7-2261
---

CHECKPOINT none (16:15Z) [open] 16:15Z: Daniel's four decisions in; premises classified (A3 and custody stay; hash-derived-key can go via per-session OS key for C-Flock --zk); class in Lean and OS salts staffed
CHECKPOINT none (16:06Z) [open] 16:07Z: rec-thm: 5b fallback builds with one lemma open; gap 7 lemma built, U2 tiling next (+300-400); gap 4 re-estimated 700-900; asked top on executable-statement property
# Gaps 7 and 4 of the recursive audit, and the compile branch's build

For proofs (bc-8416bc72), from rec-thm, Oct 9, 8:55 AM PDT. No PR opened; nothing landed; no Slack.

## Answers

**(1) Yes.** `cursor/rec-compile-sound-2261` at **4cee924bc** builds with exactly one `sorry` of its own,
`compiled_clash_or_value`. Run r20261009-145235-f591 says "Build completed successfully (5421 jobs)", and its audit
fails on `sorry` alone. The direct `sorry` warnings are `CompiledFork.lean:199`, and `Compile.lean:117` (gap 2,
rec-lean's 5a). The earlier lint warning on `fork_of_clashCL` is gone.

**(2) Gap 7's lemma closes tonight, and is built. Gap 4 does not close tonight.**
- **Gap 7.** `vstar_execStrata` is proved with no `sorry`. But it removes `_hS` from the property only once `Vs`'s laws
  are built from their executable strata (`VLaw.ofExec`). That needs a tiling fact, which comes either from the
  verifier's U2 strata check (about 300–400 lines) or from fixing V*'s statements (gap 4). The 50-line estimate covered
  the lemma, not the removal.
- **Gap 4.** Its compile-premise part is done, as lemmas: `CompiledForkSound` follows from
  `flock_inner_sound_compiled` at the class of an executable statement. What's left needs a ruling before it touches
  `Property.lean`, plus about 600–800 lines (§3).

**Shape refusals gone: none yet.** `Property.lean` and `Audit.lean` are unchanged on this branch. §4 says which
refusal each new lemma removes once it's wired in.

## Branches and builds

All builds ran on vy-nebius-1 via `research run … lean_changed.py --records Security/Proofs`.

| branch | head | run | verdict |
|---|---|---|---|
| `cursor/rec-compile-sound-2261` (off cf682258e) | **4cee924bc** | r20261009-145235-f591 | built (5421 jobs); audit FAIL on `sorry` only, as expected |
| `cursor/rec-gaps-4-7-2261` (new, off rec-lean's `cursor/rec-gap-list-35f2` at 2f4b0235b) | e2d0d2903 | r20261009-150817-1474 | built (5428 jobs); audit FAIL on `sorry` only. `VStarStrata` has no warnings; `Universal` had one style warning (`letI` → `let`) |
| same | 55ac7bf97 | r20261009-152731-3e20 | waiting for the build slot at 9:01 AM PDT, behind r20261009-150904-ae90 (another lane's run, holding the slot since 15:50Z) and r20261009-151624-6dee; adds `HClass.ofStmt`, `compiledForkSound_ofStmt`, `_ofSchedule` |
| same | **efc84f720** (head) | r20261009-155056-c3ba | queued after it; the `let` fix only |

Read the two pending runs with `research fetch RUN --all`, then look at `out/records.log`. While a run is still
running, `--all` can fail on a tar race (`resources.jsonl` changes as it is read). Plain `research fetch RUN` still
reports its status.

On r…-1474, the audit's `sorryAx` users are:
- `RecursiveAudit`;
- `flock_inner_sound_compiled` and its corollaries;
- `zk_sessions_recursive_fork_inner`;
- `compiledForkSound_of_fast100`, which is new and reaches `sorryAx` only through `flock_inner_sound_compiled`.

No declaration of `VStarStrata` is on the list.

## 1. Gap 7: `_hS` (`Security/Proofs/Flock/Recursive/VStarStrata.lean`, new, about 150 lines, no `sorry`)

**Why `_hS` doesn't follow from anything the verifier checks.** `VLaw`'s model fields (`σs`, `ks`) and its executable
strata (`St`) are independent fields. `σs` exists only in the model, so no acceptance can say anything about it. Even
the draw file is tied to `St` only through the custody premise `DrawFileZK`, which `ZkOuter` doesn't carry (it has
`RecordsLiveZK` and `DrawOkZK`). So for an arbitrary `VLaw`, the only way to get `_hS` is to read the model off `St`.

What is proved:
- `Law.Tiles S n` says the executable strata tile the units `[0, n)`. Its four fields:
  - each stratum draws at most its size;
  - its `j`-th unit, for `j` below its size, is a unit;
  - distinct `j` give distinct units;
  - every unit belongs to exactly one stratum.

  `Tiles.stratumOf` sends a unit to the stratum holding it.
- `Tiles.execStrata : ExecStrata h.stratumOf (fun s => (S s).k) S`.
- **`Law.execStrata_iff`** is the converse. Given `k s ≤ |σ⁻¹ s|`, `ExecStrata σ k S` holds if and only if `S` tiles,
  `σ` is `stratumOf` and `k` is the strata's own counts. So `_hS` says exactly that, and nothing more.
- `VLaw.ofExec St hT Kd pop Ω Lb src` is a law of V*'s units with its model read off tiling strata.
  **`vstar_execStrata`** proves `_hS` at it.
- `VLaw.execStrata_iff`: a `VLaw` satisfies `_hS` if and only if its strata tile and its model is the one `ofExec`
  builds. Requiring V*'s laws to come from `ofExec` therefore loses nothing.

**What still removes `_hS` from the property.** `Tiles` must come from the executable. Two routes:
- **The verifier's U2 check** (`Flock.Draw.UnitDraw.ofJson` refuses a stratified draw whose strata don't tile the
  population). Proposed lemma: `Recursion.tiles_of_strataProblem`. Its parts:
  - from `strataProblem k (Array.ofFn St) nv = none` and `stratumOfJson`'s range checks (non-empty, ascending, disjoint,
    not adjacent) to `Law.Tiles St nv`;
  - the loop semantics of `Stratum.size` (a `foldl`) and `Stratum.unit` (a loop with an early return), about 120 lines;
  - `qsort` as a permutation, plus the contiguous tiling giving a disjoint cover, about 150 lines;
  - tying `St` to the parsed draw (`mapM stratumOfJson`, `DrawFileZK` with `pop = nv`), about 100 lines.

  About 300–400 lines in total. `DrawFileZK` then has to be a premise or a `ZkOuter` field, which is a choice for
  rec-lean.
- **V*'s statements fixed** (gap 4): each law is `VLaw.ofExec` at V*'s own strata, and `Tiles` is a fact about them.

## 2. Gap 4, done: the compile premise at a class (`Security/Proofs/Flock/Recursive/Universal.lean`, new, about 90 lines, no `sorry`)

- `compiledForkSound_of_fast100`: `Flock.Premises.CompiledForkSound T CT cls regs sch` from `fast100 cls.m = some sch`
  and `LinkLayout`. It is `flock_inner_sound_compiled` as stated, at `execArith_correct` and hm96-sha512, so whichever
  5b route closes that lemma closes this.
- `fast100_some`: `fast100 m` is a schedule for every `22 ≤ m ≤ 35`.
- `HClass.ofStmt st hwf hm slotLog units nnz`: the class of an executable statement.
  - Its public part is the statement's `m`, `k_log`, pin and matrices: `Refine.matA` and `Refine.matB`, as
    `Refine.stmtOf` reads them.
  - The hidden template's geometry is supplied as data.
  - Its link layout is at `PT_LOCAL` and the statement's link points.
- `compiledForkSound_ofStmt` and `compiledForkSound_ofSchedule`: `CompiledForkSound` at that class, at
  `Refine.regionsOf st` and the statement's `fast100` schedule.
  - `LinkLayout` reads only the regions and the block bits, never the matrices. So it is
    `Refine.stmtOf_linkLayout` at every hidden template.
  - The schedule comes from `ZkHidden.fast100_of_schedule` and `Refine.fast100_schedOf`.
  - What's left is the executable's own checks of the statement: `StmtWF`, `RegionsWF` (what setupH's acceptance
    gives) and `Zk.schedule st.m` accepting.

These are in r…-3e20, which hasn't finished. Only `compiledForkSound_of_fast100` and `fast100_some` are built so far
(r…-1474).

## 3. Gap 4, not done, and why

There is no `UniversalUnit_v1` class in Lean. `HClass` holds the lowering's \(2^{k_{\log}} \times 2^{k_{\log}}\)
public matrices. The universal unit exists only in Python (`verity/ml/private_circuits/universal.py`, traced into a
Boolean Definition), and nothing in Lean lowers it. The route I recommend, and its parts:

| part | what | estimated lines | status |
|---|---|---|---|
| (a) the class | `cls`, `regs` and `sch` as a total function of an executable statement. `execClassAt st slotLog units nnz` bundles `HClass.ofStmt`, `regionsOf` and the schedule when `StmtWF ∧ RegionsWF ∧ Zk.schedule st.m` hold, and a fixed default class otherwise. The property then ranges over `st` (data) instead of `cls`, so no `Prop`-field input and no `_hin` remain | ~80 + ~30 changed in `Property.lean`/`Audit.lean` | **needs a ruling** (below) |
| (b) is `ofStmt` the universal unit's class? | the public part must be the universal unit's statement with its template slots' entries outside `matA`/`matB` (the template adds them in `Hidden.side`). That depends on how the private-circuit statement is laid out | — | a question for rec-private / rec-lean |
| (c) `Vs` at V*'s statements | each `VStmt` from V*'s circuits; `hU`/`hscope` from `_hck` (gap 8); `law := VLaw.ofExec` with `Tiles` from the U2 lemma (§1) | ~300–400 (the U2 lemma) + ~100 | open |
| (d) the count curve `_hr` | `rateZ` of V*'s plans at most ρ, a numeric fact about V*'s laws | ~150 | open; needs V*'s plans fixed |
| (e) (ii) at `Flock.Firewall.run` | `msgs`/`view` as `Firewall.run`'s sends (`Array Sent × Bool`) under the Lean ZK server's schedule | ~150 | open; `_hOuter` and `honest` stay until gap 2 and the per-conjunct ruling |

Gap 4's remainder is therefore about 700–900 lines, against the gap list's 300.

**The ruling (a) needs.** I recommend (a). It changes `RecursiveAudit`'s statement, which is a guarantee:
- the class binder becomes an executable statement;
- the property covers exactly the classes the executable sets up, plus a default class;
- `_hin` leaves, discharged by `flock_inner_sound_compiled`, so the property's trust moves from the premise onto 5b's
  proof.

It also touches `Property.lean` lines 81–83, next to the `_hA3` edit rec-lean is making for gap 8b (A3 over `Vs`), so
the two edits would conflict in git. So I haven't edited `Property.lean`. Proofs and rec-lean should decide whether
(a) is the form, and who lands it after 8b.

## 4. Sorrys left, and the shape refusals

No `sorry` was added on `cursor/rec-gaps-4-7-2261`.

| name | branch | file:line | estimated lines | owner |
|---|---|---|---|---|
| `compiled_clash_or_value` | `rec-compile-sound-2261` | `Recursive/CompiledFork.lean:199` | 450–750 (the fallback; bc-0bfaef0d's `table_prob_clashFree` is 250–350) | rec-thm, parked |
| `flock_inner_sound_compiled` (5b) | `rec-gaps-4-7-2261`, inherited | `Recursive/Compile.lean:86` | closed by either 5b route | bc-0bfaef0d / rec-thm |
| `zk_sessions_recursive_fork_inner` (5a / gap 2) | both, inherited | `Recursive/Compile.lean:154` (gaps branch), `:117` (compile branch) | written on `cursor/rec-fork-inner-35f2` | rec-lean |

Shape refusals of §5(i) of the gap list, and what removes each:

| refusal | removed by | state |
|---|---|---|
| `_hS` | `vstar_execStrata`, once `Vs`'s laws are `VLaw.ofExec`; `Tiles` from the U2 lemma or V*'s fixed strata | lemma built, not wired |
| `cls.hk`, `cls.hk6`, `cls.hm` | (a): the class as `execClassAt st …`, a term of the statement rather than an input with `Prop` fields | lemmas written (r…-3e20 pending), wiring needs the ruling |
| `_hin` (a premise, not a refusal) | `compiledForkSound_ofSchedule` inside (a) | same |
| `_hA3` | rec-lean's 8b | not mine |
| `L.nonempty` | gap 4's `L` at V*'s law, or the check exempting `Nonempty` | untouched |

The three refusals of part (ii) stay: no acceptance, `_hOuter` and `honest`.

## Files, branches and documents

- **New branch:** `cursor/rec-gaps-4-7-2261` (worktree `/tmp/wt-rec-gaps-2261`).
- **New files on it:** `Security/Proofs/Flock/Recursive/VStarStrata.lean` and `Security/Proofs/Flock/Recursive/Universal.lean`.
- **Edited on it:** `Security/Proofs/Flock/Recursive.lean`, which now imports the two new files.
- **New document:** `internal/proofs/rec-gaps-4-7-report.md` (this one).
- **Updated document:** `internal/rec-compile-lemma-progress.md`, whose build status was stale; it now points here.
- Nothing was renamed or moved.
