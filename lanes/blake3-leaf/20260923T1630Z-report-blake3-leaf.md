---
lane: blake3-leaf
kind: report
created: 2026-09-23T16:30Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by blake3-leaf-2 (coordinator)
# Lane blake3-leaf — `leaf/blake3.py`: BLAKE3's compression function in-circuit, the conservative control

CHECKPOINT 30abee8 (18:45Z) — rebased onto `lane/leaf-iface` **720820d** (D2; my registry commit dropped: leaf-iface
adopted it verbatim).  §9 18:00Z / 18:10Z items done in 30abee8: **role in the key** (`verity/blake3-leaf/v1/x` vs `/w`;
the digest header is now `n_chunks + 4 role` so `leaf_bytes(digest_row)` folds with the right key -- red-team NIT, one
constant + a test), `privacy_note` set, Rust `SCHEMES` entry + vectors for both roles.  Two things the D1 conformance
suite (`leaf/conformance_test.py`, fp8-ada = 32-byte columns) demanded that the D0 module did not do: (i) **half-block
columns** -- the unfolded relations carry half a 64-byte block per operand per column, so the gadget now pairs columns
(even column parks its 16 limbs in a carried msg hold, odd column compresses `[hold | own]`; column-uniform, so the even
column's compression is computed and discarded: x1 relations pay 2x the fold's hash rows; `CARRY_ELEMS` 49 -> 65),
(ii) **`leaf_bytes` total on field rows** (the suite feeds random digests and wants injective 32-byte leaves): a
malformed frame maps to `SHA-256("verity/blake3-leaf/malformed-digest/v1\0" || elems LE u32)`, a domain no BLAKE3 root
lands in; the gadget can never pin one (header constant, limbs are bit decompositions).  Schema bumped to
`blake3-keyed/row/v2`; `params_sha256` 6654cdb9…; the x4 pin below is stale until re-gated (in progress).  Laptop:
`leaf/blake3_test.py` 13 passed 1 skipped (torch stub; `importorskip(..., exc_type=ImportError)`).  Pod (pre-30abee8
tree 227e0bc): full `pytest backends/direct/ligero` **250 passed, 1 skipped, 1 failed** in 19 m -- the failure is
`fold_test.py::test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]`, main's own 5d88d70 asserting
`ratio < 4.1` against its own measured 14576 / 3516 = 4.146 (the fixture-bytes assertion before it passes; nothing in
this lane touches relation compiles) -- pre-existing on main, not booked in DISCREPANCIES.md per the rules, flagged here
for the coordinator.  `cargo test --release`: 27 + 7 + 16 = 50 passed (leaf 4 / 4 with the v2 vectors).

CHECKPOINT e51bcf4 (17:35Z) — rebased onto `lane/leaf-iface` 0d7d716 (D0); `leaf/blake3.py` now implements the D0
`LeafScheme` contract exactly (`base.py`): one registry instance for both widths (`digest_elems = carry_elems = 49`:
`[n_chunks | CV_0 | CV_1 | CV_2]` / `[cv | hold_0 | hold_1 | pos]`), the column layout derived from a carried position
row `pos` (0 at the chain start, +1 per column -- sound by the chain constraints) instead of public layout pins, so
`hashchain.compose(rel, "blake3")` needs no compose changes; 1 or 2 blocks per column (x2 / x4 folds).
`compose(fp8-ada-x4, "blake3")` compiles on the laptop: 79 152 rows / column (base 14 875 + private operands 2 816 +
hash 61 362 + digest pins 99), 12 columns / VU = **949 824 rows / VU** (hash alone 736 k = the census).  Laptop tests:
`leaf/blake3_test.py` 11 passed 1 skipped (torch); Rust `leaf.rs` has the BLAKE3 scheme (keyed parent fold; unit test
against the Python vector), `cargo test leaf` 4 passed.  `registry.py`: one additive change (`BUILTIN` lazy import of
in-tree schemes -- leaf-iface, please keep or replace with your own discovery).  Pod vy-blake3-leaf (ghpl8iy5s629sq,
RTX 4090 24564 MiB reference part, Ryzen 9 7950X host, EU-RO-1, $0.74/h) created 17:07Z, BOOTSTRAP_OK 17:27Z; pytest +
4-VU smoke gate of `fp8-ada-x4+blake3` running.  Laptop disk: 200 MB free at 17:20Z (pruned uv cache -> 6.7 GB); no pulls.

