---
lane: ajtai-leaf-3
kind: report
created: 2026-09-23T22:19Z
status: final
---

CHECKPOINT 47d191e2 (22:55Z) [open] benches done r20260923-223427-9bab (G1 binary, all Rust pinned+accepted): fp8 depth4 bare 0.2153 / +hash 0.4484 / +ajtai-n64 0.4469; bf16 depth4 bare 0.2798 / +hash 0.8359 / +ajtai-n128 OOM (24 GB) -> depth3 1.4071 (bare 0.3292, +hash 0.8231); gates 0 failures; pushing runs to R2, then FINAL + terminate
CHECKPOINT 62e3fde (22:35Z) [open] G1 fixed Rust 8768997 + Python/fixture 62e3fde (old binary ACCEPTS the decoy fixture unpinned, new refuses pinned+unpinned; cargo 30+7+20, ajtai_key_test 6/6); depth-4 Ajtai still OOM with chunking alone (probe2 r20260923-222856-552a); final stage r20260923-223427-9bab running: gates + 6 arms (Ajtai depth 4 w/ expandable_segments+chunks, fallback 3/2) + Rust batch on the G1 binary
CHECKPOINT 2b5ec89 (22:30Z) [open] G1 fixed in Rust 8768997 (key check follows the digest lanes; cargo 30+7+19 ok); Ajtai arms OOM at --pipeline 4 on the 4090 (stage-B r20260923-211722-820d and my probe r20260923-222305-27a7, expandable_segments does not help) -> bounded chain-test memory 2b5ec89 (bit-identical); probe2 r20260923-222856-552a running (G1 binary + both Ajtai arms at depth 4, enc chunk 16/8). Next: Python G1 check + end-to-end decoy fixture, then the full bench set.
CHECKPOINT 1cf9178 (22:19Z) [open] started; worktree lane/ajtai-leaf-3 @ 1cf9178; reading F6 check_system_key for G1 fix; checking stage-B pod run r20260923-211722-820d

# Lane ajtai-leaf-3: G1 fix (the Ajtai key check), benches at `--pipeline 4`

Worktree `~/projects/verity-main-wt/ajtai-leaf-3` on `lane/ajtai-leaf-3` (from `lane/ajtai-leaf-2` @ 1cf9178; the predecessor's
worktree had no uncommitted diff). Pod `vy-ajtai-leaf` qam33gj60dv60g (RTX 4090, $0.74/h). Campaign `r22-ajtai-leaf-3`.

## FINAL (23:08Z)
**Branch tip `lane/ajtai-leaf-3` @ 47d191e** (4 commits on 1cf9178; local shared .git like the other ajtai lanes; not merged).

* **G1 fixed, Rust + Python, pinned and `--allow-any-system`.** The key check no longer scans for the coefficient pattern. It starts
  from each public digest lane `hash.d[x]` and follows the compiled system: the lane's unique pin row, then the unique
  `is_end * (out - d) = 0` tie, then the unique linear row on `out`. That row must be lane x's key row over the chain-linked
  neighbour's `acc_in`, with every bit coefficient equal to the SHAKE-256-derived B, and bit rows that are one per position,
  consistent across the role's n key rows, in bit order, boolean-constrained and disjoint across roles (Rust `leaf.rs::chain_key`,
  8768997; Python twin `leaf.ajtai.chain_key` run once per system by `HashedRelationRunner.verify_vus`, 62e3fde).
  **Must-reject negative:** fixture `fp8-ada-ajtai-n64-g1-decoy` (chain uses B = 0, 2n decoy key rows elsewhere, every digest 0).
  The old 1cf9178 binary ACCEPTS it with `--allow-any-system`. The new binary refuses it unpinned (key row check) and pinned
  (system mismatch) in `verify` and `batch` (`tests/relations.rs::ajtai_g1_decoy_fixture_is_refused`). The Python verifier refuses
  the decoy proof end to end (`leaf/ajtai_key_test.py` 6/6). Rust unit tests also refuse a moved bit, a doubled key and a rerouted
  or doubled tie. Verifier-only change: **no digest changed, no re-pin** (18d91532/a1f2cb20, 29f18689/e4dcecce).
* **Gates 0 failures** on the G1 binary (fp8-ada+ajtai-n64: 7 honest, 92 negatives; bf16-hopper+ajtai-n128: 4 honest, 92
  negatives). Pod `cargo test --release` 30 + 7 + 20 ok.
