---
cursor:
  subagentId: "bc-6d082f2c-9c48-534c-9ae6-46bf3724b4a7"
---

lane: coordinator · kind: handoff · from: red-team-hm96 · created: 2026-09-26T22:56Z · status: final · repo: danielreuter/verity ·
origin: PR #93 @ cd00f704 (base main@a53900df)

# red-team-hm96: PR #93 (E4, SHA-512 commitments) @ cd00f704 is GRANTED WITH CONDITIONS; merge after C1 (two "Hashes" sentences), and Daniel decides C2

**Verdict: GRANT WITH CONDITIONS.** Each part holds on its own terms:
- **`hm96-sha512/v1`:** statistically hiding at the same bound as `hm96-sha256/v1`, and binding from SHA-512 collision resistance
  alone.
- **The derived key:** transparent, and it meets finding 6 of #88: §5 now states that the key is the statement's, never a witness.
- **Domain separation between the SHA-256 and SHA-512 schemes** holds in every cross-check I ran.
- **SHA-256 defaults:** every one stays byte-identical, and #88's C1 fail-closed rule still holds.

The one real gap: the two SHA-512 framings still rest on SHA-256, through the identity and domain digests. The specs' "Hashes"
sentences say otherwise.

- **C1, before merge (doc):** fix finding 1's two sentences in `frame_v3/PROTOCOL.md` §6 and `vllm_v1/PROTOCOL.md` §10.
- **C2, a decision for Daniel before the re-baseline cites these schemes in Table 1.** Either:
  - extend E4 to the identity and domain digests; or
  - cite `cr/sha-256` beside `cr/sha-512` in those Table 1 rows.

## Findings

1. **F1: the SHA-512 framings still rest on SHA-256 for which statement and which positions. Low, open; a decision for Daniel.**
   - **frame-v3-sha512.** Its domain id absorbs `binding` and the positions' identity digest, and both are 32-byte SHA-256 identity
     digests.
   - **vllm-v1-sha512.** Its root bindings take program, ctx, geo, layout, template and names, which are SHA-256 digests from the
     integration. `domain_digest`, which the scheme computes itself, is still a tagged SHA-256 (the vectors' openings carry 32-byte
     domain digests).
   - **What rests on what:**
     - binding a value inside a verifier-held domain rests on `cr/sha-512` alone;
     - substituting across sessions or contexts would also take a SHA-256 collision on those digests. So "which statement, which
       positions" keeps SHA-256's collision margin.
   - **What the specs say.** vllm-v1 §10 discloses that identities stay SHA-256. But both specs' Hashes lines say Table 1 lists
     `cr/sha-512` "for everything the scheme computes", `hashes` is `("sha512",)`, and `domain_digest` contradicts that sentence.
   - **Fix:** name the SHA-256 identity and domain digests in both Hashes lines (C1). Then Daniel chooses between the two options in
     C2.
2. **F2: `validate_commitment` no longer rejects a root of the other width. Info.**
   - `merkle.Commitment` and `Opening` now accept 32- or 64-byte digests for any domain.
   - The only width check against the domain is in `verify_opening`, which is also the only caller I found, so this fails closed
     today.
   - Fix: one line in `validate_commitment`, `len(root) == domain.digest_bytes`, keeps the public helper fail-closed for future
     callers.
   - `verify_multiproof` defaults to `hash="sha256"`. That also fails closed: a SHA-512 proof under the default is rejected
     (tested).
3. **F3: claims wording. Info.**
   - The `common-reference-string` entry still names only `hm96-sha256/v1`'s pinned key.
   - `hash-derived-key` says the key "is a typical draw of its family". It should name the event: the derived key is not in the
     2^-64 fraction of keys for which the pinned-key bound fails.
4. **F4: no frame-v3 schema string for hiding rows. Info.** frame-v3 §6 says "a hiding row wraps this digest in `hm96-sha512/v1`",
   but it doesn't name the schema the frame leaf binds for an hm96 leaf. Name one, for example `hm96-sha512/row/v1`, before a
   backend commits hiding rows in frame-v3. Binding isn't at risk, since the preimage tags differ; the statement just isn't
   explicit about which rule produced the 64 bytes.
5. **F5: at the re-baseline, the committer's salt sizes are SHA-256's. Info.** `LeafSchemeRule` uses the module constant
   `SALT_BYTES = 128` in `_unsalted`, `_salts_of` and `_leaf_rule`. Wiring hm96-sha512 in as it stands fails closed on sizes, not
   open, but those checks must take the instance's salt size.

## What holds

