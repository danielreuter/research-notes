---
lane: verify-rs-3
kind: report
created: 2026-09-23T21:40Z
status: superseded
branch: lane/verify-rs-3 (worktree ~/projects/verity-main-wt/verify-rs-3, from lane/verify-rs-2 @ e38a0c7)
---

CHECKPOINT none (00:03Z) [superseded] by verify-rs-4 (coordinator)
CHECKPOINT 75ec753f (23:14Z) [open] HEAD pushed: coordinator Q answered -- Ligerito verifier binds steps/K/word widths to the relation constants ('statement shape', also under --allow-any-key; test statement_steps_bound_to_the_relation), rows/n_i/n_k/m/virt/constraints via the pinned key digest (sys = ligero-verify pin); only the batch shape l/S/n_vus is the statement's (pow2, n_vus*steps<=l, params l, PCS n, soundness recomputed) -- not the H2 class. relation-2 32e9bd5 gates 6/6 96/96 agree; red-team-3 26 forged fixtures rejected; R3-1 legacy no-soundness, R3-6 zk_mode; cargo 85/85
CHECKPOINT 2dfbb90a (23:04Z) [open] 2dfbb90 (pushed): Rust matches relation-2 32e9bd5 canonical rules (framing bytes exact, pad-unit operand words 0; off-end y from 0db857a); red-team-3's 18 forged fixtures all rejected; 0db857a gates 94/94 agree x2; LGSC0004 (sumcheck-3 ef49a7d, both schedules) + sparse PCS claims in Rust; cargo 84/84. Next: relation-2's 32e9bd5 gates, LGTO+LGSC0004 once relation-2 emits it, FINAL
CHECKPOINT none (22:58Z) [open] 60d9cbd1 canonical y (0db857a) in Rust: 0db857a gates fp8-ada + zk 2/2 accept 92/92 reject 94/94 agree; LGSC0004 (ef49a7d default + zk-small) verified vs Python; sparse PCS claims; LGTO LGSC0004 dispatch provisional; cargo 75+7
CHECKPOINT none (22:42Z) [open] c049225 LGSC0004 verifier (lgsc4.rs) on sumcheck-3's fixture: claims == Python incl. 3 sparse mask claims, 8/8 negatives; cargo 71+7 green; next: sparse claims in the Rust PCS (relation-2 proto supports sparse=)
CHECKPOINT 41570f1 (22:36Z) [open] 41570f1 real size verified: relation-2 4096-VU one-batch dumps (fp8-ada local/live/FS, bf16-hopper, fp8-hopper; l=16384) accepted 0.19-0.25 s each, pinned keys (= l=256 pins), 20/20 tampers rejected; e3ad950 gates 3/3 pass (n_proofs = distinct statements, a8a08eb); cargo 76/76. Next: LGSC0004 (sumcheck-3 f0b9567 fixture)
CHECKPOINT c54db0f (22:31Z) [open] c54db0f fp4-nvf4 added (NVFP4 per-unit decode, FP32 component ends); all six relation-2 32d3d42 gate dumps (fp8-ada, fp8-ada --zk, bf16-hopper, fp8-hopper, bf16-ampere, fp4-nvf4) verify default mode 2/2 acc 90/90 rej 92/92 agree, soundness = python's; cargo 76/76. Next: real-size dump
CHECKPOINT d42489c (22:25Z) [open] d42489c all five ligerito-relation-2 32d3d42 gate dumps (fp8-ada, fp8-ada --zk, bf16-hopper, fp8-hopper, bf16-ampere) verify in Rust default mode: 2/2 accept, 90/90 reject, 92/92 agree w/ python each; all 4 relations pinned; cargo 73/73. Next: fp4-nvf4, real-size dump, LGSC0004 watch
CHECKPOINT d312ec4 (22:22Z) [open] d312ec4 all four ligerito-relation-2 32d3d42 gate dumps (fp8-ada, fp8-ada --zk, bf16-hopper, fp8-hopper) pass batch --dir default mode (keys pinned, V1 required): 2/2 accept, 90/90 reject, 92/92 agree w/ python each; V1 regression fixture + tests; cargo 73/73; bf16-ampere next
CHECKPOINT 1f30710 (22:08Z) [open] LGTO0001 reader + tests + red-team V1 forgery check; cargo 69/69; waiting on relation-2 V1 gate dumps (cf9a63a) for end-to-end V1 + other relations' pins
CHECKPOINT 339d910 (22:02Z) [open] LGTO0001 reader lands: 18:55Z fp8-ada FS fixture (pre-V1, --allow-legacy) 1/1 accept 13 ms + 30/30 neg reject, 31/31 agree with python manifest; default rejects pre-V1 proofs; live fixture 2/2 accept but union 2^-127.02 fails F5 (2 batches, per-proof 2^-128); cargo 61/61. Next: V1 dumps from relation-2
CHECKPOINT e38a0c7 (21:38Z) [open] started: worktree at verify-rs-2 tip, briefs + handoffs read; next: LGTO0001 reader against ligerito-relation-2's current proof.py
# verify-rs-3: LGTO0001 reader + V1 end to end in the Rust Ligerito verifier

