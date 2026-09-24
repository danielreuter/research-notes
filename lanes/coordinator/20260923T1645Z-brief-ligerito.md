---
lane: coordinator
kind: brief
created: 2026-09-23T16:45Z
for: lanes ligerito-design, ligerito-proto (Phase A); ligerito-relation (Phase B, later)
---

# Brief — Ligerito: a succinct backend for the same relation IR (target ≤ 1 MB proof per 4096-VU batch, ≤ 10 MB/s per GPU)

## 0. Where you start (both lanes)

* Repo `~/projects/verity` (shared `.git`). Worktree `~/projects/verity-main-wt/<lane>` on branch `lane/<lane>` from `main` at e0cf2cd.
  Never merge into main, never touch other worktrees or pods, no new `.md` in the repo (notes go to `~/.research/notes/lanes/<lane>/
  20260923T1645Z-report-<lane>.md`, front matter `lane/kind/created/status`, `CHECKPOINT <sha>` line at the top every ~45 min, `## FINAL`
  at the end). Tooling rules: `~/.research/notes/lanes/coordinator/20260923T1030Z-brief-wave2-device-lanes.md` §0–§2 (store, `research
  run`, pods, pushing, `machines.toml`, notes format). Laptop disk is tight: no dump trees on the laptop; one `.venv` per worktree.
* Read: (1) the Ligerito paper — https://eprint.iacr.org/2025/1187.pdf (Novakovic–Angeris 2025; §3 matrix-vector product = Ligero as a
  PCS, §4 partial sumcheck, §5 the merge, §6 the recursive protocol + error bounds (17)/(18) + Appendix parameter optimizer; Table 1:
  2^20 → 145 KiB / 0.08 s, 2^24 → 255 KiB / 1.3 s, 2^28 → 360 KiB, 2^30 → 420 KiB on an M1 laptop, F_2^32 base, rate 1/4); the Rust
  implementation `rotkonetworks/zcli` crate `ligerito` (docs.rs/ligerito) for a second reading of the round structure (148 queries per
  round); (2) OUR system: `backends/direct/ligero/PROTOCOL.md` (whole), `compile.py` (the relation IR: `Row` kinds bit/sel/…, `Linear`,
  `Quadratic`, lookups as one-hot selectors, `chain` = values carried between adjacent columns, `wide` groups), `protocol.py`
  (interleaved/linear/quadratic tests, D combinations, coin slots and 8c, ZK mask rows, `soundness()`), `encode_simt.py` + `merkle.py`
  (GPU RS encode + BLAKE3 Merkle), `serialize.py` (what the proof bytes are today), `relations.py` (fp8-ada: 3724 rows × 48 columns per
  VU; bf16-hopper: 3516 × 96); (3) `~/.research/notes/lanes/coordinator/20260923T1215Z-report-morning-overnight2.md` §1 for today's
  numbers (H100 BF16: proof 118 MB / 0.665 s, serialization = 40 % of prover time; fp8-ada 4090: 66 MB / 0.252 s live, 0.17 s local coins).

## 1. Why

Table 2's B-Ligero proofs are 24–118 MB per 4096-VU batch = 175–330 MB/s of proof egress per GPU. The user wants ≤ 10 MB/s per GPU, i.e.
≤ 1 MB per batch, while keeping prover overhead where it is. Ligero is O(√N) by construction (t opened columns × m rows; floor ≈ 20 MB per
batch at our N ≈ 2^29.4 cells). Ligerito is recursive Ligero: same ingredients (Reed–Solomon rows, BLAKE3 Merkle, opened rows, unique-decoding
soundness, no algebraic hash, interactive-friendly) with log²N/loglogN proofs (~400 KB at 2^30). It is the smallest change to our
assumption set that reaches the target, and it can make the prover FASTER (H100 spends 0.27 s of 0.665 s serializing 118 MB).

Constraints that do not move: exact relation IR (`compile.System`: rows / linear / quadratic / lookups / chain / wide), BabyBear base field
with degree-6 extension challenges, 2^-128 per batch in the unique-decoding regime (no conjectured proximity gaps), interactive with
verifier coins as the headline (FS only as a diagnostic), malicious-verifier ZK, Rust independent verifier, same `bench-result/v1` contract
with `proof_bytes`, `net.*`, `verify.*`.

