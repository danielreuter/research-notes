---
id: 20261001T0412Z-handoff-from-circuits-proofs-agreed-names
campaign: verity
lane: circuits-commit-tokens
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: proofs agreed the record's names and shape (9:15 PM PDT). They are final

- @proofs accepted `verity-vllm/commit-tokens/v1` as specified and added it to the interface page's no-op entry (Slack 1790826524.724449).
  Keep every field name exactly as in `internal/circuits/commit-tokens-record.md`.
- **The rule is n_r = min(cap, a_r + LAG) on an EOS stop**, and the cap on a length stop. `docs/noop-proving.md` now says the same.
- Proofs owns the core output-prefix rule and the Lean filter. Once the verifier performs this check, `link_to_commit_account` retires, and
  proofs will tell circuits when.
