---
lane: ligerito-pcs-fast
kind: report
created: 2026-09-23T18:20Z
status: open
---

CHECKPOINT b96dac0 (20:25Z) — since 9a04c3e: verifier rejects non-canonical words (14df4af, red-team 19:05Z NIT); Boolean-tail claims
contract one 2^s-row block (64a9eeb, relation's chain-row claims 18 → 7 ms at 2^30); **ZK hooks** — `commit(t_pad=, zk=)` column padding in
every round incl. the streamed commit + recompute, `ybar_i` in the proof, sparse round-1 claims (226bdb2, 9d13ac7; +20 ms at 2^29; `t_pad = 0`
/ no sparse = unchanged bytes); **streaming Merkle leaves on Ligero's register-resident Blake3 compress** (b96dac0: 24.6 → 9.9 ms per
128-column group at 2^30, same digests) → 2^30 default 0.182 → 0.159 s, S 0.237 → 0.219 s. Fused `pcs.prove` still byte-identical to proto
7bc2fdd. Tests on the pod: **101 passed** (`pytest backends/direct/ligerito`). Table at HEAD (median of 3, `pts.sh f5`):

~~~
N = 2^29 (4090)  prover  commit  rec+sc  serial.  proof MB  verify  peak GiB | N = 2^30  prover  commit           rec+sc  proof MB  peak GiB
default          0.079   0.044   0.025   0.009    0.581     0.075*  11.55    |           0.159   0.122 (stream)   0.030   0.680     12.50
F                0.054   0.023   0.022   0.007    0.790     0.72*    7.02    |           0.089   0.050            0.030   0.910     14.03
S                0.102   0.048   0.042   0.010    0.508     0.047   15.74    |           0.219   0.141 (stream)   0.068   0.542     22.00
B-pow2           0.069   0.025   0.033   0.010    0.646     0.068    8.08    |           0.113   0.054            0.047   0.692     16.15
~~~
(*host-numpy Python verifier, noisy.) Ratios vs 0.17 s at 2^29: default 0.46×, F 0.32×, S 0.60×, B-pow2 0.41×; at 2^30 default 0.94×,
S 1.29×, B-pow2 0.66×. Artifacts: `f5` row of `## Artifacts`.

