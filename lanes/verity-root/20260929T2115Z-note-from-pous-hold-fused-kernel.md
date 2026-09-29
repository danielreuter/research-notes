---
id: 20260929T2115Z-note-from-pous-hold-fused-kernel
campaign: verity
lane: verity-root
kind: note
status: final
repo: danielreuter/verity
origin: pous
---

POUS recommends holding `20260929T2115Z-request-from-pous-gpu-path-fused-kernel` (`vy-pouw-gpu-path`, $2.45). The 4090
rates in `20260929T2115Z-handoff-from-pous-gpu-path-rates` put per-word-leaf hashing alone at 46–80× BF16's linears at
2,048 rows, so the run would only reconfirm that floor. The leaf format is being reconsidered (POUS's cheap-binding lane:
Pearl-style output tickets with a checked clean-up, about 0.001 B/MAC). We will refile, resized, once a leaf format is chosen.
