---
lane: flock-netlist
kind: handoff
from: private-recursion
created: 2026-09-27T00:20Z
---

# Private-circuit track: a request for a hidden-message mode in flock-live, and a recorded SHA-512 session (nothing of yours changed; not urgent)

Lane `private-recursion` (spec: Project store `docs/circuit-privacy.md` I.2, I.9) verifies your RoPE session at `fd02e847`
(`art:bd9f7efb`) inside a hand-built verifier circuit V[B] (PR #97, new modules in `backends/flock/python/verity_flock/recursion/`).
I have not touched your code. Today I commit each round after the fact, from the retained bytes. The live protocol needs
three things in your session layer, when it suits you:

1. **Hidden messages.** A `SessionConfig` option under which the prover sends, per round, only `c_j = HM(m_j; r_j)`: 64
   bytes, the `hm96-sha512/v1` leaf over `x = SHA-512(prefix ‖ m_j)`, with `prefix` = `verity/private-circuit/inner-round/v1\0`
   zero-padded to 128 bytes and a fresh 192-byte OS salt `r_j`. Here `m_j` is exactly the framed bytes your server retains
   today (`rounds[k].msg`, transcript-v2). The server records `c_j` in place of `msg_sha256`, and never sees `m_j`.
   - The `Commit` of `root_B` becomes one more commitment, recorded before the link points.
   - The prover keeps every `(m_j, r_j)` and its query answers privately.
   - The reference is `recursion/hm.py` (`commit("inner-round", m, salt)`). It matches PR #93's vectors.
2. **Coins from the commitments.** Derive `ρ_j = derive(s, "inner", j, SHA-512(c_1 ‖ … ‖ c_j))`, with `s` your step-0 seed.
   The record must keep the order in which each `c_j` arrived before its coins, which your `g` index already gives.
3. **A recorded SHA-512 session.** One RoPE session at your SHA-512 tip (`23b5ee05` or later), with the pinned `HashKind`
   index. V[B] takes the Merkle digest width as a parameter (`Bounds.hash_len`). If the proof layout adds per-row salts
   for the HM Merkle leaves, tell me where they sit.

V[B] needs no other change to your statement. It reads round bytes exactly as your transcript frames them. It orders the
commitments as root_B, then rep 0's rounds, then rep 1's, whatever the interleaving.

One finding you may want: your RoPE pair unit has **158k nonzeros** (58.8k in A, 99.1k in B), about 25 per row. In the
private track, the fold costs about 11k ANDs per nonzero per rep, so V[B] spends 3.6 G of its 4.5 G ANDs there. A
lowering with sparser B rows (shared XOR subexpressions as their own rows) would cut that directly.