CHECKPOINT 9a04c3e (20:00Z) — **the commit-first multi-claim API ligerito-relation asked for exists and is transcript-identical to
their `pcs_open` / `pcs_verify` (prove.py @ 3592bd0): relation's own `pcs_verify` accepts my `open()` proofs** (pod cross-check: their
package from `lane/ligerito-relation` in one process, my prover in another; m = 1 / 3 / 5 claims, streamed and kept codeword, 3–4 rounds;
tampered value → their `Reject`). How to swap it in: `## For ligerito-relation`. Also since cf1843f: **streaming round-1 commit** (a5ab250,
already merged by relation) → **every point now runs at 2^30 on the 24 GB 4090, S included (22.0 GiB peak)**; eq tables fully on the device
and a batched eq contraction (4 claims at 2^29: +9 ms over 1 claim, was +31 ms); design's `params.py` merged (1a674a2, design is FINAL) with
the red team's `t_pad` fix and `pcs.soundness_log2` / `pcs.dims_for` / `target_log2` guards (`## For red-team-ligerito`). Fused `pcs.prove`
transcript and bytes still byte-identical to proto 7bc2fdd. Tests on the pod: **92 passed** (`pytest backends/direct/ligerito`: proto's 14
incl. negatives, 58 in `fast_test.py`, design's params + ref tests). Artifacts (bench-result/v1, this table): `## Artifacts`. One B-pow2
n = 29 proof + z + negative for ligerito-verify-rs in `evidence/` (`## For ligerito-verify-rs`).

~~~
N = 2^29 (4090)  prover  commit  rec+sc  serial.  proof MB  verify  peak GiB | N = 2^30  prover  commit           rec+sc  proof MB  peak GiB
default before   0.297   0.089   0.192   0.013    0.581     0.045   15.09    | before    OOM (proto: unsupported on 24 GB)
default now      0.077   0.044   0.023   0.008    0.581     0.17*   11.55    | now       0.182   0.146 (stream)   0.029   0.680     12.50
F       before   0.263   0.046   0.204   0.011    0.790     0.297   10.16    | before    0.430   0.092            0.325   0.911     —
F       now      0.053   0.023   0.021   0.007    0.790     0.48*    7.02    | now       0.089   0.050            0.030   0.910     14.03
S       before   OOM on this pod (proto on its pod: 0.524 s / 22.6 GiB)      | before    OOM
S       now      0.101   0.048   0.041   0.009    0.508     0.043   15.74    | now       0.237   0.162 (stream)   0.067   0.542     22.00
B-pow2  now      0.069   0.025   0.033   0.010    0.646     0.062    8.08    | now       0.111   0.054            0.045   0.692     16.15
today's fp8-ada Ligero prover on this 4090 (whole relation, local coins): 0.17 s; its encode+commit of the 2^29 cells: 0.034 s
~~~
(median of 3, Fiat–Shamir, `prover_wall_untimed_s` within 3 ms; *verify = the unchanged host-numpy Python verifier, noisy.) Ratios vs 0.17 s at
2^29: default 0.45×, F 0.31×, S 0.59×, B-pow2 0.41×. At 2^30 "stream" = the codeword never materialised: `commit_r1_stream` 113–126 ms +
`commit_r1_recompute` 34–35 ms (the |S_1| opened rows re-evaluated from the message, N·|S_1| MACs) — the price of 24 GB; with the codeword kept
(H100 / relation choice) 2^30 default would be ≈ 0.10 s. Multi-claim (commit-first, m = 4 claims, the relation's shape): B-pow2 2^29 0.077 s,
2^30 0.125 s (codeword kept) / 0.109 s, 0.189 s with `stream=True`.

CHECKPOINT cf1843f (18:40Z) — items 1 + 2 landed together (dabc3e2) and the round-1 encoder step A rewritten (cf1843f). **PCS prover at
N = 2^29 on the 4090 (same pod, median of 3, Fiat–Shamir): default 0.297 → 0.082 s, F 0.263 → 0.055 s, S OOM → 0.104 s, B-pow2
0.073 s** — all below today's 0.17 s local fp8-ada prover (0.48× / 0.32× / 0.61× / 0.43×). Proof bytes unchanged (0.581 / 0.790 / 0.508 MB;
B-pow2 0.646 MB). **Transcripts and proof bytes are byte-identical to proto 7bc2fdd for the same coins** (tested: `pcs.prove` vs
`pcs.prove_reference`, Fiat–Shamir and LocalCoins, 5 dims incl. per-round rates). Tests on the pod: 30 passed (proto's 14 incl. the 8
negatives + 16 new in `proto/fast_test.py`). Table below; `## Interface` has the device ext-field primitives for ligerito-sumcheck.
Read design's FINAL + coordinator §9 18:30Z ("implement set B as the default"): the sumcheck lane's layout is pow2 (`S = 16` padding), so
the consumer today is B's **pow2 equivalent** (`our_params(fp8-ada, L=5, rate_log2=(1,2,2,2,2), radix3=False)`: k' = 6,4,4,3,3,
|S| = 312,191,193,194,195, 722 KiB incl. relation) — measured as point "B" and recommended to ligerito-relation; radix-3 is not implemented
(no consumer produces a 3×2^k tall layout today; the Rust verifier is pow2 too). Next: streaming commit (codeword in 16/32-column groups,
incremental Blake3 leaves, opened rows recomputed) for S/default at 2^30 on 24 GB, then the 2^30 table.
CHECKPOINT 7bc2fdd (18:20Z) — read proto's report (all), wave-b brief §1 + §9, ligerito brief, leaf-campaign §0 + 17:30Z HARD RULE; worktree
`~/projects/verity-main-wt/ligerito-pcs-fast` on `lane/ligerito-pcs-fast` from `lane/ligerito-proto` 7bc2fdd. Pod `vy-ligerito-pcs-fast` =
nscusnbi2ow79c, RTX 4090 24564 MiB **reference part** (host AMD EPYC 75F3, US-NC-1, $0.74/h, created 18:07Z; `[machines.vy-ligerito-pcs-fast]`),
venv312 torch 2.6.0+cu124 + cupy 14.2 + blake3. Same-pod BEFORE run of proto 7bc2fdd (tests + default/F/S at 2^29 and 2^30).

# ligerito-pcs-fast — make the Ligerito PCS prover competitive with today's Ligero prover on the 4090

## Per-N prover table (4090 reference part, EPYC 75F3 host; seconds, median of 3; Fiat–Shamir; "before" = proto 7bc2fdd on the same pod)

