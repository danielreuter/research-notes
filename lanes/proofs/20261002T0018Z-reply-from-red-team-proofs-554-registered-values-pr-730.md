---
id: 20261002T0018Z-reply-from-red-team-proofs-554-registered-values-pr-730
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# #730 at `50fdfe55d` (registered values): GRANT for merge, not yet sound

Head reviewed: `50fdfe55de1b9b0bc4a260a59d9d7fb1832141d8` (still the branch head at 00:16 UTC). Evidence:
`art:041b5a32c32699224dfb30ad72c63551cf99f6047d1c283c7c3c7688c16bae64` (`findings.md`).

Labels: `grant red-team` and a `finding` on `pr:730@50fdfe55de1b9b0bc4a260a59d9d7fb1832141d8`.

The grant is for merging it as what PROTOCOL D5 says it is: a mechanism with no theorem and no corpus vector yet. Nothing
may cite it as sound until the items under "Missing before it is called sound" land.

## Binding

Binding holds under collision resistance of SHA-512:

- The verifier's domain, leaves and root are its own. They come through R7 (`registered_entries`, from its own program)
  and `reads_file`, and the domain binds the program, value, schema, words and leaves.
- The tree's framing binds each leaf's position and each node's depth and index, and pads are tagged, so no pad can be
  opened as a row.
- `Registered.check` holds each instance to the position the verifier's program reads for its unit,
  `own.reads[indices[i]]`. HmRow validates `indices` and `refs`, so the `getD` defaults can't be reached.
- The v2 registration digest covers the roots, and the draw comes after the receipt.

## Hiding

hm96 is statistically hiding given uniform secret 192-byte salts.

- Paths are functions of hiding leaves, and positions are public (from the program and the draw).
- Reusing a row across sessions reveals only that two sessions read the same public position.
- The header's new bytes (value, positions, paths) reveal nothing beyond that.
- Caveat: committing once makes every salt a long-lived secret. A single leak (M0's non-ZK witness, a prover file, a
  log) exposes that row for good, so "always hidden" needs C-Flock under `--zk`.
- Salt reuse is refused within one value only. OS salts make a collision across values negligible.
- The end-to-end run deletes the prover's file before custody, as it should.

## Fail-closed (the Lean check)

I read every refusal path, and each fails closed:

- a header entry with no reads file, or a reads file with no header entry;
- a port that is unknown, or that isn't a circuit input;
- a port in the reads file that the header leaves out;
- a value mismatch;
- positions or paths not one per table row;
- a position at or past `leaves`, or a path of the wrong length;
- the climb to `own.root`;
- the per-instance position.

`verify` and `statement` are the only commands that build statements, and both take `--registered`. The end-to-end
verdicts (`r20261001-230124-501a`, `art:f383334e`) agree: honest accepted; wrong reads, no reads file, and a plain
statement checked against registered reads refused.

## Findings (none blocks the merge)

1. **Positions are only as bound as the unit labels.** The end-to-end verdict says "units taken as stated, not derived",
   and neither `Registered.check` nor `audit_record` asks for derived units. In the full one-stage flow the draw and a
   population file covering every unit in order force the labels. Either refuse registered reads unless the units are
   derived or drawn, or say this in §16.10.
2. **"A value is committed once" depends on the caller.** R7-held runs only when the verifier passes
   `registered_roots`. `log` holds receipts (record digests), so nothing derives the held roots, and a later
   registration may carry a different root. Put `{value: root}` in the receipt and derive the held roots from `log`, or
   refuse a v2 record with a non-empty `log` and no `registered_roots`. This should land before any consumer relies on
   commit-once.
3. **`reads_file` trusts the registration.** It takes leaves and domain from the registration's entries, relying on R7
   having run. Taking them from `registered_entries` removes that dependence.
4. **Liveness: one reads file per circuit.** A reads file naming a port that a circuit lacks refuses that circuit's
   honest statements, so mixed populations need a file per circuit.
5. **`session_registered` isn't wired yet.** Nothing produces it from Lean VERDICT lines (only tests pass it), so v2
   audits fail closed until it is. It must come from the verifier of record's accepted verdicts, never from the
   registration.

## Missing before it is called sound

- **T1.** A level3 spec theorem: `Registered.check … = ok` implies each instance's `b‖c` climbs to `own.root` at
  `own.reads[indices[i]]`.
- **T2.** A path-binding lemma: two leaves at one position under one root give an explicit SHA-512 collision.
- **T3.** `Layout.regLeaf` instantiated for registered ports, so that `registered_weights_hm96` and the E2E theorem cover
  them.
- T1 to T3 pinned in `lean-audit.json`.
- **V.** D5 corpus vectors with `upstream_accepted`:
  - an honest registered session (both verifiers accept);
  - fresh salts on a registered port (upstream accepts, Lean refuses);
  - a wrong position;
  - a registered header checked without `--registered`.

  The end-to-end sessions `sessions/registered/l0000-2184772` and `plain/l0000-2187288` can seed them.
- A Lean test whose reads come from `reads()` on a real program, not the hand-written `READS`.
- After #723: take the registered values from `program.bindings`, and refuse a run parameter.
- Data-dependent reads remain out of scope, as the README says.
