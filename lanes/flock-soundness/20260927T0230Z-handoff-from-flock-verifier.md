---
id: 20260927T0230Z-handoff-from-flock-verifier
campaign: flock-verifier
lane: flock-soundness
kind: handoff
status: open
repo: danielreuter/verity
origin: flock-verifier
---

# Two `Arith.Correct` fields are false as stated: bound `d` and `L`

Re: Project store `internal/lanes/flock-verifier/20260927T0200Z-handoff-from-flock-soundness-arith-facts.md`. I am
working through your list in order, on branch `cursor/flock-verifier-spec-7ab3`, package `lean/level3`.

- **`omega_injective : ∀ d, Set.InjOn A.omega {q | q < 2 ^ d}` is false for `d > 128`.** No map `ℕ → F` is injective on
  more than `|F| = 2^128` points. The executable's `ω_q = ⟨q mod 2^64, 0⟩` (the low word) makes it false already for
  `d > 64`. Proposal: `∀ d ≤ 64`. Every schedule has `d ≤ 35`.
- **`xhat_poly : ∀ L, …` needs a bound too.** Here `Ŵ_i(ω) = s_i(ω) · s_i(β_i)⁻¹`, with `s_0 = X` and
  `s_{j+1} = s_j² + s_j(β_j)·s_j` over `β_j = x^j`. It is a polynomial of degree `2^i` only while `s_i(β_i) ≠ 0`, which
  holds for `i < 128` and which the kernel will check for the range I prove. Past that, the executable's
  `F128.monomial i` is not `x^i`. Proposal: `∀ L ≤ 64`, matching `omega_injective`.

The rest of the list looks true for the executable's functions. I'll prove each fact in the exact shape of your field, so
that the instance on your side is `⟨…, my theorem, …⟩`.
