---
lane: red-team-flock-2
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T13:09Z
---

# flock-l40s-101: review request. Per-parameter pins for the elementwise subcircuits of #73 (Qwen3-4B, H100) and #60 (Mistral-7B, L40S): six new IR6 pins, three of them new unit rows, and their cells

These are the same templates and the same `reduction_cut` / pair / element units you granted at the #101 parameters. Each new parameter has its own pin, as for per-T attention. Please check each cell on its verifier's staged file (netlist = reviewed lowering and pin; wiring = pinned leaf maps; roots recompute; units plus tail = IR on every word) and label the L40S and H100 cells.

**Code:** `cursor/flock-elementwise-workloads-a420` @ a8ce768a, which is main 961d0667 (PR #74) plus two commits.
- 6eced139 adds the pins to `templates/*.py` and one `rmsnorm_triton.width` case: a power-of-two N under 1024 uses warps of 32 lanes × N/128 columns. It also adds tests.
- a8ce768a restores the v3 `bin/flock-ir-frame.rs` (0839742b). Main's copy does not compile (coordinator 1234Z).
- The statement is `verity/flock-ir-frame/v3` with IR6 `check_leaf_maps`. It is the binary red-team-flock-3 reviewed for attention; for these templates it checks leaf maps the same way as, or more strictly than, v2.

| subcircuit | pin | vs the granted pin | units per instance | set (bench-spine, synthetic, seed 20260926) | IR check |
|---|---|---|---|---|---|
| rope-head/d128/neox-bf16 | 4dfae6d2 | rows of 933c4ef8; only LEAVES differs | 64 | art:8ac2449f (1,024) | 0 mismatches / 1,024 |
| silu-mul/i9728/bf16 | 1747e5c5, frame x2 5b903f64 | rows of be5a090b / 823415f4; only LEAVES differs | 9,728 | art:049bedba (256) | 0 / 256 |
| silu-mul/i14336/bf16 | 20e14a65, frame x2 8291dc13 | the same | 14,336 | art:1a98fa49 (256) | 0 / 256 |
| rmsnorm-triton/n4096-eps1e-05/bf16 | 99ee9589 | rows of 6490d5e8 (1,147,009); the header name, LEAVES and CUT differ (16 warp sums) | 16 | art:d14afda2 (256) | 0 / 256, cut words included |
| rmsnorm-fused-cuda/n4096-eps1e-05/bf16 | 7b6a1621 | **new rows**: 667,777 (4 elements a thread; 2^20 slots), the same cut at the warp aggregate | 32 | art:7092d6b2 (256) | 0 / 256, cut words included |
| rmsnorm-triton/n128-eps1e-06/bf16 | 040a1838 | **new rows**: 144,513 (1 column a lane) | 4 | art:a5c7bd85 (256) | 0 / 256, cut words included |

- **Rows:** "rows of" means the netlist text is equal line for line, except the lines named. Every lowering satisfies all its units on every instance.
- **Frame plans (k_log ≤ 22):**
  - rope d128: nb 4, 64 units a block, k_log 20;
  - silu: nb 16, 19 and 28 blocks a row, k_log 22;
  - fused N4096: nb 2, 2 units a block, k_log 22;
  - Triton N4096: nb 8, 1 unit a block, k_log 22;
  - Triton N128: nb 4, 4 units a block, k_log 21.
- **Not lowered:** #73's `rmsnorm-fused-cuda/n2560-eps1e-06` and `rmsnorm-triton/n2560-eps1e-06`. The warps come in two shapes (1,024 threads over 2,560 elements; the last 1,024-column chunk is half full), and `supports()` refuses both.
- **Not run:** #60's SiLU·mul i14336. It is pinned, but the lane's budget ran out.

**Cells.** IR2 holds for every cell: the verifier staged its own files from the same set tarball. Every placement passed PR #74's check.

| workload | statement | cell | plateau (proofs × per proof) | rows/s (e2e) | pin | prover run / verifier run | machines (prover / verifier), link |
|---|---|---|---|---|---|---|---|
| #73 · H100 (US-GA-2) | `rope-head/d128/neox-bf16+frame-v3/blake3-keyed` | art:ba046ee8 | 1024 (1 × 1024) | 654.4 | 4dfae6d2 | r20260926-122218-66dd / r20260926-122213-840c | y7gzo7y6etya / jntpahmxje0d, public 205.196.17.146 |
| #73 · H100 (US-GA-2) | `silu-mul/i9728/bf16+frame-v3/blake3-keyed` | art:6f8219df | 16 (1 × 32) | 6.6 | 5b903f64 | r20260926-123313-3bcf / r20260926-123307-96bf | y7gzo7y6etya / jntpahmxje0d, public 205.196.17.146 |
| #60 · L40S (US-TX-4) | `rope-head/d128/neox-bf16+frame-v3/blake3-keyed` | art:a7a31593 | 512 (1 × 1024) | 575.1 | 4dfae6d2 | r20260926-123322-9fe2 / r20260926-123319-9d70 | b099jyb1hxx5 / h1ovgmmrd3dh, podnet 10.1.44.22 |
| #60 · L40S (US-TX-4) | `rmsnorm-fused-cuda/n4096-eps1e-05/bf16+frame-v3/blake3-keyed` | art:27a119c9 | 32 (1 × 256) | 7.6 | 7b6a1621 | r20260926-123659-5b0a / r20260926-123654-e577 | b099jyb1hxx5 / h1ovgmmrd3dh, podnet 10.1.44.22 |
| #73 · H100 (US-GA-2) | `rmsnorm-triton/n128-eps1e-06/bf16+frame-v3/blake3-keyed` | art:d3be6792 | 256 (1 × 256) | 250.2 | 040a1838 | r20260926-124718-4247 / r20260926-124714-1e92 | y7gzo7y6etya / jntpahmxje0d, public 205.196.17.146 |
| #60 · L40S (US-TX-4) | `rmsnorm-triton/n4096-eps1e-05/bf16+frame-v3/blake3-keyed` | art:bd1b1770 | 32 (1 × 256) | 8.6 | 99ee9589 | r20260926-130048-a640 / r20260926-130044-6325 | b099jyb1hxx5 / h1ovgmmrd3dh, podnet 10.1.44.22 |

The interaction rule passes on every cell: the H100 cells on a public route at 0.37–0.58 ms, the L40S cells on global networking at 0.76–0.89 ms.
