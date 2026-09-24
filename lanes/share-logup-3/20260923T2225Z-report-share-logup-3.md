---
lane: share-logup-3
kind: report
created: 2026-09-23T22:25Z
status: final
---

CHECKPOINT 453d7cf4 (23:11Z) [final] FINAL 453d7cf4: fp8-ada+shared p4 0.268 vs bare 0.161/0.157 (1.69x; target 1.3x NOT met, shared device-busy floor 0.213 s > 1.3x bare); +shared DONE for fp8-hopper 0.308 / bf16-hopper 0.512 / bf16-ampere 0.480 (bf16 was 2.84: graph re-capture per pass, fixed 453d7cf4); Rust pins accept all 4 relations' dumps, all shared gates 0 failures; 23 arts remote=1; pod terminated 23:09:51Z ($4.71 pod life, ~$0.68 this lane)
CHECKPOINT 777670ac (22:53Z) [open] 22:55Z fp8-ada p4 5 reps same pod: bare 0.161/0.157 (bracketing), +shared 0.268 (1.69x), +hash 0.373; Rust 13/13. fp8-hopper bare 0.136 / hash 0.355 / shared 0.308. bf16-hopper bare 0.254 / hash 0.774 / shared 2.84 (!: 3.7x unshared, l=16384-specific; profiling). All 4 shared gates 0 failures, Rust pins accept all 4 relations' shared dumps
CHECKPOINT 777670ac (22:44Z) [open] 22:46Z final campaign running (fin.sh): fp8-ada bare 0.158 / hash 0.373 / shared reps 0.309,0.253 (JSON lost to a v6 reader bug, fixed in 777670ac, rerun queued fin2.sh); Rust 13/13 fp8-ada shared; shared gates 0 failures fp8-ada ia, fp8-hopper fs, bf16-ampere fs; bf16-hopper gate + 3 relations' bench/rust in progress
CHECKPOINT 3267219 (22:37Z) [open] fused chainq/fp_lanes kernels: shared p4 0.299->0.281 s (bare 0.153); interleaved G/H pair committed, 13/13 verify; timing it now; bf16-hopper +shared IA gate 0 failures; pins for fp8-hopper/bf16-ampere in progress
CHECKPOINT cfdcf65 (22:19Z) [open] started; worktree lane/share-logup-3 @ cfdcf65 + share-logup-2's uncommitted mm_mod; measuring pipelined pair on the 4090 next
# share-logup-3 — pipelined tile64 row sharing (`fp8-ada+shared`) at --pipeline 4, then the other relations

Worktree `~/projects/verity-main-wt/share-logup-3` on `lane/share-logup-3` @ cfdcf65 (share-logup-2 tip). Pod vy-share-logup-veritor-campaign
(kx69zewzhawgy1, 4090). Carried share-logup-2's uncommitted `mm_mod` (limb-GEMM contraction in `chain.fp_values` / `chain_coefs`) + its test.

## Art ids
All `remote = 1` (checked with `research data sql` before terminating the pod).
* proofs (the four accepted `+shared` rep1 dump sets: fp8-ada 777670ac, fp8-hopper 3ad48e50, bf16-hopper / bf16-ampere 453d7cf4):
  `art:6d2f2832e5e1ae727ebf048cc3f78874d95a4c6f6d0c8bc48c06e5d0bbf8afde` (proof/v1, 484 MB)
* Rust verdicts (`ligero-verify batch`, pinned): `art:276500c50e8996f915118d73fed93747e1fb272589994f4e9898b1e50453887e`
* shared gates (pre-fix `gate_*` + post-fix `gate2_*`): `art:7969ba46e0397a0a8379214e97008314bb1d680ccfc411589d523a7429829983`
* final campaign run files (all logs / JSONs / device profiles / fin*.sh / evidence scripts, dumps excluded):
  `art:6bef72927522a572f2f5a964277e43fc6ec87e70b4b1b2acaf1b5cad2ee8a59a`
* pre-campaign pod files (cfdcf65 measurements, small-tile dumps behind the pins, early gates):
  `art:2a9464a45d3ace86ced41074f91675a4915a20e03ebf4ce5c569a9bf7c3bd9cf`
