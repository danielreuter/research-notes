---
id: vllm-serving-commit/20260927T0935Z-handoff-from-flock-netlist
campaign: verity
lane: vllm-serving-commit
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 967b8d06
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Shared-row writer at 967b8d06: byte-match GEMM against it; the other templates are unchanged

- **GEMM:** one-stage-e2e's §3 layout (as amended 09:20Z) is exactly M0's shared-row format. Byte-match against
  `verity_flock.circuit.write(..., share_rows=True)` at `967b8d06`. Details are in
  `note:one-stage-e2e/20260927T0935Z-handoff-from-flock-netlist`.
- **The other four templates:** per-instance files are byte-identical to `68ae79f2`'s writer.
