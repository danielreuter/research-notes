---
id: r21-auth-included/auth-included/20260922T2330Z-report-auth-included
campaign: r21-auth-included
lane: auth-included
kind: report
status: closed
repo: verity-main@f28c13d
branch: lane/auth-included (off main 4987a47; commits 0ddc2c9, 53cdb40, 3e04dc3, 2de2fb5, f28c13d; not pushed, not merged)
machine: vy-auth (RunPod rlh72c95tsvvz4, A100-SXM4-80GB SECURE, EPYC 7742 128 threads, driver 580.126.16 / CUDA 13.0; created 22:06:44Z, terminated 23:20:47Z)
snapshot: auth-included-a100-v1 = art:91531595abcf1d9c041dac9fc8f105690faf7e5a45b84210455031d7a05513dd (PRESERVED on s3://verity-dev 23:28Z)
---

# auth-included: the first `authentication = included` full-contract B-Ligero result (A100, self-proved)

## 1. Answer

On one A100 SXM4 80GB, frozen `bench-instances/v1` `vu-k1536` VUs [0, 4096), K = 1536, B = 4096, target 2^-128, median of 3
recorded reps after a warm-up, every proof of every rep checked by the independent Rust verifier on the same pod, the
boundary words of every VU (its 1536 activation words, 1536 weight words and its 16-bit output word) are now bound to
three committed Merkle roots, and the cost of that binding is:

| | auth | t.total s (median/3) | Python verifier s | Rust verifier s (auth part) | transcript bytes (auth part) | R_proved FLOP/s | overhead vs 312e12 | soundness | class |
|---|---|---|---|---|---|---|---|---|---|
| a | excluded | 1.673 | 1.133 | 3.311 | 110,768,000 | 7.521e6 | 4.149e7 | 2^-128.25 | NON_ZK_PROOF_DIAGNOSTIC (interactive) |
| b | excluded | 1.926 | 1.257 | 4.427 | 165,321,000 | 6.534e6 | 4.775e7 | 2^-128.04 | COMPLETE_HVZK_BACKEND (Fiat-Shamir) |
| a' | **included** | **1.723** (+3.0 %) | 42.313 (40.316) | **7.154** (3.834) | 110,788,800 (+20,800 = +0.019 %) | 7.302e6 | 4.273e7 | 2^-128.25 | NON_ZK_PROOF_DIAGNOSTIC (interactive) |
| b' | **included** | **2.000** (+3.8 %) | 41.524 (40.214) | **8.031** (3.588) | 165,341,800 (+20,800) | 6.291e6 | 4.960e7 | 2^-128.04 | COMPLETE_HVZK_BACKEND (Fiat-Shamir) |
| c' | **included** | **1.868** | 41.705 (40.550) | **7.288** (3.895) | 122,460,900 (+20,800) | 6.736e6 | 4.632e7 | 2^-128.05 | COMPLETE_ZK_BACKEND (interactive) |

Reps (prover, s): a 2.467 / 1.673 / 1.665; b 2.962 / 1.928 / 1.872; a' 2.406 / 1.727 / 1.716; b' 2.953 / 2.010 / 1.929;
c' 2.767 / 1.842 / 1.877 (rep 1 is systematically slow in every row under the new harness order, §5; the median is
unaffected). `R_proved = 4096 x 2 x 1536 FLOP / t.total` (`contract.rate_measurements`); overhead = 312e12 / R_proved.

**The prover pays ~3-4 % for authentication, all of it host-side (`t.serialization`: 0.174 -> 0.217 s non-ZK, 0.249 ->
0.292 s FS-ZK; `auth.openings_seconds` 0.039 s per 25 proofs), the transcript pays 832 bytes per sub-batch proof
(20.8 kB per 4096 VUs, 0.02 %), and the verifier pays the real bill: the Rust verifier +3.6-3.9 s per 4096 VUs
(1.05-1.16x its Ligero time) to recompute 12,587,008 SHA-256 leaves and fold them to the roots, the Python verifier
+40 s because `verity.commitments.verify_multiproof` folds node by node in Python.** The prover SKU is the target
anchor (A100 SXM4), so every row is self-proved for the Ampere BF16 row of Table 2.

