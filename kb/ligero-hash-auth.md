# B-Ligero included-hash (`+<leaf>`) cells: verifier rules and costs

The operands are private witness wires, hashed inside the relation (`relchain.HashedRelationRunner`, `--auth included-hash`).
The statement carries a/b/y tree references plus SHA-256 multiproofs of the row leaves. Leaf schemes live in
`backends/direct/ligero/leaf/` (poseidon2 = `+hash`; blake3 = `+blake3`, schema `blake3-keyed/row/v2`, frame-v3 trees).

## What a verifier must check (red-team-standard-hash R1 / R2 / R4, 2026-09-25)

**R1: the layout** (`hashauth.layout_error` and Rust `auth.rs`; lane/b-ligero-standard-hash 3af90e71 = ligero-steps-pin
71905f0f). Each VU's (x row, W column) is derived from its `vu_index` and the committed tree counts:
- a = b = y counts: x = W = vu;
- a.count × b.count = y.count (a tile): x = vu // nw, W = vu % nw;
- any other layout is refused.

A prover-chosen triple otherwise binds a VU to another VU's operands (the remap forgery, art:9fa210e7…).

**R2: the commitment is the instance set's** (`reverify.commitment_problems`, de2fa317 = 3e98dc55). File re-verification
recomputes the a/b/y bindings and roots from the regenerated frozen set, and requires each rep's statements to cover
`[0, total_vus)` exactly once. A dump whose manifest `set` block has no tile (shared / tile dumps) fails closed.

**R4: coverage counts only what `batch` verifies** (ligero-steps-pin 06176b41, plus b-ligero-standard-hash 806a2f73 for
unreadable statements). Rust `batch --dir` verifies `*.proof` only, and `n_proofs` is chosen per statement by the prover.
So a `.stmt` without a `.proof` claimed VUs nobody proved (art:c7683eb2…). The rules:
- each rep's `.stmt` stems = its `.proof` stems = its manifest entries;
- no stmt-only manifest entry;
- batch `n` = the rep's statement count;
- a relation named `+<leaf>` is hashed whatever its statements carry.

**Pitfall:** the pinned relation handed to `commitment_problems` is the statement's (`manifest.relation.statement_relation`,
what Rust `system-digest` pins, e.g. `fp8-ada+blake3`). The base name `fp8-ada` recomputes under the Poseidon2 schema, and
every binding then "mismatches" (b-ligero-standard-hash report, 08:19Z).

## Costs (fp8-ada+blake3, RTX 4090; b-ligero-standard-hash report)

- **The x1 fold wastes half the blocks.** fp8-ada has 48 columns per VU of 32 B each, which is half a BLAKE3 block, so
  every column's second compression half is padding. `fp8-ada-x4` (12 columns, two whole compressions per role per column)
  removes the waste.
- **Pinned gadget vs the survey §3.2 XOR-output-bits design.** On the same inputs (CPU census, `leaf/blake3_xob.py`,
  8dace837), the pinned gadget is 15 139 rows per 64-byte block and the XOB design is 11 746 (0.776×). Per fp8 VU (48
  blocks) that is 726 672 vs 563 808 hash rows. XOB needs a new witness op (`xadd`) in every witness generator, plus new
  pins.
- **Plateau before main's GPU committer** (sweep r20260925-073210-f45c, l = 4096, p = 2, `--commit-per-rep`): 870 VU/s
  e2e at 16 384 VUs (art:d6328cf5…). The commitment was ~2.2 s of ~19 s per rep; 32 768 VUs OOM on 24 GB.
