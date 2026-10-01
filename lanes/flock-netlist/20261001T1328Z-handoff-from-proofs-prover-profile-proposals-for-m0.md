---
id: 20261001T1328Z-handoff-from-proofs-prover-profile-proposals-for-m0
campaign: overnight
lane: flock-netlist
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# For M0's agreement: C-Flock prover changes from a K=2048 nsys profile (nothing edited)

The research owner (4:54 AM PDT, Slack `1790855684.072569`) asked that proofs' C-Flock prover changes "come back to me with
the profile, and agree them with M0 (flock-netlist) before any edit, since M0 owns the prover". This is that step.

The profile is proofs-bf16-hill's `r20261001-125609-50f5` (K=2048, step 6, 25/25 accepted), with evidence
`art:ee5f916a410bf307fa06ba1d9b320b1caa9a8c105a7d35f9f28a49641779d05e`. The full write-up, with each change's code path
and expected share, is `note:proofs/20261001T1325Z-report-from-proofs-bf16-hill-k2048-nsys-profile`.

The eight proposals, with shares of a 705 ms K=2048 session:
1. Zerocheck's first round (`zerocheck_round1_cpustyle.cuh`): 17%, at about 12% of DRAM bandwidth. Start with one `ncu` run
   to find its limiter. This is the item whose layout follows the statement's.
2. Live-coin latency (`backends/flock/live`): 287 rounds at 0.18–0.28 ms against a 0.03 ms ping, 7–11%. The hypothesis is
   that the coin server waits behind the verifiers on the same 16 cores. Server-side timestamps first.
3. Ligerito: fuse each fold with the next message, and take its host steps (allocations, synchronous OOD copies, eq
   weights, openings) off the critical path, 3.5–5%.
4. Lincheck at K=16384 (8.5% there), chosen from a K=16384 profile.
5. CUDA graphs between coin rounds, and a session arena for allocations, about 3%.
6. The ring switch's 4.3 GB device-to-device copy, about 1%.
7. NVTX ranges per phase and per coin round.
8. The encoding commitment, after an `ncu` run.

The question for M0: which of these do you agree to, under which constraints (proof bytes and verdicts identical, layout
fixed), and which do you want to own? Reply in `lanes/proofs/`. No edit is made before your answer and the owner's. The next
two profiling jobs, `ncu` and K=16384 nsys, are with the owner.
