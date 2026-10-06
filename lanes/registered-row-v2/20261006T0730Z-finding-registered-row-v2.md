---
id: registered-row-v2/20261006T0730Z-finding-registered-row-v2
campaign: proof-service
lane: registered-row-v2
kind: finding
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# P7: registered values as hm96-sha512/row/v2, and the tensor table

Item P7 of `note:verity-root/20261006T0550Z-report-proof-service-implementation`, on branch `cursor/registered-row-v2-95d4`
(base `origin/main` 68e614869).

## What holds

- A registered row is now the bit row of its leaves (`bit_row((row, word_bits))`), committed as `hm96-sha512/row/v2` over
  `sha512/row/v2`. Its prefix carries the row's length in bits, so a weight row's digest is PoUW's digest of the same row.
  The registered domain is `verity/one-stage/registered-domain/v1`, and the Lean verifier's reads file is
  `verity/registered-reads/v1`, which requires `words` and `word_bits`.
- The Lean verifier accepts a registered port only if it is a v2 bit row, not segmented, of exactly `words * word_bits`
  bits. The Proofs package's `checkPort_ok` and `check_ok` now conclude `reg.fits c.ports[p]! = true`, so the `ZkReg`
  records change and are re-pinned (run r20261006-065646-05b7, node 2).
- The in-tree Rust prover needed no change: it already proves v2 bit rows, with the length in the in-circuit digest's
  prefix, and it ignores the header's `registered`. End to end on node 2 (run r20261006-065529-46fc, fixture
  art:aa722185): Lean accepts the honest session and refuses four forged ones (fresh salts, the value committed afresh,
  a wrong position, a verifier holding no roots).
- The tensor table is in `one_stage/tensor_table.py` (`verity/tensor-table/v1`): W's rows in a committed tensor order,
  committed as registered rows under `verity/weights/domain/v1`. The table is hidden, with 52-word entries padded to a
  public `cap` and committed under `verity/tensor-table/domain/v1`, and W's domain binds the table's root. `check` is
  the reference for W1 to W4, the well-formedness that PoUS's setup and PoUW's epoch statement prove in gates.

## For other lanes

- Recursion (#1284, #1270): `rec_live.commit_rows` must hash with `registered.row_digest` (row/v2) instead of
  `sha512_row_digest(r, 16, ROLE_X)`, and #1270's `TOPS` becomes `"hm96-sha512/row/v2/node-row"`. I tested this by
  merging each branch with this one in a scratch worktree. Before the change, #1284 has 4 failures and 3 errors and #1270
  has 2 failures. After it, all non-slow `test_rec_*` tests pass: 44 on #1284 and 70 on #1270. Nothing else on those
  branches needs to change: `rec_outer`, `rec_residuals` and `rec_vstage` go through `registered`.
- `lean-agreement` lost its registered-reads replayable set. Set 16 was a v0 reads file over v1 rows, which this verifier
  refuses. Live set 6 (`"coins": "os"`) replaces it for manual `ci.py --live` runs. A replayable set again needs an
  upstream bundle holding a v2 registered statement. Upstream binary 967b8d06 also loses its only smoke session.
- Friction: `lean_changed.py --records` needs the `build` slot pool, which only node 2 has. A records job on node 1
  fails at once with "lists no pool 'build'".
