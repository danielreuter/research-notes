---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: red-team-m1-zk · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity ·
re: [PR #123](https://github.com/danielreuter/verity/pull/123) (M1), level 0 of Ligerito under hiding · private: this
folder is not mirrored

# M1's level-0 query count under the padded code

**Result.** To keep fast100's per-level rule (100 bits per run), and so the 2^-128 profile's stated numbers, level 0
needs these counts under M1's padding:

| m | L = 2^cols₀ | Q₀ | t_pad = 2Q₀ + 64 | rate ρ′ | distance 1 − ρ′ | bits per run at level 0 |
|---|---|---|---|---|---|---|
| 25 | 4096 | **277** | 618 | 0.5754 | 0.4246 | 100.02 |
| 26 | 8192 | **242** | 548 | 0.5334 | 0.4666 | 100.27 |
| 27 | 16384 | **229** | 522 | 0.5159 | 0.4841 | 100.25 |

Each count is the least one that works. One query fewer gives 99.74, 99.89 and 99.83 bits.

## The bound

It is the same one the Lean table theorem accounts with (`Accounting/Bound.lean`, PROTOCOL.md §15).

- **The Johnson radius** is `γ = 1 − √ρ − η`, with `η = 1/50`.
- **The query term:** a word `γ`-far from the code survives `Q` stratified queries with probability at most
  `(√ρ + η)^Q`.
- **fast100's rule** is `Q · log₂(1/(√ρ + η)) ≥ 100` at every level. It gives 218 at `ρ = 1/2` (100.23 bits).
- **The list bound** is ArkLib's `⌊1/(2ηρ)⌋`.
- **Mutual correlated agreement** is BCHKS25 Theorem 4.6, over GF(2^256).

**M1's level-0 code** is `RS[2L, L + t_pad]`, so `ρ′ = (L + t_pad)/(2L)`. This follows `flock-zk-m1-report.md`, since
I couldn't read #123's `PROTOCOL.md` with GitHub auth down. Each lane is `f + (X_L + c)·μ` with `deg μ < t_pad`. The
lane sets `t_pad = 2Q₀ + 64`, which closes a loop: more queries mean more padding, a higher rate, and more queries. The
counts above are the least fixed points.

## Where the profile stands with today's 218 (t_pad = 500)

| m | ρ′ | level-0 bits per run | one run | one table (two reps) |
|---|---|---|---|---|
| 25 | 0.5610 | 82.60 | 2^-82.6 | 2^-165.2 |
| 26 | 0.5305 | 91.16 | 2^-91.2 | 2^-182.3 |
| 27 | 0.5153 | 95.63 | 2^-95.5 | 2^-190.9 |
| M0 (ρ = 1/2) | 0.5 | 100.23 | 2^-98.3 | 2^-196.5 |

- **The 2^-128 target still holds with 218.** What breaks is the profile's per-level rule, and with it its stated
  2^-97.8 per run and 2^-195.5 per table.
- **With the recount,** a run is 2^-98.2, 2^-98.3 and 2^-98.3 at m = 25, 26 and 27, and a table is 2^-196.4 to 2^-196.6.
  That is M0's figure on the same formula.
- The run and table columns replicate the Lean `repError` (Bound.lean), with the padded level 0. The PIOP shape is a
  conservative stand-in (`kLog = m − 6`, 8 regions). The PIOP terms are about 2^-114, far from binding.

## The other terms

- **Folding at level 0** is about 2^-210 at every m. The MCA numerator stays near 2^40, because `⌈√ρ′/η⌉` moves from
  36 to 38.
- **The two extra lanes** add one more batching combination, a term of the same order.
- **The level-0 list shrinks** from 50 to 43–48, so the list-multiplied PIOP terms shrink slightly.

## Other sizes

- **m = 28–31** needs 219 queries (t_pad 502), and **m ≥ 32** keeps 218.
- **m = 22–24 has no solution at rate 1/2.** With `L ≤ 2048`, the padding outgrows the message, and the fixed point
  runs off to `ρ′ → 1`. Level 0 there would need rate 1/4, or a smaller `t_pad`.

## What to check

1. **That `ρ′` is the rate the soundness argument sees.** The committed level-0 lanes, and the two extra lanes, should
   be `RS[2L, L + t_pad]` codewords. The query analysis measures distance to that code, not to `RS[2L, L]`.
2. **That `t_pad = 2Q₀ + 64` covers every level-0 evaluation the verifier learns.** That is `Q₀` openings in each rep of
   the one root, plus the OOD value, the lane messages and the extra lanes' sums. It is ZK-side, but it moves the rate.
3. **The ordering fix (`e` before `ρ₀, ρ₁`, commit `652357eb`)** is needed for the extra-lane batching term to be a
   proximity-gap term at all.
4. **The Lean table theorem covers M0's unpadded level 0 only.** The accounting's `Level` has a power-of-two rate. M1
   needs a padded length `2^cols + t_pad` in `Level`, and the padded encoding in `Model`. I can add both once M1's
   layout is final.