## 2. Architecture hypothesis (design lane confirms or corrects it, with numbers)

Today: witness matrix U (m rows × l columns) per sub-batch; three Ligero tests (interleaved proximity, linear, quadratic) each = "claimed
combination vectors are consistent with t opened columns". Ligerito world: the batch witness is one multilinear polynomial (or a few) over
N = m·l·n_sub cells; constraints become a Spartan/HyperPlonk-style zero-check sumcheck (degree 3 for a·b = c; linear and lookup-selector
rows are degree ≤ 2 terms in the same batched sumcheck); the sumcheck ends in evaluation claims of the committed polynomials at a random
point, which Ligerito proves as its inner-product/partial-evaluation argument with ℓ recursive rounds. Prover work ≈ our RS encode of the
same data (NTTs, GPU, `encode_simt` — orientation is transposed: Ligerito encodes the tall dimension) + one degree-3 sumcheck pass over
N cells in the extension + small recursive rounds. Proof ≈ Σ_i |S_i| × 2^{k'_i} × 4 B + sumcheck messages + Merkle paths, ~0.3–1 MB.

Known hard parts (design lane must address each with a concrete mechanism and a cost):
1. **Chain / wide constraints** couple ADJACENT columns (values carried column → column). In the hypercube this is a shift, not a
   per-point constraint: needs a shift/rotation argument (e.g. treat "current" and "next" as two polynomials with a permutation/equality
   argument, or lay the chain along the low variables so the shift is a fixed small-dimension linear map, or the STARK-style "next row"
   trick expressed as a sumcheck over eq(x, x+1)). Pick, cost it.
2. **Lookups** are one-hot selector rows over the table's distinct rows (quadratic constraints + range) — should carry over as degree-2
   terms; confirm, or use LogUp in the sumcheck.
3. **ZK**: Ligerito is a PCS, not ZK. Our ZK is Ligero mask rows + interactive coins (PROTOCOL.md 8b/8c). Sumcheck ZK needs masking
   polynomials (Libra-style) or a small ZK sumcheck; Ligerito openings need mask rows/columns. Design it; cost it; keep malicious-verifier ZK.
4. **Interactive rounds**: sumcheck has ~log N ≈ 30 rounds + ℓ·k'_i Ligerito rounds → maybe 40–60 verifier coins per batch. With a live
   verifier at 30 ms RTT that is 1.2–1.8 s of round trips per batch unless pipelined across sub-batches/batches (we have `--pipeline` and
   coin Futures in `live.py`/`pipeline.py`). Quantify the latency/throughput consequence and say what it implies (same-DC verifier,
   deeper pipeline, batching many batches into one sumcheck, or FS as a fallback the user has so far declined).
5. **Soundness accounting**: (17)/(18) from the paper for RS codes in the unique-decoding regime + the zero-check sumcheck error
   (degree·rounds/|F|) + batching, all over the degree-6 extension (|F| ≈ 2^186); union bound over whatever remains per batch; write it
   in the style of PROTOCOL.md §6 with the concrete numbers for fp8-ada and bf16-hopper.
6. **Parameters**: run the paper's optimizer (Appendix) for our N with 128 bits → ℓ, k_i, k'_i, |S_i|, proof bytes, verifier work; validate
   the calculator against the paper's Table 1 (must reproduce 145/255/360/420 KiB within ~10 %).

## 3. Lanes

### 3.1 `ligerito-design` (no pod, $0) — the design note + reference implementation + calculator. FINAL by 23:00Z.
D1 (by 18:30Z): proof-size/soundness calculator `backends/direct/ligerito/params.py` (+ tests reproducing the paper's table) and the
parameter set for our batch sizes; CHECKPOINT with the predicted bytes/batch and bytes/s for the five Table 2 cells at today's prover
times. D2 (by 21:00Z): pure-Python/numpy reference Ligerito PCS over BabyBear with degree-6 extension challenges (`backends/direct/
ligerito/ref.py`: commit / prove-eval / verify, toy sizes, tests incl. negatives: wrong evaluation, tampered row, wrong symbol) — this is
the spec `ligerito-proto` and the Rust verifier will be checked against. D3 (by 23:00Z): the design note covering §2 items 1–6 with
mechanisms and costs, a prover op-count comparison vs today's Ligero (encode, tests→sumcheck, serialization), the verifier cost, the
interactive-round budget, the ZK design, and a Phase B work breakdown (relation port, Rust `ligerito-verify`, ZK, live coins) with hours.
Coordinate with `ligerito-proto` through your notes (`## For ligerito-proto`): they need the round structure and parameters early.

### 3.2 `ligerito-proto` (4090, $4) — the go/no-go number: Ligerito PCS at real size on a GPU, today. FINAL by 23:00Z.
Torch implementation of the Ligerito commit + evaluation proof + (Python) verify over BabyBear with degree-6 extension challenges, at N =
2^26, 2^28, 2^29–2^30 (our per-batch witness sizes), rate 1/4 RS, |S| and ℓ from `ligerito-design`'s calculator (start with the paper's
choices: 148–190 queries per round, ℓ = 3–4; refine when D1 lands). Reuse `encode_simt.py`/`merkle.py` where the orientation allows (the
tall dimension is encoded — you may need to transpose or write a column-wise NTT path; measure both if cheap). Deliver, per N: prover wall
(commit / sumcheck-recursion / serialization buckets), proof bytes, verify time, memory; and side-by-side the cost of OUR current
encode+commit of the same number of cells on the same pod (`encoder_bench.py`). Negatives: tampered opened row, wrong final vector, wrong
evaluation → verifier rejects. Record results as `bench-result/v1`-style JSON in your notes dir and `research data put` them (`--by
ligerito-proto`). Then the question that matters: at our N, is Ligerito's prover ≤ 1.3× today's encode+commit+tests? If the recursion is
what costs, say where. Be honest and specific; a clear "no, because X" is a valid deliverable.

### 3.3 Phase B (tomorrow, after A) — `ligerito-relation`: the fp8-ada relation on the new backend (zero-check sumcheck over `compile.System`,
chain shift argument, lookups, ZK masking, live coins with pipelining), `ligerito-verify` in Rust, gates + negatives, Table 2 candidate
"B-Ligerito" with bytes/s. Not launched yet; the design note's §Phase B breakdown becomes its brief.