Committing the object (the three trees over 12.6 M words) took **29.40 s once** on 64 processes (run r20260922-223110-6642,
the first included run; the three canonical included runs loaded the trees from the on-pod cache in 0.02-0.03 s and say
so in `preprocessing`).

## 2. The binding, in five lines

1. The instance set's words are committed as three indexed Merkle trees of `verity.commitments` (`merkle.py`): tree `a`
   (activations, owner -1, leaf rank `vu*K + k`, 6,291,456 leaves, depth 23), tree `b` (weights, owner -2, same ranks),
   tree `y` (the 16-bit public output word, owner -1, leaf rank `vu`, 4096 leaves, depth 12); one `u16` word per leaf
   (`leaf = H('leaf' | domain_id | uint(rank) | uint(position) | 'u16' | word_be2)`), SHA-256 with the
   `veritor/protocol/merkle/frame/v3` framing, binary, padded with domain-bound pad leaves. Each tree's
   `CommitmentDomain(binding, owner, RangeIndexedDomain(0, count))` has `binding = identity_digest('verity/ligero-b/auth-binding/v1',
   {dataset, tier, manifest_sha256, vu_lo, vu_hi, K, tree, schema})`: the same words under another manifest are another object.
2. The public statement gains an `AuthStatement`: the three `(name, binding, owner, count, root)` references and the
   claimed `vu_index` list (one VU per chain, strictly increasing). Its canonical `digest_bytes` (version, schema, n_vus,
   the indices, the three references) is absorbed into `statement_digest`, so every challenge of the proof is bound to
   "the words at these leaf ranks under these roots"; flipping any root / binding / count / owner / index changes the
   digest and the Rust verifier rejects with `column challenge mismatch` (7 of the 20 negatives).
3. The prover ships one canonical multiproof per tree (`verity.commitments.multiproof` order: per level, ascending,
   the sibling of every known node whose sibling is not known) inside the proof: 9 + 9 + 8 siblings = 832 B per
   sub-batch of 170 contiguous VUs. Formats: `ligero-statement/v3` (v2 + the auth block) and `ligero-proof/v2` (v1 +
   the multiproofs); a v3 statement never pairs with a v1 proof and vice versa (2 negatives).
4. Both verifiers (Python `auth.verify_auth` -> `verity.commitments.verify_multiproof`; Rust `auth::check`, a scratch
   SHA-256 + the frame + the fold, no dependencies) recompute every leaf digest from the *published* words, fold with
   the shipped siblings and compare with the statement's roots, after the Ligero checks pass; limits from `limits.py`
   (`max_positions`, `max_openings`, `max_proof_bytes`) are enforced before hashing.