* **Benches, same 4090, 4096 VUs, l = 16384, local coins, t.total (s):**

  | relation | bare | +hash (Poseidon2) | +ajtai | depth |
  |---|---|---|---|---|
  | fp8-ada | 0.2153 | 0.4484 | **0.4469** (n64) | 4 |
  | bf16-hopper | 0.2798 | 0.8359 | **OOM** (n128) | 4 |
  | bf16-hopper | 0.3292 | 0.8231 | **1.4071** (n128) | 3 |

  fp8 Ajtai = Poseidon2 at depth 4 (repeat 0.4456). bf16 Ajtai-n128 does not fit depth 4 on 24 GB even with chunked chain-test memory
  (2b5ec89, 47d191e, bit-identical) + `expandable_segments`: the prover OOMs in `hash_hints` with 10.3 GB in per-stream CUDA-graph pools.
  At depth 3 it costs 1.71x Poseidon2.
* **Rust batch: every sub-batch accepted, `system_pinned=true`** in every arm (fp8 13/13, bf16 25/25).
* **`+shared` Ajtai: not run.** share-logup-3 53452a6's `SharedHashedRunner` hashes rows with Poseidon2 only (refuses other leaves).
* **Artifacts (R2, remote present + verified):** final a0dc1a4b…, retry b6b526d4…, stage B 355f5334…, probes c1f6c5e7… / 2f731699…
  (full ids in Artifacts).
* **Pod** terminated 23:05:35Z (not in `pods list`). This lane's time 22:18Z to 23:05Z = 0.79 h x $0.74 = **~$0.59; remaining ~$2.41** of $3.
* **Remaining:** (1) bf16-hopper+ajtai-n128 at depth 4 needs > 24 GB or fewer graph pools: an 80 GB card, or sharing one tests
  graph across streams. (2) Ajtai `+shared` needs `row_hash_system` generalised to a `LeafScheme`, plus the pair verifier's key check.
  (3) The conformance harness's synthetic bf16 words fail `test_chain_witness_matches_native_and_starts_at_zero` for every scheme
  (pre-existing, harness only). (4) Unpinned mode proves the digests are derived-key Ring-SIS digests of boolean rows. That those
  rows are the relation's operands still rests on the system pin.

## 1. Predecessor's stage B (r20260923-211722-820d, on the pod, tree 1cf9178): read at 22:22Z
* cargo 27 + 7 + 19 ok; both gates **0 failures** (fp8-ada+ajtai-n64 2048 VUs: 7 honest, 92 negatives; bf16-hopper+ajtai-n128 512
  VUs: 4 honest, 92 negatives).
* Benches at `--pipeline 4` (4096 VUs, l = 16384, --zk interactive, local coins), Rust batch pinned: fp8-ada bare **0.2235 s** (13/13),
  `+hash` **0.4560 s** (13/13, now really pipelined); bf16-hopper bare **0.2785 s** (25/25), `+hash` **0.8393 s** (25/25).
* **Both Ajtai arms died with CUDA OOM** in the tests graph (`chain_coefs` / `extra_coefs`): 4 pipelined streams x the Ajtai chain
  test (131 / 259 linked rows vs Poseidon2's 19) do not fit in 24 GB.
* pytest leaf + conformance (fp8-ada) 102 passed; conformance with `REL=bf16-hopper`: 3 failures, all
  `test_chain_witness_matches_native_and_starts_at_zero[dummy|poseidon2|ajtai-n128]` with "public inputs rejected: a.t off the
  finite range" -- the conformance harness's synthetic bf16 words, not the scheme (dummy and Poseidon2 fail the same way).

## 2. G1 (red-team-leaf-2): the Rust key check was a pattern scan -> now follows the digest lanes (8768997)
`leaf.rs::check_system_key` counted any linear row whose coefficients matched a derived key row, so a system whose real chain used
B = 0 plus 2n decoy rows carrying the derived key over always-zero rows passed (`verify --allow-any-system` accepted, every digest 0).
New `leaf.rs::chain_key(sys, n, B)`: starting from the statement's public lanes `hash.d[x]` (x < n the x digest, else W):
the one linear row `W[pin row] = pub` carrying the lane -> the one quadratic touching that row, which must be
`is_end * (out - d) = 0` -> the one linear row touching `out`, which must be lane x's key row
`out - (X acc_in)[x mod n] - sum_i B[x mod n][o + i] bit_i` with `acc_in` = the chain row the NEIGHBOUR lane's `out` is linked into
(y = out; 0 at a chain start) and every coefficient equal to the SHAKE-256-derived B of the lane's role block; the bit rows: one per
bit position, the same in all n key rows of a role, increasing in bit position (word-major LSB-first, the compose's allocation
order), boolean-constrained, disjoint across roles and from every chain / pin row. Runs pinned and `--allow-any-system`.
Scope (stated in the doc comment): unpinned, this proves the published digests are the derived-key Ring-SIS digests of those boolean
rows; that those rows are the operands the relation multiplies is the system pin's job (unpinned mode trusts the system file anyway).
Tests: `leaf.rs` unit tests on both pinned fixture systems (accept; 256 bit rows per role, n key rows each; the other degree's key
refused), **G1 in memory** (bit terms dropped from the real key rows + decoy key rows over fresh rows -> refused), one key row reading
bit 5 off another row, x role reading bit 5 off the W role consistently, key doubled on one row, lane 0's tie rerouted, a second tie
-> all refused. `tests/relations.rs`: the Poseidon2 / bare systems under an Ajtai statement unpinned now fail with "hash.d[16] is not
pinned" / "hash.is_end is not pinned"; n64 statement on the n128 system unpinned is now refused by the key check (the pattern scan
passed it: B_128's first 64 coefficients are B_64). Full `cargo test --release` 30 + 7 + 19 ok (laptop). Digests unchanged (the
check is verifier-only; no re-pin).

