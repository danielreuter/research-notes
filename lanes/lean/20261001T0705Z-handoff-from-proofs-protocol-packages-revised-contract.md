---
id: 20261001T0705Z-handoff-from-proofs-protocol-packages-revised-contract
campaign: overnight
lane: lean
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Protocol packages in your revised contract: five points to agree on

This supersedes `20261001T0700Z-handoff-from-proofs-protocol-packages-fit`, which used your earlier shape (`Statements`,
`Sanity`, foundations).

Daniel asked why `protocols/one_stage` isn't part of `protocols/sampled_proofs`, where the sampled-proofs Lean lives, and why
protocols still have a `PROTOCOL.md`. My answer is
`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/proofs/protocols-layout.md`.

It follows your contract as the coordinator relayed it at 11:51 PM PDT:
- a trusted part (`Model/`, `Assumptions.lean`, `Properties.lean`);
- a separate `<Package>Proofs` library;
- every pin says that assumptions imply a property;
- shared math in core's Lean package.

Each protocol's Lean is one Lake package at `protocols/<name>/lean/` that requires core's. A backend's Lean requires the
protocol package and keeps only its instantiation. A mature protocol's `PROTOCOL.md` retires into the trusted modules'
docstrings plus a README. The store copy of `docs/lean-infrastructure.md` still shows your earlier version; please update
it, so the coordinator and Daniel read the contract this assumes.

Nothing conflicts. Five points, none urgent; reply in `lanes/proofs/`:

1. **A3's home.** The audit law's coins are the verifier's, so I put `uniform/io-getrandombytes` in
   `SampledProofs/Assumptions.lean`, as an instance of core's uniform-source property, rather than with Flock's assumptions.
   Flock's headline would read it from the protocol package.
2. **Order.** The generic `Audit/` modules (`Law`, `OneStage`, `TwoStage`, `Stratified*`, `Window`, `Work`, `RegDraw`,
   `Influence*`, `Harm`, `Extraction`, `Circuit`, `Closure`, `Examples`) import soundness's `Game.Prob`/`Game.Union`. Those
   move into core's package first; the split then happens when soundness adopts the contract, after #638 lands. That way
   soundness's pins are re-recorded and statement-reviewed once. Agree?
3. **Core needs Mathlib** once it holds probability and games. The zero-dependency verifier then can't require core or any
   protocol package. Where does a protocol's executable reference live? Today it's `Flock/Draw.lean`, which the Python's
   vectors come from. It could stay with the backend's verifier, or become a dependency-free library of its own.
4. **Without `Sanity`,** where do satisfiability witnesses and counterexamples go (here `Examples` and `InfluenceWitness`)?
   Are they still pinned, given that every pin is assumptions → a property?
5. **PoUW.** Its 663-pin package lives in the Project store (`internal/pouw-lean/`), while `protocols/pouw/PROTOCOL.md`
   cites its theorems. I proposed it enter the repo at `protocols/pouw/lean/` directly in your shape, when `pouw-lean` is
   between merges.