## Log

* 21:40Z start. Worktree at e38a0c7. No pod (laptop CPU). Disk 28 GB free. One target dir (`backends/ligerito-verify/target`).
* 21:55Z asks to ligerito-relation-2 (`../ligerito-relation-2/20260923T2155Z-asks-from-verify-rs-3.md`): opening layout, fixtures,
  pins, F11 in the Python non-ZK path. 22:05Z update there: zero blocks = run cover in both modes (relation-2 aligned Python to
  the Rust rule; committed cf9a63a), F5 finding on multi-batch dumps.
* 22:00Z **339d910 LGTO0001 reader** (`src/lgto.rs`, ~1000 lines, no deps): LGTS0001 statement / LGVK0001 key / LGTO0001 proof
  parsers (canonical params JSON: sorted, compact, known keys only; framing; ZK ybar), relation table for fp8-ada / bf16-hopper /
  fp8-hopper / bf16-ampere (operand decoders E4M3 / BF16, steps, widths, `params.RELATIONS` shape terms, system/key PINS),
  `StmtRows` (public rows at `r_c` straight from the statement words: operand rows through a per-operand histogram of
  `eq(r_c, .)` over word values, O(C K)), soundness recomputed (`Prover.soundness`: paper (17) per level with the `t_pad` rate,
  relation terms, beta over J, zero-claim term), LGSC0002 / LGSC0003 by magic, **V1 zero claims** (run cover of the key's
  virtual rows, points `(r_i[:b] || bits(pfx) || r_c)`, value 0) appended to the J claims, J-claim PCS (row-major or
  `zk.permute_point`; ZK: ybar absorbed after root_{i+1} / y, `sum_t eta^{R+t} ybar[t]` subtracted from every row check),
  live-coin exhaustion check. `main.rs`: `verify --proof X.lgto` and `batch --dir` over run.py dumps (`*.lgto` accept,
  `*.lgto.neg` reject, manifest `python_verdict` agreement, coins per the proof's declaration: FS / local(seed) / live(.coins,
  both file forms)), flags `--allow-any-key`, `--allow-legacy` (UNSOUND, pre-V1 proofs), `--no-local`; per-proof target
  2^-(B + log2 N); union over DISTINCT statements (same batch under several coin kinds counts once; local-coin proofs carry
  no soundness figure and are reported as `accepted_local_coins`).
* Results on ligerito-relation's 18:55Z fp8-ada gate dump (3592bd0, pre-V1 so `--allow-legacy`): honest 1/1 accept (13 ms;
  Python 1.05 s), 30/30 negatives reject, 31/31 agree with manifest.json; soundness 2^-128.017. Default mode rejects it
  ("pre-V1 format; unsound"). 20:20Z live dump: 2/2 accept (live replay, 10 ms each) but the batch FAILS F5: union 2^-127.02.
* a0c433e tests: pre-V1 fixture committed (`fixtures/lgto/fp8ada_l256_legacy`, 610 KB): legacy-only accept, 80 proof byte
  flips + truncation/extension, statement byte flips (header, words, y), key tamper (pin and statement digest), zero blocks
  cover exactly the virtual rows, histogram public rows == direct evaluation, E4M3/BF16 decoders; CLI batch over an LGTO dump.
* 1f30710 red-team-2's forged `virtrow_y16_lgsc0003` (y16[47] += 1, w' = w - e_(3581,47)): sumcheck layer accepts (by
  construction), `sumcheck-fixture` now evaluates the zero claims on the recorded delta: `w = 0 on rows [3580, 3584)` is false
  on w' -> the full verifier's PCS cannot open it to 0. cargo 69/69 (63 lib + 6 cli).
