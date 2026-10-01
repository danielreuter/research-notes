---
id: 20261001T0700Z-handoff-from-proofs-protocol-packages-fit
campaign: overnight
lane: lean
kind: handoff
status: superseded
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Protocol packages in your contract shape: four things to agree on

Daniel asked why `protocols/one_stage` isn't part of `protocols/sampled_proofs`, where the sampled-proofs Lean lives, and why
protocols still have a `PROTOCOL.md`. My answer, written to fit your per-package contract, is
`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/proofs/protocols-layout.md`. In short: each protocol's Lean
is one Lake package at `protocols/<name>/lean/`, in your contract shape (Model, Assumptions, Statements, Sanity, then the
proofs). A backend's Lean `require`s it and keeps only its instantiation. Shared math goes to foundations. A mature
protocol's `PROTOCOL.md` retires into the contract's docstrings plus a README.

Nothing conflicts with your doc. Four points to agree on, none urgent; reply in `lanes/proofs/`:

1. **A3's home.** The audit law's coins are the verifier's, so I put `uniform/io-getrandombytes` in
   `SampledProofs.Assumptions` (an instance of foundations' `UniformSource`), not in `FlockSoundness.Assumptions` where your
   doc lists it. Flock's headline would then read it from the protocol package.
2. **Order.** The generic `Audit/` modules (`Law`, `OneStage`, `TwoStage`, `Stratified*`, `Window`, `Work`, `RegDraw`,
   `Influence*`, `Harm`, `Extraction`, `Circuit`, `Closure`, `Examples`) import soundness's `Game.Prob`/`Game.Union`. So
   foundations' probability and game core lands first (your step 4), and the split happens inside your step 6, after #638
   lands. Soundness's pins are then re-recorded and statement-reviewed once, not twice. Do you agree?
3. **Executable references.** The vectors the Python matches come from `Flock/Draw.lean` in the zero-dependency verifier.
   Should a protocol's executable reference stay with a backend's verifier, or become a dependency-free library of the
   protocol, which the verifier could `require` without pulling in Mathlib?
4. **PoUW.** Its 663-pin package lives in the Project store (`internal/pouw-lean/`), while `protocols/pouw/PROTOCOL.md`
   cites its theorems. I proposed it enter the repo at `protocols/pouw/lean/` directly in your contract shape, when
   `pouw-lean` is between merges.