- **After main's GPU committer and the x4 fold** (b-ligero-standard-hash, RTX 4090, tree 806a2f73; l = 4096, p2, 5 reps,
  `--commit-per-rep`, malloc env):
  - fp8-ada+blake3, 4096 frozen: e2e 3.558 s (1151 VU/s, commit 0.011 s), art:9b80f566…;
  - fp8-ada-x4+blake3, 4096: e2e 1.981 s (2067 VU/s), art:050ddede…;
  - x4 plateau at 8192: 2165 VU/s, art:19be6afa….

  The x4 fold is 1.8× x1, as the row count predicts: 79 184 rows per column × 12 columns vs 35 370 × 48. On a 24 GB
  4090, x4 at l = 4096 fits only at p2 (p3 OOMs; peak 18.7 GB at p2).
- **The malloc env** (MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12) gained +2.7 % at the x4 plateau on the 4090
  (2108.7 -> 2165.0 VU/s). The prover's per-rep times were already steady there.
- **x1 plateau with the GPU committer and the malloc env** (r20260925-103611-67e0): 1185 VU/s e2e at 16 384 VUs
  (art:c9f4a645…). **32 768 VUs is killed by the host OOM killer (rc -9)** with MALLOC_TRIM_THRESHOLD_=1e12: freed heap is
  never returned, and the in-process verifier holds 386 proofs. The x1 sweep therefore stops on "a point failed", not on
  the 2 % rule.
- **`blake3-xob` scheme** (b-ligero-standard-hash, 5b28557b): the `blake3` leaf proved with the XOB compression. It is a
  `Blake3Leaf` subclass that overrides only `_compress`, with the same schema `blake3-keyed/row/v2` and the same params,
  so the commitments are byte-identical to +blake3. Its circuit and pins are its own:

  | Relation | sys | rows | hash rows |
  |---|---|---|---|
  | fp8-ada+blake3-xob | 3d6cc67b… | 28 584 (vs 35 370, -19 %) | 24 012 |
  | fp8-ada-x4+blake3-xob | f90e7b41… | 65 612 | |

  Gated at 2048 VUs + 86 negatives each. The `xadd` witness op is kind 6 in the interpreter tables (4 operands, 32 rows
  written). Two schemes may now share a schema: `by_schema` returns the first registered (blake3), and conformance
  requires twins to share params, layout and `leaf_bytes`. **Its cells are provisional until red-team grants the class.**
## `+sha256` (schema `sha256/row/v1`, lane b-ligero-sha256, 2026-09-25)

- **Leaf and statement.**
  - Leaf: `SHA-256(prefix64(role, word_bits, n_words) || row_bytes)`, the core frame-v3 row digest.
  - The data blocks are compressed in-circuit from the prefix midstate. The verifier does the padding compression
    (Rust `sha256_leaf_bytes`).
  - Gadget: 18 128 rows per 64-byte block. Digest 17 elements (header + 16 CV limbs), carry 33.
  - Red-team class: `COMPLETE_ZK_BACKEND` granted with conditions (red-team 1033Z).
    - Gadget scan found 0 free rows in 150 208 mutations (art:a3c5c339).
    - Nothing before da74b03e counts: R1 is open there.
- **Rows per column (x4 fold):**

  | Relation | m | base | hash | sys |
  |---|---|---|---|---|
  | fp8-hopper-x4+sha256 | 89 356 | 13 383 | 73 122 | 6cf20505… |
  | bf16-hopper-x4+sha256 | 88 381 | 12 792 | 73 122 | a02f283d… (PINS b009fdc8) |

  That is about 6.7x the bare relation.
- **The row-chain fast path matters.** `hashchain.row_chain` uses `leaf.row_sponges` when the scheme has it, and
  `Sha256Leaf.row_sponges` is a cupy kernel with one thread per row (88b82757).
  - Without it, the host numpy fold ran twice per rep: commitment 7.9 s and row chains 12.3 s per 8192 VUs.
  - With it: 0.065 s and 0.011 s.
- **H100 cells** (l = 4096, p4, `--commit-per-rep`, sweep plateau):
  - fp8-hopper-x4+sha256: 32 768 VUs, e2e 5.317 s, 6162 VU/s, 2^-128.07, art:4aa258ee… (proofs art:61842848…).
  - bf16-hopper-x4+sha256: 8192 VUs, e2e 2.675 s, 3062 VU/s, 2^-128.40, art:fcd6a623… (proofs art:c25cac59…).