- **Hiding bound, as instantiated at SHA-512.** The parameters are n = 512 bits and l = 1,536 (192 bytes), with a 2,047-bit key
  (256 bytes, top bit zero). From these:
  - per leaf against the ideal: ½·√(2^(512 − 1024)) = 2^-257;
  - N leaves: N·2^-256 under a uniform key;
  - under the pinned key: N·2^-192 outside a 2^-64 fraction of keys, so 2^-128 at N = 2^64.

  N counts every leaf ever committed under the one pinned key. The rank of M is 512 for both the pinned and the "other" key, and
  the family is universal: rank 512 for adversarial nonzero d.
- **Key derivation.** The key is SHA-512(label ‖ u32be i) for i < 4, bit 2047 cleared, and it re-derives exactly.
  - Binding doesn't use the derived key at all.
  - The witness-key equivocation still works for SHA-512 (512 equations in 2,047 unknowns), which is exactly why §5 now forbids a
    witness key. The leaf's key digest defeats it wherever the verifier recomputes the leaf.
  - `hash-derived-key` is scoped correctly: one event of probability at most 2^-64 under a uniform key, and implied by the random
    oracle model while far weaker.
- **Binding.** The three-case reduction to `cr/sha-512` holds for any key. Length extension is refused on the inner digest, the salt
  digest and the leaf (pure-Python SHA-512 forgeries). A salt shifted by a vector in the kernel of M keeps b and is rejected through
  c.
- **Domain separation between SHA-256 and SHA-512.**
  - hm96's tags, labels and sizes differ, and the scheme digests are 64 and 32 bytes.
  - `Hm96` and `HidingLayout` refuse an instance whose hash differs from its base's or inner layout's.
  - `FrameV3` and `VllmV1` refuse mixed hashes, and a SHA-512 frame refuses SHA-256 and BLAKE3 rows (and the reverse).
  - The framings reuse their tags under the new hash. Every verifier fixes the hash from its own domain and checks digest widths,
    and vllm-v1's domain digest adds `"hash": "sha512"`.
  - Rejected by the negatives (64, all as expected): cross-hash openings in both directions, digests truncated from 64 to 32 bytes,
    doctored siblings, wrong-hash multiproofs, and another binding. hm96's leaf preimage starts `verity/h`, which keeps §5's
    first-byte separation.
- **Fail-closed.**
  - #88's C1 holds on head: `commit_block_offline` under hm96 raises at the context digest, and `NativeCollectCommitter(hm96)` is
    refused at construction (CPU torch probe).
  - The committer refuses `hm96-sha512/v1`.
  - The SHA-512 batch path refuses 32-byte digests and 128-byte salts.
- **Vectors.** I recomputed all three new files from the spec text (`recompute_sha512.py`, 241 checks, no verity import):
  - `hm96-sha512`: key, prefixes, scheme digest, row weights and XOR count (400,193), masks by matrix product and by bit loops,
    leaves over both inner layouts, and trees with SHA-512 step bindings over 32-byte identity inputs;
  - `vllm-v1-sha512`: H, the position, chunk and thread leaves with headers built from the fields, trees and paths, all six root
    bindings including the SHA-512 stream and thread contexts, and each opening's domain digest and accept flag;
  - `frame-v3-sha512`: row prefixes and digests, domain ids from binding, owner and range identity, word leaves, pads, nodes,
    roots, paths and the empty root.
- **The SHA-256 side is unchanged.**
  - No existing vector file changed, and all five generators pass `--check`.
  - #88's recomputation passes on head (128/128).
  - The vLLM default path is byte-identical between base a53900df and head in 6 configurations.
  - #88's attack battery passes on head (359/359).
  - Head and base suites match, with only the PR's added tests on top: core 1,112 vs 1,052, root 29 vs 28, vLLM commit 308 vs 307;
    flock, numerical bench and reference, and hash_gpu are the same. gkr's collection error on both is the missing torch, and gkr
    passes on head with CPU torch (61).

## Evidence

- **Artifact:** `art:29dc2ccbbe75c4e9bc43caa720e1636795e2ed34f81b0d1915e2572be4f7cf95` (redteam-findings/v1, target
  `art:b9bb217f`), preserved.
- **Scripts:** `lanes/red-team-hm96/evidence/`: `recompute_sha512.py`, `negatives_sha512.py` and `failclosed.py`, beside #88's
  scripts.
- **Labels:** `finding` by red-team-hm96 on `r20260926-221723-71aa`, `r20260926-221754-0cce`, `art:b9bb217f` and `art:a7a8ccce`,
  all with ref `art:29dc2ccb`.
- **Cost:** CPU only, $0.
