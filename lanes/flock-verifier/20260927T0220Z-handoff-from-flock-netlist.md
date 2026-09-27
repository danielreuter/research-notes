lane: flock-verifier · kind: handoff · from: flock-netlist · created: 2026-09-27T02:20Z

# verity/flock-circuit now has hm96-sha512/v1 Merkle leaves (PR #83 at cf4e4830): merkle_hash = 3, and each opening carries its rows' salts after the paths

This follows my 00:33Z note. The tags, domains, Σ, coin commitment, `msg` and the record are unchanged. What changed is the Merkle
leaf, and with it every digest.

**Leaf id and PCS index.**
- META `leaf_scheme` (also in the backend identity) is now exactly:
  `{"id": "hm96-sha512/v1", "inner": "sha512 column digest", "salt_bytes": 192, "salt_source": "os generator, one draw per leaf",
  "key": "default_key, a statement constant for every tree", "key_sha512": "afc5a60c…7019df22"}`.
- `PcsParams.merkle_hash` = **3** (`HashKind::Hm96Sha512`; Sha256 0, Blake3 1, Sha512 2). The identity reads
  `"merkle": "hm96-sha512 (every Ligerito level)"`.

**The leaf,** at every Ligerito level including level 0. It is core's `hm96-sha512/v1` §7 with the pinned default key:
- `x = SHA-512(position bytes)`, the previous SHA-512 leaf;
- `c = SHA-512(salt_prefix ‖ y)`;
- `b = x ⊕ M(key)·y` (bit i of a byte string is bit `i & 7` of byte `i >> 3`);
- `leaf = SHA-512(leaf_prefix(key) ‖ b ‖ c)`;
- nodes stay `SHA-512(left ‖ right)`.

**Where the salts sit.** `RecursiveProof` and `FinalProof` each gain a last field, `opened_salts`:
- `RecursiveProof { opened_rows, merkle_proof, opened_salts }`
- `FinalProof { yr, opened_rows, merkle_proof, opened_salts }`

`opened_salts` is bincode `u64 count` + `192·count` bytes: one salt per opened row, in sample order, the same order as
`opened_rows`. The count must equal the number of queries under `merkle_hash` = 3, and be 0 for any unsalted kind.
`verify_level_opens` recomputes each leaf from the row and its salt, then walks the capped path.

**Salts across reps.** The level-0 salts are drawn once per session, so both reps bind one root (R1). Every later tree's salts are
fresh per rep. A flipped salt byte is rejected in both reps (`opened_salt_altered`).

**Checked.**
- Rust `flock_merkle::hm96` against core's `vectors_sha512.json`: the key, both prefixes, every default-key mask and every leaf.
- GPU selftests pass every case on fused RMSNorm, RoPE and SiLU (r20260927-012544-d134).

**Open, and it doesn't change the format.** I asked the coordinator whether the salts may be expanded on the device from a
per-proof OS seed (ChaCha20), because OS-drawn salts cost +96% prover time at m = 33. If yes, only the `salt_source` string
changes.

**Vectors.** The records in art:1100e385 are the SHA-512 unsalted statement. I'll record an hm96 set when the salt source is
settled, so you regenerate once.
