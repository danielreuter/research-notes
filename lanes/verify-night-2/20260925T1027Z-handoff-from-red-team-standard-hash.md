---
lane: verify-night-2
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:27Z
cc: verify-night-2
---

# fp8-ada+blake3 @3301c435: CLASS GRANTED WITH CONDITIONS: a cell counts only if its dump passes main 3301c435's reverify.py (R1/R2/R4 + hash-commitment recomputation) or verify-night-2's 06, with 04 BOUND ≥ 2^-128; nothing verified before 3301c435 counts

Red-team verdict on the frame-v3 keyed-BLAKE3 v5 included-hash statement (schema `blake3-keyed/row/v2`, fp8-ada
half-block, 48 columns) as merged in main 3301c435. Declared class `COMPLETE_ZK_BACKEND`: granted, on the conditions below.

**Attacks run on main 3301c435** (pod tree from a `git diff` apply, 0 of 3112 blobs differ from `ls-tree`; ligero-verify built
from that tree). Evidence art:cd2828c5.
- R1, prover-chosen (vu, x, W) triple, with `--set-binding` so the a/b trees equal the core's: **refused** by Python, by Rust
  pinned (`layout_error`) and by reverify. Before 3301c435 this forgery was accepted (art:2b51c5fd, art:8f2112e2).
- R4, orphan `.stmt` and stmt-only manifest entry (3 VUs, only VU 0 proven): **refused**; the honest control passes.
- H2, steps pin: honest 48 accepted; forged 64 refused by both verifiers.
- R2: `reverify.py` recomputes the a/b/y trees from the instance set (`hashauth.binding_digest` of dataset, manifest digest,
  range), compares binding, owner, count and root per tree, and checks that every VU is covered once per rep. No dump
  without a manifest `set` block, and no v6 shared-row dump, is accepted. Code read at 3301c435; the R1 `--set-binding`
  forgery above also exercises it.

**BLAKE3 gadget scan: 0 free rows.** Evidence art:70722cab (preserved). `rtsh_blake3_free_rows.py` (branch
`lane/red-team-standard-hash` 3ee25e12) builds the honest column system, then for every computed row overrides it (1 − v or
v + 1) at one column, recomputes everything downstream and re-checks every linear and quadratic constraint. A row counts as
free if some override still satisfies all constraints.
- Shapes 8:0.5 (the fp8-ada+blake3 layout), 8:1, 16:1 and 8:2 (the x4 fold): 0 free rows in 61k, 61k, 61k and 123k mutations.
  The honest path passes and the digest equals `blake3(row, key=key_for(role))` in every shape.
- Control (one `lo.decomp` constraint dropped): 18 free rows, so the scan detects a missing constraint.
- The scan ran on the 806a2f73 tree. Its constraint program is identical to main's: the only differences in `leaf/` and
  `leaf.rs` are the batched native `leaf_bytes_many` helper and two extra PINS rows (bf16-ampere, fp8-hopper), both of
  which 806a2f73 adds and main lacks. The diff stat is in the artifact.

**Gadget and native tree check (code read; nothing found).** The operand words are sums of boolean bit rows, so the limbs
cannot alias. The layout, counter and flags come from the carried `pos`, and the chain start forces the carry to 0. The digest
is pinned at `is_end`. The verifier folds the published chunk CVs into the root in `leaf_bytes`, under a key and header that
carry the role. Earlier: art:be211735, art:cd2c38ea.

**Conditions**
1. Each cell's dump passes main 3301c435's `reverify.py` or verify-night-2's 06 ROOTS-MATCH, run by verify-night-2. `ligero-verify`
   alone does not enforce R2: it reads binding, owner, count and root from the statement.
2. 04 BOUND shows the whole-proof bound at or below 2^-128. I did not audit the soundness accounting.
3. Nothing verified before 3301c435 counts, including the 4090 cells art:e9932b72, art:e7d59ab6, art:5d20ad00 and art:d6328cf5
   until verify-night-2 re-verifies them. I did not examine those four dumps myself. art:e9932b72 is a live same-pod
   verifier cell produced at 806a2f73; the condition is the same for it.

**Scope and still open**
- The zero-knowledge half of the class is inherited from the unchanged Ligero core and was not re-audited. The published
  digests and roots are unsalted functions of the operand rows. That is part of the committed-relation statement (SP1 does
  the same), so ZK holds relative to them.
- Completeness nit (not soundness): steps 32 with blake3 crashes the honest prover, because the gadget refuses 1-chunk
  rows (ligero-steps-pin 0937Z, art:61aedd27).
- verify-night-2 1030Z found that the y root is not backend-neutral (SP1 uses the raw FP32 word, B-Ligero `pack_public`).
  That is a design-claim issue, not a soundness issue for this statement.
- +sha256 (da74b03e) class verdict follows once its gadget scan finishes (running now; control 17 free rows).

**File renames (clock drift).** My earlier handoffs `coordinator/20260925T1030Z-…` and `…T1130Z-…` are now
`20260925T0952Z-handoff-from-red-team-standard-hash.md` and `20260925T1017Z-handoff-from-red-team-standard-hash.md`.
Your `verify-night-2/20260925T1024Z-handoff-from-coordinator.md` cites the old 1130Z name.
