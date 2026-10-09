---
id: proofs/20261009T2020Z-report-rate-soundness-number
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-b16cf4f6-ebe9-5794-82d5-41f9d2ff04ab
---


# The soundness number that decides 4(d): A vs B at the 8090 class and at m = 33

Status at 20:20Z: done. Read-only: no code change, no PR, no Slack.

## Outcome

**A stands.** At the real class `UniversalUnit_v1{8090,64,32}` (n = 32, k_log 27, m = 32, 3 regions), RecursiveAudit (i)'s
fork-form bound is **2^-194.1 under A** (k = 6,171,993) and **2^-193.8 under B** (k = 1,542,999). The report's target is
2^-128 (Soundness `DESIGN.md` §7, quoted below), so A clears it by 66 bits.

- **The m = 33 sessions (L0).**
  - L0's own contribution is 2^-196.8 under A and 2^-196.0 under B.
  - If every stage and the inner table were at m = 33, the total would be 2^-193.8 under A and 2^-193.0 under B.
- **What k's size moves.** k enters the bound in one place, the factor 1/(1 − rateZ) in `tableErrZ`, and **a larger k is
  better**. Moving from B to A *gains*:
  - 0.81 bit at m = 33;
  - 0.32 bit at m = 32;
  - 0.15 bit at m = 31;
  - 0.01 bit at m = 27;
  - **0.30 bit on the total** at the real class.
- **A against the k → ∞ floor.** A costs 0.07 bit against the floor (194.19 bits), and B costs 0.37 bit.
- **The other k-dependent terms are free.** k also multiplies the k/(e·R_w) parts of `linkErrZC` and `waitErrZC`, which
  are 4× (2 bits) larger under A at a fixed R_w. But R_w and M are free binders: the fork form counts no SHA-512 cost, so
  taking them large costs nothing. At R_w = M = 2^320 (with Q_s ≤ 2^64) the total is unchanged to six decimals.
- **In the stated bound, k's size costs bits under B, not under A.** The only place A's larger k costs bits (2 bits) is
  the cryptographic cost term `2t'(1+k)/2^256`. That term belongs to the non-fork `bound`, and §7 states it separately as
  a function of t, not against 2^-128.

## The bound being evaluated

Source: branch `origin/cursor/rec-audit-land-95d4` at 6ad2fcadb (2026-10-09T19:33Z), `Security/Proofs/Flock/Recursive/`.

### RecursiveAudit (i), fork form (`Property.lean`)

RecursiveAudit (i) states: RoundFork ∨ SessionFork ∨ InnerForkRec ∨ (a run-tied registered-read break) ∨

```
prob (AcceptsStmt st ∧ VerifiesV … ∧ ¬ holds (stmt p ω)) ≤
    expAt σ (sumV … (fun R₂ j τ => (custodied …).boundCR dg N (execStmts Vs j).law.model k Rw M ρ τ))
  + ((innerAt T CT st).r : ℝ≥0∞) * expAt σ (sumV … (fun R₂ j τ => (custodied …).slackCR dg N k Rw M ρ τ))
  + ENNReal.ofReal (Accounting.tableError (execClassAt st).sch ⟨cls.kLog, regs.length, cls.mPts⟩)
```

- **Binders:** `{k Rw M : ℕ} (_hk : 1 ≤ k) (_hRw : 1 ≤ Rw) (_hM : 1 ≤ M) {ρ : ℝ} (_hρ : ρ < 1)`, and
  `_hr : ∀ … i, rateZ (planZAt dj y₀ S' R') i k ≤ ρ`. The rate lemma `hr_planZAt` discharges `_hr` from
  `2^L ≤ ρ·e·k`, at L = 23 under A and L = 21 under B.
- **Stages:** `sumV` runs over j < `outerStatementsAt st` = `outerParts 32 27 (2 + 2·3)`. That is fast100(32)'s 6 levels
  plus 2 algebra groups, 8 stages: L0 … L5, alg-p0 and alg-p1.

### The per-stage terms (`Flock.lean`, `Stage.lean`, `Finds.lean`)

