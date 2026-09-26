---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T19:58Z
---

# For review before any total-unit cell runs: 2^14-row unit slots per statement (PR #87 @ 28f55d9a)

- **The change:** `UnitNet::unit_log()` is 13 for a netlist of at most 2^13 rows, else 14. The statement's `ul` replaces the
  constant `UNIT_LOG` in:
  - `Layout::unit_pos0(ul)` (comp_slots << (comp_log − ul));
  - the Δ unit copies and chains, `(p0 + u) << ul`;
  - the unit region shapes (AccIn / AccOut / Y / AccMid / YMid);
  - `PureCircuit`'s fold (base_u over 2^ul, and per = 2^(comp_log − ul));
  - the witness;
  - the statement digest, which already hashed `UNIT_LOG`, so 2^13 statements are byte-identical.
- **Admission UL1:** `lay.fits(ul)` means unit_pos0 + units ≤ 2^(k_log − ul). Chunk(n), ChunkTail, Fp8, Fp4 and ShaFp4 fit
  at 14 with the same k_log. ShaBf16 and ShaFp8 are refused. `PureStmt::new` asserts it too.
- **CUDA:** only `PURE_UW` grows, to 2^14 bits of per-thread unit state. The kernels already took `unit_log`.
- **What to attack:**
  - Chunk(n) at ul 14: the units now end exactly at 2^20. Check the region bit layouts at 14 (unit bits 0..14, slot bits
    above).
  - The fold's per = 1 when comp_log = ul = 14.
  - The ChunkTail tail regions at unit 15.
  - That no 2^13 statement changed.
- **Evidence:** PR #87. GPU and CPU selftests pass with a total unit (flock-backend's `total_proto` lowered, 8,449 rows) on
  Chunk(4) and Chunk(16) at 8 and 64 VUs, and CPU on ChunkTail(4). Finite-unit regressions and `cargo test` pass.
  flock-backend will pin the real total netlist, with its NaN / inf negatives.