CHECKPOINT fc8dbf8 (16:58Z) — CENSUS posted (§1); `leaf/blake3.py` committed with the compression gadget, the keyed-mode
native (== `blake3` package on random rows, both widths) and the chunk-CV framing; no pod yet.  Next: CPU conformance test
(gadget == native through the witness program), then the compose shim / runner for `fp8-ada-x2+blake3`.

## 1. Census (measured by compiling the gadget in a `LigeroCtx`; `python -m backends.direct.ligero.leaf.blake3 [8|16]`)

Design of the 32-bit ARX round in BabyBear (31-bit field): a u32 = 32 boolean rows; XOR = `x + y - 2xy`, one product row
per bit, rotations free; addition mod 2^32 on two 16-bit limbs (`2^33 > p`), the low-limb sum decomposed into
`16 + ceil(log2 n)` bits (n addends), the carry bits added into the high limb -- the `_bits` decomposition IS the modular
addition, so an add costs 34 rows (2 addends) or 36 (3: `a + b + m`).  Per G: 4 adds + 4 XORs = 268 rows.

| item | rows | note |
|---|---|---|
| one compression (7 rounds x 8 G) | **14 880** | 268 x 56 = 15 008 minus the XORs with the constant `d` words of round 1 |
| finalisation `h_i = v_i ^ v_{i+8}` (8 words) | 256 | |
| **per 64-byte block, bit design** | **15 136** | 7 840 bit rows + 7 296 product rows; 448 linear (216 k terms), 15 136 quadratic (246 k terms) |
| per column & operand role (block + `cs ? key : cv` select 16, `cv[4..7]` bits 128, output copy 16, holds 16/chunk, 4-6 pins) | **15 319** (E4M3) / 15 338 (BF16) | 32 / 48 carried (linked) rows per role |
| XOR via `ctx.lookup`, 4-bit table (one-hot: 256 selectors + 8 key bits per nibble, measured) | 264 / nibble = **2 112 / u32** | vs 32 with bit rows: 66x worse. 8-bit table: 65 552 / byte. Rejected. |

Per VU (K = 1536; unshared = every VU hashes its own x row and W column; tile64 = each row hashed once per 64x64 tile, /64):

| relation | bare rows/VU | blocks/VU | hash rows/VU unshared | % of bare | + private-operand rows (13/byte, 19/BF16 word) | **total unshared** | hash rows/VU tile64 | % | total tile64 |
|---|---|---|---|---|---|---|---|---|---|
| fp8-ada (3724 x 48) | 178 752 | 48 (2 x 24) | **735 312** | **+411 %** | +33 792 (+19 %) | **+430 %** (19 747 rows per unit-equivalent, 5.3x) | 11 489 | **+6.4 %** | +25.3 % |
| bf16-hopper (3292 x 96) | 316 032 | 96 (2 x 48) | **1 472 448** | **+466 %** | +58 368 (+18.5 %) | **+484 %** | 23 007 | **+7.3 %** | +25.7 % |

