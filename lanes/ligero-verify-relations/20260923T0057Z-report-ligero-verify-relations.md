---
id: r21-ligero-verify/ligero-verify-relations/20260923T0057Z-report-ligero-verify-relations
campaign: r21-ligero-verify
lane: ligero-verify-relations
kind: report
status: closed
repo: verity-main@738e932 (branch lane/ligero-verify-relations, base main aecc298, main 1dcba68 merged)
---

# ligero-verify-relations: the Rust verifier pins every relation by digest and independently verifies the FP8 Ada dumps

Branch `lane/ligero-verify-relations` (worktree `verity-main-wt/ligero-verify-relations`), base `main` aecc298, `main`
1dcba68 (lane b-batch-bound) merged in, head **738e932** (the verifier binary is the c725954 = 857f722 build; 738e932 is a README line), clean tree (`git status --short` empty), no conflict markers.
Independent party w.r.t. lanes ada-fp8-dumps / b-hopper / b-merge-h100 / a100-dumps: every `verified*` label below is by
`ligero-verify-relations`.  Laptop only (Rust build + verification; torch-free system compilation with `torch` stubbed);
no pods, no proving.  Nothing materialised under `~/.research/store/trees/` (dumps were fetched file by file from R2 into
`/tmp/lvr`, sha256-checked against the run-files manifest, deleted after each rep).

## 1. Formats the verifier now reads

| file | formats | notes |
|---|---|---|
| system | `ligero-system/v1` (`LIGSYS01`) | unchanged; `sys_id` = trailing 32 B = Python `protocol.system_id`; table digest = BLAKE3 of the exported tables |
| statement | `ligero-statement/v2` (`LIGSTM02`), `/v3` (`LIGSTM03` = v2 + authentication block), **`/v4` (`LIGSTM04`)** | v4: v2 header through `u32 K` \| `u8 word_bytes` \| `u8 y_bytes` \| `str relation` \| `l x K a` \| `l x K b` \| `l x y` (u8 / u16 / u32 per width) \| `u8 has_auth` \| [v3 block].  Widths 1 / 2 / 4 only, `has_auth` 0 / 1 only, the auth block (u16 leaves) only with 16-bit words, relation name non-empty and <= 64 B, every length statement-bounded. |
| proof | `ligero-proof/v1`, `/v2` | unchanged |

The statement digest absorbs the words exactly as `protocol.statement_digest` under the relation's `RelationHooks`:
`"ligero-b/statement|v2" || rel.tag || params ... || "|sys=" || sys_id || layout || "|a=" || a.astype(word_dtype) ||
"|b=" || b.astype(word_dtype) || "|y16=" || y16.astype(y16_dtype) [|| auth]` -- `<u2`/`<u2` and `tag = b""` for both
BF16 units, `<u1` operands / `<u4` chain-end words and `tag = b"|rel=fp8-ada|v1"` / `b"|rel=fp8-hopper|v1"` for the E4M3
units.  A v2 / v3 file IS the Ampere BF16 unit; a v4 file naming `bf16` / `bf16-ampere` is the same statement (tested:
identical digest and verdict).  v2 / v3 behaviour is unchanged: the 7 `tests/fixture.rs` tests (b1 ZK fixture, byte
flips in every region, flipped word, `--coins`, jobs-independence, corrupted sub-batch, b-batch-bound's union-bound
test) pass as before with the Ampere pins.

## 2. The pinned relations (`backends/ligero-verify/src/relation.rs`)

The statement's relation selects the pinned pair; a system file whose `(sys_id, table_digest)` is not that pair is
refused (`system file is not the pinned <relation> system: sys_id ..., table digest ...; pinned ...`) unless
`--allow-any-system`, in which case every JSON verdict and the batch summary carry `"system_pinned": false` and the
reason ends `[system NOT pinned: --allow-any-system; sys_id ...]`.  `system-digest` prints `pinned_relation` (or null).

