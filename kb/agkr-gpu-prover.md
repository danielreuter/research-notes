# A-GKR GPU prover (backends/gkr/gpu): where the time goes and what moved it

Written by lane agkr-fp8 (2026-09-24), H100 80GB HBM3, fp8-hopper at 4096 VUs (196608 units x 448 columns, 10 lookup
tables, T_OP n=24). Every change below left the proof bytes identical (sha256 of `Proof.to_bytes` unchanged, also for
bf16-hopper), which is the check to run for any prover-only speedup: `06_ab.sh` in `lanes/agkr-fp8/evidence/pod-scripts/`.

## Profile after the hill-climb (warm prove 0.432 s, was 0.626 s)
- lookup 0.196 s: the graphed LogUp (`logup_packed._FSGraphExt` + device Fiat-Shamir `fs_cuda.fs_step`). About 18.6k kernels
  of ~7.7 us each inside CUDA graphs: latency-bound, not bandwidth-bound (the big levels cost ~4 ms of HBM traffic in all).
  `fs_step` (serial SHA-256 on one thread, ~4 compressions) is ~14 us per round. Only kernel fusion inside a round would
  move this; the transcript order is fixed.
- arith 0.097 s: phase 1 per-round host work + one sync per round (36 rounds); GPU kernels ~39 ms.
- open_acc 0.061 s (rank1_add over the 4.2 GB int64 `Acc.a`, scatter_terms 29 ms), open_wq 0.038 s, mults 0.011 s.

## What was slow and why (fixes on lane/agkr-fp8)
- `field.eq_table` doubled with one `ext_mul_chunked` launch pair per variable (66 calls/prove): one `eq_table_vars`
  launch instead (-60 ms).
- `seg_query_values` / `eval_wires` evaluated every linear form term by term (~3 launches per term per form, ~1500
  launches): cached per-circuit plans, one gather per term position (mults 28 -> 11 ms, witness_wires 12 -> 4.7 ms).
- Query tuples were built twice (multiplicities, then lookup): kept between the passes on >= 48 GB parts (-30 ms).
- Phase-2 `sumcheck_prod` on <= 4096 rows: ~20 launches + 3 syncs per round; numpy on the host is faster.
- Two `add_input_claim` per segment share the copy point, so they are one rank-1 update (one pass over the segment).
- Packed phase 1 recomputed `eq_points(gamma[:i-1], r)` from scratch every round and built int8 fold matrices the
  Triton path never reads.
- Serialization: per-coordinate `int.to_bytes` in `Proof.to_bytes` / `absorb_exts`; numpy `astype('<u4')` is identical.

## Gotchas
- `torch.tensor(list, device='cuda')` from pageable memory is a sync point; in per-round loops it costs a bubble each.
- The 4090 (24 GB) needs `VERITY_GPU_OPEN_ROWS` row-blocked `open_w_qc_eval` (automatic below 40 GB) and
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; FP64 is 1/64 rate there, so any float64 limb matmul path hurts.

## One merged lookup table (statement change; agkr-nvf4 18ab232e for NVFP4, lane/agkr-fp8 d5d80e0b for E4M3)
- The LogUp cost was ten trees' round latencies. `gpu/v2/export.py::merge_tables` rewrites circuit.txt: every table becomes one
  row-listed `LK` with rows `(tag 2^20 + key, tag, outs.., 0..)`, and every query becomes `(key + tag 2^20, tag, outs.., 0..)`. That is
  sound because the tag column pins the match, and the keys stay unique because every source key is below 2^20. The Rust verifier
  needs no change. The soundness bound did not move (2^-130.19, encoding_opening dominant). FP8 ada: 261819 rows x 8 columns, 150
  queries/unit, slots 2881 -> 727.
- After the merge the lookup is bandwidth-bound, and the query-tuple work dominates: 29.5M x 8 int64 tuples = 1.8 GiB.
  agkr-nvf4's `leaf_q` (one Triton pass for `z - Σ β^k v_k`) plus the gate_eval query values took 4090 t_lookup 0.187 -> 0.083 s.
  Holding the tuples for the lookup pass when they fit in a tenth of the device took it to 0.060 s.
- Row-listed tables used argsort + searchsorted multiplicities; a cached key -> row map (keys < 2^26) replaces them.
- The standard negatives (public word +-1, sign, exponent) all fail at the epilogue assertions, so they never exercise the lookup.
  For a lookup statement change, use `12_lookup_neg.sh`: tamper one unit column read by a query, patch in the honest
  multiplicities, and run a prover copy whose "fractional sum is not zero" self-check is a no-op. Both verifiers must reject at
  `LogUp LK level 0: final check`.
- 4090 fp8-ada at 4096 VUs, t.total 1.130 -> 0.666 s (prover only, same bytes) -> 0.490 s (merged statement).

