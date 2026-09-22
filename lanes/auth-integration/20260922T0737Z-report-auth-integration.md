---
id: r20-proof/auth-integration/20260922T0737Z-report-auth-integration
campaign: r20-proof
lane: auth-integration
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/auth_integration.md
---

# Making a numerical proof a complete Verity proof: binding x / w / y to the commitment roots

Lane `auth-integration` (track shared), 2026-09-22. Model: `explore.auth_integration` (+ the `authentication` knob of
`explore.tensor`), JSON `notes-asset:campaigns/r20-proof/assets/auth-integration/reports/auth_integration.json`, tests `tests/explore/test_auth_integration.py`. Reference
implementation of the recommended option: `verity_numerical.reference.leaf_v2` (spec
`note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2`). Every number below is a **cost-model** number (H100-SXM price
list of `note:r20-proof/tensor-cost/20260922T0450Z-report-tensor`, INT8 tensor cores at utilisation 0.172, Blake3 50 GB/s, 2^-128, B = 4096, K = 1536,
BabyBear with degree-6 challenges, t = 191 columns); no GPU code was run. "Overhead" is prover time over native
BF16 peak per VU, the campaign's unit; "ZK" is the malicious-verifier ZK number of `reports/zk_cost.md`.

## 1. Decision table

| design | option | complete overhead | vs ZK | vs non-ZK relation-only | proof bytes / VU | depth | privacy (malicious verifier) | protocol change |
|---|---|---|---|---|---|---|---|---|
| A | (a) in-circuit SHA-256, leaf/v1, all private | 3.85e7 | +260 % | +265 % | +0 | 382 -> 638 | private | no |
| A | (a) in-circuit SHA-256 for x, y; W verifier-side | **1.113e7** | +4.0 % | +5.5 % | +2.8 kB | 638 | private for x, y; **W disclosed** | no |
| A | (b) verifier-side openings, everything | 1.070e7 | +0.01 % | +1.4 % | +2.8 kB | 382 | **NOT private** | no |
| A | (c) leaf/v2-hash (Poseidon2 row leaves), all private | 1.34-1.37e7 | +25-28 % | +27-30 % | +0.5 kB | 508-556 | private (computational) | yes |
| A | (d) **algebraic leaf/v2**, all private | **1.071e7** | **+0.04 %** | **+1.47 %** | +44.6 kB | 382 (+0) | private (statistical, budgeted) | yes |
| B | (a) in-circuit SHA-256, leaf/v1, all private | 6.38e7 | +342 % | +373 % | +0 | 4 | private | no |
| B | (a) in-circuit SHA-256 for x, y; W verifier-side | **1.519e7** | +5.3 % | +12.7 % | +2.8 kB | 4 | private for x, y; W disclosed | no |
| B | (b) verifier-side openings, everything | 1.442e7 | +0.01 % | +7.0 % | +2.8 kB | 4 | NOT private | no |
| B | (c) leaf/v2-hash (Poseidon2 row leaves), all private | 2.45-2.71e7 | +70-88 % | +82-101 % | +0.5 kB | 4 | private (computational) | yes |
| B | (d) **algebraic leaf/v2**, all private | **1.443e7** | **+0.03 %** | **+7.05 %** | +44.6 kB | 4 (+0) | private (statistical, budgeted) | yes |

Baselines: A non-ZK 1.055e7, A ZK 1.070e7; B non-ZK 1.348e7, B ZK 1.442e7. "vs non-ZK" includes the ZK layer
(+1.4 % A, +7.0 % B); the authentication itself is the "vs ZK" column.

**Recommendation.** Option (d) for both designs: it is the only option that is private *and* free (the binding rides
the Ligero opening round the proofs already have: two extra row combinations, no in-circuit hashing, no depth). The
complete Verity number is then the ZK number to three digits: **A 1.07e7, B 1.44e7**, both within 20 % of the
relation-only numbers -> `--breakthrough` (ledger `auth: leaf/v2 algebraic binding (model)`). It is a protocol change
(`leaf/v2`, §4). If the owner does not want a protocol change, the fallback that costs little is (a)+(b) with public
weights: leaf/v1 stays, x and y leaves are re-hashed in circuit (+4-5 %), W rows are opened to the verifier -- but
only under bench-like sharing (§5), and only if disclosing weight rows is acceptable.

## 2. The five options

