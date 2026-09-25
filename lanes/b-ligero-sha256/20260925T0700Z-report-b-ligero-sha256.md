---
lane: b-ligero-sha256
kind: report
created: 2026-09-25T07:00Z
status: open
---

CHECKPOINT ee2a319f (10:14Z) [open] 98d878ca: MALLOC default in pod env.sh + software.allocator in every fingerprint (+2 tests), merge-ready handoff to coordinator. Screen fp8-hopper-x4+sha256 l4096p4 5837 VU/s e2e; sweep r20260925-095503-e592 running.
CHECKPOINT 5483d13b (10:07Z) [open] 10:07Z tip da74b03e (+main 3301c435 R1/R2/R4). Page-fault fix (MALLOC_MMAP_MAX_=0) -> fp8-hopper-x4+sha256 l4096 p4 sweep r20260925-095503-e592: 1024 4145, 2048 4739, 4096 5356, 8192 5860, 16384 5768 VU/s e2e; 32768 running. Handoff to coordinator on page faults.
CHECKPOINT 10996616 (09:42Z) [open] 09:45Z tip 88b82757: SHA-256 row_sponges on GPU (commit 21s->0.2s, identical roots). Found: per-proof 2.3s in opened_from_pinned = first-touch page faults on this H100 host (91MB fresh alloc 5.6s; reused 8ms). Testing glibc MALLOC_MMAP_MAX_=0 fix, then screen.
CHECKPOINT 10996616 (09:20Z) [open] 09:20Z tip be1a3bcb (merged main 94b1c4d2 GPU committer; PINS fp8-hopper-x4/fp8-ada-x4 +sha256). Gates 2048VU 7 honest+86 neg 0 fail both (art:c1351b8a, art:5b0162d6); gadget-row negs 30/30 (art:bdfcc3b3); Rust pinned batch ACCEPT. H100 screen l8192/16384 running.
CHECKPOINT 24ab6c7d (09:00Z) [open] 09:00Z H100 qmiq4rs1f0y4tr healthy (hostmem ok). r20260925-085824-e359: fp8-hopper-x4+sha256 fixture ok, gate honest 2048 VUs all True (0.31s/341VU); negatives running; fp8-ada-x4 next. Then PINS rows, Rust batch, screen, sweep cell.
CHECKPOINT a816a2b1 (08:15Z) [open] fixture fp8-ada-x4+sha256 OK: 90,848 rows/col, sys_id d6b0cd8d, table b04a579c, Python ACCEPT. First gate spent 8 min single-threaded with GPU idle (cause unknown; killed). a816a2b1 lazy conformance fixture; r20260925-080759-dd48: x4 conformance 5 passed so far, gate rerun unbuffered
CHECKPOINT 70cb6c59 (07:52Z) [open] 70cb6c59: survey landed 07:43Z, its SHA-256 rec (bit-sliced ~18k rows) = my design, adopted; merged peer dc2cae87 (sweep_vu); leaf_bytes_many + sha256_test; bench variant 'B-Ligero + SHA-256 in circuit' on frame-v3/sha256 line. pod run r20260925-075211-7893: conformance+fixtures+gate fp8-ada-x4
CHECKPOINT 922120d2 (07:27Z) [open] 922120d2 pushed: leaf/sha256.py (sha256/row/v1, 18,128 rows/blk: 1-row sels XOR/Maj, 16b-limb adds; CV published, pad block native) + ligero-verify SHA256 scheme+vectors. census fp8-ada-x4+sha256 90,848 rows/col. next: pod fixtures/pins/gates.
CHECKPOINT 00ffe398 (07:08Z) [open] started 07:00Z; merged b-ligero-standard-hash ad4c3440; design: publish CV after last data block, padding compression native; x4 folds (2 blocks/col); survey absent; next: sha256 leaf native+Rust+harness
# b-ligero-sha256: B-Ligero frame-v3 `sha256/row/v1` row leaves (SHA-256 half of the standard-hash track)

