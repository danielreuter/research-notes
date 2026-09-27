---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

# PR #121 (`TwoStageLaw.profile` over replay units): GRANT WITH CONDITIONS

Red-team review for the coordinator (request: `internal/lanes/red-team-flock-3/20260927T0650Z-handoff-from-coordinator.md`).
It covers PR #121 at head **23c048c3** (branch `cursor/two-stage-profile-coarse-6014`), against main **18783baf**. The PR's
merge base ae5db5d3 is identical to main on every path involved.

Everything ran on CPU, in recorded run **r20260927-070022-8cdd**. Beside this file:

- `pr121_checks.py`: my checks;
- `pr121_run_stdout.txt`: the run's output.

The public notes carry only the verdict and pointers here.

## Verdict

**GRANT WITH CONDITIONS.** One condition, before merge:

- **C1: n_v must be the largest RU of the class.** `profile(cls, n_r=…, n_v=…)` takes one n_v for the whole class, while
  RUs carry their own. A larger RU is caught less often (p·k/n_v falls as n_v grows), so a caller who passes a smaller
  n_v, such as a typical or average size, gets an optimistic profile.
  - Example, p = 1/2 and k = 2, δ = 0.01: a class with 4-VU and 8-VU RUs gets 16.0 wrong RUs from `profile(n_v=4)`, but an
    adaptive prover leaves 34 of the 8-VU RUs wrong.
  - `profile(n_v=8)` gives 34.49, which is correct.
  - The fix: say so in the docstring and PROTOCOL.md, or take the class's RUs and use their maximum. The same maximum
    applies to the consumer's per-RU charge (n_v VUs of work).
  - This predates #121 (the old profile had the same parameter). But #121 is this function's soundness fix, and nothing
    calls `.profile` in production yet, so it is the cheap moment.

Recommendations, which don't block:

