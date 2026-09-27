---
lane: vllm-coordinator
kind: handoff
from: one-stage-e2e
created: 2026-09-27T07:45Z
---

# one-stage-e2e -> vllm-coordinator: vLLM's challenge draws are derived, and the standing rule is the verifier's own randomness, no beacon

Routed at the root's request (07:23Z), low priority. No action is needed before your re-baseline.

## Where

`integrations/vllm/verity_vllm/commit/challenge.py`:
- **LEGACY (on by default):** opening positions, identities and the replay seed are derived from the run root, so they are
  Fiat–Shamir over the prover's own commitment.
- **The non-legacy path:** `verity.randomness.derive` of a `source` (a "beacon round" or an auditor key) with the run root as
  context: `challenge_positions`, `identity_picker`, and `replay_key` (= `verity_sampled_proofs.law.vu_key`).

## The rule

The verifier draws every coin directly from its own randomness, after the registration it follows. There is no beacon, and
no draw is derived from a commitment (Daniel, Sep 27; `docs/audit-protocols.md` §0.3).

## What's available now

- **[PR #132](https://github.com/danielreuter/verity/pull/132)** adds `verity_sampled_proofs.law.OwnRandomness`. Its exact
  samplers read the operating system's bytes directly, and they are the Lean verifier's `Flock.Draw` samplers: 80 of 80
  agreement with `flock-verify draw --stream`. `select_replay_units` and `select_verification_units` take it in place of a
  `Key`. `vu_key` is kept, unchanged, for your LEGACY path.
- **The one-stage audit** draws through the Lean `flock-verify draw`, or M0's `serve --draw` / `--draw-file`. It sends the
  draw in the clear after the registration receipt.

## Suggestion

At the re-baseline, have `challenge.py` take the verifier's draw rather than derive one: an `OwnRandomness`, or a received
draw object in the §7.3 form `{"law", "population", "k" | "p", "units"}`. Until then, LEGACY stays as it is: it's recorded in
verdicts, and changing it would move digests.
