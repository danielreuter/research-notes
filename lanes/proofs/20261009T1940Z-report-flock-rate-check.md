---
id: proofs/20261009T1940Z-report-flock-rate-check
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-cb1cfff8-66c8-5be3-9c52-84f78a9e2f12
---


# flock-rate-check: early report (step 1), stopped before building

**Answer.** `k` and `ρ` do not appear in a session's inputs, in its draw JSON, in the verifier, or in PROTOCOL.md. Both are
parameters of the extraction analysis: `k` is the number of accepted reruns in `extractProbAccZ` / `failProbAccZ`, and
`ρ < 1` is the count curve's rate. So, per the instructions, I stopped before building anything. No code is written:
branch `cursor/flock-rate-check-2f12` sits at main 6cea9a973, unpushed.

**The verifier already bounds the rate at every draw.**
- `rateZ` reads only level 0's `logLen` of a table's schedule.
- `planZAt dj y₀ S' R'` is the one-table list `[tableAtZK dj y₀ S']` (`ZkBind/At.lean:60`).
- That table is one of two things, and both carry a schedule that `Zk.schedule m` returned (`tabAt` sets
  `sch := schedOf y.sch`):
  - a `DrawSetupZK`'s table, whose field `hz : Zk.schedule x.st.m = .ok (sch, tPad)` supplies the schedule;
  - `y₀.refused`, where `y₀` is itself a `DrawSetupZK`.
- `Zk.schedule m` is `fast100 m` with only level 0's `q`, `strata` and `cap` replaced. `logLen` is unchanged.
- It accepts only m from 25 to 35 (`schedule_spec`). Any other m is refused: `queries0` and `fast100` throw "no fast100
  schedule", and PROTOCOL.md §15 says "the verifier rejects any other m".
- fast100's level 0 has rate 1 and `cols = m − 7 − k0`, so `logLen₀ = m − 6 − k0`:

  | m | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | logLen₀ | 13 | 14 | 15 | 18 | 18 | 18 | 19 | 20 | 21 | 22 | 23 |

So `rateZ (planZAt dj y₀ S' R') i k ≤ 2^23/(e·k)` holds unconditionally, at every `S'`, `R'` and `i`. That covers drawn
draws, refused draws and draws the verifier never sees, so the property's use doesn't need to change and refused draws
don't need to contribute 0.

One more point: a check made only at acceptance could not discharge `_hr` as stated, because `_hr` ranges over every
`S'` and `R'`. A check discharges it only if it sits in setup (in `Zk.schedule`), where every table, `y₀.refused`
included, carries it.

## Honest sessions (restored copies on vy-nebius-1, read-only; m from each session's `hello.link.m`)

Every run's command line is `flock-verify verify --zk`, and every session is fast100 with one table and accepted. The V*
L0 sessions are the real class's (`rec-private/8090-64-32-n32`, G=8090, N_IN=64, N_OUT=32).

| run | sessions (m) | largest logLen₀ |
|---|---|---|
| r20261009-110905-2922 | L0 (33); L1, L2 (32); L3, L4, L5 (31); alg-p0, alg-p1, other-alg-p1 (27) | 21 |
| r20261009-111638-6720 | L0 (33); L1, L2 (32); L3 (31); alg-p0, alg-p1, faulty-, other-, outside-alg-p0, outside-alg-p1 (27) | 21 |
| r20261009-111658-80e4 | same ten as 6720 | 21 |
| r20261009-114213-2f10 | L0 (33); L1, L2 (32); L3 (31); alg-p0, alg-p1 (27) | 21 |

Each session's planned rate is `2^logLen₀/(e·k)`, which depends on `k`. The largest honest value is
`2^21/(e·k) = 771,499.1/k`; across fast100's range the largest is `2^23/(e·k) = 3,085,996.4/k`. No honest session can
plan above ρ under either option below once `k` meets that option's bound.

## Option A (recommended): no new verifier form; the existing m ≤ 35 refusal, proved to bound the rate

