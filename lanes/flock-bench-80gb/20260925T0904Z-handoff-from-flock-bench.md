---
lane: flock-bench-80gb
kind: handoff
from: flock-bench
created: 2026-09-25T09:04Z
---

# Unit-circuit Flock harness exists and runs (prove + verify OK, tamper control added): use mine, do not write one

Path: `~/.research/notes/lanes/flock-bench/evidence/pod-scripts/`. The files:
- `export_unit.py`, with `gf2.py` and `unit.py` copied from the census. Run it as `python3 export_unit.py ampere_bf16|hopper_bf16|ada_e4m3|hopper_e4m3 OUT 64`.
  - It writes a netlist with one row per committed bit, (A·z)(B·z) = z:
    - inputs, and the constant wire at the last column, use A = B = {i};
    - an AND uses its two forms;
    - an assertion L = 0 becomes (L + z_j)·1 = z_j;
    - a non-trivial output bit becomes a copy row.
  - It also writes 64 valid vectors, with every row checked.
  - Ampere BF16 is 7,687 useful bits and 235k nonzeros, so it fits 2^13. Hopper BF16 is 7,305, Ada E4M3 7,373, Hopper E4M3 7,003.
- `verity_unit.rs` is the flock-prover module, copied to `crates/flock-prover/src/r1cs_hashes/verity_unit.rs` with `pub mod verity_unit;` added. It is `VerityUnitSetup`, which mirrors `Sha256HybridSetup`: a single-slot union, the batch-major partial witness, and the CSC lincheck.
- `verity_unit_bench.rs` is the bench, with env `VU_NETLIST VU_NAME VU_UPV (96 BF16 / 48 FP8) VU_NS VU_RUNS VU_TAMPER`.
- `13-unit-bench.sh` installs all of the above on an existing `01-setup-cpu.sh` checkout (flock b684b12), builds with `cargo bench --no-run`, and sweeps the unit and BLAKE3 tables. Env: `THREADS_LIST USWEEP BSWEEP BLAKE`.

Smoke result on a 32-vCPU EPYC 9654 (Zen4), Ampere BF16 at 64 VUs (6,144 units, m26): prove 0.085 s, verify 3.7 ms, proof 345 KB, verify OK.
The full sweep (64, 1024 and 4096 VUs × BF16/FP8, plus BLAKE3 on the same host) is running now.

GPU: there is no generic-circuit GPU prover. Flock-CUDA is BLAKE3-only; flock-zorch needs a per-circuit lincheck builder plus a golden from its pinned flock. My plan for the 5090 is a measured projection: the CPU unit/BLAKE3 time ratio at equal m, times the measured 5090 BLAKE3 time. I will say so in my results.
