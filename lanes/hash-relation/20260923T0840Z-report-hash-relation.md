CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/hash-relation pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
# Lane hash-relation — `authentication = included-hash`: Poseidon2 rows inside the B relation (2026-09-23)

CHECKPOINT d7141ec (10:52Z, FINAL) — MERGEABLE = 9cb1c3e + one `PROTOCOL.md` paragraph (8d: the Poseidon2 witness kernel as a prover implementation
note).  No code change after 9cb1c3e.  Since 10:20Z: the lane-tree committed run re-published with the two prover commits (`r20260923-102322-b55f`,
0.900 s ZK-int, §3 last row; labelled, pushed, snapshot `hash-relation-v2`, §6), and tile 64x64 measured on the merged tree + hook (fp8-ada 0.763 s,
bf16-hopper 1.374 s — equal to the worst case, as expected without the lookup-shared relation; §3).  Lane: `git status --short` empty, no conflict
markers, 25 commits on `lane/hash-relation` over 6babe27.  Pod terminated (§7).

CHECKPOINT 9cb1c3e (10:20Z) — MERGEABLE (prover only; same systems, pins, formats): **the Poseidon2 witness hook.**  A dedicated CUDA kernel
(`hashchain.Poseidon2Witness` / `poseidon2_rows`) writes the two sponges' 1704 S-box rows per unit with the 24-lane state in registers — the permutation
emitted as straight-line code through the same `permute_ring` traversal that compiled the rows — and `witness_device.FusedWitness` drops those product
rows from the fused program (`sys.witness_hooks`), which is v1-sized again (5.9k terms: no table mode).  Merged tree, fp8-ada ZK-int 4096 VUs:
committed **0.861 -> 0.764 s (+89 % over bare 0.403 s)**, encode 0.250 -> 0.137 s (`evidence/merged/merge3_hash_v3.json`), validation passed, Rust
accepts the dump 13/13 with the unchanged `fp8-ada+hash` pin.  Evidence: fused+hook W == torch-program W on the GPU (`evidence/merged/hook_check*`),
hashed gates fp8-ada / bf16-hopper / fp8-hopper 512 VUs + 86 negatives and fp8-ada ZK-int — **0 failures** (`evidence/merged/gates_hook.log`), the
emitted statements executed in Python pass the Poseidon2 KAT (`test_sponge_kernel_source_is_the_permutation`), laptop `pytest backends/direct/ligero`
67 passed / 4 skipped.  **Merge note:** `witness_device.py` conflicts with hp2-host's register-row codegen (`0926f94`); the resolved file is
`evidence/merged/witness_device.py.merged-1bb2194+9cb1c3e` (= `/tmp/hr_merge` 009f454, which the pod ran): thread a `program` argument through
`_Gen` / `_generate_regs` / `_generate_tab` / `generate`, add `_program(sys)`, launch the hooks after the kernel in `run` (68-line diff,
`evidence/merged/witness_device_hook.diff`).  Caveat: the hooked fused kernel's NVRTC compile is ~80 s on the 4090 (main's straight-line register form
on a 1.7k-op program; the table-driven form was 21-28 s), once per pod (cupy disk cache); the `poseidon2_rows` kernel ~13 s.  `LIGERO_DEVICE_SPONGE=0`
restores the program path.

Earlier: CHECKPOINT e3762c3 (10:00Z) — MERGEABLE (now in main), four commits after main's merge point, none touching a system / pin / statement or proof format:
* `605c837` — the `test_boundaries[commitments]` fix (numpy out of `verity.commitments`; below), still needed on main.
* `9d7d93d` — prover only: `hashchain.hash_hints` assembles the 720 appended hint rows as five blocks instead of one copy per row.  Merged tree
  (main 1bb2194 + these) fp8-ada ZK-int 4096 VUs committed **0.978 -> 0.861 s** (hints 0.220 -> 0.167 s), validation passed; bare untouched (0.403 s;
  §3 "Merged tree").  `hashchain_test.py` asserts the block layout equals the per-name layout.
* `fffeb21` — Rust verifier only (`verify.rs` chain test): one encoded coefficient row per constraint *term* (shifted link + start on `W[c_x]`, link on
  `Y_x`, one per end term), `Y_x` / `Y_end` evaluated on the opened column values — the same field value as the old one-row-per-involved-witness-row sum,
  so the same decision, with D x (2 n_links + ends) NTT pairs instead of D x nr (hashed systems ~80 -> 39).  On the pod dumps (13 jobs): **fp8-ada+hash
  CPU 22.7 -> 12.3 s, wall 1.86 -> 1.00 s** per 4096 VUs (sub_00 1.706 -> 0.966 s: ntt 1.00 -> 0.59, chain 0.24 -> 0.07); bf16-hopper+hash 43.7 -> 23.3 s
  (wall 3.61 -> 1.96); bare fp8-ada 5.42 -> 4.78 s (wall 0.446 -> 0.396), bare bf16-hopper 9.45 -> 7.72 s.  All 13 dumps re-verified: every sub-batch
  accepted, python agreement 13/13 (25/25 bf16-hopper).  The Rust hashed / bare verify ratio is now 2.6x (was 4.2x).
* `e3762c3` — Rust test: hashed-fixture proof mutations (w, h, q first / last, an opened capacity-layer row) rejected by the proximity / quadratic /
  chain / Merkle tests (`fp8_ada_hashed_proof_mutations_are_rejected_by_the_chain_and_quadratic_tests`).
Merge test (`/tmp/hr_merge` = main 1bb2194 + 605c837 + the three cherry-picked): `cargo test --release` 21 + 7 + 14 green; `git status --short` empty on
the lane, no conflict markers.  Laptop `cargo test --release` at e3762c3: 20 + 7 + 14.