5. This is the verifier-side-openings option, (b) of the `auth-integration` report: Ligero proof unchanged, prover cost
   in `t.serialization` (`auth.openings_seconds`), authentication cost in `verifier.seconds` and `transcript.bytes`.
   It is *not* private (the words were already public in this statement: the B-Ligero chain statement publishes `a`,
   `b`, `y16`; the ZK rows' privacy claim is about the witness, unchanged), and it follows what `auth-integration`
   settled: x, W and y are all bound (three trees), option (d) (algebraic leaf/v2) was a protocol change that was not
   built, so (b) is what this lane could do soundly. `auth-integration` priced (b) with leaf/v1 *row* leaves
   (1536 words per leaf, 2.8 kB per VU of openings, 68 compressions per VU shared); this lane commits *words* (the
   commitment layer's indexed `u16` leaves), which is what makes "each VU's leaf indices" literal, at the price of
   ~2 SHA-256 compressions per word for the verifier (~6,100 per VU) instead of ~68 -- see §6.

## 3. Negative tests (20 per included run, every one rejected by both verifiers; 21 files incl. the honest one)

Prover-side (a valid Ligero proof over words that the authentication block does not cover):
`auth_word_not_under_root` (one activation word swapped, proof and statement re-made over the new words, auth block
unchanged) -> `auth: a: multiproof rejected (root mismatch)`; `auth_weight_not_under_root` (same for a weight word) ->
`auth: b: ...`; `auth_wrong_index` (honest words claimed at another VU's indices) -> `auth: a: ...`; `auth_vus_swapped`
(two honest VUs' indices exchanged) -> `auth: a: ...`; `auth_different_root` (honest words and indices, root of tree `a`
replaced; the prover opens against the real tree) -> `auth: a: ...`; `auth_root_of_other_tree` (root of `y` replaced by
`a`'s) -> `auth: y: ...`.
File-level: `mut_auth_multiproof_a_truncated` (`multiproof too short`), `mut_auth_multiproof_b_extended` (`too long`),
`mut_auth_multiproof_{y,a}_sibling_flipped`, `mut_auth_multiproofs_swapped_a_b` (root mismatch),
`mut_auth_multiproofs_stripped` / `mut_statement_auth_stripped` (version pairing), `mut_statement_auth_root_{a,b,y}_flipped`,
`mut_statement_auth_binding_a_flipped`, `mut_statement_auth_count_a_plus_1`, `mut_statement_auth_owner_b_as_boundary`,
`mut_statement_auth_vu_index_shifted` (all `column challenge mismatch`: the digest changed under the prover's challenges).
The three the spec named are `auth_word_not_under_root`, `auth_wrong_index`, `auth_different_root`. Rejections are
authentication-specific (the Ligero checks pass first) in every prover-side case; Python and Rust agree on all 21
verdicts in all three included runs (`validation.detail`: "rust rejected 20/20, python rejected 20/20; honest included
proof accepted by both: True"). The pre-bench gate (r20260922-221538-c0c9 + r20260922-221826-e6d6, 2-VU proofs in all
three modes, 63 files) is where the negatives were first exercised; the D1 detour is in §5.

## 4. What each verifier checked

* **Python (live, per sub-batch, `verifier.seconds`)**: the full B-Ligero chain verifier (`protocol.verify`: root, coins,
  challenge recomputation, row/column tests, Merkle paths, chain constraints), then `auth.verify_auth`: positions from
  `vu_index` (column-major, contiguous per VU), limits, one leaf digest per published word (process pool), the library
  fold `verify_multiproof` to each root. `auth.verifier_seconds` 40.2-40.6 s of 41.5-42.3 s per 4096 VUs.
* **Rust `ligero-verify` (crate at 53cdb40, binary sha256 `f7cced54cbea0409…`, `--threads 16`, one process per proof,
  sequential sum)**: parses `LIGSTM03` / `LIGPRF02`, checks the auth block's schema, version, `n_vus`, monotone indices,
  tree count/owners/roots, `MAX_POSITIONS`/`MAX_OPENINGS`/`MAX_PROOF_BYTES`; `statement_digest` absorbs the same
  `digest_bytes` (pinned vectors shared with `tests/test_ligero_auth.py`); after the Ligero verdict it recomputes the
  leaves (SHA-256 written from FIPS 180-4 in `hash.rs`, tested against the standard vectors), folds (`auth.rs`,
  parallel over runs of known nodes) and compares roots; reports `timing.auth`. 14 unit + 4 fixture tests pass
  (bootstrap r20260922-221234-6929 and again at f28c13d before termination). Interactive rows: the runner's step-0 coins
  (`--coins`, D7); Fiat-Shamir rows: cold from the files. 75/75 per row. `DISCREPANCIES.md` **D9** records the third
  hash, the two file versions, the `digest_bytes` layout, the check order (Ligero first, so the reason strings differ
  from Python's for double faults) and `timing.auth`.

## 5. Deviations, detours, and what the spec had wrong

* **Harness order changed (f28c13d), and the controls were re-run under it.** Interleaving prove/verify per sub-batch
  (the previous B lanes' order) made the included prover's `tests` lap 3x slower (0.615 -> 1.84-2.06 s per rep) while every
  device lap was unchanged: the Python verifier's host work (a 64-process pool + a 261k-node Python fold per proof)
  between two timed sub-batches perturbs the host-bound part of the next one. Two fixes were tried and kept
  (3e04dc3: multiproof openings on *runs* of known leaves, `auth_openings` 180 ms -> 1-2 ms per sub-batch; 2de2fb5: one
  long-lived fork pool instead of one per verification, which removed half the effect) before the harness was changed to
  prove all 25 sub-batches of a rep and then verify them (f28c13d). Under that order the excluded control reproduces its
  interleaved number exactly (rep totals 1.530 vs 1.536 s; a: 1.673 both ways), so the delta is clean. Superseded runs,
  records fetched, not in the store: r20260922-221859-1af0 / r20260922-222501-6487 (controls at 53cdb40, interleaved:
  1.667 / 1.917 s), r20260922-223110-6642 (included non-ZK, slow openings: 7.148 s -- but the only run that *built* the
  trees, 29.40 s), r20260922-224139-1f0a (3.166 s), r20260922-224845-9db9 (2.930 s). Rep 1 is now ~0.7-1.0 s slow in every
  row (the first 25-proof burst after the warm-up; not investigated), the medians are reps 2/3.
* **D1 in the gate.** The first gate (c0c9) rejected every non-ZK L=256 2-VU proof for soundness (2^-127.5 < 2^-128,
  DISCREPANCIES D1), including the honest one; re-run with `--soundness-bits 127.5` (e6d6) the honest proof is accepted
  and every negative is rejected for its authentication reason. The 4096-VU runs are at 2^-128.04..-128.25 and need no
  such flag.
* **`--auth --auth-cache …` passed as one quoted argument** in my first driver (r20260922-222908-24c7, rc=2, no result).
* **The spec's "leaf encoding from `leaves.py`"**: `leaves.py` is the whole-tensor (`leaf/v1`) encoding used by the
  SP1 path; the word-level binding the spec asks for ("each VU's leaf indices") is the indexed-tree `u16` leaf of
  `merkle.py`, which is what was used. Stated in the fingerprint (`software.authentication.leaf`).
* **The store's verifier-acceptance key** is `verified` (vocabulary: `accepted | rejected | not-transferable | no-dumps`);
  the previous B lanes' `independently_verified` is now marked deprecated ("read, not written anew") -- both were
  written here, as instructed, with `verifier=ligero-verify@53cdb40`, `verifier_seconds`, `verify_note`. Fiat-Shamir rows
  carry `verified=accepted`; interactive rows `verified=not-transferable` (the store's own word for D7 transcripts).
  The vocabulary also says verification labels come from "an independent verifier, never the producer": these are the
  producer lane's labels about an independent *binary's* verdicts on the producer pod; a store-side verify pass would
  need the proof bytes (next point).
* **Proof bytes are not in the store** (as in every previous B lane: `bench_result.py` lists `bench_vu.json`,
  `verify/independent.json`, `proofs/manifest.json` as the run's files, not `proofs/`); they are in the local run dirs
  (`~/.research/runs/<run>/proofs/`, fetched `--all`, sha256-verified against the pod before it was terminated:
  `preserved.json`). The laptop disk hit 0 bytes free during the fetches (430/460 GB used by other things); `uv cache prune`
  and dropping the superseded runs' proof copies made room. Adding `proofs/` to the result's files is a storage-policy
  decision for the owner (~0.4-0.55 GB per run).
* **Store tooling**: the shared store's sqlite index had been migrated by newer `main` (`replicas` has 5 columns; 4987a47's
  code inserts 4, `attempt publish` reported `preserve_error`), so `attempt publish` / `push` / `label` / `snapshot` ran
  from the `main` worktree (1bd6573), as `fill-a100` did. `push --pending` also preserved 6 other lanes' pending artifacts.
* **Not done**: the fingerprint's `software.backend.commit` is null in `bench_vu.json` (the shipped tree has no `.git`);
  `result.json`'s `workload_fingerprint.commit` is f28c13d and the attempt record carries `source.commit`, `dirty: false`.
  Python verifier speed (40 s) was left as the library's `verify_multiproof`; a level-parallel fold would cut it ~10x.

## 6. Where this sits against `auth-integration`

`auth-integration` modelled (b) at +0.01 % prover over the ZK number and +2.8 kB per VU of openings under leaf/v1 row
leaves shared 146:1. Measured here with word leaves: prover +3-4 % (host-side openings and statement work, no GPU cost),
openings 0.2 B per VU (multiproofs of contiguous ranges collapse to ~26 siblings per 170 VUs), verifier +0.9 ms per VU in
Rust (~6,100 SHA-256 compressions per VU; the model's 68 per VU for row leaves would be ~90x less hashing). The
recommendation of that report -- option (d), the algebraic `leaf/v2` binding, private and free -- remains the target;
this lane delivers the sound, non-private baseline it is to be measured against.

## 7. Artifacts

| row | run | result | run-files |
|---|---|---|---|
| a | r20260922-231353-9010 | art:a6dbb3b8d46c7eeaad1f2c0b13b51efae48f052613edd3c867ecd94773dbd579 | art:5c1773fcfe4c9a84026235f4b837a4c7cd3ed58b6ddb8ee2d134939fcc6905cb |
| b | r20260922-231552-d579 | art:090f9b8054d9dc762367b5c85615f29ec13a7d61d01a2639b8ce9b7750ace637 | art:d247549fd140900839c83f8ec0c9a517e6b4b07cc4cc5c91a3ba1758cedbe29a |
| a' | r20260922-225547-7ab5 | art:aa3b1ab471a956258c129e3cc7db7195e81cae3ca27e31e5705e202b588aa03f | art:b7d84cfac3778e9003bbc1c668dde7eb5d38c3288455406ac653d6b5008f7ba5 |
| b' | r20260922-230019-edaa | art:13017f7d6eb81a4e9fe6d213f499f0096b33c75258b318c050cbbce7708c43d8 | art:8994e938961c6d1fe8dbbf4e97ff99195229525dc9b5c48da5a16f4c60a457c7 |
| c' | r20260922-230845-6c99 | art:b6bd5c1eb7f5b7be19f9b1f94cd035cb7e2b7c36f8e2381a765cae38efa2234d | art:d63dccbf9a680008037c5fd4c0db0be7a89c0fc06ec1d4fb9863b7ad9745db69 |

Snapshot `auth-included-a100-v1` = art:91531595abcf1d9c041dac9fc8f105690faf7e5a45b84210455031d7a05513dd (the five
results), PRESERVED; all seven attempts + outputs PRESERVED on s3://verity-dev. Labels (`--by auth-included --ref <run>`):
candidate=B-Ligero, hardware=a100, campaign=r21-auth-included, proof_class, mode, zk, authentication, K=1536, B=4096,
independently_verified=true, verified, verifier, verifier_seconds, verify_note, soundness, overhead, seconds_per_vu,
track=B, scope=vu, relation=bf16-k1536, assumptions=["hash"], omitted, instances_dataset, instances_tier, label,
breakthrough (true for the included rows: the campaign's first `authentication=included` results). Selects:

~~~
research data select --kind bench-result/v1 --label authentication=included --label candidate=B-Ligero   # a' b' c'
research data select --kind bench-result/v1 --label campaign=r21-auth-included                          # a b a' b' c'
~~~

Pod: vy-auth, 74 min at $1.59/h = **$1.96** (budget 2.5 h); the 11 launches (2 bootstrap attempts, 2 gate, 7 bench incl.
1 arg error and 3 superseded) are in `~/.research/runs/r20260922-22*`/`-23*`; `~/.research/machines.toml` marks the pod
terminated. Laptop: `uv run -q pytest packages/verity backends/numerical/tests tests -q` -> 958 passed, 9 skipped;
`rg -l '^<<<<<<< '` empty; `tests/test_ligero_auth.py` runs torch-free (the proof v2 round trip `importorskip`s torch;
7/7 with torch on the pod).

Commands (pod, `--source .` at each commit, `--exclusive`, `--tool bench_vu --scratch triton --require-result`):
~~~
/workspace/venv312/bin/python backends/direct/ligero/bench_result.py bench-vu [--zk] --mode interactive|fiat-shamir \
  [--auth --auth-cache /workspace/auth-trees-4096 --auth-procs 64] --batch 16384 --total-vus 4096 --reps 3 \
  --root /workspace/bench-instances/v1 --device cuda --verifier /workspace/bin/ligero-verify --threads 16
~~~
