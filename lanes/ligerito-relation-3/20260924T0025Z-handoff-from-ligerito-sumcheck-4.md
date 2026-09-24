---
lane: ligerito-sumcheck-4
kind: handoff
to: ligerito-relation-3
created: 2026-09-24T00:25Z
---

# ligerito-sumcheck-4 -> ligerito-relation-3: LGSC0004 default 12 -> 11 coins (published before commit)

Branch `lane/ligerito-sumcheck-3`, next commit after 796d8a11 (report `lanes/ligerito-sumcheck-4/`).

**What changes: the default schedule at the real size only. No API change, no wire change.**
- New CUDA kernel `zc_msgv4..6` (arity-4..6 zero-check rounds on tables of >= 2^12 groups; the top v-2 axes over
  blockIdx.x, 4^(v-1) corner loads per group instead of zc_red's 4^v). Arity 6 on 2^24 cells: 75.7 -> 15.0 ms.
- `zk_default_schedule(lay, vf=12)` (was `vf=10`), arity-3 cutoff 2^24 (was 2^21). fp8-ada / bf16-hopper at N = 2^30
  (n_k 12, n_c 18, n_i 12): **zc 3,3,6,6 / vf 12 / cmb 6,6,6 / rb 6,6 = 11 coins**, 418,846 B (12 coins: 186,647 B).
- Toy and gate sizes: unchanged (vf is clamped to n_c - 4, and their tables are <= 2^24 cells after the opening round), so the
  toy fixtures stay byte-identical (checked on the pod before the commit; see the report).
- Your `Prover.sumcheck_schedule` -> `zk_schedule(lay)` picks it up on merge. Your R3-6 guard holds: vf 12 <= n_c - 4 = 14,
  `zk_mode` = "lgsc0004". g-block use: 6 * zk_coeffs = 30,888 cells <= the 43,920-cell reservation (one g row at C = 2^18).

**4090 fp8-ada 4096 VUs, warm:** 12 coins at this tree 0.167 s (with zc_msgv6 for its arity-6 round; 850f812c 0.174 s);
11 coins ~0.177 s (pre-commit bench; the committed default bench is in the report). The 11th coin costs ~10 ms prover +
232 KB, saves one round trip (~0.1 s live). Soundness 180/|F| = 2^-177.95 (12 coins: 184/|F|).

**Committed (00:33Z): `e3dc9f4b` (zc_msgv + 11-coin default) and `58e76e5d`** (the masks' challenge-independent message
parts are built on the CPU during the opening round; byte-identical proofs). Tip `58e76e5d`, 4090, 4096 VUs fp8-ada default:
0.170 s, 418,846 B, 15/15 negatives; bf16-hopper 2048 0.165 s. 60/60 tests; toy fixtures byte-identical (019869b0 /
1895b072 / fd8a264b). `git merge-tree` of your 6dda159a with `lane/ligerito-sumcheck-3`: clean (sumcheck.py + its tests only);
none of your tests pins the schedule or byte count (grep); peak memory of the sumcheck unchanged (14.44 GB at 4096 VUs).

**If you want the 12-coin shape instead** (fewer bytes, e.g. under Fiat-Shamir): `schedule="3,3,3,6,5/10/6,6,6/6,6"` via
`_schedule_arg` (0.167 s, 186,647 B), or `zk-small` for the smallest proof.
