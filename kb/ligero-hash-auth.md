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