For comparison Poseidon2 (`+hash`, measured by hash-relation): fp8-ada 3769 -> 6210 rows/unit (+1720 hash + 704 private
+ 17 pins = +65 %; 82 560 hash rows/VU).  **BLAKE3 costs 8.9x Poseidon2's hash rows** (15 319 vs 1 720 per unit-equivalent).
Prediction for the pod (fp8-ada 4096 VUs, 4090): Poseidon2 unshared went 0.17 -> 0.69-0.76 s at +65 % rows; at +430 % rows
BLAKE3 unshared should land around **2.5-4 s** and will not fit `l = 16384` on 24 GB (Poseidon2's hashed peak was 10.9 GB at
6210 rows/column; ~40 k rows/column -> `l = 8192` or `4096`).  With tile64 sharing the BLAKE3 hash rows are +6.4 % of the
bare relation -- within the noise of the prover's fixed costs -- so **shared, the leaf choice is free; unshared, BLAKE3 is
a 5x relation.**  Recommendation: run unshared once on the pod for the honest number (that is the deliverable), plan the
column on tile64.

**Granularity finding (design consequence).**  A compression needs the whole 64-byte block in round 1, but a column of the
unfolded relations carries 32 B per operand.  Any column-uniform circuit on 48 columns then runs a full compression per
column and uses half of them (2x the rows above; the alternating-roles trick puts W's last block in column 49), so the
BLAKE3 leaf composes on a **fold** of the relation: the gadget takes 1 or 2 whole blocks per column, i.e. the `x2` fold
(64 B per operand per column; not registered today) or the existing, Rust-verifiable **`fp8-ada-x4`** (128 B per operand
per column = 2 compressions per role per column, 12 columns per VU; fold-private measured rows/VU flat under the fold and
t.total -8..-16 %).  **Built and gated on `fp8-ada-x4+blake3`** (no new relation registered).  Reported rows/VU are
comparable with the unfolded controls; t.total carries the fold's own (small, favourable) effect -- stated in the bench table.

**Framing (decided, as built).**  Rows are 1536 / 3072 bytes > one BLAKE3 chunk (1024 B), so the standard chunk tree
applies (2 / 3 chunks, root = left-heavy parent fold).  In-circuit: exactly the chunk compressions (24 / 48 per row;
`counter = chunk index`, `CHUNK_START` / `CHUNK_END` derived from the carried column position, below), the chunk CVs
published as the digest: `digest_elems = 49` fixed for both widths = `[n_chunks | CV_0 | CV_1 | CV_2]` (a u32 as two
16-bit limbs, low first; the unused slot of an E4M3 row is 0 -- one registry instance must serve both widths because the
D0 registry builds schemes with a zero-argument factory and `leaf_bytes` receives only the digest).  The 1-2 parent
compressions are done natively by the verifier in `leaf_bytes` (Python `leaf/blake3.py`, Rust `leaf.rs`: one compression
per row) so the leaf under the SHA-256 tree is exactly `blake3.blake3(row_bytes, key=KEY).digest()`.  **Keyed mode**
(`KEYED_HASH`, `KEY = b"verity/blake3-leaf/v1"` zero-padded to 32 B, one key for everything): domain separation of the
leaf from other BLAKE3 uses at zero circuit cost (the key words are constants replacing IV in chunks and parents).
Neither the word width nor the role is in the key: E4M3 and BF16 rows are different-length messages (1536 vs 3072 B), the
two roles live in different trees with different bindings, and `leaf_bytes` must not need either.  `schema =
"blake3-keyed/row/v1"`, `params_sha256 = efdd4cc0…` (key + framing constants), `hash_name = "blake3-keyed"`.  Unsalted, as
the Poseidon2 leaf.  Why not a parent in-circuit: it runs once per row after the last block and cannot sit in a
column-uniform chain without a full wasted compression per column; publishing the CVs costs nothing in soundness (a
collision on the CVs or on the parent fold is a BLAKE3 collision).  Why not "one BLAKE3 chunk of 1536 B": not BLAKE3.

**Layout without public pins.**  D0's compose has no scheme-specific public pins, so the per-column layout (chunk start /
end, chunk counter, "this column ends chunk c") is derived from one extra carried element `pos`: the chain forces
`pos_in = 0` at a VU's first column and `pos_out = pos_in + 1` links the columns, so `pos` is a sound private column index;
its 5-6 bit rows give `cs = [pos in starts]`, `ce = [pos in ends]`, `counter = pos >> (4 - log2 blocks_per_column)` and
the hold indicators as products of bit literals (~12 rows per role).  Carried per role: `carry_elems = 49` = `[running CV
(16 limbs) | hold_0 (16) | hold_1 (16) | pos]`; 0 at the chain start = "key, no held CVs, column 0".

