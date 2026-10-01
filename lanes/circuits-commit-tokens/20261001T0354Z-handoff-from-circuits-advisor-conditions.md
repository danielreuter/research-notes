---
id: 20261001T0354Z-handoff-from-circuits-advisor-conditions
campaign: verity
lane: circuits-commit-tokens
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: the advisor accepts the commitment link under R17-27 (a), on four conditions. Build all four in, each with a refusing test

From @old-circuits-and-proofs, circuits' research owner, 8:49 PM PDT (Slack 1790826524.716879):
1. **Independent tokens.** `generated_token_ids` come from the engine's served output path (vLLM's `RequestOutput`, what the client receives).
   Record them independently of the committer's store. If the tokens are read back from the committed store, the check is circular.
   Test: a record whose tokens were taken from the store is refused.
2. **Merkle-verified openings.** Open each served token from `run_root` with its Merkle path and verify it, not just look it up by identity.
   Test: a tampered path or value is refused.
3. **`finish_reason` agrees with the opened tokens.** `stop` requires the stop predicate to hold at n_r under the declared EOS and LAG;
   `length` requires n_r = cap with no earlier stop. Test: each mismatch is refused.
4. **Boundary linkage over the same prefix.** The replay's exhaustive boundary linkage (sampled id[s−1] → input id[s]) still runs over the
   same executed prefix, so the committed tokens are the ones the next step consumed. Confirm it does on the early-EOS case, and add an
   assertion if nothing checks it today.

The spec is updated: `internal/circuits/commit-tokens-record.md`.
