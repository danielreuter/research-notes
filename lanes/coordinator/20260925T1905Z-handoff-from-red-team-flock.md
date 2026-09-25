---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T19:05Z
---

# red-team-flock fourth audit: the route (a) cell art:8f7ef58b is GRANTED WITH CONDITIONS at proof_class NON_ZK_PROOF_DIAGNOSTIC, not the NON_ZK_PROOF it claims. The prime (A-GKR) half ran on runner-derived Fiat–Shamir coins. The bound is 2^-130.19 at the current hash convention. cell-verifier is not a non-producer.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "Fourth audit". No pods were used.

I re-ran the E1 gate myself from the store, with my own build of `verity-gkr-verify` (c95dd13a) and the records (art:3b185b68) paired with the prover's proofs (art:9464fe7a). All 5 sessions were admitted, and the prime proof was accepted in each (circuit and commitment pinned). All 5 negatives were rejected:
- a cross-paired proof (sigma parity);
- an edited sigma.txt;
- an edited commitment.txt;
- an edited y in the record;
- the operator given as a producer.

## Verdicts
- **E0: HOLDS.** `SessionConfig::check` / `try_new` refuse `link: Some` with `require_link: false`, and the R5 gate applies whenever a link exists. The verifier's build (a83d7de7) has the same `backends/flock` as the tip.
- **E1: HOLDS, with two gaps.**
  - The gate checks the exchange, gated, Σ, verdict, context, preserved-proof and prime checks. But it trusts the record's Flock verdict, and the Flock side can't be replayed offline: the record keeps only `publics_sha256`, not the committed chunk words. Keep them in the record.
  - `non_producer` compares a self-declared `verifier.json` operator against a producer list the caller supplies. `runpod_pod_id` is null, so the pod check is vacuous.
- **P1: HOLDS.**
  - root_F = SHA-256(tag ‖ transcript state), binding the Ligero root and the GKR messages, is handed to Commit before the points.
  - The prime transcript absorbs Σ, root_B, the points and y from the record, and the Rust verifier recomputes root_F against it.
  - The pairing is by construction, and a cross-pair is rejected.
- **P2: HOLDS.** Two GF(2^128) points, m = 28, 128 planes each; Σ v2 names the choice.
- **P3: HOLDS.** Keyed-BLAKE3 row leaves (key IV, KEYED_HASH, keyed parents). Σ ties the Flock verifier's digests to the prime statement's pinned public digests.
- **L1–L4 and F1–F3:** met on the CPU path, except F1's non-producer part. The shipped exchange order, both-rep link claims and chunk chain are unchanged from the third audit.
- **Non-producer: NO.** cell-verifier was launched and instructed by the producer, so it is the producer's principal chain.
  - It is adequate as the protocol's live verifier: a separate pod, OS coins, custody of its records under its own attempts, and the audited build.
  - It is not TABLES criterion 6 independence. My store re-run is a non-producer re-check of the prime proofs and the record fields, but not of the Flock verdict.
  - A verify lane should label `verified` after an offline Flock replay exists. By the contract I don't write `verified`.
- **Class: DOWNGRADE to NON_ZK_PROOF_DIAGNOSTIC.**
  - A-GKR's own label rule (PROTOCOL §0) says: "Fiat-Shamir is what the CPU prover uses too (the interactive object ... not implemented); the diagnostic label stays NON_ZK_PROOF_DIAGNOSTIC". The cell's prime proof derives rho, the GKR challenges and the Ligero queries from its own SHA-256 transcript. No live verifier supplied them.
  - The cell's `mode: interactive` string covers Flock and the link points only.
  - NON_ZK_PROOF needs the prime coins from the live verifier: the same cell-verifier session could serve them.
- **Bound: 2^-130.19 holds at the current convention.** It is A-GKR's interactive-model bound: Ligero queries 2^-130.19, lookup 2^-158.6, batching 2^-164.2, sumcheck 2^-176.4, SHA-512 hash 2^-384, plus Flock 2^-195.5, the link reduction 2^-243.9 and Schwartz–Zippel 2^-246.4.

## Two dependencies for Daniel
1. **Hash convention.** If q²/2^256 counts for 256-bit hashes, several 2^-128 terms enter: Flock's BLAKE3 Merkle trees, the SHA-256 root_F/Σ binding, and the row/frame-v3 binding. The bound becomes about 2^-126.5 to 2^-127, and the cell drops below 2^-128.
2. **FS vs live for the prime half.** At the current convention, TABLES admits it as a footnoted "file re-verification replaying the runner's coins, not transferable". Under the campaign's ×2^60 Fiat–Shamir rule (B-Ligero §8c), the one I applied to Flock, the prime half is 2^-70.2. Consistency with flock-128-r2 argues for live prime coins.

## Conditions for the cell
- **G1:** the footnote says the prime coins were runner-derived (FS, not transferable), and Flock and the link were live. The class is NON_ZK_PROOF_DIAGNOSTIC.
- **G2:** the record keeps the committed public words, so the Flock verdict can be replayed offline, and an offline replay tool is added.
- **G3:** a non-producer verify lane re-runs the gate and replay from the store, then labels `verified`.

Labels written: `proof_class NON_ZK_PROOF_DIAGNOSTIC` and a `finding` on art:8f7ef58b, both by red-team-flock, with --ref pointing to this handoff.
