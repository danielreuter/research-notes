---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-zk · kind: handoff · from: flock-soundness (bc-9e538dc5) · status: open · repo: danielreuter/verity ·
re: [PR #123](https://github.com/danielreuter/verity/pull/123), your open item "the level-0 query recount"

# Level 0's query count under your padded code

Here are the level-0 counts that keep fast100's per-level rule (at least 100 bits per run) under your padding, with
`t_pad = 2Q₀ + 64` as you set it:

| m | Q₀ | t_pad | rate | distance |
|---|---|---|---|---|
| 25 | **277** | 618 | 0.5754 | 0.4246 |
| 26 | **242** | 548 | 0.5334 | 0.4666 |
| 27 | **229** | 522 | 0.5159 | 0.4841 |

- **The bound** is the table theorem's: the Johnson radius `1 − √ρ − η` with `η = 1/50`, and the query term
  `(√ρ + η)^Q` at the padded rate `ρ = (L + t_pad)/(2L)`.
- **Each `Q₀` is the least fixed point.** More queries mean more padding and a higher rate, so the count and `t_pad`
  are solved together.
- **Levels 1 and up are unchanged.** m = 28–31 needs 219 queries (t_pad 502), and m ≥ 32 keeps 218.
- **m = 22–24 has no solution at rate 1/2**, because the padding outgrows the message there.
- **With these counts, the profile's per-run and per-table figures come back to M0's.**

The derivation, the numbers with 218, and what to check are with the M1 red team (in the store's
`red-team-m1-zk` folder).
