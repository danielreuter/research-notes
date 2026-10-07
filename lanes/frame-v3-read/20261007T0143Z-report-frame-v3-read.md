---
id: frame-v3-read/20261007T0143Z-report-frame-v3-read
campaign: proofs
lane: frame-v3-read
kind: report
status: done
repo: danielreuter/verity
origin: bc-4314efeb (worker for @proofs, launched by bc-7f347b4b)
---

# FrameV3Read_v1 and Hm96Sha512Leaf_v1 in gates (PoUW direct path, step 1)

Step 1 of `note:proofs/20261006T1940Z-draft-units-to-inner-layout` (§5) is done. It is branch `cursor/frame-v3-read-95d4` off main
`e7b5caa89`, head `cdd3502c9ea9b4bdf18dfe1575809e12cdd79029`, pushed, with four commits. It changes nothing under
`backends/flock/`, `catalog/` or `verity/protocols/`, adds no SHA-256 id and pins no program digest. The circuit-check
reports are `art:ab779a801b927abedb1d3c14d317ae9123d5c3ed4e1b4e5d5cf86a1573a077b5`.

## What it adds (`verity/primitives/commitments/gates/`)

- `FrameV3Read_v1{D, SCHEMA}` (`frame_v3.py`):
  - Signature: `(root, domain, value: Digest, pos: Array<D, Value<1>>, path: Array<D, Digest>) -> Value<1>`.
  - It is 1 iff `path` opens `value` at `pos` in the depth-D dense frame-v3-sha512 tree of domain id `domain`, matching
    `merkle._message` byte for byte. `Digest` is SHA-512's eight words LSB first, with bytes big-endian.
  - It needs SCHEMA as well as D: the leaf hashes the schema and the hidden rank. The value is fixed at 64 bytes.
  - Its parts are their own traced Definitions, one node per unit: `FrameV3Leaf_v1{B, SCHEMA}`, `FrameV3Node_v1{B}` and
    `LmsEqual_v1{N=64}`.
  - The minimal-length uint is handled by one layout per length, selected bit by bit. That costs an AND per moved value bit
    and nothing per moved constant.
- `Hm96Sha512Leaf_v1` (`hm96.py`):
  - Signature: `(x: Digest, y: Array<24, Word>) -> (b, c, leaf)` under the pinned key.
  - `b = x XOR M_key·y` uses 400,193 XORs. `c = SHA-512(salt_prefix ‖ y)` and `leaf = SHA-512(leaf_prefix ‖ b ‖ c)` each
    start from a constant midstate.
- The sidecar `frame_v3.circuit-check.py` binds `FrameV3Read_v1{D=1,SCHEMA='hm96-sha512/row/v2'}`, and
  `circuit_check.targets.load_registries` imports both modules.

## Gates

| | ANDs | gates |
|---|---|---|
| `FrameV3Leaf_v1` B = 1 / 2 (row-seg) / 3 | 110,125 / 110,922 / 111,683 | |
| `FrameV3Node_v1` B = 1 / 2 | 166,475 / 167,630 | |
| `Hm96Sha512Leaf_v1` | 215,597 | 1,438,301 |
| `FrameV3Read_v1{D=1, row/v2}` | 277,111 | 1,659,755 |
| `FrameV3Read_v1{D=13, row-seg/v1}` (D_A) | 2,280,228 | 13,658,304 |
| `FrameV3Read_v1{D=17, row/v2}` (D_B) | 2,951,509 | 17,668,695 |

A leaf is 2 compressions and a node 3: the domain id is a value, so each message's first block is computed in gates.

## Pins, controls, runs

- Tests: `test_boolean_frame_v3.py` has 9 (4 fast, 5 slow) and `test_boolean_hm96.py` has 5 (2 fast, 3 slow). All 14 passed
  in 230 s.