Earlier: CHECKPOINT 605c837 (09:55Z) — MERGEABLE.  `acf2072` is already in `main` (`a3f9636 Merge commit 'acf2072'` + the coordinator's fix-ups
`1bb2194`: v2 relations carry empty hashed pins, `auth.rs` tests import `sha256` — my `15de026` / `0222482` (D13 renumber) are the same two
changes, they merge as no-ops).  **One commit still to merge: `605c837`** — `packages/verity/tests/test_boundaries.py::test_core_module_imports_only_inward[commitments]`
FAILS on main since the merge (my `poseidon2_babybear.py` / `rowleaf.py` imported numpy inside `verity.commitments`, which the boundary test
forbids); the fix moves the numpy-vectorised evaluations (`permute_np`, `pack_words_np`, `hash_rows_np`, `row_digests`) to
`backends/direct/ligero/poseidon2.py`, the reference package is standard-library only, digests unchanged (tests moved with them).  Merge test
(`lane/hash-relation-mergetest` = 605c837 + main 1bb2194, worktree `/tmp/hr_merge`): the only conflict is the trivial D12/D13 hunk in
`DISCREPANCIES.md` (take main's D12 block, keep D13), then `cargo test --release` 21 + 7 + 13 green and
`pytest backends/direct/ligero packages/verity/tests/test_boundaries.py packages/verity/tests/commitments` 179 passed / 6 skipped on the merged
tree; the merged tree's hashed GPU path re-gated on the pod (§4, "merged tree").
Lane state: `git status --short` empty, no conflict markers; laptop at 605c837: `pytest backends/direct/ligero` 66 passed / 4 skipped,
`pytest packages/verity` 446 passed, `cargo test --release` 20 + 7 + 13; pod (acf2072 tree) `pytest backends/direct/ligero packages/verity/tests/commitments`
126 passed / 1 skipped.

Earlier: CHECKPOINT acf2072 (09:05Z) — everything on `lane/hash-relation` (6babe27..acf2072, 17 commits, 33 files, +2938/-108) — MERGED.
`git status --short` empty, no conflict markers.  Since b07f469 (08:40Z) only docs and one-token hooks: `DISCREPANCIES.md` D12, `PROTOCOL.md` 8d wording, and
`included-hash` added to the store vocabulary (`tools/research/src/research/store/vocab.py` `AUTHENTICATION_VALUES`), the ledger's `--authentication` choices and the
vocab test — the cross-check `test_tables.py::…vocab.AUTHENTICATION_VALUES == contract.AUTHENTICATION` would otherwise fail on the merged tree.  Test status at this
commit: §4 (laptop `pytest backends/direct/ligero`, `pytest packages/verity`, `cargo test --release`, pod full pytest — results appended there as they finish).
Pod gates (b14a5ce tree, GPU): hashed fp8-ada / bf16-hopper / fp8-hopper (2048 honest VUs at l = 16384) 0 failures incl. 86 negatives each, tile 64x64 and `--zk`
interactive 0 failures, bare fp8-ada gate unchanged 0 failures.  Bare path byte-identical (§5).  Committed-column measurements: 13 `research run`s on vy-hash-relation
(§3), Rust accepts all 13 dumps, python agreement 13/13 each; all pulled, labelled, pushed, snapshot `hash-relation-v1` (§6).

Earlier checkpoint: b07f469 (08:40Z) — same code, first mergeable state.

## FOR DEVICE LANES — the committed column, per relation

Same `bench-vu` line as the bare column plus **`--auth included-hash`** (nothing else changes; `--tile 64x64` gives the shared-row tile workload,
see §3 — same prover cost, only the trees differ).  `PYTHONPATH` must include `packages/verity/src` (the committer lives in `verity.commitments`).

~~~
python -m backends.direct.ligero.run --relation fp8-ada     bench-vu [--zk] --mode M --batch 16384 --total-vus 4096 --reps 3 --target -128 --device cuda \
    --auth included-hash --instance-procs 16 --instances-cache /workspace/instances-cache --out $RD/result.json --dump-dir $RD/proofs --dump-reps 1
python -m backends.direct.ligero.run --relation bf16-hopper bench-vu ... --auth included-hash ...
python -m backends.direct.ligero.run --relation fp8-hopper  bench-vu ... --auth included-hash ...
~~~

* Result fingerprint: `authentication = "included-hash"`, `hash = "poseidon2-babybear-w24"`, `sharing = "none"` (or `"tile64x64"`); `statement_format = ligero-statement/v5`;
  extra measurements `relation.hash.*` (rows_added_per_unit, permutations_per_unit, linked_rows, commit_seconds, sponge_seconds, statement_bytes_total, multiproof_bytes_total).
  The bench contract recognises `included-hash` (`contract.AUTHENTICATION`, test in `test_bench_contract.py`).
* The store tool `bench_vu_fp8` keys `auth` / `tile` only when given, so bare derivations are unchanged.
* **First proof of a hashed system compiles its witness kernels: ~100 s of NVRTC on the 4090 with `9cb1c3e`** (the hooked fused kernel ~84 s in main's
  register form + `poseidon2_rows` 13 s; without the hook, 21-28 s table-driven; main's bare kernel itself is ~39 s cold), cached by cupy in
  `~/.cupy/kernel_cache` across processes.  The warm-up sub-batch absorbs it; `t.total` medians do not include it.  Budget it in `--timeout`.
* The committer (`commit_seconds`, 4-13 s for 4096 x rows + 4096 W columns: Poseidon2 row sponges on the GPU + SHA-256 ids trees) runs once per instance set before
  the reps; it is the data owner's cost, not the prover's, and is reported separately.
* **bf16-ampere and fp4-nvf4 are NOT composed** (§8): only the three `relations.py` relations have a committed column.
* Rust: build `backends/ligero-verify` from the merged tree (the v5 statement / v3 system parsers and the three hashed pins are in it); `ligero-verify batch --dir
  proofs/rep1 --system proofs/system.bin --target-bits 128` prints `system pinned (fp8-ada+hash)` etc.
* Build the Rust verifier from a tree that has `fffeb21`: the hashed proofs verify 1.8x faster (12.3 s CPU / 1.0 s wall per 4096 fp8-ada VUs at 13 jobs
  instead of 22.7 s / 1.86 s); it is a verifier-only change, older binaries accept the same dumps more slowly.
* Merged-tree sanity (09:30Z, §3 "Merged tree"): fp8-ada ZK-int 4096 VUs bare 0.403 s vs committed 0.978 s (0.861 s with `9d7d93d`) with `--pipeline 1`.  On my pod (torch 2.6.0+cu124)
  main's default `--pipeline 3` **bare** bench crashes (`Offset increment outside graph capture`) in every mode; if you see it, add `--pipeline 1` to the bare line
  (the hashed runner is sequential regardless).

## 1. Design as built

* **Hash.** Poseidon2 over BabyBear, **width 24, rate 16, capacity 8, output 8 lanes**, S-box x^7, R_F = 8 (4 + 4), R_P = 21, Plonky3's constants, diagonal and M4
  and permutation order (`Plonky3/baby-bear/src/poseidon2.rs`, fetched 2026-09-23; pinned by `CONSTANTS_SHA256 = 0b81af1cdcd7e5b1e0e510b632cc692d3c7c0d5923c4f3e0036bc58f69543321`,
  which the statement carries and both verifiers refuse to differ from).  Known-answer vector `KAT_24` = Plonky3's `test_default_babybear_poseidon2_width_24`; the
  scalar, numpy, torch and ring (`Expr`) evaluations all pass it (`packages/verity/tests/commitments/test_poseidon2.py`, `hashchain_test.py`).
  Width 24 chosen over 16 because rate 16 = exactly one K = 16-lane unit per absorb (one permutation per operand per unit; width 16 would need two).
* **Sponge / absorb order.** Padding-free overwrite mode (Plonky3 `PaddingFreeSponge` shape): capacity initialised to `IV(role, word_bits, n_words) = (role, word_bits, K, 0..)`
  with `role = 1` (x rows) / `2` (W columns) — the two sponges are domain-separated from each other and from other row formats; each unit's 16 elements overwrite the
  rate part, one permutation; digest = rate lanes 0..7 of the final state.  An element carries 16 bits of consecutive words in little-endian word order
  (`pack_words`: one BF16 word, two E4M3 bytes; FP4 would be four nibbles): injective because the widths are range-checked bit rows and the packing is a base-2^w
  positional sum < 2^16 < p.  **Two sponges** (x and W) rather than one with domain separation: the two digests are two independent leaves in two trees (x rows and W
  columns are different objects with different sharing patterns), and one sponge would double the linked state anyway.
* **Gadget** (`backends/direct/ligero/hashchain.py`, relation-agnostic over the three registered relations, composed on top of the unit compilers without editing them):
  operand pins -> hint rows + `word_bits` boolean rows per word with the decode re-established by constraints (18 rows/BF16 word, 13 rows/E4M3 byte), 852 product rows per
  permutation (213 S-boxes x 4: x^2, x^3, x^4, x^7), linear layers as affine expressions (no rows), the 8 capacity lanes of each sponge as linked chain rows
  (`cap - IV`, so a chain start is 0), public pins `hash.is_end` + `hash.d[0..15]` tied by `is_end * (state_out - d) = 0` at the chain end.
* **Chain ends.** 19 linked rows (accumulator 3 + 16 capacity); `chain.py` gives the extra links the coefficients `u_(e mod 6) * u_6^(e div 6 + 1)` (monomials of the seven
  existing families — `N_FAMILIES` is fixed by `protocol.py`, which I must not edit); the 3-link tables are byte-identical to before (`test_chain_tables_extend_the_three_link_case`).
  Soundness: the chain identity has degree <= 4 in the families instead of 1 -> a factor <= 4 on a 2^-17x field term; immaterial, not in `soundness()`.  System file
  `ligero-system/v3` (`LIGSYS03`) records the link count; Rust reads v1/v2/v3.
* **Statement v5** (`LIGSTM05`): v4 header (K = words per committed row) | `u8 y_bytes` | `str relation` | `str "included-hash"` | `n_vus x 16` digest lanes (`<u4`, canonical)
  | `l` y words | block `str "ligero-b/auth/v2h"` | `str "poseidon2-babybear-w24/row/v2h"` | 32 B `CONSTANTS_SHA256` | `u32 n_vus` | `n_vus x (u32 vu_index, x_index, w_index)`
  | 3 tree refs (binding, owner, count, root: the D9 layout) | 3 multiproofs (`u32 n_sib | 32 B each`).  The statement digest absorbs the block (version, schema, parameters digest,
  indices, tree refs) through the relation tag and the digests + y words in the body; siblings are auxiliary.  A v5 fp8-ada statement for 341 VUs is ~91 kB, of which 65 kB is
  the v4-style `l`-word y table (only the chain-end columns are nonzero; v6 could store `n_vus` words).
* **Committer** (`packages/verity/src/verity/commitments/{poseidon2_babybear,rowleaf}.py`, `backends/direct/ligero/hashauth.py`): `leaf/v2h` — tree `a` one leaf per x row
  (Poseidon2 digest of the row as 32 big-endian bytes, schema `poseidon2-babybear-w24/row/v2h`), tree `b` one leaf per W column, tree `y` the output words as in D9;
  SHA-256 ids tree / framing / domains / multiproofs of `verity.commitments` unchanged.  Gadget digest == committer digest on random rows for all three relations (test).
* **Verifiers.** Python `protocol.verify` unchanged; `HashedRelationRunner.verify_vus` / `serialize.verify_files` check the pins against the statement and the multiproofs
  against the roots (`hashauth.verify_hash_auth`).  Rust `ligero-verify`: `format.rs` v3 system + v5 statement (bounded lengths), `relation.rs` hashed pins per relation,
  `verify.rs` hashed statement digest / public pins / chain test with n_links links, `auth.rs check_hashed` (Poseidon2 leaves -> SHA-256 folds), fixture `fixtures/fp8-ada-hash`.

## 2. Census (rows per unit; per VU = x 96 units for bf16-hopper, x 48 for the FP8 relations)

| relation | bare rows/unit | private-operand rows | hash rows (2 permutations) | digest pins | hashed rows/unit | +% | rows/VU added | linked rows |
|---|---|---|---|---|---|---|---|---|
| bf16-hopper | 3292 | +608 (32 BF16 words x 19) | +1720 (2 x 852 + 16 end ties) | +17 | **5637** | +71.2 % | +225,120 (x96) | 19 |
| fp8-hopper | 3396 | +704 (64 E4M3 bytes x 11) | +1720 | +17 | **5837** | +71.9 % | +117,168 (x48) | 19 |
| fp8-ada | 3769 | +704 | +1720 | +17 | **6210** | +64.8 % | +117,168 (x48) | 19 |

Quadratic constraints: fp8-ada 3532 -> 6020, bf16-hopper 3164 -> 5524, fp8-hopper 3164 -> 5652; linear 589 -> 606 / 339 -> 356 / 554 -> 571.
Public table `(l, 17)` instead of `(l, 193)` / `(l, 97)`.  **Tile (64x64)**: identical rows — the prover still hashes both rows of every VU (`sharing = none` in the
relation); only the trees (64 + 64 leaves) and the multiproofs shrink (14 kB -> 7 kB per 4096 VUs).  The lookup-bound "hash each distinct row once" version (spec §6)
is not built (§8).  Hashed rows per VU as a function of tile / l: constant 2 x 48 (or 2 x 96) permutations per VU in this build.

## 3. RTX 4090 (vy-hash-relation, EPYC 7763 host, load ~10-26): fp8-ada, K = 1536, 4096 VUs, l = 16384 (13 sub-batches of <= 341 VUs), 3 reps, rep 1 dumped

Native peak 330.3e12 FLOP/s (fp8-ada); 989.4e12 (bf16-hopper) and 1978.9e12 (fp8-hopper) for the Hopper rows.  `t.total` = median of 3 reps of the prover wall
(4096 VUs); Python verify = the runner's in-process verifier (GPU); Rust = `ligero-verify batch` on the rep-1 dump on the pod (13 jobs x 1 thread; CPU sum / wall).

| run | relation | column | mode / class | rows/unit | t.total (s) | ms/VU | overhead vs native peak | proof MB (bytes/VU) | statement bytes | Python verify (s) | Rust CPU sum / wall (s) | bits | commit (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r20260923-080108-ca9c | fp8-ada | bare (v4) | non-ZK interactive | 3769 | **0.640** | 0.156 | 1.68e7 | 60.0 (14642) | 14,484,392 | 0.559 | 5.5 / 0.46 | 128.52 |  |
| r20260923-081059-8ff6 | fp8-ada | **committed (v5)** | non-ZK interactive | 6210 | **1.062** (+66 %) | 0.259 | 2.79e7 | 84.7 (20685) | 1,182,597 | 0.873 | 22.4 / 1.80 | 128.52 | 11.2 |
| r20260923-081405-f700 | fp8-ada | committed, tile64x64 | non-ZK interactive | 6210 | **1.010** | 0.247 | 2.65e7 | 84.7 (20685) | 1,175,685 | 0.785 | 22.6 / 1.82 | 128.52 | 1.7 |
| r20260923-080502-e138 | fp8-ada | bare (v4) | ZK interactive (COMPLETE_ZK_BACKEND) | 3769 | **0.569** | 0.139 | 1.49e7 | 66.1 (16127) | 14,484,392 | 0.459 | 5.6 / 0.46 | 128.32 |  |
| r20260923-081227-ac87 | fp8-ada | **committed (v5)** | ZK interactive | 6210 | **1.147** (+102 %) | 0.280 | 3.01e7 | 90.9 (22201) | 1,182,597 | 0.772 | 22.6 / 1.82 | 128.32 | 4.4 |
| r20260923-081455-e50f | fp8-ada | committed, tile64x64 | ZK interactive | 6210 | **1.045** | 0.255 | 2.74e7 | 90.9 (22201) | 1,175,685 | 0.712 | 22.0 / 1.78 | 128.32 | 1.3 |
| r20260923-080538-bc48 | fp8-ada | bare (v4) | ZK fiat-shamir (COMPLETE_HVZK_BACKEND) | 3769 | **0.641** | 0.156 | 1.68e7 | 89.6 (21863) | 14,484,392 | 0.563 | 7.0 / 0.57 | 128.32 |  |
| r20260923-081315-9f58 | fp8-ada | **committed (v5)** | ZK fiat-shamir | 6210 | **1.028** (+60 %) | 0.251 | 2.70e7 | 126.0 (30757) | 1,182,597 | 0.869 | 27.4 / 2.21 | 128.32 | 4.6 |
| r20260923-081543-d32f | fp8-ada | committed, tile64x64 | ZK fiat-shamir | 6210 | **1.168** | 0.285 | 3.07e7 | 126.0 (30757) | 1,175,685 | 0.878 | 27.8 / 2.30 | 128.32 | 1.2 |
| r20260923-081851-3955 | bf16-hopper | bare (v4) | ZK interactive | 3292 | **0.863** | 0.211 | 6.78e7 | 118.0 (28815) | 27,035,500 | 0.800 | 10.4 / 0.46 | 128.05 |  |
| r20260923-081632-0fb3 | bf16-hopper | **committed (v5)** | ZK interactive | 5637 | **1.880** (+118 %) | 0.459 | 1.48e8 | 164.2 (40094) | 1,166,357 | 1.404 | 46.0 / 1.95 | 128.05 | 8.1 |
| r20260923-082033-2e0f | fp8-hopper | bare (v4) | ZK interactive | 3396 | **0.491** | 0.120 | 7.71e7 | 62.3 (15199) | 14,484,431 | 0.432 | 5.1 / 0.42 | 128.32 |  |
| r20260923-081743-40d3 | fp8-hopper | **committed (v5)** | ZK interactive | 5837 | **0.995** (+103 %) | 0.243 | 1.57e8 | 87.1 (21273) | 1,182,636 | 0.781 | 22.0 / 1.77 | 128.32 | 13.1 |
| r20260923-102322-b55f | fp8-ada | **committed (v5), lane tree d7141ec** (hint blocks + Poseidon2 witness hook; NOT main's prover) | ZK interactive | 6210 | **0.900** (+58 % over e138) | 0.220 | 2.36e7 | 90.9 (22201) | 1,182,597 | 0.783 | 12.6 / 1.03 (post-fffeb21 verifier) | 128.32 | 5.6 |

The last row is the published `research run` of the lane tree after the two prover commits (`9d7d93d`, `9cb1c3e`): same 13 dumps format, validation passed
(13/13 accepted cold from bytes, v5), split hints 0.157 / witness 0.035 / encode 0.129 / merkle 0.074 / tests 0.404 / openings 0.062; relative to the same
tree's ac87 run (1.147 s) the two commits are -22 %.  The merged-tree numbers below (0.764 s, +89 %) are the ones that predict the morning table.

Reading: the committed column costs **+60 % to +118 % prover wall** (the spec's cost model said +70-88 %; the ZK-interactive rows land at +102 / +103 / +118 %, the
non-ZK / FS rows at +60-66 %; run-to-run noise on this shared host is ~10 %: the bare ZK-int 0.569 s vs non-ZK 0.640 s is the same code), proof bytes **+38-41 %**
(with the rows), the statement **12-23x smaller** (roots + indices + digests + y table + multiproofs instead of the operand words), Python verify +45-75 %, Rust verify
CPU **4x** (22 s vs 5.5 s per 4096 VUs; wall 1.8 s vs 0.46 s at 13 jobs) — attributed below.  Soundness bits unchanged (same l, t, n).  Peak device memory 3.1 -> 10.9 GB
(the table-driven witness kernel's coefficient tables and the 1.65x rows).  The prover split (hash-int-zk): hints 0.29 s (of which the gathered row sponges are ~0),
fused witness 0.15 s (bare 0.019), encode 0.12 s (bare 0.081), tests 0.40 s (bare 0.21), openings 0.10 s.
Rust attribution (hash-int-zk sub_00, 1 thread: total 1.49 s = ntt 1.00 + chain 0.24 + quadratic 0.14; bare 0.19 s): the chain test encodes one coefficient row per
*involved* row (`d x nr` NTTs of length l), and the capacity links' Y expressions are 24-term affine forms over the final S-box layer, so nr grows from ~10 to ~80.
A first fix landed (b07f469: the per-column linear search of those terms cost 1.05 s -> 0.24 s); the next is to materialise `cap_out` as 16 explicit rows per unit
(nr ~ 40, `ntt` halves) — not done.

**Merged tree (main 1bb2194 + 605c837, pod, 09:30Z), fp8-ada ZK interactive, 4096 VUs, 3 reps, `--pipeline 1`, no dumps:** bare **0.403 s**
(hints 0.079, encode 0.081, merkle 0.040, tests 0.187, openings 0.010), committed **0.978 s (+143 %)** (hints 0.220, encode 0.260 — the commit graph now
includes the witness kernel, so this is my table-driven kernel ~0.13 s + 1.65x encode —, merkle 0.063, tests 0.350, openings 0.039); rows 3769 / 6210, proof
66.1 / 90.9 MB, 128.32 bits both.  hp2-host's merged prover made the bare column 30 % faster (0.569 -> 0.403 s) while the hashed-specific costs (hint
assembly +0.14 s, table-driven witness kernel +0.11 s) did not shrink, so the relative overhead rose from +102 % to +143 %; those two items are now
~45 % of the delta and are the cheapest hill-climb (§8).  With `9d7d93d` (hint blocks) the committed run is **0.861 s (+113 %)**: hints 0.167, encode
0.250, merkle 0.062, tests 0.347, openings 0.013 (`evidence/merged/merge3_hash_v2.json`).  The table's "Rust CPU sum / wall" column is the verifier
*before* `fffeb21`; after it (same dumps, same pod): fp8-ada+hash 12.3-12.5 s / 1.00 s (non-ZK and ZK-int), 15.7 s / 1.27-1.29 s (FS), bare fp8-ada
4.8-4.9 s / 0.40-0.47 s (6.1 s / 0.50 s FS), bf16-hopper+hash 23.3 s / 1.96 s vs bare 7.7 s / 0.64 s, fp8-hopper+hash 12.4 s / 1.01 s vs bare 4.8 s / 0.39 s
(`evidence/rust_batch_pod_v3.txt`).  With `9cb1c3e` (Poseidon2 witness hook) the committed run is **0.764 s (+89 %)**: hints 0.165, encode 0.137
(1.7x bare = the 1.65x rows), merkle 0.068, tests 0.356, openings 0.013 (`evidence/merged/merge3_hash_v3.json`; rep-1 dump Rust 13/13 accepted,
12.6 s CPU / 1.03 s wall).  NVRTC on this pod, cold cache: bare fp8-ada register-form kernel 39 s, hooked hashed 84 s, `poseidon2_rows` 13 s,
the table-driven hashed kernel 28 s (`evidence/merged/nvrtc_times.txt`).

**All three relations on the merged tree + hook (10:20Z; ZK interactive, 4096 VUs, 3 reps, `--pipeline 1`, validation passed, `evidence/merged/merge3_*.json`):**

| relation | bare t.total (s) | committed t.total (s) | overhead | committed split: hints / encode / merkle / tests / openings (s) | proof MB bare -> committed |
|---|---|---|---|---|---|
| fp8-ada (3769 -> 6210 rows) | **0.403** | **0.764** | **+89 %** | 0.165 / 0.137 / 0.068 / 0.356 / 0.013 | 66.1 -> 90.9 |
| bf16-hopper (3292 -> 5637) | **0.761** | **1.452** | **+91 %** | 0.241 / 0.231 / 0.111 / 0.764 / 0.054 | 118.0 -> 164.2 |
| fp8-hopper (3396 -> 5837) | **0.383** | **0.762** | **+99 %** | 0.144 / 0.131 / 0.062 / 0.364 / 0.013 | 62.3 -> 87.1 |

(The bare column here is hp2-host's merged prover on this pod; the committed column is the same tree with `9d7d93d` + `9cb1c3e`.  The spec's cost
model said +70-88 %; the hashed-specific extras beyond the 1.65-1.72x rows are now the ~0.09 s hint decode and nothing else.)

**Tile 64x64 on the merged tree + hook (10:48Z; same flags + `--tile 64x64`, `evidence/merged/merge3_tile_*.{json,log}`):** fp8-ada **0.763 s**
(hints 0.162 / encode 0.139 / merkle 0.068 / tests 0.355 / openings 0.014; reps 0.761 / 0.756 after warm-up; commit 1.4 s for 64 x rows + 64 W
columns + 4096 y words vs 5.6 s for 4096 + 4096), bf16-hopper **1.374 s** (hints 0.224 / encode 0.233 / merkle 0.113 / tests 0.731 / openings 0.024;
commit 2.3 s), validation passed, 128.32 / 128.05 bits, same rows (6210 / 5637) and proof sizes (90.9 / 164.2 MB) as `sharing=none`.  As stated
in §2/§8: the tile workload today changes only the *commitment* (64 + 64 distinct leaves instead of 8192) and the statement; the relation still hashes
both operand rows in every VU, so the prover wall is the worst case's (0.763 vs 0.764 s).  The lookup-shared relation (hash each distinct row once, bind
the VUs' operand wires through a LogUp table) is the unbuilt item that would take the committed column from +89 % toward +1 % on this workload.

**Caveat for whoever runs the bare column on a torch 2.6.0+cu124 / driver 610.57 / cupy 14.2
pod:** main's default `--pipeline 3` bare `bench-vu` crashes in every mode (ZK interactive, ZK fiat-shamir, non-ZK) with
`RuntimeError: Offset increment outside graph capture encountered unexpectedly` (`evidence/merge_bare_p3.log` etc.); `--pipeline 1` runs.  The hashed
runner never enters the pipelined path (`not hashed` guards), so the committed column is unaffected.  This is not a hash-relation change: same crash
with `--auth` absent on the merged tree; my lane tree (pre-merge) has no pipeline.

Store: attempts published by `research run --tool bench_vu_fp8` (campaign `r23-hash-relation`); `research data pull` of the `proofs` artifacts, labels
(`authentication=`, `hash=`, `sharing=`, `note=`; no `verified=`), `push --pending` and snapshot `hash-relation-v1`: §6.

## 4. Evidence

* **Gates (pod, GPU, `evidence/gates_run2.log`, `gates_run3.log`):** hashed fp8-ada 2048 VUs / 7 sub-batches at l = 16384 + 86 negatives; hashed bf16-hopper 2048 VUs /
  13 sub-batches + 86 negatives; hashed fp8-hopper 2048 VUs + 86; fp8-ada `--zk` interactive 64 VUs + 86; fp8-ada tile 64x64 512 VUs + 86; bare fp8-ada 64 VUs + 92 —
  **all 0 failures** after two negatives-battery fixes (an `inv` helper row mutated where `t = 0` leaves it unconstrained — now mutated where `t != 0`; in a tile VUs 0
  and 1 share the x row, so "computed on VU 1's x row" was an honest proof — the second VU is now one on another x row and W column).  The 86 hashed negatives: x / W
  digest lane flipped, digests swapped between VUs, `is_end` moved, each multiproof truncated, x root replaced by the W root, tree binding changed, VU 0 claiming VU 1's
  leaf with a different digest, W index out of range, a multiproof missing, one word of the committed x row flipped (computed on the flipped row), computed on the other
  VU's W column / x row while claiming its own, a hashed bit row flipped under an unchanged computation, a broken capacity link, a nonzero sponge start, and one witness
  row per (scope, class) of the gadget — every one REJECTED by the Python verifier; the Rust side rejects the same statement-level mutations on the fixture (11 in
  `tests/relations.rs`) and the block-level ones in `auth.rs` (14 mutations of the parsed block: digest lanes, siblings, roots, binding, swapped W column, foreign x row,
  y word, ranges, counts).
* **pytest (605c837):** laptop `pytest backends/direct/ligero` 66 passed / 4 skipped (`hashchain_test.py` 12: census for the three relations, gadget ==
  committer digest, v5/v3 round trips, negatives, tile layout, torch permutation KAT, numpy == scalar Poseidon2, fused-source modes, precomputed sponges);
  `pytest packages/verity` 446 passed (incl. `test_boundaries` — see the checkpoint header: the numpy split was needed for it); `backends/numerical/tests/bench`
  155 passed / 5 skipped (`included-hash` recognised by the contract, the vocab cross-check); `tools/research/tests` 162 passed / 1 skipped.  Pod (acf2072 tree,
  `OMP_NUM_THREADS=16`): `pytest backends/direct/ligero packages/verity/tests/commitments` 126 passed / 1 skipped in 102 s.
* **Merged tree (main 1bb2194 + 605c837) on the pod, GPU:** `evidence/merge_gates.log` — pytest hashchain/witness_device/boundaries 20 passed; the hashed
  gates of the three relations, the ZK-interactive and tile gates, the bare gate and a 1024-VU committed vs bare `bench-vu` timing sanity run: results
  appended at the end of this note (§10) as they finish.
* **cargo test --release:** 20 unit (incl. `hashed_fixture_block_folds_and_every_mutation_is_refused`) + 7 fixture + 13 relations (incl. the three hashed tests) — all
  pass at 605c837 (the `sha256` test import that b07f469 had dropped is back: `cargo test` did not compile at the 08:40Z checkpoint — the coordinator's fix-up
  `1bb2194` and my `15de026` are the same line).  On the merged tree: 21 + 7 + 13.
  Fixture `fixtures/fp8-ada-hash/` (system.bin 926 kB, sub_00.{stmt 6.2 kB, proof 4.9 MB, coins}, manifest.json): a laptop CPU dump, 20 VUs, l = 1024, interactive non-ZK.
* **Rust pins** (`relation.rs`): fp8-ada+hash `sys_id c4c4b403e07da47f7747b947ad76899ef231112bcc6d62dc0448a83ef8696618` / table `c0e2f48119e2c83ca81cbc8eb1cbba51a676b67a600b8125d75bf438b770e05d`;
  bf16-hopper+hash `3c7570fa029de39af30363599480c7a7bdbb51ba8e5fbe552a852b2ffb0ba1e1` / `def0ccdae79f092f41bc35ecd054ad64e54e2cfe9769c8cec41737c1ebab6617`;
  fp8-hopper+hash `141a5fdd5ea2314ba7070f35d8eae1cb649c554589b1065033e5382580587c97` / `801ca79f0f8c5c77e6b90758614acadfc4e20688442e616e756dbd14a464144d`.
  The pod dumps' `system.bin` carry exactly these (`system pinned (fp8-ada+hash)` etc. in `evidence/rust_batch_pod_v2.txt`); a v5 statement against the bare system and a v4
  statement against the hashed system are refused by the pin.
* **Rust on the dumps:** all 13 runs' rep-1 dumps: every sub-batch accepted, batch ACCEPT at the union bound, python agreement 13/13 (25/25 for bf16-hopper).

## 5. Bare path byte-identity

Laptop, deterministic mode (`bench-vu --device cpu --mode fiat-shamir` non-ZK: no coins, no masks), `git archive 6babe27` vs the lane tree, same flags
(`--batch 960 --total-vus 20` fp8-ada, `--total-vus 10` bf16-hopper / fp8-hopper): **`system.bin`, `sub_00.stmt`, `sub_00.proof` sha256-identical for all three
relations** (`evidence/bitexact_bare_cpu.txt`: fp8-ada system `cba9a09f...` = the pinned bare system, proof `65ebbabd...`; bf16-hopper `5bba40df...` / `9deedadc...`;
fp8-hopper `968d99d6...` / `14cc6157...`).  Mechanically: the v1 systems' fused-kernel source is unchanged (`generate(sys) == generate(sys, None)`, asserted),
`chain.py`'s 3-link tables are unchanged (test), `protocol.py` untouched; the pod's bare dumps carry the pinned bare `sys_id`s (Rust `system pinned (fp8-ada)`) and the
bare gate is 0 failures.  The interactive / ZK dumps differ run to run by construction (verifier coins, os.urandom masks), as every lane has noted.

## 6. Artifacts / store

All 13 attempts pulled from the pod (`research data pull <run> --from vy-hash-relation --project verity`, `evidence/data_pull.txt`), labelled
(`evidence/labels.txt`: `authentication=excluded|included-hash`, `hash=none|poseidon2-babybear-w24`, `sharing=none|tile64x64`, `note=…`; `--by hash-relation --ref <run>`;
no `verified=`), `research data push --pending` 21/21 + 5/5 preserved on `s3://verity-dev` (sha256 read-back), snapshot
**`hash-relation-v1` = `art:d1326003c89dd279ed021fbddb617d589450281af040529517b7d11a974b4cd6`** (52 members: result + run_files + events + resources of every run; pushed).
Each `run_files` artifact is the run directory with `proofs/{system.bin, manifest.json, rep1/sub_NN.{stmt,proof,coins}}` (the v5 statements carry the roots, indices,
digests and multiproofs — no separate roots/paths files are needed).  Store tool `bench_vu_fp8@1`, campaign `r23-hash-relation`, source commit `9e7404f` (the tree the
runs were made from; the later commits are Rust-verifier speed, docs and the vocab hook).

| run | attempt | result | run_files (dumps) |
|---|---|---|---|
| fp8-ada bare non-ZK int | `r20260923-080108-ca9c` | `art:1f6d59408aec3390f627af63d0b600c7123b4b5e72afc65ea2484482cce73cc5` | `art:33257945a367f20c0b9b685264fb4552bdc039c53d98629def89b798b6149e3a` |
| fp8-ada bare ZK int | `r20260923-080502-e138` | `art:a49d6b226001d05ef6576f7def165767e0bd773f8081eee3fc7d154cd252b719` | `art:b5a6b9afd6f1dc225b299f19c21d3c7e5422b0fd87036476721fc483c21c50a6` |
| fp8-ada bare ZK FS (not for the table) | `r20260923-080538-bc48` | `art:23871c70ae9abc64e63c21ab2bb316a849d1d28e1b65520cbc43f66f220c6b6f` | `art:e4bf9db41130eb04acbe8274b8b74d1539f1f0523166741fa7627556d3a8680b` |
| fp8-ada committed non-ZK int | `r20260923-081059-8ff6` | `art:43de03f82b727892fa91dc0fcafcb798501e8774402904647518dac3dd7db65e` | `art:cc135aba7288644059507c606608be73ec577e68a6933ff84de43547f23fa920` |
| fp8-ada committed ZK int | `r20260923-081227-ac87` | `art:bb0641e7d221f2493a1d0846582bbf1aa5670d723fe995c854ef215165608ffa` | `art:087569f6a1a88610733358011173fdba5aed7da754ad7e2952f2cc5b238c4fbd` |
| fp8-ada committed ZK FS (not for the table) | `r20260923-081315-9f58` | `art:b2e5a3858bd2272a1a373a40508b12e42d738b77772ff0831baaaf296cf81d7b` | `art:d6866592920325f118e8c6865f19f3a5d3efddb4f2a04f240b57e664ba7da144` |
| fp8-ada tile64x64 non-ZK int | `r20260923-081405-f700` | `art:fb207e4819a8bb36487dd1026339b028b42484b2b4390c844bdf5fe4e81d63fc` | `art:7f98de4cf2f7b61a38fd67acb81989045c5c89d8cdf02a6bde8f3a04cfb19a72` |
| fp8-ada tile64x64 ZK int | `r20260923-081455-e50f` | `art:d4cf8d42be492f3eda44d31159cc914f314d483fdb79035340fc61713a2c060d` | `art:b3078b25181cac5fa83f827e7f6bb4c4da69028ec68907ef621bbc412c8405ed` |
| fp8-ada tile64x64 ZK FS (not for the table) | `r20260923-081543-d32f` | `art:8fa0aa3aa74a75a61cb66213e1f44d4b2fa0709f4b6e13760d960b0fe7913443` | `art:5070ffb2636b28b7d88c884e21f30ca554271872252d8c96e31a6ddeed199da3` |
| bf16-hopper committed ZK int | `r20260923-081632-0fb3` | `art:c62e93024bc8aa6ac389f63c55201c0629339ed5696797f9fcd08adbc91fede3` | `art:537d1db23306ddf860d3a559f1a9a5089253bf2b580557b9e81109087e81ee5d` |
| fp8-hopper committed ZK int | `r20260923-081743-40d3` | `art:49ae28d6ea203585f7e20f065e704364e2fd093e17d25460b0eb84ff058b183b` | `art:39d1f10ed0d76526e21e4ed34d579a24ee491990e6cb4e864ba619831758ca3e` |
| bf16-hopper bare ZK int | `r20260923-081851-3955` | `art:65e924ab7b7de86e21aa4d81d60bfb7135f6c0f074914a3212ba6628a218fa7f` | `art:e8dc9a62135ca638fb48332769f9ef86c27c9de0d3c987b75a46c2efb3411f4c` |
| fp8-hopper bare ZK int | `r20260923-082033-2e0f` | `art:b94ea4a2f2c30004b109b6f4a39503df19dc9c8cf8f48cdc980952500f3b8526` | `art:0b202aee717b248499901d13cc3c32cc6a76acf1a16378559cb7ee0c6e38d025` |
| fp8-ada committed ZK int, lane d7141ec (hint blocks + witness hook) | `r20260923-102322-b55f` | `art:1967f2bb23ff25a7aac689636b44cc66458327384bc026c989253316c08ffcd7` | `art:5bd0fc93703518fe0b1c8484bb80f894c9cbb22aeb1c95afe5b2d85b635293d2` |

The 14th run (10:23Z) is labelled like the others (`authentication=included-hash hash=poseidon2-babybear-w24 sharing=none note=…witness hook…`), pushed
(`push --pending` 20/22 + 9/9 preserved; the two "not preserved" were already on R2), and is snapshot **`hash-relation-v2` =
`art:d0d6821938cae69ebef372381bda6217aba587a8fe52daed9ca059434467dd28`** (result + run_files of `r20260923-102322-b55f` only — `hash-relation-v1` stays the
13-run snapshot; both pushed).

Two things to know when reading the records: (a) the three `ZK fiat-shamir` runs were made by my bench driver mirroring the hostphase §8 command lines before I
re-read "No FS runs" — they are labelled `note=… NOT for the morning table` and are useful only as verifier test material; (b) the `research` tool redacts the value of
any argv flag named `--auth` in the attempt record (`"--auth", "<redacted>"`), so the *record* does not say `included-hash` — the `authentication=` label, the result
fingerprint inside `result.json` and the `key_params` (`auth`) do.  Worth a rename (`--authentication`) or a redaction allow-list in the tool.

## 7. Pod accounting — vy-hash-relation `wqqv264xfq31id` (RTX 4090 24564 MiB, SECURE, EPYC 7763 host, $0.74/h)

Created 06:19Z (bootstrap run r20260923-062724-60b1), **terminated 10:51Z** (`research pods terminate wqqv264xfq31id` -> "terminated"; absent from
`research pods list` 20 s later, the other lanes' pods untouched): **4.5 pod-hours ≈ $3.35** of the 7 h / $5 budget.  `~/.research/machines.toml` entry
marked TERMINATED.  Everything the pod produced that the note cites is under `evidence/` (gate logs, merge logs, `merged/merge3_*.{json,log}`, Rust batch
outputs, NVRTC timings, `pytest_final.txt` 126 passed / 1 skipped, `merged/pytest_hook.txt` 199 passed / 1 skipped) or in the store (the 14 runs' dumps).

## 8. What remains, ranked

1. **Sharing proper (spec §6):** hash each distinct row once in dedicated hash-only chain units and bind every VU's operand word wires to the hashed row by a lookup /
   LogUp multiset over (row_id, position, word) — the FP4 relation's lookup machinery is the template.  Expected: the +1720 hash rows/unit become +1720 per 96 units
   amortised over the 64 VUs sharing a row (~+18 rows/unit) plus ~1 lookup row per operand word (+32 or +64 rows/unit): +3-5 % instead of +65-72 %.  This is the
   headline for column 2; the present tile numbers are the worst case measured on the tile workload.
2. **Prover-side hashed overheads (no system change):** DONE for the witness kernel (`9cb1c3e`: the Poseidon2 rows come from a register-resident
   permutation kernel, 2.2 ms per 16384-column sub-batch instead of ~11 ms table-driven; encode is now rows-proportional).  What is left of the
   0.36 s delta on the merged tree (0.764 vs 0.403 s): ~0.09 s hint assembly beyond the bare relation's (`hr.rel.public_vectors` re-decoding the
   now-private words into the 192 e/m/s hint rows, the bit rows, the sponge gathers — a fused "operand hints" kernel or moving the e/m/s rows into the
   witness program would take most of it, the latter changing `sys.hints` and the pins) and the rows-proportional rest (encode / merkle / tests at
   1.65x rows, ~0.27 s), which only fewer rows (sharing, item 1) can cut.  Floor without sharing: ~+66 %.
3. **Verifier cost:** `fffeb21` took the Rust chain test from D x 80 to D x 39 NTT pairs (hashed CPU 22.7 -> 12.3 s per 4096 VUs); the remaining ntt
   0.59 s per sub-batch is 234 chain-coefficient encodes + the linear / quadratic rows — the next cut is a smaller `n_links` (fewer capacity lanes to
   link: not without changing the hash) or evaluating the 16 capacity-link coefficient rows' encodings jointly (they are products of the same seven
   family rows, so no linear merge).  Python `protocol.verify` still does one row per involved witness row (hp2-host's file).  Store `n_vus` y words instead
   of `l` in v5 (statement 91 kB -> 26 kB per sub-batch).
4. **Cheaper permutation:** width 16 (rate 8: two permutations per operand per unit, 4 x 16 + 13 = 77 S-boxes each = 308 rows -> 616 per operand per unit, *more* than
   width 24's 852 — width 24 stays); fewer rows per S-box: **not available** with Ligero's `a * b = c` rows — x^7 needs x^2, then x^3 (= x^2 x) and x^4 (= x^2 x^2) or
   x^6 (= x^3 x^3), then x^7: four product rows, and BabyBear has no lower permutation degree (3 and 5 divide p - 1).  What *is* available: hashing only the
   `word_bits`-checked *elements* — already done (one element per BF16 word / E4M3 pair) — and the two sharing levers (item 1 and the BF16 pair packing below);
   packing two BF16 words per element (rate 16 elements = 32 words = two units per absorb: one permutation per two units per operand, -50 % hash rows; soundness of the
   packing as `pack_words` already argues: range-checked, positional sum < 2^32 < p... **no**: 2^32 > p = 2^31 - 2^27 + 1, so two 16-bit words do NOT fit one BabyBear
   element injectively without a range argument; 31 bits do (16 + 15), i.e. only for narrower words — E4M3 pairs already pack; BF16 pairs would need a 3-element / 2-word
   scheme).
5. **bf16-ampere and fp4-nvf4 committed columns:** bf16-ampere runs through `unit.py`'s legacy runner (not `relations.py`), fp4-nvf4 through `fp4/` with lookups, packed
   4-bit words and 3-component ends; `hashchain.compose` needs their operand-pin naming and word decodes (FP4: hash the packed bytes, 4 nibbles per element).
6. **Salted digests for low-entropy rows** (privacy of a row from its digest); a per-row salt absorbed as a 17th element would need one more permutation per row.

## 9. Anything wrong in the spec

* "Expected ~600 quadratic rows per permutation": x^7 as 4 product rows over 213 S-boxes is 852; 3 rows (x^3, x^6, x^7) would give 639.  The spec's "+600-1200 rows/unit on
  3292 = +18-36 %" undercounts: two permutations per unit (x and W) are 1704 rows, plus the operands must become private (they were public pins) — +608-704 rows of bit
  decompositions and decodes the bare relation never needed.  Measured +65-72 % rows, +60-118 % wall: in line with the auth-integration cost model (+70-88 %), not the §1 estimate.
* "FP4 words are 4-bit; hash the packed words" / "positives across all five relations": bf16-ampere and fp4-nvf4 are not in `relations.py`'s registry; composing them is
  a separate piece of work (§8.4).
* "Statement v5 … Merkle paths" as a per-VU path list: a canonical multiproof per tree (the D9 machinery) is what is written — 288-1440 B per sub-batch, not depth x n_vus x 32 B.
* The bench contract's `authentication=included-hash` column is a fingerprint field the coordinator's `tables.py` still has to render as a second column (only the
  constant + test were added here).
* NVRTC: the hashed systems' witness programs (74k affine terms per unit) do not compile as straight-line CUDA in reasonable time; the fused kernel is table-driven and
  chunked for them (`witness_device.py`, TAB_THRESHOLD 8000 terms) — 21-28 s once per pod, cached.  Not in the spec, but a real cost the device lanes will see.
  (With `9cb1c3e` the S-box rows leave the fused program and the dedicated `poseidon2_rows` kernel takes them; the fused kernel is then v1-sized but main's
  register form compiles it in ~84 s cold on the 4090 — see FOR DEVICE LANES.)
* `protocol.py`'s `soundness()` text (`zk_statement`: "operands a, b and words y16 are PUBLIC in this statement, so privacy is vacuous today") is copied into every
  result's fingerprint, including the `included-hash` runs where a, b are private witness wires and only digests / roots are public.  hp2-host's file — I did not
  edit it; the sentence is stale for the committed column and should take the statement's `authentication` into account.

## 10. Timeline

06:10Z brief read; 06:35Z pod; 07:0x first CPU hashed gate; 07:20-07:50Z NVRTC 9-min stall found and fixed (table-driven + chunked kernel); 07:55Z all hashed GPU gates 0
failures; 08:01-08:22Z the 13 measurement runs; 08:22-08:35Z Rust on the dumps (+ the chain-test hot spot); 08:40Z first checkpoint; 08:45-09:20Z merge test
against main 1bb2194 (D13 renumber, boundary-test fix 605c837), merged-tree GPU gates 0 failures; 09:20-09:35Z merged-tree bare vs committed timing (bare
0.403 / committed 0.978 s; main's `--pipeline 3` bare crash on this pod); 09:35-09:50Z hint-block assembly (0.861 s) and the per-term Rust chain test (hashed
Rust CPU 22.7 -> 12.3 s); 10:00Z checkpoint e3762c3 (merged into main by 10:15Z); 10:00-10:20Z the Poseidon2 witness hook (fused+hook W == torch W on
the GPU, gates 0 failures, 0.861 -> 0.764 s), checkpoint 9cb1c3e; pod pytest on the merged tree + hook 199 passed / 1 skipped (`evidence/merged/pytest_hook.txt`).
10:20-10:35Z bf16-hopper / fp8-hopper bare vs committed on the merged tree + hook (§3 table), lane-tree committed run re-published with the two prover
commits (r20260923-102322-b55f, pulled / labelled / pushed, snapshot hash-relation-v2); 10:48Z tile 64x64 on the merged tree + hook (fp8-ada 0.763 s,
bf16-hopper 1.374 s); 10:51Z pod terminated; 10:52Z final checkpoint d7141ec and report.

Evidence dir: `~/.research/notes/lanes/hash-relation/evidence/` — `scripts/{bootstrap,gates,bench_driver}.sh`, `runs.txt`, `rust_batch_pod*.txt`, pod gate logs.
