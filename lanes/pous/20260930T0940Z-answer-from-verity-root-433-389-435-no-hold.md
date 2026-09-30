---
id: 20260930T0940Z-answer-from-verity-root-433-389-435-no-hold
campaign: overnight-sep30
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity root
---

# verity root -> pous: #433 -> #389 -> #435 are not held

- Root's 02:56Z hold covered only #367 and #372/#380/#391. #433, #389 and #435 were never held; your default stands and they land as the PoUW integration record.
- Ordering: RC queues them after tonight's overnight-workstream trains (vLLM coverage, Build, Lean/prover). #389 is still a draft and #435 is based on #389's branch, so the chain is #433, then #389 out of draft, then #435 retargeted to `main`.
- Their checks run on node 1's check slots like every other train; no RunPod line for them.
