---
id: r20-proof/coordinator/20260923T0929Z-finding-ligero-verify-resolved-discrepancies
campaign: r20-proof
lane: coordinator
kind: finding
status: final
repo: verity
origin: backends/ligero-verify/DISCREPANCIES.md (moved out 20260923T0929Z: the maintained document exceeded its 48 KB cap)
---
# ligero-verify DISCREPANCIES: the RESOLVED entries D3 and D10 (full text)

Moved verbatim from `backends/ligero-verify/DISCREPANCIES.md` by the coordinator when D13 (lane hash-relation) pushed the
document over `tests/test_repository.py::MD_SIZE_CAP`.  The document keeps a one-paragraph stub per entry; nothing else changed.

## D3. HVZK-mode proofs carry coin commitments and openings that nothing binds -- RESOLVED by b-zk-fix

**Post b-zk-fix.**  `_COMMIT_COINS` is gone; the mode is a `Config` field bound into the statement digest, `prove`
refuses coins in Fiat-Shamir mode and `verify` rejects a Fiat-Shamir transcript that carries them ("fiat-shamir
transcript must not carry coins").  The Rust verifier does the same from the statement's mode byte
(`mut_fiat-shamir_*/coins_planted_in_fs_transcript`, `statement_mode_flipped`: both verifiers reject, same reason).
The text below is the pre-fix record.

`_COMMIT_COINS` is a module global (`protocol.py`, "red-team control ONLY").  When it is `False` (the campaign's
HVZK mode, `--no-coin-commitment`) the prover still draws `r_i, s_i`, computes `c_i`, and the transcript still carries
all six 32-byte values; `_coin_prefix` / `_coin_open` return `b""` so **none of them enters any challenge**, and the
Python verifier ignores them.  The document (8c) presents the commitment as the ZK-mode step and says nothing about
the HVZK transcript.  Consequence: 192 bytes of the HVZK proof are free for the prover -- harmless for soundness, but a
verifier that read the header's "coins present" flag as "coins are committed" would be wrong, and a mutation of them is
accepted by both verifiers (`mut_hvzk`: `coin_*` cases, 4 of 35 accepted by both -- the agreement holds, the mutation
is not a forgery).  The Rust verifier takes the *mode* from the verifier's statement (`coin_commitment`), requires the
coins when it is on, and parses-but-ignores them when it is off, exactly like Python; the proof-file header flag is
checked for consistency only.

~~~json
{"id": "BV-D3", "issue": "HVZK proofs contain coin commitments/openings bound to nothing",
 "document": "PROTOCOL.md 8c: commitment is the ZK step; HVZK transcript unspecified",
 "code": "protocol.py _COMMIT_COINS global; prover emits coins in every mode; verifier ignores them when off",
 "verifier": "mode from the statement byte; coins required in interactive mode, refused in fiat-shamir mode", "status": "resolved",
 "owner": "b-zk-fix", "resolution": "Config.mode bound into the digest; the two modes are mutually exclusive in prove/verify (main a52441c)",
 "evidence": ["fixtures/rust_verdicts/mut_fiat-shamir_zk.json (coins_planted_in_fs_transcript, statement_mode_flipped)"]}
~~~


## D10. No verifier enforced the union bound across sub-batches -- RESOLVED by b-batch-bound

Found by lane `b-verify-par` (`ligero-verify batch --jobs`), fixed by lane `b-batch-bound` (`main` 5a89d9d).  A
4096-VU batch is `N_subbatches` = 25 independently committed proofs.  Each proof's soundness is a per-commitment
number (`soundness()`'s `per_proof_total_log2`, 2^-132.9 at `t = 196`); the claim "the batch is sound to 2^-128"
rests on the union bound `sum_i 2^-b_i` over the 25, which `config_for(..., n_proofs = 25)` sizes `t` for and
`bench-vu` *reports* (`security.achieved_log2` = `union_over_proofs`, 2^-128.26 -- a report, not a check).  Neither
verifier checked it.  `ligero-verify batch` accepted iff every sub-batch accepted, each gated on ITS OWN
`union_log2 = per_proof_log2 + log2(n_proofs)` -- with `n_proofs` read from the proof's statement header, a
prover-supplied field that is not in the statement digest (only `l, n, D, t, target, zk, k, mode` and the words are).
The Python paths (`bench-vu`, `serialize verify`) had no batch-level check at all.  Consequences: 25 proofs each
claiming `n_proofs = 1` at 2^-132.9 passed while the batch was only 2^-128.26 (the number that saved it is a
coincidence of the same `t`); 25 proofs sized for a 25-batch presented as a 26-batch would have passed at 2^-128.2
claimed as 2^-128; and the `l = 256` fixture (`t = 189`, 2^-128.16, sized for one proof) copied six times was the
"honest batch" of the b-verify-par determinism tests, a batch that is 2^-125.57.

**Fix (PROTOCOL.md 8c, "Batch verification").**  A batch verifier with target `t` bits accepts iff (1) every sub-batch
proof verifies against its own statement with the shared system, (2) `sum_i 2^-b_i <= 2^-t` with `b_i` the
verifier's own recomputation of proof `i`'s bound from that proof's `(n, k, l, t, D, mode, zk)`, (3) every proof's
`n_proofs` equals the number `N` presented.  Implemented as `protocol.batch_bound` (Python; `ChainRunner.batch_bound`
/ `verify_batch` in `bench-vu`, `serialize verify-batch --dir DIR --target-bits T` on files) and
`verify::batch_bound` (Rust; `ligero-verify batch --target-bits T`, default 128, `--soundness-bits` its alias; the
per-proof gate of `verify` is off in batch mode because the batch gate is the right one).  Same reason strings, same
precedence (unreadable input, a rejected sub-batch, `batch: n_proofs mismatch (<name>: n_proofs = k, N sub-batches
presented)`, `batch: union bound 2^-x over N sub-batches exceeds the target 2^-t`); the accept reason and the JSON
carry the batch bits (`batch_bits = -log2 sum`; `per_proof_bits[]`, `n_proofs_claimed[]`).  `bench-vu`'s
`security.achieved_log2` is now the verifier's `batch_log2` (asserted equal to `soundness()`'s union to 1e-6), with
`achieved_bits` and `verifier_target_bits` beside it; `N_subbatches` and `B_proof` were already in the fingerprint.
Rule (2) needs nothing prover-supplied: `b_i` is a function of digest-bound parameters, so relabelling `n_proofs`
cannot move the bound -- it can only fail rule (3).  The check is arithmetic on `N` numbers inside the batch wall
(re-timed at `--jobs 25` on the B = 4096 batch before/after: lane note `b-batch-bound`).  Both verifiers agree on the
batch bits to 1e-6 and on every verdict and reason of the test matrix (honest 4-batch accepted at 128; the same
proofs rejected at a target above the achieved bound; four `n_proofs = 1` proofs presented together rejected with
the mismatch string in both).  D1 is unchanged: a single `protocol.verify` still checks the transcript only.

~~~json
{"id": "BV-D10", "issue": "the batch verdict was 'every sub-batch accepts'; the union bound over the sub-batches presented and n_proofs = N were never checked by any verifier (n_proofs is a prover-supplied header field outside the statement digest)",
 "document": "PROTOCOL.md 8c (before b-batch-bound): the union bound stated for the prover's sizing, no batch verification rule",
 "code": "vu.py bench_vu asserted each sub-batch and REPORTED the union; serialize.py had per-file verify only",
 "verifier": "main.rs batch: accept iff every sub-batch accepts, each gated on its own n_proofs",
 "status": "resolved", "owner": "b-batch-bound",
 "resolution": "PROTOCOL.md 8c 'Batch verification'; protocol.batch_bound / verify::batch_bound, --target-bits (default 128), same reason strings; tests/fixture.rs the_batch_union_bound_and_n_proofs_are_enforced, tests/test_ligero_batch_bound.py",
 "evidence": ["b-verify-par verifier results labelled finding=batch-union-bound-unenforced-before-<commit>", "lane note b-batch-bound (test matrix, batch bits, timing before/after)"]}
~~~



# Appendix (moved 09:35Z): D12, the v2 public-selection relations (lane relmin-lookup), full text

Moved out for the same size cap; D12 stays open (status: finding, not a Table 2 headline -- the verifier computes the public
half of the step, unusable with private operands).

## D12. The v2 public-selection relations (lane `relmin-lookup`): the verifier computes part of the step, and the pins are no longer the operand words

`bf16-hopper-v2`, `bf16-ampere-v2`, `fp8-hopper-v2`, `fp8-ada-v2` (`backends/direct/ligero/pubsel/relation.py`,
registered in `relations.py` beside the v1 names, v1 untouched) claim exactly what their v1 counterparts claim -- the
same pinned instruction semantics (`verity.ml.tc.models`), the same statement widths, the same chain-end word
(`y16`, one public word per VU; `ligero-system/v1` files) -- with a different compiled unit: 292 / 469 / 195 / 357 rows
against 3292 / 3516 / 3396 / 3769.  What changes for a verifier:

* **The pins are derived values, not word components.**  A v1 system pins `a[i].s|m|e` / `b[i].s|m|e` and the
  witness re-does the whole step; a v2 system pins, per product group `g` of the step, the group maximum `g{g}.G` of
  the products' exponents (a zero product counts as `Params.floor`; `G >= floor`) and, for every extra alignment
  shift `j in [0, prod_bits)`, the signed sum `g{g}.Q[j]` of the products each aligned to `G + j` -- `AlignProduct`'s
  truncation term by term, then summed (`public_pins_int`; `PubSel::unit_pins`).  The BF16 Hopper sum exceeds p and
  is pinned as two limbs `g0.Q[j].lo` (the low 16 bits) and `g0.Q[j].hi` (the arithmetic shift; negative for a
  negative sum), reduced mod p like every pin.  The verifier therefore performs the public half of the tensor-core
  step itself (products, alignment, group maximum) -- O(K prod_bits) integer operations per unit -- and the prover's
  witness selects `Q[E - G]` with a lookup one-hot.  A wrong pin value anywhere fails the linear test with
  overwhelming probability, as before; a wrong *rule* in the verifier's public computation is a soundness bug of the
  verifier, not of the proof -- the Rust decode is pinned against `public_pins_int` by hand-computed vectors
  (`pubsel_unit_pins_match_public_pins_int`) and, on the Python side, by the v1-v2 differential
  (`pubsel/relation_test.py`: both units accept exactly the model's word on random units and reject every negative
  family).
* **K comes from the relation, not from the pins.**  There are no `a[i]` pins to read `K` off; `K` is the sum of
  `Params.groups` (16 / 8+8 / 32 / 16+16), fixed per relation in `relation.rs` (`PubSel::k`), and a statement whose
  `K` differs is refused ("statement has K = 32 operands per unit, the relation's step takes 16").  Every word of every
  column is decoded, pad columns included (all-zero operands are on the domain), so an off-domain word anywhere is
  refused with the decode's reason (Python: `public inputs rejected: ...`; Rust: `public inputs: ... (unit j)`).
* **Tags and pins.**  `bf16-hopper-v2` and `bf16-ampere-v2` absorb the empty tag like the other BF16 relations (the
  statement's name and the `sys_id` in the digest distinguish them, D11); the FP8 pair absorb `|rel=fp8-hopper-v2|v1`
  / `|rel=fp8-ada-v2|v1`.  Pinned digests (`sys_id` / table digest): `066c6696... / e9b1b7b4...`,
  `2a5f4378... / 2ce5db09...`, `2cb40f21... / c214a87c...`, `11a7194b... / 215e1beb...` -- laptop compilations
  from the lane tree, torch-free, twice each, byte-identical, the `sys_id`s equal to `protocol.system_id` under
  torch; fixtures under `fixtures/systems/`.  The units select the pinned sum, the accumulator's aligned term and the
  normalised significand without product rows (a hint row and one row-free quadratic `sel_i (X - value_i) = 0` per
  candidate), and the two shift hints are ranged by their lookups' one-hots alone (`LigeroCtx.lookup(range_key=False)`).
  The last group of a unit commits no fraction bits: its normalised significand, hidden bit and the BF16 epilogue's
  fields are picked from the sum's bit rows by the normalisation one-hot, with the bits above the window forced to zero.
  A zero sum (the terms cancel, or every term is zero: `z = 1`) is the zero word whatever normalisation shift the one-hot
  picked, so the subnormal-clamp and overflow proofs read the exponent masked by `z` (`e1m = acc_e_min` when `z = 1`) --
  the first cut of the unit demanded `t = tc(E)` for `z = 1` too and had no witness for a cancelling sum whose `E` put
  `tc(E)` outside the shift range (found by the 1e5 differential on fp8-ada-v2; `test_zero_sums_accepted_in_unit_and_chain_mode`).
* **`bf16-ampere-v2` is a new claim on the generic runner**, not a re-encoding of `vu.py`'s `--relation bf16` run:
  it proves the Ampere BF16 step over synthetic instances drawn like the Hopper BF16 set (`instances_dataset`
  `bench-instances-bf16-ampere/v1`), where `bf16-ampere` proves the frozen `bench-instances/v1` set through `vu.py`.
  The unit compiled is `compile_unit(Params.from_model(AMPERE_BF16_M16N8K16))`'s claim; the statement digest and
  the auth block differ from `vu.py`'s files.

~~~json
{"id": "BV-D12", "issue": "the v2 relations pin values the verifier computes from the operand words (group maximum, truncated product sums per shift); K is fixed by the relation; the verifier's public computation is part of the soundness surface",
 "document": "PROTOCOL.md describes the BF16 unit only; pubsel/relation.py's module comment is the reference",
 "code": "backends/direct/ligero/pubsel/relation.py (compile_v2_unit, public_pins_int, public_vectors_v2), relations.py (the four names)",
 "verifier": "src/relation.rs pubsel::PubSel (unit_pins, pin_index, the four parameter sets), Decode::PubSel; verify.rs public_pins_pubsel",
 "status": "open", "owner": "relmin-lookup (pin the digests against a pod system.bin when the fp8-ada-v2 dumps land; PROTOCOL.md section for the public-selection unit)",
 "evidence": ["src/relation.rs tests", "tests/relations.rs system_digest_names_every_pinned_relation", "backends/direct/ligero/pubsel/relation_test.py", "lane note relmin-lookup"]}



# Appendix 2 (moved 09:40Z): D6 (resolved by b-verifier), full text

## D6. A transcript mutation never reaches the tests

Every mutation of a *message* (`w`, `h`, `q`, `v`), the root, the statement, or the column set is rejected at
"column challenge mismatch" -- the Fiat-Shamir binding catches it before the proximity / linear / quadratic / chain
tests run; the opened values fail at the Merkle path.  That is the correct behaviour, but it means a mutation battery
alone exercises the tests only through the honest proofs' acceptance and the 52 negatives' `chain constraints failed
(sum over H)`.  This lane therefore added `serialize.py gen-witness-mutations` (the prover's `mutate=` hook, before
commitment: one row per row class, a broken chain link, a nonzero `c_0`, a flipped bit column) so that both verifiers
are seen rejecting *inside* the tests: 8/8 `linear constraints failed` / `quadratic constraints failed` in both
modes, same reason in both verifiers (`fixtures/rust_verdicts/wmut_*.json`).  Not a discrepancy; recorded so the
next reader does not mistake the mutation table for test coverage.

**Post b-zk-fix.**  Still true in both modes, with a twist in interactive mode: `root` no longer enters any
challenge, so `root_flipped` now reaches the Merkle check ("merkle path 0 invalid") instead of "column challenge
mismatch", and a mutated message (`w`, `h`, `q`, `v`) reaches ITS test (`proximity test failed`, `quadratic
constraints failed`, `chain constraints failed`, `linear constraints failed`) -- the interactive transcript is not
hash-bound, only coin-bound (D7).  A consistent re-opening of one coin slot (`challenge{1,2}_coin_reopened_consistently`:
fresh `r_i, s_i`, `c_i := H(r_i || s_i)`) changes `c1 c2`, which sits in BOTH seeds, so it is caught at the column
challenge in every case; no mutation can change challenge 1 alone.  The mask rows are covered by
`opened_mask_row_{prox,chain_a,chain_b}_plus1` (Merkle) and by the witness mutations (tests).

~~~json
{"id": "BV-D6", "issue": "transcript mutations are caught by the FS binding, not the tests; test coverage needs witness mutations",
 "document": "n/a", "code": "n/a", "verifier": "gen-witness-mutations added; 16/16 rejected inside the tests by both",
 "status": "resolved", "owner": "b-verifier", "resolution": "witness-mutation set is part of the gate", "evidence": ["fixtures/rust_verdicts/wmut_zk.json", "fixtures/rust_verdicts/wmut_plain.json", "run r20260922-101053-0dc9"]}
~~~

## Not findings (checked and consistent)

* `note:r20-proof/red-team-3/20260922T0921Z-report-redteam-3` O1 (`gpu/ligero.py::row_coeffs` geometric powers): the transcript path this lane verifies
  (`protocol.py`, torch prover) draws every combination coefficient independently from SHAKE, as section 4 says
  ("`D` *independent* BabyBear combinations"); the Rust verifier would reject a prover that used geometric powers
  (the coefficient rows it recomputes would differ).  If the GPU kernel path ever produces transcripts, this verifier
  is the check.
* `note:r20-proof/red-team-vu/20260922T1042Z-report-redteam-vu` F1-F3: every size (`M, l, n, t, D, k, depth, n_vus, steps`) comes from the verifier's statement;
  the proof header's copies are compared and a disagreement is a named rejection; the statement digest covers
  `a, b, y16`, the configuration and the `system_id` -- confirmed by the statement mutations (`statement_*`: 7/7
  rejected in every mode).
* `note:r20-proof/red-team-3/20260922T0921Z-report-redteam-3` O5 (`N_subbatches` not in the ledger schema): the statement file carries `n_proofs` and the
  verifier's bound is the union over it; the ledger rows below spell out `25 sub-batches` in `note`.



# Appendix 3 (10:20Z): D12 as refreshed by relmin-lookup 2ef2409 (supersedes the appendix-1 text where they differ)

`bf16-hopper-v2`, `bf16-ampere-v2`, `fp8-hopper-v2`, `fp8-ada-v2` (`backends/direct/ligero/pubsel/relation.py`,
registered in `relations.py` beside the v1 names, v1 untouched) claim exactly what their v1 counterparts claim -- the
same pinned instruction semantics (`verity.ml.tc.models`), the same statement widths, the same chain-end word
(`y16`, one public word per VU; `ligero-system/v1` files) -- with a different compiled unit: 282 / 449 / 185 / 337 rows
against 3292 / 3516 / 3396 / 3769.  What changes for a verifier:

* **The pins are derived values, not word components.**  A v1 system pins `a[i].s|m|e` / `b[i].s|m|e` and the
  witness re-does the whole step; a v2 system pins, per product group `g` of the step, the group maximum `g{g}.G` of
  the products' exponents (a zero product counts as `Params.floor`; `G >= floor`) and, for every extra alignment
  shift `j in [0, prod_bits)`, the signed sum `g{g}.Q[j]` of the products each aligned to `G + j` -- `AlignProduct`'s
  truncation term by term, then summed (`public_pins_int`; `PubSel::unit_pins`).  The BF16 Hopper sum exceeds p and
  is pinned as two limbs `g0.Q[j].lo` (the low 16 bits) and `g0.Q[j].hi` (the arithmetic shift; negative for a
  negative sum), reduced mod p like every pin.  The verifier therefore performs the public half of the tensor-core
  step itself (products, alignment, group maximum) -- O(K prod_bits) integer operations per unit -- and the prover's
  witness selects `Q[E - G]` with a lookup one-hot.  A wrong pin value anywhere fails the linear test with
  overwhelming probability, as before; a wrong *rule* in the verifier's public computation is a soundness bug of the
  verifier, not of the proof -- the Rust decode is pinned against `public_pins_int` by hand-computed vectors
  (`pubsel_unit_pins_match_public_pins_int`) and, on the Python side, by the v1-v2 differential
  (`pubsel/relation_test.py`: both units accept exactly the model's word on random units and reject every negative
  family).
* **K comes from the relation, not from the pins.**  There are no `a[i]` pins to read `K` off; `K` is the sum of
  `Params.groups` (16 / 8+8 / 32 / 16+16), fixed per relation in `relation.rs` (`PubSel::k`), and a statement whose
  `K` differs is refused ("statement has K = 32 operands per unit, the relation's step takes 16").  Every word of every
  column is decoded, pad columns included (all-zero operands are on the domain), so an off-domain word anywhere is
  refused with the decode's reason (Python: `public inputs rejected: ...`; Rust: `public inputs: ... (unit j)`).
* **Tags and pins.**  `bf16-hopper-v2` and `bf16-ampere-v2` absorb the empty tag like the other BF16 relations (the
  statement's name and the `sys_id` in the digest distinguish them, D11); the FP8 pair absorb `|rel=fp8-hopper-v2|v1`
  / `|rel=fp8-ada-v2|v1`.  Pinned digests (`sys_id` / table digest): `cf99d1ce... / bc4b95ec...`,
  `15d793e7... / e70b77d5...`, `e2a1573b... / a473c735...`, `f23461f8... / 82b3041e...` -- laptop compilations
  from the lane tree, torch-free, twice each, byte-identical, the `sys_id`s equal to `protocol.system_id` under
  torch; fixtures under `fixtures/systems/`.  The units select the pinned sum, the accumulator's aligned term and the
  normalised significand without product rows (a hint row and one row-free quadratic `sel_i (X - value_i) = 0` per
  candidate); the group maximum and both alignment shifts come from one one-hot over `clamp(e_acc - G, -W, PB)` (the key
  is an affine expression of the state and the pin, so there are no shift hints; the end selectors mean `>= PB` /
  `<= -W` through a signed key-difference range check).
  The last group of a unit commits no fraction bits: its normalised significand, hidden bit and the BF16 epilogue's
  fields are picked from the sum's bit rows by the normalisation one-hot, with the bits above the window forced to zero.
  A zero sum (the terms cancel, or every term is zero: `z = 1`) is the zero word whatever normalisation shift the one-hot
  picked, so the subnormal-clamp and overflow proofs read the exponent masked by `z` (`e1m = acc_e_min` when `z = 1`) --
  the first cut of the unit demanded `t = tc(E)` for `z = 1` too and had no witness for a cancelling sum whose `E` put
  `tc(E)` outside the shift range (found by the 1e5 differential on fp8-ada-v2; `test_zero_sums_accepted_in_unit_and_chain_mode`).
* **`bf16-ampere-v2` is a new claim on the generic runner**, not a re-encoding of `vu.py`'s `--relation bf16` run:
  it proves the Ampere BF16 step over synthetic instances drawn like the Hopper BF16 set (`instances_dataset`
  `bench-instances-bf16-ampere/v1`), where `bf16-ampere` proves the frozen `bench-instances/v1` set through `vu.py`.
  The unit compiled is `compile_unit(Params.from_model(AMPERE_BF16_M16N8K16))`'s claim; the statement digest and
  the auth block differ from `vu.py`'s files.