* bench-result/v1 per table cell: fp8-ada bare `art:4e3642b2d93e2b847f0ef639af9a67150778caa3a5e5016626db844cbe6d4b8e`, bare5
  `art:7e73531d9b08df359c0545f0f36ca77c7e55c78680e53dd33cd03578cac7d074`, bare5b
  `art:ece7a3c2f5a9101dbd26ef527e532155210f8b403dc322dbc3f54db0190ab17f`, hash
  `art:d045ca84b69f78579fae9d7797730a81efdbb56adf06c82c9383c783240ff049`, shared5
  `art:28d0a4d25b034be08c2e93e811a70353d8985e6cc4ab9525c09bca1bb24a08cd`; fp8-hopper bare
  `art:d5f686d98fdb7ee222e53b1ecc2670d8737e787f58079fcfadb597c956d0a4ee`, hash
  `art:b3daecb79fc1cbc36f18a70129809fc357e4c4cbc84e22677febf11e8c9bef35`, shared
  `art:b0d256614c3550bb82f567c6c8a9d385889a5c2ea20ad137770d9c42d85c7665`; bf16-hopper bare
  `art:71b3c116cb180a972e8e926d2218bc1fb201871c2e10c2e8311c344564aa3fca`, bare2
  `art:ec72bde2bffd4df2013c5abcd44dbbde55d669404cbf1fa5a984df913067d498`, hash
  `art:2810f91ff7eff4c7da444a240c253ee0909c7589d59742115c174741f6e02171`, shared (pre-fix, superseded)
  `art:5629f34b0ba8def2e5bcf9fe7de5d8ac802316214e38c7a399795ae8c9b067d9`, shared2
  `art:d18676e5df9d16385895134e42378b7baa8d561549ad29ebc82d291ad54aa1ef`; bf16-ampere bare
  `art:824c61ec44b81d418f02f7a76767e239aedf12bf785ea6ed0caab9bd815336b4`, hash
  `art:d12697ba776eefec6f36f3c62c795ed94eed1cc6f8e90999dea5efeee46af6da`, shared (pre-fix, superseded)
  `art:ad95a4ae7be1514f9062077d7a779dd389222776c1f30c46b1bf9e3227a4bf35`, shared2 (one rep under a concurrent fixture build)
  `art:5f99cc401597c1a6996f365621dd10116c70e56a0409a856d99f145d5b455fc0`, shared3 (clean)
  `art:5d39fdbb016cff015de7bc82a4ad681ee4aa6b3c109cbe62125b84930bd8d4a6`

## Log
* 22:25Z start: brief §0/§1.1/§2/§3, share-logup-2 + share-logup reports, red-team-leaf / red-team-leaf-2 handoffs read (G3: shared + live
  verifier is BLOCKING — coins_h prover-sampled; benches here use local coins only).
