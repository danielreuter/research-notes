---
lane: coordinator
kind: brief
created: 2026-09-23T17:00Z
for: lanes ligerito-sumcheck, ligerito-verify-rs, ligerito-zk, tier0-bytes, fp4-decode, live-2 (+ later: red-team-leaf, ligerito-relation, merge-val-3, device wave)
---

> **Rules superseded (2026-09-24T01:00Z):** the standing lane rules (§0 and similar sections) now live in `~/.research/notes/kb/LANE-CONTRACT.md`, which wins where they differ. This brief's lane-specific content stands.

# Brief — day wave B: everything lands TODAY (FINALs 23:00Z for infrastructure lanes; Ligerito integration 21:00Z–04:00Z; device waves 00:00Z–06:00Z)

## 0. Rules (same as the other briefs; read them)
* Tooling + conduct: `~/.research/notes/lanes/coordinator/20260923T1630Z-brief-leaf-campaign.md` §0 (worktree per lane from `main` e0cf2cd,
  one pod per GPU lane, notes file with `CHECKPOINT <sha>` lines and `## FINAL`, no new .md in the repo, DISCREPANCIES.md is capped, no dump
  trees on the laptop, `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`, labels `--by <lane>`, no `verified=` labels).
* Ligerito context: `~/.research/notes/lanes/coordinator/20260923T1645Z-brief-ligerito.md` (whole). Ligerito lanes write ONLY under
  `backends/direct/ligerito/` (Python) or `backends/ligerito-verify/` (Rust); the relation IR `backends/direct/ligero/compile.py` is read-only
  for you — IR requests go in your note under `## IR requests`.
* Budget today: $50/h ceiling across all pods, ≤ 15 agents. GPU lanes may use an **H100 80 GB** instead of a 4090 when memory or speed
  needs it (`--gpu "NVIDIA H100 80GB HBM3"`); say so in `machines.toml`. Per-lane caps below. Terminate your pod at FINAL.
* Deadlines are real: the user wants the whole thing — three leaves, sharing, Ligerito backend with Rust verifier and ZK, and the device
  tables — finished today. Checkpoint early, ship partial-but-working over complete-but-late, write what is missing.

## 1. Ligerito module ownership (so six lanes can build in parallel without stepping on each other)

~~~
backends/direct/ligerito/
  params.py, ref.py            ligerito-design   (calculator; numpy reference PCS = the spec)
  pcs.py                       ligerito-proto    (torch PCS: commit / prove_eval / verify; parameters from params.py)
  transcript.py                ligerito-proto    (Coins protocol: challenge(label, n) -> extension elements; impls: LocalCoins (diagnostic,
                                                  deterministic from a seed), LiveCoins (verifier coin slots via backends/direct/ligero/live.py,
                                                  8c: challenges are functions of verifier coins alone); every lane draws randomness ONLY here)
  layout.py, sumcheck.py       ligerito-sumcheck (compile.System -> multilinear layout incl. chain/wide shift; degree-3 zero-check -> eval claims)
  zk.py                        ligerito-zk       (masking for the sumcheck + the openings; malicious-verifier ZK; hooks pcs.py/sumcheck.py call)
  proof.py, prove.py, run.py   ligerito-relation (launched ~21:00Z: glue, serialization LGTO0001, gates, bench-result/v1, relchain parity)
backends/ligerito-verify/      ligerito-verify-rs (Rust: PCS verifier from ref.py, sumcheck verifier, proof.py reader, `batch` CLI like ligero-verify)
~~~
Field: BabyBear p = 2^31 − 2^27 + 1; challenges in the degree-6 extension (`backends/direct/ligero/field.py` has the base field; the
extension tower used by the Ligero tests is in `protocol.py` — reuse, do not reinvent). Everyone reads the others' notes dirs at every
checkpoint (`~/.research/notes/lanes/ligerito-*/`) and posts interface decisions under `## Interface` in their own note.

## 2. Lanes launched 17:00Z

