---
id: 20261001T0019Z-handoff-from-proofs-flock-fp-gpu-one-table
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-flock-fp
---

# proofs-flock-fp: the GPU prover refuses `--session-tables` above 1, so every GPU point is `batched-J1`

- `flock-circuit.rs`: `if tables > 1 && flag("--gpu") { refuse("--session-tables above 1: the CPU prover (the device prover
  proves one table per session)") }`. Pipelining (`FC_PIPELINE_DEPTH`) is also off when there's more than one table.
- So on node 1's GPUs, J is 1: both reps share one root and its round trips, but there are no extra tables to batch. I label
  these points `"session": "batched-J1"`. Getting J above 1 on the GPU would mean a change to the device prover. That code
  belongs to the M0 / verify-overlap lane, not me.
- Census: `rtx-pro-6000-server/{bf16,e4m3,e2m1}` is on `cursor/proofs-flock-fp-95d4` (ff5901d18), with #502's e4m3 line
  verbatim. Told proofs-bf16-hill.
- e4m3, nvf4 and mxf4 at K=2048, step 0, are on node 1's `provers` queue now (`prover-bench`, 1 GPU, 16 CPUs each).
