---
id: red-team-plain-leaves/20261006T0855Z-finding-pr1318-review
campaign: flock
lane: red-team-plain-leaves
kind: finding
status: final
repo: verity
origin: pr:1318@1b9bdd83c56db41dbb2a1c9ad1c122b6118c08b5
---

# red-team-plain-leaves: PR #1318 review (`verity/flock-circuit+plain-leaves`)

## Verdict: NO-GRANT

My verdict on PR #1318 at `1b9bdd83c56db41dbb2a1c9ad1c122b6118c08b5` (base `cursor/rec-step3-95d4` at `27301706`) is
NO-GRANT, on one blocking finding (B1). The engineering is otherwise correct:

- The statement's identity is upstream's, so Lean and upstream compute the same digest `59130006…`.
- The decoder accepts exactly an empty `opened_salts` per opening and nothing else.
- The `--zk` refusal is complete.
- The plain leaves are adequate for the inner proof.
- The `lean-audit.json` diff is exactly what `audit.py --update` wrote, and no guarantee changed.

B1 concerns the proof-coverage rule, not whether the construction is sound.

## Blocking finding

### B1: the compiled verifier gains a statement form ahead of its proof

**What.** `Tags.circuitPlainLeaves` is appended to `Tags.all`. Without `--zk`,
`flock-verify verify --statement verity/flock-circuit+plain-leaves` now accepts a session whose Ligerito trees have
`flock-leaf/sha512-unsalted` leaves, on an hm96-row statement with hidden outputs. Run `r20261006-070214-54f3` shows it:
its `honest` case returns `"accepted":true`. Before this PR, the same inner session was refused. The base's
`85-rec-reprice.sh` says so ("which Lean's tags refuse while they pin hm96 leaves"), and the `default` case of the same run
shows the refusal under `verity/flock-circuit`: "leaf-commitment scheme flock-leaf/sha512-unsalted is not one this verifier
implements".

**Why it blocks.** The first bullet of AGENTS.md's Lean section and Daniel's ruling of 2026-10-04 in
`.agents/skills/friction/SKILL.md` both say: "The verifier refuses any form the proof doesn't cover, and gains no new form
ahead of its proof." No soundness headline covers this form:

- The hidden-output headline chain requires `merkleLeaf = "hm96-sha512/v1"`. That hypothesis is in `TagsOk`
  (`DecodeZL/Statements.lean`), `AcceptsTablesHm96OfLeafAny` and `AcceptsVerdictHm96Any`
  (`HiddenExec/Statements.lean`), `setupHidden_hm96` and `setupOne_tagsAt_hm96`.
- The unsalted SHA-512 theorems, `verify_refines` (`Refine/Table.lean`) and `verify_refines_ofCircuit`
  (`Refine/Regions.lean`), are refinement steps for a one-table session. They are not soundness headlines, and they do not
  cover hidden outputs.
- #1179 ("C-Flock verifier fails closed", open draft, head `ca8e3a26c`) adds `Flock/ProvedScope.lean`. Its
  `statementRules` refuse every statement whose `merkleLeaf` is not `hm96-sha512/v1`, with the reason "a statement with
  {leaf} leaves". Once #1179 lands, this statement is refused anyway.

Landing #1318 first therefore widens the accepted set by a form the proof doesn't cover. Once #1179 lands, the PR body's
"Lean now accepts the session" and the new `85-rec-reprice.sh` comment both become false.

**Exact fix.** Pick one; I recommend (a), the smallest.

- **(a) Fail closed now.** In `FlockVerify.lean`'s `verifyCmd`, refuse `tags.plainLeaves` in every mode, not only under
  `--zk`, and return 2. Place the check after the existing argument checks. Use a message that names the reason, for
  example `refused: verity/flock-circuit+plain-leaves, a statement with flock-leaf/sha512-unsalted leaves: a form the
  soundness proof does not cover`.
  - Keep `Tags.withPlainLeaves`, the tag in `Tags.all` (so `flock-verify statement` still prints the identity and digest
    for agreement with upstream), `Setup.openedSalts`, the `saltLen` change in `verifyRep` and `shapeOf`, and the
    `lean-audit.json` records.
  - Change the slow test so `verify` exits 2 both with and without `--zk`.
  - Restore the base's wording in `85-rec-reprice.sh`: `INNER_LEAN=1`'s inner check is an expected refusal.
  - In PROTOCOL.md §16.15, the README line and the PR body, say that the verifier names and decodes the statement but
    refuses it until a headline covers it. Drop "Lean now accepts the session".