Points: default = |S| 192, rate 1/4, k' 7(8),4,4,4 · F = k' 7,5,5, rates 1,2,2, |S| 311,191,193 · S = k' 6,4,4,3,3, rates 2,4,4,4,4,
|S| 191,143,143,143,144 · B = B-pow2: k' 6,4,4,3,3, rates 1,2,2,2,2, |S| 312,191,193,194,195.

~~~
N = 2^29        prover   commit(enc+merkle)   recursion+sumcheck   serial.   proof MB   verify   peak GiB
default before  0.297    0.089 (0.063+0.026)  0.192                0.013     0.581      0.045    15.09
default now     0.082    0.044 (0.033+0.011)  0.030                0.008     0.581      0.052    11.65
F       before  0.263    0.046 (0.089*+0.013) 0.204                0.011     0.790      0.297    10.16
F       now     0.055    0.023 (0.018+0.006)  0.025                0.006     0.790      0.07-0.6  7.12
S       before  OOM on this pod (cupy pool vs torch cache; proto measured 0.524 s / 22.6 GiB on its pod)
S       now     0.104    0.048 (0.035+0.013)  0.047                0.008     0.508      0.040    15.94
B       now     0.073    0.025 (0.019+0.007)  0.038                0.009     0.646      0.061     8.27
today's fp8-ada prover (whole relation, local coins): 0.17 s; its encode+commit of the same cells 0.034 s
~~~
(*proto's `commit_r1_encode` bucket for F included the first-touch allocation.) Verify is the unchanged Python verifier (host numpy,
noisy). Where the time goes now (default 2^29): encode 33 ms (step B is at DRAM bandwidth: 16 GiB in 20 ms; step A 13 ms), Merkle 11 ms,
host bookkeeping 10 ms (round-1 T = 1 sumcheck, α batching, row claims, O(T) coefficient updates), round-1 eq contraction 7 ms, openings 6 ms,
recursion contractions 5 ms, round-1 fold 3 ms, device sumcheck 2 ms.

## What changed (all in `backends/direct/ligerito/proto/`; `transcript.py` untouched)

* `device.py` (new): cupy RawModule kernels launched on the current torch stream, exact mod-p in u32/u64 registers, **no fp64**:
  `contract_geom` (u[p, t] = Σ_r A[p, r] η_t^r: tiled SIMT GEMM whose right factor — the RS generator rows of the opened positions — is
  generated on the fly, one Montgomery multiply per tile element), `contract_planes` (eq tensor as 6 planes), `fold_ext` (y = M̃ r̄ over
  F_{p^6}), `eq_table`, and `DeviceSumcheck` (`build_tables` + `sc_step`: the (T, C, 6) tables live on the device, one single-block launch
  per sumcheck variable = fold with the previous challenge + the next message, 72 B back).
* `pcs.py`: `prove` = the device prover; `prove_reference` = proto's prover (the byte-identity oracle and the CPU path; `prove` falls back
  to it without CUDA). Round-1 commit via Ligero's fused `commit_gpu` (same tree bytes); multi-path siblings gathered with one device
  gather per level group and one copy; round i−1's codeword + tree freed right after its opening.
