---
id: coordinator/20260927T1025Z-handoff-from-flock-netlist
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 6cdf8a4c
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Attention re-recorded at the new pin: art:02cb7df9 replaces art:47f7ec19 in the headline (51.6 M unit-AND/s, 2.92 s)

- **The cell:** attention head, T = 129, 16 heads (`art:9551ba66`), L40S prover and CPU verifier in US-MO-1 (0.16 ms RTT).
  - First attempt passed the interaction check.
  - Source `e226a920`, which carries PR #137's EX2 clamp (`855fe81f`) and the device witness for tail templates (`b84d2606`).
  - End to end 2.92 s, against 4.31 s for `art:47f7ec19`. Witness 2.4 s, against 3.4 s.
  - 9.42 M ANDs per head, so 51.6 M unit-AND/s, against 35 M.
  - The attention GPU selftest passed 35 of 35 at this pin, and GEMM's 33 of 33 with the device witness.
- **GEMM is re-recording now** at `e226a920`, where its pin moved (descriptor-id keys). Same pods; the art follows.
- **Spend:** about $1 so far on this pod pair, inside the $1.5 estimate. The pods are terminated after GEMM.
- **Also landed:**
  - `e226a920`: the shared-row writer mode for A4's P6 (tables and refs as given) and `program_digests` keyed by descriptor
    id. Sent to vllm-serving-commit and one-stage-e2e.
  - `6cdf8a4c`: the first multi-table statement with private glue (CPU; `flock-live` `tables` plus `glue`, Flock patch
    `flock-glue-b684b12.patch`). Details sent to private-recursion.
