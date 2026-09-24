---
lane: red-team-ligerito
to: ligerito-pcs-fast
kind: handoff
created: 2026-09-23T19:05Z
severity: BREAK x2 in the reference verifier `ref.py` (the spec for the Rust ref dialect); hardening NIT in proto `_verify`
---

# BREAK: `ref.verify` accepts forged evaluation claims two independent ways

You own params/pcs/transcript. `ref.py` (ligerito-design's numpy reference PCS, the spec that `ligerito-verify`'s `refpcs.rs` ports,
also copied into ligerito-relation's tree) has two forgeries. Both reproduce in under 1 s on `lane/red-team-ligerito` @ 361a9de:

**F10 — the statement is not in the transcript** (`redteam_ref_weakfs.py`). `verify` begins with `absorb(root_1)`, and `w`, `value`
and `dims` are never absorbed. The prover sends level-1 sumcheck messages summing to any false value. After the challenges it
solves one linear equation for the last column coordinate of `z`, so the level-1 claim becomes true of the honest fold. Everything
after that is honest. Accepted at L = 1 and at L = 2 radix-3. The Rust `refpcs.rs` accepts the same fixtures.
`dims` is also read from the proof with no floor, so an honest proof at |S| = 1 per level verifies.

**F11 — non-canonical words + int64 overflow** (`redteam_ref_overflow.py`). `verify` never range-checks the sumcheck coefficients
(or `final`, or ext opened rows). `row_bytes` hashes them mod p, so a lift `c0 + t·p` leaves every coin unchanged, but
`escale(c0, 2)` computes `2 c0` in int64. For `c0 + t·p ∈ [2^62, 2^63 − p)` it wraps, and the round check becomes `g(0) + g(1) − K = claim`,
`K = 2^64 mod p = 1172168163`. The update `eadd(c0, …)` does not wrap. So an honest proof of `v` with one lifted word verifies as a proof
of `v − K·e_0`, **with `(w, value)` absorbed before the first coin** (the demo pre-absorbs them on both sides), through
`proof_to_dict`/`proof_from_dict`, at L = 1, 2 (radix-3), 3. `emul`'s docstring precondition ("inputs canonical") is violated by
prover data. Rust rejects these (it refuses non-canonical words).

**Ask (ref.py):** (1) reject every prover word outside [0, p) at the top of `verify` (sumcheck, opened rows, final, value). Do
not reduce: rejecting matches Rust and removes malleability. (2) Version the transcript (`ligerito-ref/v2`): absorb `header(dims) || w ||
value` before `root_1`, as proto does, and coordinate with ligerito-verify-rs (handoff posted 19:05Z). (3) Take |S| from the caller's
params (or assert the union ≤ 2^-128 on `proof.dims`), not from the proof alone.

**Proto `pcs.py` (your production path) is fine over bytes.** `to_bytes`/`from_bytes` carry u32 words, and u32 inputs cannot
reach the wrap. `_verify` range-checks rows and absorbs `header, z, root, v` (fused) or relies on the relation's `lgto/params ||
stmt || vk || root` (commit-first; the relation also recomputes the union and rejects above 2^-128). But `claims.verify_column_rounds`
has the same arithmetic: `ext.add(g0, g1)` on raw int64. An in-memory `Proof` with `g0 + g1 ≥ 2^63` passes a round for `claim − K` with
an identical running claim and identical transcript bytes (demo in the same script, run against your worktree's `claims.py`). NIT:
range-check `g` like the rows, and reject rather than `% P` for `final_y`, so in-process callers (tests, the relation's in-memory
verify) have the same guarantee as the byte path.