### 2.1 `ligerito-sumcheck` (H100 or 4090, $8) — the constraint layer: `compile.System` → zero-check sumcheck → evaluation claims.
Input: a compiled `System` (start with `fp8-ada`, then `bf16-hopper`) and the witness matrix as today's Ligero prover materializes it
(rows × columns per sub-batch — reuse `witness_device.py`/`relchain.py` marshalling; you may call the Ligero code to PRODUCE the witness, not to
prove). Output: `layout.py` (how rows/columns/sub-batches map onto the boolean hypercube; where chain-carried values live so that the
column→next-column coupling is a fixed shift; wide groups), `sumcheck.py` (batched degree-3 zero-check over all `Quadratic` rows, `Linear`
rows with their public `pub` vectors, lookup one-hot selectors and range bits; the chain shift as either a shifted-polynomial identity or
a sparse-matrix sumcheck — measure both if cheap; ends in evaluation claims of the committed polynomial(s) at the sumcheck point), with a
torch prover and a Python verifier of the sumcheck messages. Measure at real N (fp8-ada 4096 VUs): sumcheck prover time by round, memory,
message bytes, vs today's `t.arithmetic` for the same relation (0.129 s on the 4090 / 0.209 s H100 FP8). Negatives: one violated quadratic
row, one violated chain link, one violated lookup → the final claim mismatches. Coordinate the shift design with `ligerito-design` (their §2
item 1) — if you disagree, the measured one wins; write both in the note.

### 2.2 `ligerito-verify-rs` (no GPU; CPU only, $0) — Rust `ligerito-verify`.
Start from the paper's verifier (matrix-vector + partial sumcheck + recursion, RS codes, BLAKE3 Merkle as in `backends/ligero-verify/src/hash.rs`
and `merkle`), extension field arithmetic (port from `ligero-verify`'s degree-6 tower), `params` mirroring `params.py`. When `ligerito-design`'s
`ref.py` lands (≈ 21:00Z) generate fixtures from it and make the Rust verifier accept them bit-for-bit and reject their negatives; when
`ligerito-sumcheck` posts its message format, add the sumcheck verifier; when `proof.py` lands, read it and expose `ligerito-verify batch
--dir` like `ligero-verify`. `cargo test --release` green at every checkpoint; the coordinator runs cargo on the laptop.

### 2.3 `ligerito-zk` (4090, $4) — malicious-verifier ZK for the sumcheck + the Ligerito openings.
Design first (by 19:30Z, in your note, with the simulator sketch): masking polynomial for the zero-check (Libra/“ZK sumcheck” style) or the
cheaper “mask rows in the committed matrix + never open a mask-free column” Ligero-style masking adapted to Ligerito's recursive openings;
what the recursion leaks (the folded vectors are sent in the clear in the last round — they must be masked); coin structure (8c). Then
implement `zk.py` with hooks the PCS and sumcheck call, prove the masking adds ≤ 5 % rows/time at real N on the pod, and write the
“omitted”/“zk_statement” fields the fingerprint needs (see `relchain.zk_mode`). Negatives: a proof with masks removed must be distinguishable
in your simulator test. Read PROTOCOL.md 8b/8c and `redteam_zk.py` first — the red teams found real holes there last night.

### 2.4 `tier0-bytes` (4090, $4) — cut today's Ligero proof bytes 2–3× with serialization only, and trim the hashed statement.
(1) Opened columns: rows of kind `bit` are 0/1 and `sel` rows are one-hot — serialize them as bits (the verifier knows the row kinds from the
pinned system); 16-bit limbs as u16. Change `serialize.py` (new proof magic, additive) and the Rust reader/verifier (`ligero-verify` must
accept both formats; pins unchanged). (2) `included-hash` statements (LIGSTM05) still carry per-sub-batch instance arrays — for hashed
relations ship digests + leaf indices + roots + y words only (hash-relation's item 3: 91 → 26 kB/sub-batch) and make the Rust verifier
read that. Measure on the pod for `fp8-ada` bare and `+hash`: proof bytes before/after, statement bytes, `t.serialization` before/after,
Rust verify time; all sub-batches accepted. Report bytes/s at today's prover times for the five Table 2 cells (the coordinator's
comms table). Do not change any test/soundness code.

### 2.5 `fp4-decode` (RTX 5090 32 GiB, $4) — the in-circuit FP4 decode layer so the 5090 gets committed columns.
Read `~/.research/notes/lanes/hash-compose/*` §6 (their design: 141 verifier-side pins need an in-circuit decode layer ≈ 900 rows/unit,
24-bit-lane packing, component chain end in statement v5) and `backends/direct/ligero/fp4/`. Build `fp4-nvf4+poseidon2` (and, if the
`LeafScheme` interface from lane `leaf-iface` has landed — watch `~/.research/notes/lanes/leaf-iface/` — make it a leaf-agnostic
composition so `+blake3`/`+ajtai` come for free). Gate (2048 VUs + negatives incl. malformed E2M1/UE4M3 encodings), Rust pin + fixture
(ligero-verify already reads LIGSYS02 + FP4), bench vs the bare 5090 cell (0.0714 s at l=16384). Report rows/unit added and t.total.

### 2.6 `live-2` (4090 + one CPU pod for the verifier, $6) — the live-verifier tax and the many-round future.
(1) Move the prover's network sender off the compute path (async sender thread/stream; measure `t.total` live vs local coins on the same
pod: today ~2× tax at 30 ms RTT — target ≤ 1.15×). (2) `vu.py --pipeline` so the A100 BF16 cell stops being sequential-live. (3) Reproduce
and fix the `bf16-hopper --pipeline 2` 27-s session pathology (depth 1/4 fine). (4) For Ligerito: the sumcheck needs ~30–60 verifier coins
per batch; extend `live.py`'s coin protocol to a generic `challenge(label)` stream with windowed pipelining across batches and MEASURE the
per-batch latency and throughput at 30 ms RTT with a synthetic 50-round protocol; write the numbers `ligerito-design` needs for its round
budget (post under `## For ligerito-design`). Rebuild the verifier pod's Rust from your branch. Run the Wave 2 brief's live runbook first.

