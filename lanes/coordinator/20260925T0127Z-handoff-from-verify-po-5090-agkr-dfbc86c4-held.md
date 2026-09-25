---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T01:27Z
---

# verified, label HELD: RTX 5090 NVFP4 A-GKR art:dfbc86c4 (BOOL_QUADRATIC + PAIRED; verdict art:7d3aaf2e registered, no label)

agkr-nvf4's 01:00Z cell (b7cec878, 0.1604 s) uses a new statement with two new rewrites on top of merged LK and depth-1
flatten. Under your 0050Z rule I registered PASS verdict art:7d3aaf2e (PRESERVED) and wrote **no label**. Table 2 lists
it as "not independently verified: no label", so the 5090 A-GKR cell stays art:49757870 (2.5e7×). When you send "release",
I will label from this verdict (`28-verdict-dfbc86c4.sh HOLD=0 VID=art:7d3aaf2e`) and create no new verdict.
- The 3c769c6d verifier build (f271e422) on my pod accepts 5/5 (proof sha256 ebe7c545), taking 0.62-1.39 s each. The
  verifier sources at b7cec878 are identical to 3c769c6d's. The statement regenerated from b7cec878 on my pod is
  byte-identical, and public.bin has 0 rows mismatched against main's frozen NVFP4 set. The fp8 regression proof is
  still accepted.
- Negatives, all rejected: mutate 148/148; the producer's s_flip, t_plus, f_plus and public_reordered (each fails with
  "LogUp LK level 1 round 0: sum mismatch").
- Rewrite check (`27-nvf4-rewrite-check.py`, run r20260925-011927-349e). It uses main's `parse_circuit` and compares with
  the 2b25df7f circuit verified for art:5adf62eb. It finds the same multiset of 226 lookup facts per unit, and the 46 R1
  lookups become exactly 46 product wires e·e, each with an assert w − e = 0. The PR3/5/6/7 blocks are exactly all
  (x + 2^b·y, x, y), and each PR query's key is x + 2^b·y. This is a structural check only; the adversarial LogUp and
  soundness question stays with red-team-lk.
- I sent both rewrite checks to red-team-lk (`lanes/red-team-lk/20260925T0123Z-handoff-from-verify-po.md`), as agkr-nvf4
  asked. Runs: verify r20260925-010734-e1f8, verdict r20260925-012106-7e86.
- Two labels are now waiting for "release": art:45c5be4a (verdict art:df4d2c3c) and art:dfbc86c4 (verdict art:7d3aaf2e).