## 4. Coordination with the leaf campaign (running today on Ligero)
The leaf gadgets (Poseidon2 / BLAKE3 / Ajtai) and tile sharing are RELATION-level: rows, `Linear`/`Quadratic` constraints and one
post-commitment coin. They live in `compile.System` and port to the sumcheck backend unchanged (the post-commitment coin is natural there).
Do not touch `backends/direct/ligero/leaf/`, `hashchain.py`, `relations.py`, `protocol.py`; new code goes under `backends/direct/ligerito/`.
The relation IR is the contract between the two campaigns: if you need an IR change, write it in your note under `## IR requests` and stop
short of editing `compile.py` — the coordinator merges IR changes.

## 9. Coordinator appendix
* 16:45Z: launched ligerito-design and ligerito-proto.
* 17:00Z (COORDINATOR): DEADLINE CHANGE — Phase B is TODAY, not tomorrow. `ligerito-relation` launches ~21:00Z and must FINAL by 04:00Z, so
  D1 (params) and your `## For ligerito-proto` interface note are needed by 18:15Z, ref.py by 20:30Z, design note by 22:00Z. New parallel
  lanes since 17:00Z (module ownership in `~/.research/notes/lanes/coordinator/20260923T1700Z-brief-day-wave-b.md` §1 — READ IT):
  ligerito-sumcheck (layout.py/sumcheck.py: System -> zero-check -> eval claims, incl. the chain shift), ligerito-verify-rs (Rust verifier
  from ref.py fixtures), ligerito-zk (zk.py), live-2 (coin stream + round-latency numbers for you). ligerito-proto: you own `transcript.py`
  (Coins protocol) — post its signature in your note by 18:00Z; you may switch to an H100 80 GB if 2^30 OOMs on the 4090 (budget $8).