Sharing at B = 4096 from `fixtures/bench-instances/v1` (§5): 28 activation rows, 3 079 distinct weight rows, 28 output
rows per batch -- a VU pays 1/146 of an x or y leaf and 0.75 of a weight row.

### (a) In-circuit SHA-256 of leaf/v1 leaves + paths (the SP1 way)

leaf/v1 leaves are whole rows of 1 536 words (3 072 B + framing: 50 compressions) plus a node/lift path of ~40
compressions (`explore.authentication.read_openings`). After sharing: 68.4 compressions per VU (w 67.7, x 0.34, y
0.42). Gadgets (cited in `CITATIONS`): the Stwo-style lookup SHA-256 AIR (4 384 trace cells + 1 728 LogUp lookups per
compression, taken as 7 840 cells at L = 2T) and, as the bracket, the R1CS circuit (26 170 nonlinear constraints);
Plonky3's `p3-sha256-air` (7 488 columns, no lookups) sits between them. Priced as checker constraints of A (one
sumcheck element each, lookups as logUp leaves, hints committed) and as committed cells of B (helpers x 6 for the
lookups).

- Prover: **+260 % (A) / +342 % (B)** with private weights -- the weight rows dominate (67.7 compressions). With W
  public (verifier-side, §b) only 1.1 compressions per VU remain: **+4.0 % / +5.3 %**.
- Verifier: nothing new (the digests stay inside the proof); proof bytes +0.
- Depth: A +256 (two hashed chain positions hinted; the rest of the chain is checked, not sequenced); B +0.
- Soundness: constraints only, no new term.
- Privacy: **private** -- no new prover message; the constraints inherit the design's HVZK / step-0 argument.
  Nothing changes in `verity.commitments`; `verity.verification` unchanged (the numerical backend's statement gains
  the leaf digests as public inputs and the roots via the existing `O`).
- Sharing sensitivity: decode_step (one token, 4 096 coordinates of one projection) +340 % private / **+0.16 %** with
  W public; worst case (one coordinate per token per matrix) +930 % / +590 %.

### (b) Verifier-side openings

The prover sends leaf/v1 openings (raw leaf bytes + path) for every touched leaf; the proof pins each word to the
disclosed value by a public linear constraint (A: one more linkage constraint in the geometric batch; B: one linear
constraint). Prover +0.01 %; verifier hashes 4.4 kB and does 7 k field ops per VU; +2.8 kB proof bytes per VU (2.8 MB
per batch of 4 096 VUs: 3 079 weight rows x 3 kB / 4 096 + paths).

**What leaks.** Everything opened, in the clear: the x rows (the token's activation vector at that layer: private
user data, never acceptable), the whole output rows (the next layer's input: same), and the W rows (a weight row per
sampled coordinate; 3 079 rows out of ~1.0 M per batch, so a verifier that samples across many batches reconstructs
the model). Acceptable **only** for tensors public by policy -- open-weights W. Verdict: **NOT private**; usable as the
W-half of a mixed scheme (all "W public" rows of the table use it).

### (c) Commitment-to-commitment linking with `leaf/v2`-hash

The proof commits the leaf words in its own PCS and proves the digest equal to the Verity one. With SHA-256 this is
(a). With the PCS's hash it becomes cheap only if the Verity leaf is *small* and hashed with an arithmetisation-friendly
function: leaf = one row of a tensor, `H_row = Poseidon2(row || salt)`, tensor digest = Poseidon2 Merkle root over row
leaves, and the ids tree above unchanged (SHA-256, folded natively by the verifier from the disclosed tensor digest).
Per VU after sharing: 96 Poseidon2 permutations (rate 8 words: 192 for a row + 11 for the row tree, x 0.75 for W) for
width 16; 54 for width 24. In circuit: 900 (w16) / 1 548 (w24) multiplications + linear wires per permutation
(x^7 S-box = 4 mults, R_F = 8, R_P = 13 / 21).

- Prover: **+25-28 % (A) / +70-88 % (B)** private; +0.5-1.8 % with W public.
- Verifier: folds the SHA-256 ids path natively (1.9 kB/VU); +0.5 kB proof bytes.
- Depth: A +126 / +174 (two permutations in sequence; B +0).
- Privacy: **private under an extra assumption** -- the tensor digest is disclosed, so the row leaves must hide:
  `Poseidon2(row || salt)` with a fresh 8-element salt, i.e. Poseidon2 as a (pseudo)random function beyond CRH.