| relation | tag / widths / y range / operand | sys_id | table digest | system.bin sha256, rows | provenance |
|---|---|---|---|---|---|
| `bf16-ampere` (`bf16`; v2 / v3 files) | `b""` / u16, u16 / 16 bits / BF16 (`t = 255` off-domain) | `44cb05b9e6988219beba2d66582124e67a1893aac39d0b66126ce0b9d4db89cb` | `c147cc4cece7d61cd3046828410d18f487dcde82f709044f4b4f97e282a73a95` | `bee0ad8c9a17abac...`, 3516 | the values pinned since lane b-verifier; `compile_unit(REAL, chain=True)` recompiled on the laptop from main aecc298 == committed `fixtures/system.bin` == `proofs/system.bin` of every A100 / 4090 dump |
| `fp8-ada` | `b"\|rel=fp8-ada\|v1"` / u8, u32 / 22 bits / E4M3 (`0x7F`, `0xFF` NaN codes rejected; `t = 15` finite) | `6b570eef0c7faa07ccd1dddb2508e2699bd5367b108b15920469d46d16073d37` | `443e4fc74c0ac0cc864e50f7125d9585d71986c0b95ff5336d93a6939f3cb952` | `cba9a09f79baa90f...`, 3769 | `compile_fp8_unit(ADA, chain=True)` on main aecc298; `relations.relation("fp8-ada").compile` on lane b-hopper a39de82 and on lane b-merge-h100 01fc64f -- two runs each, all byte-identical; == `proofs/system.bin` of the pod dumps of attempts r20260922-235542-295b / -235643-98f7 / -235746-0929 (code a4b0ac7) and of the older r20260922-233507-7fb9 / -233617-4316 / -233711-6b9f (manifest `system_file.sha256` cba9a09f..., `sys_id` 6b570eef...) |
| `bf16-hopper` | `b""` / u16, u16 / 16 bits / BF16 | `9dcc7cdc1377a00d877440cc01a0dcdb73b3e989d86df8244eccb35a81be0df4` | `74ce68a2801e14fbeaab2b241886bbe3fa9146234289e52c774fd4160a6c469c` | `5bba40df0bd34eca...`, 3292 | `relations.relation("bf16-hopper").compile(params, True)` from lane b-hopper a39de82 and lane b-merge-h100 01fc64f, two runs each, all four files byte-identical; row count = the b-hopper report's.  **Not yet cross-checked against a pod system.bin** (see 6) |
| `fp8-hopper` | `b"\|rel=fp8-hopper\|v1"` / u8, u32 / 22 bits / E4M3 | `c7cbebe365cb5f773a679bc13b5382fb45714511b1912e4e4ab7fb48accd4bc3` | `d5b77463fee9b3d777174755144edaa84461b3eec6ac6a1750c887dc861d58e7` | `968d99d6d010c3c8...`, 3396 | same as bf16-hopper (a39de82 and 01fc64f, byte-identical); **not yet cross-checked against a pod system.bin** |

Determinism: every relation was compiled at least twice (main aecc298 x 2 for bf16-ampere / fp8-ada; b-hopper a39de82
x 2 and b-merge-h100 01fc64f x 2 for the three registry relations) and every pair of files is byte-identical
(`/tmp/lvr/sys_{main,bhopper,bmh}_{1,2}/report.json`; the compile is `hashlib` + table export once `torch` is stubbed).
The bf16-ampere and bf16-hopper units share tag and widths and are told apart by `sys_id` alone -- exactly as in the
Python digest -- so a v2 / v3 file against the Hopper system is refused by the pin and, unpinned, still by the digest
(the sys_id is in the statement digest).  `fixtures/systems/{bf16,fp8}-hopper.system.bin` are committed so the pins are
testable before any Hopper dump exists.

What the verifier takes from the relation, never from the file: digest tag, word widths (a v4 file whose widths disagree
with its named relation is refused before a word is decoded), the chain-end word range (`y16 < 2^y_bits`), the operand
decode for the public pins, and `K` -- read from the system's pin names (`pin_name`, `system_k`) and checked against the
statement's `K`.  Everything else (rows / kinds / linear / quadratic / pins / chain positions, the wide 26-bit path of
bf16-hopper, the 22-bit public words of the FP8 units) comes from `system.bin`; nothing is guessed from the statement.

## 3. Tests

