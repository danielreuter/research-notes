---
lane: agkr-nvf4
kind: report
created: 2026-09-24T20:58Z
status: open
---

CHECKPOINT ab57df0a (22:40Z) [open] recording ab57df0a (depth-1 flatten, merged LK, eq_rows_dot, leaf_q, gate_eval qvals) dev t.total 0.274s; prior recorded c20d 0.529s + 3b51 1.044s preserved; verify-po handoff for 3b51 filed; next: register, new handoff, hill-climb
CHECKPOINT 18ab232e (22:17Z) [open] recorded c20d t.total 0.529s (eq_rows_dot kernel, a8d471ba) art:202f23f1 result art:6aff989d run-files PRESERVED; merged LogUp tables 18ab232e dev 0.378s; negatives on merged circuit running; verify-po handoff for 3b51 written
CHECKPOINT 3c769c6d (21:52Z) [open] cell r20260924-213637-3b51 t.total 1.044s 2^-130.19 art:fe57e68b result, art:30c5bdf7 run-files PRESERVED; next: verify-po handoff, recorded negatives, hill-climb
CHECKPOINT 3e34d97e (21:11Z) [open] fp4-nvf4 A-GKR end-to-end at 64 VUs on 5090: py+rust accept, 2^-130.19, 0.27s; running 4096 dev; next: negatives, recorded research run, register
CHECKPOINT ab9573fd (20:58Z) [open] pod vy-agkr-nvf4 up (5090); bf16 smoke rc=0; gpu/nvf4/circuit.py compiles (418 cols,587 wires,depth3); multi-public chain in prover.py WIP; next: run.py/Rust multi-public, nvf4 witness, bench_result fp4-nvf4
# agkr-nvf4: A-GKR on the RTX 5090 NVFP4 row

## Design (commits 679697a4, 3e34d97e, 3c769c6d on lane/agkr-nvf4)

- `backends/gkr/gpu/nvf4/circuit.py`: the fp4-nvf4 unit = B-Ligero's `relation.compile_fp4_unit(chain=True)` line for
  line, compiled on `GkrCtx` (a `LigeroCtx` subclass): rng -> R<b> LogUp queries (16-bit limb split above 16 bits),
  boolean -> R1, lookups -> native row-listed tables (E2M1X2 256 rows: pair code 16a+b -> (na nb, nz); UE4M3X2 127^2 rows:
  scale pair 128sa+sb -> (ma mb, X, nz); POW19/POW24/RLO/RHI), shifter digits = committed R12 columns + one assertion,
  products = product wires (depth <= 3), every linear constraint keeps LigeroCtx's integer audit.  B-Ligero's pins (the
  verifier's decode) become in-circuit decode from committed operand codes (`_decode`: lookups, `any` via inverse hint,
  `part = any * nz_scale`, `G` = max by a one-hot selector over 5 candidates with range checks).
  Unit: 418 columns, 587 wires, 169 products, 93 assertions, 241 queries.  Epilogue: (s, t, f) + `s` boolean + `t` R8.
- Statement: as agkr-table's BF16 cells, the chain endpoints only (c_0 = 0 via init 0 links, final word public); the
  operand codes are witness.  The final FP32 word is 3 public columns (sign, exponent field, fraction; a 32-bit word is
  not a BabyBear element): new optional `public s t f` line in chain.txt (prover.py Chain.epi_pub, run.py read_chain,
  Rust main.rs/verify.rs; absent -> [y16], unchanged).
- `gpu/nvf4/witness.py`: B-Ligero's device hints (`fp4/hints_device.unit_hints_torch`) step by step over the VUs, the
  decode hints, then the unit's `System.program` over all 24 N units in exact int64 (inverses in the field); CUDA-graphed.
  `check_rows` = every assertion/quadratic on the rows (28 VUs: 0 failures).
- `bench_result.py --relation fp4-nvf4`: frozen NVFP4 set via `fp4/chain.instances_fp4` (digest = contract.NVFP4_INSTANCES_DIGEST
  at 4096), profile NVFP4_SM120, K = 1536 passed to soundness.budget.
- `packed/kernels_triton.py`: Triton 3.4 (5090 pod) rejects `X: tl.constexpr = v` globals -> `X = tl.constexpr(v)`.

## Evidence so far
- dev 4096 VUs on the 5090 (1 rep): t.total 1.087 s, Rust accept 0.19 s, 2^-130.19, contract clean, peak 8.5 GB.
- negatives (14 VUs, all 14 families): 115/115 rejected (54 at the verifier: Rust 54/54 too; 61 at the prover: lookup
  miss / nonzero sum); Rust `mutate` on the honest control 148/148.  4 wrong-rule variants reach the model's word on the
  512 variant VUs (frac26, frac28, negzero, participate-zero-scale: no chain-level negative, as in B-Ligero's gate).
- BF16 hopper smoke at 4096 OOMs on the 32 GB part (7.3 GB cupy in the opening; agkr-fp8's 07a8edd6 addresses it); not needed here.