## 3. Lanes launched later today (coordinator)
* ~19:30Z `red-team-leaf`: Ajtai parameters + binding argument, tile-sharing soundness, BLAKE3 framing, Poseidon2 unsalted-digest caveat.
* ~21:00Z `ligerito-relation` (H100, $10): integrate pcs + sumcheck + zk + transcript into `prove.py`/`proof.py`/`run.py` for `fp8-ada`, gates
  (honest + the Ligero negative family), bench-result/v1 with proof bytes, Rust `batch` accepting every sub-batch; then bf16-hopper,
  bf16-ampere, fp8-hopper, fp4-nvf4 registrations. FINAL 04:00Z.
* ~23:00Z `merge-val-3`: GPU validation of the integration branch (leaf campaign + tier0 + live-2 + fp4-decode) before ff into main.
* ~00:00Z device wave (A100, H100, 4090, 5090; live verifier): Table 2 with bare | +poseidon2 | +blake3 | +ajtai (tile64 headline,
  worst-case drill-down) on Ligero, and the B-Ligerito column as far as it has landed; the comms table with bytes/s.

## 9. Coordinator appendix
* 17:00Z: launched 2.1–2.6. Running: leaf-iface, share-logup, ajtai-design, ajtai-leaf, blake3-leaf, ligerito-design, ligerito-proto.
* 17:30Z (COORDINATOR — HARD RULE, user request): the LAPTOP IS NOT A COMPUTE OR STORAGE NODE. Disk is at 6.7 GB free and the user just
  lost work to it. Effective immediately: (a) NO `uv pip install torch`/cupy/triton in any laptop worktree — torch is on the pods only; I have
  UNINSTALLED torch from the leaf-iface, ligerito-proto and ligerito-sumcheck laptop venvs (each was +550 MB); if `import torch` fails on the
  laptop, that test belongs on the pod (`research run --on <pod>` or ssh); laptop tests are the numpy/pure-python subset only. (b) No dump
  trees, fixtures > 20 MB, or run-files pulled to the laptop (`research data fetch` only for manifests/results JSON). (c) No CPU-heavy
  long runs on the laptop (> ~1 min of 100 % CPU, e.g. parameter sweeps, 1e5 differentials, cargo builds of the big crate in parallel with
  others) — run them on your pod or on `vy-sp1`. (d) `cargo` builds: `--release` only when needed, `cargo clean` your target dir before FINAL.
  Check `df -h /` before anything that writes > 100 MB; if free < 4 GB, stop and note it.
* 18:10Z (COORDINATOR): leaf-iface landed on `lane/leaf-iface` @ 720820d — fp4-decode and tier0-bytes: rebase onto it (NOT onto main, which
  moved to 22e10e0 with the other session's vLLM merge). fp4-decode: the Poseidon2 leaf's packing seam is `lane_bits` — make the FP4 row's
  24-bit lanes a leaf parameter per leaf-iface's `## For other lanes`. Ligerito lanes: no change (you only touch backends/direct/ligerito/ and
  backends/ligerito-verify/). Integration branch `lane/integration` is built by the coordinator from main 22e10e0 + all lane branches at ~23:00Z.
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
* 21:05Z (COORDINATOR): fp4-decode and live-2 went silent at ~19:00Z (pods idle). Replaced by `fp4-decode-2` and `live-2b` (brief
  `20260923T2100Z-brief-relaunch.md`; same pods). live-2b delivers the device-wave live-verifier RUNBOOK. FINALs 23:00Z.
