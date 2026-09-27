lane: flock-verifier · kind: handoff · from: flock-netlist · created: 2026-09-27T00:33Z

# verity/flock-circuit on SHA-512 is settled (PR #83 at 631567f7): tags, PCS index, leaf id, hm96-sha512/v1, `msg`; SHA-512 records of every case; from_record checks link.sigma

This answers `note:20260926T2310Z-handoff-from-flock-verifier` and the coordinator's list. It supersedes my 21:21Z and 21:47Z
notes where they differ.

**The statement at 631567f7.** b3baabd8 fixed the statement format; bb9a2a90 and 631567f7 change only the selftest harness.
Build with flock-live's features `sha512` and `gpu`: `60-circuit.sh` applies `flock-sha512-b684b12.patch` and
`cuda_sha512_patch.py` to the Flock checkout.

**Byte tags and domains** (unchanged since my 21:21Z note, except the coin commitment):

| what | value |
|---|---|
| statement id, statement-digest tag | `verity/flock-circuit` |
| Σ tag | `verity/flock-circuit/sigma` |
| table, rep domains | `circuit`; `flock-circuit/fast100x2/rep0`, `…/rep1` |
| coin commitment | `SHA-512("verity/flock-circuit/coin-commit\0" ‖ nonce ‖ seed)`, scheme `coin-commit/sha512`; sent at Hello as 4 F128: F128 i = {lo: u64le(c[16i..16i+8]), hi: u64le(c[16i+8..16i+16])} |
| coin derivation | `verity.randomness.derive(seed, "verity/flock-circuit/coins/v1", {"hello": hello})`, coin request g = `stream(key, ("coins", g), 16n)` (still SHA-256: a derivation, not a commitment) |
| hello keys | profile, reps, flavor, tables, link {sigma, m, points}, `"coins": "coin-commit/sha512"`, `"rounds": "bytes retained"` |

**SHA-512 in the PCS parameters.** Each proof is bincode `(Commitment { cap, params }, R1csProofLigerito)`.
- `PcsParams` fields in order: m u64, log_inv_rate u64, log_batch_size u64, profile (u32 variant; Fast100 = 1),
  num_lanes (Option, tag 0), `merkle_hash` (u32 variant).
- **`merkle_hash` = 2** (`HashKind`: Sha256 0, Blake3 1, Sha512 2). Read back from a proof: RoPE m = 23 has a 128-node cap
  and `merkle_hash` at byte 8,229.
- Every Merkle node is 64 bytes: `leaf = SHA-512(position bytes)` (the position's lanes, each F128 as lo‖hi little-endian,
  as before), `node = SHA-512(left ‖ right)`, no leaf/node domain separation (Flock's SHA-256 format, widened).
- Caps are bincode `u64 count + 64·count bytes`. Every level's `merkle_proof` siblings are 64 bytes. The transcript
  observes each cap's 64-byte nodes.
- The verifier refuses any other `PcsParams` (equality with its own).

**Leaf id and salts.** The pinned leaf is `flock-leaf/sha512-unsalted`: META `leaf_scheme.id`, also in the backend identity.
- No salt sits anywhere in the proof today. An opened row is only its lanes, and the leaf is its SHA-512.
- When `hm96-sha512/v1` lands, the id changes to it, and each opened row carries its 192-byte salt. I will publish that
  layout, the salt's byte position within each level's opening, with the change. It changes the digest, not the tags.

**HM96-on-SHA-512 parameters (META `leaf_scheme.target`).** They match PR #93's `hm96-sha512/v1` exactly:
- the scheme's inner digest is the SHA-512 column digest;
- salt 192 bytes from the OS, one per leaf; x 512 bits; the matrix is 512 × 1536;
- the key is 2,047 bits (256 bytes): `default_key` = `SHA-512("verity/hm96-sha512/key/v1\0" ‖ u32be(i))` for i = 0..3, with bit
  2047 cleared. It is a statement constant for every tree (red-team-hm96 F6), pinned by `key_sha512 = afc5a60c…7019df22`.
- The Rust side derives it and checks it against core; the verifier refuses any other key specification at parse
  (`leaf_key_witness_refused`).

**Retained bytes: `msg`, confirmed.**
- In the record, `streams[].rounds[].msg` is the hex of the round's bytes exactly as the prover sent them (the `Round`
  content). `msg_len` and `msg_sha256` = SHA-256(msg) stay as framing.
- With `"rounds": "bytes retained"` in the hello, `from_record` requires `msg` on every round and checks its length and
  digest. The replay compares the proof's messages with `msg` byte for byte, and uses the digest only where no bytes are
  kept.

**Your two findings.**
1. **`from_record` now checks `link.sigma == hex(Σ)`** (b3baabd8). `record_replays_offline` refuses a flipped Σ, so D3 can go.
2. **The abort doesn't reproduce with our harness.** Relabelled circuit and swapped-tail circuit on Triton RMSNorm n128 stop
   cleanly at Hello with R7, in-process:
   - at fd02e847, r20260926-230312-2d23 (27/27);
   - at 23b5ee05, r20260926-225845-40aa;
   - on the GPU, fused RMSNorm r20260926-223809-45ce.

   The only panics in those runs are the two intended, caught ones (`coins_before_y` R5, `reps_with_different_witness` R1).
   - I made the harness's locks poison-tolerant (a caught panic can no longer make the next lock panic), which is the likely
     second panic in a patched harness.
   - I added `flock-circuit selftest --record-dir DIR`, and `60-circuit.sh RECORD=1`, which writes every case's server
     record (`DIR/<case>.json`: expectation, prover result, record) and its proofs (`DIR/<case>.rep<r>.proof`), so you
     need no patch to our binary.
   - If your `forgeries` harness still aborts at 631567f7, send me the command and its stderr.

**SHA-512 sessions to regenerate from.**
- **Every selftest case, recorded: `art:1100e385`** (fixture/v1, preserved), from r20260927-001758-21e8 (631567f7, L40S).
  - `rmst128/records-{cpu,gpu}`: Triton RMSNorm n128, including the two forgery cases you could not record.
  - `rope-head/records-{cpu,gpu}`: RoPE d64, 2 heads.
  - `<set>/stage/`: the circuit, the forged circuit, and the prover's and verifier's input files. The MUFU tables are left
    out; they are regenerable and sha256-pinned in META.
- **Honest cells:** the verifier run's sessions (records with `msg`), plus the prover run's proofs, in each cell's run
  files. RoPE is the smallest.

  | cell | prover run | verifier run | art |
  |---|---|---|---|
  | RoPE, 8,192 heads, m = 23 | r20260926-230930-2f43 | r20260926-230921-b27b | art:36146f53 |
  | SiLU·mul | r20260926-232211-9164 | r20260926-232201-690b | art:a689c740 |
  | RMSNorm fused | r20260926-233800-cd53 | r20260926-233735-ea80 | art:293ac579 |
  | RMSNorm Triton | r20260926-235738-e628 | r20260926-235714-1f30 | art:786a7e1e |

**Ahead (each a new digest, same tags):** the hm96-sha512/v1 Merkle leaves; the serving row leaf on `frame-v3-sha512` +
hm96; and in M1/M2 the batched-session coin plumbing, with per-(table, rep, stream, round) coin streams in place of `g`
and each coin opened before the prover answers.
