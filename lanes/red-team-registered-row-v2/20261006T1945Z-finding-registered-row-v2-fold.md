---
id: red-team-registered-row-v2/20261006T1945Z-finding-registered-row-v2-fold
campaign: proofs
lane: red-team-registered-row-v2
kind: finding
status: final
repo: verity
origin: [pr:1320@4e71e8c9deb2384d0036fe66c93490f7b0a2d0b2, git:a9c858edb909c7b09dd30b0386bd9b683e51a8a7]
---

# red-team-registered-row-v2: #1320's fold over the rec and firewall-release trains (`a9c858edb`)

## Verdict: would grant

I would grant #1320's final head if it is `a9c858edb` plus only a merge of `main` that contains the rec and firewall
trains. There are no blocking findings. One line in the trial tree's `rec_vstage.py` union should be fixed before the
final head (F1, below). I wrote no label: the PR's head is still `4e71e8c9d`
(`note:red-team-registered-row-v2/20261006T1819Z-finding-registered-row-v2-b1`).

## 1. The three commits, against trial tree `ef30451a9`

`git diff ef30451a9 a9c858edb` touches 4 files, 13 lines added and 11 removed, all of them rows:
- **`4938eb20e`:** `rec_live.commit_rows` uses `registered.row_digest`, the `sha512/row/v2` digest of the bit row at
  `WORD_BITS`, which matches the rec reads' `word_bits: 16`. `commit_top` goes through `commit_rows`, so the salted tops are
  v2 too. Two module-docstring lines and `live/PROTOCOL.md`'s salted-roots row now say `row/v2`.
- **`2a7d96876`:** `rec_outer.stage` and `rec_residuals.statement` pass `port_bits=[16·w …]` and `v2_out_rows` (every
  output port). Neither statement has public inputs at the trial tree, and `test_rec_outer` and `test_rec_residuals`
  assert there is no `public-inputs.bin` and no `public_inputs` in META. So `port_bits` on every row is right.
- **`a9c858edb`:** `TOPS = "hm96-sha512/row/v2/node-row"`, with its comment and the `live/PROTOCOL.md` line that quotes it.

Nothing else changed. Nothing in the rec, firewall or release Python, or in flock-live's `firewall.rs`/`release.rs`,
still computes a v1 row digest. flock-live's `circuit.rs` handles every row schema, as a prover should.

The `rec_vstage.py` union in merge `b5008fb72` (#1347 into the fold, base `c8aa2cb5c`):
- The docstring union is right: #1315's `filler` bullet and `--cap` paragraph, plus #1347's `coef` and `dirs` bullets.
- `FORGERIES` is the union of both sides' entries.
- Every other change from each side is present. The one exception is F1.

**F1 (fix in the fold):** `VERIFIER_FILES` keeps `"public-inputs.bin"`. #1315 didn't touch that line; #1347 removed the
entry, because with `coef` and `dirs` registered no V* statement has a public input. The union reverts #1347's line.
- It breaks nothing today: `VERIFIER_FILES`' only reader, `_copy_verifier`, is never called on any head.
- But it disagrees with the correct resolution the trains will land, so the final merge of `main` could keep it, or
  conflict.
- Exact fix: take #1347's line,
  `VERIFIER_FILES = ("circuit.txt", "pub.bin", "program.json", "partition.json", "registered.json")`.

## 2. Nothing checks a record's `tops` name

The claim is true. The record's `"tops": TOPS` (public and private) is written by `rec_live` and read by no Python, Rust,
Lean or pod code. `node-row` occurs only in `rec_live.py` and `live/PROTOCOL.md`.

How it happened:
- `rec_vstar` checked the name in `root` and `caps` from `8c9a6631d` on: `public.get("tops") != RL.TOPS` was refused
  "the record's tops are not salted".
- Merge `a83c72890` ("Merge #1284 into cursor/zk-gateway-95d4", #1270's branch) kept rec-step3's rewritten `tops` and
  `opened_top`, and dropped the check. Its message doesn't mention the drop. #1320 didn't do it.

It is not a soundness regression:
- `opened_top` recomputes every top with `RL.commit_top` and refuses any mismatch, so a v1-salted record is still refused.
- `rec_inner.py forge --what unsalted` (clear tops, `pub["tops"]` deleted) is still refused, now as
  `FIREWALL-REFUSED: tree top: … does not open its commitment` instead of by name.

The firewall train (#1270) should take one of two fixes. I recommend (a):
- **(a)** Restore the two lines at the top of `rec_vstar.tops`. Then `TOPS`' v1-to-v2 bump refuses old records by name,
  and the `unsalted` control is refused by name, as `85-rec-reprice.sh` says.
- **(b)** Drop the claim from `live/PROTOCOL.md` (around line 634: "or when the record's tops are not salted", which also
  names `rec_vstar.root`/`caps`, both gone).

Not blocking for #1320.

## 3. The skipped Lean legs

Run `r20261006-192325-2321` on vy-nebius-1, at `a9c858edb` from my own clone (`--cwd clone`), `rc=0`:
- `flock-verify` was built from a warm copy under `lean_slot`.
- The store was reached through the run's custody key (`CHECK_STORE_CUSTODY`, with `VERITY_STORE_REQUIRED=1`), and
  `art:aa722185` was fetched on the node.

| Step | Passed | Skipped |
|---|---|---|
| Every `test_lean_*` module with store fixtures, plus `test_ci_fetch` | 77 | 2 |
| The author's targeted list | 443 | 7 |

`test_lean_registered_reads` passes, including live set 6's session test (`art:aa722185`). The targeted list is the
author's 432 passed plus the 11 store legs that skipped in their run.

All 9 remaining skips are opt-in flags, not store reach. I didn't run them: they're unrelated to the fold, and `check`
doesn't turn them on.
- `FLOCK_VERIFIER_SLOW`: `test_lean_zk.py:93` and `test_lean_session_tables.py:103`.
- `FLOCK_IR_SLOW`: 5 tests.
- `VERITY_FLOCK_INNER_FOLD`: 1 test.

## For the final head

If the final head is `a9c858edb` plus F1, plus only a merge of `main` holding both trains, I'd label it after checking that:
- the merge adds only `main`'s changes;
- `rec_vstage.py` comes out with #1347's `VERIFIER_FILES`.