```
boundCR Lm k Rw M ρ τ = Lm.miss 1 + (tableErrZ … Lv k R + linkErrZC … Lv k Rw M ρ + waitErrZC … Lv k Rw ρ)
slackCR k Rw M ρ τ    =               tableErrZ … Lv k R + linkErrZC … Lv k Rw M ρ + waitErrZC … Lv k Rw ρ

tableErrZ planZ L k R = avg_ω ⨆ j, ofReal( (planZ (L.draw ω) R).get j).bound.toReal / (1 − rateZ (planZ (L.draw ω) R) j k) )
rateZ j k             = 2 ^ (lvOf (ts.get j).sch 0).logLen / (Real.exp 1 * k)          (ZkLink/Compiled.lean)
qsZC L                = Σ_c card(ΩcZ c) / card L.Ω                       ("the expected number of commit strings the drawn units read")
linkErrZC L k Rw M ρ  = ofReal( qsZC · (1/(e·M) + k/(e·Rw)) / (1 − ρ) )
waitErrZC L k Rw ρ    = ofReal( qsZC · (k/(e·Rw)) / (1 − ρ) )
miss L K              = ⨆ B, K ≤ |B|, escape B,   escape B = Pr_ω[ draw ω ∩ B = ∅ ]   (Audit/Law.lean)
```

So, summing the stages:

**P ≤ Σ_j [ miss_j + (1 + r)·(tableErrZ_j + linkErrZC_j + waitErrZC_j) ] + tableError_inner.**

### The table bound inside `tableErrZ`: `TabZK.bound` (`ZkSession/Session.lean`, `ZkSession/Inner.lean`)

```
TabZK.bound   = ofReal(padLinkError sch shape t) + (ofReal(padRepError sch shape t e) + εInner N F q δ)²
εInner N F q δ = (N + 3)/|F| + (1 − δ)^q,     |F| = 2^128
```