## 2. Status / evidence
* `backends/direct/ligero/leaf/blake3.py` (fc8dbf8): `compress_np` (numpy, all rows in lockstep) passes the single-block
  and multi-chunk checks against the `blake3` package (keyed and unkeyed); `Blake3Leaf.native` + `leaf_bytes` ==
  `blake3.blake3(row_bytes, key).digest()` on random E4M3 and BF16 rows, both roles.  Two bugs found on the way, both in
  the framing not the compression: the parent nodes take the KEY (not IV) as their chaining value in keyed mode, and carry
  the `KEYED_HASH` flag.

## 2b. Gate and bench (pod vy-blake3-leaf, RTX 4090 24564 MiB reference part, Ryzen 9 7950X, torch 2.6.0+cu124; tree 4b83172+)

**Gate** `python -m backends.direct.ligero.run --relation fp8-ada-x4+blake3 gate-vu --vus 2048 --batch 512 --device cuda
--auth included-hash`: **49 honest sub-batches (2048 VUs), 86 negatives, 0 failures** (1 m 15 s; evidence
`evidence/gate_fp8-ada-x4+blake3_2048.txt`).  The negative families are hashchain's (digest lanes flipped / swapped,
`is_end` moved, multiproofs corrupted / truncated, roots and bindings swapped, VU claims another's row, committed word
flipped, hashed word bits flipped with the computation unchanged, the carried state broken at a link and non-zero at a
chain start, single-row mutations of hint / prod / inv rows) -- every one rejected, with the linear / quadratic / column
challenge / auth reason strings.  `--batch 512` because the gate's honest self-check (`witness.check_constraints`, torch)
materialised `n_terms x l` (fixed afterwards in 6f3d2a5: column-sliced `apply_sparse`).

**Bench**, all on this pod, `bench-vu --zk --mode interactive --total-vus 4096 --reps 3 --target -128 --device cuda`,
local coins, median of 3 reps (`t.total`), 4096 VUs = 13 sub-batches in every row of the table:

| relation | rows / column | columns / VU | **rows / VU** | l (`--batch`) | peak dev. mem | witness | encode+commit | tests | **t.total** | proof bytes / rep | vs bare | vs Poseidon2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `fp8-ada` bare (`--pipeline 1`) | 3 769 | 48 | 180 912 | 16384 | 3.2 GB | 0.012 | 0.111 | 0.097 | **0.232 s** | 66 MB | 1x | -- |
| `fp8-ada` `--auth included-hash` (Poseidon2) | 6 210 | 48 | 298 080 | 16384 | 10.9 GB | 0.068 | 0.183 | 0.272 | **0.541 s** | 91 MB | 2.3x | 1x |
| `fp8-ada-x4` bare (the fold the BLAKE3 leaf sits on) | 14 875 | 12 | 178 500 | 4096 | 3.1 GB | 0.031 | 0.124 | 0.073 | **0.255 s** | 163 MB | 1.1x | -- |
| **`fp8-ada-x4+blake3`** | **79 152** | 12 | **949 824** | 4096 | 14.7 GB | 0.112 | 3.848 | 1.226 | **7.505 s** | 832 MB | **32x** | **13.9x** |
| `fp8-ada-x4+blake3` | 79 152 | 12 | 949 824 | 2048 | 7.4 GB | 0.165 | 6.934 | 1.336 | 10.04 s | 1 648 MB | 43x | 18.6x |

