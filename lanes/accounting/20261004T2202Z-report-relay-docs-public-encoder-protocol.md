---
id: 20261004T2202Z-report-relay-docs-public-encoder-protocol
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/public-encoder/protocol.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/public-encoder/protocol.md`, sha256 `cb7787091cb648734853e0d7dd1074e7ab807ebeb0389dce297c686197fd9916`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Public encoder, milestone 1: setup protocol (the exact check)

Spec for the reference implementation (`code/pous-ref`, Verity `protocols/pous`), 28 Sep 2026. Status: **ready for implementation.**
- The red team reviewed the Lean statement as named statement reviewer (review §38, GO).
- The statement is proved in `lean/submissions/public-encoder/` (`NOTES.md`, `AXIOMS.txt`).

Background is in the [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/public-encoder/problem-statement.md) §5. The server encodes. The verifier decodes the server's codeword, checks the result against the commitment to W, and builds vk from the bytes it decoded. It never runs the encoder, and it never holds W.

## What changes

Only setup step 3 of `PROTOCOL.md`'s lifecycle changes. Commit, salt, serve and audit are unchanged.

| | Today (`setup.verifier_key`) | Milestone 1 |
|---|---|---|
| Verifier input | W, com_W, salt | com_W, salt, the server's blocks C* |
| Verifier computes | its own Enc(W, salt), then vk | Dec(C*), then commit(Dec(C*)) = com_W, then vk from C* |
| Verifier cost per 32 MiB segment | 131,328 dependent Π₂ calls | the same 131,328 calls, but only 512 deep |
| Acceptance | always; `check_server_root` is optional | only if the recomputed commitment equals com_W |

## Messages

1. **Server → verifier: com_W = `setup.commit(params, W)`.** Unchanged. The verifier then fixes `params` and the manifest itself.
2. **Verifier: salt = `setup.draw_salt(source, com_W)`,** drawn only after com_W is received. Unchanged.
3. **Server → verifier: C*.** Segments s = 0, …, N − 1, in order; each is `blocks_per_segment` blocks of `block_bytes` bytes.
4. **Verifier, for each segment s:**
   - check the segment's size and block count against its own `params`, and reject otherwise;
   - compute `W′_s = params.codec.decode_segment(params, prims, salt, s, C*_s)`;
   - feed `W′_s` into the running commitment hash, byte for byte as `setup.commit` frames it: the tagged-SHA-256 header, then the lengths and the verifier's own manifest, then the segments in order;
   - keep `verifier.segment_leaves(params, salt, s, C*_s)`, and discard `W′_s`.
5. **Verifier, after the last segment:** accept iff the digest equals com_W.
   - On acceptance, vk = `VerifierKey.from_leaves(params, salt, leaves)`, over the leaves of exactly the decoded bytes.
   - On rejection, there is no vk and no audit.
6. **Audits** run against vk, as today.

## Rules

Each rule is followed by the reason it holds.

- **The verifier calls no encoder.** The Lean check `exactCheck` is `dec pp C* = W` and nothing else.
- **vk comes only from the bytes the verifier decoded.** Never take a root, a leaf digest or a manifest from the server. The Lean audit checks answers against the same C* the check read.
- **All-or-nothing:** one mismatch, in any byte, block count or segment count, rejects all of setup. Milestone 1 is exact soundness, φ = 0.
- **Salt after commitment.** If W could depend on the salt, W := Dec(salt, 0) would make C* = 0. Lean fixes W before the primitive.
- **Commitment framing identical to `setup.commit`.** A second framing would be a second, unreviewed binding assumption.
- **Stream per segment.** The verifier holds one segment's blocks, its leaves and the hash state, never W. Rows within a segment decode in parallel.
- **Codecs.** The interface is codec-generic, but the Lean covers only the dense codec (`chainDense`, the secure-first default). P3 is also a bijection, but its encode-after-decode lemma is not proved.

## Assumptions and cost

- **Assumptions.** None new. SHA-256 collision resistance binds com_W, as the salt order already requires. The ideal-permutation heuristic for Π₂ is unchanged.
- **What Lean proves** (`lean/submissions/public-encoder/`, three standard axioms, `leanchecker --fresh`):
  - Acceptance forces C* = Enc(W, salt) (`chainDense_encDec`).
  - The public game with this check is equivalent to today's (`pubAuditSecure_exact_iff`), so today's certificates apply unchanged at k = 111: `dense_pub_meets_64`, `seg_pub_meets_14` and `chain_pub_meets_64`.
  - The chain instance, like today's `chain_meets_64`, is conditional on `ChainExPostFacto`.
  - An accept-all check provably fails the game (`acceptAll_fails_dense`). So the implementation's check is load-bearing, and test 3 below is the case it must reject.
- **Cost** is one full decode per setup: 131,328 Π₂ calls per segment, 512 deep.
  - On an L40S, 2.7 s per segment at the measured codec rate: 80 s for Qwen2.5-0.5B, about 20 min for 14 GB.
  - On one CPU core, 5.2 min per segment.

## API and tests

~~~python
def verifier_key_from_encoding(params, prims, commitment: bytes, salt: bytes,
                               encoded: Iterable[Sequence[bytes]], codec=None) -> VerifierKey:
    """Milestone 1: decode each segment of the server's C*, check commit(Dec(C*)) == commitment, and return vk built
    from the decoded blocks. Raises ValueError on any mismatch; never calls an encoder."""
~~~

Keep `verifier_key` (the verifier encodes) as the reference path in tests. Tests:

1. **Honest.** Accepted, and the root equals `verifier_key`'s on the same W and salt.
2. **One flipped byte** in any block of any segment: rejected.
3. **Corrupt and continue.** Set block j to zeros, encode the later blocks honestly on top of it, and send the result: rejected. It decodes to W′ ≠ W at block j only; this is the distance the problem statement uses.
4. **Wrong sizes.** A missing or extra block, a missing or extra segment, or a wrong block size: rejected.
5. **Server data unused.** A server-supplied root or leaf list is never read; the root comes from the decoded bytes.
6. **No encoder.** Monkeypatch the codec's `encode_segment` to raise; the verifier path still succeeds.
7. **Known-answer vectors.** The decode matches `tests/fixtures/lean_dense_vectors.json`.