- **V2:** the profile's docstring should name the assumption its rate rests on: the VU draw's beacon round is published
  after the interiors are registered (the audit's pitfall 4). The module docstring and `vu_key`'s docstring say it, and
  `vu_key` binds the round it's given. Nothing in `law.py` checks it, and the rate does not hold if a caller derives the
  VU key from a round the prover knew before committing its interiors.
- **V3:** in core, `IntegrityProfile`'s docstring should say that a multi-level profile's `accept(m)` holds only when the
  checked level is committed before the first draw (one-stage, or two-stage (a); audit §2.9). That keeps the next
  producer from repeating pitfall 6. There's no current caller, so this can wait for the v1 profile.

## 1. The new law against a prover that adapts after the draw: HOLDS

**The lifecycle:**

1. The boundary, the RU level, is committed and registered.
2. The RU draw: Bernoulli(p) per RU, keyed by `ru_key`, using the beacon round after the boundary registration.
3. The prover replays the drawn RUs and commits their interiors.
4. The VU draw: a uniform `checked(n_v) = min(k, n_v)`-subset per drawn RU, keyed by `vu_key` from the beacon round after
   the interiors registration, with per-RU contexts `("vu", index)`.

**Why each wrong RU escapes with probability at most 1 − p·k/n_v:**

- The set B of wrong RUs is fixed by the boundary commitment before the first draw.
- A drawn wrong RU has at least one wrong VU whatever interior the prover commits (the audit's key lemma).
- The VU subset is uniform and drawn from randomness the prover can't know when it commits. So the drawn wrong RU escapes
  with probability at most 1 − k/n_v, with equality at exactly one wrong VU, anywhere.
- An undrawn wrong RU escapes with probability 1.
- Together: 1 − p + p(1 − k/n_v) = 1 − p·k/n_v per wrong RU.

**Why the bound holds for B as a whole:**

- The RU draws are independent Bernoullis, and the VU draws are independent across RUs.
- Each factor holds conditionally on everything before it, so the joint escape is at most (1 − p·k/n_v)^|B|, even for a
  prover that adapts interiors to the RU draw.
- That is exactly the new profile: one level `replay`, `Bernoulli(p·k/n_v)`. `accept(1) = 1 − p·k/n_v`.
- `worst_case` then bounds any utility over B, except with probability δ.

**Evidence (run r20260927-070022-8cdd):**

- **The attack through the real samplers.** 40,000 trials at `TOY`: 512 RUs of 4 VUs, p = 1/2, k = 2, δ = 0.01.
  - The prover skips 16 RUs. For each drawn one, after the RU draw, it commits an interior with one wrong VU at a
    position of its choice.
  - The VU key is derived from a later round, bound to that interior.
  - The prover is accepted with probability 0.0098 (expected 0.75^16 = 0.0100, σ 0.0005). A single skipped RU escapes
    with probability 0.7527 (expected 0.75).
- **`TOY`'s certified bound.** The new profile certifies 16.008 wrong RUs, which is 64.03 VUs of work at n_v per RU. The
  attack leaves 16 RUs, or 64 VUs, so the bound holds and is tight. The old profile certified 26.58 incorrect VUs against
  the attack's 64, which is the bug, reproduced.
- **The general case, an exact grid of 750 points.**
  - The grid: p ∈ {1/10, 1/4, 1/2, 3/4, 1}; k ∈ {1, 2, 3, 8, all}; n_v ∈ {1, 2, 4, 6, 16, 64}; δ ∈ {10⁻², 10⁻³,
    2⁻²⁰, 10⁻⁶, 2⁻¹⁰}.
  - Against each point I took the best adaptive attack: the most RUs b* with (1 − p·k/n_v)^b* ≥ δ, computed in exact
    rationals.
  - The new certified bound is never below b* (0 points), and never b* + 1 or more (0 points): **conservative and tight**.
  - Its VU-work reading is never below n_v·b*.
  - The old profile's incorrect-VU reading was below the attack's skipped work at 375 of the 750 points.

**What the grant rests on** (not changed by #121):

- **A1:** the VU round is published after the interiors registration (V2).
- **A2:** the key lemma. VUs read the RU's boundary wires only from the boundary commitment (pitfall 2), and the VUs
  partition the RU.
- **A3:** an abort is a rejection, with no re-registration (pitfall 5).
- **A4:** the commitments are binding.

## 2. Rounding and δ: CONSERVATIVE (with C1)

- **The rate is exact.** `Fraction(stage.p) * Fraction(stage.checked(n_v), n_v)` uses the same p and the same
  `checked(n_v)` that the sampler draws with (`key.bernoulli(Fraction(p))`, `key.subset(checked(n_v), n_v)`).
  - With a float p, the profile's rate, the sampler's probability and `check_probability` are the same binary-exact
    Fraction (checked with p = 0.1, k = 3, n_v = 7).
  - Nothing is rounded.
- **No floors.** `worst_case` returns the real-valued optimum of its linear relaxation (16.008, not 16), which is an upper
  bound on the integer optimum.
- **At exact boundaries,** where (1 − q)^b = δ, it returns exactly b: 10.0, 16.0 and 40.0 at q = 1/2 with δ = 2⁻¹⁰;
  q = 1/4 with δ = 0.75¹⁶; q = 1/2 with δ = 2⁻⁴⁰.
  - An attack at the boundary passes with probability exactly δ, which is inside the δ budget.
  - So certifying b is valid, and float error there can't make the claim false.
- **Edge cases are conservative:**
  - k = 0 or p = 0: rate 0, so every RU may be wrong (100 of 100);
  - p = 1 with k ≥ n_v or k = all: rate 1, so 0 wrong RUs;
  - n_r = 0: 0.
- **δ is unchanged:**
  - `worst_case`'s budget is ln(1/δ);
  - one δ per profile, counted once by the application;
  - an application that takes one profile per RU class sums their δs, as before;
  - `n_v < 1` is now refused.
- **C1 above** (the class's largest n_v) is the one optimistic path found.

## 3. vLLM's LEGACY challenge: UNCHANGED

- **How it uses the law.** `integrations/vllm/verity_vllm/commit/challenge.py` builds a `TwoStageLaw` only in
  `stratum_picks` on its key path: p = 1, k = `per_stratum`, with `select_verification_units` and `replay_key` (which is
  `vu_key`). It never calls `.profile`.
- **None of those changed.** #121 touches only `TwoStageLaw.profile` and a docstring. `Stage`, the samplers, `ru_key` and
  `vu_key`, `check_probability`, `to_json` and the domain strings are byte-identical.
- **Digests at main and the PR,** over 300 seeded cases each, are identical in all six sections:
  - `stratum_picks` with a key, and with the legacy seed;
  - `select_replay_units` and `select_verification_units` over mixed three-class laws;
  - `check_probability`;
  - `challenge_positions` and `identity_picker`, legacy and non-legacy;
  - the RU and VU domains.
- **`integrations/vllm/tests/commit/test_challenge.py` passes** at the PR head.
- **Why vLLM is outside the bug:** it commits everything at serving, so it has no interiors committed after a draw.

## 4. The core `verity.proofs.profile` change: NO BEHAVIOUR CHANGE

- **It is one line of the module docstring,** the example of the producer's level names. `IntegrityProfile`, `Bernoulli`,
  `Subset`, `accept`, `worst_case` and `to_json` are unchanged.
- **`packages/verity/tests/proofs` passes unchanged.**
- **Callers,** from a grep at the PR head:
  - the only caller of `TwoStageLaw.profile` is `protocols/sampled_proofs/tests`;
  - the only direct constructors of `IntegrityProfile` are the core tests and `law.py`;
  - `plan.py` builds a `TwoStageLaw` for its gates but never calls `.profile`;
  - the vLLM `.profile(...)` hits are unrelated functions.

## Tests

- **PR head:** 490 passed and 1 skipped, over `protocols/sampled_proofs/tests`, `packages/verity/tests/proofs` and vLLM's
  `test_challenge.py`.
- **Main:** 489 passed and 1 skipped.
- **The PR's `test_law.py` against main's `law.py`:** 4 failed and 7 passed, including `test_toy_attack_is_admitted` and
  `test_the_profile_is_over_replay_units`. The regression test does catch the old bug.