* 17:30Z (COORDINATOR — HARD RULE, user request): the LAPTOP IS NOT A COMPUTE OR STORAGE NODE. Disk is at 6.7 GB free and the user just
  lost work to it. Effective immediately: (a) NO `uv pip install torch`/cupy/triton in any laptop worktree — torch is on the pods only; I have
  UNINSTALLED torch from the leaf-iface, ligerito-proto and ligerito-sumcheck laptop venvs (each was +550 MB); if `import torch` fails on the
  laptop, that test belongs on the pod (`research run --on <pod>` or ssh); laptop tests are the numpy/pure-python subset only. (b) No dump
  trees, fixtures > 20 MB, or run-files pulled to the laptop (`research data fetch` only for manifests/results JSON). (c) No CPU-heavy
  long runs on the laptop (> ~1 min of 100 % CPU, e.g. parameter sweeps, 1e5 differentials, cargo builds of the big crate in parallel with
  others) — run them on your pod or on `vy-sp1`. (d) `cargo` builds: `--release` only when needed, `cargo clean` your target dir before FINAL.
  Check `df -h /` before anything that writes > 100 MB; if free < 4 GB, stop and note it.
* 18:20Z (COORDINATOR): LIGERITO-PROTO FINAL — `lane/ligerito-proto` @ 7bc2fdd; note `~/.research/notes/lanes/ligerito-proto/20260923T1645Z-report-ligerito-proto.md`
  (`## Interface` frozen 17:45Z = `transcript.py` Coins protocol: absorb / challenge(label, n) -> (n,6) / indices / rounds; FiatShamirCoins,
  LocalCoins, LiveCoins; extension field F_{p^6} = F_p[x]/(x^6 - 31) in `proto/ext.py` — Ligero's protocol.py "extension" is a product ring,
  NOT a field: the sumcheck must use `proto/ext.py`). `pcs.prove(f, z, dims, coins) -> Proof`, `pcs.verify(proof, z, v)`.
  MEASURED on the 4090: proof 0.51-0.91 MB at N = 2^29-2^30 (113-130x smaller than today; ligerito-design's byte model over-predicts 20-30 %
  because of batched multi-path dedup); PCS prover 0.37-0.53 s = 1.5-3x today's WHOLE fp8-ada prover, zero-check not included -> go/no-go
  (<= 1.3x) FAILS as measured; gap = host sumcheck bookkeeping 0.13-0.15 s + fp64 recursion contractions 0.10-0.17 s + two-pass tall NTT.
  OWNERSHIP CHANGE: `pcs.py`, `transcript.py`, `proto/` now belong to NEW lane `ligerito-pcs-fast` (launched 18:20Z; items 1-3 of proto's list).
  Everyone: base your Ligerito code on `lane/ligerito-proto` 7bc2fdd (cherry-pick or merge it into your branch; it only adds backends/direct/ligerito/).
  - ligerito-sumcheck: use `proto/ext.py` for F_{p^6}; your zero-check is the one remaining O(N) extension pass — measure it on-device.
  - ligerito-verify-rs: reproduce `merkle_multi.plan` (batched multi-paths, ~25 % of bytes) and the tensor-claim final check; fixtures from
    proto's tests are usable NOW (don't wait for ref.py).
  - ligerito-zk: hooks against proto's `pcs.prove` signature.
  - live-2: proto uses 21-29 sequential coins per proof -> your 50-round numbers decide whether >1 variable per coin is needed.
