---
id: 20261001T1426Z-handoff-from-proofs-prover-profile-results-two-questions
campaign: proofs-hillclimb
lane: flock-netlist
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# @M0: the prover profiles are in, with two questions for you before any C-Flock edit

This follows note:flock-netlist/20261001T1328Z-handoff-from-proofs-prover-profile-proposals-for-m0. bf16-hill's write-up is
note:proofs/20261001T1415Z-report-from-proofs-bf16-hill-ncu-zc-round1-and-k16384-nsys (runs `r20261001-135118-4223` and
`r20261001-135122-b18a`). It refines items 1, 4 and 5 and adds item 9. No C-Flock file was edited, and none will be until
you and the research owner both say yes.

**The two questions:**
1. **1b:** is zerocheck's `mcol` (in `upload_zerocheck_first_round_tables`) a map that sends each bit to a fixed GF(2^8) element
   per byte? If it is, the `s_t0` word build becomes a bit transpose plus masked xors on the ALU.
2. **4a:** can the prover's lincheck comb use the block structure, as the verifier's structured lincheck already does
   (`comb_partial`, C0 = I), instead of `linear_check_compressed_column_fold`'s column-by-column gather? That kernel takes
   30.5 ms per session at K=16384.

**And one yes or no:** 1a is a bench variant on node 1 that computes the GF(2^8) products on the ALU and checks its output
against the current kernel. Is it yours to own, or may bf16-hill run it?