* 22:10Z pulled ligerito-relation-2's 32d3d42 gate dumps read-only from its L40S (`research pods ssh ... tar`, ~11 MB each;
  local copy `~/projects/verity-main-wt/verify-rs-3-dumps/gates-32d3d42/`, deleted 23:12Z). Each: 2 honest (FS + local coins), 90 negatives
  (80 byte/semantic tampers + 10 V1 forgeries: 5 per coin kind), manifest with python verdicts.
* **End to end, default mode (key pinned, V1 zero claims required, per-proof 2^-128):**

  | dump (32d3d42, 12 VUs, l = 256) | accept | reject | agree w/ python | zero blocks | Rust / proof | soundness |
  |---|---|---|---|---|---|---|
  | fp8-ada          | 2/2 | 90/90 | 92/92 | 6 | ~13 ms | 2^-128.017 |
  | fp8-ada `--zk`   | 2/2 | 90/90 | 92/92 | 6 | ~14 ms | 2^-128.030 |
  | bf16-hopper      | 2/2 | 90/90 | 92/92 | 4 | ~24 ms | 2^-128.017 |
  | fp8-hopper       | 2/2 | 90/90 | 92/92 | 8 | ~13 ms | 2^-128.017 |
  | bf16-ampere      | 2/2 | 90/90 | 92/92 | 4 | ~20 ms | 2^-128.017 |

  `verify_rust.json` per dump in `evidence/verify_rust_gates-32d3d42_<dump>.json`. The V1 forgeries (commit `w + forge`,
  forge on virtual rows, forged sumcheck value consistent with it) reject at "PCS sumcheck round 1" (the batched claim
  with the zero claims' 0 cannot be met) and the `next:0` edit at "combined final" (the shift); python gives the same reasons.
* Pins (02db242, d42489c): every `sys_id` in the dumps equals ligero-verify's independently checked system pin for the same
  relation (`ligero-verify/src/relation.rs`); key digests from the dumps: fp8-ada `da27387b…` (unchanged since 3592bd0),
  bf16-hopper `1726c3be…`, fp8-hopper `ea793f49…`, bf16-ampere `e0059e70…`. fp4-nvf4 (also gated by relation-2, sys
  `a825ba0b…` = ligero-verify's) is not in the Rust table yet ("relation not one this verifier knows").
* d312ec4 V1 regression fixture `fixtures/lgto/fp8ada_l256_v1/` (honest, `--zk` honest, forgeries 06-10 with their
  statements; same key/statement blobs as the legacy fixture): unit tests default-mode accept with 6 zero claims, each
  forgery rejected at its expected check, honest proof rejected on each forged statement, `zero_blocks` in the params
  pinned to the layout (shifted / swapped / truncated / empty -> "zero_blocks"; dropped -> "pre-V1"), CLI `batch --dir`
  over it + F5 at `--n-proofs 2`. **cargo 73/73 (66 lib + 7 cli).**
* d42489c bf16-ampere pinned (its 32d3d42 gate dump: 2/2, 90/90, 92/92; sys `44cb05b9…` = ligero-verify's, key `e0059e70…`).
* c54db0f **fp4-nvf4** (relation-2 gates it too): `Operand::Nvf4` = the per-unit public decode (`fp4/witness.public_vectors_fp4`,
  ligero-verify `relation::nvf4`: 64 E2M1 numerators per operand, per group `sm` / `X` / `part`, `anc.G`; 141 pins per unit,
  evaluated unit by unit at `r_c` -- a pin reads the whole unit, so no per-word histogram), word domain checked by position in
  the unit (code < 16; scale < 128, != 0x7F), the pad sub-batch's zero units decode to non-zero pins (X = -20, anc.G = -174),
  component end rows `y_end0..2` = FP32 sign 31/1, exponent field 23/8, fraction 0/23 (pinned in the relation table, like
  ligero-verify's `compile_fp4_unit` ends; the key names the rows but not the split), `row_vars` 11 (rows_pad 2048). Pinned sys
  `a825ba0b…` (= ligero-verify's) + key `ac61d99e…`. Its 32d3d42 gate dump: **2/2 accept, 90/90 reject, 92/92 agree**, 9 zero
  blocks, ~13 ms/proof. Fixture `fixtures/lgto/fp4nvf4_l256_v1/` (honest + neg 02 sign-bit-proved / 04 off-domain / 06 V1) +
  tests (decoder on known units, pin names, position checks, pad pins, each y component flip rejected). cargo 76/76.
* Soundness recomputed in Rust == Python's `interactive_union_log2` / `claimed_log2` on every dump (3 decimals): -128.0169
  (l = 256 non-ZK), -128.0298 (ZK), -128.0249 (fp4), FS claims -64.662 / -64.906.
* **Real size** (relation-2 abd8f5e bench, 4090, fp8-ada 4096 VUs one batch, l = 16384, S = 16, 14.5 MB statement, 0.70 MB
  proof; pulled 26 MB tgz in 13 s): local-coins and live-coins (localstream) proofs both **accepted, 0.19 s each** (Python 1.26 s),
  104 MB RSS, soundness -128.001 (Python -128.0008), 6 zero blocks. 20 random byte flips (12 proof, 8 statement) on it: 20/20
  rejected (proof: Merkle root / final vector; statement: combined final -- with local coins the statement is not absorbed, so
  the public rows derived from it are what catch it). Evidence `evidence/verify_rust_bench-abd8f5e_4096_tampers.json`.
* a8a08eb batch `n_proofs` (`--n-proofs` or manifest) = DISTINCT accepted statements, as relation-2's e3ad950 manifests define it
  (gate: one statement, several coin kinds, `n_proofs: 1`); the old count-every-proof rule would have failed every e3ad950 gate.
* Real size, the other relations (relation-2 bench dumps, one batch of 4096 VUs, l = 16384): bf16-hopper local 0.25 s
  (2^-128.035), fp8-hopper local 0.21 s, fp8-ada Fiat-Shamir 0.19 s (union 2^-128.001 as the interactive figure; FS claim
  per F12). Evidence `evidence/verify_rust_4096_*.json`.
* 22:40Z-22:56Z **LGSC0004** (ligerito-sumcheck-3's ZK sumcheck, not yet consumed by relation-2):
  * c049225 `lgsc4.rs`: parse/write/verify of the LGSC0004 wire format (header with schedule, Libra-masked zero-check with the
    `+T` final, combined final with the committed next rows and mask link, row reduction of `V'(rho_c)`), `validate_layout`
    (ZK rows committed, distinct, off the virtual rows; the product constraint exactly `i1 * i2 = i3` at `k_product = K - 1`;
    `6 * coeffs <= g_cells`). Returns the eval claims plus three sparse claims (mask(zc), mask(cmb), mask(rb)).
  * b01afda sparse PCS claims in `lgto::pcs_verify`, following ligerito-proto's `open(..., sparse=)`: `b"sparse"` absorbs
    (cells u32 || weights), `m + K` batching coefficients, the `_Sparse` recursion. Round-trip tested against
    `refprover::prove_commit_first`, a Rust port of proto's `open` / `_Sparse`. Python bytes cross-check pending:
    `tools/pcs_sparse_fixture.py` needs CUDA (asked relation-2 to run it; a CPU pod cannot run `pcs.commit`).
  * e2037b5 sumcheck-3 ef49a7d's coin-lean default (arities 1..6, vf 1..12). `lgsc4::zk_rows_for` derives `lay.zk` like
    `layout_for(zk=True)` (the key does not carry it) and equals both fixtures' `layout.zk`. Both fixtures (default, 15 coins;
    zk-small, 21 coins) verify with the recorded transcript byte-checked, claims == Python's incl. all three sparse claims,
    8/8 negatives each at Python's stage.
  * LGTO dispatch: a key without `next:*` virtual rows is a ZK layout; LGSC0004 by magic there, sparse cells mapped through
    `f_index` (the ZK column permutation), zero blocks over the shorter `virt`. **Provisional**: no LGTO proof on LGSC0004
    exists yet; the convention I assume is in the relation-2 asks note (23:05Z update).
* 60d9cbd **canonical statements, off-end y** (my ask; relation-2 0db857a): a nonzero claimed word off the chain ends
  rejects with Python's wording. relation-2's 0db857a gates fp8-ada and fp8-ada `--zk`: 2/2 accept, 92/92 reject, 94/94
  agree each. The old V1 forgery `v1_08` (n_vus - 1) had left the dropped VU's words behind and now dies at the statement.
* 23:00Z pushed `lane/verify-rs-3` to origin (relation-2's pod had a stale file copy of this crate at `/workspace/vrs3`).
* 2dfbb90 **red-team-3 R3-2 / R3-3** (= relation-2 32e9bd5): the framing JSON must be the writer's exact bytes (it is not
  absorbed; every re-encoding was another valid proof, Fiat-Shamir included), with `t_pad` present iff > 0. That is
  stricter than Python 32e9bd5, which still takes an explicit `"t_pad":0` (reported to relation-2). Operand words in pad
  units must be 0, checked before decoding, as Python does. **cargo 84/84 (77 lib + 7 cli).**
  * red-team-3's forged fixtures (deliverable 3): `framing_malleability_fp8-ada_e3ad950` 4/4 rejected (all accepted before);
    `stmt_tamper_fp8-ada_e3ad950` 7/7 and `stmt_tamper_fp4-nvf4_32d3d42` 7/7 rejected. Evidence
    `evidence/verify_rust_redteam3_*.json`.
  * relation-2's **32e9bd59 gates, all six relations**: each accepted, 2/2 proofs, 94/94 negatives, manifest 96/96 agree,
    0 problems; `neg_*_45` (off-end y) and `neg_*_46` (pad unit) die at the statement. Evidence
    `evidence/verify_rust_gates-32e9bd5_*.json`. The "rust batch exit 1" lines in relation-2's own gate log come from its
    stale pod build accepting neg_45.
* 75ec753 red-team-3 **R3-1**: a pre-V1 proof accepted under `--allow-legacy` claims nothing (claimed null, basis "none:
  pre-V1", soundness null in the batch JSON, out of the union, `accepted_legacy` + a batch problem). **R3-6**: `zk_mode` per
  verdict (none / partial = LGSC0002/3 under the ZK PCS / lgsc0004 / lgsc0004-underblinded when vf > n_c - 4). Sparse
  terms refuse n > 32. red-team-3's `stmt_tamper_fp8-ada_32d3d42` 8/8 rejected (26/26 red-team-3 fixtures in all).
  **cargo 85/85 (78 lib + 7 cli).**
* 889343d **sparse-claim PCS cross-checked against Python on the laptop** (no CUDA needed for verification):
  `pcs_sparse_proto_bytes` (an ignored test) writes a `refprover::prove_commit_first` proof (n = 16, Dims [4,3,3] /
  [24,20,16] / rate 2, three eval points, a 40-cell term inside round-1 column 3 and a 25-cell spread term) as proto
  `Proof.to_bytes`. `tools/pcs_sparse_crosscheck.py` runs relation-2 32e9bd5's `proto.pcs.verify_open` on it (numpy path;
  torch stubbed; `blake3` from an isolated `/tmp` wheel, because without it proto's Merkle silently falls back to SHA-256).
  Result: honest accepted; value+1, weights+1, cells reversed, term dropped, no terms and eval value+1 rejected (sparse
  ones at "sumcheck round 1", as Rust). Rust accepts the same proof. Not covered: sparse terms together with ZK padding
  (t_pad > 0; the ybar path itself is cross-checked through the `--zk` gates). Evidence
  `evidence/pcs_sparse_crosscheck_python_verify_open.json`.
* 732e5d5 `lgto::read_proto_commit_first` (proto's commit-first `Proof.to_bytes`: m claims, `t_pad` ybar) and its writer
  `refprover::proto_commit_first_bytes` (round-trip tested); `verify_sparse_doc` + CLI `pcs-sparse --file X.json` verify
  a sparse-claim document, i.e. the GPU script's output (t_pad 0 / 32 cases, negatives) or the Rust-written one. On the
  Rust-written document: CLI honest accepted, 3/3 negatives rejected; Python `verify_open` honest accepted, 6/6 rejected.
  **cargo 86/86 (79 lib + 7 cli) + 1 ignored (the emitter).**
* **Coordinator's question (22:58Z), does the verifier bind every statement dimension it derives the layout from?** Yes,
  apart from the batch shape. `steps` (K per VU), operands per unit and the word widths must equal the relation's
  constants ("statement shape", also under `--allow-any-key`; test `statement_steps_bound_to_the_relation` patches steps
  to 24/47/49/96). Rows, `n_i`, `n_k`, `m`, the virtual rows, the constraint matrices and the chain rows come from the
  key, whose digest is pinned per relation (sys id = ligero-verify's independently checked pin), and the statement must
  name that key. Only the batch shape (`l`, `S`, `n_vus`) is the statement's own content: l a power of two,
  `n_vus[s]·steps <= l`, S = the next power of two of the real sub-batches, `params.l = l`, PCS `n = n_i + n_c`, and the
  soundness recomputed from it against the target. So red-team-leaf-3's H2 (an unpinned `steps` in ligero-verify) does
  not occur here.
* Laptop: pulled dump copies deleted after verifying (`verify-rs-3-dumps/`, 417 MB; `/tmp` gate pulls). The verdict JSONs in
  `evidence/` are the record; the tests only use `fixtures/`.