`padLinkError`, `padRepError` (`Accounting/Padded.lean`) and `tableError`, `repError`, `linkError`, `piopError`,
`ligeritoError` (`Accounting/Bound.lean`) are transcribed term by term in the evaluator (see "How the numbers were
computed"). Their constants:

- qF = 2^128 and qK = 2^256;
- η = 1/200;
- `listBound` = 100·2^r, and `padListBound` = ⌊100·2^logLen/(2^logCols + t)⌋;
- nClaims = 2 + 2·regions.

## Input values

| input | value | source |
|---|---|---|
| inner class | `UniversalUnit_v1{G=8090,N_IN=64,N_OUT=32}`, n = 32 instances, k_log 27, m = 32, 3 regions, 8 claims | run r20261009-092332-af31; `note:proofs/20261009T1354Z-report-rec-stage-8090-run` |
| inner mPts | 29 = PT_LOCAL (24) + nbl (5) | `verity_flock/rec_live.py` `schedule_for` (`link.m = PT_LOCAL + nbl`) |
| inner schedule | fast100(32): k0 = 6, ext = 4, levels (logCols, logInvRate, queries, lanes) = (19,1,218,6), (16,2,106,4), (13,3,71,4), (10,4,53,4), (7,5,43,4), (4,6,36,4) | `Accounting/Schedule.lean` |
| r = `(innerAt T CT st).r` | 257 at m = 32: 2 reps × 128 coin rounds + 1 link-coin round. 259 at m = 33 (2 × 129 + 1). ±1 round is ±0.006 bit | `rec_live.rep_rounds(m, 27, 8)`, run here: 128 at m = 32, 129 at m = 33 |
| V* stages and m | L0: m 33, k_log 24 (436 × RecOpen_v4{64,13}); L1, L2: 32, 23; L3, L4, L5: 31, 23; alg-p0, alg-p1: 27, 26 (2 × InnerRepCheck_v2 each) | sessions in r20261009-110905-2922 (`hello.link.m`), per `note:proofs/20261009T1940Z-report-flock-rate-check` and `…1354Z-report-rec-stage-8090-run` |
| V* draw | `--draw subset:n` at every stage (every unit drawn), so escape B = 0 for every B ≠ ∅ and **`Lm.miss 1 = 0`** | `…1354Z-report-rec-stage-8090-run` |
| V* table shapes (regions, mPts) | not on this VM. Evaluated at the in-range worst, (1024, 64) (`Stmt.InRange`: regions ≤ 1024, mPts ≤ 64), and at (1, 24); the totals below use the worst | `Accounting/Fast100.lean` |
| `--zk` schedule | fast100(m) with level 0's queries q0 = 229 (m 27), 219 (m 28–31), 218 (m 32–35); padding t = 2·q0; e = 2 extra lanes | `verity/core/service/flock/Flock/Zk.lean` (`queries0`, `schedule`) |
| inner code (εInner) | L = PadLayout.len + K_PAD (192); N = nextPow2(L)·2^3; q = 168; δ = 7/16 (`TabZK.hδ`'s floor `relUDR_ge_m1`, valid since 8L ≤ N) | `Flock/Zk.lean`, `ZkSession/Numbers.lean` |
| k | A: 6,171,993 = ⌈2^23/(e·ρ)⌉; B: 1,542,999 = ⌈2^21/(e·ρ)⌉ | 2^23/(e/2) = 6,171,992.85 and 2^21/(e/2) = 1,542,998.21 |
| ρ | 1/2 under both. ρ appears in the bound only as 1/(1 − ρ) on `linkErrZC` and `waitErrZC`; `tableErrZ` uses the actual rateZ, not ρ | `Finds.lean` |
| R_w, M | **free.** No other binder or premise fixes them. The infimum, R_w, M → ∞, is attained to six decimals at R_w = M = 2^320 (next section) | below |
| Q_s | needed only for the concrete R_w, M check: Q_s ≤ 2^64 (loose; V*'s packed tables hold ≤ 2^35 elements) | `qsZC` |

### Why R_w and M are free

- They are universally quantified binders (`_hRw : 1 ≤ Rw`, `_hM : 1 ≤ M`). Only the forks and `VBridge` also read them.
- `VBridge … k Rw` is the circuit fact that any `Good` value layer, which is computed at `(k, Rw)`, makes the inner
  verifier accept. It places no constraint on R_w.
- The fork disjuncts are priced separately, by the finders' expected cost. Per Soundness `DESIGN.md` §3 that cost is
  "2(1+k) t evaluations in expectation (Wald)", and the waits and the finder's further trials are truncations
  ("Waits give up after R_w runs and the finder after M further trials").
- In the non-fork `linkBoundZC`, the cost term `2t'(1+k)/2^256` has no R_w or M.
- So taking R_w and M large costs no bits anywhere. A concrete choice is R_w = M = 2^320.

## Per-stage values at the in-range worst shape (regions 1024, mPts 64), log2

| stage | m | k_log | logLen₀ | q0 | t | L | N | padRepError | εInner | TabZK.bound | rateZ (A) | tableErrZ (A) | rateZ (B) | tableErrZ (B) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L0 | 33 | 24 | 21 | 218 | 436 | 510 | 4096 | −102.518 | −115.999 | −205.036 | 0.12500 | −204.843 | 0.50000 | −204.036 |
| L1 | 32 | 23 | 20 | 218 | 436 | 506 | 4096 | −102.514 | −115.999 | −205.029 | 0.06250 | −204.935 | 0.25000 | −204.614 |
| L2 | 32 | 23 | 20 | 218 | 436 | 506 | 4096 | −102.514 | −115.999 | −205.029 | 0.06250 | −204.935 | 0.25000 | −204.614 |
| L3 | 31 | 23 | 19 | 219 | 438 | 504 | 4096 | −102.533 | −115.999 | −205.065 | 0.03125 | −205.019 | 0.12500 | −204.872 |
| L4 | 31 | 23 | 19 | 219 | 438 | 504 | 4096 | −102.533 | −115.999 | −205.065 | 0.03125 | −205.019 | 0.12500 | −204.872 |
| L5 | 31 | 23 | 19 | 219 | 438 | 504 | 4096 | −102.533 | −115.999 | −205.065 | 0.03125 | −205.019 | 0.12500 | −204.872 |
| alg-p0 | 27 | 26 | 15 | 229 | 458 | 502 | 4096 | −102.888 | −115.999 | −205.775 | 0.00195 | −205.773 | 0.00781 | −205.764 |
| alg-p1 | 27 | 26 | 15 | 229 | 458 | 502 | 4096 | −102.888 | −115.999 | −205.775 | 0.00195 | −205.773 | 0.00781 | −205.764 |

- **Inner table:** `tableError(fast100(32), 27, 3, 29)` = **2^-205.224**, made of `repError` 2^-102.612 (piop 2^-111.83,
  Ligerito 2^-102.61) and `linkError` 2^-237.06. At the in-range worst, (27, 1024, 64), it is 2^-205.042.
- **Shape sensitivity:** at (regions 1, mPts 24) every `TabZK.bound` is 0.18–0.23 bit smaller. For example, L0 is 2^-205.217.

## Totals (miss = 0; R_w, M at the infimum)

**(a) The real class, m = 32 (8 stages, r = 257):** P ≤ (1 + 257)·Σ_j tableErrZ_j + tableError_inner.

| k | Σ_j tableErrZ_j | total | **soundness** | at (1, 24) and inner (27, 3, 29) |
|---|---|---|---|---|
| A = 6,171,993 | 2^-202.125 | 2^-194.113 | **194.11 bits** | 194.30 bits |
| B = 1,542,999 | 2^-201.827 | 2^-193.815 | **193.81 bits** | 194.00 bits |
| k → ∞ (floor) | 2^-202.198 | 2^-194.186 | 194.19 bits | 194.38 bits |

**(b) m = 33, the largest honest m:**

| | A | B | k → ∞ |
|---|---|---|---|
| (b1) L0's stage, tableErrZ | 2^-204.843 | 2^-204.036 | 2^-205.036 |
| (b1) L0's contribution, (1 + 257)·tableErrZ | **2^-196.83 (196.83 bits)** | **2^-196.02 (196.02 bits)** | 2^-197.02 |
| (b2) every stage and the inner table at m = 33 (k_log 27, worst shape, r = 259, N = 8192) | **2^-193.82 (193.82 bits)** | **2^-193.01 (193.01 bits)** | — |
| (b2) the same at shape (1, 24) | 194.00 bits | 193.19 bits | — |

**Concrete R_w and M.** At R_w = M = 2^320, Q_s ≤ 2^64 and ρ = 1/2:

- per stage, `linkErrZC` = `waitErrZC` = 2^-233.9 under A and 2^-235.9 under B;
- summed over (1 + 257) × 8 stages: 2^-221.9 under A and 2^-223.9 under B;
- the (a) totals stay 194.112633 bits (A) and 193.814836 bits (B), identical to six decimals.

At R_w = M = 2^300 the sum would be 2^-201.9, which costs 0.006 bit. That is the "R_w ≫ k" tightness cost the rate-check
report names.

## Which term k's size moves, and by how many bits

| term | how k enters | A vs B |
|---|---|---|
| `tableErrZ` | factor 1/(1 − 2^logLen₀/(e·k)); smaller k is worse | B worse by 0.807 bit at m = 33 (A: 0.193, B: 1.000), 0.322 at m = 32, 0.147 at m = 31, 0.008 at m = 27. **0.298 bit on the (a) total; 0.81 bit on the (b2) total** |
| `linkErrZC`, `waitErrZC` | Q_s·k/(e·R_w)/(1 − ρ); larger k is worse | A worse by log2(k_A/k_B) = 2.000 bits *at a fixed R_w*; 0 bits once R_w is chosen ≫ Q_s·k (free) |
| `Lm.miss 1`, the inner `tableError` | none | 0 |
| non-fork only: `linkBoundZC`'s cost term Q_s·2t'(1+k)/2^256/(1 − ρ) | linear in k | A worse by 2.000 bits: Q_s·t'·2^-231.44 per stage under A, Q_s·t'·2^-233.44 under B. This is part of the cryptographic part (forks priced by A2/`cr/sha-512`), which §7 states as a function of t, not against 2^-128 |

**So k's size costs B bits, not A.** In the statistical part the smaller k of B is the worse choice everywhere. The one place
A's larger k costs bits is the cryptographic cost term, 2 bits at any (Q_s, t').

## The bound the report states

No recursion report gives a numeric target. `note:proofs/20261009T1920Z-report-rec-exec-statement` gives the bound's
form, and `note:proofs/20261009T1940Z-report-flock-rate-check` says only "`R_w` must be much larger than `k`. This is a
tightness cost of the reduction, not a soundness gap." The target of record is Soundness `DESIGN.md` §7
(`Security/Proofs/Flock/Soundness/DESIGN.md`, last changed 319b8f37b, 2026-10-09T03:16Z):

> **Stating soundness.** a16z's concrete levels are 100 bits as the bare minimum and 128 bits as standard practice. We
> target 2^-128, and state the number the way the stages suggest:
>
> 1. **The statistical part, per table:** `−log2` of the proven error against any prover at the oracle layer. That is
>    205 bits for every m, 22 ≤ m ≤ 35. […] A session with several tables adds their errors.
> 2. **The cryptographic part, with its model named:** collision resistance of SHA-512, as
>    `Σ_ℓ √(N_ℓ·Q_ℓ·Adv_ℓ) + Adv_×` for explicit collision finders. That is at most `t·2^{17.3−256}` under the generic
>    bound (§2), for classical provers.

- **Against 2^-128:** A gives 194.1 bits at (a) and at least 193.8 at (b). It meets the target with 66 bits to spare.
- **Against "205 bits per table":** that is the table's own error. `TabZK.bound` is 2^-205.04 at L0 and 2^-205.03 to
  2^-205.78 elsewhere; the inner table is 2^-205.22. k does not touch it.
  - The recursion's per-stage table term `tableErrZ` = bound/(1 − rateZ) is 2^-204.84 at L0 under A and 2^-204.04 under B,
    at the worst shape.
  - So neither option keeps L0's stage term at 205 bits. Keeping it there needs rateZ ≤ 0.0246, that is k ≥ 3.1·10^7 at
    m = 33.
  - This is a property of the recursion's count curve, not a regression of the per-table claim.

## Verdict

| | (a) 8090 class, m = 32 | (b1) L0 stage, m = 33 | (b2) all at m = 33 |
|---|---|---|---|
| A (k = 6,171,993) | **194.11 bits** | 196.83 bits | 193.82 bits |
| B (k = 1,542,999) | **193.81 bits** | 196.02 bits | 193.01 bits |

- **k's size moves only `tableErrZ`'s 1/(1 − rateZ)** in the stated bound, and in favour of A: B is 0.30 bit worse at (a)
  and 0.81 bit worse at m = 33. The k/(e·R_w) terms cost nothing at a free, large R_w.
- **A meets the stated 2^-128 target**, by 66 bits at (a) and 65.8 at (b2). **A stands**; B buys nothing in soundness.

## Caveats

- **Lean-proved vs evaluated.**
  - Lean proves `tableError ≤ 2^-205` at 22 ≤ m ≤ 35 (`Fast100.lean`), which covers the inner term.
  - For the `--zk` table it proves `TabZK.bound ≤ 2^-203` only at m = 25..27 (`ZkSession/Numbers.lean`, `bound_le_m1`).
  - At m = 31–33 the `TabZK.bound` values above come from evaluating the definitions, not from a Lean lemma. A proved
    total today would substitute 2^-203 where a lemma exists and has none at m = 31–33.
- **The V* sessions' regions and mPts** were not read; the session files aren't on this VM. The worst in-range shape was
  used, and the best shape moves the totals by +0.19 bit.
- **`miss = 0`** relies on `--draw subset:n` at every V* stage. A sampled outer draw would add `Lm.miss 1` per stage,
  with no k in it.
- **r = 257** counts one link-coin round besides the 256 rep rounds. If it is 256, the totals change by 0.006 bit.

## How the numbers were computed

- **Evaluator (scratch, not in the repository):** a scratch transcription on the proofs VM (not kept).
  - It transcribes `fast100`, `queries0`, the `--zk` schedule, `tableError`, `repError`, `piopError`, `ligeritoError`,
    `padRepError`, `padLinkError`, `PadLayout.len`, the inner code's N, `εInner`, `rateZ`, `tableErrZ`, `linkErrZC` and
    `waitErrZC`, in Python `Decimal` at 80 digits.
  - Before use, it reproduced Lean's numeric claims:
    - fast100 `tableError`'s worst in range is −206.38 (m = 22), −205.68 (m = 25, 27), −205.04 (m = 31, 32, 33) and
      −205.01 (m = 35), all ≤ −205, as `Fast100.lean` states;
    - `padTableError`'s worst in range at m = 25 and 27 is ≤ −205, as `padTableError_le_m1` states.
- **Lean source:** a read-only worktree, detached at origin/cursor/rec-audit-land-95d4 (6ad2fcadb).
- **Rounds:** computed with that worktree's `verity_flock.rec_live.rep_rounds`.
