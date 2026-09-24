# fp4-nvf4 (NVFP4 sm_120) and fp4-nvf4+poseidon2

Measured facts and how-tos for the NVFP4 relation and its hashed (committed) composition. Sources inline.

## Pins (Rust `backends/ligero-verify/src/relation.rs` FP4_NVF4)
- bare `fp4-nvf4`: sys_id `a825ba0b...`, m = 1583, table `b597b003...` (fp4-proof lanes).
- hashed `fp4-nvf4+hash`: sys_id `8c6d260c675cad40...`, table `8dad2d28...`, m = 4442, 19 linked rows; fixture
  `fixtures/fp4-nvf4-hash/` (40 VUs, l = 1024, system.bin sha256 `80ac30a9...`). Pinned by lane fp4-decode (6ffa0351),
  reproduced byte for byte on main's leaf interface by fp4-port-2 (lane/fp4-port @ 1aa1f00e; FS non-ZK dumps identical
  to 6ffa0351's, art:3c4d2bbc).
- The v5 header K of a hashed fp4 statement is 1536 (24 steps x 64 E2M1 codes; `check_vu_shape` reads K = 64 per unit)
  although the committed row is 24 x 68 words (4 UE4M3 scale bytes per operand ride along). The tree bindings' K is
  `FP4HashedRelation.vu_words` = 1632.

## How to run (main after lane/fp4-port merges)
- `python -m backends.direct.ligero.run --relation fp4-nvf4+poseidon2 bench-vu --auth included-hash ...` (the `+leaf`
  suffix does not imply `--auth`; `--auth` goes after the subcommand). `--relation fp4-nvf4 ... --auth included-hash` is
  the same. Only the poseidon2 leaf takes the FP4 lane format; `included-hash-shared` is refused.
- Seam: `fp4/hashed.py FP4Format` is the relation's `hash_format`; `hashchain.compose` decodes the operands through it and
  hands `Poseidon2Leaf.with_lanes(fmt)` the 72 nibble elements per column (6 per 24-bit lane, rate lanes 12..15 zero,
  IV `IV(role, 4, 24 x 72)`). `leaf/poseidon2.py LaneFormat` is the protocol.

## RTX 4090 numbers (4096 VUs, l = 16384, --zk --mode interactive, local coins, --pipeline 4)
- fp4-port-2, 1aa1f00e, vy-fp4-port, 3 alternating rounds: hashed 0.2404 / 0.2447 / 0.2363 s, bare 0.0673 / 0.0597 /
  0.0613 s (median ratio 3.9x); all 6 dumps Rust-pinned 7/7 ACCEPT; bench.summary contract ok. Report
  `lanes/fp4-port-2/*report*`.
- fp4-decode-3 (6ffa0351 base d86e014): hashed 0.2617 s, bare 0.0532 s on another 4090.