* 18:30Z (COORDINATOR): LIGERITO-DESIGN FINAL — `lane/ligerito-design` @ 760260d (includes proto 7bc2fdd); note
  `~/.research/notes/lanes/ligerito-design/20260923T1645Z-report-ligerito-design.md` `## FINAL`. USE PARAMETER SET **B** (level-1 rate 1/2 with
  the ternary tall digit, later levels 1/4, 2^-128 union, ZK counted): fp8 (3*2^28 cells) L=5 -> 622 KiB, 53 coins; bf16 (3*2^29) L=4 -> 704 KiB,
  51 coins; fp4 (3*2^26) L=4 -> 532 KiB, 47 coins. `params.py` reproduces the paper's Table 1 (x0.95-1.02) and proto's 8 measured proofs to <= 1 %.
  `ref.py` = numpy reference PCS (1-3 levels, radix-3 tall, batched Merkle, FS coins, JSON fixtures, 9 negatives, interop with proto's transcript).
  ZK design (mask column in the top level-1 PCS column + 239 random coefficients per level-1 column in pad cells + Libra-style zero-check mask)
  is the SAME as ligerito-zk's. Laptop clock is authoritative (proto's 20:xxZ stamps were ~2 h fast).
  - ligerito-verify-rs: `ref.py` JSON fixtures exist NOW — accept them bit-for-bit + reject the 9 negatives; parameter set B shapes.
  - ligerito-pcs-fast: implement set B (radix-3 tall digit) as the default; keep default/F/S measurable; the model says encode x1.09 / Merkle
    x0.87 vs today — your buckets should approach that.
  - ligerito-sumcheck: zero-check tables are 12.9 GB base / 38 GB in the extension at fp8 real N — chunk them; 2 sumcheck variables per coin is
    the design's choice (51-53 coins/batch); 3 per coin -> 37 coins.
  - live-2: measure the coin stream at 50 AND 37 rounds/batch, window 1/4/8/11, at the real RTT; the design says depth 9-11 is needed at
    30 ms RTT vs a 0.16 s prover and the 4090 fits only 5 in flight (4.3 GB each) -> 0.35 s/batch; state what a same-DC verifier gives.
  - NEW: `ligerito-relation` launched 18:30Z (not 21:00Z) — owns prove.py / proof.py / run.py; integrates against your current interfaces
    and stubs what is missing, so post `## Interface` updates as soon as they change.
* 18:45Z (COORDINATOR): LIGERITO-SUMCHECK FINAL — `lane/ligerito-sumcheck` @ 5b33e23; note `~/.research/notes/lanes/ligerito-sumcheck/20260923T1700Z-report-ligerito-sumcheck.md`
  (`## 3. Interface` = wire format LGSC0002 + Coins call order + claim points in the PCS's column-major order `x = row + R*col` + the verifier's exact
  checks; fixture `evidence/fixture_fp8ada_l64_S2.json.gz`). Chain shift = shifted virtual rows + one degree-2 shift sumcheck over the 18 column
  variables (10 ms). MEASURED H100 fp8-ada 4096 VUs: 0.291 s steady (1.4x today's t.arithmetic 0.209 s), 37.1 GB peak, 4645 B messages,
  **61 sequential coins for the sumchecks alone** (design assumed 51-53 for the WHOLE batch; with the PCS's ~21 the total is ~80). bf16-hopper
  0.482 s / 73.6 GB. The 4090 cannot hold a 4096-VU batch (2048-VU half batches 0.190 s / 18.6 GB).
  OWNERSHIP: `layout.py` / `sumcheck.py` pass to NEW lane `ligerito-sumcheck-2` (launched 18:45Z): coin reduction (batch the rows + shift
  sumchecks into one, 2 variables per coin in the column rounds), 4090 fit (column-striped zero-check / half batches), kernel floor ~0.2 s.
  - ligerito-relation: build the PCS input `f[i + R*c] = z[i, c]` for i < m; ONE coins object in the order commitment -> sumcheck draws -> PCS;
    say which `pub:*` vectors have closed forms over the public words (the only O(C) verifier work). Take `__init__.py` from either branch.
  - ligerito-verify-rs: implement §3 from the fixture now (LGSC0002 may shrink in coin count under sumcheck-2 — keep the verifier data-driven by
    the round list in the header).
  - live-2: plan for ~80 coins/batch today, target ~40-50 after sumcheck-2; measure window depth vs RTT at 80 AND 40.
  - ligerito-zk: the Libra mask goes on LGSC0002's zero-check (29 messages incl. the bivariate opening round).
