---
cursor:
  subagentId: "bc-b483c71e-c321-599b-b63b-e4cc0dccb710"
---

# To flock-zk (M1 lane), from zk-public: implement the keyed coin tree, `coin-tree/hm96-sha512/v2`

The coordinator chose the red team's fix for its auxiliary-input condition on the ZK proof: the prover sends a fresh nonce
in `Hello` that prefixes every coin-tree hash. This supersedes my 05:58Z note's "don't build it yet" for the nonce.

**The spec:** `docs/coin-tree-v2.md`, byte for byte. It includes test vectors, a Python reference built on core's hm96, and
a per-file list of what to change in `backends/flock/live` (its §8).
- **The nonce.** 32 bytes from the OS, drawn when `Hello` is built, carried in `Hello`'s `coins` object. The server's R7
  check then compares everything but the nonce byte for byte.
- **The hashes.** Every coin-tree SHA-512 input becomes `ν ‖ (v1's input)`, with v2 tags, including both hashes inside each
  hm96 leaf. `flock_merkle::hm96::leaf` can't be reused as is.
- **The answer.** The server answers `Hello` with 20 words: the root, then a fresh 256-byte hm96 key it draws for the
  session's tree. The prover refuses any other length, or a key with bit 2047 set.
- **Tests.** First a regression that today's v1 code reproduces the spec's `v1_root` from its tape: that confirms the reading
  of v1 the spec rests on. Then the v2 vectors, and the refusals.

**Where:** #229 (the proof now tracks it: `docs/zk-proof-public.md` §2.8 and §2.9, my line-by-line review, no findings beyond
§2.8's rows), or its successor.

**Status.** The spec and its Lean instance (#245) await the red team's statement review, so please don't merge before it
lands. The session key in the answer is my addition for soundness (the spec's opening section says why). **Update
(06:42Z): the coordinator decided to keep it, so build it as specified.** Daniel may reverse that in the morning, so it still
helps if the key is easy to drop.

**Also for #229, if the coordinator routes it to you:** the Rust side of the region-word check, in `Stmt::new`
(`docs/region-word-check.md`). The verifier lane has the Lean side. And my 05:50Z note still stands: the GPU run of
`gpu_proofs_match_cpu` is what lets the theorem cover the device prover.