- **(b) Order after #1179.** Rebase onto #1179 once it lands, keep its `merkleLeaf == "hm96-sha512/v1"` rule unchanged, and
  make the same changes to the docs, the test and the script as in (a). The expected refusal is then ProvedScope's message.
- **(c) Prove the form.** Extend the hidden-output headline chain to plain leaves:
  - Widen the `merkleLeaf = "hm96-sha512/v1"` hypotheses of `TagsOk`, `AcceptsTablesHm96OfLeafAny`,
    `AcceptsVerdictHm96Any`, `setupHidden_hm96` and `setupOne_tagsAt_hm96` so they also admit `flock-leaf/sha512-unsalted`
    with `openedSalts`.
  - Two existing results help. `climb_binding` (`Verifier/Merkle.lean`) is already generic over any `Sized` scheme, and
    `Refine/Salted.lean` shows that hm96's node climb equals `MerkleScheme.sha512`'s.
  - Pin the new headline in `verity/Security/lean-audit.json` with a named statement reviewer, and add the form to #1179's
    `ProvedScope`.

  The verifier then gains the form together with its proof.
- **(d) Get an explicit exception** from Daniel through @proofs, recorded as a ruling in `.agents/skills/friction/SKILL.md`.
  Use this only if the recursive campaign needs Lean to accept the inner session before (c) is done.

## Answers to the review questions

### Q1. Identity: is `Tags.withPlainLeaves` upstream's `identity()`, and can Lean and upstream disagree?

Yes, it is upstream's identity, and I found no proof on which they can disagree.

`withPlainLeaves` makes the same two changes to the identity that upstream's `identity()` makes for a plain-leaf
statement:

- It sets `leaf_scheme` to the pinned object `leafSchemePlain`.
- It sets `hashes.merkle` to `"sha512 (every Ligerito level)"`. Upstream builds this string by appending
  `" (every Ligerito level)"` to `HashKind::Sha512`'s name, `"sha512"`.

Upstream writes the circuit file's own `leaf_scheme` into the identity. Lean compares the file's pinned leaf scheme with
`leafSchemePlain` canonically (`Flock/Circuit.lean`, the leaf id check and then the canonical JSON compare), and
`Flock/Canon.lean` refuses non-integer numbers. So any file Lean accepts has the same identity on both sides.

The run evidence agrees:

- `flock-verify statement` prints `statement_digest` `59130006…` in run `r20261006-070214-54f3`.
- The honest session's record carries the prover's Σ, which S4 compares against the statement's Σ. S2 compares the Hello.
  The honest session is accepted, so Σ and the digest agree with upstream's.

The accept sets also match:

- Leaf and node hash are SHA-512 with `merkle_hash` index 2.
- Digests are 64 bytes.
- The empty-salts rule is the same: the patch's `verify_level_opens` requires
  `salts.len() == if salted { queries.len() } else { 0 }`.

### Q2. Decoding: does `verifyRep` accept exactly the empty `opened_salts`?

Yes.

- **The new statement.** `Setup.openedSalts := st.tags.hm96Rows` together with `saltBytes = 0` gives `saltLen = some 0`.
  `decodeProof` then reads `vecExact 0 (Reader.bytes 0)` at each level, which accepts only a bincode `u64` length of 0. A
  non-empty vector, or any other length prefix, is rejected before any element is read.
- **Trailing bytes.** Bytes after the proof pair are ignored by design. This predates the PR (§8.1, the comment in
  `decodeProof`), and S17 binds the proof bytes to what the server received.
- **The older statements decode as before.**
  - hm96 statements (`saltBytes = 192`) still read `some 192`.
  - `631567f7` (unsalted, no hm96 rows, so `openedSalts = false`) still reads `none`, meaning no field.
  - Every other statement's `saltLen` is unchanged, because `openedSalts` changes the value only when `saltBytes = 0` and
    `hm96Rows` both hold. Of the statements in `Tags.all`, only the new one has both.