Goal (launch message): a SHA-256 compression gadget in B-Ligero's relation proving frame-v3 `sha256/row/v1` row digests of the
x rows and W columns, published and checked natively by `ligero-verify` against the scheme's trees; pinned in Rust; gated
with the 86-negative battery; then the first SHA-256 full-relation cell (frame-v3, then a vllm-v1 variant). Decision doc:
Project store `docs/commitment-scheme-decision.md` §3, §5, §6.2 step 5, §6.3. Worktree `~/projects/verity-main-wt/b-ligero-sha256`,
branch `lane/b-ligero-sha256`, base main 00ffe398. Pod scripts: `evidence/pod-scripts/`.

## 0. Starting state (07:00Z)
* Merged origin/lane/b-ligero-standard-hash ad4c3440 (`--commit-per-rep`, +blake3 pins bf16-ampere / fp8-hopper) -> my tip
  ad4c3440. blake3-leaf-3 820aa6f and the pipelined hashed runner 1cf9178 are already ancestors of main.
* steps pin (red-team H2): Rust `check_vu_shape` + Python `layout_error` already on main (lane steps-pin); ligero-steps-pin's
  236020a6 closes the +shared (v6) Python gap only, which this lane does not use. Merge it when it reaches main.
* Survey `docs/hash-proving-survey.md`: not present at 07:00Z.

## 1. Design (fixed by the core schema, not by the gadget)
`sha256/row/v1` = `SHA-256(prefix64(role, word_bits, n_words) || row_bytes)`: the first block is a public constant, so the
chain starts at a constant midstate; the row is 24 (E4M3) / 48 (BF16) whole blocks; the padding block (0x80, zeros, bit
length) is a public constant.  **In-circuit: the data blocks only.  Published: the chaining value after the last data block
(8 u32 = 16 limbs) plus a constant header (role, word width, n_words).  The verifier runs the padding compression natively**
(`leaf_bytes`), exactly like the BLAKE3 leaf's native parent fold: two rows with the same published CV are a SHA-256
collision (same prefix, same length).  So "one extra block for padding" costs 0 rows.