- What they pin:
  - The `frame_v3/vectors_sha512.json` trees: every position of the six trees with D ≥ 1, and every hiding leaf.
  - `hm96/vectors_sha512.json`'s 8 leaves, and the key's masks and salt digests (13 cases).
  - The library at one-, two- and three-byte uints, including a D = 17 read of a 2^16 + 1-leaf `MerkleTree`.
- Wrong-position control: `pos ^ 1`, the high bit, and `pos ^ 2^16` at D = 17. Each gives 0.
- Wrong-salt control: one flipped salt bit, or the other row's salt. Each gives a leaf that differs from the vector's and that
  the read refuses.
- Further controls: a wrong root, sibling, value or domain id gives 0, and malformed bindings are refused.
- Suites, all `--quick --fresh`:
  - commitments: 403 passed.
  - circuit_check: 85 passed, 2 xfailed.
  - `tests/test_repository.py`: 14 passed.

## circuit-check

All six runs are ok with 0 failures:

| target | gates | time | max RSS | warnings |
|---|---|---|---|---|
| D = 1 read | 1,659,755 | 824 s | 7.4 GB | `redundant-gates/ir` 6,991 |
| D = 13 read | 13,658,304 | 1,306 s | 8.6 GB | none; partition and redundant gates are over budget, so unchecked |
| D = 17 read | 17,668,695 | 1,553 s | 9.0 GB | none; partition and redundant gates are over budget, so unchecked |
| `Hm96Sha512Leaf_v1` | 1,438,301 | 1,429 s | 7.0 GB | 12 `Not` |
| `FrameV3Leaf_v1{B=1}` | 659,843 | 648 s | 9.5 GB | 6 `Not` |
| `FrameV3Node_v1{B=1}` | 998,376 | 801 s | 8.2 GB | 6 `Not` |

- Q_call is clean wherever it is checked (≤ 4M gates).
- The 6 `Not` per SHA-512 message appear in every message, most likely from the shared gadget.
- The D = 1 read's other 6,985 are values the node computes again from the domain id, after the leaf has computed them:
  schedule words of the first block, about 970 ANDs per node (0.6%). The PR leaves them alone.

## Step 3 fit (`Pc8TileServed`)

- **The A side, the B side and the window read fit.** `served_commit` builds them as dense frame-v3-sha512 trees, with
  `hm96-sha512/row-seg/v1`, `row/v2` and `row/v2` leaves.
- **Two conditions for step 2:**
  - Each side domain's count must lie in (2^(D−1), 2^D], since a fixed-D read refuses a shallower tree. Pads can't be
    opened, so no `pos < count` check is needed.
  - The domain id must not depend on the hidden entry. Today the port is `f"{e}/{side}"`; one public domain per window and
    side fixes that.
- **The `-h3` tile tree doesn't fit.** `HASH_FORMATS["h3"]` is `blake3-s256` (frame-b3s) over 32-byte keyed-BLAKE3 tile
  leaves (`pearl-c/h1/leaf`), so its leaves aren't SHA-512. `Pc8TileHidden` outputs h0's TurboSHAKE128 digest, which is
  neither. Neither `FrameV3Read_v1` nor `MerkleRead_v1` reads that tree, and no parameter changes that.
- **What the third read needs.** The recommendation is a statement tile tree in frame-v3-sha512, as `rows_bench`'s `t.hm96`
  commits it: `hm96-sha512/row/v2` leaves over the 32-byte digests. `FrameV3Read_v1{D_t, 'hm96-sha512/row/v2'}` then serves
  it unchanged. The value chain is the digest, then a `sha512/row/v2` row digest in gates (one compression; not yet a
  Definition), then `Hm96Sha512Leaf_v1`.
- **The alternative** is frame-b3s in gates: keyed-BLAKE3 Definitions, plus a BLAKE3 tile digest in `Pc8TileHidden`, which
  is a `verity/protocols/` change.

## Not done

- Step 3's pieces: the `sha512/row/v2` digest of a 32-byte row in gates, and the value-width static that a 32-byte frame
  value would need.
- The redundant-gate warnings stay as they are.
- `check` isn't run here: there is no pod.
