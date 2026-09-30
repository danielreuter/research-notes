---
id: 20260930T2351Z-handoff-from-proofs-live-coins-and-batching
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Daniel, 4:50 PM PDT: from now on, OS-random live coins (no seed mode) and the batched serialized session

This supersedes `note:20260930T2343Z-handoff-from-proofs-record-coin-mode`: switch now, don't just record.
1. **Coins: OS-random live coins.** Turn seed mode off for non-ZK sessions; it's turned on at
   `backends/flock/live/src/bin/flock-circuit.rs:470`, see `coin_seed.rs`. The verifier draws each round's coins from the
   OS, as the verifier of record does. It's the only way M0's soundness path stays on SHA-512 CR only.
2. **Session: the batched serialized session.** Tables and reps each keep their own fresh coins and share round trips: ~220
   round trips per session regardless of table count. It's proved via the pinned `table_sound` and
   `session_knowledge_sound` (red-team #335). **Don't** share identical coins across tables; that's proved only on paper.
3. **Every point from now on:** `"coins": "live-os"`, `"session": "batched"`. Start a new step series at step 0 on this
   configuration, so the console shows it as the baseline. Earlier seed-mode points stay, flagged `coins-seed-mode`.
4. **Overhead** includes the session's interaction (`note:20260930T2348Z-handoff-from-proofs-overhead-includes-verifier`).
5. If you can't find the flags, the old research coordinator was asked at 4:51 PM PDT. @proofs relays its answer. Meanwhile,
   read `flock-circuit.rs` around line 470 and the session code yourself, and proceed.