- Protocol change: yes (`leaf/v2-hash`: new leaf and column hash, salt per row, `dtype`/`shape`/`id` still in the
  digest; sampling protocol unchanged). Verdict: dominated by (d) on every axis except proof bytes.

Blake3 or SHA-256 over field-encoded row leaves would be the same structure with a 5-10x more expensive gadget; not
priced separately (they are bounded by (a)).

### (d) Algebraic binding (`leaf/v2`)

The Verity commitment to a tensor *is* a Ligero commitment over the code the proofs use: rows of l = 3 840 words +
256 randomizers, RS-encoded to n = 16 384 over BabyBear, Merkle over the columns in chunks of R = 64 rows, leaf digest
= H(id, dtype, shape, code, chunk roots) in the unchanged ids tree. The proof commits its witness rows (x row, w row,
y word) in its own tableau; on its opening round the verifier's column set Q is applied to both tableaus and two
tests bind them (spec §5): the IRS proximity test over the claimed tensor rows + witness rows (`v`, degree < k) and the
linear test with one equality constraint per claimed word (`q`, degree < 2k-1, `sum_{subgroup} q = 0`). A whole-row
claim and a single-word claim are the same constraint type; with geometric position coefficients the per-row
interpolants collapse to one shared `G(X)` (PROTOCOL A §12.2's `rho_geo`): one NTT per test.

- Prover: 2 x 3 135 claimed rows x n x 4 x 24 limb MACs + one matrix-DFT = 2.4e6 MACs per VU (**+0.04 % A / +0.03 % B**);
  the 12.6 M equality constraints are public-coefficient terms in the existing linear test (`simt`); nothing hashed;
  no hints; **depth +0** (both tests ride the design's opening round).
- Verifier: folds t = 191 columns of each of 1 379 touched chunks (73 kB hashed per VU) and evaluates the two
  combinations at Q: 1.8 k field ops per VU. Proof bytes **+44.6 kB per VU** (183 MB per batch): 191 columns x
  (84 707 rows in touched chunks x 4 B + 1 379 paths x 14 x 32 B) + k x 4 B. Chunk size sweep (bench sharing):
  R = 1 -> 66 kB, 16 -> 54 kB, **64 -> 44.6 kB**, 256 -> 48 kB, 4 096 -> 64 kB; the weight rows dominate (a chunk of
  64 rows opened for 2.3 sampled rows on average). This is the one axis where (d) is worse than everything else
  (ZK Ligero proofs are already ~MBs; 45 kB/VU is +183 MB on a batch proof). Smaller t is not available (t is the
  soundness parameter); `n = 8192` would halve it.
- Soundness (`security.accounting`, `soundness_with_auth`): the equality constraints join the linear test's
  Schwartz-Zippel term (12 587 008 constraints: 2^-161.9) and the tensor rows join the IRS combination's field term
  (84 707 rows: 2^-169.1); the query terms `(1-e/n)^t`, `((k+l)/n)^t` are the design's own. Total 2^-129.5 before
  and after, for A and B.
- Binding/hiding (spec §6): binding via CRH of H on columns + the IRS test (a non-codeword row is rejected -- the
  reference's `test_negative_non_codeword_tensor_row_is_caught_by_irs`); hiding via Ligero Lemma 4.15 (any
  t <= k - l opened columns of a randomised row are uniform) + the proof's two blinding rows for `v`, `q`. The digest
  is a *commitment*, not a hash of the bytes: two commitments to one tensor differ, and the root alone does not
  certify well-formedness (the test does, at verification time).
- **Randomizer budget** (the real cost of (d)): t = 191 of k - l = 256 randomizers are consumed per opening of a
  chunk, so a commitment supports **one** proof at full privacy. Activations: one proof per decode step is the
  normal case. Weights: either re-randomise per proof (0.6 s per 1.5 B-parameter model on an H100-class GPU: encode
  0.45 s + hash 0.15 s, §3), or size l for the number of proofs (`l = 3328` -> 4 proofs, +15 % rows), or declare W
  public (then W goes through (b): 4 kB/VU proof bytes, +0.02 %).
- Capture-time committer (§3): +60 ms per 256-token decode step on the vLLM side.
- Protocol change: yes (`note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2`); what stays: the tree above the leaf, ids digest, `(id, dtype, shape)` domain
  separation, the sampling protocol's `(tree, rank, word index)` addressing.

### (e) ZK: what the verifier sees per option and why it is simulatable

| option | verifier sees | simulatable because | assumption beyond the design's |
|---|---|---|---|
| (a) | roots (in O), verdict | no new prover message; checker constraints inherit HVZK / HM96 step 0 | none |
| (b) | the opened leaves in the clear | n/a | n/a: not private |
| (c) | tensor digest (Poseidon2 root of salted row leaves), SHA-256 ids path | salted row leaves hide under Poseidon2 as a PRF; the digest is then independent of the rows | hiding of salted Poseidon2; fresh salt per row per commitment |
| (d) | t columns of each touched chunk, `v`, `q`, chunk roots, ids path | columns uniform (Lemma 4.15, t <= k - l) **only with the codeword on a coset `31 H_n` disjoint from the message domain `H_k`** -- the systematic encoding of the first leaf/v2 reference exposed payload word j at column (n/k) j in the clear (red team F4, fixed 2026-09-22, `note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2` §2/§6, pin `test_no_opened_column_is_a_payload_word`); `v`, `q` one-time-padded by the blinding rows; Q and coefficients committed at step 0 (HM96) | the per-commitment randomizer budget (a 2nd session past `k - l` is a payload-equality oracle: re-randomise or accept one private proof per commitment -- protocol owner) |

In (d) the column openings are simulatable even against an adaptive verifier without step 0 (any t columns of a
fresh-randomizer row are uniform); step 0 protects the rest of the proof, as in `note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction`.

## 3. Capture time (what the vLLM-side committer computes under leaf/v2)

Qwen2.5-1.5B shapes (28 layers, hidden 1 536, intermediate 8 960, qkv 2 048), 256-token decode step, all GEMM input
and output rows: 1.03 M words and 392 tableau rows per token; 100 k rows per step.

| | rows | encode (H100 @ 0.172, matrix DFT) | encode (Brakedown expander) | bytes hashed | hash (SHA-256, 446 GB/s, 4090) | leaf/v1 SHA-256 over the same words |
|---|---|---|---|---|---|---|
| activations per decode step | 100 352 | 45 ms | 6 ms | 6.6 GB | 15 ms | 1.7 ms |
| weights per (re)commitment | 1.0 M | 0.45 s | 0.06 s | 66 GB | 0.15 s | 17 ms |

Against a ~10-20 ms decode step at this batch, +60 ms per step is a 3-6x slowdown of capture if done inline on the
same GPU; `n = 8192` (rate 1/2) halves it and a Brakedown encoder brings it to ~20 ms; committing asynchronously on a
second GPU removes it from the critical path. The PRG stream is 0.1 GB per step (randomizers can be derived from a
per-tensor seed as the reference does). This is the operational price of (d); the proving-side price is zero.

## 4. What changes in `verity.commitments` / `verity.verification`

Only (c) and (d) change anything; (a) and (b) are backend-side. For (d), `note:r20-proof/auth-integration/20260922T0737Z-report-leaf-v2` §1, §9 lists it exactly:
nothing above the leaf digest changes (`node/lift/ids/v1`, `levels`, `path_shape`, `fold_path`, `LeafTree`,
`commitments.json`); the leaf digest becomes `H("verity-vllm/leaf/v2", id, dtype, shape, code_text, u32be(chunks),
chunk roots)` with column leaves `H("verity-vllm/col/v2", chunk, column, elements)`; the framing name
`packed/v1:verity-vllm/leaf/v2:u16le:<count>:<index>` selects the checker; `schema.py` admits it, `packed.py` gains
a v2 `PackedLeaf` (row + randomizers + chunk columns + v1 path; the transparent re-encode check of spec §4),
`transparent.py`/`statement.py` compute the v2 digest, `binding.py` is unchanged, SP1 stays on v1. Both framings
coexist; recorded roots and conformance vectors are untouched.

## 5. Sharing structure and how it moves the costs

`vu-k1536.index.json` + `seeds/seeds.json`: 3 456 real VUs = 24 activation rows (one per token per GEMM: 24 seeds
across 18 weight matrices) x 144 weight rows each; 2 598 distinct `(matrix, row)` weight rows; the 640 corners are
synthetic and have no Verity leaves. Scaled to 4 096 real VUs: **28 x rows, 3 079 w rows, 28 y rows** -- x and y are
shared by ~146 VUs, weight rows by 1.33. So under leaf/v1 the weight rows are 99 % of the hashing (67.7 of 68.4
compressions per VU), which is why every "W public" row of the table is cheap and every "all private" hashing option
is not. Brackets (`sharing_sensitivity`): decode_step (one token, all 4 096 coordinates of one projection: x, y shared
by every VU, one weight row per VU) -- in-circuit SHA-256 with W public drops to +0.16 %, (d) stays +0.04 % and its
proof bytes drop to 2 kB/VU (one chunk per 64 VUs); worst (one coordinate per token per matrix: nothing shared) --
in-circuit SHA-256 +930 % private / +590 % W public, (d) +0.08 % but 307 kB/VU proof bytes (every VU opens its own
weight chunk; the bracket counts R rows per chunk). (d)'s prover cost is insensitive to sharing; its proof size is
what sharing buys.

## 6. Red-team checklist for the recommendation (d)

1. **Binding of the digest to the payload.** The root binds columns (CRH); the payload is bound only through the IRS
   test at verification. A committer can put garbage under a root -- the proof then fails, which is the intended
   outcome (an operator cannot claim a computation on a tensor it did not commit well-formedly). Confirm no path in
   `verity.verification` treats a v2 digest as certifying bytes without the test (§4 transparent form re-encodes).
2. **Cross-tensor / cross-chunk / cross-column confusion.** `canonical_id`, `dtype`, `shape_text`, `code_text`,
   `u32be(chunks)` in the leaf digest; `u32be(chunk)`, `u32be(column)` in every column leaf; ids digest and path
   shape from v1. Reference negatives: swapped weight row, claim naming the wrong tensor id, tampered column value,
   flipped word, wrong output word.
3. **Malleability.** Two commitments to the same tensor have different digests (randomizers) -- fine for binding, but
   the verifier can no longer detect "same weights as last time" by digest equality; if that property is wanted, a
   v1 digest of the bytes can be carried alongside (hashed into the v2 leaf as one more part) at native hash cost.
4. **Randomizer budget accounting.** The verifier (or the sampling protocol) must count openings per chunk per
   commitment; exceeding `k - l` leaks payload linear relations. Decide: per-proof re-commitment of W, larger `k - l`,
   or public W.
5. **Coin commitment.** Q must be fixed before the prover's messages under a malicious verifier (HM96 step 0 as in
   `note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction`); with Fiat-Shamir the transcript must include every chunk root and the leaf digests.
6. **Field/encoding injectivity.** Words are 16-bit; elements >= 2^16 in a payload are rejected by the checker's range
   check; `code_text` fixes `w`. A tensor of another dtype width (fp32) needs a `w = 32` two-element encoding: define
   before use, not ad hoc.
7. **Encoder agreement.** Committer and prover must use the identical subgroup generator AND coset shift
   (spec §2-3: Plonky3's `0x1a427a41`, shift 31, `coset=31` in `code_text`; the layout is non-systematic since
   2026-09-22 -- a systematic encoder is a privacy failure, F4); a mismatch is a completeness failure, not a soundness one, but is a
   cross-implementation risk -- ship conformance vectors (the reference produces them).
8. **Proof size.** +183 MB per 4 096-VU batch at R = 64; check the verifier's bandwidth budget; `n = 8192` halves it.

## 7. Open risks

- The baselines are `explore.tensor`'s model prices (A 1.055e7, B 1.348e7 non-ZK). The b-encode lane's measured SIMT
  NTT encoder has since re-priced B to 2.57e6 (4090) / 1.18e6 (H100 scaling): against that smaller base the algebraic
  option's absolute delta (2.4e6 limb MACs + 12.6 M public-coefficient terms per batch) is still < 1 % -- the
  option table should be re-run once `DESIGNS` carries the measured encoder.
- Every prover-side number is a model at the H100 price list; the relative claims (+0.04 %) rest on the algebraic tests
  costing two row combinations, which the tensor model prices the same way as the designs' own combinations.
- The capture-time cost (45 + 15 ms per decode step) is the only new *measured-rate-derived* wall-clock; it competes
  with inference on the same GPU unless committed asynchronously.
- The randomizer budget makes weights the operational question: re-commit per proof (0.6 s), or accept public W.
- Poseidon2 gadget counts for (c) are from Plonky3's round constants and a 4-mult S-box; a lookup-based SHA-256 AIR at
  fewer than 7 840 cells would move (a) but not enough to matter with private W.
- The reference implementation runs at n = 4 096, k = 1 024, l = 768 (pure Python); the full-size code is the same
  arithmetic, not tested here.