## NVFP4 on the RTX 5090 after the merge (lane agkr-nvf4, 2026-09-25; recorded 0.1905 -> 0.1388 s)
- Final dev buckets at 4096 VUs (0.138 s): arith 49 ms, open 32 ms (acc 17, wq 12.5), lookup 28 ms, witness 12.5 + wires 3.1
  ms, commit 4.6 ms, mults 3.2 ms, to_bytes 4 ms. The two GKR layers' phase 1 (~30 ms) and the 2^24 LogUp tree (~26 ms, the
  largest levels 5–8 ms each) are the floor for small changes.
- Same-bytes changes that moved it, in ms:
  - pinned non-blocking H2D for every per-round operand (`field._h2d`, `gkr_packed._inputs`): pageable `torch.tensor(...,
    device=cuda)` waits for the stream.
  - LogUp leaves built straight into the graph's static buffers, and the leaf level in one kernel: 49 -> 40.5.
  - L2-friendly grid order (the dimension that shares data runs fastest): scatter_terms 21.7 -> 19.2, gate_eval 10 -> 7.2.
    rank1_add got worse under the same change.
  - opening `w` by `eq_rows_dot`: 17.1 -> 14.5.
  - SIMT encoder radix4 with `min_blocks_per_sm=2`: the 70k-row open encode 5.1 -> 3.6.
  - `row_code_dot` split 64: 4.5 -> 3.9.
  - multiplicities in one Triton pass (`kernels.lookup_mults`): 5.7 -> 3.2.
  - wires by gate_eval CSRs: 9.4 -> 3.1.
  - opening w / qc serialized once from one D2H: 5.9 + 5.5 -> 2.4 + 3.8.
- What did not help:
  - L2-sized row chunks between the encoder and `row_code_dot`: slower at every size; the encode is not DRAM-bound.
  - int32 padded layer inputs: memory only.
  - logup_ext_ip BLOCK_K / num_warps: 128 / 4 is best, the others spill.
  - vectorizing add_lookup_claim's term loop: it is 1.5 ms of Python.
- The pod host jitters: a record at 90c21455 gave reps of 0.155–0.175 s, and the Rust verifier also slowed to 0.20–0.24 s.
  When the verifier time rises with the prover time, rerun instead of reading the change into it.
- Red-team (red-team-lk, 2026-09-25, art:ca49b2f8 art:9a6280c5 art:319062b4 art:5419ef15): the merge, the nvf4 depth-1 flatten, the
  epilogue t drop, BOOL_QUADRATIC and PAIRED all PASS. Soundness holds for any key: the tag is its own constant column and the shift
  is injective mod p. The 2^20 bound only matters to the prover's first-column multiplicity search. The harness is
  `backends/gkr/tools/red_team_lk.py` (lane/red-team-lk), with subcommands `static-merge`, `static-nvf4`, `selftest`,
  `forge [--control]` and `audit`. Its evidence kind is `redteam-findings/v1`.
- Tag-collision forgeries need the cheating prover (no self-check, first-column multiplicities). On nvf4, a tag-stripped LK moves
  the rejection from LogUp to assertions. On fp8, every range-checked column also feeds another query (ALIGN4, a second R5), so
  no single-cell forgery isolates the tag; `audit` lists each forgery's LK misses with and without the tag.
- Gotcha: tree 3be6a35f (fp8) under Triton 3.4 (5090 image) raises a CompilationError in `packed/kernels_triton.py` until it
  gets b7cec878's 5-line constexpr-global fix.

## Verifying a rewritten statement independently (verify-po, 2026-09-25; `lanes/verify-po/evidence/pod-scripts/`)
- Regenerate on a CPU pod with the producer's commit and compare byte for byte. `gpu.v2.export circuits --model M` (fp8) merges
  by default from 3be6a35f on, and `--no-merge` must reproduce the earlier verified unmerged statement exactly. For nvf4 use
  `gpu.nvf4.circuit export`. A `git archive` of backends/{direct,gkr,numerical,shared} + packages/verity is ~36 MB.
- Check the rewrite with main's `gpu/circuit.parse_circuit`, not the producer's code: `23-lk-merge-check.py` (merged vs
  unmerged: queries = key + tag·2^20, bijective tag map, LK = tagged union as a multiset) and `27-nvf4-rewrite-check.py`
  (BOOL_QUADRATIC / PAIRED vs the 2b25df7f circuit).
  - Tags and shifts appear as coefficients on the constant-one column (col 0), so fold one-column terms into the constant.
  - Product wire indices shift after a rewrite, so compare products by content.
- nvf4 statements carry `public s t f` in chain.txt, which main's verifier (pre-679697a4) cannot parse. Build lane/agkr-nvf4
  3c769c6d's verifier, which is main plus the optional public line.
