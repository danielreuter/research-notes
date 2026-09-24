---
lane: ligerito-sumcheck-4
kind: handoff
to: verify-rs-4
created: 2026-09-23T23:58Z
---

# ligerito-sumcheck-4 -> verify-rs-4: LGSC0004 default 12 coins, no wire change

I continue ligerito-sumcheck-3 on `lane/ligerito-sumcheck-3` (report `lanes/ligerito-sumcheck-4/`).

* **850f812c: the LGSC0004 wire format is unchanged.** Only the prover's default schedule at the real size moved: zc 3,3,3,6,5 /
  vf 10 / cmb 6,6,6 / rb 6,6 = 12 coins, 186,647 B (was 3,3,3,3,3,5 = 13 coins, 170,448 B). Every bound your `lgsc4.rs` checks
  (round arity 1..6, 1 <= vf <= 12, vf <= n_c, sums, g-cell budget) already admits it.
* **Toy fixtures unchanged**: at l = 64, S = 2 the default schedule is still zc 3,5,4,4 / vf 3 / cmb 6,6 / rb 6,6. I will
  re-generate both LGSC0004 fixtures at my tip and confirm the JSON sha256 (1895b072… default, fd8a264b… zk-small) in my report.
* R3-6: the Python prover will refuse `vf > n_c - 4` on a ZK layout unless the caller opts in (format tests); the verifier keeps
  accepting (your `zk_mode = lgsc0004-underblinded` label matches the Python `zk_mode(lay, schedule)` I am adding). The zk-small
  toy fixture has vf 4 > n_c - 4 = 3 (a format test, not a ZK instance, as before): your label for it should read underblinded.
