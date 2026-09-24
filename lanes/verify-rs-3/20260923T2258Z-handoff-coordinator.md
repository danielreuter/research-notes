# coordinator -> verify-rs-3 (22:58Z)
red-team-leaf-3 left you `20260923T2255Z-handoff-from-red-team-leaf-3.md` (H2: unpinned `steps`). That is the LIGERO verifier
(backends/ligero-verify) and belongs to ajtai-leaf-3; ignore it for ligero-verify. One question for YOUR crate instead: does the Ligerito
verifier bind every statement dimension it derives the layout from (n_vus, K/steps, rows, log sizes) to the pinned relation, or can a
prover pick them? If not bound, add it to your list (it is the same class of bug) and say so in your next CHECKPOINT.
