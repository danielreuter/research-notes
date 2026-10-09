---
id: proofs/20261009T2015Z-report-flock-rate-readscover
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-cb1cfff8-66c8-5be3-9c52-84f78a9e2f12
---


# flock-rate-check: the rate lemma, and ReadsCover as a refusal

Status at 20:15Z:
- **Rate lemma: done, built and audited.** It is written at any cap `L`, instantiated at `L = 23` from the existing m
  range, and `_hr` is derived from `2^L ≤ ρ·e·k`. Committed on `cursor/flock-rate-check-2f12` (off main d54efbb95), head
  4a0d4e18b, pushed. Run r20261009-195356-bc6f on vy-nebius-2 passes: built, audit PASS with only `propext`,
  `Classical.choice` and `Quot.sound`, lock unchanged. Details under "Rate lemma: build".
- **No verifier change for the rate:** none until top rules on A or B (Slack 1791575026.272919).
- **ReadsCover: stopped at the stop condition.** No honest V* program reads any row of the private circuit's description:
  every honest V* session's `--registered` file holds no port for it. No verifier change and no Lean for ReadsCover;
  details under "ReadsCover".

## Rate lemma

`Security/Proofs/Flock/Soundness/Discharge/ZkBind/Rate.lean` (namespace `FlockSoundness.Discharge.ZkBind`, imported from
`ZkBind.lean`):

| declaration | statement |
|---|---|
| `ZkLogLenCap L` | `∀ m s t, Zk.schedule m = .ok (s, t) → (lvOf (schedOf s) 0).logLen ≤ L` |
| `zkLogLen₀_le` | `∀ m, 25 ≤ m → m ≤ 35 → zkLogLen₀ m ≤ 23`, by `interval_cases m <;> decide +kernel` (as `zkSchedFacts_all`) |
| `zkLogLenCap_23` | `ZkLogLenCap 23`, from `schedule_spec` (Zk.schedule accepts only m from 25 to 35) and `zkLogLen₀_le` |
| `logLen_tableAtZK_le` | `ZkLogLenCap L → (lvOf (tableAtZK dj y₀ S).sch 0).logLen ≤ L` at every `S`: the draw's `DrawSetupZK` or `y₀`, each by its `hz` |
| `planZAt_get` | the one-table plan's table at every index is `tableAtZK dj y₀ S` |
| `rateZ_planZAt_le` | `ZkLogLenCap L → rateZ (planZAt dj y₀ S R) i k ≤ 2^L / (Real.exp 1 * k)` |
| `hr_planZAt` | `ZkLogLenCap L → (2:ℝ)^L ≤ ρ * (Real.exp 1 * k) → rateZ (planZAt dj y₀ S R) i k ≤ ρ` |
| `hr_planZAt_23` | the same at `zkLogLenCap_23`: `(2:ℝ)^23 ≤ ρ * (Real.exp 1 * k) → … ≤ ρ` |

- **Uniformity:** `hr_planZAt` holds at every `dj`, `y₀`, `S`, `R` and `i`.
- **Discharging `_hr`:** rec-lean's `_hr` (every `R ω t R₂ j S' R' i` at
  `(custodied zs₀ _hCust R ω t R₂ j).dj` and `.y₀`) is
  `fun R ω t R₂ j S' R' i => hr_planZAt_23 _ _ hkρ S' R' i`.
  - `_hkρ : (2:ℝ)^23 ≤ ρ * (Real.exp 1 * k)` replaces `_hr` in `Property.lean`. That is rec-lean's edit; I made no change
    there.
  - The property's use stays as it is: refused draws carry `y₀`'s schedule, so they are covered and need not contribute 0.
- **Under B:** the cap goes into `Zk.schedule`. B needs one new lemma, `zkLogLenCap_21` (or whatever `L` top picks),
  proved by the same `decide +kernel`, and then uses `hr_planZAt` at that `L`.
- **`k = 0`:** `hkρ` already excludes it (since `2^L > 0`), so the lemma takes no `1 ≤ k`.

### Rate lemma: build

**PASS.** Run r20261009-195356-bc6f ran `lean_changed.py --records Security/Proofs --update` on vy-nebius-2, build slot 0,
at tree 4a0d4e18b (node 1's build slot was full, with two waiting). The result was rc 0, class SUCCESS, kind `lean-fast/v1`,
in 461 s total.
- Build: `Build completed successfully (5424 jobs)`, including
  `✔ [5342/5424] Built Proofs.Flock.Soundness.Discharge.ZkBind.Rate (3.3s)`. No warning names `Rate.lean`.
- Audit: `Security/Proofs: PASS 61772 declarations in 960 modules`. The axioms are `propext`, `Classical.choice` and
  `Quot.sound` only; `ZkBind.Rate` is among the 960 modules; there are no offenders, escapes or declared axioms; failures are
  `[]`.
- Records: the run's `lean-audit.json` is byte-identical to the branch's `Security/Proofs/lean-audit.json`, so no
  guarantee record changes and there is nothing for Daniel's DM.
- Not run: the kernel replay and the tests. `lean-fast/v1` is not a Lean verdict, and `research merge` refuses it. Both
  come with the PR's `check.py --record`. The one computed step, `zkLogLen₀_le`, is `decide +kernel`, which the kernel
  already checked at elaboration.

## Honest sessions' planned rates (restored copies on vy-nebius-1, read-only; m from each session's `hello.link.m`)

Every run's command line is `flock-verify verify --zk`, and every session is fast100 with one table and accepted.
**Correction to the 19:17Z version:** only run 2922's sessions are the real class 8090-64-32 (G = 8090, N_IN = 64,
N_OUT = 32). The other runs' classes (from each session's `--registered` path) are:
- 6720: `16-16-8-n64`;
- 80e4: `1024-1024-512-n8`;
- 2f10: `sc-16-16-8`.
The m values are unchanged.

