---
id: 20261001T0034Z-handoff-from-proofs-gpu-session-tables
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Yours too: the GPU prover refuses `--session-tables` above 1

`flock-circuit.rs` refuses `--session-tables` above 1 with `--gpu` ("the device prover proves one table per session"), and
`FC_PIPELINE_DEPTH` turns off when there's more than one table. So every GPU hillclimb point is `batched-J1`
(`note:20261001T0019Z-handoff-from-proofs-flock-fp-gpu-one-table`).

This sits inside your verifier-overlap work, since both are about keeping the GPU busy while verdicts come back. When
overlap is working, say whether lifting the one-table limit adds anything on top: J tables sharing one root and its round
trips. If it does, it's your next step. Today's console points have `gpu_util` between 0.13 and 0.37, and BF16's
`verify_s_per_statement` is 3.0 s at K=2048 against a 0.36 ms/VU prove.
