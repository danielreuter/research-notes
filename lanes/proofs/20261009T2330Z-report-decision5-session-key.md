---
id: proofs/20261009T2330Z-report-decision5-session-key
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-ad20837e-6819-5833-9cc4-68a702c2d504
---

## Decision 5 (23:30Z)

**Yes, and better than 2^-128.** If the prover draws a fresh hm96 key for each `--zk` session, the bad-key term goes away
instead of shrinking. The zero-knowledge distance becomes the mean over the key: 2·N_hid·2^-257 ≈ **2^-234 per session**
at the 8090 class, with no `hash-derived-key`. The 2^-64 belongs only to the per-key bound that the pinned key needs.

1. **Where the 2^-64 comes from.** A key K is bad when its hiding gap δ₁(K) exceeds 2^-193 (`Hm96Hiding`, and
   `HashDerivedKey` in `Security/Proofs/Flock/Soundness/Assumptions.lean`, which `Assumptions/Zk.lean`'s
   `HashDerivedKeyHm96` instantiates). δ₁(K) is the distance between (M(K)·y, SHA-512(sp‖y)) and (U, SHA-512(sp‖y)), for a
   uniform 1536-bit salt y and uniform U. The leftover hash lemma bounds its mean over keys at 2^-257
   (`CROnly.hm96_sha512_sum`; hm96 `PROTOCOL.md` §3). Markov's inequality, cut at 2^-193, then gives the 2^-64 fraction
   (`CROnly.hm96_sha512_bad_keys`, from `hm96_bad_keys`' b + e = 257). The cut buys a bound that holds for one fixed key.
   It isn't a property of a fresh draw.
2. **A fresh key needs no cut, and Lean already has the averaged form.** With the key uniform and independent of the salts,
   the simulator draws a key too, and the distance is the mean over the key. That form is proved for Lemma C, with V* and
   the event allowed to depend on the key (`CROnly.adaptive_prefinal_hm96_sha512`, `CROnly/ZKKey.lean`). It is also proved
   for the coin tree's per-session key, which the coin server already draws (`ZkCoins.CommittedLeHm96`,
   `SessionCoinsHm96`). Two conditions:
   - **The prover draws the key, not the coin server.** A key the coin server draws, a malicious verifier would choose,
     and that brings the per-key bound back.
   - **The key is fixed before the commitment.** It goes in `Commit`, before any coin, and every leaf's prefix binds
     H(key). This is red-team-hm96 F6: a key chosen after the commitment opens a leaf to any value
     (`leaf_key_witness_refused`).
3. **The candidate parameters.**
   - Key length and derivation rounds: no effect. The Hankel family fixes the key at n + l − 1 = 2047 bits, and the
     derivation bears only on the pinned key's common-reference-string step.
   - Rejecting bad keys, by the prover or by a verifier check: impossible, so no check can remove the term. δ₁(K) is a
     statistical distance over 2^1536 salts through SHA-512, and nothing can decide it efficiently. M(K)'s full rank is
     checkable, but it is necessary, not sufficient.
   - More salt bits: works, but only for the per-key form. The rule is n + m + 2a ≤ l and b + e = a + 1, so a 1664-bit
     (208-byte) salt gives 2^-128 bad keys at 2^-193. That is a new hm96 instance (2175-bit key) and so a statement
     change, with about 8% more salt reads and Hankel work per leaf. SHA-512(sp‖y) stays at two compressions, and proof
     size doesn't move, because salts are never sent.
   - The free Markov trade at l = 1536: 2^-128 bad keys at δ₁ = 2^-129, which leaves 2·N·2^-129 ≈ 2^-106 per session.
4. **What a fresh key costs.**
   - Proof size: +256 bytes per session (the key, sent in `Commit`), against 1.09 MB per rep at 8090 L0.
   - Prove time: one 256-byte OS read and the key's Hankel rows, once per session. I haven't measured it, since this was
     reading only.
   - A statement change:
     - a new tag set, whose META `leaf_scheme.key` says "per session, the prover's OS bytes, in Commit", and a verifier
       that takes the key from the record;
     - every theorem that takes `hKey` restated first at the averaged key: `ZeroKnowledgeHidden`, `viewZ` and Lemma B,
       the FailClosed composed theorems (their simulation takes it) and `RecursiveZK`.
   - The in-circuit hidden-output rows (`hm96-sha512/row/v1`, META `row_key_sha512`) keep the pinned key and its premise.
     There the key is a circuit constant, so a per-session key would mean a per-session circuit.
5. **The total at the 8090 class.** m = 33, one table, codeword logs [21, 19, 17, 15, 13, 11] (`Accounting/Schedule.lean`):
   level 0's 2^21 leaves once, and levels 1 to 5 once per rep. So N_hid ≈ 2^21.74 Ligerito leaves, plus the small pads
   trees and τ's leaf.
   - Pinned key today: 2·N·2^-193 ≈ 2^-170 per session, plus a one-time 2^-64 bad-key event, which `hash-derived-key`
     assumes away.
   - Fresh key, averaged: about 2^-234 per session, with no bad-key event.
   - Fresh key, per-key form: 2^-64 per session at 2^-193, so Q·2^-64 over Q sessions. Only this form has a total to push
     toward 2^-128, and the averaged form makes it unnecessary.