- **Construction.** `Setup.ofCircuit` is the only construction of a `Setup` from a statement, so no other path sets
  `openedSalts` differently.

The control run `r20261006-065052-f085` confirms the encoding against the prover's real proofs.

### Q3. Scope: who chooses the statement, and can a hiding path accept a plain-leaf proof?

The verifier chooses the statement, and no hiding path accepts a plain-leaf proof.

**The verifier chooses.** `verifyCmd` reads it from `--statement`, defaulting to `Tags.circuit`, and the prover's files
never select it. The callers name their own statements:

- `benchmarks/one_stage/a0.py` uses `STATEMENT_ID = "verity/flock-circuit"`.
- `85-rec-reprice.sh` runs the outer V* sessions with `verify --zk --statement verity/flock-circuit`, and the inner check
  with `--statement verity/flock-circuit+plain-leaves`.

**The `--zk` refusal is complete for this statement.**

- `verify` is the only command that takes `--zk` or verifies a session.
- The refusal comes right after the `--zk`/`--coins` check and before any input is read.
- Run `r20261006-070214-54f3` shows `zk exit 2` with the message.

**No hiding path accepts it.**

- A plain-leaf circuit file cannot pass setup under any hm96 statement. The leaf id must equal `tags.merkleLeaf`, and the
  pinned leaf scheme must match canonically. The run's `default` case shows this refusal.
- The one-stage audit names `verity/flock-circuit`.
- `rec_vstar` and the outer sessions verify under `--zk` against `verity/flock-circuit`.

**Pre-existing, non-blocking.** `--zk` refuses only `plainLeaves`, not `631567f7`'s older unsalted statement, which pins
the different object `leafSchemeSha512`. #1179's ProvedScope makes this moot.

### Q4. Soundness: are plain leaves adequate for the inner proof?

Yes, for binding and for the hiding that this session needs.

- **Binding.** A plain SHA-512 tree binds under `cr/sha-512` (`climb_binding` holds for any `Sized` scheme, and
  `MerkleScheme.sha512_sized` provides it).
- **Hiding.** The inner proof is V*'s private witness. The gateway (`rec_live`'s proxy) sends the coin server only salted
  tops (hm96 rows with fresh 192-byte salts) and the hiding commitments `c_k`. Σ and the statement digest stay hidden.
  Hiding is thus supplied by the gateway's salts and the outer ZK proof, so a leaf needs no salt of its own.

B1 is about the Lean proof's coverage, not about this argument.

### Q5. Lean records: is the `lean-audit.json` diff exactly `--update`'s, and are the theorems unchanged?

Yes on both counts.

- **The diff.** Run `r20261006-071311-b0d6` ran `audit.py --update` on `verity/Security`. Its output
  `security-lean-audit.json` is byte-identical to the PR's `verity/Security/lean-audit.json`.
- **What changed.** The 8 changed lines are the `reads` digests that 111 guarantees read:
  - in `Flock.Verify`: the module digest, `Flock.Setup`, `Setup.ofCircuit`, the new `Setup.openedSalts`,
    `instInhabitedSetup.default` and `verifyRep`;
  - in `Proofs.Flock.Soundness.Refine.Rep`: the module digest and `shapeOf`.

  No guarantee's type changed, and no guarantee reads `Tags.all` or `Tags.find?`.
- **The theorems keep their meaning.**
  - `shapeOf` gets the same `saltLen` expression as `verifyRep`, so `verify_refines`, `verify_refines_ofCircuit` and
    `zk_session_sound` still speak about the decoder `verifyRep` actually runs.
  - `shapeOf`'s value changes only when `saltBytes = 0` and `openedSalts` both hold. That never happens on the
    statements the headlines cover, so no theorem is weakened.
  - The ZkExec shapes (`VerdictStatements.lean`, `Statements.lean`) and `Zk.lean` keep the old expression. This is
    consistent, because `--zk` never reaches a plain-leaf statement.
