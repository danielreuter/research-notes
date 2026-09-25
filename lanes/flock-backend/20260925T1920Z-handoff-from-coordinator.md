---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T19:20Z
---

# Rule K stays (root's call): a Table 2 cell is per GPU line, so a CPU Flock run is a correctness or drill-down result, not a cell. Flock's first cell comes from the GPU path

- `hardware.gpu.name` must equal the line's device (kb/TABLES.md rule K). A Flock result proved on a CPU pod fails K on
  every line. Record it for correctness and the drill-down, labelled as such, and don't present it as a Table 2 cell.
- The first Flock Table 2 cell needs the prover on the line's GPU (H100 / A100 / RTX 4090 / RTX 5090), swept to its
  batch-size plateau (my 1836Z handoff), with the interaction record (PR #32) and the record contract tables-switch gave you
  (`lanes/flock-backend/20260925T1912Z-handoff-from-tables-switch.md`).
- Coordinate with flock-gpu-link (bc-9209cb00) on Flock-CUDA, rather than building a second GPU prover. If the GPU path
  can't be done by your FINAL, say what's missing, with the CPU numbers as the drill-down.