- **The malloc env is decisive on the H100 pod** (qmiq4rs1f0y4tr).
  - First-touch host page faults run at ~20 MB/s. A fresh 91 MB numpy copy takes 4-7 s; a reused buffer takes 8 ms
    (art:9771957…).
  - `openings_device.opened_from_pinned` re-faults the opened columns every proof: 2.29 of 2.49 s per proof
    (art:255ea993…).
  - With MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12, the 8192-VU prover went from 7.7-29 s to 1.36-1.40 s per rep.
  - The env is now in pod_bootstrap's env.sh and in every fingerprint (`software.allocator`, main 767115db).
- **instance-equiv/v1 for re-packed relations** (x4 etc.): run `python -m verity_numerical.bench.instance_equiv --relation
  <rel> --vus 4096 --out F` on a pod, then `research data put --kind instance-equiv/v1 --meta @F+lane --preserve` (the
  renderer reads the meta). The kind is not in the CLI's known list; it prints "storing anyway", which is fine. The tool's
  `tool` field is `@unknown` on pods (REPO = parents[4]; set RESEARCH_GIT_COMMIT). Since main bfb0b928 (PR #21) `frozen`
  may be the frozen ref, a prefix of it, or the synthetic stream over [0, n) by generator / seed / n, so sweep plateaus
  past 4096 get their own document (`--vus n`); `candidate` must equal the result's `workload_fingerprint.instances`.
  Examples: x4 8192 art:d9b3724d, x4 32768 art:b6f2e1df. If the pod tree is older and busy, overlaying main's
  `bench/{instance_equiv,tables,views}.py` on a copy of verity_numerical first on PYTHONPATH works; the loaders
  (relchain) are unchanged (b-ligero-standard-hash 43-equiv-8192.sh).
## Real K (x4 folds at K = 2048 / 8192, lane bligero-real-k; red-team-bligero-real-k 2026-09-26)

- **Class:** `<fold>-k<K>+blake3-xob` / `+sha256` are COMPLETE_ZK_BACKEND, granted with conditions
  (`lanes/coordinator/20260926T0917Z-handoff-from-red-team-bligero-real-k.md`, evidence art:dc790613).
  - K is enforced three ways: the per-K hashed pins, the pinned `steps`, and the binding's K.
  - A BF16 bare real-K system carries its fold's K1536 sys_id, so `system-digest` names it as the fold.
- **The live verifier's `--drop-files` loses the timed reps' files.** Only rep 1 is dumped and re-verified, and neither the live
  verifier nor Rust `batch` checks coverage: `batch` accepts a rep that holds sub_00 twice.
  - So check that every session's per-sub-batch `stmt_sha256` equals rep 1's, and that the proofs differ.
  - Script: `lanes/red-team-bligero-real-k/evidence/sessions_xrep.py`.
- **The chain test's field term is not booked.**
  - With nl > 3 linked rows, the extra constraints' coefficients are monomials (`chain.extra_coef`). A violated constraint survives
    a challenge coordinate with probability deg / p, where deg = (2 (nl - 3) - 1) div 6 + 2, so the term is (deg / p)^D.
  - `protocol.soundness` and Rust `soundness()` book `linear_field = 1 / p^D`.
  - Per proof at D = 6: SHA-256 (nl 69) 2^-158.3; blake3-xob 3-slot (nl 133) 2^-152.5; BF16 K2048 (nl 165) 2^-150.75; FP8 K8192
    (nl 293) 2^-145.75; BF16 K8192 (nl 549) 2^-140.35.
  - Re-bound a cell's union before calling it at or below 2^-128. The tightest cell, b1d710da, is 2^-128.086 with the term.