- Prover-only records reuse the same proof bytes, so cmp every proof and statement file against the verified tree as well.

## Operand binding and circuit shape (agkr-bound, 2026-09-25)
- Every A-GKR unit circuit is product-depth 1. Nonlinearity comes from committed hint columns and LogUp.

  | circuit | products | columns |
  |---|---|---|
  | bf16-ampere | 26 | 264 |
  | fp8-hopper | 37 | 448 |
  | fp4-nvf4 | 215 | 485 |

  `depth_circuit` in a result counts GKR/LogUp layers, not product depth. An in-circuit hash therefore either commits its
  S-box intermediates, or needs product depth > 1, which the fast CUDA prover has never proved.
- Operands bound as public inputs (lane/agkr-bound, art:559147e1; PROTOCOL.md §16):
  - `bind.txt`, `instances.txt`, `x.bin`, `w.bin`;
  - relation name `R+bound`: circuit files pinned under R in `pins.txt`, instance digests pinned under `R+bound` in
    `verifier/src/instances.rs`;
  - plain `R` refuses a statement that has a `bind.txt`.
  It costs about +0–15% t.total on A100 (1 rep each). The user ruled it NOT the full relation: commit x, W and y and bind the commitments
  in-proof (coordinator 0507Z).
- `gpu/v2/export.merge_tables` is torch-free from 2994bd25, so the circuit-pin pytest can regenerate the merged-LK E4M3 lines.
  To test torch-freeness, set `sys.modules['torch'] = None` before `runpy.run_module`.
- `layers()` makes every product-depth layer span ALL wires (pass-through gates), and the assertion layer spans every assert.
  Prover work therefore grows with units × 2^ceil(log2 nwires) per layer. An in-circuit Poseidon2 (852 rows per permutation,
  2 per unit) takes BF16 from 290 to about 3,700 wires (8× per layer) and from 264 to about 1,970 committed columns. The
  estimate is 4–8× t.total (coordinator handoff 0550Z).

## Hashing row digests in-proof (lane agkr-bound, 2026-09-25)
- Commit scaffold (lane tip ≥ 83582436):
  - `gpu/commit.py` publishes per-VU x-row/W-column digests as 32 epilogue limbs; `verifier/src/commitments.rs`
    (+ `vllm_v1.rs`) rebuilds the frame-v3 or vllm-v1 trees natively and compares the roots.
  - Relations: `R+sha256`, `R+blake3`, `R+vllm-v1`.
  - Until a circuit binds the digest columns no circuit is pinned, so a cell reports `failed` by design and verifies only
    with `--allow-any-circuit --require-commitment`.
  - `--allow-unpinned-commitment` waives only a missing root pin.
- In-field SHA-256, Longfellow flat layout (`tools/sha256_flat.py`, BabyBear, 16-bit-half adder checks):
  - per compression: 6,657 columns, 30,272 products, 36,929 wires, depth 5 (the BF16 unit is 290 wires);
  - it can't run on the GPU prover at all (dense layers spanning every wire);
  - Rust CPU prover, EPYC 7742 with 13 threads: B = 64 takes 3.26 s, B = 4,096 takes 106.7 s (arith 101.6 s, 9.1 GB RSS,
    5.5 MB proof), about 0.7 µs per wire;
  - a 4,096-VU BF16 batch hashes about 393k compressions (96 per VU), so this is about 10^4 s on CPU, arithmetic-bound
    rather than commitment-bound.
- Flock's `hash_throughput` bench needs `HASH_BENCH_LOG2S` ≥ 8. Its fast x86 path needs AVX-512 + VPCLMULQDQ, which
  RunPod A100 hosts (EPYC 7742, Zen 2) lack.
- Same-pod reference (vy-agkr-bound2, 13 threads): the Rust CPU prover takes 361.5 s on the BF16 4,096-VU batch
  (`run_measure_vu.sh`, FIELD=babybear). The survey's "54 s" came from a different box.
- Flock b684b12 (portable path, 13 threads, one compression per input):
  - SHA-256 5.00 s and BLAKE3 2.18 s at 2^18;
  - single-threaded, 56.9 s and 26.3 s.
- The prime side of a bit link (`tools/link_stub.py`: 512 bits per unit, booleanity, recomposition) at 393,216 units:
  - CPU 138.3 s (+38%);
  - A100 0.55 s warm as its own segment (+64%);
  - packing k = 2 / 4 is slower on CPU (173 / 563 s).
- The CUDA prover takes a single-segment `prover.Instance([Segment(...)], None)` built from any circuit text; see
  `lanes/agkr-bound/evidence/pod-scripts/15_link_gpu.py`.
