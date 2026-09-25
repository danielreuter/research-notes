---
lane: flock-bench
kind: handoff
from: flock-bench-80gb
created: 2026-09-25T09:00Z
---

# flock-bench-80gb (H100/A100 lines) reuses your scripts; who writes the unit-circuit Flock harness? I will unless you already have

I am the sibling lane doing the same measurement on H100 80GB then A100 80GB (coordinator launch, FINAL 15:00Z, numbers by 14:30Z).
I do NOT redo the 5090 / pod-CPU work.

- I reuse your `02-setup-gpu.sh`, `01-setup-cpu.sh`, `10-cpu-bench.sh`, `20/21-gpu-*.sh` and `verity_shape.rs` (copies with
  paths/arch changed live in `~/.research/notes/lanes/flock-bench-80gb/evidence/pod-scripts/`; outputs under /workspace/flock-bench-80gb).
- Unit circuit (census `internal/binary-census/unit.py`, 7,100 ANDs / BF16 unit): unless you reply otherwise by ~09:30Z with a path,
  I write the exporter (Python netlist -> Flock R1CS row lists) plus a Rust bench `unit_shape.rs` in my pod-scripts dir, and will
  drop a handoff to you as soon as it runs, so you can run it on the 5090 / pod CPU instead of writing your own.
  If you already started one, tell me the path and I'll use yours.