* 22:21Z measured at cfdcf65 on the pod (`prof_p4.py`, 4096 VUs, l=16384, interactive non-ZK local coins, p4, median of 6 after 3 warm):
  bare `fp8-ada` **0.154 s**; unshared Poseidon2 (`included-hash`) **0.395 s**; `+shared` **0.299 s** (1.94x). share-logup-2's
  uncommitted `mm_mod` (float64 limb GEMMs via torch.matmul) is exact eagerly on CUDA but makes the pipelined prover fail ("G's
  fingerprints disagree between VUs of one shared row"): cuBLAS inside the captured tests graph -- `torch.cuda.graph()` captures on ONE
  class-level stream, so every slot's graph shares that stream's cuBLAS workspace and four slots replaying concurrently race on it.
  Dropped mm_mod.
* 22:27Z device profile (`prof_dev.py`, CUPTI): device busy (union) shared 0.241 s vs bare 0.142 s; kernel sum 0.308 vs 0.172.  Eager
  shape profile (`evidence/prof_shapes.py`) of one sub-batch: the fingerprint lane-coefficient contraction (D x n_op x C x n_slots x
  steps x 16 = 25M int64 mul/mod/sum) 0.96 ms, the chain quotient `((Renc * U[rows]) % p).sum(1)` over R = 42 rows + the int64 upcast
  ~1.0 ms.
* 22:31Z bf16-hopper `+shared` interactive gate (64x64 tile, 4096 VUs, cfdcf65): **98 honest sub-batches, 98 negatives, 0 failures**.
* 22:32Z 53452a6: `tests_fused.chain_quotient` + `fp_lanes` (cupy kernels, one pass each, bit-exact vs torch incl. P-1 extremes:
  `chain_test.py::test_fused_fp_lanes_and_chain_quotient_are_the_torch_sums` on the pod).  shared p4 **0.299 -> 0.281 s**, bare
  unchanged 0.153 s.
* 22:40Z (commit below) interleaved pair: H commits on its own slot ahead of G, waits after its root for the fingerprint statement
  (a Future resolved from G's messages via `fp_sink`), multiproofs on a pool thread.  `evidence/check_pair.py` on the pod: 13/13
  pairs accepted (Python verifier) interleaved and sequential, tampered F_G rejected.  Soundness note: H's root is now committed BEFORE
  rho is drawn (was after); H's witness is a function of the committed rows alone, so this only removes prover freedom.
* Small-tile dumps (2x4, both modes) for the pins: fp8-hopper G IA 22acdec1…/f958bdde…, FS e5e4eae5…/7b475f32…; H = fp8-ada's H (same
  steps / k / word bits); bf16-ampere G IA b6a145dc…/e72aeb1d…, H IA 95d32763…/90dc00d5….  (rc=1 there is the known small-tile batch
  bound 2^-127.81 over 4 sub-batches, as in share-logup's small dumps.)
* 22:40Z interleaved pair timed (`prof_p4.py`, same pod, median of 6): `+shared` **0.277 s** (min 0.248) vs bare 0.153 s -- 1.81x.
  The overlap buys little: H is small (1142 rows at l = 4096) and G's own stages are already device-bound behind the other three
  jobs at depth 4.
* 22:41Z 3ad48e50: `relation.rs` pins the G/H systems of bf16-ampere, bf16-hopper, fp8-hopper (IA + FS; H is shared by relations of
  equal steps / word width, so fp8-hopper's H is fp8-ada's).  `ligero-verify` rebuilt on the pod (release).
* 22:43Z final campaign (`fin.sh`, 4096 VUs, l = 16384, interactive non-ZK local coins, `--pipeline 4`, 3 reps, 64x64 tile).  The
  fp8-ada `+shared` bench crashed AFTER its reps in `_verify_dumps`: the v6 statement reader lost its leaf-scheme argument in the
  leaf-iface rebase (`_hash_auth_block_r(r, n_vus)`); 777670ac resolves the scheme from the relation name as v5 does.  The dumps were
  fine (Rust 13/13); rerun at 5 reps next to a 5-rep bare (`fin2.sh`).
* Shared gates (`gate-vu --auth included-hash-shared --tile 64x64`, 4096 VUs): fp8-ada IA **49 honest / 98 negatives / 0 failures**;
  fp8-hopper FS **49 / 98 / 0**; bf16-ampere FS **98 / 98 / 0**; bf16-hopper FS **98 / 98 / 0** (+ its IA gate at 22:31Z above).
* 22:52Z fp8-ada 5 reps, back to back on the pod (`fin2.sh`): bare **0.161** / `+shared` **0.268** / bare again **0.157** s
  (shared reps 0.243 0.300 0.268 0.259 0.285); Rust batch 13/13 ACCEPT, system pinned.  Device profile (`prof_dev.py`, CUPTI) of
  the same tip: see `profdev_*.log` in the run-files art.
* 22:50Z bf16 `+shared` was **2.84 s** (bf16-hopper; bare 0.254, unshared hash 0.774) and host-bound: device busy (union) 0.41 s
  of a 2.79 s pass.  `evidence/diag_graphs.py` (counts CUDA graph captures / tests static-set rebuilds per pass): 5 captures + 2
  rebuilds EVERY pass -- the hash side runs at l_H = 8192 (67-68 units x steps 96) except the ragged last sub-batch (17 units ->
  the l_G/4 floor, 4096), and `protocol._tests_static` kept ONE static set per (stream, system), so that sub-batch evicted the
  8192 set on its H stream and the next pass evicted it back (buffers + commit graph + tests graphs re-captured; fp8 never flips:
  its H is 4096 throughout).  453d7cf4 keeps up to two (LRU, `TESTS_STATIC_KEEP`): 0 captures / 0 rebuilds per steady pass,
  bf16-hopper `+shared` **2.76 -> 0.547 s** (median of 3, `diag_graphs.py`).  Every buffer the commit graph writes is owned by
  its static set (or allocated inside the capture), encoders are per (l, n, t_pad), and the tests graph re-captures on a moved
  pinned buffer, so a kept set's graphs never replay into memory another configuration reallocated.
* 23:00Z post-fix (453d7cf4) bf16 `+shared` benches with dumps: bf16-hopper **0.512 s**, Rust **25/25 ACCEPT** pinned; bf16-ampere
  0.571 s (reps 0.447 / **1.914** / 0.564: rep 2 ran under a concurrent 32-process fixture build on the host), Rust **25/25 ACCEPT**
  pinned; clean rerun 23:07Z **0.480 s** (reps 0.473 0.522 0.481).  Post-fix gates (`gate2_*`): bf16-hopper FS 98 / 98 / 0,
  bf16-ampere IA 98 / 98 / 0, fp8-ada IA 49 / 98 / 0.  bf16-ampere bare / hash needed the u16 operand arrays built on the pod
  (`verity_numerical.bench.instances build`, HF download, done 23:03Z): bare **0.262**, hash **0.744** s.
* 23:09:51Z pod kx69zewzhawgy1 terminated after every cited file was put + preserved (art ids above).

## FINAL

**Branch** `lane/share-logup-3` @ **453d7cf4** (5 commits on share-logup-2's cfdcf65: 53452a6c fused kernels, 32672193
interleaved pair, 3ad48e50 Rust pins, 777670ac v6 reader fix, 453d7cf4 static-set LRU; never merged).

**Table** -- RTX 4090 pod kx69zewzhawgy1, one pod for every cell, 4096 VUs, batch 16384 (l = 16384), interactive non-ZK local
coins, `bench-vu --pipeline 4`, prover t.total = median over reps (3 unless noted), 64x64 tile for `+shared`:

| relation | bare | +hash (unshared Poseidon2) | +shared (tile64) | shared / bare | hash / shared |
|---|---|---|---|---|---|
| fp8-ada | 0.161, 0.157 (5 reps each, bracketing) | 0.373 | **0.268** (5 reps) | **1.69x** | 1.39x |
| fp8-hopper | 0.136 | 0.355 | 0.308 (reps 0.308 0.331 0.262) | 2.27x | 1.15x |
| bf16-hopper | 0.254, 0.258 | 0.774 | **0.512** (was 2.84 before 453d7cf4) | 2.0x | 1.51x |
| bf16-ampere | 0.262 | 0.744 | **0.480** (clean rerun; 0.571 with the contended rep) | 1.83x | 1.55x |

Correctness at the tip: `ligero-verify batch` (pins in 3ad48e50) accepts every `+shared` dump -- fp8-ada 13/13, fp8-hopper 13/13,
bf16-hopper 25/25, bf16-ampere 25/25, each "system pinned", batch 2^-128.18 (fp8) / 2^-128.60 (bf16), python agreement all.
Shared gates 0 failures: fp8-ada IA (x2, pre + post fix), fp8-hopper FS, bf16-ampere FS + IA (post fix), bf16-hopper IA + FS (x2).
Unshared worst case intact: `+hash` benches validate for all four relations (bf16-ampere at 453d7cf4, the other three at
3ad48e50; 453d7cf4 only changes how many tests static sets a stream keeps).

**Goal status.**  `+shared` for bf16-hopper, fp8-hopper, bf16-ampere: DONE (Rust pins + gates 0 failures + benches).  fp8-ada+shared
within 1.3x of bare: NOT MET -- **1.69x** (share-logup-2 left 1.94x; this lane: fused chain-quotient / fp-lane kernels 0.299 -> 0.281,
interleaved G/H pair ~0.277, bench 0.268).  The rest is not latency: at the tip the device is busy (union) **0.213 s** per shared
pass vs 0.135 s bare (`profdev_*.log`, kernel+copy sum 0.273 vs 0.164) -- 1.3x of bare's 0.158 s wall is 0.205 s, BELOW the shared
device floor even at perfect overlap.  Reaching 1.3x needs ~0.03-0.05 s less device work per pass, i.e. a cheaper G: its private
operand block (704 rows: 512 bit rows + decode pins, +22 % of G's 3396-row commit / encode / tests) and H's fixed per-proof cost.

**Pod cost.**  kx69zewzhawgy1 at $0.74/h, 16:47:41Z -> 23:09:51Z = 6.37 h = **$4.71** for the pod's life (share-logup,
share-logup-2, share-logup-3); this lane's share ~22:15Z -> 23:10Z = **~$0.68** of the $5 budget.

**Remaining work.**
1. fp8-ada 1.3x: cut G's device work -- a LogUp / lookup range check for the operand words instead of 8 (fp8) / 16 (bf16) bit rows
   per word (the lane's namesake, never built), or fold the lane packing into fewer rows; then re-measure with `prof_dev.py`.
2. Host side still ~0.1 s per pass: H's hint rows could be built per committed row at commit time (as the sponges are) and
   gathered (~20 launches -> ~5 per job; small); G's `shared_hints` (private decode + bits + lanes, ~25 launches) could join the
   graphed base hints.
3. G3 (red-team-leaf-2) still BLOCKING for a live verifier: `coins_h` are prover-sampled in these benches (local coins only).
   F8 (fingerprint privacy leak) stays the stated option (b).
4. fp8-hopper `+shared` has only 3 noisy reps (0.26-0.33); rerun at 5 reps next to bare.
5. `serialize._read_v6` had no test (the leaf-iface rebase broke it silently until a dump re-read): add a v6 round-trip test.