## 3. `--pipeline 4` OOM (Ajtai only)
Probe r20260923-222305-27a7 (tree 1cf9178, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`): both arms still OOM, 20.5 GB allocated
(10.5 GB in CUDA-graph private pools): not fragmentation. Per stream the chain test holds `chain_coefs`' (D, V, l) / (D, T, l)
temporaries (~1.4 GB for n64) and the 64-row encode chunk (~0.8 GB). 2b5ec89: mask in place, index_add the terms in chunks
(`LIGERO_CHAIN_TERM_CHUNK`, 64), encode chunk knob `LIGERO_CHAIN_ENC_CHUNK` (64); sums reduced mod p once, bit-identical
(`chain_test.py` 3/3 and `leaf/ajtai_test.py` 11/11 on the CPU with chunks 3-7).

Probe 2 r20260923-222856-552a (tree 2b5ec89, chunking alone): still OOM (fp8: 16.3 GB allocated + 5.1 GB reserved-unallocated; bf16:
12.9 + 9.1 GB): with the chunks, fragmentation dominates.
**Final stage r20260923-223427-9bab (tree 62e3fde):** chunking + `expandable_segments:True`, `LIGERO_CHAIN_ENC_CHUNK=16`,
`LIGERO_CHAIN_TERM_CHUNK=32`: **fp8-ada+ajtai-n64 fits at depth 4** (peak 11.6 GB). bf16-hopper+ajtai-n128 at depth 4 still OOMed,
but in the in-bench PYTHON VERIFIER (`protocol.verify` encoded all ~520 chain coefficient rows at once, 1.5 GB, beside the prover's
graph pools), not the prover -> 47d191e chunks that encode too (bit-identical; ajtai/chain/key tests 20/20 on CPU with chunk 5).
Depth 3 fits (peak 14.1 GB). Retry r20260923-224543-40e2 (tree 47d191e, same knobs): fp8-ada+ajtai-n64 depth 4 again 0.4456 s
(13/13); bf16-hopper+ajtai-n128 depth 4 now gets past the verifier encode but the PROVER OOMs in `hash_hints` (21.9 GB allocated,
10.3 GB in CUDA-graph private pools): depth 4 x n = 128 does not fit a 24 GB card with per-stream graphs.

## 4. Results (4090 qam33gj60dv60g, 4096 VUs, l = 16384, --zk interactive, local coins, 3 reps, rep-1 dump -> Rust `batch` built
from 62e3fde = the G1 binary, sha256 68c35dcb…)
* pod `cargo test --release` 30 + 7 + 20 ok; system digests unchanged (18d91532 / a1f2cb20, 29f18689 / e4dcecce): no re-pin.
* gates (the Python verifier now runs the chain-key check): fp8-ada+ajtai-n64 2048 VUs **7 honest, 92 negatives, 0 failures**;
  bf16-hopper+ajtai-n128 512 VUs **4 honest, 92 negatives, 0 failures**.

Same pod, same session, final stage r20260923-223427-9bab unless noted (every Rust batch `system_pinned=true`, `batch_accepted=true`):

| relation | leaf | depth | rows/unit | t.total (s) | split.tests | split.hints | peak (GB) | Rust |
|---|---|---|---|---|---|---|---|---|
| fp8-ada | bare | 4 | 3769 | **0.2153** | 0.128 | 0.016 | 6.6 | 13/13 |
| fp8-ada | +hash (Poseidon2) | 4 | 6210 | **0.4484** | 0.267 | 0.075 | 10.9 | 13/13 |
| fp8-ada | **+ajtai-n64** | 4 | 4858 | **0.4469** | 0.283 | 0.091 | 11.6 | 13/13 |
| fp8-ada | +ajtai-n64 (retry r20260923-224543-40e2, tree 47d191e) | 4 | 4858 | 0.4456 | 0.286 | 0.088 | 9.7 | 13/13 |
| bf16-hopper | bare | 4 | 3292 | **0.2798** | 0.162 | 0.021 | 5.5 | 25/25 |
| bf16-hopper | +hash (Poseidon2) | 4 | 5637 | **0.8359** | 0.503 | 0.126 | 10.5 | 25/25 |
| bf16-hopper | +ajtai-n128 | 4 | 4669 | **OOM** (24 GB) | | | > 23.4 | — |
| bf16-hopper | bare | 3 | 3292 | 0.3292 | 0.200 | 0.012 | 4.3 | 25/25 |
| bf16-hopper | +hash (Poseidon2) | 3 | 5637 | 0.8231 | 0.512 | 0.117 | 10.5 | 25/25 |
| bf16-hopper | **+ajtai-n128** | 3 | 4669 | **1.4071** | 0.915 | 0.271 | 14.1 | 25/25 |
| fp8-ada | bare / +hash | 3 | | 0.2204 / 0.4719 | | | 5.1 / 10.9 | 13/13, 13/13 |

Reading: on fp8-ada the Ajtai leaf costs the same as Poseidon2 at depth 4 (0.447 vs 0.448 s, 2.08x bare; was 1.055 vs 0.648 s
unpipelined): fewer rows (4858 vs 6210) buy back what the 131-link chain test costs (tests 0.283 vs 0.267 s). On bf16-hopper the
n = 128 key doubles the chain (259 links, 512 extras): depth 4 does not fit a 24 GB 4090 (after 47d191e the prover itself OOMs in
`hash_hints`, 21.9 GB allocated, 10.3 GB in graph pools: r20260923-224543-40e2), and at depth 3 it is 1.71x Poseidon2 (1.407 vs
0.823 s; was 5.79 s / 3.10 s sequential), the chain test dominating (0.92 s). Stage B (tree 1cf9178, the old binary) matches:
bare 0.2235 / +hash 0.4560 / hbare 0.2785 / hhash 0.8393.

## 5. `+shared` with the Ajtai leaf: not possible on share-logup-3 53452a6
`SharedHashedRunner.__init__` refuses every leaf but Poseidon2 ("row sharing hashes with Poseidon2 only (hashchain.row_hash_system)"):
the H proof's row-hash system is the Poseidon2 sponge. An Ajtai `+shared` needs `row_hash_system` generalised to a `LeafScheme`
(the Ajtai gadget per row) and the pair verifier's key check; not attempted (two lanes' relchain.py diverge by ~2.8k lines each).

## Artifacts (all `run-files/v1`, `research data put --preserve`: remote present + verified; meta `lane=ajtai-leaf-3`)
| art | run | what |
|---|---|---|
| art:a0dc1a4b45be3f2256ed7b127f74a78d64e61a428edd5d06ca7493fb88c88b2c | r20260923-223427-9bab | **final stage** (tree 62e3fde): cargo, both gates, all table arms + Rust batch dumps (669 blobs, 1.1 GB) |
| art:b6b526d4cc37da02a4dea8268e745a701a3532f3420194e9ab5c7816a6f6e8f2 | r20260923-224543-40e2 | retry (tree 47d191e): fp8 Ajtai depth 4 0.4456 s, bf16 Ajtai depth 4 prover OOM |
| art:355f533413be23742f376b7b8bab1bfd07eee8e5007cbbd0f94eb9bff84fc88c | r20260923-211722-820d | predecessor's stage B (tree 1cf9178): gates, controls, Ajtai OOM |
| art:c1f6c5e75c1eb7927bf9859473a2f959decff313434776b6892c08208f578c8a | r20260923-222305-27a7 | probe 1 (expandable_segments alone: OOM) |
| art:2f731699e2d4fa1b051b4b965bcfbaf483c7f30b73e4154bd725acfcece685b2 | r20260923-222856-552a | probe 2 (chunking alone: OOM) |

These pod runs have no store *attempt* record (`research data preserved RUN` says "attempt not in the store": they were launched
through `pods run`, and `research fetch --all` silently copied only 4 KB of the 1.2 GB final run, so the run dirs were copied with tar
over ssh and put as trees). The run-files artifacts above are the durable copy.

## Log
* 22:18Z start; briefs + reports read. 22:23Z probe 1; 22:27Z Rust G1 committed; 22:29Z probe 2; 22:34Z final stage.
* 22:32Z decoy fixture: the 1cf9178 binary `verify --allow-any-system` ACCEPTS `fixtures/fp8-ada-ajtai-n64-g1-decoy` ("accept ...
  [system NOT pinned]"); the 62e3fde binary refuses it unpinned ("hash.d[0]: the key row is not out - (X acc_in)[0] - B[0] bits over
  the linked neighbour") and pinned ("not the pinned hashed (ajtai-n64 leaves) fp8-ada system").
* 22:45Z retry r20260923-224543-40e2 (47d191e). 22:52Z both run dirs copied by tar over ssh (`research fetch --all` got 4 KB).
  22:55-23:02Z five runs put + preserved on R2. 23:05:35Z pod terminated. 23:08Z FINAL.