The brief's controls (fp8-ada bare ~0.17 s, +hash 0.69-0.76 s) are from other hosts / trees; the same-pod controls above
are the comparison.  `rows / VU`: 5.25x the bare relation (the census said 5.3x: 735 k hash rows + 34 k private-operand
rows + the fold's own base), 3.2x Poseidon2's.  `t.total`: 13.9x Poseidon2 -- worse than the row ratio because (i) the
24 GB card caps `l` at 4096 for 79 k-row columns (peak 14.7 GB; Poseidon2 runs `l = 16384`), and (ii) `encode+commit`
is 3.85 s for 1.30 G codeword elements per sub-batch set vs 0.18 s for Poseidon2's 0.41 G -- 7x slower per element at
m = 79 152, n = 16 384 than at m = 6 210, n = 65 536; the encoder / column-Merkle shape effect is worth a look by an
encoder lane (not chased here).  The witness (the new interpreter kernel, 38 k ops / 1.8 M terms per column) is 0.11 s
and not the problem; the fused tests 1.2 s; the remaining ~2.2 s of `t.total` is the 832 MB of openings per rep
(79 152 rows x 200 opened columns x 13 sub-batches: proof size scales with rows too).  The committer (`commit_seconds`
6.8 s per 4096 x rows + 4096 W columns: chunk CVs on the GPU 0.27 s + SHA-256 trees) is the data owner's cost.

**Rust verifier** (`ligero-verify` built from the tree on the pod, `leaf.rs` with the BLAKE3 scheme + the
`(fp8-ada-x4, blake3)` pin): `batch --system system.bin --dir rep1 --target-bits 128` on the `l = 4096` dump -> **13 / 13
ACCEPT, batch ACCEPT (union 2^-128.33), system pinned (fp8-ada-x4+blake3), Python agreement 13 / 13**, 27.7 s CPU / 6.4 s
wall at 6 jobs (`evidence/rust_batch_blake3_b4096.txt`); the BLAKE3 leaves open under the SHA-256 roots through the Rust
parent fold, i.e. the Rust verifier recomputes `blake3(row) = fold(CVs)` without the `blake3` crate.  `cargo test
--release`: the `leaf` tests include the Python test vector (a random E4M3 row: digest elements -> the `blake3`
package's keyed digest) and the malformed-digest rejections.

## 3. Findings on the way (for hostphase / leaf-iface / the coordinator)

* **The fused witness kernel does not scale to this program** (`witness_device.py` table form): 38 032 ops / 1.79 M
  operand terms per column (the XOR outputs are affine forms `x + y - 2xy` that are never re-materialised, so the `b` and
  `d` words of the G function grow to ~50-term expressions over the 7 rounds) generate a 5.1 MB / 49 k-line CUDA source
  that NVRTC had not finished after 12 min at 26 GB RSS (two such compiles in parallel hit the pod's 46 GB cgroup and
  the gate was OOM-killed).  Fix, additive (4b83172): a **program-independent interpreter kernel** (`INTERP_OPS = 16384`:
  op tables `(kind, row, operands)` + the existing `affine` loop; source ~60 lines, compiles in ~1 s; same residues in
  program order, so W is identical -- `witness_device_test.py::test_interpreter_kernel_equals_torch_program` forces it on
  bf16-hopper / fp8-ada and compares with the torch program).  No existing system crosses the threshold (Poseidon2-hashed
  fp8-ada is ~6 k ops), so nothing else changes.
* **`check_constraints` (the gate's honest self-check, torch path) materialises `n_terms x l` int64**: 870 k linear terms x
  l = 4096 = 27.7 GiB -> OOM.  Worked around with `--batch 512` for the gate; a chunked `apply_sparse` would remove the
  limit (not done; witness.py is not mine).
* `registry.py`: `BUILTIN = ("poseidon2", "blake3")` lazily imported by name (D0 imported only poseidon2).

## Discrepancies
(none yet)

## FINAL
(pending)