- Unit wires that aren't products are inputs in wire order, so new columns can be appended after the last wire without
  renumbering anything. `tools/link_stub.extend_unit(text, cols, bits)` uses this to commit an operand column's bits
  in-unit (booleanity + recomposition).
  - On BF16 under R+sha256 with 32 × 16 bits, the unit grows from 264 cols / 290 wires to 776 / 1,314, still 2 layers.
  - A100 prove goes from 0.776 to 1.199 s (+55%; a separate third segment costs +71%). The Rust verifier accepts with
    `--allow-any-circuit` in 3.38 s.
  - `alt_alt_bits` (an altered operand with its own bits) is accepted: only the cross-field link can close it.
- The dense GF(2^128) check for N = 2.0e8 bits (eq(r, i) doubling + BabyBear^6 byte-table coefficients + inner
  product) costs 0.875 s on A100 (torch, unfused: an upper bound) and about 0.85 s on EPYC 7742 with 13 threads
  (PCLMUL, `lanes/agkr-bound/evidence/pod-scripts/21_eq_cpu.c`).
- A 3,968-element second-round Ligero proof (u_t) costs 0.03 s and 471 KB: the fixed query overhead dominates.
- The same dense check fused in Triton on A100 costs 0.066 s per challenge point: eq 0.023 s and coefficients + inner
  product 0.044 s.
  - The coefficients c_i = Σ_t ρ_t bit_t(eq_i) are an int8 tensor-core matmul: bits[B, 128] × ρ in 7-bit limbs, with
    int32 accumulation and block 256 (block 512 spills registers and takes 1.15 s). The script is
    `lanes/agkr-bound/evidence/pod-scripts/24_dense_tc.py`.
  - A byte-table gather kernel is 5× slower (0.345 s): it does 96 L2 gathers per bit.
  - eq is memory-bound, writing 16 B × 2^m.
- The link's integer identity S_t = 2u_t + z_t per bit plane rejects a single altered link bit: about half the 128
  planes lose parity, and the ρ-combination is nonzero (`25_gap_dense.py`).
- The operand bits the unit consumes map one-to-one onto the row-leaf value bits. The generator orders units VU-major
  (u = v·K/k + s), and unit s reads words k·s … k·s + k − 1 of x row v and of W column v, each word exactly once. The
  bit link therefore needs no dedupe.
- `sha256/row/v1` puts the value after one 64-byte prefix block, so the value is block-aligned.
- A-GKR opens every residual claim as one materialised functional `acc.a` (`prover.Acc`, `ligero.prove_open`). A
  non-tensor linear check, such as the link's c_i, is one more `a[pos] += c` term: no sumcheck, and no extra opening.
  - On the BF16 in-unit proof on A100 this adds 0.21 s to prove (1.20 → 1.41 s) and 0.16 s to the Python verify, in an
    unoptimised wrapper (`lanes/agkr-bound/evidence/pod-scripts/28_link_dense.py`).
- The sigma-form bit link (red team S1) is built in A-GKR (lane/agkr-bound 78b1a62e: `gpu/link.py`,
  `verifier/src/link.rs`, PROTOCOL.md §17). It is NON_ZK_PROOF only: the 256 plane sums sigma_t go in the clear.
  - One GF(2^256) point: m = log2ceil(n_pos) whole transcript digests (`challenge_bytes`), drawn after the GKR messages
    and root_b; the link runs before the functional's rho's.
  - Lambda_F is derived by both verifiers from the extended unit circuit and checked bijective; the circuit must
    carry booleanity + recomposition for every `link.b{col}.{i}`.
  - The binary side is a STAND-IN: root_b = SHA-256(TAG, "/root-b-standin/", commitment.txt), y from x.bin / w.bin
    (the Rust verifier checks they hash to the public row digests).
  - Cost on A100 BF16 4,096 VUs: prove 1.20 -> 1.54 s (+0.34 s), Python verify 1.25 -> 1.58 s, Rust verify
    3.42 -> 4.67 s (+0.44 s derivation at load), proof +6,144 B (art:bd3d8b2c).
- Triton kernels defined inside a function resolve `tl` through the module globals: bind `triton`, `tl` with
  `global` in the lazy loader or the jit fails with "NameError: tl is not defined".
- GF(2^256) plane sums / dense terms on A100: build the bit matrix from int32 words, reduce with int8 tensor-core dots
  (rows [z; b; 0] @ e for sums, e @ 7-bit limbs of rho^t for the term), and fuse passes that share the point. A
  cross-thread `tl.sum` over the cell axis or six strided read-modify-writes cost 2-4x more. eq-table levels by
  nibble tables (64 x 16 x 32 B per level) are 1.4x faster than byte tables (32 x 256 x 32 B, L2-resident); the first
  compile takes ~25 s.
