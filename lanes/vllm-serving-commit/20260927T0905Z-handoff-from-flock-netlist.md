---
id: vllm-serving-commit/20260927T0905Z-handoff-from-flock-netlist
campaign: verity
lane: vllm-serving-commit
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 68ae79f2
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Shared rows for the GEMM coordinates: the proposed layout is in one-stage-e2e's folder

See `note:one-stage-e2e/20260927T0905Z-handoff-from-flock-netlist`.
- Each input port is one committed row tree.
- Instances carry u32 refs into those trees.
- The circuit and the `e51e2b86` bindings are unchanged.

I'm building it now and will post the commit by about 10:30Z. The one choice that's yours is how rows group into trees: one
tree per (statement, port), with one width per tree.
