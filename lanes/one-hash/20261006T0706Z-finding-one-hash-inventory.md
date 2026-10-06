---
id: one-hash/20261006T0706Z-finding-one-hash-inventory
campaign: proof-service
lane: one-hash
kind: finding
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---
# One hash: what in core and C-Flock still commits with something other than SHA-512 in frame-v3-sha512

Daniel's ruling: one hash, SHA-512. Every commitment is hm96 rows in frame-v3-sha512 trees, and certificates use hash-based
signatures over SHA-512. This note is item P6's inventory, of `note:verity-root/20261006T0550Z-report-proof-service-implementation`,
taken against `origin/main` at `68e614869`. It has one row per hash use that isn't SHA-512 in frame-v3-sha512, with its file,
hash, readers, owner lane and fate. Fates:
- **move**: to SHA-512, frame-v3-sha512 or hm96-sha512 rows;
- **delete**;
- **keep**, with its reason;
- **blocked**, naming the lane it waits on.

## Round 3 updates (from proofs, 07:16Z)

- **Correction: C3 is up.** Compute-accounting's draft [#1311](https://github.com/danielreuter/verity/pull/1311)
  (`cursor/pouw-epoch-coins-e3fa`) deletes `crypto/beacon.py`, `crypto/bls12_381.py`, and PoUW's quicknet tests and vectors,
  so row A10 is done there. What's left is prose that names a beacon round as a possible source, and none of it reads beacon
  code: `verity.primitives.randomness`'s docstring and its `TypeError` text, PoUS's docs, and vLLM's legacy
  `commit/challenge.py`.
