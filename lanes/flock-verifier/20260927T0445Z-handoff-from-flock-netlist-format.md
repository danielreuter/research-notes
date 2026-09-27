---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: flock-verifier · kind: handoff · from: flock-netlist · created: 2026-09-27T04:45Z · status: final · repo: danielreuter/verity ·
origin: PR #83 @ eb90718f (in the store bundle until the branch is pushed)

# `verity/flock-circuit`'s new format: SHA-512 digests, hm96-sha512 serving rows, the unit draw, the partition field

This is the format your #85 follows. It is fixed at `eb90718f`: CPU selftest 31 of 31, including both draw cases. A GPU
selftest is running on L40S. It changes three things from `631567f7`:
- serving rows are `hm96-sha512/row/v1` leaves proved in the circuit (BLAKE3 is gone);
- every identity and binding digest is SHA-512;
- the unit draw is live.

## 1. Tags

| tag | value |
|---|---|
| `TAG`, META `statement` | `verity/flock-circuit` |
| META `scheme`; `row_schema` | `frame-v3-sha512/hm96-sha512`; `hm96-sha512/row/v1` |
| Merkle leaves of the proof | `hm96-sha512/v1` (`HashKind::Hm96Sha512`, index 3), openings carry 192-byte salts |
| public file format; circuit hash key | `flock-circuit-inputs`; `circuit_sha512` |
| `Hello` | as `631567f7` plus `"digests":"sha512"`: `{"coins":"coin-commit/sha512","digests":"sha512","flavor":"rs","link":{…,"sigma":hex(64)},"profile":"fast100","reps":2,"rounds":"bytes retained","tables":["circuit"]}` |
| identity `hashes` | `frame_v3_tree: "sha512 (frame-v3-sha512)"`, `row_leaf_in_circuit: "hm96-sha512/row/v1 over sha512/row/v1"`, plus `seed_injection: false` in a proving build |

## 2. Digests (all SHA-512)

- **Circuit pin.** `SHA-512(circuit file)`, lowercase hex. `serve --pin` takes it, and the header's `circuit_sha512` names it.
- **Public digest.** `SHA-512(compact-sorted-JSON(header with rows := false) ‖ public bytes)`.
  - The public bytes are every row's `b ‖ c` (128 bytes per instance and port, instance-major, ports in order), then every
    output word (u16 LE).
  - For a drawn statement (§5) the header is the drawn one, and the public bytes are the whole registered population's.
- **Statement digest.** `SHA-512(TAG ‖ circuit SHA-512 ‖ compact-sorted-JSON(identity) ‖ le64[n, blocks_real, nbl, m, k_log,
  pin, |regions|, G] ‖ le64|Δ_A| ‖ Δ_A pairs (le32, le32) ‖ le64|Δ_B| ‖ Δ_B pairs)`.
  - `D_b3` and the row key are gone.
  - Flock's own 32-byte statement slot (the R1CS digest its round 0 absorbs, `Binding::R1cs`) is the digest's first 32
    bytes. The whole digest is bound through Σ.
- **Σ.** `SHA-512("verity/flock-circuit/sigma" ‖ circuit SHA-512 ‖ statement digest ‖ public digest)`, 64 bytes. It is sent
  in `Hello`, recorded as `link.sigma`, and committed as root_F.
- **Record** (`SessionConfig::sha512_digests`; other statements keep `_sha256`). Each digest is SHA-512 of the same bytes as
  before, under a `_sha512` key:

  | record field | replaces |
  |---|---|
  | `link.root_f_sha512` | `link.root_f_sha256` |
  | `link.root_b_sha512.<t>` | `link.root_b_sha256.<t>` |
  | `link.publics_sha512.<t>` | `link.publics_sha256.<t>` |
  | `link_sha512` | `link_sha256` (the same bytes as your S14) |
  | `streams[i].root_sha512` | `streams[i].root_sha256` |
  | `streams[i].rounds[k].msg_sha512` | `streams[i].rounds[k].msg_sha256` (`msg` retained) |
  | `proof_sha512[j] = {stream, sha512, bytes}` | `proof_sha256[j] = {stream, sha256, bytes}` |

  The coin commitment is unchanged: `coin-commit/sha512`. The coin derivation stays SHA-256, per your §7.2.

## 3. The statement

**Rows.** For each port with row bytes `R` (a multiple of 128) and `words = R/2`:
- `x = SHA-512(sha512_row_prefix(role 1, word_bits 16, words) ‖ row)`;
- `b = x XOR M(key) y` and `c = SHA-512(salt_prefix ‖ y)` for the row's private 192-byte salt `y`;
- the key is `hm96-sha512/v1`'s `default_key`.

The frame leaf is `leaf(dom, i, "hm96-sha512/row/v1", tree_leaf(key, b ‖ c))`, with `tree_leaf = SHA-512(leaf_prefix(key) ‖
b ‖ c)`. The frame is frame-v3 with SHA-512 in place of SHA-256 (the same framing, 64-byte domain ids and nodes). Output
leaves are `u16` words under SHA-512 domains. The padding instance has zero rows and zero salts, so its `b ‖ c` is
`x(0-row) ‖ SHA-512(salt_prefix ‖ 0^192)`. It is pinned in META `dummy.bc`, and the verifier checks it natively.

**Slot types** (all `flock-ir-unit/v2`, in the file as `CIRCUIT <name>` sections).

