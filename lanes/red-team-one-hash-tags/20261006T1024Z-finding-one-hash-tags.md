---
id: red-team-one-hash-tags/20261006T1024Z-finding-one-hash-tags
campaign: proofs
lane: red-team-one-hash-tags
kind: finding
status: final
repo: verity
origin: [pr:1331@00b6e793a4ef12c84f1696b70bbffdde10c44563]
---

# Red team, PR #1331 (M0's and the served frame domains bind 64-byte SHA-512 identities): GRANT

Reviewed 3:24 AM PDT, 6 Oct, by red-team-one-hash-tags for the proofs coordinator. I reviewed head
`00b6e793a4ef12c84f1696b70bbffdde10c44563` of `cursor/one-hash-binding-tags-95d4`, stacked on #1325
(`cursor/one-hash-binding64-95d4` at `8b29df794`), in a separate worktree. The posted body is the author's claim, and it
matches `internal/proofs/one-hash-pr5.md`. Context: note:one-hash/20261006T0706Z-finding-one-hash-inventory and item P6
of note:verity-root/20261006T0550Z-report-proof-service-implementation. The probe scripts and the item 1 detail are in
the Project store's `private/red-team-reviews/1331/`.

**Verdict: GRANT.** I found nothing blocking. There are three non-blocking notes (N1 to N3), and the author can take them
in this PR or a later one.

## What I ran

All runs were on my VM, with no Lean and no `research run`. Imports were pinned to the worktree with `PYTHONPATH`, and
pytest ran without xdist.

- At the head:
  - sampled proofs: 69 passed, including `test_registered.py` at 16 passed;
  - `verity/protocols`: 248 passed;
  - the repository suite: 45 passed;
  - vLLM's `test_serving_rows.py` and `test_row_group.py`: 24 passed and 1 skipped (`cryptography` isn't installed);
  - flock's `test_circuit.py` and `test_class_statement.py`: 44 passed;
  - flock's `test_typed_statement.py`, `test_stage_typed.py`, `test_registered_rows.py`, `test_circuit_types.py` and
    `test_pouw_rows.py`: 87 passed.
- On #1320 merged in (`git archive` of the merge tree): sampled proofs plus protocols 331 passed, vLLM 24 passed and 1
  skipped, `test_circuit.py` 24 passed. These match the body.
- The body's negative control reproduces: 5 failures. The three flock failures are `AttributeError` (the base has no
  `FC.BINDING_TAG`), so the mutation check is what shows the test reads the binding's value. The second commit's control
  reproduces: the first commit's `registered.py` fails the 16-bit and 32-bit pinned-root tests. The mutation check
  reproduces: a 32-byte digest under v2 fails `test_rope_composes_private_by_default` on the binding's value.

## Items

1. **What the bindings protect: unchanged by this PR.** A domain id is SHA-512 over a length-framed message of the
   binding, owner + 2, the positions' SHA-512 identity and the count (#1325's `CommitmentDomain`, `hash="sha512"`).
   Lean's `HmRow.checkPublic` and Rust's `frame_roots` take `frame_v3.domain_ids` as given, and neither reads
   `bindings`, as the body says. The only place that derives domain ids is one-stage: R3 holds the registration to the
   verifier's own derivation (a0's `stand_in_ports`, a2's `served_domain`), and `matches_public` holds the public file to
   the registration. Without those checks, a domain id doesn't tie a root to its set or range. The PR adds and removes no
   check, and the body claims none, so this is not blocking.
2. **Domain separation holds.** `identity_digest_sha512` is SHA-512 of `verity/tagged-sha512/v1\0`, then the tag with a
   u32be length, then the canonical JSON with a u64be length. Both new tag strings first appear in this PR, and each has
   one definition. `OWNER = -1` is the value M0 borrowed from `ir_frame.OWNER`; served also uses -1 and registered uses
   -2. The owner isn't what separates domains: the tag is. M0 binds `{set, lo, hi, port, schema}`, the same five fields
   its base bound under `ir_frame.BINDING_TAG`, and the served domain keeps its six fields. Nothing is dropped. Legacy
   `ir_frame` and `ir_sampling` also bind `content_digest`, which base M0 had already left out for hidden outputs. So the
   base's v1 tag had two document shapes, and M0's own v2 tag ends that for new statements.
3. **Both sides agree.** A probe over 2,592 inputs gives byte-identical domains from `served_domain` and
   `Window.domain`, all distinct. I drifted one side at a time: the tag, the owner or the width on the one-stage side,
   and the tag, the owner or the `run` field on the vLLM side. All six fail the vLLM test. Each one-stage-side drift fails
   on the new `R.served_domain` line, so that line carries the check.
4. **`--binding` can't weaken a verifier.** Only `a0.py` and `a3.py` read it; a2 (the served path), `registration`,
   Lean and Rust don't. Its default is v2 in both, and its choices are two fixed tag and hash pairs. I staged real M0 at
   the head and at the base: a0's derivation matches the header only under that tree's tag, and the cross pairs match no
   port, so a wrong tag is refused at registration.
5. **No tag has two meanings.** `git merge-tree` of the head with #1320 (`fd9720b6d`) and with `main` (`89fb2c28c`) is
   clean. The PR leaves `registered.py`, its README paragraph and `test_registered.py` identical to its base. In both
   merged trees, each of `served-domain/v1`, `flock-circuit/binding/v2` and `registered-domain/v0` (main) or `v1`
   (#1320) has one definition.
6. **Scope is as claimed.** The PR changes 9 files and no Definition, subcircuit template or Boolean lowering. Staging
   `rope-head/d64/neox-bf16` (4 instances, salt key zero) at base and head gives byte-identical `circuit.txt`, SHA-512
   `5c33464ccf92…3926d6`. No circuit-check report is needed.

## Non-blocking notes

- **N1 (test).** `test_circuit.py`'s `assert_public_only` holds `bindings` to the rule but doesn't tie `domain_ids` to
  `bindings`. A mutation that builds the domains from a different binding, while reporting the right one, passes all
  three `test_circuit.py` tests. Only `test_class_statement.py`'s core-rows test catches it. Suggested line in the
  `for nm in names` loop: `assert fv["domain_ids"][nm] == CommitmentDomain(bytes.fromhex(fv["bindings"][nm]),
  fv["owner"], RangeIndexedDomain(0, counts[nm]), hash="sha512").domain_id.hex()`, after `counts` is defined.
- **N2 (benchmarks).** `pod.sh` passes `STATEMENT` through to a0 and a3 but has no binding variable, so a pod run on an
  M0 tar pinned before this change can't select v1; it refuses at registration rather than passing. Suggested addition
  to the a0 and a3 lines: `${BINDING:+--binding $BINDING}`. a0's `summary.json` also doesn't record the tag it derived
  under (nor `--statement`).
- **N3 (docs).** `ir_sampling.py`'s docstring still points at `ir_frame.BINDING_TAG`. That is right for the legacy path
  and needs no change before the legacy deletion.
