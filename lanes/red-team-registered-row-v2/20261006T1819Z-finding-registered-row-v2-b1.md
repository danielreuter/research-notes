---
id: red-team-registered-row-v2/20261006T1819Z-finding-registered-row-v2-b1
campaign: proofs
lane: red-team-registered-row-v2
kind: finding
status: final
repo: verity
origin: [pr:1320@4e71e8c9deb2384d0036fe66c93490f7b0a2d0b2]
---

# red-team-registered-row-v2: PR #1320 re-review at `4e71e8c9d` (B1 answered)

## Verdict: GRANT

#1320 at `4e71e8c9d` answers my NO-GRANT at `fd9720b6`
(`note:red-team-registered-row-v2/20261006T1131Z-finding-registered-row-v2`):
- B1: the five registered `--zk` guarantees are restated over `sha512/row/v2` rows, and nothing in them is vacuous any more.
- B2: the restack plan for #1284 and #1270 is now complete.

There are no blocking findings, and two non-blocking notes follow.

## The audit

The author's replay audit is `r20261006-163809-de0f` on vy-nebius-1. Its source tree is exactly
`4e71e8c9deb2384d0036fe66c93490f7b0a2d0b2`, and it exited `rc=0`. It used a private, empty verdict cache, and replay was on.

| Package | Result | Declarations | Modules | Guarantees |
|---|---|---|---|---|
| verity/Security | PASS | 6,873 | 217 | 1,683 |
| verity/Security/Proofs | PASS | 57,736 | 890 | 0 |

Both packages use only the axioms propext, Classical.choice and Quot.sound, and the overall line reads `AUDIT: PASS`. I
didn't rerun it.

## B1: the five restatements

I diffed the recorded signatures in `verity/Security/lean-audit.json`, `5e7dd33dc` against `4e71e8c9d`.

The five guarantees are `zk_session_soundR`, `…HR`, `…HR_custody`, `…HJR` and `…HJR_custody`. In each, the only lines
that changed are:
- the scope hypothesis: `Layout.scopeOk` becomes `ZkRegV2.scopeOkV2` (for R) or `scopeOkHV2` (for the H and HJ forms);
- the rows and layout: `rsZAtS` and `rowsSh` become their V2 forms; `rsZHS` and `rsShHS` do too; `ZkHidden.layShH` becomes
  `ZkReg.layShHV2`; and the HJ equivalents follow the same pattern.

Owners, assumptions and line counts are unchanged.

The rest of the lock:
- Guarantees: 5 changed, 7 new (the pins), none gone.
- Definition records: 32 new, 6 gone (`rowsSh`, `rsZAtS`, `rsZHS`, `rsShHS`, `rsZHJS`, `rsShHJS`), 0 changed.
- So no other guarantee's record moved. `Flock.Circuit`'s module digest moved only because `Flock.Port.nb` is now
  recorded; the verifier source is untouched.

The V2 rows encode the verifier's own prefix: `Hm.preV2 w = HmRow.rowPrefixV2 (16·w)`. Their `Computes` fact is
`keyedRowsOutsV2_computes`, proved against the parsed circuit. `layShHV2` and `layShHJV2` are the v1 layouts'
constructions (`keyLayoutHV2` over the same `keyProg` partition, plan and tables).

## B1: non-vacuity

`check_refuses_scopeOk` states exactly what made v1 vacuous: at a `Layout.scopeOk` circuit, `Registered.check` refuses
every non-empty `own`. It is my phase-1 probe, now pinned.

The circuit-level pins (`registered_v2_nonvacuous`, `…H`, `witness`, `witnessH`) show three things at one circuit:
`scopeOkV2` (or `scopeOkHV2`) holds, `scopeOk` fails, and the registered check's port test holds (name and `Port.fits`).

Their gap, which the body states, is that they are about `v2Rows c` and hand-built witnesses, not a parsed circuit with
`Registered.check = ok`. I checked by hand that nothing else conflicts:
- **The parser:** an unsegmented v2 row of \(l = 1024k\) bits parses to `words` \(= 64k\) and `chunks` \(= k\), with
  `segs` none. So `2·words = 128·chunks` and `bits = 16·words` both hold, and a parsed whole-block v2 port is `v2Row` of
  its v1 port.
- **`Registered.check`:** it reads only the header names, `derived`, `pub.tables`, the port by name, `fits` and the
  openings. None of these touch the unit or `chunks`.
- **`AcceptsZKR`'s other parts:** `Zk.shapeOk` reads only the mask slot. `HmLinks`' v1-only rule applies only to
  statements with `links`.
- **The composer:** in v2 mode it pads each `out_row` to whole blocks and writes no `out_row_ports`, so `outRowPorts` is
  one port per output row.
- **A live session:** the Lean verifier accepts `art:aa722185`'s honest registered session (`test_lean_registered_reads`),
  a hidden-output RoPE circuit with 1,024-bit v2 rows. It is verified without `--zk`, so it doesn't meet `AcceptsZKR`
  itself; but by the points above, a `--zk` session over such a circuit meets no new obstruction.

## B2 and scope

The followers' plan matches what I found at `fd9720b6`. Both #1284 and #1270 need:
- `rec_live.commit_rows` using `registered.row_digest`;
- `rec_outer.stage` and `rec_residuals.statement` passing `port_bits` (`16·words` for each input row, `None` for public
  inputs) and `v2_out_rows` (every output port).

#1270 also needs `TOPS = "hm96-sha512/row/v2/node-row"`, with its comment and the `live/PROTOCOL.md` line. The author
reports 66 passed and 1 skipped on #1284's merged tree, and 89 passed on #1270's. I didn't touch either branch.

Scope:
- `git diff --name-only 5e7dd33dc 4e71e8c9d` is 17 Lean files under `Discharge/ZkReg{,V2}` plus `lean-audit.json`.
- `git merge-tree --write-tree origin/main 4e71e8c9d` (main at `cb50af5e8`) is clean.
- The merged lock is exactly `main`'s lock plus this PR's delta. On the two module `guarantees` lists both sides touched
  (`Flock.HmNets` and `Flock.Field`), it holds both sides' additions, sorted and without duplicates.

## Non-blocking

- **N1:** the non-vacuity pins stop short of a parsed circuit. An optional strengthening is a test that `scopeOkHV2`
  holds of `art:aa722185`'s parsed circuit, or a `--zk` registered fixture.
- **N2, for the followers:** `v2_out_rows` rows are exact-width, and `scopeOkV2` and `scopeOkHV2` need whole SHA-512
  blocks. So rec-thm's `hscope` theorems, when moved to `scopeOkV2` or `scopeOkHV2`, cover a follower statement only if
  every row is a multiple of 64 words: the fresh-salted `row` and `aux` rows and every output, not just the registered
  1,024- and 2,048-bit `out`, `acc`, `acc_out` and `m0`.
