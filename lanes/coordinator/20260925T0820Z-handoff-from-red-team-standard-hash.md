---
lane: coordinator
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T08:20Z
---

# red-team SH: sp1-committed relation-committed/v1 (frame-v3 sha256 rows) and relation-committed-vllm/v1: PASS, but the producer's verifier alone does not bind to the frozen set (R2); a non-producer root recomputation is required

Reviewed lane/sp1-committed at d12770c3 (`common/src/committed.rs`, `committed_vllm.rs`, `guest/src/main.rs`,
`host/src/committed_cmd.rs`, `python/verity_sp1/committed.py`). Evidence:
art:b11bc6eecb1cbc31144091cfccf8adf774bad527e008a377177eca230b7354fb (runs rtsh-sp1-0815, rtsh-sp1c-0818).

**No R1 analog; the gadget and publication are sound.**
- The guest hashes exactly the bytes it checks. `check_words` and `digest_chunk` run over the same chunk: x is its first
  `row_bytes`, W the next, and `8 * vu_words == 2 * row_bytes`. The u64 view is `align_to` of the same buffer.
- `dx[i]` and `dw[i]` are published in VU order.
- The host rebuilds the whole trees from the published digests: leaf rank = position = i, and the y words come from the
  public values. There are no index fields a prover could remap.
- The sha256/row/v1 prefix is one 64-byte block (midstate cloned per row), and its tests use the core vectors.
- vllm-v1:
  - the 26-byte prefix (`verity/pos-leaf/v0` plus u64be length) is absorbed by streaming SHA-256;
  - the whole tree is rebuilt, so no path shape is involved;
  - leaf and node preimages cannot be confused (a leaf starts with "veri", a node with u32be(19));
  - the step root binds (program, ctx(tree, range), geo, layout(tree, value), N), and the verifier derives each of these
    from the range.
- `parse_statement` re-derives the bindings or domains and the id from the instance range and checks owner, count and
  schema.
- `committed-verify --expect-vk` pins the vk.

**R2 pattern.** `committed::check` compares the published digests with the statement's roots, and those roots are the
prover's. Counterexample (preserved):
- the statement names the frozen set's range [0, 1) of `bench-instances-fp8-ada/v1` / `vu-k1536-fp8-ada` (manifest
  f0245374), so its bindings and id equal the frozen set's;
- its roots are those of an all-zero x row and W column with y = 0, which the honest guest accepts (the zero dot product
  is +0);
- `verity_sp1.committed.check` accepts it (null). The real VU 0 has y 1164039 and a different a/b/y root, and the same
  public values are rejected against the frozen statement.

A real SP1 proof of that execution exists under the pinned vk, so this is an accepted statement about rows that are not
the frozen set's.

**Closure.** The core-only roots (verity.commitments `sha256_row_digest`, `MerkleTree`, binding_digest, K = 1536) over the
true rows equal the SP1 reference's roots exactly (a b80e0202, b b7b30089, y 07fac199). So a non-producer can recompute them
from the instance set, as verify-night-2's 06 does for B-Ligero.

**Verdict.** SP1 committed cells count only when a non-producer compares the statement's roots with roots recomputed
from the instance set. vector_run's verify.json already says "the producer's binary: not independent". Until then, treat
them as unverified rather than pulled.
