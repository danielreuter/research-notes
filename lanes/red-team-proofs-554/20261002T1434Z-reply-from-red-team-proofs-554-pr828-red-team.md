---
id: red-team-proofs-554/20261002T1434Z-reply-from-red-team-proofs-554-pr828-red-team
campaign: e2e-guarantees
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: red-team-proofs-554 (agent bc-d8964c29-a9c2-539a-8a10-812b9fcbc0c1; started by proofs bc-8416bc72)
---

# red-team-proofs-554 → proofs: #828 NO-GRANT at d5311b9f4

[#828](https://github.com/danielreuter/verity/pull/828) (`cursor/e2e-integrate-95d4` at
`d5311b9f43f3f9bf452c160c47811219daa44602`, the origin tip at 7:27 AM PDT): `flock_headline_exec`.

There is one blocking finding, B1: `hs : I.tags.sharedRows = false`, together with the headline's own Scope (OS coins
only), admits no M0 session. The fix is a one-hypothesis change (take `hpt : pub.tables = none` back), which needs a
statement re-review. The executable change refuses no M0 circuit, but it is stricter than upstream and PROTOCOL.md
doesn't name it (N1, non-blocking). The other hypotheses are satisfiable at an honest M0 RoPE session. The three
integration fixes are harmless. N2 is a merge collision with #757.

I worked read-only in a detached worktree at the head, with no build and no fetch. I refreshed the local store index
from the remote.

## B1 (blocking): `hs` and the Scope's OS coins exclude every M0 session

The chain:

1. The Scope paragraph (Headline.lean:97–98) says: "seed-derived coins are outside the headline, so an M0 session
   counts only under `FC_COINS=os`."
2. The untyped `verity/flock-circuit` tags with `sharedRows = false` are `circuitEb90718f`, `circuit` (e51e2b86's
   statement) and their `+seed-injection` forms.
   - Their identity is `identityHm96 _`, which names the round digest, statement digest and Σ as SHA-256.
   - Their `liveOs` is false, so under `--coins os` `Tags.withCoins` (Statement.lean:140) leaves the identity as it is.
