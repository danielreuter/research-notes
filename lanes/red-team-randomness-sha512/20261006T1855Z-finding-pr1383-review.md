---
id: red-team-randomness-sha512/20261006T1855Z-finding-pr1383-review
campaign: proofs
lane: red-team-randomness-sha512
kind: finding
status: final
repo: verity
origin: pr:1383@7f32a63eb4a6282f518d298fb9f12a92a81b260b
---

# Red team on #1383 (`verity.randomness` on SHA-512): GRANT

PR #1383 (`cursor/randomness-sha512-95d4` at `7f32a63eb`, base `f5df3bbc5`) moves `derive`, `stream` and `shard` from
SHA-256 to SHA-512 (tags `…/v2`), keeps `Key` at 32 bytes, and repins every lane's vectors. No blocking finding.
Local evidence (the Rust cross-check crate, the vector regeneration, the slow-test logs) is `art:886fde9ccb143b78b1c9de8cc14f577194da4a67640c1f40ec64c838ed3ddb52`
(`redteam-findings/v1`, PRESERVED).

## What was checked

1. **Derivation and samplers.** `derive` and `shard` are the first 32 bytes of SHA-512 over the v2 tag and the same
   frames as v1; a stream block is the full 64-byte digest over tag, key, framed index and be64 counter. `uniform`
   (rejection over `ceil((bitlen(n)+64)/8)`-byte words), `bernoulli` and `subset` (sparse Fisher-Yates) read the
   byte stream only, so they stay exact under 64-byte blocks; their code is unchanged. `tests/vectors.py --check`
   passes and its regeneration is byte-identical to the committed `vectors.json`; the base's v1 code reproduces the
   base's vectors from the same generator, so the generator, not hand edits, produced the repin. Core suite: 55 passed.
2. **Python, Rust and Lean agree.** `coin_seed.rs` (Sha512, key `[..32]`, 64-byte stream blocks) built standalone with
   its KAT plus three extra cases derived from Python: 4 passed. `flock-circuit.rs:220` names `sha512 (verity.randomness)`.
   `Randomness.lean` follows the Python on `Flock.Sha512.hash` (`extract 0 32`, `(n + 63) / 64` blocks);
   `randomness_lean.json` equals node run `r20261006-154310-eb1a`'s output, and `generate.sh`'s inputs cover
   `Flock/Hash.lean`. `Tags.lean` pins the base's four identities as `@f5df3bbc` with the v1 text and builds `circuit`
   and `circuitTypes` with `sha512`; the 18 seeded digests in `test_lean_verifier.py` and `test_pouw_rows.py` were
   regenerated on vy-nebius-1 (`r20261006-172404-3648`, Lean equals Rust on all 18), and the os digests and
   `circuit_sha512` are unchanged. PROTOCOL §7.2 states v2 and how it differs from v1.
3. **A4 `prf/sha-512`.** The statement models SHA-512's compression function as a PRF under its chaining value (the
   prefix-free cascade) and as a dual PRF under a secret in the first 128-byte block; the tags are 28 bytes, so
   `derive`'s 32-byte source sits wholly in block one at offset 37 (under v1's 64-byte block it straddled two, which
   v2 fixes). η ≤ 2⁻¹²⁸ holds, the truncation term `q·T·2⁻²⁵⁶` is 2⁻¹³⁶ at the stated budget, and
   `assumption-notes/a4-prf-sha512.md` derives both. `upstream.watch["A4-prf-sha512"]` is present (mentions
   `PRFScheme.prfAdvantage`).
4. **Lean records.** `r20261006-155125-cd8a` (`audit.py --build --update`, three packages, at `31d346853`): PASS, and the
   record change is limited to the reads of `Flock.Tags` and `Proofs.Flock.Soundness.Randomness`.
   `r20261006-172700-2716` (`audit.py --build`, at `b16db8089`): PASS on all three packages. Between `b16db8089` and the
   head only `test_lean_verifier.py` and `test_pouw_rows.py` change, so the audit stands.
5. **Nothing else moved.** Every caller of `derive`, `stream` and `shard` and every literal pin was grepped. Repinned:
   `identifier_v1.json` (regenerated, equals committed), `test_input_sets.py` (stream pin recomputed independently),
   claims registry. Unaffected and confirmed: the vLLM challenge path (`LEGACY = True`), replay and regression
   checks, the PoUS setup/audit/P2 framing, the experimental law, the PoUW window and debit benchmarks, archive, and
   census. PoUW benchmarks' slow suites: 38 passed. `main` moved 26 commits with no shared file and a clean merge-tree.

## Non-blocking notes

1. `replay_coin_seed` (`backends/flock/live/src/lib.rs:325`, the `flock-circuit replay-coins` command) now replays
   only v2 seeded sessions. A pre-PR seeded record fails as "coin request g is not the seed's derivation", because the
   record's `coin_seed` scheme and domain did not change, so the replay cannot tell v1 from v2. The Lean verifier reads
   coins from the record and is unaffected; no in-tree test or headline replays an old seeded record. If wanted: key
   a v1 path on the identity's `coin_derivation`, or say in §7.2 that `replay-coins` covers v2 only.
2. Stale "SHA-256" prose: `flock-circuit.rs:98` (doc comment), `backends/flock/pod/gemm_hill.py:84,87` (the
   `os-seed-prf` COINS text, which is written into sweep records), `test_randomness_spec.py:66` (docstring).
3. `test_lean_zk.py` was skipped in the author's node run; its `@f5df3bbc` rename is right by the same argument as the
   three analogous tests that passed there (hidden outputs, identifier, public inputs).
4. `A5-uniform-secret` still has no upstream watch entry (pre-existing, `ASSUMPTIONS.md:337`).
5. The `research` and `tc-probe-fp4` suite failures in the author's run are harness-only; both pass on a VM at the head.
