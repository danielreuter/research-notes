# ligerito-sumcheck-3 -> verify-rs-3 (23:00Z, updated 23:25Z): LGSC0004 addendum: new default schedule, wider limits, new fixtures

Supersedes the fixture and hash in `20260923T2245Z-handoff-from-ligerito-sumcheck-3.md`. The WIRE FORMAT IS UNCHANGED (same
header, body, coin order, and checks). What changed at `lane/ligerito-sumcheck-3` @ 62f24d4:

1. **Parser limits for LGSC0004 only** (LGSC0003 keeps MAX_ARITY = 4):
   * every zc / cmb / rb round arity: `1 <= a <= ZK_MAX_ARITY = 6` (a round message is 3^a ext; 3^6 = 729)
   * the final table round: `1 <= vf <= ZK_MAX_VF = 12` (still also `vf <= n_c`)
   Your `lgsc4.rs:114` checks all four against `lgsc3::MAX_ARITY` (4), so it will reject the new default proofs. Your
   rb-arity tamper test (`lgsc4.rs:536`) must use a value outside 1..=6 (0 or 7) to still be rejected at parse.
2. **The LGSC0004 default schedule is now coin-lean** (`zk_default_schedule`): at the real size (n_k 12, n_c 18, n_i 12)
   zc 3,3,3,3,3,5 / vf 10 / cmb 6,6,6 / rb 6,6 = **13 coins** (was 21), 170,448 B of sumcheck messages (was 15,800 B; the
   vf = 10 table is 3 x 1024 ext). The old schedule is the preset `zk-small` (21 coins, 15.8 KB). A proof carries its
   schedule in the header; the verifier accepts any schedule within the limits. Relation-2 may pick one per mode (default
   for live, zk-small for FS): your verifier must take either. (Earlier versions of this note said 15 coins @ ef49a7d and
   zc 3,2,3,3,3,6 @ 19b5830; the toy fixtures below are the same at all three tips.)

3. **LGSC0003 `lean` preset** (opt-in for relation-2's non-ZK live mode; the LGSC0003 default and fixture 019869b0… are
   unchanged): zc 3,3,3,3,3,4,4,3 / vf 4 / cmb 3,3,4,4,4 = 15 coins. Within LGSC0003's limits (arity <= 4), so lgsc3.rs
   should accept it as is; if you pin schedules anywhere, allow it. Regenerate a toy fixture with
   `python -m backends.direct.ligerito.sumcheck --schedule lean --fixture PATH` (at the toy size it is zc 3,4,4,4 / vf 4 /
   cmb 4,4,4, the tests' "arity4" schedule).

Also: `ZK_CELLS_PER_VAR` in layout.py grew from the arity-4 worst case to the arity-6 worst case (6 x 122 cells per sumcheck
variable), so the toy layout has more g rows (C = 128: 246 g rows, `layout.zk.g_rows` 3842..4087) and every other ZK row
moved. At the real size it is still one g row (43,920 cells < C = 2^18). Read the rows from `layout.zk` as before.

Fixtures (all fp8-ada, l = 64, S = 2, `LocalCoins(b"fixture")`, masks from `sha256(b"fixture-masks")`), in
`~/.research/notes/lanes/ligerito-sumcheck-3/evidence/`:

| file | schedule | coins | proof B | JSON sha256 |
|---|---|---|---|---|
| `lgsc0004_fixture_fp8-ada_l64_S2.json.gz` (default) | zc 3,5,4,4 / vf 3 / cmb 6,6 / rb 6,6 | 10 | 81,093 | `1895b0720b8d85d4864b708e3c18316979aab664be0ce9de20b43ea07fbd4778` |
| `lgsc0004_fixture_fp8-ada_l64_S2_zksmall.json.gz` | zc 3,3,3,3,3 / vf 4 / cmb 3,3,3,3 / rb 4,4,4 | 14 | 12,985 | `fd8a264b562d31d60e724d64cf2096af4b643ac0882300b803f1f4fa8572a62a` |
| `lgsc0004_fixture_fp8-ada_l64_S2_f0b9567_obsolete.json.gz` | (the one you verified; old layout) | 14 | 12,985 | `8c89da93…` |

Regenerate: `python -m backends.direct.ligerito.sumcheck --zk --fixture PATH [--schedule zk-small]`. Both new fixtures have 8
negatives (4 byte flips, "zc"/"all" cheats, broken mask link, broken product row). The default fixture's `zk_g_cells` has
20,040 cells (`EXT_DEG * coeffs()` for its schedule). The LGSC0003 fixture is unchanged (019869b0…).

In your `lgsc0004_fixture_fp8ada_toy` test, the pinned schedule `(vec![3; 5], 4, vec![3; 4], vec![4; 3])` and `rounds() == 14`
hold for the `_zksmall` file; the default file is `(vec![3,5,4,4], 3, vec![6,6], vec![6,6])` with 10 rounds.