3. Only the pinned M0 trees eb90718f and e51e2b86 write that identity, and both seed: `cfg.coin_seed = true` with no
   `FC_COINS` (e51e2b86's `flock-circuit.rs:126`, the same since 34c3d0815). Every M0 session such a tag accepts is
   seeded, which puts it outside the Scope.
4. Main's prover writes the SHA-512 text (`live/src/bin/flock-circuit.rs:206–207`), and under `FC_COINS=os` it writes
   the live-OS identity (from 804be92b4).
   - The statement digest hashes `canon tags.identity` (Statement.lean:196), so these sessions verify only at
     `verity/flock-circuit@967b8d06` (`identityHm96 false true`, `liveOs := true`).
   - That tag has `sharedRows := true` (Tags.lean:226), so `hs` is false there.
   - `test_lean_live_os.py:23` and lean-agreement's sets 14–15 verify at that tag.

So at an M0 session inside the Scope, `hs` fails. At a tag where `hs` holds, every M0 session is seeded and outside
the Scope.

The theorem is true, and its hypotheses can be met by some prover against `Tags.circuit` on OS coins. But it bounds a
verifier configuration that rejects every current M0 session. Several texts take M0's tag to be `Tags.circuit`, which
is e51e2b86's statement, so they are wrong for current M0:
- the PR body's "M0 is inside both";
- the docstring's "M0's `verity/flock-circuit` by `rfl`" (Headline.lean:81–82);
- `Layout/Tables.lean:10–13` and `Layout.lean:70`;
- the status file's `pub.tables = none` row.

The statement review's T2 rests on the same premise ("It is outside M0").

**Fix: take `hpt : pub.tables = none` back in place of `hs`.**
- `table_bcSite` and `sitesAt_bcSite` take exactly `hpt` (Sites.lean:273, 291). `Layout.loadPublic_tables hpub hs`
  still gives it at the old tags.
- M0 stages per-instance public files by default: `circuit.py`'s `write` and `stage` take `share_rows=False`, and only
  `class_statement.py` sets it.
- At `@967b8d06` a file without a `shared_rows` header loads with `tables = none`. `HmRow.sharedRows` returns none
  without the header, and `vectors.json` has the case: "set 14's instances without shared_rows: the file reads as
  before, under the 967b8d06 statement name".
- Nothing else in the composition reads the tag. `Exec.Inputs` and `tagsAt` don't pin it, and e2e-exec's tag facts
  are already stated at `@967b8d06` too (`retainRounds_circuit967b8d06`, `merkleLeaf_circuit967b8d06`).
- The fix changes the records of `Integrate.flock_headline_exec` and `Integrate.rsAt_computes`, the two pins that
  take `hs`, so it needs a statement re-review. Correct the texts listed above in the same change.

The alternative is to land as is, keep `hs`, and say that the headline covers no current M0 session until `hpt`
returns. I don't recommend it, because the PR's point is the M0 headline.

## Q1: `HmNets.check` refuses no M0 circuit; stricter than upstream and unnamed (N1, non-blocking)

**It refuses no M0 circuit.**
- The check compares the file's `sha512x3` and `hm96` nets with the verifier's constants (`HmNets.sha512x3Net` and
  `hm96Net`, which take no arguments).
- Every composer emits those same two nets, built from `S.compression3()` and `S.hm96_row()` with no key:
  `circuit.py:420–421`, `class_statement.py:278–279` and `typed_statement.py:384`. No caller passes `hm96_row` a key.
- Pre-main check `r20261002-112059-6065` at 736bcd615 already had the check (HmRow.lean:459 then, :548 now; HmNets.lean
  is unchanged since). Its lean-agreement accepted honest sessions of RoPE (sets 8, 10–12, 14–15), RMSNorm (set 9) and
  GEMM k1024 (set 13), and `backends_flock` had 0 failures.
- The head check `r20261002-130723-16b5` was not in the store at 7:32 AM PDT, after a refresh. Main's bit-row test
  goes through the check only there.

**It is stricter than upstream.**
- Rust (`live/src/circuit.rs:753–763`) checks the per-VU counts and the two nets' port widths, never their rows.
- So a file whose `sha512x3` or `hm96` net has the right ports but other gates is accepted upstream and refused by
  Lean. That direction is safe for soundness, since the verifier of record refuses more.
- `verifier/PROTOCOL.md` doesn't name the divergence. §16.10 "Slots" only says both nets are `CIRCUIT` sections with
  those ports. §17.1 lists D1–D5 and then says "Everywhere else the spec follows upstream".
- Follow-up, docs only: a D6 in §17.1, for example "the verifier refuses a `sha512x3` or `hm96` net that is not its
  own (`Flock.HmNets.check`); upstream checks their ports only".
- A completeness note for later: an `hm96` net built from a keyed `hm96_row(key)` would be refused.

## Q2: the other hypotheses are not empty at an honest M0 RoPE session

- **`DrawSetup`.** At every accepted draw, `drawSetup_of_accepts` (Accepted.lean:124) builds one from flock-verify's
  acceptance, for sessions of one table, given that the draw proves `S` and that `st.mPts = mPts`. The pieces come from:
  - `g_pos`: `HmRow.check`'s unit range;
  - the block bound: setupH's `nbl`;
  - `hsch` and `hm`: the verifier's own schedule. `fast100` exists only for 22 ≤ m ≤ 35, in both the executable and
    `Accounting.fast100`, and then has ≥ 3 levels (`fast100_two`).

  `x₀` needs one such draw.
- **`tableAt`'s refused table.** It is chosen only at a draw with no `DrawSetup`, and it enters only through `Sat`
  (`tableAt_unsat`, the second branch of `sitesAt_bcSite`). At an accepted draw a `DrawSetup` exists, provided the
  `mPts` condition holds. So the refused table can make `hdec` fail, but it cannot silently empty the theorem.
- **`mPts`.** It is one value for every draw. `mPts := mPtsOf c.g (∑ k)` is right at every draw of a successful run
  (`setupH_mPts_execOS`). The all-units fallback (a run that reads past the source's bytes) sets up at
  `mPtsOf c.g n`, and `hdec` fails there unless the two `log2ceil`s agree. The status file's Finding states this
  correctly; it sits inside the open `hdec` and does not block.
- **`hscope`.** It is true on M0's RoPE d64 (e2e-layout's `#eval`, with `v1Ports`). RMSNorm and GEMM fail it, and the
  Scope names them as outside.
- **`ht`, `hc`, `hpub`.** They hold at an honest untyped session of one table.

## Q3: the three integration fixes are harmless

- **`Exec/Merkle.lean` (09c94c633).** Two proof lines: one more `except_bind_ok` in `parse_leafScheme_pre` and in
  `parse_leafScheme_tmpl` steps over the `HmNets.check` bind and discards its result. No statement changes.
- **`Hm/Exec.lean` (a38a7f0ec).** One import (`FlockLevel3.LookupRows`) with a comment. No declaration changes. The
  replay limitation behind it is `tools/lean`'s, as the status file's Finding says.
- **`Aliased/Keys.lean` (7bf7cbf96).**
  - The texts of `srcAt_leaf` and `srcKey_leaf` hash equal to e2e-zero's 8752529f1.
  - `srcAt` and `srcKey` hash equal at 8752529f1, main d2b4a6d83 and the head.
  - `srcKey_leaf`'s pin is identical to 8752529f1's record.
  - From main to the head, `lean-audit.json` adds 173 pins, removes none and changes no existing record.

## N2: coordination with #757

At #757's tip 9d79e54ae, `Tags.circuit` is `{ circuit967b8d06 with … hiddenOutputs := true }` (Tags.lean:264–265), and
`setupH` sends it to `setupHidden` (HmRow.lean:1413). Whichever of #828 and #757 lands second faces two problems:
- `Layout.circuit_sharedRows` (pinned, proved by `rfl`) stops building;
- at the default statement, `flock_headline_exec` goes through `setupHidden`, which this composition doesn't cover.

With `hpt` in place of `hs`, only the `setupHidden` half remains.

## Done

- No label: the verdict is NO-GRANT at d5311b9f4.
- I created this note. I removed the worktree `/tmp/review-828` and my scratch directory `/tmp/r554-811/`.
