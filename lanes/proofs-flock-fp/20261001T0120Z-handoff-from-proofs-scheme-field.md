---
id: 20261001T0120Z-handoff-from-proofs-scheme-field
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# At your next gemm_hill.py merge: two more fields on every hillclimb point, `scheme` and `impl`

Daniel wants overhead plots that separate protocol changes from implementation changes (proposal:
`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/protocol-schemes.md`). Your branch holds the merged
`gemm_hill.py`, so please add these to the `verity/hillclimb-point/v0` record. They're additive, so the schema id stays
the same:

- **`scheme`**:
  - `"flock-i-v1"` for today's M0 configuration (SHA-512 Merkle, two Fast100 repetitions, `os-seed-prf` coins,
    batched session, tile layout);
  - `"flock-i-v1+livecoins"` when coins are fresh OS coins every round.
  Derive it from the coin and session fields you already record. Write it into the point, never infer it later.
- **`impl`**: `{"commit": <tree commit>, "prover_sha256": <flock-circuit binary sha256>, "verifier_sha256": <the serve
  binary's sha256, the same binary if one>}`.

Backfill existing roll-up points as `flock-i-v1`, with `impl.commit` from their `commit` field. Tell console the field
names in its lane when it's done. This comes after your clean re-runs.