| slot | size | inputs → outputs | what it computes |
|---|---|---|---|
| `sha512x3` | 2^18 | `cv0, msg0, cv1, msg1, cv2, msg2` (512/1024 bits each) → `out0..2` (512 each) | three independent compressions; words are LE bit lists, a block's bytes are big-endian per word |
| `hm96` | 2^18 | `cv, pad, y` (512 / 1024 / 1536 bits) → `bc` (1024 bits) | the padding compression `x = F(cv, pad)`, then `b ‖ c` in byte-string bit order (bit `t` = bit `t & 7` of byte `t >> 3`) |
| `unit` | 2^unit_log | | the template's unit |
| stages, lookups | | | as before |
| `mask` | 2^14 | | as before |

**Layout.**
- Per VU, port `p`'s compressions are numbered `off_p + k` over the ports in order, three per `sha512x3` slot (slot
  `idx / 3`, sub `idx % 3`); `per_vu[sha512x3] = ceil(total / 3)`.
- The `sha512x3` range is *packed*: `packed: true`, aligned to one slot, spanning `count` slots. Every other range is
  aligned to its power-of-two span.
- There are `per_vu[hm96] = next_pow2(ports)` hm96 slots per VU; slot `g · P + p` is VU `g`'s port `p`.

**Δ, besides the constants' pin wiring.**
- *Row wires.* These are META `wires`' first entries. The verifier derives them from the ports and refuses a META that
  differs:
  - compression `k`'s `cv` ← compression `k−1`'s `out`;
  - hm96 slot `p`'s `cv` ← the row's last compression's `out`.
- *Constants.* Each is "both" copies of the pin (bit 1) or of the unit range's first slot's forced-zero row `useful`
  (bit 0):
  - compression 0's `cv` = the midstate after the prefix block;
  - hm96 `pad` = the padding block `0x80 ‖ 0 ‖ be128(8 (128 + R))`, as big-endian message words.
- *Unit leaf wiring.* Leaf bit `t` of the u16 word at row byte `B` copies the message bit of byte `B + t/8`, bit `t % 8`:
  compression `B / 128`, word `o / 8`, bit `56 − 8 (o % 8) + (t % 8)` with `o = B % 128`.

**META.** The verifier recomputes `rows[p] = {prefix, midstate (8 × 16 hex), pad (hex)}` and refuses a mismatch.
`row_key_sha512 = SHA-512(default_key)`.

**Regions.**
- `Digest(p)`, one per port: the hm96 range's `bc` output group, with free bits `[0, 10)` plus the log2 G slot bits above
  the port's. Its value is the VUs' `b ‖ c`, in VU order; a padding VU's is the pinned dummy.
- `Out` is unchanged. There are no `Params` or `CvIn` regions.

## 4. The public file

- **Header.** `units = {"vus_per_block": G, "units_per_vu": U, "indices": [global unit index per instance, ascending], "blocks":
  [indices in chunks of G]}`. `frame_v3.frame = "frame-v3-sha512"`, `frame_v3.row_key_sha512`.
- **Body.**
  - The prover's file has the rows (u16 LE, ports in order), then every salt (192 bytes, instance-major, ports in order).
  - Both files then have every `b ‖ c` (128 bytes), then every output word.
  - `serve` refuses a file with rows. Staging writes both files from one salt draw.

## 5. The unit draw (your §7.3, live)

- **The flow.** A new request `Register` (wire tag 10) comes before `Hello`, and a new response `Draw(json)` (tag 6).
  - A server with a draw law (`serve --draw subset:K` or `bernoulli:NUM/DEN`) draws over the registered population, the
    staged public file's `n` units at positions `[0, N)`.
  - It uses the exact `uniform`, `subset` and `bernoulli` on OS bytes, as your spec gives them (`w = ceil((bitlen(n) +
    64) / 8)` big-endian bytes; partial Fisher–Yates).
  - It then rebuilds its statement for the drawn units and answers `Draw` with the canonical object. It answers
    `Draw("null")` when it draws nothing, and it refuses a second `Register`, or a `Register` after `Hello`.
- **The drawn statement.** Both sides derive it from the population file and the draw:
  - instance `i` is population position `units[i]`;
  - the header is the population's plus `unit_draw` (the object), `instances = K`, `population = N`, and `units` with the
    drawn units' global indices;
  - the public digest covers that header and the population's public bytes, so the frame-v3 roots stay the population's
    and are recomputed over all N leaves;
  - the Digest and Out region values are the drawn units'.
- **The record and the checks.**
  - The record keeps `unit_draw`: the object, or null.
  - `from_record` checks U1 (canonical equality with the statement's) and U2. `check_public` checks U3: `instances` equals
    the number of drawn units.
- **Selftest cases.**
  - `unit_draw_session`: a draw of 1 of 4 is accepted live and replays offline. It is refused under the population's
    statement at S2, since Σ covers the draw, and an altered draw is refused at U1.
  - `unit_draw_ignored_refused`: a prover that ignores the draw is refused at `Hello` (R7).

## 6. The partition field

META `partition = {"rule": "flock-circuit/unit-cover/v0", "digest": hex(64)}`, with digest `SHA-512(rule ‖ 0x00 ‖
canon(unit cover))`. This is `verity/partition/v1`'s shape: when cross-call-check lands it in core, the rule becomes
`verity/partition/v1` and the object becomes §2's. The header's `units.indices` are global unit indices in §2's order.
META `program_digests` is still core's `program_digest` (SHA-256), because core defines that digest.

## Not changed

- The Merkle trees, their openings and salts (`hm96-sha512/v1` at every Ligerito level) are unchanged since `b32e1a7b`.
- C1 is at `e2190ca3`.
- The lookup tables' pins in META are still SHA-256. `ir_lower` defines them for every IR statement; say if you need
  SHA-512 pins for them.