`cargo test --release` in `backends/ligero-verify`: **30 passed** (17 unit incl. the E4M3 / BF16 decodes against
`public_vectors_fp8` / `unit.public_vectors`; 7 `tests/fixture.rs` unchanged + b-batch-bound's; 6 `tests/relations.rs`):

* `fp8_ada_v4_honest_proof_is_accepted_against_its_pinned_system` -- `fixtures/fp8-ada/` = rep1/sub_00 of run-files
  art:c5dff3c6... (attempt r20260922-235542-295b, interactive non-ZK, 85 VUs x 48 steps, l = 4096, K = 32, t = 198) with
  its coins: accept, `system_pinned = true`, relation `fp8-ada`, format v4, digest 6c9794e9....
* `system_digest_names_every_pinned_relation` -- the four system files name their relation; a sys_id-flipped file is null.
* `a_statement_against_another_relations_system_is_rejected_unless_unpinned` -- fp8-ada statement vs the Ampere / Hopper
  systems and vice versa: refused by the pin; with `--allow-any-system` flagged `system_pinned = false` and still
  rejected (`header M` mismatch / digest mismatch).
* `batch_reports_the_pin_and_reads_the_parent_manifest` -- `batch` on a bench-vu rep dir reads `proofs/manifest.json`
  one level up (`rep1/sub_00.proof`), reports `system_pinned` + `system`, agrees with `python_verdict`; one sub-batch
  of a 49-batch is refused by the batch rule (`batch: n_proofs mismatch (sub_00.proof: n_proofs = 49, 1 sub-batches
  presented)`); the same dir against the Ampere system unpinned exits 3 (disagrees with the manifest).
* `fp8_ada_negatives_are_rejected` -- NaN operand code (`public inputs: E4M3 NaN operand`), a changed finite operand
  (challenge mismatch), a changed public word, a proof byte flip, widths that disagree with the named relation, an
  unknown relation name (`fp8-adb`), `word_bytes = 3`, `has_auth = 2`, an auth block on 8-bit words.
* `v4_named_bf16_statement_is_the_v2_statement_and_the_hopper_name_is_pinned_apart` -- b1 re-encoded as v4 `bf16` =
  same digest and verdict (with and without the auth block); named `bf16-hopper` it is refused by the pin and, unpinned,
  by the digest.

Python (laptop): `uv run pytest tests packages/verity/tests tools/research/tests backends/numerical/tests -q` -- **1214
passed, 15 skipped** on the merged tree.

## 4. Independent verification runs and labels

Verifier: `ligero-verify` built from c725954 (binary sha256 `7273f531877c6cd09094b2627f37c7e119a0795cbc1404104532b9cfa8029dbe`,
identical to the 857f722 build), `batch --target-bits 128 --jobs 3 --threads 2`, pinned (no `--allow-any-system`),
every `<sub>.coins` of the dump used as `--coins` for that proof.  Every `proofs/` file was fetched from R2 by the
run-files manifest and sha256-checked against it before use; `system.bin` sha256 `cba9a09f...` = the laptop compilation.

| bench-result | attempt (stage) | relation | mode / zk | proofs accepted / total | batch bits (min over reps) vs target | wall (3 reps) | pinned | python agrees | verdict artifact | labels (by ligero-verify-relations) |
|---|---|---|---|---|---|---|---|---|---|---|
| art:df1f99631dddee3bc543065bd19f95b012a17ae65c2b7e5469f80034aaef68e5 | r20260922-235542-295b (fp8_nonzk_interactive) | fp8-ada | interactive / no | **147 / 147** (3 x 49) | 2^-128.6156 <= 2^-128 | 1.968 s | yes | 147/147 | art:746c2b0383f57ba0e875043a40c04ac0c778a69bc5ca3ca87c9a32317a36ff2f | `verified=accepted`, `verifier=ligero-verify (... c725954 ... PINNED ...)`, `verifier_seconds=1.9684`, `note=...` |
| art:8d03e01e219071065364e2793dd4682a54cc5debf4ce68d86176f1ed389ca823 | r20260922-235746-0929 (fp8_zk_interactive) | fp8-ada | interactive / **ZK** | **147 / 147** | 2^-128.3957 <= 2^-128 | 2.047 s | yes | 147/147 | art:57a2d452da028004edc58de56cd7f8d93bec49a60dddfc2598e876977706f10c | same four |
| art:f247cd1550880e407f28516c91f67ded99e5f4b9099dc9690d81a87049a7d9ad | r20260922-235643-98f7 (fp8_zk_fiat_shamir) | fp8-ada | Fiat-Shamir / ZK (HVZK) | **147 / 147** | 2^-128.4001 <= 2^-128 | 2.900 s | yes | 147/147 | art:7e92060af9237819d23cf20370e64e54e97603541188a6a795487c07d5e2a38b | same four |

Run-files verified: art:c5dff3c62eba6a1f29ae50a86eb5763300978e1af97af64809fe0632e1ad30ca (169.9 MB), art:4a37603fb930...
(195 MB), art:66c0ac67f572... (277 MB) -- fetched straight to `/tmp` and deleted; no store tree materialised.  The three
`verification-verdict/v1` artifacts (refs `result`, `run_files`; payload `verification.json` + `reps/rep{1,2,3}.json`
batch JSON with per-proof verdicts, timings, soundness terms + the logs) are PRESERVED on the remote.  Verify time per rep
0.65-0.73 s wall (interactive) / 0.95-0.97 s (Fiat-Shamir, t = 302) at 3 x 2 threads; 38-56 ms per proof.

Label spelling: `verified=accepted` (the freeze spec's name, what `tables.VERIFIED_LABELS` reads), `verifier`,
`verifier_seconds` (number), `note`; `independently_verified` was NOT written (the vocabulary marks it deprecated,
"read, not written anew").  `--ref` = the verdict artifact.  Interactive mode caveat, stated in every note: the accept is
against the step-0 coins the dump carries -- the runner's -- so it is the verdict of whoever owned those coins (D7); the
Fiat-Shamir result is the transferable one.  The coordinator labelled art:0b9acdf5 (A100, interactive ZK) the same way
today; lane `verify` labels the same class `not-transferable`.  Both readings are on the record; Table 2's predicate
reads `accepted`.

**Renderer** (`uv run python -m verity_numerical.bench.tables --root ~/.research/store --format md`): the RTX 4090 / E4M3
row's B-Ligero cell is now art:8d03e01e... (**6.1e7x**, t.total 2.34 s, COMPLETE_ZK_BACKEND) with its Table 3 phase row;
art:f247cd15... (HVZK) is the drill-down `6.5e7x`; art:df1f9963... is rejected only for `proof_class
NON_ZK_PROOF_DIAGNOSTIC` (the control row, as intended).  Before the labels all three were "not independently verified".

No proof rejected.  No `verified=rejected` written.

## 5. The old FP8 Ada dumps (r20260922-233507-7fb9, -233617-4316, -233711-6b9f; art:5421786a run-files and siblings)

Confirmed the collision: their statements are the pre-a4b0ac7 relation-named layout under the magic `LIGSTM03` (`v2
header | u8 word_bytes = 1 | u8 y_bytes = 4 | str "fp8-ada" | 8-bit / 32-bit words`; bytes `... 01 04 07 00 00 00 66 70
38 2d 61 64 61 ...` right after `K = 32`), which `ligero-statement/v3` (auth block) also claims; their `proofs/manifest.json`
even says `statement: ligero-statement/v3`.  Read as v3 the file is malformed -- `ligero-verify`: `statement file:
truncated file` (exit 1) -- and per the ground rules no heuristic was added to tell the two layouts apart.  Bench-results
art:53b01a3e..., art:4601022c..., art:5421786a... got a `note` label by this lane saying so and pointing at the v4
re-dumps above; **no `verified` verdict** on them (they are neither rejected proofs nor dump-less).  lane b-merge-h100's
serialize.py docstring records the same ("b-hopper's LIGSTM03 dumps died with their pod, so no file of that layout
exists" -- for the Ada ones, three run-files artifacts of that layout do exist in the store).

## 6. What remains

* **H100 dumps** (`bf16-hopper`, `fp8-hopper`): lane b-merge-h100's `h100-dumps-v1` snapshot had not landed by 00:57Z
  (store snapshots: `h100-self-proved-v1` = b-hopper's self-verified results without surviving dumps; b-merge-h100 at
  01fc64f, not yet merged to main and not yet containing 1dcba68).  The pins are ready: the H100 statements will be
  `ligero-statement/v4` naming `bf16-hopper` / `fp8-hopper` (b-merge-h100's serialize.py), and the systems they will be
  proved against compile byte-identical from the b-merge-h100 tree.  When the snapshot exists: fetch `proofs/system.bin`
  first, `ligero-verify system-digest` must print `pinned_relation` = the relation; then `batch --target-bits 128` per
  rep (75 proofs per rep for bf16 at B = 4096, 39 for fp8 unless b-merge-h100 sub-batches differently), then the four
  labels as above.  If the pod `system.bin` differs from the pin, that is a finding about the compile (not a verifier
  change): report before touching `relation.rs`.
* The `bf16-ampere` / `bf16-hopper` distinction is by `sys_id` only (Python does the same).  A v4 file named
  `bf16-hopper` carrying the Ampere words would be refused by the pin, and unpinned by the digest -- fine -- but a
  reader that trusts the file's name learns nothing more than the digest already says; PROTOCOL.md got a "Relations"
  paragraph (section 8c "What both modes share") saying a file verifier must take tag / widths / range from the named
  relation and pin the system.  DISCREPANCIES.md **D11** (D10 is b-batch-bound's union bound) is the structured entry,
  owner b-merge-h100 for the Hopper cross-check.
* `backends/direct/ligero/verify_result.py` and `bench_result.py` were not re-checked against v4 (out of scope; the
  Python `serialize.read_statement` is the reference and agrees on all 441 files).

## Files (branch lane/ligero-verify-relations, 4 commits: 768c692, merge 857f722, c725954, 738e932)

`backends/ligero-verify/src/relation.rs` (new), `format.rs` (v4), `verify.rs` (relation-aware digest / pins / gate,
`system_pinned`), `main.rs` (JSON fields, parent manifest, `system-digest`), `tests/relations.rs` (new),
`fixtures/fp8-ada/{sub_00.stmt,sub_00.proof,sub_00.coins,system.bin}` (3.8 MB), `fixtures/systems/{bf16,fp8}-hopper.system.bin`,
`README.md`, `DISCREPANCIES.md` (D11), `backends/direct/ligero/PROTOCOL.md` (relations paragraph).  No other `.md`.
Scratch (not in the repo): `/tmp/lvr/{compile_systems.py,fetch_subset.py,verify_dumps.sh,make_verdicts.py,verdicts/}`.