Columns: the x4 folds (`fp8-ada-x4`, `bf16-*-x4`: 128 bytes = 2 whole blocks per operand per column) -- no half-block
columns, so no discarded compression (the x1 relations would waste half of every SHA-256 compression like BLAKE3's).

## 2. Gadget options (written before the survey; the survey gate decides)
| option | rows / 64 B block (est.) | notes |
|---|---|---|
| (a) bit design as §3 of the decision doc (2-input XOR products, 3-input XOR = 2 products) | ~27 000 + schedule 7 900 | §3's estimate |
| (b) bit design with a carry-bit 3-XOR: for booleans x, y, z one row `c = maj(x,y,z)` with `c^2 = c` and `(s-2c)^2 = (s-2c)`, `s = x+y+z`; XOR = `s - 2c` affine, Maj = `c` itself | ~18 300 (rounds 64 x 204, schedule 48 x 100, H bits, feed-forward) | message bits reused from the operand bit rows (hashchain's `hash.a[i].b<j>`) |
| (c) one-hot lookup tables (`ctx.lookup`) for XOR / Ch / Maj | 66x worse per XOR (blake3-leaf census: 2 112 rows per u32 XOR) | Ligero's lookup here is a one-hot selector, not LogUp |
| (d) LogUp / Lasso-style lookups (Flock, Jolt) | n/a in today's B-Ligero relation | needs a LogUp argument in the Ligero relation (share-logup has one for Poseidon2 sharing only); out of this lane's scope |
| (e) GKR / Binius (binary-field towers) | n/a | a different proof system; not B-Ligero |

Per round (b): Sigma1 32 + Ch 32 + Sigma0 32 + Maj 32 carry rows + the two modular sums a' (7 addends) and e' (6) on 16-bit
limbs, 19 + 19 bit rows each = 204.  Schedule: sigma0 32 + sigma1 32 + 4-addend sum 36 = 100 per W_t, 48 of them.

**Survey gate (07:43Z, `docs/hash-proving-survey.md` landed):** §3.2 recommends for SHA-256 in B-Ligero exactly option (b),
"bit-sliced, ~202 rows per round, ~18k rows": commit the parity of each Sigma (one row per bit), Maj one row, Ch = e(f-g), the
new e / a with 32 bits + carries.  Its parity row `(s-o)(s-o-2)=0` is my `c=[s>=2]` row with `o=s-2c` (same one committed
element per bit).  Byte LogUp: "not worth it" for SHA-256; GKR / Flock routes are other proof systems (4.2 step 2, blocked
on Flock ZK).  **Adopted unchanged**: 18,128 rows per block (census below), survey projection ~5.9x bare for SHA-256.
Lower bound check: Sigma0/Sigma1/sigma0/sigma1 outputs are cubic in the input bits (x+y+z-2(xy+yz+zx)+4xyz), so each output
bit needs one committed element in a quadratic relation; Ch needs one product per bit; so ~96 bit rows + ~70 addition bits
per round is the floor for a bit design with committed booleans.

**Census (measured, `python -m backends.direct.ligero.leaf.sha256`, no torch):** rows / block = 64 x 204 + 48 x 100 + 8 x 34
= 18,128 (BLAKE3 15,136).  Per column, `fp8-ada-x4+sha256`: 90,848 rows (bare x4 14,875; hash 73,122 incl. H-bits and copies),
12 columns / VU = 1.09 M rows / VU.  `bf16-ampere-x4+sha256` 90,165 x 24.  x1 (half-block pairs): `fp8-ada+sha256` 41,918 x 48.

## Log
* 07:00Z started; read LANE-CONTRACT v2.0, TABLES (+ amendments), decision doc, blake3-leaf-3 / red-team-leaf-3 /
  b-ligero-standard-hash / ligero-steps-pin reports, `leaf/blake3.py`, `leaf/base.py`, `hashchain.compose`, `rowleaf.py`,
  `ligero-verify/src/leaf.rs`; inbox empty.
* 07:27Z 922120d2 `leaf/sha256.py` + registry + ligero-verify `SHA256` scheme (`leaf.rs`, `hash.rs::compress` pub(crate)) with
  Python-generated vectors (x, w, x16, malformed).  Laptop checks (torch-free): native == core `sha256/row/v1` vectors; one
  compression gadget evaluated from its witness program: 0 violations, output == SHA-256 compression, a flipped carry row fails.
* 07:44Z pod vy-b-ligero-sha256 (RTX 4090, $0.74/h, guard 90) bootstrap r20260925-074414-ece7: OK except BENCH_INSTANCES
  (BF16 frozen-set rebuild hit HTTP 429 on the range fetch; not needed for FP8). Health OK (encode 1.07x ref, matmul 0.99x).
* 07:43Z survey landed (see §2); 07:52Z coordinator handoff: adopt it; R1/R2 (red-team SH: prover-chosen (vu, x, W) triple;
  reverify recomputes no roots) gate counting until ligero-steps-pin's fix lands -- merge it then.
* 07:50Z merged origin/lane/b-ligero-standard-hash dc2cae87 (sweep_vu, blake3 leaf_bytes_many, ligero-steps-pin 236020a6 via
  blake3-80gb).  fff7bf76 sha256 `leaf_bytes_many` + `leaf/sha256_test.py` (4 passed, 0.6 s).  70cb6c59 bench: "B-Ligero +
  SHA-256 in circuit" (drilldown variant, views config on the existing `frame-v3/sha256` line -- TABLES: five lines x three
  schemes, the SHA-256 row leaf is that line's -- `tables._LEAF_FAMILIES`); bench tests 247 passed.
* 07:52Z r20260925-075211-7893 (tree 70cb6c59): core_schema 3 passed; conformance on fp8-ada-x4 errored in the module fixture
  (it composed every scheme; Poseidon2 has no x4 layout) -> a816a2b1 builds runners lazily.  x1 fp8-ada conformance (eager
  fixture: all four schemes on CPU) killed after 6 passes at ~5 min; rerun on the new tree.
* 07:58Z handoff to b-ligero-standard-hash: shared primitives (`_carry` 1-row parity/majority, `_add` 16-bit limbs, operand bits).
* vllm-v1 analysis: pos leaf = 26-byte prefix + 1536 value bytes + pad -> 25 compressions, all in-circuit (block 0 and block 24
  hold private bytes).  On x4 columns (128 value bytes) blocks become ready at 2c+2 by column c, and block 24 only in column 11,
  so every column needs a 3rd slot per operand (column-uniform): ~1.4x frame-v3's rows, plus a native vllm-v1 tree check in
  ligero-verify (new).  Deferred behind the frame-v3 cell.
* 07:58Z fixture fp8-ada-x4+sha256 (r20260925-075211-7893): 90,848 rows/col (base 14,875, operand bits 2,816, hash 73,122,
  pins 35), sys_id d6b0cd8d69cb7ff5…, Rust `system-digest` table_digest b04a579ceb48fb57… (sys_id agrees), Python ACCEPT.
* 08:19Z gate fp8-ada-x4+sha256 (r20260925-080759-dd48, unbuffered): compose 16.8 s; **7/7 honest sub-batches ACCEPT**
  (2048 VUs, l = 4096, 341 VUs/proof; 3 s/proof unpipelined incl. check).  x4 conformance: 5 passed before I stopped it
  (CPU runner too slow; the negatives were on their way on the GPU).  The negatives phase stalled single-threaded:
  r20260925-082825-5ad9 (`12-prof.py`, cProfile of a 2-VU l=256 proof): 3.46 s of the proof in `opened_from_pinned`'s
  numpy copy, 13.5 s of the Python verify in `astype`.  Direct test on the pod: 220 MB numpy copy 0.65-0.81 s, out of pinned
  memory 9.6-11.4 s, astype int64 20.5 s -- **the host's memory was degraded** (pod health checks GPU encode/matmul only).
  Nothing from that pod is a timing.  All four runs fetched and preserved; pod drained 08:40Z.  00-bootstrap.sh now checks
  host memory (220 MB copies < 0.25 s).
* 08:41Z new pod vy-b-ligero-sha256 = H100 80GB HBM3 SECURE reference part (qmiq4rs1f0y4tr, $3.49/h, 28 vCPU), the launch
  message's 80 GB part.  Line: **FP8 Hopper (`fp8-hopper-x4+sha256`)**: FP8 rows are 24 blocks against BF16's 48, and the x4
  fold carries 2 whole blocks per operand per column (no discarded compression), 89,356 rows/col x 12 = 1.07 M rows/VU
  (fp8-hopper+blake3 x1: 34,997 x 48 = 1.68 M; blake3-80gb measured it at 1,471.7 VU/s plateau on H100).
* 08:53Z bootstrap r20260925-085339-4356 BOOTSTRAP_OK: host memory 0.107 / 0.100 s (220 MB numpy / pinned copy), encode
  0.295 ms, matmul 665.9 TFLOP/s.
* 09:05Z r20260925-085824-e359 (tree a816a2b1): fixtures + gates, both on the H100.
  - fp8-hopper-x4+sha256: 89,356 rows/col (base 13,383, operand bits 2,816, hash 73,122, pins 35), L 3,734, Q 125,490,
    sys_id 6cf20505b38e1425…, table_digest 76c1ce7f09b99fac….  Gate: **7 honest sub-batches (2048 VUs, l = 4096,
    0.31 s/proof) + 86 negatives rejected, 0 failures** (art:c1351b8a5b8af38c…).
  - fp8-ada-x4+sha256: same result (art:5b0162d6ff8f2807…).
  - Caveat: the 86-battery's 60 row picks are one per 3-part name prefix and all land on the operand bit rows
    (hash.a[i].b*), before the gadget.  The gadget is still bound by the digest / carry / multiproof negatives.
* 09:13Z r20260925-091132-8c01 (`20-gadget-negs.py`, tree ee00bc4a): supplementary gadget-row negatives on
  fp8-hopper-x4+sha256.  One random row per (digit-normalized name, kind) class of the 73,056 `sha256.*` rows: rounds'
  Σ/σ XOR sels, Maj, Ch prods, a/e limb bits, schedule, feed-forward, h / hout.  **30 of 30 classes rejected, 0 failures**
  (art:bdfcc3b35522ec6e…).
* 09:10Z merged origin/main 94b1c4d2 (GPU committer of commit-gpu, SP1 committed variants) -> ee00bc4a.  Conflicts only in
  the bench test lists (both sides' variants kept); bench + sha256 leaf tests 259 passed.  frame_gpu.ROW_SCHEMES is BLAKE3
  only: SHA-256 row digests stay on the host (numpy compress_np), the word / y trees go to the GPU.
* 09:14Z be1a3bcb: PINS rows fp8-hopper-x4+sha256, fp8-ada-x4+sha256.  09:18Z r20260925-091800-e60f: ligero-verify rebuilt
  (cargo test 33 + 7 + 27 ok), pinned batch ACCEPT on both fixtures (system pinned, 2^-128.05).
* 09:18Z screen r20260925-091800-e60f, l = 8192 p2, 8192 VUs (killed after rep 1: a host-bound timing):
  - commit: 21 s cold, 7.9 s per rep.
  - row chains: 12.3 s per rep, inside t.total.
  - e2e 37.4 s.
  - SHA-256 had no `row_sponges`, so the host numpy fold ran twice (chain witness, then `native` in the trees).
* 09:25Z 88b82757 `Sha256Leaf.row_sponges`: cupy kernel, one thread per row, every block's CV (hash_gpu's compression);
  carry and digests from it; test vs carry_values / native for 8/16-bit, whole and half blocks (9 passed on the pod).
  r20260925-092757-6a32: commit 0.2 s cold, **identical evidence sha256 7561bfae…**, per rep commit 0.065 s, row chains
  0.011 s.  Rep 2 (warm): prover 7.70 s per 8192 VUs, e2e 7.84 s.  Rep 1: 29 s (tests 26 s).
* 09:35Z diagnostics:
  - r20260925-093456-e16a: the fused witness runs in level mode (389 levels, 53k ops): W 19 ms at l = 8192.  The Python
    verify takes 9.8 s per proof: 6.2 s numpy astype, 3.1 s per-VU leaf_bytes.
  - r20260925-093705-64d3, cProfile of a steady proof: 2.29 of 2.49 s is `openings_device.opened_from_pinned`'s numpy
    copy.
  - r20260925-094418-65bd, `23-pinned-bench.py`: **first-touch page faults on this host run at ~20 MB/s**.  A fresh
    91 MB numpy copy takes 4.0-7.0 s; a reused buffer 8 ms.  glibc unmaps its large blocks on free, so every proof
    re-faults its opened columns (M x t).  With `MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12`: one 10 s fault-in, then
    every copy 7-9 ms.  (The 4090's "degraded host memory" at 08:20Z was probably the same.)  Set in `lib.sh` for every
    run from 09:49Z.
  - da74b03e: `leaf_bytes` by a Python-int compression (0.09 ms vs 2.2 ms).
* 09:40Z merged origin/main 3301c435 (steps pin + R1/R2/R4, ligero-steps-pin c8a16e2b) -> 329b3e1a, clean.

## Discrepancies
(none yet)

## FINAL
(pending)