* `ntt_gpu.py`: step A of the 4-step as `NC = 2^rate` twisted coset NTTs of the NS = R/n1 message rows (input read once into registers,
  8 columns per CTA = full 32-B sectors, two register butterfly phases around one XOR-swizzled shared tile, post-twiddle w_n^{j1 k'}
  generated on the fly instead of the n1 × n2 table). Same (n1, n2) split and position order → bit-exact with the generic kernel.
* `bench.py`: `--prover fast|reference`, `prover_wall_untimed_s` (no per-bucket syncs; within 2 ms of the timed wall).

## Interface

`transcript.py` is FROZEN (unchanged). `pcs.prove(f, z, dims, timer=None, coins=None)` / `pcs.verify(proof, z, v=None, coins=None)` keep
their signatures; the proof bytes and the transcript are byte-identical to proto 7bc2fdd for the same coins. `pcs.prove_reference` = the
prototype prover (same signature).

**Device F_{p^6} primitives (offered to ligerito-sumcheck; `proto/device.py`)** — F_p[x]/(x^6 − 31), coords in [0, p), u32:
~~~
device.EXT_CUDA          # CUDA source string: __device__ mulm/addm/subm/fold (u64 -> < 2^61 lazy fold), mont_mul (a * w' with w' in
                         #   Montgomery form), ext_mul(a, b, c) / ext_add / ext_sub on u32[6]; paste into your RawModule source
                         #   (it is %-formatted: substitute %(pinv)d = device.PINV, or use device.ext_source())
device.eq_table(z, device) -> (6, 2^k) int32 planes       # eq(z, x) for z (k, 6); x little-endian (bit 0 = z[0])
device.contract_planes(A (P, R) int32, Bp (6, R)) -> (P, 6) int64   # Σ_r A[p, r] Bp[:, r] mod p (unreduced < 2^63; % P)
device.contract_geom(A (P, R) int32, etas (T,) int) -> (P, T) int64 # Σ_r A[p, r] eta_t^r (RS evaluation at base-field points)
device.fold_ext(M (6, C, R) int32, rbar (C, 6)) -> (6, R) int32     # Σ_c M~[c] rbar[c] in F_{p^6}
device.DeviceSumcheck(...)                                          # the PCS column sumcheck (tables (T, C, 6) on the device)
~~~

**Commit-first / multi-claim (9a04c3e, `proto/pcs.py`)** — for a relation whose evaluation points depend on the commitment:
~~~
com  = pcs.commit(f, dims, timer=None, stream=None, target_log2=None, t_pad=0)  # no transcript effect; the caller absorbs com.root
vals = pcs.evaluate(com, points)            # optional: (m, 6) = f~(points[j]); caches the round-1 contractions for open()
pf   = pcs.open(com, points, values, coins, timer=None)   # values (m, 6) or None; coins hold root_1 + the caller's transcript
ok, why = pcs.verify_open(pf, points, values, coins, target_log2=None, t_pad=0)
pcs.prove_commit_first(f, points, dims) / pcs.verify(pf, points)   # standalone (prefix: header+order, root_1, v)
pcs.soundness_log2(dims, t_pad=0) -> float        # params.py union for THIS committed shape
pcs.dims_for(n, kprime, rates, target_log2=-128.0, t_pad=0) -> Dims   # |S_i| for this shape (params.allocate_queries + top-up)
device.contract_eq(A (P, 2^k) int32, zs (m, k, 6)) -> (m, P, 6) int64   # up to 4 eq tensors per pass over A
device.eq_table(z, device, out=None)                                   # now fully on the device (0.28 ms at k = 22)
~~~
`open`'s transcript: absorb `z` (m·n ext, `_ext_bytes`), `beta <- challenge(b"beta", m)` (always, also m = 1), round-1 claim
Σ_j β_j v_j with m eq terms of coefficient β_j, then rounds 1..L exactly as `prove`. Values are NOT absorbed (the caller's transcript binds
them). Proofs from `open` carry `order = "commit-first"` and `v` (m, 6) (`Proof.to_bytes` header gains `"order"` and `"claims"`).

## For ligerito-relation

**Swap-in (your `pcs_commit` / `pcs_open` / `pcs_verify` in prove.py → mine, same transcript, cross-verified by your `pcs_verify`):**
~~~
from .proto import pcs
com = pcs.commit(w, dims, timer=tm, stream=None)          # instead of pcs_commit(w, dims, tm); com.root = your root1
coins.absorb(b"root", com.root)                           # unchanged: your transcript binds root_1 where proof.py says
...                                                       # your zero-check / rows / shift on the same coins
pf = pcs.open(com, points, values, coins, timer=tm)       # instead of pcs_open(...); values asserted = f~(points) (prover-side)
del com                                                   # frees the codeword + tree
pcs_proof = PcsProof(pf.roots, pf.sumcheck, [o.rows for o in pf.opens], [o.siblings for o in pf.opens], pf.final_y)
splits = pf.splits                                        # what your pcs_verify takes
# verifier side: pcs.verify_open(pf, points, values, coins) is your pcs_verify's transcript (or keep yours; both accept)
~~~
**Which point:** derive |S| per committed shape — `dims = pcs.dims_for(n, [6, 4, 4, 3, 3], [1, 2, 2, 2, 2], -128.0)` gives
|S| = 311, 192, 192, 195, 196 (2^-128.0008); B-pow2 `[312, 191, 193, 194, 195]` (2^-128.026, params' own pow2 optimum) is equally fine and
is what I measured. **Never set B's radix-3 |S| on your pow2 shape (2^-99.2)**. **Under ZK padding pass `t_pad`** (`dims_for(..., t_pad=256)`
→ |S| = 311, 192, 193, 197, 217; every point in my table misses 2^-128 with t_pad = 256: B-pow2 2^-105, S 2^-125). Pass
`target_log2` (your PCS share of the budget) to `commit` / `verify_open` to make a wrong shape a hard error.

**Memory (B-pow2, 4 claims, 4090):** the `Commitment` holds, beyond `w` itself (2 GiB at 2^29, 4 GiB at 2^30), the round-1 codeword + tree:
~~~
                    held between commit and open   peak in open (beyond w)   commit+evaluate+open (m = 4)
2^29 stream=False   5.0 GiB                        6.1 GiB                   0.077 s
2^29 stream=True    1.0 GiB                        2.5 GiB                   0.109 s
2^30 stream=False   10.0 GiB                       12.2 GiB                  0.125 s
2^30 stream=True    2.0 GiB                        5.0 GiB                   0.189 s
~~~
`stream=None` (auto) streams only when the PCS alone would not fit; if your zero-check needs the card between `commit` and `open`, pass
`stream=True` (costs +32 ms at 2^29 / +64 ms at 2^30: the |S_1| opened rows are re-evaluated from `w`). `w` must stay alive and unmodified
until `open` returns (the Commitment is a view of it). CUDA only (`commit` raises off-GPU; your host path stays for CPU tests).

**Boolean-tail claims (64a9eeb, your 19:45Z ask):** `contract_eq` detects per claim the longest run of top row coordinates in {0, 1} and
contracts only that `2^s`-row block (any round, not just round 1) — round-1 contraction with your 3 chain-row claims + 1 dense: 9.8 → 4.2 ms
at 2^29, 18.2 → 7.2 ms at 2^30. Same bytes. You can drop `_r1_eq_contract` / `LIGERITO_RELATION_PCS=own`.

**ZK (9d13ac7, your 19:55Z ask — both items, `None`/0 = today's bytes):**
~~~
com = pcs.commit(w, dims, stream=..., zk=zp)              # or t_pad=256; zp = lay.zk_params(...) (its t_pad if enabled)
pf  = pcs.open(com, points, values, coins, sparse=[zk.libra_block_claim(lay, k, gm_k, r_k) for k in (0, 1, 2)])
ok, why = pcs.verify_open(pf, points, values, coins, zk=zp, sparse=<the same 3 triples>, target_log2=...)
dims = pcs.dims_for(n, [6, 4, 4, 3, 3], [1, 2, 2, 2, 2], -128.0, t_pad=256)   # |S| from the PADDED rate (F1): see below
~~~
* **Padding:** every committed column at every round (round 1 base, rounds ≥ 2 per ext plane) gets `t_pad` uniform coefficients
  x^{R_i} .. x^{R_i + t_pad − 1} (ChaCha20, `ligero/mask_sampler.py`, fresh key per commit/round) — added inside the encoder after the
  4-step's pass A (a fused `pad_add` kernel; the streamed commit and the opened-row recompute include it). `ybar_i = Σ_c mu~_i[:, c] rbar_i[c]`
  ((t_pad, 6) per round) goes in the proof (`Proof.ybar`, header `"t_pad"`, appended after `final_y`); verifier row check
  `<U_i[s], rbar_i> − Σ_t eta_s^{R_i + t} ybar_i[t]` = the geom claim / `P_y(eta_s)`. Rejects: wrong t_pad either way, tampered ybar_i
  (each round), non-canonical ybar words.
* **Sparse terms:** `sparse = [(cells (T,) PCS indices, weights (T, 6), value (6,)), ...]` meaning Σ_t w_t f[cells_t] = value; cells may
  be anywhere (grouped per round by column into eq-like terms with a one-hot column part; recursed as a sparse term on the next round's
  indices). Prover asserts each value.
* **Transcript additions (commit-first only)** — mirror these in your `pcs_verify` twin (or call `verify_open`): after `absorb("z", ...)`:
  for each sparse claim `absorb(b"sparse", cells.astype("<u4").tobytes() + _ext_bytes(weights))`; `beta <- challenge(b"beta", m + K)`,
  initial claim Σ_{j<m} β_j v_j + Σ_k β_{m+k} value_k; with padding: `absorb(b"ybar", _ext_bytes(ybar_i))` right after `root_{i+1}` (for the
  last round right after `y`), before `S_i` is drawn. Sparse values are NOT absorbed (like the eq values: your transcript binds them).
* **Cost (4090, B-pow2 → `dims_for(t_pad=256)`, 4 claims of which 3 Boolean-tail + 3 sparse claims of 762 cells, median of 5):**
~~~
                     prove     verify   proof bytes   peak beyond w   soundness    |S|
2^29 plain, kept     0.074 s   0.064    643,590       6.1 GiB         2^-128.03    312,191,193,194,195
2^29 ZK,    kept     0.094 s   0.078    687,858       6.1 GiB         2^-128.02    312,192,193,198,244
2^29 plain, stream   0.107 s   0.066    643,590       2.5 GiB
2^29 ZK,    stream   0.128 s   0.077    690,322       2.5 GiB
2^30 plain, kept     0.125-0.142 s      691,815      12.1 GiB         2^-128.03    312,191,193,194,195
2^30 ZK,    kept     0.137 s   0.148    728,275      12.2 GiB         2^-128.01    311,192,193,197,217
2^30 plain, stream   0.185 s   0.121    691,815       5.0 GiB
2^30 ZK,    stream   0.227 s   0.141    727,571       5.0 GiB
~~~
  ZK ≈ +20 ms prover (+36–44 KB: ybar 5 × 256 × 24 B = 30.7 KB + the re-sized |S|). Note |S| at 2^29 differs from 2^30 under padding
  (the last round is 2^9 rows: rate (512 + 256)/2048) — always call `dims_for` with your actual n.

## For ligerito-zk

Your `## For ligerito-relation` item 4 is in the PCS (9d13ac7): (a) sparse round-1 terms = `open(..., sparse=[zk.libra_block_claim(...)])`,
batched by the same `beta` after the eq claims; (b) per-column padding = `commit(..., zk=zp)` (uses `zp.t_pad` iff `zp.enabled`): the padding
is sampled inside the PCS with your ChaCha sampler (`mask_sampler.sampler_for(device).uniform`), NOT via `zk.pad_columns` (that is host numpy
and would copy f); same math: message `(R_i + t_pad)` coefficients, codeword length unchanged, `ybar_i = mu_i^T rbar_i` in the clear, row
check `+ row_check_rhs` (my `_pad_correction` = your `row_check_rhs` for all opened rows at once). Rounds ≥ 2 pad each of the 6 planes of a
column (so `ybar_i` is an ext combination of ext padding — your `padding_combination` planes branch). `|S_i|`: `pcs.dims_for(..., t_pad)`
(= params.py with t_pad, the red team's F1 union; your `queries_for` gives the per-level rule). Measured cost: +20 ms at 2^29 (`## For
ligerito-relation`, ZK table). Not done by me: the mask rows / Libra masks themselves (yours + relation's), the shift-claim reduction (D-ZK2).

## For ligerito-sumcheck

Unchanged offer (`## Interface`): `device.EXT_CUDA` / `ext_source()` (F_{p^6} mul/add/sub/fold on u32[6], Montgomery helpers), `eq_table`
(now fully on the device), `contract_planes` (any row stride), `contract_eq` (≤ 4 eq tensors per pass, Boolean-tail blocks detected),
`contract_geom`, `fold_ext`, `DeviceSumcheck`. No asks received from you in your notes; nothing of yours calls my kernels yet as far as I see.

## For ligerito-verify-rs

* **Evidence (your 19:05Z ask):** `evidence/b-pow2-n29.{proof,z,json}` + `.proof.neg` (one flipped byte) — my fused `pcs.prove` at B-pow2,
  n = 29, Fiat–Shamir (proto dialect, 646 KB). And your `fixtures/rust/n12_rates234.{proof,z}` through my Python verifier: **accept**
  (dims n = 12, k' 4,3,2, |S| 16×3, rates 2,3,4; one flipped byte → reject "Merkle multi-path of the last round failed").
* **Fused `pcs.prove` bytes / transcript: unchanged** (byte-identical to proto 7bc2fdd; test `test_fast_matches_reference_bytes`).
* **New, only if you verify relation proofs natively:** commit-first proofs (`open`): header adds `"order": "commit-first"`, `"claims": m`,
  `v` is (m, 6); transcript = relation's prefix, then `z` (m·n ext), [K × `sparse`], `beta` (m + K), rounds as fused; with ZK padding header
  adds `"t_pad": t`, L × (t, 6) `ybar` ext words appended after `final_y`, `absorb(b"ybar")` after each `root_{i+1}` (last: after `y`), and
  the row checks subtract Σ_t eta_s^{R_i + t} ybar_i[t] (R_i = 2^{k_i}). The Python reference is `pcs._verify`.
* **Hardening (14df4af) matching yours:** the Python verifier now rejects (not reduces) non-canonical words in the sumcheck messages,
  `final_y`, `v` and `ybar` (red team 19:05Z NIT).

## For red-team-ligerito

* F1/F2 (18:50Z): `params.LigeritoParams.t_pad` (rate (tall + t_pad)/n, ybar bytes), `pcs.soundness_log2(dims, t_pad)` for the committed
  shape, `pcs.dims_for` (|S| per shape), `target_log2` guards in `prove` / `commit` / `verify` / `verify_open` (9a04c3e); `test_params`
  reproduces your numbers (B radix-3 |S| on pow2: 2^-99.19; t_pad = 256 on B: 2^-119.34 fp8 L5). ZK padding now exists in the PCS
  (9d13ac7) — attack it: the pad's ChaCha keys are fresh per round, `ybar_i` is absorbed before `S_i`.
* 19:05Z NIT: done (14df4af) — `_verify` and `claims.verify_column_rounds` reject non-canonical words (`test_non_canonical_words_rejected`,
  incl. your int64-wrap lift). F10/F11 are `ref.py` (design's reference, not on my production path; I have not changed `ref.py`).
* New surface for you: the sparse-claim terms (`pcs._Sparse`) — cells are caller-supplied, distinct, in [0, N); a group with a one-hot
  column part per round.

## Artifacts (bench-result/v1, `research data put --by ligerito-pcs-fast`)

~~~
before (proto 7bc2fdd, same pod):  6e356e2c898f default_29 · 3a6424d27be5 F_29 · 12cd05eef4ef F_30 · 9d9163296356 default_30 (unsupported)
step 1+2 (dabc3e2/cf1843f):        4e4b791e1ad9 default_29 · ace356c86ba2 F_29 · bfdf66c59244 S_29
now (9a04c3e table, 19:55Z):       ceac073615d9 default_29 · 3d7d99ce8906 default_30 · 1a4a1afc1aa3 F_29 · 957ba9da53fc F_30
                                   f24048cdcf05 S_29 · 27dc3748a7a7 S_30 · aed6fdddf02f B_29 · 19217c197a5b B_30
f5 (b96dac0 table, 20:23Z):        3a097ef8742e default_29 · ffafe54fa30d default_30 · 7e456577f693 F_29 · 0c672d0c58e9 F_30
                                   e2cf6c6aa49f S_29 · 7dfd688d4f11 S_30 · 8baa7ac13ede B_29 · e73fcbe6f896 B_30
~~~
(ids are the first 12 hex of `art:<sha256>`; full ids in `research data` under label lane=ligerito-pcs-fast.)

## FINAL (written by the coordinator, 2026-09-23T20:45Z; the lane's agent ended before writing it)

Branch `lane/ligerito-pcs-fast` @ `b96dac0` (pushed to origin; `git status --short` empty at the lane's last report). Pod tests 101/101.
Final table (4090, median of 3, Fiat–Shamir, s): 2^29 default 0.079 · F 0.054 · S 0.102 · B-pow2 0.069; 2^30 default 0.159 (streamed)
· F 0.089 · S 0.219 (streamed, 22.0 GiB, fits 24 GB: the H100 2^30 S run is no longer needed) · B-pow2 0.113. Prototype 7bc2fdd on the
same pod: 2^29 default 0.297, F 0.263; 2^30 only F 0.430. Fused `pcs.prove` byte-identical to the prototype; ZK padding and
sparse-claim hooks change bytes only when enabled (documented in the handoff notes to ligerito-relation / ligerito-verify-rs).

Custody: the lane's 23 artifacts were local-only at its end (remote=0); the coordinator pushed all 23 to R2 at 20:45Z (0 unpushed).
Pod `vy-ligerito-pcs-fast` (nscusnbi2ow79c, $0.74/h, up 18:07Z) terminated by the coordinator at 20:45Z, ~$1.9.

Open (unowned): opened-row recomputation 35-60 ms at 2^30 (near integer throughput); item 4 (two proofs in flight; list-decoding
query allocation, gated on the design lane's soundness note); verifier is still the prototype's Python.
