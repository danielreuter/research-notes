---
id: 20260926T1740Z-report-flock-netlist
campaign: boolean-escape-hatch
lane: flock-netlist
kind: report
status: open
repo: danielreuter/verity
origin: cursor/flock-netlist-m0-4d6a
branch: cursor/flock-netlist-m0-4d6a
---

CHECKPOINT cf4e4830 (02:10Z) [open] hm96-sha512/v1 leaves built and GPU-verified; measured +96% prover time at m=33 from OS salts (670 MB/proof) -> asked coordinator to allow device ChaCha20 salts from a per-proof OS seed; verifier lane told the hm96 proof layout; pod terminated; next: serving row leaf (SHA-512 compression slots + hm96 row unit)
CHECKPOINT 2908d078 (01:53Z) [open] hm96-sha512/v1 Merkle leaves built (2908d078), GPU selftests all pass r20260927-012544-d134 (A6000); estimate for the multi-table glue statement sent to coordinator (about $8-12, after attention); next: hm96 cost A/B on the A6000, then the serving row leaf
CHECKPOINT 631567f7 (01:05Z) [open] SHA-512 statement published to flock-verifier (tags, merkle_hash=2, flock-leaf/sha512-unsalted, hm96-sha512/v1 target, msg; records art:1100e385); both pods terminated via drain (all attempts preserved); next: HM96-on-SHA-512 Merkle leaves and attention in the circuit (M0 left)
CHECKPOINT 631567f7 (00:23Z) [open] SHA-512 Merkle trees built (Flock Rust patch + CUDA patch, feature sha512), GPU selftests all pass r20260926-223809-45ce; final cells: RoPE art:36146f53 2.88G, SiLU art:a689c740 3.27G, RMSNorm fused art:293ac579 2.30G, Triton art:786a7e1e 1.55G AND/s ref-profile; SHA-512 cost none measurable in time, proofs +36-39%; batched-sessions design noted for M1/M2; record run r20260927-001758-21e8 for the verifier lane
CHECKPOINT fd02e847 (21:46Z) [open] red-team-hm96 F6: the hm96 key is a statement constant (DEFAULT_KEY pinned by SHA-256, derived in Rust and checked against core), negative leaf_key_witness_refused, fd02e847; format final there (verifier lane told); cells recording at fd02e847
CHECKPOINT 4f8316ce (21:21Z) [open] from_record replays circuit records (verifier lane's fix, a2a7e7f4; selftest record_replays_offline); tags/domains/Σ final, format final for the NON_ZK unsalted-leaf statement at 4f8316ce (handoff to flock-verifier); circuit_bench merge fix (rmsf/rmst results had KeyError); all four cells re-running at 4f8316ce
CHECKPOINT 99e2f750 (20:59Z) [open] internal leaf slot aligned with hm96-sha256/v1 (OS salts 128 B/leaf, one key per proof; verifier checks the whole pinned scheme; negative leaf_scheme_seeded_salts_refused); coordinator 19:55Z rename handoff already done (backend identity flock-circuit / C-interactive/flock-circuit); GPU selftest r20260926-200726-8dce all-pass incl determinism; SiLU cell art:76750e45 superseded by a timing fix (wait inside e2e window), cells re-running at the final commit; handoff to coordinator: frame-v3 hm96 row schema needs an owner
CHECKPOINT 0615b284 (20:12Z) [open] renamed to verity/flock-circuit; coin record replayable (global index g); prover deterministic with explicit seed; every commitment hash SHA-256 and pinned in the identity (HM96 Merkle leaf + serving row leaf left); L40S GPU selftest r20260926-200726-8dce running, then cells SiLU/RoPE/RMSNorm x2
CHECKPOINT f1112817 (18:41Z) [open] SiLU L40S cell ok (loopback 4.6 G AND/s e2e at 128 rows; ref-profile 3.3 G) r20260926-181746-69fe; step-0 coin seed + RMSNorm tails in circuit (lookups, two-phase device witness) landed; selftests of 4 templates on L40S r20260926-183942-576e
CHECKPOINT e231d583 (18:05Z) [open] GPU path works on RTX 4090 dev pod: device witness + multi-range fold, GPU selftests all-pass RoPE (k_log 20) and SiLU (k_log 26, private BLAKE3 parent tree) r20260926-175514-5b86; verifier-tail refusal + negative (Daniel's rule) landed; now timing r20260926-180450-ecfa; L40S hunter running (no stock); next RMSNorm tail in circuit (MUFU lookup slots)
CHECKPOINT 9fd167e1 (17:40Z) [open] started M0: verity/flock-circuit CPU statement landed (RoPE 19/19 CPU selftest cases incl relabelled circuit, SiLU in-circuit parent tree); next GPU device witness + multi-range fold; branch cursor/flock-netlist-m0-4d6a; agent bc-ff572e70
# flock-circuit: M0 `verity/flock-circuit` (NON_ZK, ZK-ready)

Spec: Project store `docs/boolean-prover-scoping.md` (M0 row, M0 acceptance, section 4). Agent bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a.

## Design (as built)

- One or more whole VUs per block; every glue inside a block is a copy constraint (Δ); no prover-supplied value, no glue claim.
- Slot types per block: BLAKE3 compressions (chunk runs per port; for a multi-chunk port its parent tree, root first), the
  template's units, a reserved mask slot (free cells, A = B = I), forced-zero padding apart from it.
- Public: frame-v3 roots, the row digests (serving leaves; unsalted until Daniel's call), declared outputs, the pinned layout.
  Chaining values, chunk values, every word between slots: private.
- The pinned composite circuit (`flock-circuit`, sha256 = pin) is the meaning: META (ports, ranges, compression roles, leaf
  and output maps, pinned padding-instance values, leaf-commitment scheme) + each slot type's `flock-ir-unit/v2` expanded circuits. The
  verifier derives Δ, regions and values from it and its own public file (no rows).
- Code: `backends/flock/python/verity_flock/circuit.py`, `backends/flock/live/src/{circuit,zk_hooks}.rs`, `bin/flock-circuit.rs`.

## Standing rule (Daniel, 18:01Z): the verifier evaluates no part of the computation

Tightens scoping §4.1 (no exception for functions of public data). Built into the statement: `Composite::parse` refuses a `CUT`
line in any NET and META keys `tail`/`cut`/`cut_words`/`public_ports`/`public`/`native`; negative `verifier_evaluated_tail_refused`
(both forms refused at parse). The verifier no longer evaluates the unit's expanded circuit on zero inputs to check the pinned padding
outputs (the circuit forces them; a wrong pinned value only makes the statement unsatisfiable). It still hashes a zero row to
check the pinned padding digest (the commitment scheme's own function) and recomputes the frame-v3 roots.

Sampling under the rule (not in M0 acceptance; estimate, not lowered): per vocabulary lane, Gumbel noise =
Philox4x32-10 (~15k ANDs/lane amortised) + libdevice `logf(-log1pf(-u))` (~24 fma + 5 mul + 3 add + add.rz + 3 cvt ≈ 125k
ANDs at the fp piece costs 4,498 / 2,406 / 823) ≈ 140k ANDs/lane vs 5,099 today (27x); V = 128,256 → ~1.8e10 ANDs/row;
#101's 32 rows → ~5.8e11 ANDs (+0.37% of #101's 1.57e14; ~+580 L40S-s at 1 G AND/s ≈ +1.1% of ~51k s). Top-p keep word
(MUFU EX2/RCP over whole-row reductions) in circuit: the scoping's x2 on sampling (another ~0.65 G ANDs/row) plus EX2/RCP
lookup slots (~40k ANDs each). Sampling carries become private Δ glue between consecutive lane units (free).

## Checkpoint results (18:25Z)

- CPU selftests: RoPE 20/20, SiLU (in-circuit BLAKE3 parent tree) all pass (local).
- GPU (RTX 4090 dev, then L40S): selftests all-pass RoPE k_log 20 and SiLU k_log 26 (runs r20260926-175514-5b86,
  r20260926-180609-0360); device witness = BLAKE3 kernel + new bit-sliced level-ordered unit kernel; multi-range fold.
- 4090 loopback timing (r20260926-180450-ecfa): SiLU 32 rows (707M ANDs, m=31, both reps) e2e 0.218 s = 3.2 G AND/s;
  device witness units 17 ms, compressions 4.5 ms per rep.
- Tail pieces: RsqrtApprox (954 ANDs), MufuSqrtFtz (148), DivFullRcp (5,657) exact vs the IR primitives on ~4k words (19
  NaN-payload-only differences in DivFullRcp from fp's canonical NaN, the lowering's existing policy). Lookup slot (lookup.rs):
  fast witness = its rows' evaluation (unit test). RMSNorm tails: fused 2 stages (27.7k + 0.2k ANDs) + 1 rsq lookup; Triton
  3 stages (8.5k + 3.3k + 5.0k) + sqrt + rcp lookups (DivFullRcp of the constant N folded).

## ZK-readiness choices as built (scoping §4)

1. **Private by default.** Public: frame-v3 roots, row digests, declared outputs, pinned layout. The verifier's own instance file
   (`pub-N.bin`) holds no row; `serve` refuses a file with rows. Every intermediate word is private Δ glue inside a block.
2. **One commitment, reserved room.** One root per statement bound by both reps (flock-128-r2, R1). Each block reserves a
   2^14-bit mask slot of free cells (A = B = I; zeros in M0, random cells accepted: negative `mask_cells_random` accepts),
   apart from forced-zero padding. `t_pad` is a hook (0 in M0). Single-run 2^-128 is NOT done: Flock's F128 PIOP union is
   2^-118.4 per run (flock-128), so a single run needs F256 challenges or a doubled PIOP on the same opening (M1/M2 item).
3. **Leaf commitments of the proof's Merkle trees:** a named, pinned, swappable scheme in META and the backend identity.
   Pinned today: `flock-leaf/sha256-unsalted` (Flock's own leaf) because the hiding leaf is NOT implemented yet. Its target is
   core's `hm96-sha256/v1` (PR #88): 128 B salt per leaf from the OS generator, hm96's pinned key as a statement constant (section "Internal
   leaf slot aligned" below).
4. **Live coins from a seed committed at step 0** (`coin_seed.rs`, SessionConfig.coin_seed): the verifier draws seed + nonce
   from the OS, answers Hello with `SHA-256(tag‖nonce‖seed)` (scheme `coin-commit/sha256`, HM96 the target), derives every
   coin with `verity.randomness.derive` (domain `verity/flock-circuit/coins/v1`, context = the hello; byte-compatible, pinned
   by a Python vector), reveals seed + nonce in the verdict; the prover checks the opening and every coin
   (negative `coin_seed_opening_forged`). Prime-field live coins with a committed seed are refused (not built).
5. **Masking hooks as no-ops** (`zk_hooks.rs`): sumcheck-round hook, `t_pad`, claim-point permutation, mask-fill slot, `zk`
   in the identity (pinned in the statement digest). **Prover randomness:** `ProverRng::from_os()` only (getrandom 256-bit
   seed per proof, ChaCha20 streams addressed by (purpose, index) for device expansion); no transcript input; the test-seed
   constructor is `#[cfg(test)]`; ignored TODO test `two_proofs_share_no_mask_bits` for M1.
6. **The circuit pin is the meaning.** The composite circuit's sha256 is `--pin`; the verifier derives Δ, regions and values from
   it alone (`relabelled_circuit` / `relabelled_circuit_refused_at_load` negatives).

## Cells (final statement: SHA-512 Merkle trees; commits b3baabd8, bb9a2a90, 631567f7 differ only in the selftest harness)

Prover L40S (RunPod US-TX-4), verifier RTX 4090 (EU-RO-1, a separate machine, RTT about 143 ms), relation `circuit:<template>`,
backend `flock-circuit` (configuration `C-interactive/flock-circuit`), every cell checked (no problems) and registered.
End to end = loopback median of 5 timed sessions at the plateau; reference profile = prover compute + rounds × 1 ms +
bytes / 100 Gb/s (the renderer's formula).

| template (input set) | rows | prover / verifier run | art | ANDs | e2e loopback | AND/s loopback | AND/s ref. profile | proof |
|---|---|---|---|---|---|---|---|---|
| RoPE d64 neox (art:20ad905f, synthetic) | 8,192 | r20260926-230930-2f43 / -230921-b27b | art:36146f53 | 1.57 G | 0.295 s | 5.32 G | 2.88 G | 1.50 MB |
| SiLU·mul i8192 (art:d3e2d9b1, captured) | 128 | r20260926-232211-9164 / -232201-690b | art:a689c740 | 2.83 G | 0.607 s | 4.66 G | 3.27 G | 1.56 MB |
| RMSNorm fused n2048 (art:a261c0c2, tails in the circuit) | 256 | r20260926-233800-cd53 / -233735-ea80 | art:293ac579 | 2.60 G | 0.836 s | 3.11 G | 2.30 G | 1.64 MB |
| RMSNorm Triton n2048 (art:9582a734, tails in the circuit) | 256 | r20260926-235738-e628 / -235714-1f30 | art:786a7e1e | 2.32 G | 1.22 s | 1.90 G | 1.55 G | 1.60 MB |

All four clear the 1 G AND/s target end to end under the reference profile. SHA-256 predecessors (superseded, kept for the
cost comparison above): SiLU art:e3e349b5 (4f8316ce), RoPE art:7d23d5d9 (fd02e847); SiLU art:76750e45 is labelled
`superseded_by` (its prover-compute field was wrong).

## Naming (Daniel, 19:47Z)

The statement is `verity/flock-circuit` (no version in the name; versioning is by digest: the pinned composite circuit's
sha256 and the statement digest). Formats `flock-circuit` (the pinned composite circuit), `flock-circuit-inputs` (instance files);
scheme ids `flock-leaf/sha256-unsalted`, `coin-commit/sha256`; relation `circuit:<template>`; binary `flock-circuit`. "Expanded
circuit" names a slot type's gate-by-gate `flock-ir-unit/v2` form. One exception: the coin derivation domain is
`verity/flock-circuit/coins/v1`, because `verity.randomness.derive` requires `verity/<protocol>/<purpose>/v<n>`. Left as they are:
`ir_lower.netlist()` and `IrUnitNet`, owned by the lowering lane (called through one helper). Cells before 19:56Z ran under the
old id and are measurements only.

## Step 0 replayable from the record (verifier lane, 19:49Z)

Every seed-derived round in the session record carries `g`, its session-wide coin-request index; the link points carry
`points_g`; the record's `coin_seed` section holds the scheme, the domain, the derivation context (the exact hello), the
commitment, the request count and (once the verdict is issued) seed and nonce. `flock_live::replay_coin_seed(record)` /
`flock-circuit replay-coins --record session.json` re-derives every request from the record alone, however the reps interleave,
and checks that the indices are exactly `0 .. requests`. Selftest `coin_seed_record_replays`: an honest record replays (RoPE: 175
requests); the same record with two rounds' indices swapped is refused.

## The prover as a function of (statement, witness, prover seed, coins) (19:52Z)

`zk_hooks::ProverSeed` is an explicit input of every proof: `ProverSeed::from_os()` (getrandom) is the only constructor in a
proving build; `ProverSeed::injected` and the verifier's `Server::inject_coin_seed` exist only under the cargo feature
`seed-injection`, which `60-circuit.sh` enables for MODE=selftest and never for bench or cells (61-circuit-cell.sh builds without).
Selftest `prover_is_deterministic`: two sessions with the same injected prover seed and verifier seed give byte-identical proofs
(both reps) and transcripts (every round's message digest and coins, the link exchange, the proof digests); CPU passes on RoPE,
and the L40S GPU path passes on RoPE and fused RMSNorm with every other case (run r20260926-200726-8dce, all_pass both;
record replay 175 and 271 requests).
No message byte depends on scheduling: every parallel reduction is a GF(2^128) sum (XOR, order-free), device kernels are
deterministic, M0 draws no prover randomness into any message.

## SHA-512 on every commitment path (Daniel, 21:53Z; supersedes the SHA-256 section below where they differ)

Commits 4bceebef (contained part) and 23b5ee05 (Merkle trees). What the statement pins now (backend identity `hashes`):

| path | hash | how |
|---|---|---|
| Ligerito Merkle trees, every level, leaves and nodes | **SHA-512**, 64-byte digests | `leaf = SHA-512(column bytes)`, `node = SHA-512(left ‖ right)`, no domain separation (Flock's SHA-256 format, widened); caps and paths carry 64-byte nodes; the transcript observes the cap's 64-byte nodes |
| round digests | SHA-256, framing only | the coin server retains every round's bytes (`SessionConfig.retain_rounds`, bound in the hello as `"rounds": "bytes retained"`); the record carries them (`msg`), `from_record` rechecks them, and the replay compares the proof's messages with the kept bytes byte for byte; the digest is compared only where no bytes are kept |
| step-0 coin commitment | **SHA-512** (`coin-commit/sha512`) | `SHA-512("verity/flock-circuit/coin-commit\0" ‖ nonce ‖ seed)`, sent at Hello as four GF(2^128) words |
| internal leaf target | HM96 on SHA-512 | 192-byte OS salts, a 2047-bit key that is a statement constant (red-team-hm96 F6); core has no SHA-512 hm96 scheme yet |
| coin derivation, statement digest, Σ | SHA-256 | not commitments (`verity.randomness`, identifiers) |
| frame-v3 tree, serving row leaf | SHA-256, keyed BLAKE3 | the serving side's formats (core, salted-leaves), not this statement's to choose |

**How it is built.** Flock hard-codes a 32-byte `Digest`, so the Merkle change is a Flock patch applied only to the circuit
build (60-circuit.sh), selected by flock-live's feature `sha512`:
- `backends/flock/flock-sha512-b684b12.patch` (Rust): `Digest = [[u8; 32]; 2]` (64 bytes; the two halves keep serde's array
  support and turned every byte-level assumption into a compile error, about 25 sites fixed), `HashKind::Sha512`,
  `Sha512MerkleHash`; the 32-byte Merkle kinds panic in this build rather than misalign a tree; Fiat–Shamir and PoW keep
  their own hashes (live coins use neither).
- `backends/flock/cuda_sha512_patch.py` + `cuda/sha512.cuh` (device): a warp-staged SHA-512 leaf kernel (each 128-byte chunk
  staged with coalesced loads is one SHA-512 block), a byte kernel for other leaf sizes, a node kernel, and 64-byte nodes in
  the gathers, cap copies, tree allocations, cap observations and the proof writer (every edit asserted by count).
- flock-live reads and writes digests at whatever width the linked Flock has (`merkle_digest_bytes`, `merkle_digest_read`),
  so the other statements' 32-byte builds are unchanged.

**Checked.** GPU selftests on the L40S, all cases pass for fused RMSNorm (k_log 25), RoPE (k_log 20) and SiLU (k_log 26):
r20260926-223809-45ce (23b5ee05). CPU selftest on Triton RMSNorm n128 on the RTX 4090 pod: r20260926-225845-40aa (27/27).
Locally, the CPU SHA-512 build passes RoPE 25/25 at b3baabd8. The proof's `PcsParams.merkle_hash` is bincode variant 2
(`HashKind`: Sha256 0, Blake3 1, Sha512 2), read back from a proof's bytes.

**Cost, measured** (same sets, L40S, loopback median of 5 timed sessions; SHA-256 cells from earlier the same day):

| template | SHA-256 e2e | SHA-512 e2e | change | proof bytes SHA-256 → SHA-512 |
|---|---|---|---|---|
| RoPE d64, 8,192 heads (m = 23) | 0.296 s (art:7d23d5d9) | 0.295 s (art:36146f53) | none measurable | 1,096,114 → 1,496,370 (+36.5%) |
| SiLU·mul i8192, 128 rows (m = 33) | 0.602 s (art:e3e349b5) | 0.607 s (art:a689c740) | +0.8% | 1,123,058 → 1,557,042 (+38.6%) |

The encoding-and-commitment bucket is unchanged (RoPE 12.2 against 12.3 ms per rep): the staged SHA-512 leaf kernel keeps
the Merkle work in the noise. Proofs grow by the hash share, as ASSUMPTIONS.md §4.2a expected (about 36%). Reference-profile
throughput is unchanged: RoPE 2.88 G AND/s, SiLU 3.27 G AND/s.

## SHA-256 for every commitment hash (Daniel, 20:00Z)

Audit of the statement's hash paths (commit 448092ae pins each in the backend identity, so the statement digest binds them):

| path | CPU prover | GPU prover | status |
|---|---|---|---|
| Ligerito Merkle trees (proof-internal) | SHA-256 | SHA-256 | done: `PcsParams.merkle_hash = Sha256`; the verifier checks params equality |
| round digests, statement digest, Σ | SHA-256 | SHA-256 | done |
| step-0 coin commitment and derivation | SHA-256 | SHA-256 | done (`coin-commit/sha256`; `verity.randomness` is SHA-256) |
| frame-v3 root tree | SHA-256 | SHA-256 | done |
| live-coin transcript | none | none | no hash: coins come from the verifier |
| Merkle leaf commitment | SHA-256, unsalted | SHA-256, unsalted | to do: `flock-leaf/hm96-sha256` |
| serving row leaf, hashed in the circuit | BLAKE3 keyed | BLAKE3 keyed | waits on lane salted-leaves' HM96-on-SHA-256 row format; `verity.commitments.rowleaf` is not this lane's |

The CPU prover's BLAKE3 was Flock's default Merkle hash, and this statement never used it: both provers build with
`HashKind::Sha256`. What is left is the two leaf constructions.

Cost (estimates from the layout; nothing lowered or measured yet):
- **Serving row leaf in the circuit, BLAKE3 → SHA-256.** A SHA-256 compression slot is 2^15 bits against 2^14 for BLAKE3, and
  SHA-256 is Merkle–Damgård, so there is no parent tree: a 4 KB row costs 65 compressions (64 blocks + padding) instead of
  4 chunks × 16 plus 3 parents. The four M0 templates stay at the same k_log because the extra rows fit in each block's slack,
  so proving time is about unchanged; the device witness gains a SHA-256 kernel (a few ms per rep). HM96 on top adds about
  1–2 compressions per row (the universal hash of x plus the extra block).
- **HM96 internal Merkle leaves** (`hm96-sha256/v1`, next section; this corrects my 20:15Z estimate of +1–3% hashing and
  +150 KB, which assumed a per-leaf key and one extra block): +5 SHA-256 compressions per leaf (3 for c, 2 for the leaf; both
  prefixes are constant midstates). A level-0 leaf is a 1 KiB column (17 compressions plus about 2 per tree node), so level-0
  hashing grows about 26%, more on the recursive levels' 256 B leaves; encoding and commitment are 24 ms of about 300 ms per
  rep (SiLU, 128 rows), so about +2–3% of prover time. The proof grows 128 B per opened leaf: 527 openings per rep at m = 33
  (218 + 106 + 71 + 53 + 43 + 36), 1,054 per proof, about +135 KB (+12% of 1.12 MB); the key is a constant, never sent. The work
  is a Flock CPU leaf function, the CUDA Merkle kernel patch, and the opened salts in the proof format.

## Internal leaf slot aligned with `hm96-sha256/v1` (core PR #88; handoff note:20260926T2034Z-handoff-from-salted-leaves, 20:50Z)

Commit on PR #83 after 0615b284. The pinned leaf scheme (META `leaf_scheme`, backend identity, checked whole by the verifier at
parse; negative `leaf_scheme_seeded_salts_refused`) is still `flock-leaf/sha256-unsalted` with `salt_bytes` 0, and its
`target` now reads, field for field with PROTOCOL.md section 7:
- scheme `hm96-sha256/v1` over the SHA-256 column digest (x); leaf = `tree_leaf(key, b ‖ c)`; an opening = column + salt;
- **salts: 128 B per leaf straight from the OS generator (getrandom), one draw per leaf.** Chosen over the ChaCha20 stream so
  the leaves hide statistically. Cost measured: getrandom runs at 0.55 GB/s per core and scales linearly (1, 2, 4 threads:
  0.55, 1.11, 2.20 GB/s on this VM); a SiLU proof at 128 rows needs about 430 MiB (level 0: 2^21 leaves × 128 B, shared by
  both reps since R1 binds one root; recursive levels about 0.7M leaves per rep), about 0.06 s on the prover's 14 threads,
  and it overlaps the device witness. No reason to prefer ChaCha20. `STREAM_SALT` is gone from `ProverRng`. The salts will be
  a second explicit prover input beside `ProverSeed` (injectable only under `seed-injection`), so the prover stays a
  deterministic function of its inputs and the byte-for-byte comparison with a Lean prover still works;
- **key: hm96's `DEFAULT_KEY`, one constant of the statement for every tree and for the serving-row gadget** (red-team-hm96
  F6, 21:45Z, commit fd02e847; this replaces my 20:55Z per-proof OS key). META pins it by SHA-256 `57b257a0…3df6e0`; the Rust
  side derives the key from hm96's label and checks the digest; the verifier refuses any other key specification at parse.
  Never a witness: with the key in the prover's hands after commitment, M_k'·y = b ⊕ x' is 256 linear equations in 1,279
  unknowns, so a committed `b ‖ c` opens to any x' (red-team-hm96's demo). Negative `leaf_key_witness_refused`: a circuit whose
  META declares the key a prover witness, or pins another key, is refused at load. Hiding with the pinned key is N·2^-192
  outside a 2^-64 fraction of keys (the common-reference-string step of hm96 section 3, red-team F2), about 2^-170 at our
  ~2^22 leaves per proof; the formal ZK proof carries that setup step. A per-proof public key bound before the root would
  remove it and still satisfy F6, if wanted in M1;
- a test checks the target's name, salt size and key digest against `verity.commitments.hm96` (skips until PR #88 is on
  main; passes against its branch).

**Serving rows.** What the circuit proves per row, once switched: the inner `sha256/row/v1` digest (constant-midstate prefix),
3 compressions for c, the XOR network `b = x ⊕ M·y` (135,803 XORs for the pinned key, no AND); public `b ‖ c`, 64 B per row
where the Digest region has 32 B today. Per 4 KB row 1,543,328 ANDs against 697,872 (keyed BLAKE3), 2.21× (salted-leaves'
table). One key per tree for the rows too.

**Trees.** PR #83 binds frame-v3 roots: the lowering's leaf maps and every captured IR input set are frame-v3, and core's
`Hm96Sha256` wraps vllm-v1 only. M0 keeps frame-v3 and needs the frame-v3 variant salted-leaves offered (the frame-v3 leaf over
`tree_leaf(key, b ‖ c)` under schema `hm96-sha256/v1`); salted-leaves is final, so the request went to the coordinator.
Production serving commits vllm-v1 position leaves (salted-leaves' correction), so binding vllm-v1 trees in this statement is
an M1/M2 item.

**For the formal ZK plan.** With salts from the OS, the leaf hiding needs no PRG assumption (only the pinned key's setup step). The masks, Reed–Solomon
padding and sumcheck masks are small (a 2^14-bit mask slot per block, t_pad rows per level): drawing them from the OS too
would make the whole simulator argument statistical, with no ChaCha20 step, at negligible cost. Worth deciding with
flock-soundness before M1 fixes the tape.

## hm96-sha512/v1 Merkle leaves (M0 item; 2908d078, cf4e4830)

- **Built:** `flock_merkle::hm96`, core's leaf checked against `vectors_sha512.json`. `HashKind::Hm96Sha512` sets
  `merkle_hash` = 3. Every opening carries `opened_salts` (192 B per opened row, after the paths).
- **Salts:** `zk_hooks::SaltTape` draws from getrandom, or from an injected seed's ChaCha20 stream in a test harness only. The
  level-0 salts are drawn once per session for both reps.
- **Device:** `hm96_finish_leaves`, the per-tree salts from the host callback, the opened salts in the proof writer.
- **Checked:** negative `opened_salt_altered`. GPU selftests pass every case on fused RMSNorm, RoPE and SiLU
  (r20260927-012544-d134, RTX A6000; no L40S in stock).
- **Cost:** on the same A6000, SiLU at 128 rows goes from 1.19 s to 2.33 s end to end (+96%). Proofs grow 13% per rep
  (778,521 → 879,753 B). Runs r20260927-020146-d89a (b3baabd8) and r20260927-015700-5b99 (cf4e4830).
  - About 670 MB of OS salts per proof at m = 33 dominate: drawing, copying and uploading them.
  - Asked the coordinator (`note:20260927T0215Z-handoff-from-flock-netlist`) whether to expand the salts on the device
    from a per-proof OS seed.
- **Salt source changed (Daniel approved, 02:21Z; b32e1a7b).** This reverses the 20:55Z choice ("salts straight from the OS").
  - The salts are now a ChaCha20 expansion of a fresh 256-bit getrandom key per proof. Leaf i of tree `id` is blocks 3i to 3i+2
    under nonce `id`. Level 0 is id 0 for both reps, and every later tree takes a fresh id.
  - The key is never reused, never written anywhere, and zeroed on drop: Rust `LeafSalts`, the FFI copy, and the C++ guard.
  - The device expands the salts inside `hm96_finish_leaves`, so none cross PCIe. The host recomputes only the opened ones.
  - The pinned `salt_source` records it, and the proof format is unchanged.
  - Checks: `chacha20_block` matches RFC 7539; CPU selftest 26/26.
  - Red-team note: `lanes/red-team-hm96/20260927T0235Z-handoff-from-flock-netlist.md`.
- **Cap raised to $80 total** (02:21Z); it covers the multi-table glue statement. Order: serving row leaf, attention, then
  multi-table. Descriptor format sent early: `lanes/private-recursion/20260927T0240Z-handoff-from-flock-netlist.md`.

## Backlog (queued)

- **Serving row leaf on frame-v3-sha512 + hm96 (next).** SHA-512 compression slots in place of BLAKE3, an hm96 finishing
  unit, per-row salts in the prover's file, `b ‖ c` public, native frame-v3-sha512 leaves and roots.
  - The statement format change also carries the program digest, the partition digest and the unit indices
    (`internal/commitments-decisions-routing.md` §1). The serving roots binding the partition digest waits for the
    re-baseline.
- **In-circuit attention (M0 acceptance).**
- **Multi-table statements with private glue** (private-recursion's spec): estimate sent
  (`note:20260927T0155Z-handoff-from-flock-netlist`); after attention.
- **Hidden-message mode** (`note:20260927T0020Z-handoff-from-private-recursion`): at its pace.

## Batched, serialized sessions (Daniel, locked 2026-09-27; DESIGN.md §11.1 on PR #89): what M1/M2 changes in the coin plumbing

No M0 change. Against today's session layer:
- **Many tables per session:** `SessionConfig.tables`, one `Commit` carrying every table's root before the link points, and
  a per-table replay already exist; the circuit statement uses one table today.
- **Per-table coin streams:** M0 derives every coin from one session-wide request counter (`coin_seed::coins(key, g, n)`,
  `g` recorded per round). That counter serializes requests through one server. M1: derive per (table, rep, stream,
  round) from the one step-0 seed, domain-separated, so co-located coin-server instances on different machines need no
  shared counter, and replay needs no `g`. The reps' independent coins (2^-97.8 squared) come from the rep in the index.
- **Each coin checked before answering:** M0 reveals the seed only in the verdict, and the prover checks afterwards. The
  single-rewind simulator needs every prover machine to check each revealed coin against the step-0 commitment before
  sending its next message. So the commitment has to be to the schedule with per-round openings that hide unopened rounds:
  a per-stream key would reveal that stream's future coins. Candidate: a SHA-512 tree over hiding per-round leaves (HM96,
  or salted SHA-512), with each coin response carrying its leaf opening. To be specified with flock-soundness.
- **Statement fixed before the first coin:** the hello (every table's Σ) and the one `Commit` (every root) precede any coin.
  The rule that no coin is released before its round's bytes are recorded becomes per stream (retained bytes, M0), not a
  cross-machine barrier.
- **Co-located coin servers:** server state is already per stream; a coin-server instance per datacenter opens its tables'
  streams from the one committed schedule, and the verdict joins the per-table records.

## For the formal ZK plan (flock-soundness; M1/M2 spec, no M0 scope change)

What M0 exposes for a formalizable M1 masking spec:
- **Randomness tape.** Masks and padding come from `ProverRng` = ChaCha20 keyed by the 256-bit `ProverSeed`, independent streams
  `(purpose, index)` (`STREAM_MASK` 1, `STREAM_PAD` 2; word position 8·index). Leaf salts (128 B each) come straight from
  the OS; the leaf key is the statement's constant. A simulator's tape is these streams plus the salts.
- **Mask placement.** Per block, one 2^14-bit region of free cells (A = B = I) at a pinned position, apart from forced-zero padding;
  the zerocheck/lincheck claim points are fully random (reach every cell); the public region claims fix Boolean coordinates outside
  the mask region (they reveal only public data).
- **Hooks** (`zk_hooks::Hooks`): sumcheck-round message hook (`+ρ·g`), `t_pad` per Ligerito level, claim-point permutation,
  mask-slot fill, `zk` in the identity. The M1 spec must pin, per message: the mask distribution (uniform over the free cells and the
  t_pad ≥ queries padding rows; masking polynomials' degree and support), where it enters (each sumcheck round's univariate, the
  ring-switch `s_hat_v`, each Ligerito level's opened rows and final vector, the claim values), and the simulator (the verifier's
  coins fixed at step 0 by the seed commitment; leaves by HM96 openings).
- **Coins.** Step-0 seed commitment + `verity.randomness` derivation, replayable from the record (above); HM96 is the target commitment.
