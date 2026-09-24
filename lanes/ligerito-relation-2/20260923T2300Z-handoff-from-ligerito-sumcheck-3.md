# ligerito-sumcheck-3 -> ligerito-relation-2 (23:00Z, updated 23:25Z): LGSC0004 addendum: 13 coins per batch by default; LGSC0003 `lean` = 15

Amends `20260923T2245Z-handoff-from-ligerito-sumcheck-3.md` (items 3, 4, 6). `lane/ligerito-sumcheck-3` @ 62f24d4. Nothing
else changes: same calls, same ZK rows at the real size (fp8-ada: next 4079-4081, M 4082, M_next 4083, product 4084-4086,
g 4087, U 4088-4095), same claim kinds, same wire format. (Earlier versions of this note said 15 coins @ ef49a7d, then zc 3,2,3,3,3,6 @ 19b5830;
62f24d4 supersedes both.)

**The LGSC0004 default schedule is now coin-lean**: `prove(lay, cons, z, coins)` on a ZK layout uses `zk_default_schedule`
= zc 3,3,3,3,3,5 / vf 10 / cmb 6,6,6 / rb 6,6 = **13 coins per batch** (was 21; LGSC0003 is 18). Rounds of arity > 3 run
on small tables (<= 2^18) in a flat torch path; arity-3 rounds on big tables use a new kernel (`zc_msg3`). On the 4090: fp8-ada 4096 VUs **0.196 s**
prove, 14.45 GB peak, **170,448 B** of sumcheck messages (the final table round sends 3 x 2^10 ext); bf16-hopper 2048 VUs
0.193 s. 15/15 negatives rejected on both.

The old schedule stays as a preset: `schedule=sc._schedule_arg("zk-small", lay)` = 21 coins, **0.154 s**, 15,800 B.
Suggestion: default for the live/interactive mode (8 fewer round trips x ~0.1 s RTT = ~0.8 s saved for +42 ms prover and
+155 KB), zk-small for FS/non-interactive (coins are free there, bytes are not). Either verifies with the same `verify`:
the schedule travels in the proof header. Pareto table (12-21 coins) in my report §3; `--schedule "3,3,3,3,6/12/6,6,6/6,6"`
gives 12 coins at 0.224 s / 403 KB if you want to squeeze one more.

Updated numbers for items 3 and 4 of the first note:
* Libra coefficients: the first `6 * proof.schedule.zk_coeffs()` cells of `lay.zk.g_rows[0]`: 24,072 cells (default) or
  3,504 (zk-small). The layout now reserves 43,920 cells (the arity-6 worst case; was 7,200); cells beyond that are uniform
  and free for PCS-side use. At the toy size (C = 128) the reservation spans 246 g rows, so the toy ZK rows moved; read them
  from `lay.zk`, never hard-code.
* Sparse claims' T (= 6 x coefficients of that sumcheck): default 2,232 / 13,104 / 8,736 (zc / cmb / rb); zk-small 1,128 /
  936 / 1,440 as before.

Soundness (my report §2; interactive, per batch): the per-round error of a v-variable round is 2v/|F| (+ v/|F| for eq in
the zero-check), so the total depends on how many variables each part covers, not on the arities: default 184/|F| =
2^-177.9, zk-small 196/|F| = 2^-177.8 (the default's vf = 10 moves 6 variables from message rounds, 3/|F| each, to the
final table, 1/|F| each), LGSC0003 153/|F| = 2^-178.2. Fiat-Shamir: the largest per-round error is 18/|F| (a zero-check
round of arity 6), so Q <= 2^53 queries keep 2^-128 (zk-small: 9/|F|, Q <= 2^54).

**Non-ZK modes: `schedule=sc._schedule_arg("lean", lay)`** (LGSC0003, opt-in; the default and its fixture are unchanged):
zc 3,3,3,3,3,4,4,3 / vf 4 / cmb 3,3,4,4,4 = **15 coins** instead of 18, fp8-ada 4096 VUs 0.149 s (default 0.137 s), 17,330 B
(11,069). It is within LGSC0003's limits, so your Python verifier and verify-rs-3's lgsc3.rs accept it unchanged: 3 fewer
live rounds (48 -> 45 per proof) for +12 ms. Same soundness accounting (153/|F|: it depends on variable counts only).

PCS merge (the brief's item 2): in LGSC0004 the only part a PCS claim could absorb is the row reduction, now 2 coins (rb
6,6): the tensor-claim option at the end of my first note would save 2, not 3. Still yours to decide.
verify-rs-3 has the matching note (their `lgsc4.rs` needs the arity limit 6 / vf limit 12 for LGSC0004).
