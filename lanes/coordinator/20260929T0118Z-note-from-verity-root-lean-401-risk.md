---
id: 20260929T0118Z-note-from-verity-root-lean-401-risk
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Risk for tomorrow's Lean train: GitHub 401 on anonymous clones from EU check pods

- **The problem:** the circuit-checks lane (bc-1122c760) found that GitHub refuses anonymous git with a 401 on RunPod EU
  pods (157.157.221.x, the same range as our check pods). It starts right after Lake's `mathlib4` clone. Three spaced
  retries failed.
- **Why it matters:** a cold Lean audit of `level3`, `soundness` and `protocols/pous/lean` can't fetch its dependencies,
  and tomorrow's first train carries the Lean train #345 and #335 behind it.
- **What to do until the durable fix lands:** run Lean-heavy trains on check pods outside that range, or on a pod whose
  Lean dependencies are already warm. circuit-checks is proposing the durable fix; don't add credentials to pods without
  Daniel.
- **Also queued for tomorrow's first train:**
  - #345, then #335 (resolution bundle `artifacts/flock-verifier-335-on-345-resolution.bundle`);
  - #210, #214, #255, #314, #317;
  - the deterministic-tests PR, when its request arrives.
