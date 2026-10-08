---
id: red-team-vbridge-c/20261008T0624Z-finding-vbridge-restack-regrant
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: verity
origin: [pr:1428@7d6f82b50cd94be892ce6a360a5001d239d4becd, pr:1391@2ade21342c235ba9a54ac6b8db936c2030de5ea4, pr:1419@7d0adc62547eb1363bf989fb315f3bab418bfaa5]
---

# Red team regrant of #1428, #1391 and #1419 across main's two moves: grant #1428 at H1 and #1391 at H2'; #1419's code holds

Addendum to `note:red-team-vbridge-c/20261007T0226Z-finding-pr1391-1419-1428-review`, which granted the old heads
(`1ce9a45cc`, `f76770e48`, `2a0dc5910`). The restack (`tools/move/restack.py` over `c8cfc5650`'s `layout.py` and
`18b6cf4a0`'s `rename.py`) carried all three PRs' code unchanged. The only differences from the old patches are in the
locks, and they are the ones the coordinator decided.

- **#1428 at H1 `7d6f82b50`: grant.**
- **#1391 at H2' `2ade21342`: grant.** H2' is H2 `3f26ba878` plus the `check_ok` delisting.
- **#1419 at H3 `7d0adc625`:** the code holds; it gets its grant on H3' after the re-record. Nothing blocks.

## Method

For each PR I compared the old patch, with its paths mapped, against the new per-PR diff, comparing the added and removed
lines file by file. The mapping is `backends/flock/verifier/lean/` → `verity/core/service/flock/`, `backends/flock/` →
`verity/ml/flock/` and `verity/Security/` → `Security/`. The pairs were:
- #1428: old `e7b5caa89..1ce9a45cc`, new main `93b5e95a9..H1`;
- #1391: old `e7b5caa89..f76770e48`, new `H1..H2`;
- #1419: old `f76770e48..2a0dc5910`, new `H2..H3`.

**Every code file is byte-identical** in its added and removed lines:
- #1428: `HmRow.lean`, `test_lean_verifier.py` and `PROTOCOL.md`.
- #1391: `RecOpen.lean` (339 lines), `Flock.lean`, `HmRow.lean`, the six proof files, the test and `PROTOCOL.md`.
- #1419: `VBridge/Verifier.lean` (363 lines) and the import line in `VBridge.lean`.

No per-PR diff touches any other file.

I also checked that identical bytes are right after the move:
- No added line names a retired path or module, such as `backends/`, `verity/Security`, `Specs` or
  `Proofs.Flock.Soundness.Randomness`.
- The names the added lines import exist in the new tree under those names. Main's own `test_lean_verifier.py` still
  imports `verity_flock` and `verity_numerical`.
- Both codemods leave the PRs' files alone at H3. `rename.py --dry-run` rewrites 0 files.
  `layout.py --dry-run --report-splits` rewrites 4 files, all main's leftovers: the friction skill, `pod_bootstrap.sh`
  and `test_doc_paths.py`.

## #1428 at H1: grant

- **Code.** Unchanged, as described.
- **Lock.** Both of H1's locks are byte-identical to main's; the old patch's re-record of `Flock.HmRow` is dropped.
  - This matches "the head below's plus only the entries the PR added": #1428 lists no guarantee.
  - Main's reduced Security lock still has a `Flock.HmRow` reads group, so it doesn't yet record #1428's `parse`,
    `MAX_K_LOG` and `kLogOf`. H1 alone would fail an audit's lock comparison. That's fine under the plan: there is one
    re-record at #1419's head, and the three land as one tip.
- **Accepting paths.** My Oct 7 analysis carries unchanged:
  - Main's `HmRow.lean` is byte-identical to the old base's.
  - Main's verifier changes add no caller of `HmRow.parse`, `HmOut.parse`, `parseTyped` or `setupH`. The firewall
    (`Flock/Firewall*`, `flock-firewall`) mentions `HmRow` only in a doc comment.
  - `FlockVerify` only gains a refusal, for plain-leaf statements.

## #1391 at H2 / H2': grant at H2' `2ade21342`

- **Code.** Unchanged, as described.
- **The combined `HmRow.parse`.** H2's `HmRow.lean` equals the clean three-way merge of the two old heads
  (`git merge-file`, base `e7b5caa89`).
  - Order: `kLog := ← kLogOf mj` as `c` is built, then `check c tags leafScheme`, then `HmNets.check c`, then
    `RecOpen.check c`, then `return c`. Both refusals are there, and `setupH`'s own `k_log > 27` refusal is untouched.
  - The header cap still bounds what `RecOpen.check` sees. `RecOpen.check` reads only the circuit's name and its unit
    (`check_congr`). `check` runs first, and it gives the unit net exactly one range with
    `unitLog = slot_log ≤ k_log ≤ 27`. So the unit has at most 2^27 rows and at most 2^27 input bits, and the bit cap
    then allows `unitNet L H` only for `384·L + 2048 + 1024·⌈H/2⌉ ≤ 2^27`, that is `L` below 349,526.
- **Lock.**
  - H2's Security lock equals H1's. Its verifier lock is H1's plus `Flock.RecOpen.check_ok`, a record byte-identical to
    the old one.
  - **H2' `2ade21342`** is one commit on `3f26ba878` ("delist Flock.RecOpen.check_ok") that removes exactly that record.
    Its verifier lock is byte-identical to H1's and main's.
  - Nothing outside Lean names `check_ok`, so delisting it fits #1170's rule.
- **GitHub.** At 06:23Z #1391's head was still `cursor/vbridge-net-check-95d4` at `3f26ba878`. The `-95d4` mirror has to
  follow `-5a30` to `2ade21342`.

## #1419 at H3: the code holds; no grant until H3'

- **Code.** Unchanged, as described.
- **The import.** `VBridge.lean` imports both `VBridge.Verifier` and main's `VBridge.OfVStar`.
- **No name collides or resolves to the wrong declaration.**
  - I extracted declarations: `Verifier` has 54, all in `FlockVBridge`; `OfVStar` has 59, all in
    `FlockVBridge.OfVStar`. They share 25 short names (`recOpen_eq`, `shaFrom_eq`, `residualForms_eq`, …) and no full
    name.
  - Neither module imports the other, and only the umbrella `VBridge.lean`, which declares nothing, imports both. The
    only module above it is `Proofs/Flock.lean`, also imports only.
  - No module opens `FlockVBridge.OfVStar`. `Verifier`'s transitive closure (213 modules) doesn't contain `OfVStar`, so
    every short name in `Verifier` resolves as it did.
- **Main's changes inside `Verifier`'s closure.** They are `Soundness/Assumptions.lean` (an import path), `Refine/Rep.lean`
  and `Flock/Verify.lean` (`openedSalts`), and `Flock/Tags.lean` (the plain-leaf tag set). `Verifier.lean` reads none of
  them: no `Setup`, `saltLen`, `Tags` or `verifyRep`. Whether the combined tree builds is the re-record run's to show
  (`r20261008-055539-db9c`).
- **Lock.** H3's Security lock is H2's plus G's six `FlockVBridge` records, each byte-identical to the old ones. Reads
  groups and reader lists are left to the re-record.

## Tests

The touched tests (`test_hm96_header_sizes_are_refused_before_their_powers` and
`test_rec_open_unit_of_other_bits_is_refused_before_its_net_is_built`) need a Lean build, and Lean doesn't build on
this VM. The tip's full check with `--agreement` runs them. On H3 I ran:
- `py_compile` on the test file: it compiles;
- `tests/test_repository.py`, `test_lean_packages.py` and `test_no_wall_clock.py`: 29 passed;
- `test_doc_paths.py`, `test_module_strings.py` and `test_gate_paths.py` with H3's own `tools/research/src` on
  `PYTHONPATH`: all pass, the same as main.

With the VM's venv, four `test_gate_paths` tests fail identically on main and on H3. The venv imports `research` from
`/workspace`'s checkout, which predates the move.

## Non-blocking

- H1 and H2' carry stale `Flock.HmRow` reads (and H2' lacks a `Flock.RecOpen` group) until the tip's re-record. That is
  intended.
- `layout.py --dry-run` on post-move main fails on its own stale `[split]` acknowledgements unless given
  `--report-splits`. That is main's issue, not these PRs'.
