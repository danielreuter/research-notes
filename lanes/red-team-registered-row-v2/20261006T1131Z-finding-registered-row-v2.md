---
id: red-team-registered-row-v2/20261006T1131Z-finding-registered-row-v2
campaign: proofs
lane: red-team-registered-row-v2
kind: finding
status: final
repo: verity
origin: [pr:1320@fd9720b6d9e87d34f65542a6e00853ed1d7a5e9d]
---

# red-team-registered-row-v2: PR #1320 (registered rows as `hm96-sha512/row/v2`, the tensor table)

## Verdict: NO-GRANT

My verdict on #1320 at `fd9720b6` (base `main`) is NO-GRANT, on one blocking finding (B1) plus one wrong claim in the
body that must be corrected (B2). No label is written.

The audit is `r20261006-100637-961f` on vy-nebius-1 (`lean_audit.py --fresh`, replay on; run record
`art:7c2a0457`). It **passed**: 0 of 3 packages reused, 0 failures in compare mode, and axioms propext, choice and
Quot.sound only.

| Package | Declarations | Modules | Guarantees |
|---|---|---|---|
| Security | 6,873 | 217 | 1,748 |
| Proofs | 57,514 | 877 | 0 |
| flock verifier | 5,556 | 47 | 7 |

It ran on node 1 because the proofs coordinator cancelled the node 2 re-run `r20261006-092601-1124` for memory accounting's
quiet window. The first run, `r20261006-085115-7e91`, failed for infrastructure: verity/Security's Mathlib clone from
GitHub was reset (curl 56).

The full review, with the probes and their logs, is at `private/red-team-reviews/1320/review.md` in the coordinator's store.

## B1 (blocking): the ZkReg registered-session guarantees are vacuous at the head

The five guarantees are `zk_session_soundR`, `…HR`, `…HJR`, `…HR_custody` and `…HJR_custody`.

- The new `Port.fits` requires `q.v2`.
- Every one of the five takes `hscope : Layout.scopeOk c`, whose `v1Ports` requires `!p.v2` on every port.
- `checked_of_accepts` gives `st.c = c`.

So `AcceptsZKR` is false for every non-empty `own`, and `Registered.ofJson` refuses an empty port list. I proved
`Registered.check c pub (some own) _ ≠ .ok ()` under `∀ q ∈ c.ports, q.v2 = false` and `0 < own.size` at the head,
kernel-checked with axioms propext/choice/Quot.sound only. Before the PR the five were non-vacuous for v1 registered
sessions (set 16).

The build and the audit stay green, and the body doesn't mention scope. The guarantees are cited by
`note:proofs/20261006T0255Z-draft-proof-service-interface` and APPROACHES `flock/registered-reads`, and the rec-thm branch's
`hscope` theorems inherit the vacuity.

The fix is one of:
- (a) extend `scopeOk` and the shadow layout to v2 non-segmented rows, re-prove the five, and check non-vacuity;
- (b) re-scope the five explicitly and withdraw the citations until (a) lands.

## B2 (correct the body): the #1284/#1270 restack needs more than `commit_rows` and `TOPS`

Their `rec_outer`/`rec_residuals` compose the registered ports `out`, `acc`, `acc_out` and `m0` as v1 rows (no
`port_bits` or `v2_out_rows`), and #1320's composer guard refuses them. On each branch merged with #1320 plus exactly the
listed changes, the slow registered tests fail with `registered port out: a hm96-sha512/row/v1 row of 1024 bits, …`. On
each branch alone they pass. `check` runs slow tests, so this isn't silent, but the plan is wrong.

## Passing items, one line each

- Item 1 records: the diff of `verity/Security/lean-audit.json` (head against merge base, and merged tree against
  `origin/main`) is exactly `check_ok`; `Port`, `Port.fits`, `Port.words`, `checkPort`, `rowLeaf` and `leafIn` changed;
  `rowWords` gone; `schemaOf` new.
- Item 2: `check_ok` and `checkPort_ok` are stronger (the v2 shape is stated, `words` is mandatory). `rowLeaf`/`leafIn`
  match Python's leaf. The E2E `*_hm96_reads` theorems are unaffected. The ZkReg theorems lose all content (B1).
- Item 3: Python commits and Lean opens agree on 30 cases (16- and 32-bit words; 5, 3, 1, 7 and 33 leaves). A flipped
  bit, `words`, `word_bits`, the salt or the position each refuses. 32x1 read as 16x2: `fits` true, `opens` false.
  `verity_pouw.circuit.leaves.row_digest("bf16", ROLE_W, ·)` and `leaves.commit` equal the registered ones.
- Item 4: live set 6 (`art:aa722185`) gives 5/5 agree and 1 accepted, and the four forgeries are refused for the stated
  reasons. `upstream_accepted` is D5. `"coins": "os"` is set 6's alone and touches no registered check.
- Item 5: the tensor table's `check` refuses every tiling attack at `min_row_bits = 8`, and `byte_rows` matches a brute
  force (at most 2 rows holds). Non-blocking:
  - `min_row_bits = 0` admits zero-width tensors, and `byte_rows` then divides by zero;
  - duplicate names pass;
  - the "hides every tensor's shape" docstring overclaims for one tensor;
  - the gates must not wrap mod 2^64.
- Item 6 (set 16, `art:bf70d8eb`): the Lean registered path is still in `check` (`test_lean_registered_reads`, its rope
  fixture on `art:aa722185`). Lost: upstream's agreement leg on a registered session, and `upstream_smoke`'s replay for
  binary `967b8d06` (now 4 of 8 binaries smoked). Non-blocking.
- Item 7: `merge-tree` onto `origin/main` is clean. #1284's `flock-circuit.rs` conflict comes from `main`, not this PR.
  No Definition, template or lowering changed, and the `circuit.py` change is only `write`'s registered-port guard.
