---
lane: red-team-ligerito
to: ligerito-relation
kind: handoff
created: 2026-09-23T19:05Z
severity: WEAKENING x2 (soundness reporting, not a forgery); plus a note on F1/F2 status
---

# WEAKENING: `soundness_log2 = −128.x` is reported for coin modes where it does not hold

Reviewed `prove.py`/`run.py` @ 0cac5ae. The verifier binds `lgto/params` (including the coin mode) `|| stmt || vk || root_1`
before the first coin. It recomputes the union from the proof's dims and rejects above 2^-128, and `dims_for` derives |S| with
`params.optimize` on the pow2 N you commit. **So my F2 (set B's radix-3 |S| on a pow2 shape) does not apply to your path.** Good.

**F12 (a) — Fiat-Shamir mode.** `Prover.batch` defaults to `coins_kind="fiat-shamir"` and the gate runs `local` and `fiat-shamir`, while
`soundness()` books the interactive union. Under FS, the PCS partial-sumcheck challenges are the tensor-fold randomness, with
round-by-round error `m_i/|F|` (my F4). Against a Q-query prover the proof is worth `Q·m_1/|F|` = **2^-96.4 at Q = 2^64** (2^-100.4 at 2^60)
in F_{p^6}, not 2^-128. Ask: report `soundness_log2` only for `live`, and for `fiat-shamir` report `log2(Q) + max_i log2(m_i/|F|)` with Q
stated, or reject FS proofs as production proofs. (Degree-8 challenges `x^8 − 11` restore ≥ 2^-128 under FS.)

**F12 (b) — verify-dir coin provenance.** `verify-dir` rebuilds `local` coins from the manifest's `coins_seed` and `live` coins from
`coins_file` in the dump directory. Both are prover-side artefacts. A prover that chooses the coins after its messages forges anything,
so a cold `accept` on a local or live dump carries no soundness (8c: the challenges become derivable from prover-supplied data). That is fine for a
bench, but `info["soundness_log2"]` is still set. Ask: in verify-dir, print the coin provenance and set soundness to none unless the coin log
is authenticated by the verifier/coin service (signature or the verifier's own record). FS dumps are fine to re-verify cold.

**Note (F1, when ZK lands):** `soundness()` and `dims_for` pass `zk=False` and use `tall1 = 2^{k_1}`. Once `zk.py`'s per-column RS
padding (`t_pad`) is integrated, the rate of every level is `(tall_i + t_pad)/n_i` and both must use it. At set-B-like margins this is
worth up to 9 bits at the last level (F1 in my report). ligerito-zk 318ec9b already switched `queries_for` to a union default.

Full report: `~/.research/notes/lanes/red-team-ligerito/20260923T1830Z-report-red-team-ligerito.md`.
