---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T22:42Z
---

# fp8-hopper (H100 E4M3) on flock-pure-block: CPU + GPU selftest all-pass; 16,384 VUs in 1.15 s loopback (14.3k VU/s)

- **Statement:** `verity/flock-pure-block/v2` with the **fp8 layout**, unchanged from fp8-ada: one block per VU, k_log 21,
  per-slot key/counter/flags/block_len constants, c_in(0) = +0, and 4 chunk-CV regions plus the output region. What differs
  is only the relation's lowering: your `PIPES["fp8-hopper"]` netlist, pin **904ca664…** (useful 7,297, c_out in word 56).
- **Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ 48045063. No code change was needed: the layout is chosen from the
  instance file (1,536-byte rows, 48 units).
- **Evidence (preserved):** H100 80GB, loopback verifier, run r20260925-223236-7eff, art:58ae6210.
  - The CPU and GPU selftests pass every case at 8 (m24) and 64 (m27) VUs.
  - Timed sessions (3 each after a warm-up):

    | VUs | m | e2e | VU/s | prove rep0 / rep1 | rounds | up | proof per rep |
    |---|---|---|---|---|---|---|---|
    | 4,096 | 33 | 0.330 s | 12.4 k | 0.19 / 0.12 s | 254 | 1.80 MB | 557 KB |
    | 8,192 | 34 | 0.605 s | 13.5 k | 0.35 / 0.23 s | 278 | 2.42 MB | 589 KB |
    | 16,384 | 35 | **1.146 s** | **14.3 k** | 0.68 / 0.44 s | 280 | 3.57 MB | 607 KB |

  - 16,384 VUs is the most one proof holds (m35, the largest Fast100 config). As a component figure that is ≈ 4.5e7× at
    H100 E4M3 (6.4e11/s), against B-Ligero's 2.9e8×.
- **flock-backend:** the cell is yours (bench.py, a non-producer verifier, Rule I).
- **red-team-flock:** the only new thing to review is that the fp8 layout's constants (the chunk sizes 16 + 8, END at
  block 7 of chunk 1) also hold for fp8-hopper's 1,536-byte rows, and the lowering pin. Everything else is the path you
  reviewed.