- **The audits.**
  - `verity/Security` passed: 1747 guarantees, axioms `propext`, `Classical.choice` and `Quot.sound`.
  - `verity/Security/Proofs` failed only on the unrelated Warden `runs` check (`Proofs.Warden.DifftestMain`'s `generate`
    imported the run's source tree, not the checkout). Its axioms and replay passed.
  - `backends/flock/verifier/lean` at the PR head passed in run `r20261006-075425-d9b4`: 5562 declarations, the same three
    axioms, 7 guarantees.

  I did not run `#print axioms` separately. The audits check every declaration's axioms and replay it through the kernel.

### Q6. Tests and controls: do the five tests pin Lean against upstream, and do the negative controls hold?

The tests pin the source text, not the behavior. The PR body's run controls hold.

**The four fast tests pass:** `4 passed, 1 deselected in 0.25s` at the PR head. They match strings across the Lean
sources, upstream's Rust, the patch and the Python constants.

- Test 3 checks that `openedSalts := st.tags.hm96Rows` appears in `Verify.lean`, and that the patch's `opened_salts`
  comment appears in the patch. No test decodes a proof or computes a digest.
- My negative control put the base's `Verify.lean` into the PR's tree. Only test 3 failed
  (`test_a_plain_leaf_opening_carries_an_empty_salt_vector`), at the string assertion.
- The slow fifth test runs the binary, but only checks that `verify --zk` exits 2.

**The run controls in `r20261006-070214-54f3` hold:**

| Case | Result |
|---|---|
| `statement` | Exit 0, digest `59130006…` |
| `honest` | Accepted |
| `default` (under `verity/flock-circuit`) | Refused at setup |
| `zk` | Exit 2 |
| `tampered` (one byte of `circuit.rep0.bin` flipped) | Refused by S17 |

**Non-blocking suggestions:**

- Add one slow test that decodes a plain-leaf opening through `flock-verify`, both with an empty salt vector and with a
  one-element one. Add another that compares `flock-verify statement`'s digest with upstream's identity, or with the
  pinned `59130006…`.
- The run's script prints the statement digest but never compares it with the session's recorded `statement_digest`. S4
  covers this in the verifier, so the gap is in the evidence only.
- The tampered control is caught by S17 (proof bytes), so it never reaches the new Merkle and salt decode path. A control
  that re-encodes one opening with a 192-byte salt, with a matching server receipt, would reach it.

### Q7. Anything else wrong in the 9 files?

Nothing beyond B1 and the points under Q3 and Q6.

- PROTOCOL.md §16.15 and the README line describe the identity, the leaf scheme and the `--zk` refusal accurately.
- Under fix (a) or (b), both must also say that `verify` refuses the statement until a headline covers it.
- The `85-rec-reprice.sh` comment ("on Lean's plain-leaf statement") must then go back to describing a refusal.

## What I ran

| What | Run or source | Evidence |
|---|---|---|
| Honest, default, zk and tampered controls on the plain-leaf inner session (vy-nebius-1) | `r20261006-070214-54f3`, source `3da9a71a` | `art:89b0ed4e737c7cc72299b0dca07f1847b31ea7c7f787c2c9d1e0653e919336f2` |
| Encoding control | `r20261006-065052-f085`, source `8708c0ba` | `art:0a88deadf1c88a285f3f599d95d61cd219bf706dd9ef1cc4906d8e217c6d3fb7` |
| `audit.py --update` on `verity/Security` and `verity/Security/Proofs` | `r20261006-071311-b0d6`, source `5b54c900` | `art:bc08366e966024651fe887c0428ed0103aeb32ca18d87740226e85560602f6c7` |
| `audit.py --build` on `backends/flock/verifier/lean` at the PR head | `r20261006-075425-d9b4`, source `1b9bdd83` | `art:b6c4c75364bed45cda0a7ca9bd294709ed607b9bf53f6a306b176704e1040964` |
| The four fast tests, and the negative control with the base's `Verify.lean` | local, worktree `/tmp/rt1318` and a scratch worktree at the PR head | `/workspace/.venv/bin/python -m pytest -p no:cacheprovider` |
| #1179's `Flock/ProvedScope.lean` | read at `ca8e3a26cad79abb6b49c911f1cb57216a8253be` | — |

I compared `r20261006-071311-b0d6`'s `security-lean-audit.json` byte for byte with the PR's `lean-audit.json`. I read the
upstream sources `backends/flock/live/src/bin/flock-circuit.rs` and `flock-sha512-b684b12.patch` at the PR head.
