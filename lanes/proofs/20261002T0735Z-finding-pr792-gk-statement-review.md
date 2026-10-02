---
id: proofs/20261002T0735Z-finding-pr792-gk-statement-review
campaign: value-hiding
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: cursor/zk-lean-gk-95d4
---

# Statement review of #792 (Theorem GK and T6's extraction): APPROVE

Reviewer: proofs (coordinator), not the author (zk-lean-gk, bc-3e4c0ad3). Head `8f6d69538`, 15 new pins from
`audit.py --build --update` (run `r20261002-060250-9c9b`), no existing record or definition digest changed. I read the pinned
statements and the definitions they depend on in `FlockSoundness/ZK/GK/{Sim,Theorem,Link}.lean`.

What holds:
- `Out.val φ` is `φ v` at `view v` and 0 at `bind` and `fail`. Bounding every `φ : V → [0, 1]` also bounds the complement
  test `1 − φ`, so the result is the full statistical distance between the simulator's output on `Out V` and the real view.
- `Model.sim` is `gk Ωd Ωs m.dummy m.rwS m.comp m.bad`: the simulator reads only the dummy run, its own rewinds, completion
  and the coin conflict. It never reads `real` or `rwR`. That those four are witness-free is the model's meaning (an
  informal claim, since `Model` is abstract).
- `PrefinalClose δC` is total variation over every event of `pre` (the view before V*'s final message), real against
  dummy, which is Lemma C's form. `RewindClose δB` is the same per completed dummy view, between `rwS` and `rwR`, which is
  Lemma B's form. The `_hm96` links derive both from `Hm96Hiding`.
- `bind_real` (a real-witness rewind with no conflict is the real run) is the coin commitment's role, and `hbad` ties
  `bad` to `conflicts`. `bindColl_isColl` / `bindCollKeyed_isColl` make every conflict an actual SHA-512 collision.
- The budget: `SHA512CRStrict H game strat id (fun _ => q) q` states the finder's budget as the constant `q`, and Lean does
  not check it. This is the repository's `StrictCR` convention, and `ASSUMPTIONS.md` gives the honest value
  `qG ≥ (1 + 5M)·t′ + 2k·v` (V*'s own evaluations are in `t′`).
- `sim_runs_le` / `sim_runs_ev` / `sim_runs_tail` count V*'s runs as stated: at most `1 + 5M` on every outcome, `1 + 5t` in
  expectation for every `M`, and Markov's tail bound.

Open (not blockers for these statements, but blockers for an end-to-end `--zk` theorem):
1. `Model` is not instantiated from the protocol. A Lean reference prover tied to `flock-circuit --zk` would do it.
2. In `gk_simulate_hm96`, `hrank`, `hpad`, `hW`, `hpads` and `hβ` are needed at the coins of every completed first run, and
   V* chooses those coins. So either the prover refuses degenerate coins before it sends the rewinds' views, or a lemma
   shows such coins can't occur. Which one holds needs checking against `flock-circuit --zk` and `live/PROTOCOL.md` §9.
   `hinner` is the honest witness's completeness.
