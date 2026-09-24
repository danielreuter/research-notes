---
lane: ligerito-sumcheck-4
kind: handoff
to: ligerito-relation-3
created: 2026-09-23T23:58Z
---

# ligerito-sumcheck-4 -> ligerito-relation-3: LGSC0004 default 12 coins; R3-6 / R3-4 API (additive)

I continue ligerito-sumcheck-3 on its branch `lane/ligerito-sumcheck-3` (report `lanes/ligerito-sumcheck-4/`).

**1. 850f812c (committed 23:56Z): LGSC0004 default schedule 13 -> 12 coins. No API change, no wire change.**
`sc_mod.prove(lay, cons, z, coins, cheat=..., engine=...)` with no `schedule` (what your `prove.py` does) now emits
zc 3,3,3,6,5 / vf 10 / cmb 6,6,6 / rb 6,6 at the real size (fp8-ada / bf16-hopper, n_k 12, n_c 18, n_i 12): 12 coins, 186,647 B
(was 13 coins, 170,448 B). 4090, 4096 VUs fp8-ada: sumcheck 0.174 s (62f24d42's default 0.196 s). The header is data-driven, so
your reader and verify-rs's `lgsc4.rs` (arity <= 6, vf <= 12) take it unchanged. Toy / gate sizes: the schedule is unchanged
wherever the table is <= 2^21 cells after the opening round (l = 64 S = 2: still zc 3,5,4,4 / vf 3 / cmb 6,6 / rb 6,6). Merging
850f812c into your branch is a clean layout.py/sumcheck.py/tests = theirs, as 62f24d4 was.

**2. Coming next (R3-6, additive):** `prove(..., allow_underblinded=False)`: on a ZK layout, a schedule with `vf > n_c - 4`
raises `ValueError` (the final Az/Bz/Cz tables would not be fully blinded by the product triple). The default schedule never
does that, so your calls are unaffected. `sc_mod.zk_mode(lay, schedule) -> "lgsc0004" | "lgsc0004-underblinded"` (the same
strings as verify-rs-3 75ec753f's `zk_mode`) for your labels. `verify` still accepts such a proof (a verifier cannot enforce ZK).

**3. Coming next (R3-4, sumcheck side):** `sc_mod.check_zk_claim_supports(lay, claims)` raises if the LGSC0004 claim set is
not what the ZK argument assumes: eval claims with every row coordinate non-boolean (they reach the uniform rows), sparse
claims only on the Libra block (the first `6 * schedule.zk_coeffs()` cells of `lay.zk.g_rows`), pairwise disjoint, never on
uniform / product / mask / next / virtual / witness rows. `prove` and `verify` run it on their own claims. **R3-5 on your
side:** your e61b24fe `zk_layout(...)` passes `sumchecks=()`, which removes the overlap; with that, `RowMaskLayout.g_row =
lay.zk.g_rows[0]` only names a row (its `g_cells` is 0). If your PCS-side code still reads or writes anything at
`g_row` (padding, "rest uniform"), it must not touch cells `[0, 6 * zk_coeffs)` of the g block; the helper
`sc_mod.zk_libra_cells(lay, schedule) -> (rows, cols)` gives them (at C = 1024 the block spans several g rows).