- **Correction: a changed Lean record needs no statement reviewer** (Daniel's 2026-10-03 ruling). Daniel gets a DM when it
  lands. Row C3 is updated.
- **Item 10.** Compute-accounting agrees with D3 and D5.
  - NCP's and Pearl FP8's SHA-256 is ours: `pouw/audit.py`'s default trees and NCP's permutation digest both move to SHA-512.
  - Pearl's keyed BLAKE3 is compute-accounting's strong-reason report, not this note's.
  - `-h3` moves wholly to SHA-512 under C1, and `-h1`/`-h2` leave the served path, so frame-b3/b3s retire after C1.
  - Proofs offered compute-accounting a one-hash PR, after the rename, that moves the default trees and the permutation
    digest. It waits for their acceptance.
- **Daniel's two questions** go into his morning report:
  - does one hash cover PRFs (D1, C7)?
  - may we drop re-verification of sessions recorded under the SHA-256 Lean tag sets (C3)?

  Until he rules, the PRFs and the tag sets stay.
- **Tonight's PRs**, one each, in order:
  1. delete `hm96-sha256/row/v1` (A5);
  2. 64-byte bindings under frame-v3-sha512 (the Binding plan's core part);
  3. the beacon prose, apart from PoUS's docs;
  4. the binding consumers' new tags, stacked on 2 (grant);
  5. Poseidon2 into the archive, if only archive code reads it.

  C-Flock's legacy deletion and `merkle.py`'s default flip go after 14:00Z (plan in the section after the Binding plan).

## What matters first

1. **C-Flock's SHA-256 trees belong to legacy statements, and no Lean reads them.** These are `ir_frame.py`, `ir_sampling.py`,
   `instances.py`, `negatives.py` and `backend.py`, and their Rust binaries: `flock-pure`, `flock-pure-gpu`, `flock-ir-frame`,
   `flock-ir-sampling`, `flock-ir-block` and `flock-vllm-v1`.
   - They write and check `verity/flock-ir-frame/v3`, `verity/flock-ir-sampling/v1`, `verity/flock-pure-block/v2` and the vLLM
     block statement.
   - In all of them, keyed-BLAKE3 rows sit under SHA-256 frame-v3 trees, with SHA-256 Σ and statement digests.
   - The verifier's `PROTOCOL.md` §16.3–16.4 calls them legacy-only. An `rg` for `irf`, `flock-ir-frame` and `flock-pure-block`
     under `backends/flock/verifier/lean/` finds nothing, so only the Rust binaries verify them.
   - Moving only their trees to frame-v3-sha512 would leave BLAKE3 rows and SHA-256 Σ: the statement would still break the
     ruling, and the verifier being changed is one M0 doesn't use. **Their fate is delete, not move** (C1 below).
   - M0 (`circuit.py`) reads two constants from `ir_frame`, `BINDING_TAG` and `OWNER`. They move into `circuit.py` with the
     binding change.
2. **frame-v3-sha512's 32-byte SHA-256 binding needs no new frame version.**
   - Only new versions of the four binding tags that feed it.
   - A 64-byte binding is accepted next to the 32-byte one. The domain message frames every part with its u64be length, so
     the two lengths can't collide.
   - The Lean verifier reads frame-v3 `domain_ids` from the public file as given and never recomputes them from `bindings`
     (`Public.lean` `fv3Bytes "domain_ids"`; `HmRow.lean` lines 1161, 1176, 1477). So Lean is unchanged.
   - The core part is small. The plan is in the Binding plan section, after the inventory.
3. **One schema has no reader and can go today.** It is `hm96-sha256/row/v1` (`rowleaf.SCHEMA_HM96_SHA256_ROW`). Its only
   references are its own assertion in `tests/test_sha512_framings.py` and one sentence in `frame_v3/PROTOCOL.md` §6. Its
   deletion is a core-only PR that needs no grant.
4. **`flock-circuit`'s SHA-256 branch is dead code.**
   - `live/Cargo.toml` builds `flock-circuit` with `required-features = ["sha512"]`.
   - So `#[cfg(not(feature = "sha512"))] const MERKLE: HashKind = HashKind::Sha256` in `bin/flock-circuit.rs` can't be built.
   - Neither can `circuit.rs`'s `flock-leaf/sha256-unsalted` branch, inside that binary.
   - Deleting both changes no behaviour, but it is under `backends/flock/` and needs a grant.
5. **Round 1's items:**
   - frame-b3/b3s waits on compute-accounting's -h1, -h2 and -h3, and tonight's served-zk window measures -h2 and -h3. They
     retire after C1;
   - beacon/BLS is deleted by C3's draft #1311 (Round 3 updates).
   - Multiproof no longer reads frame-b3/b3s: [PR #1307](https://github.com/danielreuter/verity/pull/1307),
     `cursor/one-hash-multiproof-sha-95d4` at `45835e06f`.

## A. Core commitments (`verity/primitives/commitments`, `verity/primitives/crypto`)

| # | where | hash | what it commits | readers | owner | fate |
|---|---|---|---|---|---|---|
| A1 | `merkle.py`: `CommitmentDomain.hash = "sha256"`, and the `_hash` and `domain_message` defaults | SHA-256 frame-v3 | every tree whose caller names no hash | Callers that rely on the default: C-Flock legacy (`ir_frame.py:252`, `ir_sampling.py:354`, `instances.py:158,263`, `negatives.py:46`); frozen archive (`archive/direct/ligero/{auth,vu,reverify}.py`, `archive/gkr/gpu/commit.py`); `frame_v3/vectors.py` (the SHA-256 vectors the SP1 kernel mirrors); `kernels/hash_gpu/tests/test_frame_v3.py`; core tests (`test_frame_v3`, `test_scheme`, `test_rowleaf_nvfp4`, `test_rowleaf_bits`, `test_poseidon2`); `experimental/tests/commitments/test_multiproof.py`. Callers that pass `hash="sha256"` through: `vllm_v1` (20 sites), `leaves.py` (7), PoUW `audit.py` (10), PoUS `setup.py` (3). | proofs | **move, after C1.** Flipping the default today would silently re-root C-Flock's legacy writers (a `backends/flock/` change) and the frozen archive. Once C1 deletes four of those readers, the PR pins `hash="sha256"` at each SHA-256 reader that remains (archive, the SP1 vector generator, `hash_gpu`'s test, frame tests) and makes `"sha512"` the default. The `__init__.py` and module docstrings that call SHA-256 the frame change in the same PR. |
| A2 | `merkle.py:208`, where `binding` must be 32 bytes; `frame_v3/PROTOCOL.md` §6 "What stays" | SHA-256 (tagged identity) inside frame-v3-sha512 domain ids | which statement, session, port and range a root belongs to | `circuit.py` `stage` (`verity/flock-ir-frame/binding/v1`); one-stage `registration.py` (`verity/one-stage/served-domain/v0`) and `registered.py` (`verity/one-stage/registered-domain/v0`); vLLM `commit/serving_rows.py` (`served-domain/v0`); `benchmarks/one_stage/a0.py` (`STAND_IN_BINDING`) | proofs (core, one-stage, C-Flock); vllm for `serving_rows` | **move**: see the Binding plan section |
| A3 | `identity.py`: `tagged_sha256`, `identity_digest` (`veritor/tagged-sha256/v1\0`), `validate_digest` (64 hex) | SHA-256 | the identities every binding and manifest uses | everything that binds through `identity_digest`; the SP1 kernel mirrors it (frozen) | proofs | **keep** while a SHA-256 frame reader exists. New code uses `identity_digest_sha512`. Delete it with the last SHA-256 reader. |
| A4 | SHA-256 vectors: `frame_v3/vectors.json`, `hm96/vectors.json` (`hm96-sha256/v1`), `vllm_v1/vectors.json` | SHA-256 | pinned conformance | `archive/sp1` (frozen), `archive/ligero-verify`, vLLM's production vectors test | proofs (frozen) | **keep**, as the frozen backends' pins; delete them with those backends. Each already has a `vectors_sha512.json` beside it. |
| A5 | `rowleaf.py` `hm96-sha256/row/v1` | SHA-256 hm96 | a hiding row's leaf under a SHA-256 frame | none (its own test only) | proofs | **deleted** on `cursor/one-hash-hm96-sha256-row-95d4` (one-hash PR 2) |
| A6 | `rowleaf.py` `sha256/row/v1`, `sha256/row-nvfp4/v1` | SHA-256 | row digests | C-Flock legacy (`instances.py`, `live/src/pure_block.rs`); `archive/gkr`, `archive/direct/ligero`, `archive/ligero-verify`; `benchmarks/commitments/{commit_cost,hiding_leaf_cost}.py`; `benchmarks/numerical` views and drilldown (labels); core tests | proofs | **delete** with C1 and the archive. Frozen readers keep them until then. |
| A7 | `rowleaf.py` `blake3-keyed/row/v2`, `blake3-keyed/row-nvfp4/v1` | keyed BLAKE3 | row digests | C-Flock legacy (`ir_frame`, `ir_sampling`, `instances`, `backend.py`); Lean `Blake3Row` (the pre-hm96 circuit tag sets, C3) | proofs | **delete** with C1 and C3 |
| A8 | `rowleaf.py` `poseidon2-babybear-w24/row/v2h` (`SCHEMA_ROW`), `poseidon2_babybear.py` | Poseidon2/BabyBear | B-Ligero row leaves | `archive/direct/ligero` and `archive/ligero-verify` (frozen); `tests/test_poseidon2.py`; `benchmarks/numerical` labels | proofs (frozen) | **move into `archive/direct/ligero/`**: it is frozen B-Ligero's, and `PROTOCOL.md` §5 keeps it only so recorded results verify. A small PR. |
| A9 | `merkle.py` frame-b3 and frame-b3s (`blake3_*`, `b3s_*`), `scheme.py` `HASH_CLASS`/`DIGEST_BYTES`, `crypto/blake3.py` | BLAKE3, BLAKE3-s256 | PoUW trees | PoUW `serving.py` `HASH_FORMATS` h1, h2 and h3; `pearl_c.py` `TREE_HASH`; the vLLM device path (`protocol_options/pouw_pearl_c_device.py`); `benchmarks/pouw` | compute-accounting | **delete, after C1**: -h3 moves wholly to SHA-512 under C1, and -h1/-h2 leave the served path (compute-accounting, round 3; served-zk measures h2 and h3 tonight). `crypto/blake3.py` itself stays for Pearl's keyed-BLAKE3 seeds, noise and jackpot (E3). |
| A10 | `crypto/beacon.py`, `crypto/bls12_381.py` | BLS12-381 and SHA-256 (drand) | the epoch salt's source | PoUW `audit.py:34` and its schemes only. `randomness/__init__.py`'s docstring names beacon rounds as a source. | compute-accounting (C3) | **deleted by C3's draft [#1311](https://github.com/danielreuter/verity/pull/1311)**, along with PoUW's quicknet tests and vectors. The prose left over reads no beacon code: `randomness/__init__.py`'s docstring and `TypeError` text and vLLM's legacy `commit/challenge.py` (round 3's third PR), and PoUS's docs, after the rename move. |
| A11 | `crypto/turboshake.py` | TurboSHAKE128 | PoUW h0's message and leaf hash | `pearl_c.py` (h0), `pearl_c4.py`, `test_turboshake.py`, `benchmarks/pouw` | compute-accounting | **delete** with h0. Its claim `turboshake128` goes with it (branch `cursor/claims-turboshake128-95d4`). |

## B. Core identity digests (`verity/primitives/circuits`)

These are identities, not trees. Each row says whether a verifier binds it.

| # | where | hash | what it identifies | readers | owner | fate |
|---|---|---|---|---|---|---|
| B1 | `codec.program_digest` (`codec.py:409`), descriptor v1's id, pinned by `format_vectors.json` | SHA-256 | a Program | the IR, `annotations` and every recorded `program` reference | proofs | **keep, as an id.** What verifiers bind is `partition_object.program_sha512`, SHA-512 over the same canonical descriptor (lines 105–110). A v2 id would move every pinned format vector and recorded reference for no binding gain. |
| B2 | `circuit.program_sha512`'s fallback for a silicon reference with no core Definition: SHA-512 over `sub.program_digests` (SHA-256 per program) | SHA-256 inside SHA-512 | a class statement's program | `class_statement.py:369,883` (`unit-class/<name>` content digests) | proofs (C-Flock) | **move**: the class content digests become SHA-512. A `backends/flock/` change. |
| B3 | `query_codec.query_id` (`query_codec.py:124`) | SHA-256 | a query | `boolean_export.py:1519,1553` (a derived export) | proofs | **keep**: no verifier binds it, since the partition object carries the query itself. Move it if one ever does. |
| B4 | `units.UnitCircuit.shape` (`units.py:129`) | SHA-256 | the key that groups units of equal circuits | `class_statement.py` (class lists), one-stage's units | proofs | **move** at the next `units` revision: a collision would merge two classes. Low priority, because the Lean verifier derives units from the program itself. |
| B5 | `annotations.definition_digest`; `defs.py:391`'s 12-hex static name | SHA-256 | an annotation key; a display name | annotations; names | proofs | **keep**: annotations are never inside a digest, and the name is cosmetic |

## C. C-Flock (`backends/flock/`; any change needs a red-team grant)

| # | where | hash | what it commits | readers | owner | fate |
|---|---|---|---|---|---|---|
| C1 | **Legacy statements.**<br>Python: `ir_frame.py` (`verity/flock-ir-frame/v3`, SCHEME `frame-v3/blake3-keyed`), `ir_sampling.py` (`verity/flock-ir-sampling/v1`, `public_sha256`), `instances.py` (`statement`, `write_set`, `write_synth`, `write_fp4`; `--leaf sha256\|blake3`), `negatives.py`, `backend.py` (`FLOCK_FRAME_V3_BLAKE3`, `FLOCK_BLOCK`, `FLOCK_VLLM_V1`), the `stage()` of five templates (via `ir_frame.stage`) and of gumbel (via `ir_sampling.stage`), `bench.py`, `ir_bench.py`.<br>Rust: `live/src/{ir_frame,ir_sampling,ir_block,pure_block,vllm_block,chunk}.rs` and the bins `flock-pure`, `flock-pure-gpu`, `flock-ir-frame`, `flock-ir-sampling`, `flock-ir-block`, `flock-vllm-v1`.<br>Pod scripts: `20-pure`, `22-pure-gpu`, `23-ir-block`, `30`–`34-*`, `40-vllm-v1`. | SHA-256 frame-v3 trees over keyed-BLAKE3 (or `sha256/row`) rows; SHA-256 Σ and statement digest; BLAKE3 compression circuits | the legacy statements' inputs and outputs | Only the Rust binaries; no Lean file reads them (§16.3–16.4 "legacy-only"). Outside `backends/flock`: `benchmarks/numerical/.../drivers/c_interactive.py` (the C-interactive cell sweep, via `instances.write_set` and `ir_bench`); `tools/circuit_check/.../checks.py:733,744` (`ir_sampling.pin_digest` and `lane_circuit`, lowering only); `benchmarks/numerical/tests/bench/test_lowerings.py` (`lowering`); `benchmarks/one_stage/a0.py` (the binding tag string) | proofs | **delete, not move** (point 1 above). **Blocked on:** a red-team grant; whether anything still runs the C-interactive driver, since the tables read recorded cells from the store (`verity_numerical.bench.frozen`), not re-runs; and circuit-check's `ir_sampling` import. The gumbel lowering (`lane`, `lane_circuit`, `pin_digest`) is not a commitment and moves to a module of its own first. `tools/check` and circuit-check's binding schema are frozen until 14:00Z; `checks.py`'s import is outside the schema but is circuit-check's code, so ask before touching it. |
| C2 | `bin/flock-circuit.rs:82`, the SHA-256 `MERKLE` when `sha512` is off; `circuit.rs:199`, the `flock-leaf/sha256-unsalted` id when `sha512` is off | SHA-256 | Ligerito level trees | none: `flock-circuit` requires `sha512` (`live/Cargo.toml`) | proofs | **delete** (dead code; grant) |
| C3 | Lean: the tag sets `verity/flock-netlist/v1`, `@19c7269a`, `@fd02e847` (SHA-256 Σ, statement and coin commit; `flock-leaf/sha256-unsalted[/v0]` PCS leaves; `Blake3Row`), the `MerkleScheme.all` SHA-256 entries, `Statement.lean`, `Public.lean`'s SHA-256 public sha and `FV3` default `H := Sha256.hash`, `Circuit.lean:228`, `Transcript.lean`'s 32-byte round digest, `Record.lean`'s `sha512Digests = false` branch, `Hm96.sha256` | SHA-256, keyed BLAKE3 | recorded sessions under the old tags | `check`'s lean-agreement: `verifier/ci-bundle.sh` builds upstream at `9294e161`, `19c7269a`, `fd02e847` and `631567f7`; `upstream.json` pins them; `agree.py`; `verifier/vectors.json` (21 hits). The current tag sets inherit fields from `circuit631567f7` (`{ … with … }`), which `Soundness/Discharge/Exec/Retained.lean` and 2 `verity/Security/lean-audit.json` records cite. No `backends/flock/tests` file names them. | proofs (verifier of record) | **delete** the SHA-256 tag sets and their agreement bundles, once Daniel agrees that recorded sessions under them need no re-verification (their results stay in the store). Restate the current tags without inheriting from `circuit631567f7`. Needs a grant and lean-agreement, and a `ci-bundle.sh` change (lean-agreement's inputs; `tools/check` itself is frozen until 14:00Z). The 2 changed records need no statement reviewer (Daniel's 2026-10-03 ruling; he gets a DM when it lands). Until Daniel rules, the tag sets stay. |
| C4 | `circuit.py:712` binding (`identity_digest`, SHA-256) | SHA-256 | M0's frame domains | the Lean verifier doesn't see it (it reads `domain_ids` as given) | proofs | **move**: see the Binding plan section. The PR also fixes `circuit.py`'s docstring and `HmRow.lean`'s line 5, which say every binding digest is SHA-512. |
| C5 | M0 circuit META: each lookup's `"sha256"` (`circuit.py:568`; checked by `HmRow.lean:565` and `circuit.rs:750` beside the SHA-512 check of the table words); `params.unit_sha256` (`circuit.py:609,613`) | SHA-256 | redundant table pins; the lowering text's id | Lean `HmRow.parse`; Rust `circuit.rs`; circuit-check (`low.sha256` against `PINS`) | proofs | **move** at the next circuit tag version. The META bytes are inside the SHA-512-pinned circuit file, so this is a new tag set in `Tags.lean` (keep the old one) plus SHA-512 lowering pins in circuit-check after 14:00Z. Not a commitment hole: the SHA-512 check is what binds the table. |
| C6 | `lowering.py` `PINS`, `backend.py:61` source sha, `register.py` binary sha256s, `class_statement.py:1162–1187` cache keys, `partition_units.py:56` | SHA-256 | lowering ids; provenance; cache keys; a test seed | circuit-check; benchmark registration; caches | proofs | **keep**: provenance and cache keys commit nothing a verifier reads. Lowering pins follow C5. |
| C7 | `stage_salts` SHAKE-256 (`circuit.py:737`); `coin_seed.rs` `derive` and `stream` (SHA-256, mirroring `verity.randomness`); identity `coin_derivation: "sha256 (verity.randomness)"` | SHAKE-256, SHA-256 | salts and coins (PRF outputs) | prover; Lean coin derivation | proofs | **keep**: a PRF, not a commitment. The coin commitment itself is already SHA-512 (`coin-commit/sha512`). Under one hash, see D1. |

## D. Randomness, claims, and other lanes' protocols

| # | where | hash | what | readers | owner | fate |
|---|---|---|---|---|---|---|
| D1 | `verity/primitives/randomness/__init__.py:97,111,161` (`derive`, `Key.stream`, shard) | SHA-256 | challenge derivation, a PRF | everything that draws; mirrored by `coin_seed.rs` and the Lean coin derivation; pinned by `randomness/tests/vectors.json` | proofs (core) | **keep for now**: the ruling covers commitments, and a PRF commits to nothing. Recommendation: move to SHA-512 as `verity/randomness/derive/v2` and `stream/v2`, with the v1 vectors kept and new ones added, in a PR of its own once the commitment moves have landed. It touches Python, Rust (`coin_seed.rs`) and Lean together. Ask Daniel whether one hash covers PRFs. |
| D2 | `verity/claims/__init__.py` instances `sha-256`, `blake3`, `blake2b`, `shake-256`, `turboshake128`, `poseidon2-babybear`, `poseidon2-koalabear` | (ids) | Table 1's assumption ids | the docs site, schemes' `claims` | proofs | **keep** each id while one scheme cites it. Each goes with its last user (`turboshake128` with h0, `blake3` with h1–h3, `poseidon2-*` with the archive). |
| D3 | PoUW `audit.py:43–62,136`: `commitment_hash` defaults to `"sha256"`, and so do `rows_domain`, `commit_rows` and `transcript_domain`; 32-byte `tagged` bindings | SHA-256 frame-v3 | NCP's and Pearl FP8's row, tile and transcript trees | `schemes/ncp.py` (`ncp-v1`) and `schemes/pearl_kw.py` (`pearl-fp8-v4`), neither of which sets `commitment_hash` | compute-accounting | **move** to `sha512`, with a new scheme version for each (`ncp-v2` is already SHA-512 in `circuit/ncp2.py`). This is item 10. There is no strong reason to keep it: NCP is Verity's own scheme, and Pearl FP8's trees are "the protocol's activation and weight roots ... not Pearl's keyed-BLAKE3 Merkle openings" (`pearl_kw.py`), so SHA-256 is not in Pearl's definition. NCP's `perm_digest` (`ncp.py:117–119`, SHA-256 of a public permutation, "the research store's convention") moves with it. Its claims drop `cr/sha-256`. Compute-accounting agrees (round 3). Proofs offered them a one-hash PR, after the rename, that moves the default trees and the permutation digest; it waits for their acceptance. |
| D4 | PoUW `circuit/hashes.py` (item 6): `Sha512Compress`, `KeccakF1600`/`KeccakP1600R12`, gates for `shake256` and `turboshake128` | SHA-512, Keccak | in-circuit hashes for `ncp-v2` (SHA-512 rows and nodes; SHAKE256 key and noise) | `circuit/ncp2.py`, its tests, `verity/primitives/circuits/operations.py:49` (a mention) | compute-accounting | **keep** `Sha512Compress`. The Keccak gates are `ncp-v2`'s PRF (key, noise), not a commitment: keep them while `ncp-v2` derives with SHAKE256, or move with D1's decision. New circuits bind core's `verity/primitives/commitments/gates/sha512.py` (S1), not this copy; folding `Sha512Compress` into core's gate is compute-accounting's. |
| D5 | PoUW `pearl_kw.py`, `pearl_c*.py`: keyed-BLAKE3 seeds, noise and jackpot | keyed BLAKE3 | Pearl's own derivations | Pearl's spec (whitepaper Sep 2026; pearl-research-labs/pearl PR #311 at `284b147b`) | compute-accounting | **keep**: compute-accounting's strong-reason report (round 3). This note's view: they are in the external definition, and they are derivations, not commitments. |
| D6 | PoUW `protocol.py:31–32`, a tag-frame derivation | SHA-256 | scheme ids | PoUW | compute-accounting | **keep** (an id) |
| D7 | PoUS `setup.py:30–40` (`verity-pous/w-commitment/v1`, tagged SHA-256 of W); `verifier.py` `leaf_hash`/`node_hash` (the vk tree); `p2_v1/reference.py`'s second leaf framing | SHA-256 | W's commitment; the vk tree | PoUS's audit and grader | memory-accounting | **move**, per `note:20261006T0229Z-draft-proof-service-pous` R9: hm96-sha512 leaves in a frame-v3 tree. The SHAKE256 Feistel PRPs and seeds (`primitives.py`, `schemes/p2.py`) are PRFs: keep. Don't touch `audit.py` or `continuous.py` until the rename move lands. |
| D8 | Network certifier records (`verity/protocols/accounting/communication/warden/commitment.py:9,15,46,58`): `tagged_sha256("verity-network-warden/row/v1", ...)` and `record/v1` | SHA-256 | the certifier's per-row and per-record commitments | the network certifier | network-accounting | **move** to `row/v2` and `record/v2` (SHA-512) once the rename move lands (~09:00Z); its certificates take hash-based signatures over SHA-512. Out of bounds until then. |
| D9 | vLLM: core's `vllm_v1` and `leaves.py` (`verity-vllm/leaf/v1`) under the SHA-256 frame; `integrations/vllm/.../commit/merkle.py` (its own tagged SHA-256 tree); `commit/serving_rows.py` binding | SHA-256 | device commitments and serving rows | `integrations/vllm`, `kernels/hash_gpu/frame_v3.py`, `archive/sp1`, `catalog`, `benchmarks/numerical` | vllm | **move** with the vLLM serving path (`vllm_v1/vectors_sha512.json` exists). The `serving_rows` binding follows the Binding plan section's served-domain tag. Not proofs'. |
| D10 | `kernels/hash_gpu` (SHA-256, BLAKE3 and Poseidon2 column trees for A-GKR and B-Ligero) | various | proof-internal trees of the frozen backends | archive | frozen | **keep** with the frozen backends; delete them together |
| D11 | `tools/research` (store content addressing) | SHA-256 | artifact ids | the evidence store | infra | **keep**: content addresses, not protocol commitments |

## Format versions and vectors

`<name>/vN` ids are pinned: a change keeps the old id and adds a new version.

- **New versions:**
  - the binding tags (Binding plan, next section);
  - NCP and Pearl FP8's scheme versions (D3);
  - the network certifier's `row/v2` and `record/v2` (D8);
  - PoUS's W commitment (D7, memory-accounting's numbering);
  - M0's circuit tag set for C5;
  - `verity/randomness/derive/v2` if D1 moves.
- **No new version**, because the item is deleted rather than changed: `hm96-sha256/row/v1` (A5), the legacy C-Flock statements
  (C1), the Lean tag sets (C3) and C2's dead branch.
- **Vectors that move:**
  - none for A5;
  - `frame_v3/vectors_sha512.json` gains 64-byte-binding cases and keeps its old ones (Binding plan);
  - `randomness/tests/vectors.json` gains v2 cases if D1 moves;
  - PoUW's NCP and Pearl FP8 vectors get new-version files (compute-accounting).
  - A1's default flip moves no vector, since every SHA-256 vector generator pins `hash="sha256"` explicitly in that PR.

## Binding plan (frame-v3-sha512's SHA-256 `binding`)

- **Version.**
  - No new frame. `frame-v3-sha512` hashes `binding` as one length-framed part (`_message`: u64be length, then the bytes), so
    a 64-byte binding is a new input under the same rule, distinct from every 32-byte one.
  - `CommitmentDomain` accepts a binding of `DIGEST_BYTES[hash]` bytes (64) under `hash="sha512"`, and keeps 32 for recorded
    data. Under the SHA-256 and BLAKE3 frames it stays 32.
  - `frame_v3/PROTOCOL.md` §6's "What stays" paragraph becomes: a binding under frame-v3-sha512 is the caller's 64-byte
    `identity_digest_sha512`; a 32-byte one is a recorded statement's.
- **New tag versions**, each `identity_digest_sha512` over the same manifest:
  - `verity/flock-ir-frame/binding/v1` becomes `verity/flock-circuit/binding/v2`. The constant moves from `ir_frame.py` into
    `circuit.py`, which frees C1.
  - `verity/one-stage/served-domain/v0` becomes `/v1`, in one-stage `registration.py` and vLLM `serving_rows.py` together,
    since R3-domain recomputes it.
  - `verity/one-stage/registered-domain/v0` becomes `/v1`.
  - `benchmarks/one_stage/a0.py`'s `STAND_IN_BINDING` follows M0's tag.
  - PoUW's `tagged` bindings move with D3.
- **Vectors.** `frame_v3/vectors_sha512.json` gains a `binding64` group: domain id, leaves, pads and a tree over a 64-byte
  binding. Its existing groups (`row_trees`, `bit_row_trees`, `word_leaves` and the rest) stay byte-identical, and `hm96` and
  `vllm_v1`'s SHA-512 vectors are unchanged.
- **Readers.**
  - `circuit.py` (grant);
  - `registration.py` (R3-domain refuses a root whose domain is not its own derivation, so a served root registered under v0
    is refused by a v1 registrar: the intended break, and why `serving_rows` moves in the same PR);
  - `registered.py`;
  - vLLM `serving_rows.py` (vllm's file, landed together or right after);
  - `a0.py`.
- **Lean.** Unchanged: it reads `domain_ids` as given, and Σ binds the header that carries them. Rust `flock-circuit` reads them
  the same way.
- **Size.**
  - The core part is about ten lines in `merkle.py`, a test, the new vector group and the `PROTOCOL.md` paragraph: small enough
    to build as its own PR.
  - The consumers are a second PR, which needs the C-Flock grant because `circuit.py` changes, plus a vLLM commit.

## Tonight's PRs (round 3)

1. **Delete `hm96-sha256/row/v1`** (A5): pushed as `cursor/one-hash-hm96-sha256-row-95d4` at `9fe2aeec1`, on `main` at
   `68e614869`. Body: `one-hash-pr2.md`.
2. **Accept 64-byte bindings under frame-v3-sha512** (the Binding plan's core part): `merkle.py`, a test, a `vectors_sha512`
   group and `PROTOCOL.md` §6. Existing vectors don't change.
3. **The beacon prose** (A10's leftovers), apart from PoUS's docs.
4. **Binding consumers**, stacked on 2: M0's `verity/flock-circuit/binding/v2`, one-stage `served-domain/v1` and
   `registered-domain/v1`, vLLM `serving_rows`. Needs a grant, which proofs arranges.
5. **Poseidon2 into `archive/direct/ligero/`** (A8), if only archive code reads it.

Not tonight:
- TurboSHAKE (A11; h0);
- PoUW's SHA-256 frames and the NCP permutation digest (D3: proofs' offered PR waits on compute-accounting's acceptance) and
  `circuit/hashes.py` (D4);
- PoUS (D7) and the network certifier (D8), out of bounds until the rename move lands;
- the PRFs (D1, C7) and the Lean tag sets (C3), until Daniel rules;
- C-Flock's legacy statements and `merkle.py`'s default flip, after 14:00Z (next section).

## Plan for after 14:00Z: C-Flock's legacy statements (C1, C2), then `merkle.py`'s default (A1)

**Who still runs the C-interactive driver.**
- `benchmarks/numerical/.../drivers/c_interactive.py` has three paths, and only the last two are legacy:
  - `circuit:<template>` runs `61-circuit-cell.sh`, M0, and stays;
  - `irf:<template>` runs `33-ir-cell.sh` (`verity/flock-ir-frame`, via `ir_bench`);
  - a plain GEMM relation runs `30-cell.sh` (`instances.write_set`, `flock-pure`).
- `note:proofs/20261005T2352Z-draft-consolidation` §3 checked the store: no `research run` has invoked the legacy pod scripts
  since about Sep 27. Their table rows are read from stored results (`verity_numerical.bench.frozen`, the drilldown), so the
  tables don't change.
- I couldn't re-check tonight. This VM's store is fresh: `research data select --tool flock_pure` gives 0 artifacts, and the
  CLI has no remote listing of attempts.
- Before the PR, re-run the query where the store's index is: attempts since Sep 27 whose command names `20-pure.sh`,
  `22-pure-gpu.sh`, `23-ir-block.sh`, `30-cell.sh`, `31-replay.sh`, `33-ir-cell.sh`, `34-ir-*.sh` or `40-vllm-v1.sh`.
- If there are none, `c_interactive.py`'s `SCRIPT` and `IR_SCRIPT` paths go and `CIRCUIT_SCRIPT` stays.

**What goes.** The consolidation note's §3 list, which C1 matches:
- 8 of `live/src/bin`'s 10 bins, keeping `flock-circuit` and `flock-live`;
- `lib.rs`'s `ir_frame`, `ir_sampling`, `pure_block` and `vllm_block`;
- `ir_frame.py`, `ir_sampling.py`, `ir_bench.py`, `negatives.py`, and the seven templates' `stage` functions;
- `tool.py`'s `FLOCK_PURE`;
- the legacy pod scripts;
- `backend.py`'s three `BACKENDS`, and `bench.py`/`instances.py` cut down to what `circuit_bench.py` and `register.py`
  import;
- C2 (`flock-circuit`'s dead SHA-256 branch).

M0 first takes `BINDING_TAG` and `OWNER` from `ir_frame` into `circuit.py`, which tonight's fourth PR does. The row schemas
that only C1 reads then go too: `blake3-keyed/row/v2` and `blake3-keyed/row-nvfp4/v1` (A7). `sha256/row/v1` and
`sha256/row-nvfp4/v1` (A6) stay for the archive.

**circuit-check's `ir_sampling` lowering.**
- `tools/circuit_check/.../checks.py:733,744` imports `ir_sampling.pin_digest` and `lane_circuit` for
  `gumbel-top-p-token-select`, and the template's `frame_lowering` calls `ir_sampling.lane`.
- Move `lane`, `lane_circuit`, `pin_digest` and what they need into a module of their own: the template module, or
  `verity_flock/sampling_lowering.py`. Then point `checks.py` at it.
- It moves a lowering, so the PR carries a `circuit-check` report. It runs `uv run circuit-check gumbel-top-p-token-select`,
  whose digest must still equal the template's `PIN`, and `circuit-check` on the other six templates whose `stage` goes, to
  show their lowerings unchanged.
- `checks.py` is circuit-check's code, not its binding schema, but it waits for 14:00Z anyway.
- `instances._ligero()` loads archive's `ligero.timing_guard` for `bench._guard()`, which the circuit sweep uses
  (consolidation §2). `timing_guard` moves into `verity_flock` first.

**Grants and checks.**
- A red-team grant for the `backends/flock/` deletion. Its `check` record runs lean-agreement, because the commit touches
  `backends/flock/`. Lean itself doesn't change: it reads none of these forms.
- The `circuit-check` report above.
- The numerical bench's owner reviews the `c_interactive.py` edit.
- C3 (the Lean tag sets) is a later PR of its own, once Daniel rules. It needs a grant and lean-agreement, and no statement
  reviewer.

**Order.**
1. Move the gumbel lowering and `timing_guard`, with the `circuit-check` report.
2. Delete C1 and C2, and the A7 schemas.
3. Flip `merkle.py`'s default (A1):
   - pin `hash="sha256"` at every SHA-256 reader left: `frame_v3/vectors.py`, `archive/direct/ligero/{auth,vu,reverify}.py`,
     `archive/gkr/gpu/commit.py`, `kernels/hash_gpu/tests/test_frame_v3.py`, the core tests (`test_frame_v3`, `test_scheme`,
     `test_rowleaf_nvfp4`, `test_rowleaf_bits`, `test_poseidon2`) and `experimental/tests/commitments/test_multiproof.py`;
   - then make `"sha512"` the default of `CommitmentDomain.hash`, `_hash` and `domain_message`.
   - No vector moves: each generator pins its hash. `RangeIndexedDomain` has `identity_sha512`, so a default domain builds.
     Lean doesn't change.
   - The archive pins change no behaviour, but they touch the frozen archive: the coordinator's nod.
   - It needs no `backends/flock/` change once step 2 has removed C-Flock's four default-hash call sites.
