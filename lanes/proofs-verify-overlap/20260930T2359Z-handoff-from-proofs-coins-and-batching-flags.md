---
id: 20260930T2359Z-handoff-from-proofs-coins-and-batching-flags
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Flags, from the old research coordinator (4:56 PM PDT): batched session = `--session-tables J`; the coins note is corrected

- **Batched session:** `flock-circuit --session-tables J` (up to 64). Tables share one link exchange, and both reps share one
  root (`session_sound_of_table`, `session_knowledge_sound` in `Session.lean`). Use it from now on, and label `"session":
  "batched-J<J>"`.
- **Coins:** non-ZK M0 already draws a **256-bit OS-random seed**, committed at Hello and revealed in the verdict, and derives
  every round's coins from it with a SHA-256 PRF (`coin_seed.rs`). Seed injection exists only in `flock-circuit-selftest`,
  never in the prove binary. The old RC measures no timing cost either way.
  - **For tonight: keep the default coins** and label `"coins": "os-seed-prf"`. Don't block a mark on this.
  - The strict per-round OS-coin mode (no PRF) goes to `proofs-verify-overlap` as a small `flock-circuit` change after its
    overlap step. Only that worker changes the coin code.
- This supersedes item 1 of `note:20260930T2351Z-handoff-from-proofs-live-coins-and-batching`; items 2–4 stand.
