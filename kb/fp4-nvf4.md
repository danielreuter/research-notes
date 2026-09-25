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

## RTX 5090 numbers (wave-5090-2, EU-RO-1, 4096 VUs, l = 16384, --zk --mode interactive, reps 5, medians of 3+ alternating rounds)
- bare local: p4 0.0404 s (12 rounds), p8 0.0423, p1 0.0727; l = 8192 p4 0.0403. committed (+poseidon2 included-hash,
  d30c32f6 = main + fp4-port 1aa1f00e): p4 0.1550, p8 0.1497 (3.7x bare).
- live, same-DC 8-vCPU CPU verifier: bare p8 t.total_live 0.0683 (p4 0.0764); committed p8 0.1619 (p4 0.1634).
  Every session accepted (152/152 over both verifiers); Rust reverify PASS. Report `lanes/wave-5090-2/*report*`.
- Before lane/wave-5090 b278f508, `bench-vu --verifier` proved fp4-nvf4 sub-batches SEQUENTIALLY whatever `--pipeline`
  said (`fp4/chain.py`: `... and live is None`): live bare was 0.114-0.133 s. b278f508 wires live pipelining as relchain does
  (HELLO window = N, `live.pipeline_factory`, `set_statement` per sub-batch).
- The live tax on the bare cell (0.068 live vs 0.040-0.042 local) is the in-session opening round trip: ~3-4 ms median while
  `live probe` says 0.6-0.8 ms idle; it did NOT change with the verifier's CPU (2 vCPU jobs 2 / jobs 1 / 8 vCPU jobs 8:
  sequential 0.133 / 0.116 / 0.114). At 40 ms per rep, 14 round trips of ~3.5 ms cannot hide; the hashed cell (155 ms) hides them.
- `reverify.py` before lane/wave-5090 04141baf crashed on fp4/chain.py dumps (manifest `relation` is a bare string there).

## GOTCHA: fp4-nvf4+poseidon2 results said `synthetic` / `dev` until lane/fill-consumer 444084d3
`fp4/hashed.py FP4HashedRelation` draws `chain.instances_fp4` (seed 20260922) and uses `chain.instances_digest`, which
is exactly the frozen NVFP4 set, but it labelled the instances `dataset: synthetic, tier: dev`. `bench.tables` rejected
every 5090 column-2 result on dataset + tier alone (manifest, range and seed matched), so the cell stayed empty. From
444084d3 it names `contract.NVFP4_INSTANCES_DATASET` / `_TIER`. Those strings also enter the tree binding digests, so an
`--auth-cache` built before the fix does not match; the Rust pin (`fp4-nvf4+hash`) is unchanged. Results produced before
the fix need an instance-equiv file or a rerun.

## RTX 5090 numbers (fill-consumer, 1b3c7be6 / 444084d3, EU-RO-1 SECURE kjzbulmek8or0z, 4096 VUs, zk interactive, reps 5)
- **l = 8192 beats l = 16384 on both columns** (13 sub-batches). Bare, local: l8192 p8 0.0340-0.0344, l8192 p4 0.0356-0.0367,
  l16384 p8 0.0395-0.0399, l4096 p4 0.044. Committed (included-hash), local: l8192 p8 0.1387-0.1491, l8192 p4 0.147-0.148,
  l4096 p8 0.161-0.164.
- Live on a same-DC cpu3c 16-vCPU verifier (15 jobs): bare l8192 p8 t.total 0.0417-0.0441, t.total_live 0.043-0.045;
  l16384 p8 0.051 / 0.057-0.061. Committed l8192 p8 0.146-0.153. 75/75 fp4 sessions accepted.
  Candidates are in `lanes/verify-night/20260924T0725Z-handoff-from-fill-consumer.md`.

## A-GKR (GKR + LogUp + Ligero, backends/gkr) on fp4-nvf4, RTX 5090 (lane agkr-nvf4, 2026-09-24)
- Circuit: `backends/gkr/gpu/nvf4/circuit.py` compiles B-Ligero's `relation.compile_fp4_unit(chain=True)` onto `GkrCtx`. The
  pins become in-circuit decode from committed operand codes. The statement is the chain endpoints only: c_0 = 0 through
  `init 0` links, and the final FP32 word as three public columns (s, t, f) via the `public s t f` line in chain.txt. That
  needs the multi-public verifier change (lane/agkr-nvf4, +30/-13 in main.rs/verify.rs); main's verifier rejects the line.
- What moved t.total at 4096 VUs (1.04 s -> ~0.22 s): phase-2 `eq_rows_dot` (110 -> 2.5 ms per layer); ALL lookup/range
  tables merged into one tagged row-listed table LK (key + tag·2^20; the LogUp cost is per-tree round latency, so 16 trees
  -> 1 saved ~0.16 s, and even 2^24 + 2^23 -> one 2^25 saved 6 ms); products of depth > 1 commit their deep operand
  (`_flatten`, 418 -> 485 columns, 4 GKR layers -> 2); `torch.compile` on the witness chain step (graphed witness
  28.7 -> 12.1 ms; a cold compile adds ~200 s of untimed warm-up); agkr-fp8's shared prover commits (0.232 -> 0.216 s).
- Record scripts under `research run` must export the env.sh thread caps (see ops-tools.md): without them the same tree
  timed 0.314 s instead of 0.274 s.
- The pod's host-bound phases jitter: back-to-back dev runs of one tree gave medians 0.232 and 0.265 s. Record with 5 reps.
- Final (2026-09-25, lane/agkr-nvf4 @ c97d2ad2): r20260925-015152-d098, t.total 0.1388 s (~1.4e7× against the 1.283e15 FLOP/s
  native peak), 2^-130.19, Rust 5/5. Result art:f277786d…, run-files art:1f0b0b60…; proof 9469288 B, sha ebe7c545.
  - Statement: two more rewrites on top of the merged LK and the depth-1 flatten.
    - BOOL_QUADRATIC: each 1-bit range check is a `b·b = b` product wire, not an R1 query.
    - PAIRED: each pair of R3/R5/R6/R7 queries is one `(x + 2^b y, x, y)` query into a listed PR<b>.
    - Result: 226 -> 166 queries per unit, LK 110613 rows, 700 wires, and the LogUp tree drops 2^25 -> 2^24 leaves
      (t_lookup 40.5 -> 28 ms).
  - The size of the tree is set by units × queries + table rows. At 98304 units the 2^24 boundary is 170 queries per unit,
    so count queries before adding any.
  - The coordinator holds the Table 2 label for statements with rewrites until red-team-lk passes (0050Z). Until then Table 2
    shows the provisional art:49757870 (0.1905 s, 2.5e7×). Prover-side details are in agkr-gpu-prover.md.