| run (class) | sessions (m) | largest logLen₀ |
|---|---|---|
| r20261009-110905-2922 (8090-64-32) | L0 (33); L1, L2 (32); L3, L4, L5 (31); alg-p0, alg-p1, other-alg-p1 (27) | 21 |
| r20261009-111638-6720 (16-16-8) | L0 (33); L1, L2 (32); L3 (31); alg-p0, alg-p1, faulty-, other-, outside-alg-p0, outside-alg-p1 (27) | 21 |
| r20261009-111658-80e4 (1024-1024-512) | the same ten as 6720 | 21 |
| r20261009-114213-2f10 (sc-16-16-8) | L0 (33); L1, L2 (32); L3 (31); alg-p0, alg-p1 (27) | 21 |

- **Planned rate:** `2^logLen₀/(e·k)`. The largest honest value is `2^21/(e·k) = 771,499.1/k`; the cap's is
  `2^23/(e·k) = 3,085,996.4/k`.
- **No honest session exceeds ρ** under A once `k ≥ 2^23/(e·ρ)` (6,171,993 at ρ = 1/2), or under B with `L = 21`
  once `k ≥ 2^21/(e·ρ)` (1,542,999 at ρ = 1/2).
- **Options A and B:** as in the 19:17Z version, summarized here.
  - A: no verifier change; `_hkρ` at 23.
  - B: a cap `L` in `Zk.schedule` with a refusal "planned rate 2^{logLen₀}/(e·K) > ρ = RHO". At `L = 21` it refuses
    m = 34 and 35, which no honest session uses.
  - The lemma serves both.

## ReadsCover

**Answer: no existing check gives it, and a new refusal can't be added without refusing every honest V* session.** No
honest V* program reads the private circuit's description at all, which is the task's stop condition. So I stopped: no
verifier change, no crafted session, no Lean, and no check command for ReadsCover.

### What V*'s sessions register (all four restored runs, from each session's `--registered` file)

| V* statement | registered values (`ports` of `verity/registered-reads/v0`) |
|---|---|
| L0 … L5 (RecOpen) | `rec-top-L*` (port `out`), `rec-acc` (`acc`, `acc_out`), `rec-coef` (`coef`), `rec-dirs` (`dirs`) |
| alg-p0 (InnerRepCheck) | `rec-c0` … `rec-c57`, `rec-v`, `rec-residuals-zero` |
| alg-p1 (InnerRepCheck) | `rec-c50` … `rec-c101`, `rec-acc` (`acc0`, `acc1`), `rec-v`, `rec-residuals-zero` |

These are the same in 2922, 6720, 80e4 and 2f10, including the faulty-, other- and outside- sessions. Every value is the
recursion's own: the inner proof's tops, the accumulator chain, coefficients, directions, and the algebra's constants
and residuals. **None is the private circuit's description.** V*'s port `out` is the V* statement's own output row
(`rec-top-L*`), not the description's `out` rows.

### So `readsZ` is empty at the description's port, and ReadsCover can't hold

- `readsZ zs rt o i` counts only sessions with `rt ∈ own` (`ReadV`).
- With `rt` the description's registration, no honest session holds it, so `readsZ zs rt o i` is false for every `i`.
- `ReadsCover` then says `stmt q ω = stmt q' ω` for all `q` and `q'`. That is false for any `stmt` that reads its strings,
  including bc-66706a46's, which reads every `src` and `out` row.
- This is gap 3b's case 1 ("a session that never holds `rt`") and gap 3a's "non-vacuity needs `rt ∈ own`", and both
  happen in every honest run.

### Why a refusal can't fix it at V*'s sessions

- **Requiring the port** (refuse a V* session whose `own` lacks the description's port, or reads fewer of its rows than
  the class has) refuses every honest V* session.
- **Putting the port in V*'s `own`** doesn't help: `Registered.checkPort` refuses a port that is not a row of the
  session's circuit ("{name} is not a row of the circuit"). V*'s circuits (RecOpen_v4, InnerRepCheck_v2) have no port
  carrying the description.
- **A generic "every registered row is read" refusal** also refuses honest sessions. Port `acc` registers 1,055 rows
  of `rec-acc` and L0 reads 436 of them (positions 0 … 744); L1 … L5 read windows further along. `coef`, `dirs` and `out`
  are read in full.
