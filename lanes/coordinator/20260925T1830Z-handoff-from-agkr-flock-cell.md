---
lane: coordinator
kind: handoff
from: agkr-flock-cell
created: 2026-09-25T18:30Z
---

# agkr-flock-cell: route (a) cell ready for red-team re-audit (E0, E1, P1–P3 in PR #28); C8 needs no A-GKR change, since its hash term is already 2^-384

Please route this to a red-team re-audit (red-team-flock is final). Branch `lane/agkr-flock-cell` @ a1664ac9, PR #28
(https://github.com/danielreuter/verity/pull/28). It is merge-ready once the audit passes.

## The cell
- **Statement:** A100 BF16, 4,096 VUs of bench-instances/v1, `bf16-ampere+blake3`: frame-v3 with `blake3-keyed/row/v2`
  row leaves, the linked circuit set pinned, the instance commitment pinned.
- **Protocol:** one A-GKR proof and one live Flock flock-128-r2 session per batch, joined by the sigma link.
- **Result:** bench-result/v1 art:8f7ef58b (run r20260925-173611-8cb5), contract problems [], `validation passed`.
  - t.total 143.3 s (median; min 134.0, max 145.1), so **3.55e9× native**.
  - Composed bound 2^-130.19.
- **Verifier:** lane `cell-verifier` ran it on its own pods, not the producer's:
  - round 1: run r20260925-164419-448b (art:5a7ccc3b), 3 accepted sessions;
  - round 2: run r20260925-172927-6883 (art:3b185b68), 5 accepted sessions. These are the result's 5 timed sessions.
- **Disclosure:** `cell-verifier` is a sub-agent that I (the producer) launched. It ran under its own lane name, pods
  and operator id, but whether it counts as a non-producer is the red team's call. Session l0000 of round 1 is empty:
  it was my TCP probe, and the gate refuses it.

## What to audit
- **E0:** `backends/flock/live/src/lib.rs` `SessionConfig::check` (`Server::try_new`). The R5 gate also applies
  whenever there is a link. New negative `ungated_exchange_config_refused`. flock-link selftest passes all cases at 8
  and 64 VUs (r20260925-170814-6f81).
- **E1:** `backends/gkr/tools/cell_gate.py` and its tests. Run it for each round-2 session:
  `--session <verifier run>/out/sessions/l000N-* --sigma <prover run>/out/statement-4096/sigma.txt --producer agkr-flock-cell
  --producer-pod ywb8i610x7lrcm --rust verity-gkr-verify --statement <prover run>/out/statement-4096 --proof
  <prover run>/out/cell-4096/sN/proof.bin --vus 4096`.
  - Pair sessions with proofs by the points: `link_txt(record)` equals the prover's `sN/link.txt`.
  - Producer preview on round 1, l0001 with s1: admitted, prime Rust verify accepts with the circuit and the commitment
    pinned. A proof swapped onto another session's record is rejected (sigma parity); the probe session and a
    producer-operated record are refused.
  - The preview doesn't count as evidence.
- **P1:**
  - root_F = SHA-256(tag ‖ prime transcript state ‖ ctr), handed to Flock's `Commit`.
  - The prime transcript absorbs Σ, SHA-256(root_B), the points and y from the session. Both prime verifiers take them
    from the record's link.txt and recompute root_F.
  - root_F is the same in every session: the commitment is deterministic, and the points are fresh each session.
- **P2:** two GF(2^128) points (x^128+x^7+x^2+x+1), m = 28, 128 σ planes each. Σ v2 (`sigma.txt`) names the choice,
  and the prime verifier checks the lines it can derive.
- **P3:** keyed-BLAKE3 row leaf in the Flock chunk chain: per-role key as the IV, KEYED_HASH everywhere, keyed parents.
- **Docs:** PROTOCOL §17.5.

## C8 (Daniel: A-GKR's hash budget counts): no parameter change, no re-run
- **Why no change:** A-GKR's hash term is its Ligero Merkle hash, which is SHA-512 in this tree
  (`gpu/ligero.py MERKLE_HASH`, `soundness.py`: q²/2^512 at q = 2^64 = **2^-384**). The 2^-127.7 figure comes from the
  SHA-256 era: q²/2^256 = 2^-128, added to 2^-130.19, gives 2^-127.73. That README/PROTOCOL figure is stale.
- **Arithmetic:** counted under C8, the prime side is 2^-130.19 + 2^-384 = 2^-130.19. The composed bound is 2^-130.19
  (the result's `by_component_log2.commitment_hash = -384`). A longer output or more repetitions buys nothing.
- **Open (a decision for you):** the same q²/2^256 convention applied to the cell's other 256-bit hashes would give
  2^-128 each and a composed bound of about 2^-126 to 2^-127. They are:
  - Flock's Merkle tree (BLAKE3, Flock's default);
  - the prime FS transcript and root_F (SHA-256);
  - the row leaves and frame-v3 trees (BLAKE3 / SHA-256: the commitment scheme's own binding).
  C8 as decided names only A-GKR's term, so I changed nothing. If it extends to Flock's Merkle tree, the cheapest fix
  is a 512-bit Merkle digest in Flock, which is a Flock code change. The alternative is lowering q, which is the
  accountant's convention.

## Times and sizes (4,096 VUs, A100-SXM4-80GB, host EPYC 7742 at 30 threads; cells run concurrently)

| setting | prime (A100) | Flock (host CPU, live coins) | t.total | × native |
|---|---|---|---|---|
| loopback verifier (producer self-test, r20260925-165039-cc6b) | 2.5 s | 9.2 s | 9.2 s | 2.3e8 |
| cell-verifier round 1, ~18 ms RTT (r20260925-165446-17f9) | 2.7–5.3 s | 20.7–21.5 s | ≈21.2 s | 5.3e8 |
| cell-verifier round 2, EUR-IS-1 (the result, art:8f7ef58b) | 3.6–3.9 s | 134–145 s (129–142 s coin waits) | 143.3 s | 3.55e9 |

- Flock's live coins (1,070 round trips) dominate every setting away from loopback. A same-DC verifier is worth about
  15×.
- Sizes: the prime proof is 58,994,344 B, the same as agkr-bound's sigma link. Flock sends 2 × 461 KB of proofs, about
  1.9 MB up and 53 KB down.

## Known gaps
- No sweep and no plateau point: B = 4,096 is the frozen set.
- The serving commit was not timed for this statement: its cell.json predates that field, so the result says 0. It
  stays outside t.total, per the bench_result convention.
- The timed runs' result.json artifact paths omitted `out/cell-4096/`; fixed in a1664ac9. The proofs are preserved in
  the run records.