- **Lean:** a new file, `Security/Proofs/Flock/Soundness/Discharge/ZkBind/Rate.lean`, of about 40 lines:
  - `zk_logLen₀_le : Zk.schedule m = .ok (sch, t) → (lvOf (schedOf sch) 0).logLen ≤ 23`, by
    `interval_cases m <;> decide +kernel`, the same way as `zkSchedFacts_all`;
  - `rateZ_planZAt_le : rateZ (planZAt dj y₀ S R) i k ≤ 2^23/(Real.exp 1 * k)`, by cases on `tableAtZK`'s `dite`;
  - `hr_planZAt : (2:ℝ)^23 ≤ ρ * (Real.exp 1 * k) → ∀ S R i, rateZ (planZAt dj y₀ S R) i k ≤ ρ`.
- **Property (rec-lean's edit, not mine):** in `RecursiveAudit`, `_hr` becomes `_hkρ : (2:ℝ)^23 ≤ ρ * (Real.exp 1 * k)`.
  This constrains the property's own parameters, the same kind of binder as `_hk` and `_hρ`; it is not a premise about
  the world. Alternatively, rec-lean could fix `ρ := 2^23/(e·k)` with `2^23 < e·k`. The proof applies `hr_planZAt` once
  per custodied `j`.
- **Verifier, PROTOCOL.md, agreement:** no change, no divergence, and no new refusal for Daniel's DM. `audit.py --update`
  only adds lock hashes for the three new non-guarantee declarations. No guarantee record changes until rec-lean changes
  the binder in `Property.lean`.
- **Cost:** `k ≥ 2^23/(e·ρ)`, which is 6,171,993 at ρ = 1/2. Because `linkErrZC` and `waitErrZC` carry `k/(e·R_w)`,
  `R_w` must be much larger than `k`. This is a tightness cost of the reduction, not a soundness gap.

## Option B (the ruling's literal form): a verifier cap in `Zk.schedule`

- **Why a cap:** the session fixes `logLen₀` through m, so the only free choice is a class cap `L ≤ 23`. Writing it as
  constants `K` and `RHO` would also need a rational lower bound on e.
- **Verifier:** `Zk.schedule` throws "planned rate 2^{logLen₀}/(e·K) > ρ = RHO" when `logLen₀ > L`. That is about 5 lines
  and one constant in `Flock/Zk.lean`, plus a line in PROTOCOL.md's check list.
- **Lean:** `hz` already carries the check, so `DrawSetupZK` is unchanged. The lemma is as in A with `L` in place of 23,
  and `k` need only be at least `2^L/(e·ρ)`; with `L = 21` that is 1,542,999 at ρ = 1/2.
- **Effect:** with `L = 21` the cap refuses m = 34 and 35, which narrows the accepted forms (no new form). No honest
  session uses m = 34 or 35.
- **Records:** `Zk.schedule` and the declarations that read it get new lock hashes, and the cap goes into Daniel's DM as a
  new refusal.
- **Agreement:** a D5-style expected divergence only if the agreement corpus has a `--zk` session above `L`. I haven't
  checked the corpus yet.

## Recommendation

Choose A unless Daniel wants a smaller `k`, in which case choose B with the `L` he picks; 21 is the real class's value.
Under A, the fail-closed refusal the ruling asks for already exists: the m ≤ 35 refusal, documented in §15, is the
planned-rate refusal at `L = 23`. Once the form is confirmed I can implement either one, run its tests, and give the
`check --record --agreement` command.

## PR title and body

None yet: no code until the form is confirmed. If A is confirmed, the proposed PR is:

Title: `Flock --zk: every planned rate is at most 2^23/(e·k) (discharges RecursiveAudit's _hr)`

Body:
> `rateZ` at every table `planZAt` can return (drawn, refused or never seen) reads a schedule that `Zk.schedule`
> returned, whose level 0 has `logLen₀ = m − 6 − k0 ≤ 23` on the m range it accepts (25 to 35; any other m is refused,
> PROTOCOL.md §15). New lemmas in `Proofs/Flock/Soundness/Discharge/ZkBind/Rate.lean`: `zk_logLen₀_le`,
> `rateZ_planZAt_le` and `hr_planZAt` (`2^23 ≤ ρ·e·k → _hr`). No verifier, PROTOCOL.md or agreement change, and no
> guarantee record changes. Honest `--zk` sessions (runs 2922, 6720, 80e4 and 2f10, real class 8090-64-32) plan
> `logLen₀ ≤ 21`.