- **Existing checks:** none is a coverage check. In `Registered.check` / `checkPort`:
  - one position and one path per table row;
  - every table row opens the registered root at its position;
  - every instance's ref names a table row whose position is the program's for its unit.

  `HmRow`'s count checks bound a statement's own table sizes, not the registered value's rows. Nothing requires the read
  positions to cover `[0, reg.leaves)`.

### Where the description actually is in the honest runs

- **Inner statement:** the universal unit's, partition template
  `ProgramRow[UniversalUnit_v1{G=8090,N_IN=64,N_OUT=32}]_v1` (2922's `u/stage`).
  - Its public header has `shared_rows: {"out": 32, "p0": 32, "p1": 1}` and no `registered` key.
  - The description is the shared row `p1`, one row that every one of the 32 instances reads. Its `b ‖ c` sits among the
    public file's row digests, which is instance data of `st`: "the regions' bytes", per rec-exec-statement's A.4.
- **The inner session's own Lean verify** runs without `--registered` and refuses on plain leaves ("a form the
  soundness proof does not cover yet"). In the recursion, V* verifies the inner proof instead.
- So in the honest runs nothing opens the description against a registered root. Neither V* nor the inner statement
  does it; the description reaches the circuit only through `st`'s public row digests.

### What would make ReadsCover hold (a route call: top's)

1. **Read the description from `st`, not from V*'s reads.**
   - `stmt` takes its commit strings from the inner statement's own row digests (its shared rows' `b ‖ c`, a function of
     `st`).
   - Then `x R ω := stmt (rowsOf st) ω` doesn't depend on the outcome, and `_hx` and `ReadsCover` hold by `rfl`.
   - The registration link moves to `st`: a refusal that the inner statement's description rows open the developer's
     registered root. That is `Registered.check` at the inner statement, with a `--registered` port for `p1` (or for
     `op`, `src` and `out` under circuits' option (a)), plus a coverage refusal that every row of that port's table is
     read. Every instance reads the shared row, so that holds by construction at one row.
   - Neither check reads a V* session, and rec-lean's `readsZ` stops being on this path.
   - It needs the inner statement staged with a `registered` header (Python, restaging the inner statement) and the
     Lean lemma at the inner statement's `checkRegistered`. Both are moderate.
2. **Make V* read the description.**
   - V*'s staging gets a port carrying the description's rows and a statement whose instances read all of them, plus the
     coverage refusal in `Registered.checkPort`: every `i < reg.leaves` is some instance's `reg.reads` position.
   - Then the Lean lemma "acceptance ⇒ `∀ i < rt.leaves, readsZ zs rt o i`" gives ReadsCover for any `stmt` that reads
     only rows `[0, nr)` with `nr ≤ rt.leaves`.
   - This is a V* construction change: new circuits, restaging and new honest runs. It is large, and nothing in V*'s
     design reads the description today.

I recommend route 1: it puts the check where the description already is. Either way the choice is top's. Without one,
neither the verifier refusal nor its Lean can land by 23:00Z, since the stop condition holds in every honest run. **The
ReadsCover refusal PR won't make 23:00Z**, and I'm saying so now (20:05Z).

## PR title and body (the rate lemma; no verifier change)

Title: `Flock --zk: every planned rate is at most 2^L/(e·k) under a cap on level 0's logLen (discharges RecursiveAudit's _hr)`

Body:
> `rateZ` at every table the one-table `--zk` plan `planZAt dj y₀ S R` can hold (a draw's `DrawSetupZK` table or `y₀`'s
> refused one, at every draw) reads level 0's `logLen` of a schedule `Zk.schedule` returned (`DrawSetupZK.hz`). So a
> cap `ZkLogLenCap L` bounds every planned rate by `2^L/(e·k)` (`rateZ_planZAt_le`), and `2^L ≤ ρ·(e·k)` gives
> `rateZ … ≤ ρ` at every `dj`, `y₀`, `S`, `R` and `i` (`hr_planZAt`), the form of `RecursiveAudit`'s `_hr`.
> `zkLogLenCap_23`: `Zk.schedule` accepts m from 25 to 35 only (PROTOCOL.md §15), where fast100's level 0 has
> `logLen₀ = m − 6 − k0 ≤ 23` (`decide +kernel` at each m).
>
> - New file `Security/Proofs/Flock/Soundness/Discharge/ZkBind/Rate.lean`, imported from `ZkBind.lean`.
> - No verifier, PROTOCOL.md or agreement change; no guarantee record changes.
> - Honest `--zk` sessions (runs 2922, 6720, 80e4 and 2f10) plan `logLen₀ ≤ 21`.
> - Under top's option B (a cap `L < 23` in `Zk.schedule`), the same lemma applies at `L`.
>
> Tests: r20261009-195356-bc6f (`lean_changed.py --records Security/Proofs --update`, vy-nebius-2) builds 5424 jobs, and the
> audit passes 61,772 declarations in 960 modules with only `propext`, `Classical.choice` and `Quot.sound`. The lock is
> unchanged. The kernel replay and the tests come with this PR's `check.py --record`.
